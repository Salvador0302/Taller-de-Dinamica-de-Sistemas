# VENSIM TO PYTHON (Python 3.9.7)
## Modelo: Forrester (taller5_forrester.mdl)

## Configuracion del servidor

- Tener tu servidor local (Preferencia Xampp) iniciando Apache y MySQL
- Dentro del servidor (Admin en MySQL) ejecutar el archivo `vensimweb.sql` (el archivo se encuentra en `Backup`)
  - Este SQL configura la base de datos con las variables del modelo Forrester:
    - Delincuentes en la calle
    - Policias en servicio
    - Inmigrantes desempleados
    - Poblacion inmigrante
- El archivo VENSIM debe estar en `static/vensim/taller5_forrester.mdl` (ya incluido)
- Si configuras de distinta manera actualizar el archivo `.env`

## Implementación

- Paso 1: Crear entorno virtual y instalar dependencias:
  ```bash
  python -m venv venv
  venv\Scripts\activate
  pip install -r requirements.txt
  ```

- Paso 2: Ejecutar el archivo SQL en MySQL:
  - Abrir phpMyAdmin o MySQL Admin
  - Ejecutar el contenido de `Backup/vensimweb.sql`

- Paso 3: Crear archivo `.env` en la raíz del proyecto:
  ```env
  DB_HOST=localhost
  DB_PORT=3306
  DB_USERNAME=root
  DB_PASSWORD=
  DB_DATABASE=vensimweb
  APP_URL_VENSIM=http://localhost/assets/vensim/document.mdl
  ```

- Paso 4: Ejecutar la aplicación:
  ```bash
  python app.py
  ```

- Paso 5: Acceder a:
  - Local: http://127.0.0.1:5000/
  - Ngrok: URL pública que se mostrará en la consola (opcional, válida por 2 horas)
