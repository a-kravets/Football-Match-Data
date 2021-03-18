mkdir -p ~/.streamlit/
echo "
[general]
email = "your-email@domain.com"
" > ~/.streamlit/credentials.toml
echo "[server]
headless = true
port = $PORT
enableCORS = false
" > ~/.streamlit/config.toml