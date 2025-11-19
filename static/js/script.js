window.addEventListener('load', function() {
    var loadingScreen = document.getElementById('loading');
    var template = document.getElementById('graficos-container');
    var title = document.getElementById('title');
    //var title = document.getElementById('title');
    loadingScreen.style.opacity = '0';
    // Esperar a que finalice la transición antes de ocultar completamente la pantalla de carga
    setTimeout(function() {
        loadingScreen.style.display = 'none';
    }, 30); // Duración de la transición (ajusta según sea necesario)

    // Mostrar los gráficos una vez que la pantalla de carga esté completamente oculta
    setTimeout(function() {
        template.style.display = 'block';
        title.style.display = 'block';
    }, 50); // Duración de la transición (ajusta según sea necesario)
});