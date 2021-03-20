#Load in Statsbomb competition and match data
#This is a library for loading json files.
import json
import pandas as pd
from pandas import json_normalize
import matplotlib.pyplot as plt
import streamlit as st
import altair as alt
import requests

#Load the competition file
competitions = requests.get('https://raw.githubusercontent.com/statsbomb/open-data/master/data/competitions.json')
competitions = competitions.json()

competitions_list = []
for competition in competitions:
    if [competition['competition_name'], competition['season_name'], competition['competition_id'], competition['season_id']] not in(competitions_list):
        competitions_list.append([competition['competition_name'], competition['season_name'],
                                  competition['competition_id'], competition['season_id']])
        #competitions_list.append(competition['competition_name'])
#print(competitions_list)
#print(competition['competition_name'], competition['season_name'])
   
add_selectbox_competition = st.selectbox(
    "What competition are interested in?",
    (competitions_list)
)


competition_id = add_selectbox_competition[2]
season_id = add_selectbox_competition[3]

#Load the list of matches for this competition
matches = requests.get('https://raw.githubusercontent.com/statsbomb/open-data/master/data/matches/'+str(competition_id)+'/'+str(season_id)+'.json')
matches = matches.json()
    
matches_list = []
for match in matches:
    if [match['home_team']['home_team_name'], match['away_team']['away_team_name'], match['home_score'], match['away_score'], match['match_date'], match['match_id']] not in(competitions_list):
        matches_list.append([match['home_team']['home_team_name'], match['away_team']['away_team_name'], 
                                  match['home_score'], match['away_score'], match['match_date'], match['match_id']])
        #competitions_list.append(competition['competition_name'])
#print(matches_list)

add_selectbox_match= st.selectbox(
    "What match are interested in?",
    (matches_list)
)

match_id = add_selectbox_match[5]

data = requests.get('https://raw.githubusercontent.com/statsbomb/open-data/master/data/events/'+str(match_id)+'.json')
data = data.json()


df = json_normalize(data, sep = "_")

# excluding (...) for large number of columns
pd.set_option("display.max.columns", None)

df.loc[(df['type_name'] == 'Pass') & (df['possession_team_name']== matches_list[0][0]), 'home_passes'] = 1
df.loc[(df['type_name'] == 'Pass') & (df['possession_team_name']== matches_list[0][1]), 'away_passes'] = 1
#train.loc[(train['age'] > 15) & (train['age'] <= 25), 'new'] = 1
df.loc[(df['type_name'] == 'Shot') & (df['possession_team_name']== matches_list[0][0]), 'home_shots'] = 1
df.loc[(df['type_name'] == 'Shot') & (df['possession_team_name']== matches_list[0][1]), 'away_shots'] = 1

# Dividing games to 15-min periods
df.loc[(df['minute'] < 15), '15_min'] = 15
df.loc[(df['minute'] >= 15) & (df['minute'] < 30), '15_min'] = 30
df.loc[(df['minute'] >= 30) & (df['period'] == 1), '15_min'] = 45
df.loc[(df['minute'] >= 45) & (df['minute'] < 60) & (df['period'] == 2), '15_min'] = 60
df.loc[(df['minute'] >= 60) & (df['minute'] < 75), '15_min'] = 75
df.loc[(df['minute'] >= 75), '15_min'] = 90

#df['count_students_graduated_running_total'] = df['count_students_graduated'].cumsum()

df['cum_home_passes'] = df['home_passes'].cumsum()
df['cum_away_passes'] = df['away_passes'].cumsum()
df['cum_home_shots'] = df['home_shots'].cumsum()
df['cum_away_shots'] = df['away_shots'].cumsum()



test_group_passes = df.loc[df['type_name'] == 'Pass']
test_group_passes = test_group_passes.groupby(['minute', 'possession_team_name'])["type_name"].count()
#test_group_passes.tail(10)

pass_data = pd.DataFrame(test_group_passes.reset_index(), 
                       columns=['minute', 'possession_team_name', 'type_name'])

# https://www.geeksforgeeks.org/create-grouped-bar-chart-using-altair-in-python/
pass_chart = alt.Chart(pass_data, title="Passes by teams").mark_bar(size=3).encode( 
  alt.X('minute', axis=alt.Axis(title=None)), 
  alt.Y('type_name', axis=alt.Axis(grid=False)),  
  alt.Color('possession_team_name', legend=alt.Legend(title="Teams")),
  opacity=alt.value(0.9)
  ).properties(width=600)
  
st.altair_chart(pass_chart, use_container_width=True)



test_group_shots = df.loc[df['type_name'] == 'Shot']
test_group_shots = test_group_shots.groupby(['minute', 'possession_team_name'])["type_name"].count()
#test_group_shots.tail(10)
#test_group_shots.unstack().plot(kind='bar', figsize=(18,8))

shots_data = pd.DataFrame(test_group_shots.reset_index(), 
                       columns=['minute', 'possession_team_name', 'type_name'])

# https://www.geeksforgeeks.org/create-grouped-bar-chart-using-altair-in-python/
shots_chart = alt.Chart(shots_data, title="Shots by teams").mark_bar(size=7).encode( 
  alt.X('minute', axis=alt.Axis(title=None)), 
  alt.Y('type_name', axis=alt.Axis(grid=False)),  
  alt.Color('possession_team_name', legend=alt.Legend(title="Teams")),
  opacity=alt.value(0.9)
  ).properties(width=600)
  
st.altair_chart(shots_chart, use_container_width=True)





test_group_passes = df.loc[df['type_name'] == 'Pass']
test_group_passes = test_group_passes.groupby(['15_min', 'possession_team_name'])["type_name"].count()

pass_data = pd.DataFrame(test_group_passes.reset_index(), 
                       columns=['15_min', 'possession_team_name', 'type_name'])

pass_chart = alt.Chart(pass_data, title="Passes by teams").mark_bar(size=20).encode( 
  alt.Column('15_min:O'),
  alt.X('possession_team_name', axis=alt.Axis(title=None)), 
  alt.Y('type_name', axis=alt.Axis(grid=False)),  
  alt.Color('possession_team_name', legend=alt.Legend(title="Teams")),
  opacity=alt.value(0.9)
  )

st.altair_chart(pass_chart)



test_group_shots = df.loc[df['type_name'] == 'Shot']
test_group_shots = test_group_shots.groupby(['15_min', 'possession_team_name'])["type_name"].count()

shots_data = pd.DataFrame(test_group_shots.reset_index(), 
                       columns=['15_min', 'possession_team_name', 'type_name'])

shots_chart = alt.Chart(shots_data, title="Shots by teams").mark_bar(size=20).encode( 
  alt.Column('15_min:O'),
  alt.X('possession_team_name', axis=alt.Axis(title=None)), 
  alt.Y('type_name', axis=alt.Axis(grid=False)),  
  alt.Color('possession_team_name', legend=alt.Legend(title="Teams")),
  opacity=alt.value(0.9)
  )

st.altair_chart(shots_chart)





test_group_xg = df#.loc[df['type_name'] == 'Pass']
test_group_xg = test_group_xg.groupby(['15_min', 'possession_team_name'])["shot_statsbomb_xg"].sum()
#test_group_xg.tail(10)
#test_group_xg.unstack().plot(kind='bar', figsize=(8,4))
#mpld3.show()

xg_data = pd.DataFrame(test_group_xg.reset_index(), 
                       columns=['15_min', 'possession_team_name', 'shot_statsbomb_xg'])
#st.bar_chart(b)

# https://www.geeksforgeeks.org/create-grouped-bar-chart-using-altair-in-python/
xg_chart = alt.Chart(xg_data, title="xG by teams").mark_bar(size=20).encode( 
  alt.Column('15_min:O'),
  alt.X('possession_team_name', axis=alt.Axis(title=None)), 
  alt.Y('shot_statsbomb_xg', axis=alt.Axis(grid=False)),  
  alt.Color('possession_team_name', legend=alt.Legend(title="Teams")),
  opacity=alt.value(0.9)
  )
  
# https://altair-viz.github.io/user_guide/customization.html
st.altair_chart(xg_chart)




# Shots & xG chart
xg_shots_data = df.loc[df['type_name'] == 'Shot']
xg_shots_data = xg_shots_data.groupby(['15_min', 'possession_team_name']
                                       ).agg({'shot_statsbomb_xg' : 'sum',
                                              'type_name' : 'count'})

xg_shots_data = pd.DataFrame(xg_shots_data.reset_index(), 
                       columns=['15_min', 'possession_team_name', 'shot_statsbomb_xg', 'type_name'])
                                              
xg_shots_chart = alt.Chart(xg_shots_data, title="xG per shot").transform_calculate(
    xgPerShot="datum.shot_statsbomb_xg / datum.type_name").mark_point(size=20).encode(
    x='15_min',
    y='xgPerShot:Q',
    color='possession_team_name',
    size='shot_statsbomb_xg')

st.altair_chart(xg_shots_chart)
# pass pitch



# heatmap























match_id_required = match_id
home_team_required =add_selectbox_match[0]
away_team_required =add_selectbox_match[1]

import numpy as np

#Size of the pitch in yards (!!!)
pitchLengthX=120
pitchWidthY=80

#A dataframe of shots
shots = df.loc[df['type_name'] == 'Shot'].set_index('id')

#A dataframe of passes
passes = df.loc[df['type_name'] == 'Pass'].set_index('id')

#Draw the pitch
from FCPython import createPitch
(fig,ax) = createPitch(pitchLengthX,pitchWidthY,'yards','gray')

'''
#Draw the pitch OLD
from FCPython import createPitchOld
(fig,ax) = createPitchOld()
'''

#Plot the shots
for i,shot in shots.iterrows():
    x=shot['location'][0]
    y=shot['location'][1]
    
    goal=shot['shot_outcome_name']=='Goal'
    team_name=shot['team_name']
    
    #circleSize=2
    circleSize=np.sqrt(shot['shot_statsbomb_xg'])*8
    #size of circle depends on probability of scoring from this spot (shot_statsbomb_xg)

    if (team_name==home_team_required):
        if goal:
            shotCircle=plt.Circle((x,pitchWidthY-y),circleSize,color="red")
            plt.text((x+1),pitchWidthY-y+1,shot['player_name']) 
        else:
            shotCircle=plt.Circle((x,pitchWidthY-y),circleSize,color="red")     
            shotCircle.set_alpha(.2) #alpha sets the opacity of red circles
    elif (team_name==away_team_required):
        if goal:
            shotCircle=plt.Circle((pitchLengthX-x,y),circleSize,color="blue") 
            plt.text((pitchLengthX-x+1),y+1,shot['player_name']) 
        else:
            shotCircle=plt.Circle((pitchLengthX-x,y),circleSize,color="blue")      
            shotCircle.set_alpha(.2)
    ax.add_patch(shotCircle)
    
away_team_shots_sum = shots.loc[shots['team_name'] == away_team_required]
home_team_shots_sum = shots.loc[shots['team_name'] == home_team_required]     
plt.text(5,75,away_team_required + ' shots' + ' (total ' + str(len(away_team_shots_sum)) + ')') 
plt.text(75,75,home_team_required + ' shots' + ' (total ' + str(len(home_team_shots_sum)) + ')')  
   
fig.set_size_inches(10, 7)
st.write(fig)

#Exercise: 
#1, Create a dataframe of passes which contains all the passes in the match
#2, Plot the start point of every Sweden pass. Attacking left to right.
#3, Plot only passes made by Caroline Seger (she is Sara Caroline Seger in the database)
#4, Plot arrows to show where the passes went


#Draw the pitch
(fig,ax) = createPitch(pitchLengthX,pitchWidthY,'yards','gray')

#Placeholder for counting good and bad passes
bad_passes = []
good_passes = []


player_pass_list = []
for passs in passes['player_name']:
    if passs not in(player_pass_list):
        player_pass_list.append(passs)
        #competitions_list.append(competition['competition_name'])
#print(matches_list)

add_selectbox_player_pass= st.selectbox(
    "What player are interested in?",
    (player_pass_list)
)





#Plot the passes
for i,passs in passes.iterrows():
    x=passs['location'][0]
    y=passs['location'][1]
    
    team_name=away_team_required # we'll choose Sweden passes only
    
    circleSize=1.5

    if passs['player_name'] == add_selectbox_player_pass: #goalkeeper
        
        #if pass was unsuccessful it'll be red
        if any([passs.pass_outcome_name == 'Incomplete', passs.pass_outcome_name == 'Out', 
            passs.pass_outcome_name == 'Unknown', passs.pass_outcome_name == 'Pass Offside',
            passs.pass_outcome_name == 'Injury Clearance']):
            color="red"
            bad_passes.append(passs['index'])
        else:
            color="green"
            good_passes.append(passs['index'])
        
        passCircle=plt.Circle((x,pitchWidthY-y),circleSize,color=color)
        passCircle.set_alpha(0.4)
       # plt.text((pitchLengthX-x+1),y+1) 
        ax.add_patch(passCircle)
        
        dx=passs['pass_end_location'][0]-x
        dy=passs['pass_end_location'][1]-y

        passArrow=plt.Arrow(x,(pitchWidthY-y),dx,-dy,width=3,color=color)
        passArrow.set_alpha(.4)
        ax.add_patch(passArrow)
     
away_team_passes = passes.loc[passes['player_name'] == 'Rut Hedvig Lindahl']
passes_stats = 'Good passes: ' + str(len(good_passes)) + ', bad passes: ' + str(len(bad_passes))
plt.text(5,81,'Rut Hedvig Lindahl' + ' passes' + ' (total ' + str(len(away_team_passes)) + ') ' + str(passes_stats)) 

   
fig.set_size_inches(10, 7)
st.write(fig)