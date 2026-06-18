document.addEventListener('DOMContentLoaded', function () {
    const mapElement = document.getElementById('outorgas-map');
    const fieldSelect = document.getElementById('classification-field');
    const summaryTableBody = document.getElementById('map-summary-table-body');
    const summaryColumnLabel = document.getElementById('map-summary-column-label');
    const detailTableBody = document.getElementById('map-detail-table-body');

    if (!mapElement || !fieldSelect) {
        return;
    }

    const fieldLabels = {
        outorgas_IAT_agrupado_CBH_COMITE: 'Comitê de bacia',
        outorgas_IAT_agrupado_ATV_MACRO: 'Atividade macro',
        bac_nome: 'Bacia hidrográfica',
    };

    const palette = [
        '#2563eb', '#f97316', '#16a34a', '#7c3aed', '#dc2626', '#0891b2',
        '#ca8a04', '#db2777', '#4f46e5', '#059669', '#9333ea', '#ea580c',
        '#0284c7', '#65a30d', '#be123c', '#0f766e',
    ];

    const map = L.map('outorgas-map', {
        center: [-24.7, -51.9],
        zoom: 7,
        zoomControl: true,
        attributionControl: true,
        preferCanvas: true,
    });
    const canvasRenderer = L.canvas();

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19,
        referrerPolicy: 'no-referrer-when-downgrade',
    }).addTo(map);

    window.addEventListener('resize', function () {
        map.invalidateSize();
    });

    document.addEventListener('visibilitychange', function () {
        if (!document.hidden) {
            setTimeout(function () {
                map.invalidateSize();
            }, 200);
        }
    });

    function formatValue(value) {
        if (value === null || value === undefined) {
            return 'Não informado';
        }

        const normalized = String(value).trim();
        return normalized ? normalized : 'Não informado';
    }

    function escapeHtml(value) {
        return String(value)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function makeColorScale(values) {
        const colors = {};
        values.forEach(function (value, index) {
            if (index < palette.length) {
                colors[value] = palette[index];
                return;
            }

            const hue = Math.round((index * 137.508) % 360);
            colors[value] = 'hsl(' + hue + ', 68%, 48%)';
        });
        return colors;
    }

    function buildPopup(properties, activeField, activeValue) {
        const items = [
            ['Município', formatValue(properties.municipio)],
            ['Comitê de bacia', formatValue(properties.outorgas_IAT_agrupado_CBH_COMITE)],
            ['Atividade macro', formatValue(properties.outorgas_IAT_agrupado_ATV_MACRO)],
            ['Bacia hidrográfica', formatValue(properties.bac_nome)],
            ['Atividade', formatValue(properties.atv_nome)],
            ['Finalidade', formatValue(properties.finalida_1)],
            ['Condição', formatValue(properties.condicao)],
            ['Portaria', formatValue(properties.portaria)],
            ['Código do ponto', formatValue(properties.codigo_pon)],
        ];

        const detailsHtml = items.map(function (item) {
            return '<p><strong>' + escapeHtml(item[0]) + ':</strong> ' + escapeHtml(item[1]) + '</p>';
        }).join('');

        return [
            '<div class="popup-content">',
            '<h5>' + escapeHtml(formatValue(properties.municipio)) + '</h5>',
            '<p><span class="badge text-bg-primary">' + escapeHtml(fieldLabels[activeField]) + ': ' + escapeHtml(activeValue) + '</span></p>',
            detailsHtml,
            '</div>',
        ].join('');
    }

    function showError(message) {
        mapElement.innerHTML = [
            '<div class="d-flex align-items-center justify-content-center h-100">',
            '<div class="text-center">',
            '<i class="fas fa-exclamation-triangle fa-3x text-warning mb-3"></i>',
            '<h5>Erro ao carregar o mapa</h5>',
            '<p class="text-muted">' + escapeHtml(message) + '</p>',
            '<button class="btn btn-primary" onclick="location.reload()">',
            '<i class="fas fa-redo me-2"></i>Tentar novamente',
            '</button>',
            '</div>',
            '</div>',
        ].join('');
    }

    function renderMessageRow(element, colspan, message) {
        element.innerHTML = '<tr><td colspan="' + colspan + '" class="text-center text-muted py-4">' + escapeHtml(message) + '</td></tr>';
    }

    const legend = L.control({ position: 'bottomright' });
    legend.onAdd = function () {
        const div = L.DomUtil.create('div', 'legend');
        div.innerHTML = '<h4>Legenda</h4><div class="text-muted small">Carregando...</div>';
        return div;
    };
    legend.addTo(map);

    let outorgasLayer = null;
    let geojsonData = null;
    let hasFittedBounds = false;
    let currentField = fieldSelect.value;
    let currentUpdateRun = 0;
    const fieldStatsCache = {};
    let detailRows = [];

    function getFieldStats(fieldName) {
        if (fieldStatsCache[fieldName]) {
            return fieldStatsCache[fieldName];
        }

        const counts = {};
        geojsonData.features.forEach(function (feature) {
            const category = formatValue(feature.properties[fieldName]);
            counts[category] = (counts[category] || 0) + 1;
        });

        const entries = Object.entries(counts).sort(function (a, b) {
            if (b[1] !== a[1]) {
                return b[1] - a[1];
            }
            return a[0].localeCompare(b[0], 'pt-BR');
        });

        const colors = makeColorScale(entries.map(function (entry) {
            return entry[0];
        }));

        fieldStatsCache[fieldName] = {
            counts: counts,
            entries: entries,
            colors: colors,
        };
        return fieldStatsCache[fieldName];
    }

    function buildDetailRows() {
        const combinedCounts = new Map();

        geojsonData.features.forEach(function (feature) {
            const cbh = formatValue(feature.properties.outorgas_IAT_agrupado_CBH_COMITE);
            const activity = formatValue(feature.properties.outorgas_IAT_agrupado_ATV_MACRO);
            const key = cbh + '||' + activity;

            if (!combinedCounts.has(key)) {
                combinedCounts.set(key, {
                    cbh: cbh,
                    activity: activity,
                    total: 0,
                });
            }

            combinedCounts.get(key).total += 1;
        });

        detailRows = Array.from(combinedCounts.values()).sort(function (a, b) {
            if (b.total !== a.total) {
                return b.total - a.total;
            }
            if (a.cbh !== b.cbh) {
                return a.cbh.localeCompare(b.cbh, 'pt-BR');
            }
            return a.activity.localeCompare(b.activity, 'pt-BR');
        });
    }

    function updateLegend(activeField, stats) {
        const legendContainer = legend.getContainer();
        if (!legendContainer) {
            return;
        }

        const entries = stats.entries.map(function (entry) {
            const label = entry[0];
            const count = entry[1];
            const color = stats.colors[label];
            return [
                '<div class="legend-item">',
                '<span style="background:' + color + '"></span>',
                '<strong>' + escapeHtml(label) + '</strong>',
                '<small class="text-muted ms-2">(' + count.toLocaleString('pt-BR') + ')</small>',
                '</div>',
            ].join('');
        }).join('');

        legendContainer.innerHTML = [
            '<h4>' + escapeHtml(fieldLabels[activeField]) + '</h4>',
            entries,
        ].join('');
    }

    function renderSummaryTable(activeField, stats) {
        summaryColumnLabel.textContent = fieldLabels[activeField];

        if (!stats.entries.length) {
            renderMessageRow(summaryTableBody, 4, 'Nenhum dado disponível.');
            return;
        }

        const total = geojsonData.features.length;
        const rows = stats.entries.map(function (entry, index) {
            const label = entry[0];
            const count = entry[1];
            const percentage = total ? ((count / total) * 100) : 0;

            return [
                '<tr>',
                '<td class="map-table-rank">', index + 1, '</td>',
                '<td><span class="map-category-badge">', escapeHtml(label), '</span></td>',
                '<td class="text-end fw-semibold">', count.toLocaleString('pt-BR'), '</td>',
                '<td class="text-end text-muted">', percentage.toFixed(1).replace('.', ','), '%</td>',
                '</tr>',
            ].join('');
        }).join('');

        summaryTableBody.innerHTML = rows;
    }

    function renderDetailTable() {
        if (!detailRows.length) {
            renderMessageRow(detailTableBody, 5, 'Nenhum dado disponível.');
            return;
        }

        const total = geojsonData.features.length;
        const rows = detailRows.map(function (entry, index) {
            const percentage = total ? ((entry.total / total) * 100) : 0;

            return [
                '<tr>',
                '<td class="map-table-rank">', index + 1, '</td>',
                '<td>', escapeHtml(entry.cbh), '</td>',
                '<td>', escapeHtml(entry.activity), '</td>',
                '<td class="text-end fw-semibold">', entry.total.toLocaleString('pt-BR'), '</td>',
                '<td class="text-end text-muted">', percentage.toFixed(1).replace('.', ','), '%</td>',
                '</tr>',
            ].join('');
        }).join('');

        detailTableBody.innerHTML = rows;
    }

    function createLayer() {
        const initialStats = getFieldStats(currentField);

        outorgasLayer = L.geoJSON(geojsonData, {
            pointToLayer: function (feature, latlng) {
                const category = formatValue(feature.properties[currentField]);
                return L.circleMarker(latlng, {
                    radius: 5,
                    fillColor: initialStats.colors[category],
                    color: '#ffffff',
                    weight: 1,
                    opacity: 1,
                    fillOpacity: 0.78,
                    renderer: canvasRenderer,
                });
            },
            onEachFeature: function (feature, layer) {
                const category = formatValue(feature.properties[currentField]);
                layer.bindPopup(buildPopup(feature.properties, currentField, category), {
                    maxWidth: 340,
                });
                layer.on({
                    mouseover: function () {
                        layer.setStyle({
                            radius: 7,
                            weight: 2,
                            fillOpacity: 0.95,
                        });
                        if (layer.bringToFront) {
                            layer.bringToFront();
                        }
                    },
                    mouseout: function () {
                        layer.setStyle({
                            radius: 5,
                            weight: 1,
                            fillOpacity: 0.78,
                        });
                    },
                });
            },
        }).addTo(map);

        if (!hasFittedBounds) {
            const bounds = outorgasLayer.getBounds();
            if (bounds.isValid()) {
                map.fitBounds(bounds, { padding: [24, 24] });
            }
            hasFittedBounds = true;
        }
    }

    function applyClassification(activeField) {
        currentField = activeField;
        const stats = getFieldStats(activeField);

        updateLegend(activeField, stats);
        renderSummaryTable(activeField, stats);

        if (!outorgasLayer) {
            return;
        }

        const updateRun = ++currentUpdateRun;
        const layers = outorgasLayer.getLayers();
        let index = 0;

        fieldSelect.disabled = true;

        function processChunk() {
            if (updateRun !== currentUpdateRun) {
                return;
            }

            const end = Math.min(index + 800, layers.length);
            for (; index < end; index += 1) {
                const layer = layers[index];
                const category = formatValue(layer.feature.properties[activeField]);

                layer.setStyle({
                    radius: 5,
                    fillColor: stats.colors[category],
                    color: '#ffffff',
                    weight: 1,
                    opacity: 1,
                    fillOpacity: 0.78,
                });
                layer.setPopupContent(buildPopup(layer.feature.properties, activeField, category));
            }

            if (index < layers.length) {
                window.requestAnimationFrame(processChunk);
                return;
            }

            fieldSelect.disabled = false;
        }

        window.requestAnimationFrame(processChunk);
    }

    renderMessageRow(summaryTableBody, 4, 'Carregando dados...');
    renderMessageRow(detailTableBody, 5, 'Carregando dados...');

    fetch(mapElement.dataset.geojsonUrl)
        .then(function (response) {
            if (!response.ok) {
                throw new Error('Erro ao carregar GeoJSON: ' + response.status);
            }
            return response.json();
        })
        .then(function (data) {
            geojsonData = data;
            buildDetailRows();
            renderDetailTable();
            createLayer();
            applyClassification(fieldSelect.value);
            map.invalidateSize();
        })
        .catch(function (error) {
            console.error(error);
            renderMessageRow(summaryTableBody, 4, error.message);
            renderMessageRow(detailTableBody, 5, error.message);
            showError(error.message);
            map.setView([-24.7, -51.9], 7);
        });

    fieldSelect.addEventListener('change', function () {
        applyClassification(this.value);
    });
});
