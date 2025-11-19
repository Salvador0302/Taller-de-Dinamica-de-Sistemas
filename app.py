import os
import ssl
import mysql.connector
from flask import Flask

# Asegurar que el directorio de trabajo sea el del script
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

from src.Routes.route import modelRoute

ssl._create_default_https_context = ssl._create_unverified_context

app = Flask(__name__)
modelRoute(app)

if __name__ == "__main__":
    # Intentar configurar Ngrok (opcional)
    try:
        from pyngrok import ngrok
        ngrok.set_auth_token('2hKn4UWWXYkrNTCBS8HWz0IKXtY_6YwXJMKDn4w3KWwTZUFfN')
        public_url = ngrok.connect(5000)
        public_url_str = str(public_url)
        print('URL pública de Ngrok:', public_url_str)
        print('URL local: http://127.0.0.1:5000/')
        print('(Ngrok crea una URL pública temporal para compartir tu app)')
    except Exception as e:
        print('Ngrok no disponible (opcional):', str(e))
        print('La aplicación se ejecutará solo en modo local.')
    
    print('URL local: http://127.0.0.1:5000/')
    print('Presiona CTRL+C para detener el servidor')
    print()
    
    exclude_patterns = [
        '*/static/vensim/*.py',
        '*/static/vensim/__pycache__/*',
        '*/venv/**/*'
    ]
    
    app.run(
        debug=True, 
        host='0.0.0.0', 
        port=5000,
        exclude_patterns=exclude_patterns
    )
    
