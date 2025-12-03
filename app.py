import os
import ssl
import mysql.connector
from flask import Flask
from dotenv import load_dotenv
from decouple import config

# Cargar variables de entorno desde .env
load_dotenv()

# Asegurar que el directorio de trabajo sea el del script
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

from src.Routes.route import modelRoute

ssl._create_default_https_context = ssl._create_unverified_context

def setup_database_if_needed():
    """Crea la base de datos y las tablas automáticamente si no existen"""
    try:
        # Conectar sin especificar base de datos primero
        connection = mysql.connector.connect(
            host=config('DB_HOST', default='localhost'),
            port=int(config('DB_PORT', default=3306)),
            user=config('DB_USERNAME', default='root'),
            password=config('DB_PASSWORD', default='12345')
        )
        
        cursor = connection.cursor()
        
        # Crear base de datos si no existe
        cursor.execute("CREATE DATABASE IF NOT EXISTS vensimweb")
        cursor.execute("USE vensimweb")
        
        # Crear tabla color
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS `color` (
              `idColor` int(10) NOT NULL AUTO_INCREMENT,
              `nameColor` varchar(50) NOT NULL,
              PRIMARY KEY (`idColor`),
              UNIQUE KEY `nameColor` (`nameColor`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
        """)
        
        # Insertar colores si no existen
        colors = [
            (1, '#1f77b4'), (8, 'black'), (2, 'blue'), (5, 'cyan'),
            (3, 'green'), (6, 'magenta'), (4, 'red'), (9, 'white'), (7, 'yellow')
        ]
        for id_color, name_color in colors:
            cursor.execute(
                "INSERT IGNORE INTO `color` (`idColor`, `nameColor`) VALUES (%s, %s)",
                (id_color, name_color)
            )
        
        # Crear tabla model
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS `model` (
              `idModel` int(10) NOT NULL AUTO_INCREMENT,
              `title` varchar(200) NOT NULL,
              `nameLabelX` varchar(200) NOT NULL,
              `nameLabelY` varchar(200) NOT NULL,
              `position` int(1) NOT NULL DEFAULT 0,
              `nameNivel` varchar(200) NOT NULL,
              `idColor` int(10) NOT NULL DEFAULT 1,
              PRIMARY KEY (`idModel`),
              UNIQUE KEY `nameNivel` (`nameNivel`),
              KEY `model_color` (`idColor`),
              CONSTRAINT `model_color` FOREIGN KEY (`idColor`) REFERENCES `color` (`idColor`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
        """)
        
        # Insertar modelos si no existen
        models = [
            (1, 'Comportamiento de Delincuentes en la Calle', 'Meses', 'Cantidad de Delincuentes', 0, 'Delincuentes en la calle', 1),
            (2, 'Comportamiento de Policías en Servicio', 'Meses', 'Cantidad de Policías', 1, 'Policias en servicio', 3),
            (3, 'Comportamiento de Inmigrantes Desempleados', 'Meses', 'Cantidad de Inmigrantes', 2, 'Inmigrantes desempleados', 7),
            (4, 'Comportamiento de Población Inmigrante', 'Meses', 'Cantidad de Personas', 3, 'Poblacion inmigrante', 4)
        ]
        for model_data in models:
            cursor.execute(
                """INSERT IGNORE INTO `model` 
                   (`idModel`, `title`, `nameLabelX`, `nameLabelY`, `position`, `nameNivel`, `idColor`) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                model_data
            )
        
        connection.commit()
        cursor.close()
        connection.close()
        print("✓ Base de datos y tablas verificadas/creadas automáticamente")
        return True
        
    except mysql.connector.Error as error:
        print(f"⚠ Advertencia: No se pudo configurar la base de datos automáticamente: {error}")
        print("  Asegúrate de que MySQL esté corriendo y las credenciales en .env sean correctas")
        return False
    except Exception as e:
        print(f"⚠ Advertencia: Error al configurar base de datos: {e}")
        return False

# Configurar base de datos automáticamente al iniciar
setup_database_if_needed()

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
    
