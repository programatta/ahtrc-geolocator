(function() {
    let timeoutId = null;

    function initGeocoder(map, fieldId) {
        if (typeof L.Control.Geocoder !== 'undefined' && typeof L.Control.Geocoder.nominatim === 'function') {
            window.clearTimeout(timeoutId);

            var geocoder = L.Control.Geocoder.nominatim();
            // Nominatim no soporta autocompletar ("suggest" siempre lanza
            // SuggestUnsupportedError). Si se deja activo, el control se queda
            // enganchado al evento "input" y, al fallar esa petición, nunca
            // dispara "finishsuggest" -> el spinner de búsqueda se queda encendido
            // para siempre. Lo desactivamos para que solo existan peticiones de
            // geocode "normales", que sí completan correctamente.
            geocoder.suggest = undefined;

            L.Control.geocoder({
                geocoder: geocoder,
                defaultMarkGeocode: false,
                placeholder: "Buscar ciudad...",
                errorMessage: "No se encontró."
            })
            .on('markgeocode', function(e) {
                var latlng = e.geocode.center;

                // 1. Centrar el mapa
                map.setView(latlng, 14);

                // 2. Colocar el marcador dentro de la capa de dibujo de django-leaflet
                //    (drawnItems) en vez de uno suelto, para que quede sincronizado
                //    con las herramientas de edición del mapa (arrastrar, borrar...).
                var drawControl = map['drawControl' + fieldId];
                var drawnItems = drawControl && drawControl.options.edit.featureGroup;
                var marker = L.marker(latlng);

                if (drawnItems) {
                    drawnItems.clearLayers();
                    drawnItems.addLayer(marker);
                } else {
                    marker.addTo(map);
                }

                // 3. Guardar el punto en el textarea del formulario, en formato
                //    GeoJSON (el mismo que usa L.FieldStore, ver leaflet.forms.js;
                //    un WKT rompería la deserialización al reabrir el formulario).
                if (fieldId) {
                    var targetTextarea = document.getElementById(fieldId);
                    if (targetTextarea) {
                        targetTextarea.value = JSON.stringify(marker.toGeoJSON().geometry);
                        // Disparamos un evento de cambio por si Django tiene algún listener activo
                        targetTextarea.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                }
            })
            .addTo(map);
        } else {
            timeoutId = setTimeout(function() {
                initGeocoder(map, fieldId);
            }, 200);
        }
    }

    // Escuchamos el evento nativo de django-leaflet
    window.addEventListener("map:init", function (event) {
        var map = event.detail.map;

        map.on('map:loadfield', function (e) {
            // e.fieldid nos da siempre el ID exacto del elemento HTML en el DOM (Ej: "id_geom")
            var fieldId = e.fieldid;

            if (fieldId) {
                initGeocoder(map, fieldId);
            }
        });
    });
})();
