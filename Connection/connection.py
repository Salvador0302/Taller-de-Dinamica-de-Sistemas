import mysql.connector
from decouple import config

def create_database_if_not_exists():
    """Crea la base de datos si no existe"""
    try:
        # Conectar sin especificar base de datos
        connection = mysql.connector.connect(
            host=config('DB_HOST', default='localhost'),
            port=int(config('DB_PORT', default=3306)),
            user=config('DB_USERNAME', default='root'),
            password=config('DB_PASSWORD', default='12345')
        )
        cursor = connection.cursor()
        db_name = config('DB_DATABASE', default='vensimweb')
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        cursor.close()
        connection.close()
        return True
    except Exception as e:
        print(f"Error al crear base de datos: {e}")
        return False

def connect():
  try:
      return mysql.connector.connect(
          host=config('DB_HOST', default='localhost'),
          port=int(config('DB_PORT', default=3306)),
          user=config('DB_USERNAME', default='root'),
          password=config('DB_PASSWORD', default='12345'),
          database=config('DB_DATABASE', default='vensimweb')
      )
  except mysql.connector.Error as error:
      # Si la base de datos no existe, intentar crearla
      error_msg = str(error)
      error_code = getattr(error, 'errno', None)
      if "Unknown database" in error_msg or error_code == 1049:
          if create_database_if_not_exists():
              # Intentar conectar nuevamente
              try:
                  return mysql.connector.connect(
                      host=config('DB_HOST', default='localhost'),
                      port=int(config('DB_PORT', default=3306)),
                      user=config('DB_USERNAME', default='root'),
                      password=config('DB_PASSWORD', default='12345'),
                      database=config('DB_DATABASE', default='vensimweb')
                  )
              except mysql.connector.Error as retry_error:
                  return [{'message':retry_error}]
      return [{'message':error}]

def connection_select(cursorObject,select_stmt):
    cursorObject.execute(select_stmt)
    return cursorObject.fetchall()
