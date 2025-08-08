// mapa.js
// JS do mapa Leaflet e integração com GeoJSON

document.addEventListener('DOMContentLoaded', function() {
    // Inicializa o mapa com centro e zoom padrão
    window.map = L.map('map', {
        center: [-24.7, -51.9],
        zoom: 7,
        zoomControl: true,
        attributionControl: true,
    });
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: 'Map data © <a href="https://openstreetmap.org">OpenStreetMap</a> contributors'
    }).addTo(window.map);
    // Ajusta tamanho do mapa ao redimensionar janela
    window.addEventListener('resize', function() {
        window.map.invalidateSize();
    });
    
    // Adiciona evento para redimensionar o mapa quando a aba é restaurada
    document.addEventListener('visibilitychange', function() {
        if (!document.hidden) {
            setTimeout(function() {
                window.map.invalidateSize();
            }, 200);
        }
    });

    function mostrarErroNoMapa(mensagem) {
        const mapElement = document.getElementById('map');
        if (mapElement) {
            mapElement.innerHTML = `
                <div class="d-flex align-items-center justify-content-center h-100">
                    <div class="text-center">
                        <i class="fas fa-exclamation-triangle fa-3x text-warning mb-3"></i>
                        <h5>Erro ao carregar o mapa</h5>
                        <p class="text-muted">${mensagem}</p>
                        <button class="btn btn-primary" onclick="location.reload()">
                            <i class="fas fa-redo me-2"></i>Tentar novamente
                        </button>
                    </div>
                </div>
            `;
        }
    }

    fetch('/static/geojson/PR_Municipios_2023_optimized.geojson')
        .then(response => {
            if (!response.ok) throw new Error('Erro ao carregar GeoJSON: ' + response.status);
            return response.json();
        })
        .then(geojsonData => {
            var municipioLayer = L.geoJSON(geojsonData, {
                style: function(feature) {
                    return {
                        color: '#3388ff',
                        weight: 1,
                        fillOpacity: 0.1
                    };
                },
                onEachFeature: function (feature, layer) {
                    layer.bindPopup('<strong>' + feature.properties.NM_MUN + '</strong>');
                    layer.on({
                        mouseover: function(e) {
                            const l = e.target;
                            l.setStyle({
                                weight: 3,
                                color: '#666',
                                fillOpacity: 0.5
                            });
                            l.bringToFront();
                        },
                        mouseout: function(e) {
                            const l = e.target;
                            l.setStyle({
                                color: '#3388ff',
                                weight: 1,
                                fillOpacity: 0.1
                            });
                        },
                        click: function(e) {
                            const l = e.target;
                            window.map.fitBounds(l.getBounds(), {padding: [20, 20]});
                            l.openPopup();
                        }
                    });
                }
            }).addTo(window.map);

            // Enquadrar todo o Paraná ao carregar, após o layer estar pronto
            municipioLayer.once('layeradd', function() {
                try {
                    var bounds = municipioLayer.getBounds();
                    window.map.fitBounds(bounds, {padding: [20, 20]});
                    window.map.invalidateSize();
                } catch (e) {
                    window.map.setView([-24.7, -51.9], 7);
                }
            });

            var municipioSelect = document.getElementById('municipio');
            if (municipioSelect) {
                municipioSelect.addEventListener('change', function() {
                    var municipioSelecionado = this.value;
                    municipioLayer.eachLayer(function(layer) {
                        if (layer.feature.properties.NM_MUN === municipioSelecionado) {
                            layer.setStyle({ color: 'red', weight: 3, fillOpacity: 0.3 });
                            window.map.fitBounds(layer.getBounds(), {padding: [20, 20]});
                            layer.openPopup();
                        } else {
                            layer.setStyle({ color: '#3388ff', weight: 1, fillOpacity: 0.1 });
                            layer.closePopup();
                        }
                    });
                });
            }
        })
        .catch(error => {
            console.error(error);
            mostrarErroNoMapa(error.message);
            window.map.setView([-24.7, -51.9], 7);
        });
});
