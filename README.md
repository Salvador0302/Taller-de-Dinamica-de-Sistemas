# 🎯 VENSIM TO PYTHON - Dashboard Interactivo de Sistemas Dinámicos

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=flat&logo=python)
![Flask](https://img.shields.io/badge/Flask-2.0.2-green?style=flat&logo=flask)
![PySD](https://img.shields.io/badge/PySD-3.14%2B-orange?style=flat)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat)

**Dashboard web interactivo para visualizar y simular modelos de dinámica de sistemas creados en Vensim**

[🚀 Características](#-características) • [📋 Requisitos](#-requisitos-previos) • [⚙️ Instalación](#️-instalación-paso-a-paso) • [🎮 Uso](#-uso) • [🛠️ Tecnologías](#️-tecnologías)

</div>

---

## 📖 Descripción

Sistema web que convierte modelos Vensim (.mdl) en visualizaciones interactivas con capacidades de:
- ✨ Gráficos interactivos con zoom, pan y descarga
- 🔄 Diagramas de Forrester y causales generados automáticamente
- 🎚️ Control dinámico de parámetros del modelo
- 📊 Visualización de tablas de datos
- 🎨 Interfaz moderna con tema futurista oscuro

### Modelo Incluido
**Sistema de Inmigración, Delincuencia y Seguridad Pública**
- 4 variables de nivel (stocks): Población Inmigrante, Inmigrantes Desempleados, Delincuentes en la Calle, Policías en Servicio
- 9 flujos principales
- 10 parámetros configurables (tasas)

---

## 🌟 Características

### 📈 Gráficos de Simulación Interactivos
- **Zoom In/Out**: Botones y rueda del ratón
- **Pan/Arrastre**: Mueve los gráficos con el mouse
- **Reset**: Restaura la vista original
- **Descarga PNG**: Exporta gráficos como imágenes
- **Tooltips**: Información de coordenadas al pasar el mouse

### 🔄 Diagramas Dinámicos
- **Diagrama de Forrester**: Flujos y niveles con código de colores
  - Azul: Stocks (Niveles)
  - Verde: Flows (Flujos)
  - Púrpura: Variables Auxiliares
  - Naranja: Constantes/Parámetros
- **Diagrama Causal**: Lazos de retroalimentación con polaridades (+/-)

### 🎛️ Control de Parámetros
- 6 sliders interactivos para modificar tasas
- Actualización en tiempo real de simulaciones
- Validación de rangos

### 📱 Interfaz Responsive
- Diseño adaptable a móvil, tablet y desktop
- Navegación intuitiva entre secciones
- Notificaciones visuales

---

## 📋 Requisitos Previos

### Software Necesario

| Software | Versión Mínima | Propósito | Descarga |
|----------|----------------|-----------|----------|
| **Python** | 3.9.7+ | Entorno de ejecución | [python.org](https://www.python.org/downloads/) |
| **MySQL** | 5.7+ o 8.0+ | Base de datos | [mysql.com](https://dev.mysql.com/downloads/installer/) |
| **Git** | Cualquiera | Control de versiones (opcional) | [git-scm.com](https://git-scm.com/downloads) |

### Opciones de MySQL

**Opción 1: XAMPP (Recomendado para principiantes)**
- Incluye MySQL, Apache y phpMyAdmin
- Descarga: [apachefriends.org](https://www.apachefriends.org/)
- Instalación simplificada

**Opción 2: MySQL Standalone**
- Solo el servidor MySQL
- Descarga: [MySQL Community Server](https://dev.mysql.com/downloads/mysql/)
- Mayor control

**Opción 3: MySQL Workbench**
- Cliente gráfico para administrar MySQL
- Descarga: [MySQL Workbench](https://dev.mysql.com/downloads/workbench/)
- Interfaz visual completa

---

## ⚙️ Instalación Paso a Paso

### 1️⃣ Clonar el Repositorio

```bash
# Con Git
git clone https://github.com/Salvador0302/Taller-de-Dinamica-de-Sistemas.git
cd Taller-de-Dinamica-de-Sistemas

# O descargar ZIP desde GitHub y extraer
```

### 2️⃣ Verificar Python

```bash
# Windows
python --version
# Debe mostrar: Python 3.9.7 o superior

# Si no está instalado, descargar de python.org
# ⚠️ IMPORTANTE: Marcar "Add Python to PATH" durante la instalación
```

### 3️⃣ Crear Entorno Virtual

```bash
# Windows PowerShell o CMD
python -m venv venv

# Activar entorno virtual
# PowerShell:
venv\Scripts\Activate.ps1

# CMD:
venv\Scripts\activate.bat

# Verificar activación (debe aparecer (venv) al inicio del prompt)
```

### 4️⃣ Instalar Dependencias

```bash
# Con el entorno virtual activado
pip install --upgrade pip
pip install -r requirements.txt

# Esperar a que se instalen todos los paquetes (~2-3 minutos)
# Paquetes principales: Flask, PySD, MySQL Connector, NetworkX, mpld3
```

### 5️⃣ Configurar MySQL

#### Si usas XAMPP:
1. Abrir XAMPP Control Panel
2. Iniciar **Apache** y **MySQL**
3. Click en "Admin" de MySQL (abre phpMyAdmin)
4. Ir a pestaña "SQL"
5. Copiar y pegar el contenido de `Backup/vensimweb.sql`
6. Click en "Go" o "Continuar"

#### Si usas MySQL directamente:
```bash
# Conectar a MySQL
mysql -u root -p

# Crear base de datos
source Backup/vensimweb.sql

# O importar desde cliente gráfico
```

#### Verificar instalación:
```sql
USE vensimweb;
SHOW TABLES;
-- Debe mostrar: color, model
SELECT * FROM model;
-- Debe mostrar 4 registros (los 4 gráficos del modelo)
```

### 6️⃣ Configurar Variables de Entorno

<<<<<<< HEAD
**Copiar el archivo de ejemplo y configurarlo:**

```bash
# Windows PowerShell
Copy-Item .env.example .env

# Linux/Mac
cp .env.example .env
```

Luego edita el archivo `.env` con tus credenciales:
=======
Crear archivo `.env` en la raíz del proyecto:
>>>>>>> origin/main

```env
# Configuración de Base de Datos
DB_HOST=localhost
DB_PORT=3306
DB_USERNAME=root
<<<<<<< HEAD
DB_PASSWORD=tu_contraseña_aqui
DB_DATABASE=vensimweb
APP_URL_VENSIM=http://localhost/assets/vensim/document.mdl

# Configuración del Asistente AI (Opcional)
AI_PROVIDER=gemini
GEMINI_API_KEY=tu_api_key_aqui
=======
DB_PASSWORD=
DB_DATABASE=vensimweb

# Configuración Opcional (no modificar)
APP_URL_VENSIM=http://localhost/assets/vensim/document.mdl
>>>>>>> origin/main
```

**⚠️ Notas importantes:**
- `DB_PASSWORD` déjalo vacío si no configuraste contraseña en MySQL
- Si cambiaste el puerto de MySQL, ajusta `DB_PORT`
- Si creaste un usuario específico, ajusta `DB_USERNAME`
<<<<<<< HEAD
- **NUNCA subas el archivo `.env` al repositorio** (ya está en `.gitignore`)
=======
>>>>>>> origin/main

### 7️⃣ Verificar Modelo Vensim

```bash
# Verificar que existe el archivo del modelo
# Debe estar en: static/vensim/taller5_forrester.mdl
# (Ya incluido en el repositorio)

dir static\vensim\*.mdl
# Debe mostrar: taller5_forrester.mdl
```

---

## 🚀 Ejecutar la Aplicación

### Inicio Normal

```bash
# 1. Activar entorno virtual (si no está activo)
venv\Scripts\Activate.ps1

# 2. Ejecutar aplicación
python app.py

# 3. Esperar mensaje:
# * Running on http://127.0.0.1:5000/
# * Running on http://192.168.X.X:5000/ (red local)
```

### Acceder al Dashboard

Abrir navegador en:
- **Local**: http://127.0.0.1:5000/
- **Red Local**: http://192.168.X.X:5000/ (desde otros dispositivos en tu red)

### Detener el Servidor

```bash
# Presionar CTRL + C en la terminal
```

---

## 🎮 Uso

### Navegación

La aplicación tiene 4 secciones principales:

1. **📊 Tablas y Simulación** (Página principal)
   - 4 gráficos interactivos con los resultados del modelo
   - Controles de zoom, pan, reset y descarga
   - Botones "Ver datos" para tablas detalladas
   - Panel de control de parámetros (abajo)

2. **🔵 Diagrama Causal**
   - Visualización de relaciones causales
   - Polaridades (+/-) en las conexiones
   - Identificación de bucles de retroalimentación
   - Controles interactivos

3. **🟢 Diagrama de Forrester**
   - Representación de flujos y niveles
   - Código de colores por tipo de variable
   - Vista completa de la estructura del modelo
   - Controles interactivos

4. **💧 Símil Hidrodinámico** (Enlace externo)
   - Representación física del modelo

### Modificar Parámetros

1. Scroll hasta el panel "Parámetros del modelo"
2. Ajustar los sliders de las 6 tasas:
   - Tasa de inmigrantes
   - Tasa de emigrantes
   - Tasa de desempleo
   - Tasa de nuevos delincuentes
   - Tasa de muertes
   - Tasa de policías contratados
3. Click en "Actualizar simulación"
4. Los gráficos se regeneran con los nuevos valores

### Controles de Gráficos

| Acción | Método 1 | Método 2 |
|--------|----------|----------|
| **Zoom In** | Botón 🔍+ | Scroll hacia arriba |
| **Zoom Out** | Botón 🔍- | Scroll hacia abajo |
| **Pan** | Arrastra con mouse | - |
| **Reset** | Botón 🔄 | - |
| **Descargar** | Botón ⬇️ | - |

---

## 🛠️ Tecnologías

### Backend
- **Flask 2.0.2**: Framework web
- **PySD 3.14+**: Parser de modelos Vensim
- **MySQL Connector 8.0.32**: Conexión a base de datos
- **Python-decouple 3.8**: Gestión de variables de entorno

### Visualización
- **Matplotlib**: Generación de gráficos
- **mpld3 0.5.9**: Conversión a gráficos web interactivos
- **NetworkX 3.6**: Generación de diagramas de red
- **Pillow 10+**: Procesamiento de imágenes

### Frontend
- **Bootstrap 5.3.0**: Framework CSS
- **Bootstrap Icons**: Iconografía
- **JavaScript Vanilla**: Interactividad

### Análisis
- **Pandas 2.0+**: Manipulación de datos
- **NumPy 1.24+**: Computación numérica
- **SciPy 1.10+**: Algoritmos científicos
- **xarray 0.21+**: Datos multidimensionales

---

## 📁 Estructura del Proyecto

```
Taller-de-Dinamica-de-Sistemas/
├── app.py                          # Punto de entrada de la aplicación
├── requirements.txt                # Dependencias Python
├── .env                           # Variables de entorno (crear)
├── README.md                      # Este archivo
│
├── Backup/
│   └── vensimweb.sql             # Script SQL de la base de datos
│
├── Connection/
│   └── connection.py             # Configuración de conexión MySQL
│
├── src/
│   ├── Controllers/
│   │   ├── controller.py         # Lógica de simulación
│   │   └── diagram_generator.py  # Generación de diagramas
│   ├── Models/
│   │   └── model.py              # Consultas a base de datos
│   └── Routes/
│       └── route.py              # Definición de rutas Flask
│
├── static/
│   ├── css/
│   │   └── style.css             # Estilos personalizados
│   ├── js/
│   │   └── script.js             # Lógica de interactividad
│   ├── vensim/
│   │   └── taller5_forrester.mdl # Modelo Vensim
│   └── ico/
│       └── icono.ico             # Favicon
│
└── templates/
    ├── template.html              # Página principal
    ├── diagrama_causal.html       # Diagrama causal
    ├── diagrama_forrester.html    # Diagrama de Forrester
    └── error.html                 # Página de error
```

---

## 🐛 Solución de Problemas

### Error: "No module named 'flask'"
```bash
# Verificar que el entorno virtual está activado
# Debe aparecer (venv) al inicio del prompt

# Reinstalar dependencias
pip install -r requirements.txt
```

### Error: "Can't connect to MySQL server"
```bash
# Verificar que MySQL está corriendo
# XAMPP: Iniciar MySQL en el panel de control
# MySQL Standalone: Verificar servicio en Windows Services

# Verificar credenciales en .env
# Probar conexión:
mysql -u root -p
```

### Error: "Port 5000 is already in use"
```bash
# Detener proceso en puerto 5000
# PowerShell:
Get-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess | Stop-Process

# O cambiar puerto en app.py (línea final):
# app.run(debug=True, host='0.0.0.0', port=5001)
```

### Error: "Template not found"
```bash
# Verificar estructura de carpetas
# Debe existir carpeta templates/ con los archivos .html
dir templates\*.html
```

### Gráficos no se muestran
1. Abrir consola del navegador (F12)
2. Verificar errores en pestaña "Console"
3. Verificar que mpld3 se instaló correctamente:
   ```bash
   pip show mpld3
   ```

### Base de datos vacía
```bash
# Reimportar SQL
mysql -u root -p vensimweb < Backup/vensimweb.sql

# O desde phpMyAdmin:
# 1. Seleccionar base de datos vensimweb
# 2. Pestaña "Import"
# 3. Seleccionar Backup/vensimweb.sql
# 4. Click en "Go"
```

---

## 📝 Notas Adicionales

### Ngrok (Opcional)
- La aplicación intenta usar Ngrok para crear una URL pública
- Si falla, la app sigue funcionando en modo local
- Para desactivar: comentar líneas 21-30 en `app.py`

### Rendimiento
- Primera carga: ~3-5 segundos (genera diagramas)
- Actualizaciones de parámetros: ~2-3 segundos
- Navegación entre páginas: instantánea (diagramas en caché)

### Personalización
- Modificar colores: `static/css/style.css`
- Agregar variables: Actualizar `Backup/vensimweb.sql` y BD
- Cambiar modelo: Reemplazar `static/vensim/taller5_forrester.mdl`

---

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

---

## 👥 Autores

- **Salvador Cordova** - [@Salvador0302](https://github.com/Salvador0302)

---

## 🙏 Agradecimientos

- **PySD Project**: Por el parser de Vensim en Python
- **Flask Team**: Por el framework web minimalista
- **mpld3**: Por la conversión de matplotlib a HTML interactivo
- **Bootstrap**: Por el framework CSS responsive

---

<div align="center">

**⭐ Si este proyecto te fue útil, considera darle una estrella en GitHub ⭐**

[⬆ Volver arriba](#-vensim-to-python---dashboard-interactivo-de-sistemas-dinámicos)

</div>
