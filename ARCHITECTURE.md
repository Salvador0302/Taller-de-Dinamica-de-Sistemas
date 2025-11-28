# Arquitectura del Sistema

Este documento describe la arquitectura técnica del proyecto "Taller-de-Dinamica-de-Sistemas" y cómo se organizan sus componentes, flujos de datos, rutas y dependencias.

## Visión General

- Tipo de aplicación: Dashboard web interactivo para simulación de modelos Vensim (dinámica de sistemas).
- Backend: Flask (Python) + PySD para ejecutar modelos `.mdl`.
- Frontend: Bootstrap + Plotly con plantillas Jinja2.
- Datos: MySQL para metadatos de gráficos y configuración.
- Diagramas: Generación server-side de Forrester y causal con NetworkX y Matplotlib.

## Estructura de Carpetas

```
Taller-de-Dinamica-de-Sistemas/
├── app.py                        # Entrypoint Flask y bootstrap de rutas
├── requirements.txt              # Dependencias
├── README.md                     # Guía de uso
├── ARCHITECTURE.md               # Este documento
│
├── Connection/
│   └── connection.py            # Conexión a MySQL (python-decouple)
│
├── src/
│   ├── Controllers/             # Lógica de negocio
│   │   ├── controller.py        # Ejecuta modelo Vensim (PySD) y arma gráficas
│   │   ├── diagram_generator.py # Genera diagramas Forrester y causal (PNG)
│   │   ├── export_controller.py # Exporta datos (Excel/CSV/PDF)
│   │   ├── scenario_controller.py # CRUD y comparación de escenarios
│   │   ├── ai_assistant_controller.py # Endpoints AI (Gemini/heurísticas)
│   │   └── predictive_controller.py  # Análisis predictivo (correlaciones, forecast)
│   ├── Models/
│   │   └── model.py             # Consultas a BD (SELECTs)
│   └── Routes/
│       └── route.py             # Definición de rutas Flask
│
├── static/
│   ├── css/                     # Estilos
│   ├── js/                      # Interactividad (Plotly, KPIs, escenarios, AI)
│   ├── images/                  # Salidas de diagramas (si se usan persistentes)
│   └── vensim/                  # Modelos `.mdl` y relacionados
│
└── templates/
    ├── template.html            # Página principal (gráficos + controles)
    ├── diagrama_causal.html     # Vista de diagrama causal
    ├── diagrama_forrester.html  # Vista de diagrama Forrester
    └── error.html               # Página de error
```

## Componentes Principales

- `app.py`
  - Carga variables de entorno (`dotenv`).
  - Inicializa Flask y registra rutas con `modelRoute(app)`.
  - Arranque del servidor (`app.run`).
  - Opcional: integración Ngrok (recomendado mover token a `.env`).

- `src/Routes/route.py`
  - Rutas UI:
    - `/` Render de `template.html` con datos iniciales.
    - `/diagrama-causal`, `/diagrama-forrester` renderizan diagramas como imágenes base64.
  - API de simulación: `/api/update-simulation` (POST) recibe parámetros de sliders, ejecuta modelo y devuelve datos.
  - Exportaciones: `/api/export/excel|csv|pdf`.
  - Escenarios: `create`, `list`, `get`, `compare`, `delete`, `export`, `import`.
  - AI Assistant: `analyze`, `ask`, `suggest-parameters`, `history`, `clear-history`.
  - Predictivo: `forecast`, `anomalies`, `correlations`, `report`.

- `src/Controllers/controller.py`
  - Lee el modelo Vensim `static/vensim/taller5_forrester.mdl` con PySD.
  - Ejecuta `model.run(params)` con parámetros opcionales desde sliders.
  - Construye objetos para el frontend: datos tabulares y gráficos Plotly (JSON) por variable.
  - Calcula indicadores derivados ("Indicadores de Seguridad").
  - Valida la existencia de variables en el modelo y retorna errores con sugerencias.

- `src/Controllers/diagram_generator.py`
  - Usa `pysd.read_vensim` y `networkx` + `matplotlib` para diagramas.
  - Por ahora define nodos y relaciones principales de forma explícita (hardcode) basadas en el modelo incluido.
  - Devuelve imágenes en base64 para inserción en HTML.

- `src/Models/model.py` y `Connection/connection.py`
  - Conexión a MySQL (`host`, `port`, `user`, `password`, `database` desde `.env`).
  - Consulta `model` unida a `color` para metadatos: títulos, etiquetas, orden y color por variable.

- `templates/template.html`
  - Estructura UI (Bootstrap), contenedor de gráficos, KPIs y panel de parámetros.
  - Inserta `initialData` y renderiza con Plotly en cliente.
  - Modales de tablas por gráfico, sección de indicadores y modales de escenarios.

- `static/js/script.js`
  - Tema oscuro/claro; render y relayout Plotly.
  - Actualización de simulación vía `/api/update-simulation` y re-render dinámico.
  - KPIs, notificaciones, exportaciones, gestión de escenarios (localStorage + API), panel AI.

## Flujo de Datos

1. Al cargar `/`, backend ejecuta `controller()`:
   - Lee BD (`getModelAll`) para metadatos de gráficos.
   - Carga y corre el modelo `.mdl` con PySD.
   - Retorna estructura `nivel` con datos y `plot_json` por variable + indicadores.
2. `template.html` inserta `nivel` y Renderiza Plotly en cliente.
3. Usuario ajusta sliders y pulsa "Actualizar simulación":
   - Frontend envía `POST /api/update-simulation` con parámetros.
   - Backend corre `model.run(params)` y devuelve nuevos `nivel`.
   - Frontend re-renderiza gráficos y actualiza KPIs.
4. Exportaciones invocan endpoints que generan archivos en memoria y los descargan.
5. Diagramas se generan en backend y se embeben como imágenes base64 en sus vistas.

## Dependencias Clave

- Flask 2.0.x, Werkzeug.
- PySD (>=3.14) para leer/ejecutar Vensim.
- Plotly (cliente) y `kaleido` (si se exportan imágenes server-side).
- NetworkX + Matplotlib para diagramas.
- MySQL Connector, python-decouple / dotenv.
- Opcionales: `reportlab` (PDF), `google-generativeai` (AI), `pyngrok`.

## Consideraciones y Mejores Prácticas

- Seguridad
  - No hardcodear tokens (Ngrok, APIs). Usar `.env` (`NGROK_AUTH_TOKEN`).
  - Evitar `ssl._create_unverified_context`; mantener verificación TLS.
- Configuración
  - Validar existencia de `.env` y manejo de errores en conexión a BD.
  - `app.run` no admite `exclude_patterns`; remover o usar `use_reloader=True`.
- Performance
  - Cachear `pysd.read_vensim()` y reutilizar el objeto del modelo.
  - Validar rangos de sliders y parámetros antes de ejecutar.
- Diagramas
  - Considerar generar nodos y aristas desde `model.get_dependencies()` para evitar hardcode.
- Frontend
  - Proteger cálculos de KPIs ante divisiones por cero.
  - Proveer feedback de carga por gráfico al actualizar simulación.

## Endpoints Principales

- UI: `/`, `/diagrama-causal`, `/diagrama-forrester`.
- Simulación: `POST /api/update-simulation`.
- Exportación: `POST /api/export/excel`, `POST /api/export/csv`, `POST /api/export/pdf`.
- Escenarios: `POST /api/scenarios/create`, `GET /api/scenarios/list`, `GET /api/scenarios/get/<id>`, `POST /api/scenarios/compare`, `DELETE /api/scenarios/delete/<id>`, `GET /api/scenarios/export/<id>`, `POST /api/scenarios/import`.
- AI: `POST /api/ai/analyze`, `POST /api/ai/ask`, `POST /api/ai/suggest-parameters`, `GET /api/ai/history`, `POST /api/ai/clear-history`.
- Predictivo: `POST /api/predictive/forecast`, `POST /api/predictive/anomalies`, `POST /api/predictive/correlations`, `POST /api/predictive/report`.

## Diagrama (alto nivel)

```
[Usuario/Browser]
   ↕ HTTP
[Flask app.py] —› [Routes/route.py]
   ↳ Controllers:
       - controller.py (PySD model.run)
       - diagram_generator.py (NetworkX/Matplotlib)
       - export_controller.py (Excel/CSV/PDF)
       - scenario_controller.py (CRUD + compare)
       - ai_assistant_controller.py (IA)
       - predictive_controller.py (análisis)
   ↳ Models/model.py —› Connection/connection.py —› MySQL
   ↳ Templates/*.html —› static/js/script.js —› Plotly
```

## Estado Actual y Próximos Pasos

- Arquitectura funcional y modular.
- Mejoras prioritarias: seguridad (tokens/.env), performance (cache PySD), limpieza de `app.run`, uso dinámico de dependencias para diagramas.
- Opcional: documentación de contratos de datos (`nivel` y formatos de exportación) y pruebas unitarias para controladores.
