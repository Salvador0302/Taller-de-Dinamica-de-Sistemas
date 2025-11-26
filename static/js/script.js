// ================== ESTADO GLOBAL ==================
// initialData se define en template.html y está disponible globalmente

// ================== SISTEMA DE TEMAS ==================
const ThemeManager = {
    init() {
        this.theme = localStorage.getItem('theme') || 'dark';
        this.applyTheme(this.theme);
        this.setupToggle();
    },

    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        this.theme = theme;
        
        // Actualizar gráficos Plotly si existen
        this.updatePlotlyTheme();
    },

    toggle() {
        const newTheme = this.theme === 'dark' ? 'light' : 'dark';
        this.applyTheme(newTheme);
        
        // Animación suave
        document.body.style.transition = 'background 0.5s ease, color 0.3s ease';
    },

    setupToggle() {
        const toggle = document.getElementById('themeToggle');
        if (toggle) {
            toggle.addEventListener('click', () => this.toggle());
        }
    },

    updatePlotlyTheme() {
        // Actualizar colores de gráficos Plotly existentes
        const graphDivs = document.querySelectorAll('[id^="graph-"]');
        const isDark = this.theme === 'dark';
        
        graphDivs.forEach(div => {
            if (div._fullLayout) {
                Plotly.relayout(div, {
                    'paper_bgcolor': isDark ? '#020617' : '#ffffff',
                    'plot_bgcolor': isDark ? '#020617' : '#f8fafc',
                    'font.color': isDark ? 'white' : '#0f172a',
                    'xaxis.gridcolor': isDark ? 'rgba(31, 41, 55, 0.6)' : 'rgba(148, 163, 184, 0.3)',
                    'yaxis.gridcolor': isDark ? 'rgba(31, 41, 55, 0.6)' : 'rgba(148, 163, 184, 0.3)',
                    'xaxis.color': isDark ? 'white' : '#0f172a',
                    'yaxis.color': isDark ? 'white' : '#0f172a'
                });
            }
        });
    }
};

// ================== INICIALIZACIÓN ==================
window.addEventListener('load', function() {
    // Inicializar tema
    ThemeManager.init();
    
    var loadingScreen = document.getElementById('loading');
    var template = document.getElementById('graficos-container');
    
    loadingScreen.style.opacity = '0';
    setTimeout(function() {
        loadingScreen.style.display = 'none';
    }, 30);

    setTimeout(function() {
        template.style.display = 'block';
        // Animar entrada de cards
        animateCardsEntry();
    }, 50);

    setupParameterControls();
});

// ================== ANIMACIONES ==================
function animateCardsEntry() {
    const cards = document.querySelectorAll('.graph-card, .control-panel, .kpi-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = 'all 0.6s cubic-bezier(0.16, 1, 0.3, 1)';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 50);
    });
}

// ================== ACTUALIZACIÓN DE KPIs ==================
function updateKPIs(data) {
    if (!data || Object.keys(data).length === 0) return;
    
    // Mapeo de variables a IDs de KPI
    const kpiMapping = {
        'Delincuentes en la calle': 'kpi-delincuentes',
        'Policias en servicio': 'kpi-policias',
        'Inmigrantes desempleados': 'kpi-desempleados',
        'Poblacion inmigrante': 'kpi-poblacion'
    };
    
    for (const [varName, kpiId] of Object.entries(kpiMapping)) {
        if (data[varName]) {
            const values = Object.values(data[varName].data);
            if (values.length > 0) {
                const lastValue = values[values.length - 1];
                const firstValue = values[0];
                const change = ((lastValue - firstValue) / firstValue) * 100;
                
                // Actualizar valor
                const valueElement = document.getElementById(`${kpiId}-value`);
                if (valueElement) {
                    animateNumber(valueElement, firstValue, lastValue, 1000);
                }
                
                // Actualizar tendencia
                const trendElement = document.getElementById(`${kpiId}-trend`);
                if (trendElement) {
                    const trendValue = change >= 0 ? `+${change.toFixed(1)}%` : `${change.toFixed(1)}%`;
                    trendElement.textContent = trendValue;
                    
                    // Actualizar clase de tendencia
                    const trendContainer = trendElement.closest('.kpi-trend');
                    if (trendContainer) {
                        trendContainer.classList.remove('positive', 'negative', 'neutral');
                        
                        // Lógica específica por KPI
                        if (kpiId === 'kpi-delincuentes') {
                            // Para delincuentes, aumento es negativo
                            trendContainer.classList.add(change > 0 ? 'negative' : 'positive');
                        } else if (kpiId === 'kpi-policias') {
                            // Para policías, aumento es positivo
                            trendContainer.classList.add(change > 0 ? 'positive' : 'negative');
                        } else if (kpiId === 'kpi-desempleados') {
                            // Para desempleados, disminución es positiva
                            trendContainer.classList.add(change < 0 ? 'positive' : 'negative');
                        } else {
                            // Neutral para población
                            trendContainer.classList.add('neutral');
                        }
                    }
                }
            }
        }
    }
}

function animateNumber(element, start, end, duration) {
    const startTime = performance.now();
    const difference = end - start;
    
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function
        const easeOutQuart = 1 - Math.pow(1 - progress, 4);
        const current = start + (difference * easeOutQuart);
        
        element.textContent = Math.round(current).toLocaleString();
        
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    requestAnimationFrame(update);
}

// ==================  CONTROLES DE PARÁMETROS ==================
function setupParameterControls() {
    const sliders = document.querySelectorAll('.control-item input[type="range"]');
    sliders.forEach(slider => {
        const valueSpan = slider.nextElementSibling;
        slider.addEventListener('input', function() {
            valueSpan.textContent = parseFloat(this.value).toFixed(2);
        });
    });

    const updateBtn = document.getElementById('updateBtn');
    if (updateBtn) {
        updateBtn.addEventListener('click', updateSimulation);
    }
}

async function updateSimulation() {
    const updateBtn = document.getElementById('updateBtn');
    const originalText = updateBtn.innerHTML;
    
    updateBtn.disabled = true;
    updateBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Actualizando...';

    const params = {
        'tasa_de_inmigrantes': parseFloat(document.getElementById('tasa_inmigrantes').value),
        'tasa_de_emigrantes': parseFloat(document.getElementById('tasa_emigrantes').value),
        'tasa_de_desempleo': parseFloat(document.getElementById('tasa_desempleo').value),
        'tasa_de_nuevos_delincuentes': parseFloat(document.getElementById('tasa_nuevos_delincuentes').value),
        'tasa_de_muertes': parseFloat(document.getElementById('tasa_muertes').value),
        'tasa_de_policias_contratados': parseFloat(document.getElementById('tasa_policias_contratados').value)
    };

    try {
        const response = await fetch('/api/update-simulation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(params)
        });

        const result = await response.json();

        if (result.success) {
            updateGraphs(result.data);
            updateKPIs(result.data);
            showNotification('Simulación actualizada correctamente', 'success');
        } else {
            showNotification('Error: ' + result.error, 'error');
        }
    } catch (error) {
        showNotification('Error al actualizar la simulación: ' + error.message, 'error');
    } finally {
        updateBtn.disabled = false;
        updateBtn.innerHTML = originalText;
    }
}

// ================== ACTUALIZACIÓN DE GRÁFICOS PLOTLY ==================
function updateGraphs(data) {
    const graphsContainer = document.getElementById('graphs-container');
    
    if (!data || Object.keys(data).length === 0) {
        showNotification('No hay datos para mostrar', 'error');
        return;
    }
    
    graphsContainer.innerHTML = '';

    // Clear/update indicators area (if present)
    const indicatorsDiv = document.getElementById('indicators-graph');
    const indicadorTableBody = document.querySelector('#tablaModalIndicadores tbody');
    if (indicatorsDiv) indicatorsDiv.innerHTML = '';
    if (indicadorTableBody) indicadorTableBody.innerHTML = '';
    
    let index = 1;
    
    for (const [key, value] of Object.entries(data)) {
        // Si se trata del objeto 'Indicadores de Seguridad' lo manejamos en la sección dedicada
        if (key === 'Indicadores de Seguridad') {
            try {
                if (indicatorsDiv && value.plot_json) {
                    const plotData = JSON.parse(value.plot_json);
                    const config = {
                        responsive: true,
                        displayModeBar: true,
                        displaylogo: false,
                        modeBarButtonsToAdd: ['pan2d', 'zoom2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d'],
                        modeBarButtonsToRemove: ['select2d', 'lasso2d'],
                        toImageButtonOptions: {
                            format: 'png',
                            filename: (value.title || 'Indicadores').replace(/\s+/g, '_'),
                            height: 600,
                            width: 1000,
                            scale: 2
                        }
                    };
                    Plotly.newPlot('indicators-graph', plotData.data, plotData.layout, config);
                }

                // Llenar tabla de indicadores si viene el detalle
                if (indicadorTableBody && value.data) {
                    indicadorTableBody.innerHTML = Object.entries(value.data).map(([time, row]) => `
                        <tr>
                            <td>${time}</td>
                            <td>${parseFloat(row.Delincuentes_por_policia).toFixed(2)}</td>
                            <td>${parseFloat(row.Fraccion_arrestos).toFixed(4)}</td>
                            <td>${parseFloat(row.Indice_seguridad).toFixed(2)}</td>
                        </tr>
                    `).join('');
                }
            } catch (err) {
                console.warn('No se pudo renderizar indicadores:', err);
            }

            // saltar la lógica normal de creación de cards
            continue;
        }
        const col = document.createElement('div');
        col.className = 'col-12 col-lg-6 d-flex';
        
        const cardHTML = `
            <article class="graph-card flex-fill">
                <header class="graph-card-header">
                    <h5 class="graph-title">${value.title}</h5>
                    <div class="graph-controls">
                        <button class="btn btn-sm btn-outline-light table-icon" data-bs-toggle="modal" data-bs-target="#tablaModal${index}">
                            <i class="bi bi-table"></i>
                            <span class="d-none d-sm-inline">Ver datos</span>
                        </button>
                    </div>
                </header>
                <div class="graph-body" id="graph-${index}"></div>
            </article>

            <div class="modal fade" id="tablaModal${index}" tabindex="-1">
                <div class="modal-dialog modal-dialog-centered modal-lg">
                    <div class="modal-content modal-glass">
                        <div class="modal-header">
                            <h5 class="modal-title">${value.title}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="table-responsive">
                                <table class="table table-dark table-striped table-hover align-middle mb-0">
                                    <thead>
                                        <tr>
                                            <th>${value.xlabel}</th>
                                            <th>${value.ylabel}</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${Object.entries(value.data).map(([date, val]) => `
                                            <tr>
                                                <td>${date}</td>
                                                <td>${Math.round(val)}</td>
                                            </tr>
                                        `).join('')}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-outline-light" data-bs-dismiss="modal">Cerrar</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        col.innerHTML = cardHTML;
        graphsContainer.appendChild(col);
        
        // Renderizar gráfico Plotly
        const plotData = JSON.parse(value.plot_json);
        
        // Configurar opciones de Plotly
        const config = {
            responsive: true,
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToAdd: ['pan2d', 'zoom2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d'],
            modeBarButtonsToRemove: ['select2d', 'lasso2d'],
            toImageButtonOptions: {
                format: 'png',
                filename: value.title.replace(/\s+/g, '_'),
                height: 600,
                width: 1000,
                scale: 2
            }
        };
        
        Plotly.newPlot(`graph-${index}`, plotData.data, plotData.layout, config);
        
        index++;
    }
}

// ================== NOTIFICACIONES ==================
function showNotification(message, type) {
    const toast = document.createElement('div');
    toast.className = `notification-toast ${type}`;
    toast.innerHTML = `
        <i class="bi bi-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('show');
    }, 100);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ================== EXPORTACIÓN DE DATOS ==================
async function exportData(format) {
    try {
        showNotification(`Generando archivo ${format.toUpperCase()}...`, 'success');
        
        // Obtener datos actuales de la simulación
        const currentData = getCurrentSimulationData();
        const parameters = getCurrentParameters();
        
        const response = await fetch(`/api/export/${format}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                data: currentData,
                parameters: parameters
            })
        });
        
        if (!response.ok) {
            throw new Error('Error en la exportación');
        }
        
        // Descargar archivo
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        
        // Determinar extensión
        const extension = format === 'excel' ? 'xlsx' : format;
        const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
        a.download = `simulacion_${timestamp}.${extension}`;
        
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showNotification(`Archivo ${format.toUpperCase()} descargado exitosamente`, 'success');
    } catch (error) {
        console.error('Error exportando:', error);
        showNotification('Error al exportar: ' + error.message, 'error');
    }
}

function getCurrentSimulationData() {
    // Obtener datos desde el objeto global inicialData o desde gráficos
    if (typeof initialData !== 'undefined') {
        return initialData;
    }
    return {};
}

function getCurrentParameters() {
    return {
        'tasa_de_inmigrantes': parseFloat(document.getElementById('tasa_inmigrantes')?.value || 0.12),
        'tasa_de_emigrantes': parseFloat(document.getElementById('tasa_emigrantes')?.value || 0.1),
        'tasa_de_desempleo': parseFloat(document.getElementById('tasa_desempleo')?.value || 0.14),
        'tasa_de_nuevos_delincuentes': parseFloat(document.getElementById('tasa_nuevos_delincuentes')?.value || 0.21),
        'tasa_de_muertes': parseFloat(document.getElementById('tasa_muertes')?.value || 0.18),
        'tasa_de_policias_contratados': parseFloat(document.getElementById('tasa_policias_contratados')?.value || 0.15)
    };
}

async function exportAllGraphs() {
    try {
        showNotification('Descargando todos los gráficos...', 'success');
        
        const graphDivs = document.querySelectorAll('[id^="graph-"]');
        let count = 0;
        
        for (const div of graphDivs) {
            if (div._fullData && div._fullData.length > 0) {
                const title = div._fullData[0].name || `grafico_${count + 1}`;
                await Plotly.downloadImage(div, {
                    format: 'png',
                    width: 1200,
                    height: 800,
                    filename: title.replace(/\s+/g, '_')
                });
                count++;
                
                // Esperar un poco entre descargas
                await new Promise(resolve => setTimeout(resolve, 500));
            }
        }
        
        showNotification(`${count} gráficos descargados exitosamente`, 'success');
    } catch (error) {
        console.error('Error descargando gráficos:', error);
        showNotification('Error al descargar gráficos: ' + error.message, 'error');
    }
}

// ================== FUNCIONES LEGACY (mantener compatibilidad) ==================
// Estas funciones ya no son necesarias con Plotly, pero las mantenemos por si acaso
function zoomGraph(graphId, direction) {
    // Plotly maneja el zoom nativamente
    console.log('Zoom nativo de Plotly activo');
}

function resetGraph(graphId) {
    // Plotly maneja el reset nativamente
    console.log('Reset nativo de Plotly activo');
}

function downloadGraph(graphId) {
    // Plotly maneja la descarga nativamente
    console.log('Descarga nativa de Plotly activa');
}

// ================== GESTIÓN DE ESCENARIOS ==================
const ScenarioManager = {
    scenarios: [],
    selectedForComparison: new Set(),
    
    init() {
        this.loadScenariosFromStorage();
        this.setupEventListeners();
    },
    
    setupEventListeners() {
        // Crear escenario
        const createForm = document.getElementById('createScenarioForm');
        if (createForm) {
            createForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.createScenario();
            });
        }
        
        // Comparar escenarios
        const compareBtn = document.getElementById('compareBtn');
        if (compareBtn) {
            compareBtn.addEventListener('click', () => this.compareScenarios());
        }
        
        // Actualizar lista al abrir pestaña
        document.querySelectorAll('button[data-bs-toggle="tab"]').forEach(btn => {
            btn.addEventListener('shown.bs.tab', (e) => {
                if (e.target.id === 'list-tab') {
                    this.renderScenariosList();
                } else if (e.target.id === 'compare-tab') {
                    this.renderCompareList();
                }
            });
        });
    },
    
    async createScenario() {
        const name = document.getElementById('scenarioName').value;
        const description = document.getElementById('scenarioDescription').value;
        const parameters = getCurrentParameters();
        
        try {
            showNotification('Creando escenario...', 'success');
            
            const response = await fetch('/api/scenarios/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, description, parameters })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.scenarios.push(result.scenario);
                this.saveScenariosToStorage();
                showNotification('Escenario creado exitosamente', 'success');
                
                // Limpiar formulario
                document.getElementById('createScenarioForm').reset();
                
                // Cambiar a pestaña de lista
                document.getElementById('list-tab').click();
            } else {
                showNotification('Error: ' + result.error, 'error');
            }
        } catch (error) {
            console.error('Error creando escenario:', error);
            showNotification('Error al crear escenario', 'error');
        }
    },
    
    renderScenariosList() {
        const container = document.getElementById('scenariosList');
        if (!container) return;
        
        if (this.scenarios.length === 0) {
            container.innerHTML = `
                <div class="alert alert-info">
                    <i class="bi bi-info-circle"></i>
                    No hay escenarios guardados. Crea uno en la pestaña "Crear Escenario".
                </div>
            `;
            return;
        }
        
        container.innerHTML = this.scenarios.map(scenario => `
            <div class="scenario-card">
                <div class="scenario-card-header">
                    <h6 class="scenario-card-title">${scenario.name}</h6>
                    <div class="scenario-card-actions">
                        <button class="btn btn-sm btn-primary" onclick="ScenarioManager.loadScenario('${scenario.id}')">
                            <i class="bi bi-play-fill"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="ScenarioManager.deleteScenario('${scenario.id}')">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>
                <p class="scenario-card-description">${scenario.description || 'Sin descripción'}</p>
                <div class="scenario-card-meta">
                    <div><strong>Creado:</strong> ${new Date(scenario.created_at).toLocaleString()}</div>
                    <div><strong>Parámetros:</strong></div>
                    ${Object.entries(scenario.parameters || {}).map(([key, value]) => 
                        `<div style="margin-left: 1rem;">• ${key}: ${value}</div>`
                    ).join('')}
                </div>
            </div>
        `).join('');
    },
    
    renderCompareList() {
        const container = document.getElementById('compareScenariosList');
        if (!container) return;
        
        if (this.scenarios.length < 2) {
            container.innerHTML = `
                <div class="alert alert-warning">
                    <i class="bi bi-exclamation-triangle"></i>
                    Necesitas al menos 2 escenarios para comparar. Crea más escenarios primero.
                </div>
            `;
            return;
        }
        
        container.innerHTML = this.scenarios.map(scenario => `
            <div class="compare-scenario-item">
                <input type="checkbox" 
                       id="compare-${scenario.id}" 
                       value="${scenario.id}"
                       onchange="ScenarioManager.toggleCompareSelection('${scenario.id}')">
                <div class="compare-scenario-info">
                    <div class="compare-scenario-name">${scenario.name}</div>
                    <div class="compare-scenario-params">
                        ${Object.entries(scenario.parameters || {})
                            .slice(0, 3)
                            .map(([k, v]) => `${k}: ${v}`)
                            .join(' | ')}
                    </div>
                </div>
            </div>
        `).join('');
    },
    
    toggleCompareSelection(scenarioId) {
        const checkbox = document.getElementById(`compare-${scenarioId}`);
        if (checkbox.checked) {
            this.selectedForComparison.add(scenarioId);
        } else {
            this.selectedForComparison.delete(scenarioId);
        }
        
        // Habilitar/deshabilitar botón de comparación
        const compareBtn = document.getElementById('compareBtn');
        compareBtn.disabled = this.selectedForComparison.size < 2;
    },
    
    async compareScenarios() {
        const scenarioIds = Array.from(this.selectedForComparison);
        
        if (scenarioIds.length < 2) {
            showNotification('Selecciona al menos 2 escenarios', 'error');
            return;
        }
        
        try {
            showNotification('Comparando escenarios...', 'success');
            
            const response = await fetch('/api/scenarios/compare', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ scenario_ids: scenarioIds })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.renderComparison(result.comparison);
                showNotification('Comparación completada', 'success');
            } else {
                showNotification('Error: ' + result.error, 'error');
            }
        } catch (error) {
            console.error('Error comparando escenarios:', error);
            showNotification('Error al comparar escenarios', 'error');
        }
    },
    
    renderComparison(comparison) {
        const resultsDiv = document.getElementById('comparisonResults');
        const chartsDiv = document.getElementById('comparisonCharts');
        
        if (!resultsDiv || !chartsDiv) return;
        
        resultsDiv.style.display = 'block';
        chartsDiv.innerHTML = '';
        
        // Crear un gráfico por variable
        comparison.variables.forEach((varName, index) => {
            const chartContainer = document.createElement('div');
            chartContainer.className = 'comparison-chart-container';
            chartContainer.id = `comparison-chart-${index}`;
            chartsDiv.appendChild(chartContainer);
            
            const traces = [];
            const varData = comparison.comparative_data[varName] || [];
            
            // Colores para distinguir escenarios
            const colors = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#06b6d4'];
            
            varData.forEach((scenarioData, idx) => {
                const xValues = Object.keys(scenarioData.data);
                const yValues = Object.values(scenarioData.data);
                
                traces.push({
                    x: xValues,
                    y: yValues,
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: scenarioData.scenario_name,
                    line: {
                        color: colors[idx % colors.length],
                        width: 3
                    },
                    marker: {
                        size: 6
                    }
                });
            });
            
            const layout = {
                title: {
                    text: varData[0]?.title || varName,
                    font: { 
                        size: 16, 
                        color: getComputedStyle(document.body).getPropertyValue('--text-primary').trim()
                    },
                    x: 0.5,
                    xanchor: 'center'
                },
                xaxis: {
                    title: varData[0]?.xlabel || 'Tiempo',
                    gridcolor: 'rgba(148, 163, 184, 0.2)',
                    color: getComputedStyle(document.body).getPropertyValue('--text-secondary').trim()
                },
                yaxis: {
                    title: varData[0]?.ylabel || 'Valor',
                    gridcolor: 'rgba(148, 163, 184, 0.2)',
                    color: getComputedStyle(document.body).getPropertyValue('--text-secondary').trim()
                },
                paper_bgcolor: 'transparent',
                plot_bgcolor: 'transparent',
                font: { 
                    family: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
                    color: getComputedStyle(document.body).getPropertyValue('--text-primary').trim()
                },
                legend: {
                    orientation: 'v',
                    yanchor: 'top',
                    y: 0.99,
                    xanchor: 'right',
                    x: 0.99,
                    bgcolor: 'rgba(15, 23, 42, 0.8)',
                    bordercolor: 'rgba(148, 163, 184, 0.3)',
                    borderwidth: 1
                },
                hovermode: 'x unified',
                margin: {
                    t: 80,
                    r: 20,
                    b: 60,
                    l: 80
                },
                height: 450,
                autosize: true
            };
            
            const config = {
                responsive: true,
                displayModeBar: true,
                displaylogo: false,
                modeBarButtonsToRemove: ['select2d', 'lasso2d']
            };
            
            Plotly.newPlot(`comparison-chart-${index}`, traces, layout, config);
        });
    },
    
    loadScenario(scenarioId) {
        const scenario = this.scenarios.find(s => s.id === scenarioId);
        if (!scenario) return;
        
        // Cargar parámetros en los sliders
        Object.entries(scenario.parameters).forEach(([key, value]) => {
            const slider = document.getElementById(key);
            if (slider) {
                slider.value = value;
                const valueSpan = slider.parentElement.querySelector('.control-value');
                if (valueSpan) {
                    valueSpan.textContent = value;
                }
            }
        });
        
        // Actualizar simulación
        document.getElementById('updateBtn').click();
        
        // Cerrar modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('scenarioModal'));
        if (modal) modal.hide();
        
        showNotification(`Escenario "${scenario.name}" cargado`, 'success');
    },
    
    deleteScenario(scenarioId) {
        if (!confirm('¿Estás seguro de eliminar este escenario?')) return;
        
        this.scenarios = this.scenarios.filter(s => s.id !== scenarioId);
        this.saveScenariosToStorage();
        this.renderScenariosList();
        showNotification('Escenario eliminado', 'success');
    },
    
    saveScenariosToStorage() {
        try {
            localStorage.setItem('simulation_scenarios', JSON.stringify(this.scenarios));
        } catch (error) {
            console.error('Error guardando escenarios:', error);
        }
    },
    
    loadScenariosFromStorage() {
        try {
            const stored = localStorage.getItem('simulation_scenarios');
            if (stored) {
                this.scenarios = JSON.parse(stored);
            }
        } catch (error) {
            console.error('Error cargando escenarios:', error);
            this.scenarios = [];
        }
    }
};

// Inicializar gestor de escenarios cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    ScenarioManager.init();
});

// ================== ASISTENTE AI ==================
function toggleAIAssistant() {
    const panel = document.getElementById('aiPanel');
    const toggle = document.getElementById('aiToggle');
    
    if (panel.classList.contains('active')) {
        panel.classList.remove('active');
        toggle.style.display = 'flex';
    } else {
        panel.classList.add('active');
        toggle.style.display = 'none';
    }
}

const AIAssistantManager = {
    messages: [],
    isProcessing: false,
    
    init() {
        // Cargar historial si existe
        this.loadHistory();
    },
    
    async sendMessage() {
        const input = document.getElementById('aiInput');
        const question = input.value.trim();
        
        if (!question || this.isProcessing) return;
        
        // Agregar mensaje del usuario
        this.addMessage('user', question);
        input.value = '';
        
        // Mostrar indicador de carga
        this.showTypingIndicator();
        this.isProcessing = true;
        
        try {
            const context = this.prepareContext();
            
            const response = await fetch('/api/ai/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    question: question,
                    context: context
                })
            });
            
            const result = await response.json();
            
            this.hideTypingIndicator();
            
            if (result.success) {
                this.addMessage('assistant', result.answer);
            } else {
                this.addMessage('assistant', 'Lo siento, ocurrió un error: ' + result.error);
            }
        } catch (error) {
            this.hideTypingIndicator();
            console.error('Error:', error);
            this.addMessage('assistant', 'Lo siento, no pude procesar tu pregunta en este momento.');
        } finally {
            this.isProcessing = false;
        }
    },
    
    async analyzeSimulation() {
        if (this.isProcessing) return;
        
        this.addMessage('user', '🔍 Analizar simulación actual');
        this.showTypingIndicator();
        this.isProcessing = true;
        
        try {
            const simulationData = typeof initialData !== 'undefined' ? initialData : {};
            const parameters = getCurrentParameters();
            
            const response = await fetch('/api/ai/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    simulation_data: simulationData,
                    parameters: parameters
                })
            });
            
            const result = await response.json();
            
            this.hideTypingIndicator();
            
            if (result.success) {
                this.addMessage('assistant', result.analysis);
                if (result.is_fallback) {
                    showNotification('Análisis básico generado. Configura API key para análisis con IA.', 'info');
                }
            } else {
                this.addMessage('assistant', 'Error al analizar: ' + result.error);
            }
        } catch (error) {
            this.hideTypingIndicator();
            console.error('Error:', error);
            this.addMessage('assistant', 'No pude completar el análisis.');
        } finally {
            this.isProcessing = false;
        }
    },
    
    showSuggestionForm() {
        const form = document.getElementById('aiSuggestionForm');
        form.style.display = 'block';
    },
    
    hideSuggestionForm() {
        const form = document.getElementById('aiSuggestionForm');
        form.style.display = 'none';
    },
    
    async requestSuggestions() {
        const goalSelect = document.getElementById('aiGoalSelect');
        const goal = goalSelect.value;
        
        if (!goal || this.isProcessing) return;
        
        this.hideSuggestionForm();
        this.addMessage('user', `💡 Sugerir parámetros para: ${goal}`);
        this.showTypingIndicator();
        this.isProcessing = true;
        
        try {
            const currentParams = getCurrentParameters();
            const simulationData = typeof initialData !== 'undefined' ? initialData : null;
            
            const response = await fetch('/api/ai/suggest-parameters', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    current_params: currentParams,
                    goal: goal,
                    simulation_data: simulationData
                })
            });
            
            const result = await response.json();
            
            this.hideTypingIndicator();
            
            if (result.success) {
                const suggestions = result.suggestions;
                let message = `### 💡 Sugerencias para: ${goal}\n\n`;
                
                if (suggestions.recommendations && suggestions.recommendations.length > 0) {
                    message += '**Recomendaciones de Parámetros:**\n\n';
                    suggestions.recommendations.forEach((rec, idx) => {
                        message += `${idx + 1}. **${rec.parameter}**\n`;
                        message += `   - Valor actual: ${rec.current_value}\n`;
                        message += `   - Valor sugerido: ${rec.suggested_value}\n`;
                        message += `   - Razonamiento: ${rec.reasoning}\n`;
                        message += `   - Impacto esperado: ${rec.expected_impact}\n\n`;
                    });
                }
                
                if (suggestions.overall_strategy) {
                    message += `\n**Estrategia General:**\n${suggestions.overall_strategy}\n`;
                }
                
                if (suggestions.expected_outcome) {
                    message += `\n**Resultado Esperado:**\n${suggestions.expected_outcome}`;
                }
                
                this.addMessage('assistant', message);
                
                if (result.is_fallback) {
                    showNotification('Sugerencias básicas generadas. Configura API key para sugerencias con IA.', 'info');
                }
            } else {
                this.addMessage('assistant', 'Error al generar sugerencias: ' + result.error);
            }
        } catch (error) {
            this.hideTypingIndicator();
            console.error('Error:', error);
            this.addMessage('assistant', 'No pude generar sugerencias.');
        } finally {
            this.isProcessing = false;
        }
    },
    
    addMessage(role, content) {
        const container = document.getElementById('aiChatContainer');
        
        // Remover mensaje de bienvenida si existe
        const welcome = container.querySelector('.ai-welcome-message');
        if (welcome) {
            welcome.remove();
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `ai-message ${role}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'ai-message-avatar';
        avatar.innerHTML = role === 'user' ? '<i class="bi bi-person"></i>' : '<i class="bi bi-robot"></i>';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'ai-message-content';
        contentDiv.innerHTML = this.formatMessage(content);
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(contentDiv);
        
        container.appendChild(messageDiv);
        container.scrollTop = container.scrollHeight;
        
        // Guardar en historial
        this.messages.push({ role, content, timestamp: new Date().toISOString() });
        this.saveHistory();
    },
    
    formatMessage(text) {
        // Formato básico de markdown
        let formatted = text
            // Headers
            .replace(/^### (.+)$/gm, '<h6>$1</h6>')
            .replace(/^## (.+)$/gm, '<h5>$1</h5>')
            // Bold
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
            // Listas
            .replace(/^- (.+)$/gm, '<li>$1</li>')
            .replace(/^(\d+)\. (.+)$/gm, '<li>$2</li>')
            // Saltos de línea
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>');
        
        // Envolver listas
        formatted = formatted.replace(/(<li>.+<\/li>)/g, '<ul>$1</ul>');
        
        return '<p>' + formatted + '</p>';
    },
    
    showTypingIndicator() {
        const container = document.getElementById('aiChatContainer');
        const indicator = document.createElement('div');
        indicator.className = 'ai-message assistant';
        indicator.id = 'typingIndicator';
        indicator.innerHTML = `
            <div class="ai-message-avatar">
                <i class="bi bi-robot"></i>
            </div>
            <div class="ai-message-content">
                <div class="ai-message-loading">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        container.appendChild(indicator);
        container.scrollTop = container.scrollHeight;
    },
    
    hideTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) {
            indicator.remove();
        }
    },
    
    clearChat() {
        if (!confirm('¿Limpiar toda la conversación?')) return;
        
        const container = document.getElementById('aiChatContainer');
        container.innerHTML = `
            <div class="ai-welcome-message">
                <i class="bi bi-stars"></i>
                <h6>¡Hola! Soy tu asistente AI</h6>
                <p>Puedo ayudarte a:</p>
                <ul>
                    <li>Analizar resultados de simulaciones</li>
                    <li>Sugerir ajustes de parámetros</li>
                    <li>Explicar tendencias y relaciones</li>
                    <li>Responder tus preguntas</li>
                </ul>
                <div class="ai-quick-actions">
                    <button class="btn btn-sm btn-primary" onclick="AIAssistantManager.analyzeSimulation()">
                        <i class="bi bi-graph-up"></i> Analizar Simulación
                    </button>
                    <button class="btn btn-sm btn-info" onclick="AIAssistantManager.showSuggestionForm()">
                        <i class="bi bi-lightbulb"></i> Sugerir Parámetros
                    </button>
                </div>
            </div>
        `;
        
        this.messages = [];
        this.saveHistory();
        showNotification('Conversación limpiada', 'success');
    },
    
    prepareContext() {
        const simulationData = typeof initialData !== 'undefined' ? initialData : {};
        const parameters = getCurrentParameters();
        
        return {
            simulation_data: simulationData,
            parameters: parameters
        };
    },
    
    saveHistory() {
        try {
            localStorage.setItem('ai_chat_history', JSON.stringify(this.messages));
        } catch (error) {
            console.error('Error saving history:', error);
        }
    },
    
    loadHistory() {
        try {
            const stored = localStorage.getItem('ai_chat_history');
            if (stored) {
                this.messages = JSON.parse(stored);
                // No restaurar mensajes automáticamente para mantener UI limpia
            }
        } catch (error) {
            console.error('Error loading history:', error);
        }
    }
};

// Inicializar asistente AI
document.addEventListener('DOMContentLoaded', function() {
    AIAssistantManager.init();
});
