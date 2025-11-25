window.addEventListener('load', function() {
    var loadingScreen = document.getElementById('loading');
    var template = document.getElementById('graficos-container');
    
    loadingScreen.style.opacity = '0';
    // Esperar a que finalice la transición antes de ocultar completamente la pantalla de carga
    setTimeout(function() {
        loadingScreen.style.display = 'none';
    }, 30); // Duración de la transición (ajusta según sea necesario)

    // Mostrar los gráficos una vez que la pantalla de carga esté completamente oculta
    setTimeout(function() {
        template.style.display = 'block';
    }, 50); // Duración de la transición (ajusta según sea necesario)

    // Configurar controles de parámetros
    setupParameterControls();
});

function setupParameterControls() {
    // Actualizar valores mostrados cuando se mueven los sliders
    const sliders = document.querySelectorAll('.control-item input[type="range"]');
    sliders.forEach(slider => {
        const valueSpan = slider.nextElementSibling;
        slider.addEventListener('input', function() {
            valueSpan.textContent = parseFloat(this.value).toFixed(2);
        });
    });

    // Botón de actualizar simulación
    const updateBtn = document.getElementById('updateBtn');
    if (updateBtn) {
        updateBtn.addEventListener('click', updateSimulation);
    }
}

async function updateSimulation() {
    const updateBtn = document.getElementById('updateBtn');
    const originalText = updateBtn.innerHTML;
    
    // Deshabilitar botón y mostrar loading
    updateBtn.disabled = true;
    updateBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Actualizando...';

    // Recopilar parámetros (usar guiones bajos como en PySD)
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
            // Actualizar gráficos con nuevos datos
            updateGraphs(result.data);
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

function updateGraphs(data) {
    const graphsContainer = document.getElementById('graphs-container');
    
    if (!data || Object.keys(data).length === 0) {
        showNotification('No hay datos para mostrar', 'error');
        return;
    }
    
    // Limpiar contenedor
    graphsContainer.innerHTML = '';
    
    let index = 1;
    
    for (const [key, value] of Object.entries(data)) {
        // Crear columna
        const col = document.createElement('div');
        col.className = 'col-12 col-lg-6 d-flex';
        
        // Crear contenido HTML
        const cardHTML = `
            <article class="graph-card flex-fill">
                <header class="graph-card-header">
                    <h5 class="graph-title">${value.title}</h5>
                    <div class="graph-controls">
                        <button class="graph-btn" title="Zoom In" onclick="zoomGraph(${index}, 'in')">
                            <i class="bi bi-zoom-in"></i>
                        </button>
                        <button class="graph-btn" title="Zoom Out" onclick="zoomGraph(${index}, 'out')">
                            <i class="bi bi-zoom-out"></i>
                        </button>
                        <button class="graph-btn" title="Resetear Vista" onclick="resetGraph(${index})">
                            <i class="bi bi-arrow-counterclockwise"></i>
                        </button>
                        <button class="graph-btn" title="Descargar PNG" onclick="downloadGraph(${index})">
                            <i class="bi bi-download"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-light table-icon" data-bs-toggle="modal" data-bs-target="#tablaModal${index}">
                            <i class="bi bi-table"></i>
                            <span class="d-none d-sm-inline">Ver datos</span>
                        </button>
                    </div>
                </header>
                <div class="graph-body" id="graph-body-${index}" data-graph-id="${index}">
                </div>
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
        
        // Insertar el gráfico mpld3 correctamente
        const graphBody = document.getElementById(`graph-body-${index}`);
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = value.graph;
        
        // Mover todos los elementos (incluidos scripts) al contenedor real
        while (tempDiv.firstChild) {
            graphBody.appendChild(tempDiv.firstChild);
        }
        
        // Ejecutar scripts mpld3
        const scripts = graphBody.querySelectorAll('script');
        scripts.forEach(script => {
            const newScript = document.createElement('script');
            newScript.textContent = script.textContent;
            script.parentNode.replaceChild(newScript, script);
        });
        
        index++;
    }
    
    // Re-habilitar controles interactivos después de actualizar gráficos
    setTimeout(() => {
        enableGraphDragging();
    }, 300);
}

function showNotification(message, type) {
    // Crear notificación toast
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

// ================== CONTROLES INTERACTIVOS DE GRÁFICOS ==================

// Almacenar estados originales de los gráficos
const graphStates = {};

function zoomGraph(graphId, direction) {
    const graphBody = document.querySelector(`.graph-body[data-graph-id="${graphId}"]`);
    if (!graphBody) return;
    
    const svg = graphBody.querySelector('svg');
    if (!svg) return;
    
    // Inicializar estado si no existe
    if (!graphStates[graphId]) {
        graphStates[graphId] = {
            scale: 1,
            translateX: 0,
            translateY: 0
        };
    }
    
    const state = graphStates[graphId];
    const zoomFactor = direction === 'in' ? 1.2 : 0.833;
    
    state.scale *= zoomFactor;
    
    // Aplicar transformación
    svg.style.transform = `scale(${state.scale}) translate(${state.translateX}px, ${state.translateY}px)`;
    svg.style.transformOrigin = 'center center';
    svg.style.transition = 'transform 0.3s ease';
}

function resetGraph(graphId) {
    const graphBody = document.querySelector(`.graph-body[data-graph-id="${graphId}"]`);
    if (!graphBody) return;
    
    const svg = graphBody.querySelector('svg');
    if (!svg) return;
    
    // Resetear estado
    graphStates[graphId] = {
        scale: 1,
        translateX: 0,
        translateY: 0
    };
    
    svg.style.transform = 'scale(1) translate(0px, 0px)';
    svg.style.transition = 'transform 0.3s ease';
    
    showNotification('Vista restablecida', 'success');
}

function downloadGraph(graphId) {
    const graphBody = document.querySelector(`.graph-body[data-graph-id="${graphId}"]`);
    if (!graphBody) return;
    
    const svg = graphBody.querySelector('svg');
    if (!svg) {
        showNotification('No se pudo encontrar el gráfico', 'error');
        return;
    }
    
    try {
        // Obtener el título del gráfico
        const titleElement = graphBody.closest('.graph-card').querySelector('.graph-title');
        const filename = titleElement ? 
            titleElement.textContent.trim().replace(/\s+/g, '_') + '.png' : 
            `grafico_${graphId}.png`;
        
        // Clonar SVG y aplicar estilos inline
        const clonedSvg = svg.cloneNode(true);
        const svgData = new XMLSerializer().serializeToString(clonedSvg);
        
        // Crear canvas para convertir SVG a PNG
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const img = new Image();
        
        // Configurar tamaño del canvas
        const bbox = svg.getBBox();
        canvas.width = bbox.width || 800;
        canvas.height = bbox.height || 600;
        
        // Fondo oscuro para el canvas
        ctx.fillStyle = '#020617';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        img.onload = function() {
            ctx.drawImage(img, 0, 0);
            
            // Descargar imagen
            canvas.toBlob(function(blob) {
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
                
                showNotification('Gráfico descargado', 'success');
            });
        };
        
        img.onerror = function() {
            showNotification('Error al generar imagen', 'error');
        };
        
        img.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgData)));
        
    } catch (error) {
        console.error('Error descargando gráfico:', error);
        showNotification('Error al descargar: ' + error.message, 'error');
    }
}

// Habilitar pan/arrastre en gráficos
function enableGraphDragging() {
    document.querySelectorAll('.graph-body').forEach((graphBody, index) => {
        const graphId = index + 1;
        const svg = graphBody.querySelector('svg');
        if (!svg) return;
        
        let isDragging = false;
        let startX, startY;
        
        svg.style.cursor = 'grab';
        
        svg.addEventListener('mousedown', (e) => {
            if (e.button !== 0) return; // Solo botón izquierdo
            isDragging = true;
            startX = e.clientX;
            startY = e.clientY;
            svg.style.cursor = 'grabbing';
        });
        
        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            
            const deltaX = e.clientX - startX;
            const deltaY = e.clientY - startY;
            
            if (!graphStates[graphId]) {
                graphStates[graphId] = { scale: 1, translateX: 0, translateY: 0 };
            }
            
            graphStates[graphId].translateX += deltaX;
            graphStates[graphId].translateY += deltaY;
            
            svg.style.transform = `scale(${graphStates[graphId].scale}) translate(${graphStates[graphId].translateX}px, ${graphStates[graphId].translateY}px)`;
            
            startX = e.clientX;
            startY = e.clientY;
        });
        
        document.addEventListener('mouseup', () => {
            if (isDragging) {
                isDragging = false;
                svg.style.cursor = 'grab';
            }
        });
        
        // Zoom con rueda del ratón
        svg.addEventListener('wheel', (e) => {
            e.preventDefault();
            const direction = e.deltaY < 0 ? 'in' : 'out';
            zoomGraph(graphId, direction);
        });
    });
}

// Inicializar controles cuando se carga la página
window.addEventListener('load', function() {
    setTimeout(() => {
        enableGraphDragging();
    }, 500);
});