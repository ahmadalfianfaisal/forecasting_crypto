"""
WSGI entry point untuk aplikasi Dash
"""
from src.views.app import app

# Ini adalah server WSGI yang akan digunakan oleh Gunicorn
server = app.server

if __name__ == "__main__":
    app.run_server(debug=True)