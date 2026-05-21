// Aguarda o DOM estar completamente carregado
document.addEventListener('DOMContentLoaded', function() {
    console.log('Iniciando mapa...');
    
    // Inicialização do mapa
    var map = L.map('map', {
    center: [-24.7, -51.9],
    zoom: 7,
    zoomControl: true,
    attributionControl: true
});

// Adiciona o tile layer do OpenStreetMap
// URL correta conforme política oficial: https://operations.osmfoundation.org/policies/tiles/
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 19,
    referrerPolicy: 'no-referrer-when-downgrade'
}).addTo(map);

// Função para atualizar o tamanho do mapa
function updateMapSize() {
    if (map) {
        console.log('Atualizando tamanho do mapa...');
        map.invalidateSize();
    }
}

// Eventos para garantir que o mapa seja renderizado corretamente
window.addEventListener('load', updateMapSize);
window.addEventListener('resize', updateMapSize);

// Carrega o GeoJSON do Paraná
fetch('/static/geojson/PR_Municipios_2023_optimized.geojson')
    .then(response => {
        console.log('Status da resposta GeoJSON:', response.status);
        if (!response.ok) {
            throw new Error('Erro ao carregar GeoJSON: ' + response.status);
        }
        return response.json();
    })
    .then(data => {
        console.log('GeoJSON carregado com sucesso');
        L.geoJSON(data, {
            style: {
                color: '#3388ff',
                weight: 1,
                fillOpacity: 0.1
            },
            onEachFeature: function(feature, layer) {
                layer.bindPopup(feature.properties.NM_MUN);
            }
        }).addTo(map);
    })
    .catch(error => {
        console.error('Erro ao carregar o GeoJSON:', error);
        document.getElementById('map').innerHTML = `
            <div class="alert alert-danger">
                Erro ao carregar o mapa: ${error.message}
            </div>
        `;
    });

    // Log para debug
    console.log('Script do mapa carregado');
});
