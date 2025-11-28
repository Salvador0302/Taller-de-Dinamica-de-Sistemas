# 📐 Arquitectura del Proyecto - Taller de Dinámica de Sistemas

## 🎯 Visión General

Este proyecto es una *aplicación web Flask* que convierte modelos de dinámica de sistemas creados en Vensim (.mdl) en un dashboard interactivo con capacidades avanzadas de visualización, análisis y simulación.

---

## 🏗️ Arquitectura General

El proyecto sigue una *arquitectura en capas (Layered Architecture)* con separación clara de responsabilidades:


┌─────────────────────────────────────────────────────────┐
│                    CAPA DE PRESENTACIÓN                 │
│  (Templates HTML + CSS + JavaScript - Frontend)         │
└─────────────────────────────────────────────────────────┘
                          ↕
┌─────────────────────────────────────────────────────────┐
│                    CAPA DE RUTAS                        │
│  (Flask Routes - route.py)                              │
└─────────────────────────────────────────────────────────┘
                          ↕
┌─────────────────────────────────────────────────────────┐
│                  CAPA DE CONTROLADORES                   │
│  (Business Logic - Controllers/)                         │
└─────────────────────────────────────────────────────────┘
                          ↕
┌─────────────────────────────────────────────────────────┐
│                    CAPA DE MODELOS                       │
│  (Data Access - Models/)                                 │
└─────────────────────────────────────────────────────────┘
                          ↕
┌─────────────────────────────────────────────────────────┐
│                    CAPA DE DATOS                         │
│  (MySQL Database + Vensim Files)                       │
└─────────────────────────────────────────────────────────┘


---

## 📁 Estructura de Directorios


Taller-de-Dinamica-de-Sistemas/
│
├── app.py                          # 🚀 Punto de entrada principal
│
├── Connection/
│   └── connection.py              # 🔌 Gestión de conexión MySQL
│
├── src/
│   ├── Routes/
│   │   └── route.py               # 🛣️ Definición de rutas Flask
│   │
│   ├── Controllers/               # 🎮 Lógica de negocio
│   │   ├── controller.py          # Controlador principal de simulación
│   │   ├── diagram_generator.py   # Generación de diagramas
│   │   ├── export_controller.py   # Exportación de datos
│   │   ├── scenario_controller.py # Gestión de escenarios
│   │   ├── ai_assistant_controller.py  # Asistente AI
│   │   └── predictive_controller.py    # Análisis predictivo
│   │
│   └── Models/
│       └── model.py               # 📊 Acceso a base de datos
│
├── static/                        # 📦 Archivos estáticos
│   ├── css/                       # Estilos
│   ├── js/                        # JavaScript del frontend
│   ├── vensim/                    # Modelos Vensim (.mdl)
│   └── images/                    # Imágenes
│
├── templates/                      # 🎨 Plantillas HTML
│   ├── template.html              # Página principal
│   ├── diagrama_causal.html       # Diagrama causal
│   ├── diagrama_forrester.html    # Diagrama de Forrester
│   └── error.html                 # Página de error
│
└── Backup/                        # 💾 Respaldo de BD y modelos


---

## 🔄 Flujo de Datos

### 1. *Flujo Principal de Simulación*


Usuario → Frontend (template.html)
    ↓
JavaScript envía parámetros → API /api/update-simulation
    ↓
route.py → controller.py
    ↓
model.py → MySQL (obtiene configuración de gráficos)
    ↓
controller.py → PySD (lee modelo Vensim .mdl)
    ↓
controller.py → Plotly (genera gráficos interactivos)
    ↓
JSON Response → Frontend
    ↓
Frontend renderiza gráficos con Plotly.js


### 2. *Flujo de Generación de Diagramas*


Usuario → /diagrama-forrester o /diagrama-causal
    ↓
route.py → diagram_generator.py
    ↓
PySD (lee modelo .mdl) → NetworkX (crea grafo)
    ↓
Matplotlib (genera imagen) → Base64
    ↓
Template HTML → Usuario ve diagrama


---

## 🧩 Componentes Principales

### 1. *app.py* - Punto de Entrada
- *Responsabilidad*: Inicializar la aplicación Flask
- *Funciones*:
  - Configuración de Flask
  - Integración con Ngrok (opcional, para URL pública)
  - Registro de rutas
  - Inicio del servidor

### 2. *Connection/connection.py* - Gestión de Base de Datos
- *Responsabilidad*: Abstracción de conexión MySQL
- *Funciones*:
  - connect(): Establece conexión usando variables de entorno
  - connection_select(): Ejecuta consultas SELECT
- *Configuración*: Usa python-decouple para leer .env

### 3. *src/Routes/route.py* - Enrutamiento
- *Responsabilidad*: Definir endpoints de la API
- *Rutas Principales*:
  - GET /: Página principal con simulaciones
  - POST /api/update-simulation: Actualizar simulación con nuevos parámetros
  - GET /diagrama-forrester: Diagrama de Forrester
  - GET /diagrama-causal: Diagrama causal
  - POST /api/export/*: Exportación (Excel, CSV, PDF)
  - POST /api/scenarios/*: Gestión de escenarios
  - POST /api/ai/*: Asistente AI
  - POST /api/predictive/*: Análisis predictivo

### 4. *src/Models/model.py* - Acceso a Datos
- *Responsabilidad*: Consultas a MySQL
- *Funciones*:
  - getModelAll(): Obtiene configuración de gráficos (títulos, colores, variables)
- *Tablas*:
  - model: Configuración de gráficos (idModel, title, nameLabelX, nameLabelY, position, nameNivel)
  - color: Colores asociados a cada gráfico

### 5. *src/Controllers/controller.py* - Lógica de Simulación
- *Responsabilidad*: Procesar modelos Vensim y generar visualizaciones
- *Flujo*:
  1. Lee configuración desde BD (getModelAll())
  2. Carga modelo Vensim con PySD (pysd.read_vensim())
  3. Ejecuta simulación con parámetros (si se proporcionan)
  4. Para cada variable configurada:
     - Extrae datos de la simulación
     - Genera gráfico interactivo con Plotly
     - Prepara datos para tablas
  5. Calcula indicadores derivados (ej: Índice de Seguridad)
  6. Retorna diccionario con gráficos y datos

### 6. *src/Controllers/diagram_generator.py* - Generación de Diagramas
- *Responsabilidad*: Crear diagramas visuales del modelo
- *Funciones*:
  - generate_forrester_diagram(): Diagrama Stock-Flow
    - Usa NetworkX para crear grafo
    - Clasifica nodos: Stocks (azul), Flows (verde), Auxiliares (púrpura), Constantes (naranja)
    - Renderiza con Matplotlib
  - generate_causal_diagram(): Diagrama de lazos causales
    - Muestra relaciones con polaridades (+/-)
    - Colores: Verde (+) y Rojo (-)

### 7. *src/Controllers/export_controller.py* - Exportación
- *Responsabilidad*: Exportar datos en múltiples formatos
- *Funciones*:
  - export_to_excel(): Excel con múltiples hojas
  - export_to_csv(): CSV simple
  - generate_pdf_report(): Reporte PDF con ReportLab
  - export_comparison_to_excel(): Comparación de escenarios

### 8. *src/Controllers/scenario_controller.py* - Gestión de Escenarios
- *Responsabilidad*: Crear, comparar y gestionar escenarios
- *Clase*: ScenarioManager
- *Funciones*:
  - create_scenario(): Crea escenario con parámetros específicos
  - compare_scenarios(): Compara múltiples escenarios
  - list_scenarios(): Lista todos los escenarios
  - export_scenario() / import_scenario(): Persistencia JSON

### 9. *src/Controllers/ai_assistant_controller.py* - Asistente AI
- *Responsabilidad*: Análisis inteligente con IA
- *Clase*: AIAssistant
- *Proveedores soportados*:
  - Google Gemini (por defecto)
  - OpenAI GPT
  - Anthropic Claude
- *Funciones*:
  - analyze_simulation_results(): Análisis automático de resultados
  - ask_question(): Chat interactivo
  - suggest_parameters(): Sugerencias de optimización
- *Fallback*: Análisis estadístico básico si no hay API key

### 10. *src/Controllers/predictive_controller.py* - Análisis Predictivo
- *Responsabilidad*: Machine Learning para predicciones
- *Clase*: PredictiveAnalyzer
- *Funciones*:
  - predict_future_values(): Predicción con regresión lineal
  - detect_anomalies(): Detección con Isolation Forest
  - analyze_correlations(): Matriz de correlación
  - generate_forecast_report(): Reporte completo
- *Fallback*: Métodos estadísticos simples si no hay scikit-learn

---

## 🗄️ Base de Datos

### Esquema MySQL

*Tabla: model*
- idModel: ID único del gráfico
- title: Título del gráfico
- nameLabelX: Etiqueta del eje X
- nameLabelY: Etiqueta del eje Y
- position: Orden de visualización
- nameNivel: Nombre de la variable en Vensim
- idColor: FK a tabla color

*Tabla: color*
- idColor: ID único
- nameColor: Nombre/hex del color

*Relación*: model.idColor → color.idColor

---

## 🔌 Integraciones Externas

### 1. *PySD (Python System Dynamics)*
- *Uso*: Parser de modelos Vensim (.mdl)
- *Funciones clave*:
  - pysd.read_vensim(): Lee archivo .mdl
  - model.run(): Ejecuta simulación
  - model.get_dependencies(): Obtiene estructura del modelo

### 2. *Plotly*
- *Uso*: Gráficos interactivos en frontend
- *Flujo*:
  - Backend genera JSON con fig.to_json()
  - Frontend renderiza con Plotly.newPlot()

### 3. *NetworkX + Matplotlib*
- *Uso*: Generación de diagramas
- *Proceso*: Grafo → Layout → Renderizado → Base64

### 4. *MySQL Connector*
- *Uso*: Conexión a base de datos
- *Configuración*: Variables de entorno (.env)

### 5. *APIs de IA* (Opcional)
- Google Gemini API
- OpenAI API
- Anthropic API

---

## 🎨 Frontend

### Tecnologías
- *Bootstrap 5.3*: Framework CSS
- *Plotly.js*: Gráficos interactivos
- *JavaScript Vanilla*: Lógica del cliente

### Características
- *Gráficos interactivos*: Zoom, pan, reset, descarga
- *Tema oscuro/claro*: Toggle de tema
- *Responsive*: Adaptable a móvil/tablet/desktop
- *Actualización dinámica*: AJAX para actualizar simulaciones

---

## 🔄 Patrones de Diseño Utilizados

### 1. *MVC (Model-View-Controller)*
- *Model*: src/Models/model.py
- *View*: templates/*.html
- *Controller*: src/Controllers/*.py

### 2. *Repository Pattern*
- Connection/connection.py abstrae acceso a BD

### 3. *Singleton Pattern*
- ScenarioManager y AIAssistant son instancias globales

### 4. *Strategy Pattern*
- Múltiples proveedores de IA (Gemini, OpenAI, Anthropic)

### 5. *Factory Pattern*
- Creación de gráficos según tipo (Forrester, Causal)

---

## 🔐 Seguridad

### Implementado
- Variables de entorno para credenciales (.env)
- Validación de parámetros en controladores
- Manejo de errores con try/except
- Headers de seguridad en respuestas HTTP

### Consideraciones
- API keys de IA almacenadas en variables de entorno
- Conexión MySQL con credenciales desde .env
- Ngrok token hardcodeado (considerar mover a .env)

---

## 📊 Modelo de Datos del Sistema

### Variables Principales (Stocks)
1. *Población Inmigrante*: Stock principal
2. *Inmigrantes Desempleados*: Stock derivado
3. *Delincuentes en la Calle*: Stock de seguridad
4. *Policías en Servicio*: Stock de recursos

### Flujos Principales
- Inmigrantes que llegan/se van
- Nuevos inmigrantes desempleados
- Inmigrantes que obtienen empleo
- Nuevos delincuentes
- Delincuentes arrestados/muertos
- Policías asignados/retirados

### Indicadores Calculados
- *Delincuentes por Policía*: Ratio de seguridad
- *Fracción de Arrestos*: Efectividad policial
- *Índice de Seguridad*: Indicador compuesto (0-100)

---

## 🚀 Flujo de Ejecución Típico

1. *Inicio*: Usuario accede a http://localhost:5000/
2. *Carga inicial*: 
   - route.py → controller.py
   - Lee BD → Obtiene configuración
   - Lee Vensim → Ejecuta simulación por defecto
   - Genera gráficos → Renderiza en template
3. *Interacción*:
   - Usuario ajusta parámetros (sliders)
   - JavaScript envía POST a /api/update-simulation
   - Backend recalcula con nuevos parámetros
   - Retorna JSON con nuevos gráficos
   - Frontend actualiza visualización
4. *Análisis*:
   - Usuario puede ver diagramas (Forrester/Causal)
   - Exportar datos (Excel/CSV/PDF)
   - Crear escenarios y comparar
   - Usar asistente AI para análisis
   - Realizar análisis predictivo

---

## 🛠️ Dependencias Principales

### Backend
- *Flask 2.0.2*: Framework web
- *PySD 3.14+*: Parser Vensim
- *mysql-connector-python 8.0.32*: Base de datos
- *Plotly 5.18+*: Gráficos
- *NetworkX 3.0+*: Grafos para diagramas
- *Matplotlib 3.7+*: Renderizado de diagramas
- *pandas 2.0+*: Manipulación de datos
- *numpy 1.24+*: Computación numérica
- *scikit-learn 1.3+*: Machine Learning (opcional)

### Frontend
- *Bootstrap 5.3*: CSS Framework
- *Plotly.js*: Gráficos interactivos (CDN)
- *JavaScript ES6+*: Lógica del cliente

### IA (Opcional)
- *google-generativeai*: Gemini API
- *openai*: OpenAI API
- *anthropic*: Claude API

---

## 📈 Escalabilidad y Rendimiento

### Optimizaciones Actuales
- *Caché de diagramas*: Headers Cache-Control en respuestas
- *Lazy loading*: Diagramas se generan bajo demanda
- *JSON eficiente*: Plotly genera JSON compacto

### Consideraciones Futuras
- Implementar caché Redis para simulaciones frecuentes
- Paralelización de simulaciones múltiples
- Compresión de respuestas JSON grandes
- CDN para archivos estáticos

---

## 🧪 Testing y Calidad

### Estado Actual
- Manejo de errores con try/except
- Validación de parámetros
- Mensajes de error descriptivos
- Logging básico con print()

### Mejoras Sugeridas
- Unit tests para controladores
- Integration tests para rutas
- Tests de carga para simulaciones
- Logging estructurado (logging module)

---

## 📝 Conclusión

Este proyecto implementa una *arquitectura modular y escalable* que separa claramente:
- *Presentación* (Templates + Static)
- *Lógica de negocio* (Controllers)
- *Acceso a datos* (Models + Connection)
- *Integraciones externas* (PySD, APIs de IA)

La arquitectura permite:
- ✅ Fácil mantenimiento
- ✅ Extensibilidad (nuevos controladores)
- ✅ Reutilización de componentes
- ✅ Separación de responsabilidades
- ✅ Testing independiente de capas

---

*Última actualización*: 2025
*Versión del proyecto*: 1.0