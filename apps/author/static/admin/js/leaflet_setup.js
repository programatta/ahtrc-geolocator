(function() {
    let timeoutId = null;
    function initGeocoder(map) {
        // Comprobamos si la librería del Geocoder ya está disponible en el objeto L
        if (typeof L.Control.Geocoder !== 'undefined' && typeof L.Control.Geocoder.nominatim === 'function') {
            window.clearTimeout(timeoutId);
            L.Control.geocoder({
                defaultMarkGeocode: false,
                placeholder: "Buscar ciudad...",
                errorMessage: "No se encontró."
            })
            .on('markgeocode', function(e) {
                var latlng = e.geocode.center;
                map.setView(latlng, 14);
                
                // Intentamos mover el marcador del administrador de Django
                if (window.leaflet_admin_map_layer) {
                    window.leaflet_admin_map_layer.setLatLng(latlng);
                }
            })
            .addTo(map);
        } else {
            // Si aún no está cargado, esperamos un poquito y reintentamos
            timeoutId = setTimeout(function() {
                initGeocoder(map);
            }, 200);
        }
    }

    window.addEventListener("map:init", function (event) {
        var map = event.detail.map;
        initGeocoder(map);
    });
})();
