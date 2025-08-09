// mapa_temp.js
// JS do mapa Leaflet melhorado com integração ao dashboard

console.log('mapa_temp.js carregado');
console.log('Leaflet disponível:', typeof L !== 'undefined');

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOMContentLoaded - mapa_temp.js');
    // Só inicializa o mapa se o elemento existir
    const mapElement = document.getElementById('map');
    if (!mapElement) return;

    // Inicializa o mapa com centro no Paraná
    window.map = L.map('map', {
        center: [-24.7, -51.9],
        zoom: 7,
        zoomControl: true,
        attributionControl: true,
        preferCanvas: true // Melhor performance
    });

    // Adiciona tile layer com melhor qualidade
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© <a href="https://openstreetmap.org">OpenStreetMap</a> contributors',
        maxZoom: 18,
        tileSize: 256,
        zoomOffset: 0
    }).addTo(window.map);

    // Adiciona legenda ao mapa
    const legend = L.control({position: 'bottomright'});
    legend.onAdd = function (map) {
        const div = L.DomUtil.create('div', 'legend');
        div.innerHTML = `
            <h6><i class="fas fa-palette me-2"></i>OSCs por Município</h6>
            <div class="legend-item"><span style="background: #D3D3D3"></span> 0 OSCs</div>
            <div class="legend-item"><span style="background: #FFEDA0"></span> 1-10</div>
            <div class="legend-item"><span style="background: #FED976"></span> 11-20</div>
            <div class="legend-item"><span style="background: #FEB24C"></span> 21-50</div>
            <div class="legend-item"><span style="background: #FD8D3C"></span> 51-100</div>
            <div class="legend-item"><span style="background: #FC4E2A"></span> 101-200</div>
            <div class="legend-item"><span style="background: #E31A1C"></span> 201-500</div>
            <div class="legend-item"><span style="background: #BD0026"></span> 501-1000</div>
            <div class="legend-item"><span style="background: #800026"></span> 1000+</div>
        `;
        return div;
    };
    legend.addTo(window.map);

    // Variáveis globais para controle
    let municipioLayer = null;
    let oscsData = {};
    let municipiosList = []; // Lista de todos os municípios para busca

    // Função para mostrar erro no mapa
    function mostrarErroNoMapa(mensagem) {
        mapElement.innerHTML = `
            <div class="d-flex align-items-center justify-content-center h-100 bg-light rounded">
                <div class="text-center p-4">
                    <i class="fas fa-exclamation-triangle fa-3x text-warning mb-3"></i>
                    <h5 class="text-dark">Erro ao carregar o mapa</h5>
                    <p class="text-muted">${mensagem}</p>
                    <button class="btn btn-primary btn-sm" onclick="location.reload()">
                        <i class="fas fa-redo me-2"></i>Tentar novamente
                    </button>
                </div>
            </div>
        `;
    }

    // Função para obter cor baseada na quantidade de OSCs
    function getColor(count) {
        return count === 0   ? '#D3D3D3' :  // Cinza claro para zero OSCs
               count > 1000 ? '#800026' :
               count > 500  ? '#BD0026' :
               count > 200  ? '#E31A1C' :
               count > 100  ? '#FC4E2A' :
               count > 50   ? '#FD8D3C' :
               count > 20   ? '#FEB24C' :
               count > 10   ? '#FED976' :
                              '#FFEDA0';
    }

    // Função para estilizar municípios
    function style(feature) {
        const municipio = feature.properties.NM_MUN;
        const count = buscarOSCsPorMunicipio(municipio);

        // Log para debug específico para alguns municípios importantes
        if (municipio === 'Curitiba' || municipio === 'Londrina' || municipio === 'Maringá' ||
            municipio === 'CORONEL DOMINGO SOARES' || municipio === 'DIAMANTE DO OESTE') {
            console.log(`🔍 Município importante: "${municipio}", OSCs: ${count}`);
            console.log('   Dados disponíveis para este município:', oscsData[municipio]);

            // Debug específico para Coronel Domingo Soares
            if (municipio === 'CORONEL DOMINGO SOARES') {
                console.log('🎯 DEBUG CORONEL DOMINGO SOARES:');
                console.log('   Variações disponíveis:');
                Object.keys(oscsData).forEach(key => {
                    if (key.toLowerCase().includes('coronel') && key.toLowerCase().includes('domingo')) {
                        console.log(`      "${key}": ${oscsData[key]} OSCs`);
                    }
                });
            }
        }

        return {
            fillColor: getColor(count),
            weight: 2,
            opacity: 1,
            color: 'white',
            dashArray: '3',
            fillOpacity: 0.7
        };
    }

    // Função para destacar município
    function highlightFeature(e) {
        const layer = e.target;
        layer.setStyle({
            weight: 5,
            color: '#666',
            dashArray: '',
            fillOpacity: 0.9
        });
        layer.bringToFront();
    }

    // Função para resetar destaque
    function resetHighlight(e) {
        if (municipioLayer) {
            municipioLayer.resetStyle(e.target);
        }
    }

    // Função para zoom no município
    function zoomToFeature(e) {
        const layer = e.target;
        window.map.fitBounds(layer.getBounds(), {padding: [20, 20]});

        // Atualiza o select do município
        const municipioSelect = document.getElementById('municipio');
        if (municipioSelect) {
            municipioSelect.value = layer.feature.properties.NM_MUN;
        }
    }

    // Função para adicionar eventos a cada feature
    function onEachFeature(feature, layer) {
        const municipio = feature.properties.NM_MUN;
        const count = buscarOSCsPorMunicipio(municipio);

        layer.bindPopup(`
            <div class="popup-content">
                <h5><i class="fas fa-map-marker-alt me-2"></i>${municipio}</h5>
                <p><strong>OSCs cadastradas:</strong> <span class="badge bg-primary">${count}</span></p>
                <small class="text-muted">Clique para filtrar por este município</small>
            </div>
        `);

        layer.on({
            mouseover: highlightFeature,
            mouseout: resetHighlight,
            click: zoomToFeature
        });
    }

    // Função para normalizar texto removendo acentos e padronizando
    function normalizarTexto(texto) {
        if (!texto) return '';

        return texto
            .toLowerCase()
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '') // Remove acentos
            .replace(/[^a-z0-9\s]/g, '') // Remove caracteres especiais
            .replace(/\s+/g, ' ') // Normaliza espaços
            .trim();
    }

    // Função para calcular similaridade entre dois textos
    function calcularSimilaridade(texto1, texto2) {
        const norm1 = normalizarTexto(texto1);
        const norm2 = normalizarTexto(texto2);

        // Igualdade exata após normalização
        if (norm1 === norm2) return 1.0;

        // Verificar se um contém o outro
        if (norm1.includes(norm2) || norm2.includes(norm1)) return 0.8;

        // Verificar palavras em comum
        const palavras1 = norm1.split(' ').filter(p => p.length > 2);
        const palavras2 = norm2.split(' ').filter(p => p.length > 2);

        if (palavras1.length === 0 || palavras2.length === 0) return 0;

        const palavrasComuns = palavras1.filter(p => palavras2.includes(p));
        const similaridade = palavrasComuns.length / Math.max(palavras1.length, palavras2.length);

        return similaridade;
    }

    // Função para encontrar melhor correspondência de município
    function encontrarMelhorCorrespondencia(nomeBusca, listaDisponivel) {
        let melhorMatch = null;
        let melhorScore = 0;

        for (const nomeDisponivel of listaDisponivel) {
            const score = calcularSimilaridade(nomeBusca, nomeDisponivel);

            if (score > melhorScore && score >= 0.6) { // Threshold mínimo de 60%
                melhorScore = score;
                melhorMatch = nomeDisponivel;
            }
        }

        return melhorMatch;
    }

    // Função para normalizar nomes de municípios (versão melhorada)
    function normalizarNomeMunicipio(nome) {
        if (!nome) return '';

        // Mapeamento específico de nomes conhecidos (corrigindo erros do IPEA)
        const mapeamentoEspecifico = {
            'CURITIBA': 'Curitiba',
            'LONDRINA': 'Londrina',
            'MARINGA': 'Maringá',
            'MARINGÁ': 'Maringá',
            'FOZ DO IGUACU': 'Foz do Iguaçu',
            'FOZ DO IGUAÇU': 'Foz do Iguaçu',
            'SAO JOSE DOS PINHAIS': 'São José dos Pinhais',
            'SÃO JOSÉ DOS PINHAIS': 'São José dos Pinhais',
            // Correções específicas para nomes incorretos do IPEA:
            'CORONEL DOMINGOS SOARES': 'CORONEL DOMINGO SOARES', // IPEA -> GeoJSON correto
            'Coronel Domingos Soares': 'Coronel Domingo Soares',
            'coronel domingos soares': 'coronel domingo soares',
            'DIAMANTE D\'OESTE': 'DIAMANTE DO OESTE', // IPEA -> GeoJSON correto
            "Diamante D'Oeste": 'Diamante do Oeste',
            'diamante d\'oeste': 'diamante do oeste'
        };

        const nomeUpper = nome.toUpperCase();
        if (mapeamentoEspecifico[nomeUpper]) {
            return mapeamentoEspecifico[nomeUpper];
        }

        // Se não encontrou mapeamento específico, usar busca por similaridade
        const municipiosDisponiveis = Object.keys(oscsData);
        const melhorMatch = encontrarMelhorCorrespondencia(nome, municipiosDisponiveis);

        return melhorMatch || nome;
    }

    // Carrega dados de OSCs por município
    function carregarDadosOSCs() {
        console.log('Carregando dados de OSCs...');
        return fetch('/municipios-data/')
            .then(response => response.json())
            .then(data => {
                console.log('Dados de OSCs recebidos:', data);

                // Converte array para objeto para busca rápida
                // Cria múltiplas entradas para facilitar a busca com estratégia de aproximação
                data.data.forEach(item => {
                    const municipio = item.municipio;
                    const count = item.total_oscs;

                    // Função para armazenar variação se não existir
                    function armazenarVariacao(variacao) {
                        if (variacao && !oscsData[variacao]) {
                            oscsData[variacao] = count;
                        }
                    }

                    // 1. Nome original
                    armazenarVariacao(municipio);

                    // 2. Variações de capitalização
                    armazenarVariacao(municipio.toUpperCase());
                    armazenarVariacao(municipio.toLowerCase());
                    armazenarVariacao(municipio.charAt(0).toUpperCase() + municipio.slice(1).toLowerCase());

                    // 3. Variações sem acentos
                    const semAcentos = municipio.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
                    armazenarVariacao(semAcentos);
                    armazenarVariacao(semAcentos.toUpperCase());
                    armazenarVariacao(semAcentos.toLowerCase());

                    // 4. Variações com normalização completa
                    const normalizado = normalizarTexto(municipio);
                    armazenarVariacao(normalizado);

                    // 5. Mapeamentos específicos para corrigir nomes incorretos do IPEA
                    const mapeamentosEspecificos = {
                        // Coronel Domingos Soares (IPEA) -> Coronel Domingo Soares (GeoJSON correto)
                        'Coronel Domingos Soares': [
                            'CORONEL DOMINGO SOARES',
                            'Coronel Domingo Soares',
                            'coronel domingo soares'
                        ],
                        // Diamante D'Oeste (IPEA) -> Diamante do Oeste (GeoJSON correto)
                        "Diamante D'Oeste": [
                            'DIAMANTE DO OESTE',
                            'Diamante do Oeste',
                            'diamante do oeste'
                        ],
                        'Foz do Iguaçu': [
                            'FOZ DO IGUACU',
                            'Foz do Iguacu',
                            'FOZ DO IGUAÇU'
                        ],
                        'São José dos Pinhais': [
                            'SAO JOSE DOS PINHAIS',
                            'Sao Jose dos Pinhais',
                            'SÃO JOSÉ DOS PINHAIS'
                        ]
                    };

                    // Aplicar mapeamentos específicos
                    if (mapeamentosEspecificos[municipio]) {
                        mapeamentosEspecificos[municipio].forEach(armazenarVariacao);
                    }

                    // 6. Variações invertidas (buscar se este município é variação de outro)
                    Object.keys(mapeamentosEspecificos).forEach(chave => {
                        if (mapeamentosEspecificos[chave].includes(municipio)) {
                            armazenarVariacao(chave);
                        }
                    });
                });

                console.log('OSCs Data processado:', oscsData);
                console.log('Total de entradas criadas:', Object.keys(oscsData).length);

                // Log específico para municípios importantes
                console.log('Curitiba:', oscsData['Curitiba']);
                console.log('Londrina:', oscsData['Londrina']);
                console.log('Maringá:', oscsData['Maringá']);
                console.log('CURITIBA:', oscsData['CURITIBA']);
                console.log('LONDRINA:', oscsData['LONDRINA']);
                console.log('MARINGÁ:', oscsData['MARINGÁ']);

                // Recarrega o layer se já existir
                if (municipioLayer) {
                    console.log('Atualizando estilo do layer...');
                    municipioLayer.setStyle(style);

                    // Atualiza popups existentes
                    municipioLayer.eachLayer(function(layer) {
                        const municipio = layer.feature.properties.NM_MUN;
                        const count = buscarOSCsPorMunicipio(municipio);

                        layer.setPopupContent(`
                            <div class="popup-content">
                                <h5><i class="fas fa-map-marker-alt me-2"></i>${municipio}</h5>
                                <p><strong>OSCs cadastradas:</strong> <span class="badge bg-primary">${count}</span></p>
                                <small class="text-muted">Clique para filtrar por este município</small>
                            </div>
                        `);
                    });
                }

                return oscsData;
            })
            .catch(error => {
                console.error('Erro ao carregar dados de OSCs:', error);
                throw error;
            });
    }

    // Função para buscar OSCs por município com estratégia de aproximação
    function buscarOSCsPorMunicipio(municipio) {
        if (!municipio) return 0;

        // Debug específico para Coronel Domingo Soares
        const isCoronelDomingo = municipio === 'CORONEL DOMINGO SOARES' ||
                                municipio.toLowerCase().includes('coronel') && municipio.toLowerCase().includes('domingo');

        if (isCoronelDomingo) {
            console.log(`🔍 Buscando OSCs para: "${municipio}"`);
        }

        // 1. Busca exata
        if (oscsData[municipio] !== undefined) {
            if (isCoronelDomingo) {
                console.log(`   ✅ Busca exata encontrou: ${oscsData[municipio]} OSCs`);
            }
            return oscsData[municipio];
        }

        if (isCoronelDomingo) {
            console.log(`   ❌ Busca exata falhou para: "${municipio}"`);
        }

        // 2. Busca com normalização básica (maiúscula/minúscula)
        const municipiosDisponiveis = Object.keys(oscsData);

        for (const municipioDisponivel of municipiosDisponiveis) {
            if (municipio.toLowerCase() === municipioDisponivel.toLowerCase()) {
                return oscsData[municipioDisponivel];
            }
        }

        // 3. Busca com normalização de acentos e caracteres especiais
        const municipioNormalizado = normalizarTexto(municipio);

        for (const municipioDisponivel of municipiosDisponiveis) {
            if (municipioNormalizado === normalizarTexto(municipioDisponivel)) {
                return oscsData[municipioDisponivel];
            }
        }

        // 4. Busca por similaridade (palavras em comum)
        let melhorMatch = null;
        let melhorScore = 0;

        for (const municipioDisponivel of municipiosDisponiveis) {
            const score = calcularSimilaridade(municipio, municipioDisponivel);

            if (score > melhorScore && score >= 0.6) { // Threshold de 60% para correspondência (mais tolerante)
                melhorScore = score;
                melhorMatch = municipioDisponivel;
            }
        }

        if (melhorMatch) {
            console.log(`✅ Correspondência encontrada: "${municipio}" -> "${melhorMatch}" (score: ${melhorScore.toFixed(2)})`);
            if (isCoronelDomingo) {
                console.log(`   🎯 CORONEL DOMINGO: Retornando ${oscsData[melhorMatch]} OSCs`);
            }
            return oscsData[melhorMatch];
        }

        if (isCoronelDomingo) {
            console.log(`   ❌ Nenhuma correspondência por similaridade encontrada`);
        }

        // 5. Busca por contenção (uma string contém a outra)
        for (const municipioDisponivel of municipiosDisponiveis) {
            const norm1 = normalizarTexto(municipio);
            const norm2 = normalizarTexto(municipioDisponivel);

            if ((norm1.length > 5 && norm2.includes(norm1)) ||
                (norm2.length > 5 && norm1.includes(norm2))) {
                console.log(`✅ Correspondência por contenção: "${municipio}" -> "${municipioDisponivel}"`);
                return oscsData[municipioDisponivel];
            }
        }

        // Log para debug de municípios não encontrados
        console.warn(`❌ Município não encontrado: "${municipio}"`);

        if (isCoronelDomingo) {
            console.warn(`🔍 DEBUG CORONEL DOMINGO - Chaves disponíveis com 'coronel':`);
            Object.keys(oscsData).forEach(key => {
                if (key.toLowerCase().includes('coronel')) {
                    console.warn(`   "${key}": ${oscsData[key]} OSCs`);
                }
            });
        }

        console.warn(`   Municípios disponíveis similares:`,
            municipiosDisponiveis
                .map(m => ({ nome: m, score: calcularSimilaridade(municipio, m) }))
                .filter(m => m.score > 0.3)
                .sort((a, b) => b.score - a.score)
                .slice(0, 5)
                .map(m => `${m.nome} (${m.score.toFixed(2)})`)
        );

        return 0;
    }

    // Funções de busca de municípios
    function initializeMapSearch() {
        const searchInput = document.getElementById('map-search');
        const searchResults = document.getElementById('map-search-results');

        if (!searchInput || !searchResults) {
            console.log('Elementos de busca não encontrados');
            return;
        }

        // Event listener para input de busca
        searchInput.addEventListener('input', function(e) {
            const query = e.target.value.trim().toLowerCase();

            if (query.length === 0) {
                hideSearchResults();
                return;
            }

            if (query.length < 2) {
                return; // Só busca com 2+ caracteres
            }

            const filteredMunicipios = filterMunicipios(query);
            showSearchResults(filteredMunicipios);
        });

        // Esconder resultados quando clicar fora
        document.addEventListener('click', function(e) {
            if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
                hideSearchResults();
            }
        });

        // Limpar busca com ESC
        searchInput.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                searchInput.value = '';
                hideSearchResults();
            }
        });
    }

    function filterMunicipios(query) {
        return municipiosList.filter(municipio => {
            const nome = municipio.nome.toLowerCase();
            const normalizado = municipio.nome.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();

            return nome.includes(query) ||
                   normalizado.includes(query) ||
                   nome.startsWith(query) ||
                   normalizado.startsWith(query);
        }).slice(0, 10); // Limita a 10 resultados
    }

    function showSearchResults(municipios) {
        const searchResults = document.getElementById('map-search-results');

        if (municipios.length === 0) {
            searchResults.innerHTML = '<div class="map-search-result-item">Nenhum município encontrado</div>';
        } else {
            searchResults.innerHTML = municipios.map(municipio =>
                `<div class="map-search-result-item" data-municipio="${municipio.nome}">
                    <strong>${municipio.nome}</strong>
                    <small class="text-muted ms-2">${municipio.oscs} OSCs</small>
                </div>`
            ).join('');

            // Adiciona event listeners para os itens
            searchResults.querySelectorAll('.map-search-result-item').forEach(item => {
                item.addEventListener('click', function() {
                    const municipioNome = this.getAttribute('data-municipio');
                    selectMunicipio(municipioNome);
                });
            });
        }

        searchResults.style.display = 'block';
    }

    function hideSearchResults() {
        const searchResults = document.getElementById('map-search-results');
        if (searchResults) {
            searchResults.style.display = 'none';
        }
    }

    function selectMunicipio(municipioNome) {
        const searchInput = document.getElementById('map-search');

        // Atualiza o campo de busca
        searchInput.value = municipioNome;
        hideSearchResults();

        // Encontra o layer do município no mapa
        if (municipioLayer) {
            municipioLayer.eachLayer(function(layer) {
                if (layer.feature.properties.NM_MUN === municipioNome) {
                    // Destaca o município
                    highlightMunicipio(layer);

                    // Centraliza o mapa no município
                    const bounds = layer.getBounds();
                    window.map.fitBounds(bounds, {
                        padding: [50, 50],
                        maxZoom: 10
                    });

                    // Abre o popup
                    layer.openPopup();

                    return;
                }
            });
        }
    }

    function highlightMunicipio(layer) {
        // Remove destaque anterior
        if (window.highlightedLayer) {
            municipioLayer.resetStyle(window.highlightedLayer);
        }

        // Aplica novo destaque
        layer.setStyle({
            weight: 4,
            color: '#3498db',
            dashArray: '',
            fillOpacity: 0.8
        });

        window.highlightedLayer = layer;

        // Remove destaque após 3 segundos
        setTimeout(() => {
            if (window.highlightedLayer === layer) {
                municipioLayer.resetStyle(layer);
                window.highlightedLayer = null;
            }
        }, 3000);
    }

    // Carrega dados de OSCs primeiro, depois o GeoJSON
    carregarDadosOSCs()
        .then(() => {
            console.log('Dados de OSCs carregados, agora carregando GeoJSON...');
            return fetch('/static/geojson/PR_Municipios_2023_optimized.geojson');
        })
        .then(response => {
            if (!response.ok) throw new Error('Erro ao carregar GeoJSON: ' + response.status);
            return response.json();
        })
        .then(geojsonData => {
            console.log('GeoJSON carregado, criando layer...');
            municipioLayer = L.geoJSON(geojsonData, {
                style: style,
                onEachFeature: onEachFeature
            }).addTo(window.map);

            // Popula a lista de municípios para busca
            municipiosList = [];
            municipioLayer.eachLayer(function(layer) {
                const municipio = layer.feature.properties.NM_MUN;
                const oscs = buscarOSCsPorMunicipio(municipio);
                municipiosList.push({
                    nome: municipio,
                    oscs: oscs,
                    layer: layer
                });
            });

            // Ordena por nome
            municipiosList.sort((a, b) => a.nome.localeCompare(b.nome));
            console.log('Lista de municípios criada:', municipiosList.length, 'municípios');

            // Inicializa a busca
            initializeMapSearch();

            // Ajusta o zoom para mostrar todo o Paraná
            window.map.fitBounds(municipioLayer.getBounds(), {padding: [20, 20]});

            console.log('Mapa criado com sucesso!');
        })
        .catch(error => {
            console.error('Erro ao carregar mapa:', error);
            mostrarErroNoMapa(error.message);
        });

    // Event listeners para redimensionamento
    window.addEventListener('resize', function() {
        if (window.map) {
            setTimeout(() => window.map.invalidateSize(), 100);
        }
    });

    // Redimensiona quando a aba fica visível
    document.addEventListener('visibilitychange', function() {
        if (!document.hidden && window.map) {
            setTimeout(() => window.map.invalidateSize(), 200);
        }
    });

    // Integração com filtro de município
    const municipioSelect = document.getElementById('municipio');
    if (municipioSelect) {
        municipioSelect.addEventListener('change', function() {
            const municipioSelecionado = this.value;

            if (municipioLayer) {
                municipioLayer.eachLayer(function(layer) {
                    if (layer.feature.properties.NM_MUN === municipioSelecionado) {
                        // Destaca o município selecionado
                        layer.setStyle({
                            fillColor: '#ff7800',
                            weight: 4,
                            color: '#ff7800',
                            fillOpacity: 0.8
                        });
                        window.map.fitBounds(layer.getBounds(), {padding: [20, 20]});
                        layer.openPopup();
                    } else {
                        // Restaura estilo padrão
                        municipioLayer.resetStyle(layer);
                    }
                });
            }
        });
    }

    console.log('Mapa inicializado com sucesso!');
});