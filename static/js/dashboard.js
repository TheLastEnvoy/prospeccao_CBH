// dashboard.js
// JS principal do dashboard: filtros, AJAX, tabela, paginação, exportação

document.addEventListener('DOMContentLoaded', function() {
    // Variáveis globais
    let currentPage = 1;
    let totalPages = 0;
    let totalRecords = 0;
    let currentFilters = {};
    let keywords = []; // Array para armazenar múltiplas palavras-chave
    let excludeKeywords = []; // Array para armazenar palavras-chave de exclusão
    let selectedMunicipios = []; // Array para armazenar múltiplos municípios
    let isMunicipiosExpanded = false;
    let selectedNaturezas = []; // Array para armazenar múltiplas naturezas jurídicas
    let selectedSituacoes = []; // Array para armazenar múltiplas situações cadastrais
    let allMunicipios = []; // Lista de todos os municípios disponíveis
    let cbhData = {}; // Mapeamento cbh_id → {nome, municipios[]}
    let selectedCBH = null; // CBH atualmente selecionado

    // Instância da tabela moderna
    let oscTable = null;
    const MAX_VISIBLE_MUNICIPIOS = 10;
    const statsTotalElement = document.getElementById('stats-total');
    const initialTotalRecords = parseInt(
        statsTotalElement ? (statsTotalElement.dataset.total || statsTotalElement.textContent || '0') : '0',
        10
    ) || 0;

    // Utilitários
    function escapeHtml(value) {
        const div = document.createElement('div');
        div.textContent = value == null ? '' : String(value);
        return div.innerHTML;
    }

    function showToast(type, message) {
        const toastElement = document.getElementById(`toast-${type}`);
        const messageElement = document.getElementById(`toast-${type}-message`);

        if (toastElement && messageElement) {
            messageElement.textContent = message;
            const toast = new bootstrap.Toast(toastElement);
            toast.show();
        }
    }

    function updateStats(filtered = 0) {
        const statsTotal = document.getElementById('stats-total');
        const statsFiltered = document.getElementById('stats-filtered');
        const totalOscs = document.getElementById('total-oscs');

        if (statsTotal) statsTotal.textContent = initialTotalRecords;
        if (statsFiltered) statsFiltered.textContent = filtered;
        if (totalOscs) totalOscs.textContent = filtered || initialTotalRecords;
    }

    function resetPaginationControls() {
        const infoPag = document.getElementById('info-paginacao');
        const paginaAt = document.getElementById('pagina-atual');
        const btnAnt = document.getElementById('btn-anterior');
        const btnProx = document.getElementById('btn-proximo');

        if (infoPag) infoPag.textContent = 'Mostrando 0 de 0 registros';
        if (paginaAt) paginaAt.textContent = 'Página 1';
        if (btnAnt) btnAnt.disabled = true;
        if (btnProx) btnProx.disabled = true;
    }

    function clearTableState() {
        if (!oscTable) return;

        oscTable.data = [];
        oscTable.filteredData = [];
        oscTable.currentPage = 1;
    }

    function getActiveFilterSummary() {
        const summary = [];
        const naturezasVer = Array.from(document.getElementById('naturezas_ver').selectedOptions).map(option => option.value);

        if (selectedCBH && cbhData[selectedCBH]) {
            summary.push({
                label: 'CBH',
                value: cbhData[selectedCBH].nome
            });
        }

        if (selectedMunicipios.length > 0) {
            summary.push({
                label: 'Municípios',
                value: `${selectedMunicipios.length} selecionado(s)`
            });
        }

        if (selectedNaturezas.length > 0) {
            summary.push({
                label: 'Naturezas',
                value: `${selectedNaturezas.length} selecionada(s)`
            });
        }

        if (selectedSituacoes.length > 0) {
            summary.push({
                label: 'Situações',
                value: `${selectedSituacoes.length} selecionada(s)`
            });
        }

        if (keywords.length > 0 || document.getElementById('palavras_chave').value.trim()) {
            const count = getKeywordsString().split(/\s+/).filter(Boolean).length;
            if (count > 0) {
                summary.push({
                    label: 'Incluir',
                    value: `${count} termo(s)`
                });
            }
        }

        if (excludeKeywords.length > 0 || document.getElementById('palavras_excluir').value.trim()) {
            const count = getExcludeKeywordsString().split(/\s+/).filter(Boolean).length;
            if (count > 0) {
                summary.push({
                    label: 'Excluir',
                    value: `${count} termo(s)`
                });
            }
        }

        if (naturezasVer.length > 0) {
            summary.push({
                label: 'Visualização',
                value: `${naturezasVer.length} natureza(s)`
            });
        }

        return summary;
    }

    function normalizeFilters(filters) {
        return JSON.stringify({
            municipio: filters.municipio || '',
            natureza_juridica: filters.natureza_juridica || '',
            palavras_chave: filters.palavras_chave || '',
            palavras_excluir: filters.palavras_excluir || '',
            situacao_cadastral: filters.situacao_cadastral || '',
            naturezas_ver: Array.isArray(filters.naturezas_ver) ? [...filters.naturezas_ver].sort() : []
        });
    }

    function havePendingFilterChanges() {
        return normalizeFilters(getFilters()) !== normalizeFilters(currentFilters);
    }

    function updateResultsStatus() {
        const badge = document.getElementById('results-status-badge');
        if (!badge) return;

        const activeFilters = getActiveFilterSummary().length;

        if (havePendingFilterChanges()) {
            badge.textContent = 'Filtros alterados, clique em Filtrar Dados';
            badge.classList.remove('section-status-badge--muted');
            return;
        }

        if (totalRecords > 0 && activeFilters === 0) {
            badge.textContent = 'Base completa carregada';
            badge.classList.remove('section-status-badge--muted');
            return;
        }

        if (totalRecords > 0) {
            badge.textContent = `${totalRecords} registro(s) disponível(is)`;
            badge.classList.remove('section-status-badge--muted');
            return;
        }

        if (activeFilters > 0) {
            badge.textContent = 'Consulta montada, aguardando retorno';
            badge.classList.remove('section-status-badge--muted');
            return;
        }

        badge.textContent = 'Aguardando consulta';
        badge.classList.add('section-status-badge--muted');
    }

    function updateMapVisibilityStatus(isVisible) {
        const badge = document.getElementById('map-visibility-status');
        if (!badge) return;

        badge.textContent = isVisible ? 'Mapa visível' : 'Mapa oculto';
    }

    function updateFilterSummaryUI() {
        const summary = getActiveFilterSummary();
        const summaryContainer = document.getElementById('active-filter-summary');
        const activeFilterBadge = document.getElementById('active-filter-count');
        const heroActiveFilters = document.getElementById('hero-active-filters');

        if (activeFilterBadge) {
            activeFilterBadge.textContent = `${summary.length} filtro(s) ativo(s)`;
        }

        if (heroActiveFilters) {
            heroActiveFilters.textContent = summary.length;
        }

        if (!summaryContainer) return;

        if (summary.length === 0) {
            summaryContainer.innerHTML = '<span class="filter-chip filter-chip--placeholder">Nenhum filtro ativo</span>';
            const activeFiltersValue = document.getElementById('insight-active-filters');
            const activeFiltersDetail = document.getElementById('insight-active-filters-detail');
            if (activeFiltersValue) activeFiltersValue.textContent = '0';
            if (activeFiltersDetail) activeFiltersDetail.textContent = 'Consulta ampla em toda a base';
            updateResultsStatus();
            return;
        }

        summaryContainer.innerHTML = summary.map(item =>
            `<span class="filter-chip"><strong>${escapeHtml(item.label)}:</strong> ${escapeHtml(item.value)}</span>`
        ).join('');

        const activeFiltersValue = document.getElementById('insight-active-filters');
        const activeFiltersDetail = document.getElementById('insight-active-filters-detail');
        if (activeFiltersValue) activeFiltersValue.textContent = String(summary.length);
        if (activeFiltersDetail) activeFiltersDetail.textContent = 'Consulta refinada por critérios ativos';

        updateResultsStatus();
    }

    function getTopOccurrence(data, key) {
        if (!Array.isArray(data) || data.length === 0) return null;

        const counts = {};
        data.forEach(item => {
            const value = item[key];
            if (!value) return;
            counts[value] = (counts[value] || 0) + 1;
        });

        return Object.entries(counts).sort((a, b) => b[1] - a[1])[0] || null;
    }

    function updateDashboardInsights(data = []) {
        const activeFilters = getActiveFilterSummary();
        const resultsTotal = document.getElementById('insight-results-total');
        const pagePreview = document.getElementById('insight-page-preview');
        const coverageValue = document.getElementById('insight-coverage-value');
        const coverageBar = document.getElementById('insight-coverage-bar');
        const coverageDetail = document.getElementById('insight-coverage-detail');
        const activeFiltersValue = document.getElementById('insight-active-filters');
        const activeFiltersDetail = document.getElementById('insight-active-filters-detail');
        const focusTitle = document.getElementById('insight-focus-title');
        const focusDetail = document.getElementById('insight-focus-detail');
        const topMunicipio = getTopOccurrence(data, 'edmu_nm_municipio');
        const topNatureza = getTopOccurrence(data, 'natureza_juridica');
        const coverage = initialTotalRecords > 0 ? Math.min(100, Math.round((totalRecords / initialTotalRecords) * 100)) : 0;

        if (resultsTotal) resultsTotal.textContent = totalRecords;

        if (pagePreview) {
            pagePreview.textContent = data.length > 0
                ? `${data.length} registro(s) exibido(s) na página atual`
                : (getActiveFilterSummary().length > 0 || totalRecords > 0 ? 'Nenhum registro na página atual' : 'Aguardando a primeira consulta');
        }

        if (coverageValue) coverageValue.textContent = `${coverage}%`;
        if (coverageBar) coverageBar.style.width = `${coverage}%`;
        if (coverageDetail) {
            coverageDetail.textContent = totalRecords > 0
                ? `${totalRecords} de ${initialTotalRecords} registro(s) dentro do recorte`
                : 'Nenhum recorte retornado no momento';
        }

        if (activeFiltersValue) activeFiltersValue.textContent = activeFilters.length;
        if (activeFiltersDetail) {
            activeFiltersDetail.textContent = activeFilters.length > 0
                ? 'Consulta refinada por critérios ativos'
                : 'Consulta ampla em toda a base';
        }

        if (focusTitle && focusDetail) {
            if (selectedCBH && cbhData[selectedCBH]) {
                focusTitle.textContent = cbhData[selectedCBH].nome;
                focusDetail.textContent = `${selectedMunicipios.length} município(s) carregado(s) pelo CBH`;
            } else if (selectedMunicipios.length > 0) {
                focusTitle.textContent = `${selectedMunicipios.length} município(s) em foco`;
                focusDetail.textContent = selectedMunicipios.slice(0, 2).join(' • ');
            } else if (topMunicipio) {
                focusTitle.textContent = topMunicipio[0];
                focusDetail.textContent = `Maior concentração nesta página: ${topMunicipio[1]} registro(s)`;
            } else if (topNatureza) {
                focusTitle.textContent = topNatureza[0];
                focusDetail.textContent = `Natureza em destaque nesta página: ${topNatureza[1]} registro(s)`;
            } else {
                focusTitle.textContent = 'Visão estadual';
                focusDetail.textContent = 'Sem município ou CBH priorizado';
            }
        }
    }

    function handleEmptyMunicipioResult(municipio) {
        // Limpar filtros
        clearAllFilters();

        // Mostrar mensagem específica
        showToast('warning', `O município "${municipio}" não possui OSCs cadastradas.`);

        // Atualizar tabela com mensagem específica
        const tbody = document.getElementById('tabela-body');
        tbody.innerHTML = `
            <tr>
                <td colspan="9" class="text-center text-warning py-5">
                    <i class="fas fa-exclamation-triangle fa-2x mb-3 d-block"></i>
                    <h6>Município sem OSCs cadastradas</h6>
                    <p class="mb-2">O município <strong>"${municipio}"</strong> não possui OSCs cadastradas no sistema.</p>
                    <p class="mb-0 text-muted">Os filtros foram limpos automaticamente. Tente selecionar outro município.</p>
                </td>
            </tr>
        `;

        // Reset stats
        updateStats(0);

        // Reset pagination
        currentPage = 1;
        totalPages = 0;
        totalRecords = 0;
        clearTableState();
        resetPaginationControls();
        updateDashboardInsights([]);
        updateResultsStatus();
    }

    // ── CBH ─────────────────────────────────────────────────────────────────

    function selectCBH(cbh_id) {
        const cbh = cbhData[cbh_id];
        if (!cbh) return;

        selectedCBH = cbh_id;

        // Substitui todos os municípios selecionados pelos do CBH
        selectedMunicipios = [...cbh.municipios];
        isMunicipiosExpanded = false;
        updateMunicipiosList();

        // Atualiza info visual
        const infoEl = document.getElementById('cbh-info');
        const countEl = document.getElementById('cbh-municipios-count');
        if (infoEl && countEl) {
            countEl.textContent = cbh.municipios.length;
            infoEl.style.display = 'block';
        }

        updateFilterSummaryUI();
        updateDashboardInsights([]);
        showToast('success', `${cbh.nome}: ${cbh.municipios.length} municípios carregados.`);
    }

    function clearCBH() {
        selectedCBH = null;
        const selector = document.getElementById('cbh_selector');
        if (selector) selector.value = '';
        const infoEl = document.getElementById('cbh-info');
        if (infoEl) infoEl.style.display = 'none';
        selectedMunicipios = [];
        isMunicipiosExpanded = false;
        updateMunicipiosList();
        updateFilterSummaryUI();
        updateDashboardInsights([]);
    }

    // ── Filtros ──────────────────────────────────────────────────────────────

    function clearAllFilters() {
        document.getElementById('municipio').value = '';
        document.getElementById('natureza_juridica').value = '';
        document.getElementById('palavras_chave').value = '';
        document.getElementById('palavras_excluir').value = '';
        document.getElementById('situacao_cadastral').value = '';
        document.getElementById('naturezas_ver').selectedIndex = -1;

        // Limpa seleção de CBH
        clearCBH();

        // Limpar palavras-chave múltiplas
        keywords = [];
        updateKeywordsList();

        // Limpar palavras-chave de exclusão
        excludeKeywords = [];
        updateExcludeKeywordsList();

        // Limpar municípios múltiplos
        selectedMunicipios = [];
        isMunicipiosExpanded = false;
        updateMunicipiosList();

        // Limpar naturezas jurídicas múltiplas
        selectedNaturezas = [];
        updateNaturezasList();

        // Limpar situações cadastrais múltiplas
        selectedSituacoes = [];
        updateSituacoesList();

        // Reset current filters
        currentFilters = {};
        updateFilterSummaryUI();
        updateDashboardInsights([]);
    }

    // Funções para gerenciar múltiplas palavras-chave
    function addKeyword() {
        const input = document.getElementById('palavras_chave');
        const keyword = input.value.trim();

        if (keyword && !keywords.includes(keyword)) {
            keywords.push(keyword);
            input.value = '';
            updateKeywordsList();
            // Não executa busca automática - só quando clicar em "Filtrar Dados"
        }
    }

    function removeKeyword(keyword) {
        keywords = keywords.filter(k => k !== keyword);
        updateKeywordsList();
        // Não executa busca automática - só quando clicar em "Filtrar Dados"
    }

    function updateKeywordsList() {
        const container = document.getElementById('keywords-list');
        if (!container) return;

        container.innerHTML = keywords.map(keyword =>
            `<span class="keyword-tag">
                ${keyword}
                <button type="button" class="remove-keyword" onclick="removeKeyword('${keyword}')" title="Remover">
                    <i class="fas fa-times"></i>
                </button>
            </span>`
        ).join('');
        updateFilterSummaryUI();
    }

    function getKeywordsString() {
        // Pegar palavras-chave do array E do campo de input (caso o usuário não tenha clicado em +)
        const inputKeywords = document.getElementById('palavras_chave').value.trim();
        const allKeywords = [...keywords];

        // Adicionar palavras do input que não estão no array
        if (inputKeywords) {
            const inputWords = inputKeywords.split(/\s+/).filter(word => word.trim());
            inputWords.forEach(word => {
                if (!allKeywords.includes(word.trim())) {
                    allKeywords.push(word.trim());
                }
            });
        }

        return allKeywords.join(' ');
    }

    // Funções para gerenciar palavras-chave de exclusão
    function addExcludeKeyword() {
        const input = document.getElementById('palavras_excluir');
        const keyword = input.value.trim();

        if (keyword && !excludeKeywords.includes(keyword)) {
            excludeKeywords.push(keyword);
            input.value = '';
            updateExcludeKeywordsList();
        }
    }

    function removeExcludeKeyword(keyword) {
        excludeKeywords = excludeKeywords.filter(k => k !== keyword);
        updateExcludeKeywordsList();
    }

    function updateExcludeKeywordsList() {
        const container = document.getElementById('exclude-keywords-list');
        if (!container) return;

        container.innerHTML = excludeKeywords.map(keyword =>
            `<span class="exclude-keyword-tag">
                ${keyword}
                <button type="button" class="remove-exclude-keyword" onclick="removeExcludeKeyword('${keyword.replace(/'/g, "\\\'")}')" title="Remover">
                    <i class="fas fa-times"></i>
                </button>
            </span>`
        ).join('');
        updateFilterSummaryUI();
    }

    function getExcludeKeywordsString() {
        // Pegar palavras de exclusão do array E do campo de input
        const inputExcludeKeywords = document.getElementById('palavras_excluir').value.trim();
        const allExcludeKeywords = [...excludeKeywords];

        // Adicionar palavras do input que não estão no array
        if (inputExcludeKeywords) {
            const inputWords = inputExcludeKeywords.split(/\s+/).filter(word => word.trim());
            inputWords.forEach(word => {
                if (!allExcludeKeywords.includes(word.trim())) {
                    allExcludeKeywords.push(word.trim());
                }
            });
        }

        return allExcludeKeywords.join(' ');
    }

    // Funções para gerenciar múltiplos municípios
    function addMunicipio() {
        const input = document.getElementById('municipio');
        const municipio = input.value.trim();

        if (municipio && !selectedMunicipios.includes(municipio)) {
            // Verifica se o município existe na lista
            const municipioExists = allMunicipios.some(m =>
                m.toLowerCase() === municipio.toLowerCase()
            );

            if (municipioExists) {
                selectedMunicipios.push(municipio);
                isMunicipiosExpanded = false;
                input.value = '';
                updateMunicipiosList();
                hideMunicipioSuggestions();
            } else {
                showToast('warning', 'Município não encontrado. Selecione da lista de sugestões.');
            }
        }
    }

    function removeMunicipio(municipio) {
        selectedMunicipios = selectedMunicipios.filter(m => m !== municipio);
        if (selectedMunicipios.length <= MAX_VISIBLE_MUNICIPIOS) {
            isMunicipiosExpanded = false;
        }
        updateMunicipiosList();
    }

    function toggleMunicipiosExpansion() {
        isMunicipiosExpanded = !isMunicipiosExpanded;
        updateMunicipiosList();
    }

    function updateMunicipiosList() {
        const container = document.getElementById('municipios-list');
        if (!container) return;

        const hasOverflow = selectedMunicipios.length > MAX_VISIBLE_MUNICIPIOS;
        const visibleMunicipios = hasOverflow && !isMunicipiosExpanded
            ? selectedMunicipios.slice(0, MAX_VISIBLE_MUNICIPIOS)
            : selectedMunicipios;
        const hiddenCount = selectedMunicipios.length - visibleMunicipios.length;

        container.innerHTML = visibleMunicipios.map(municipio =>
            `<span class="municipio-tag">
                ${municipio}
                <button type="button" class="remove-municipio" onclick="removeMunicipio('${municipio.replace(/'/g, "\\\'")}')" title="Remover">
                    <i class="fas fa-times"></i>
                </button>
            </span>`
        ).join('');

        if (hasOverflow && !isMunicipiosExpanded) {
            container.innerHTML += `
                <button type="button" class="municipio-overflow-toggle" onclick="toggleMunicipiosExpansion()" title="Mostrar mais municípios">
                    &hellip;
                    <span>+${hiddenCount}</span>
                </button>
            `;
        } else if (hasOverflow) {
            container.innerHTML += `
                <button type="button" class="municipio-overflow-toggle municipio-overflow-toggle--expanded" onclick="toggleMunicipiosExpansion()" title="Mostrar menos municípios">
                    Recolher
                </button>
            `;
        }

        updateFilterSummaryUI();
    }

    function getMunicipiosString() {
        return selectedMunicipios.join(',');
    }

    // Funções para gerenciar múltiplas naturezas jurídicas
    function addNatureza() {
        const select = document.getElementById('natureza_juridica');
        const natureza = select.value.trim();

        if (natureza && !selectedNaturezas.includes(natureza)) {
            selectedNaturezas.push(natureza);
            select.value = '';
            updateNaturezasList();
        }
    }

    function removeNatureza(natureza) {
        selectedNaturezas = selectedNaturezas.filter(n => n !== natureza);
        updateNaturezasList();
    }

    function updateNaturezasList() {
        const container = document.getElementById('naturezas-list');
        if (!container) return;

        container.innerHTML = selectedNaturezas.map(natureza =>
            `<span class="natureza-tag">
                ${natureza}
                <button type="button" class="remove-natureza" onclick="removeNatureza('${natureza.replace(/'/g, "\\\'")}')" title="Remover">
                    <i class="fas fa-times"></i>
                </button>
            </span>`
        ).join('');
        updateFilterSummaryUI();
    }

    function getNaturezasString() {
        return selectedNaturezas.join(',');
    }

    // Funções para gerenciar múltiplas situações cadastrais
    function addSituacao() {
        const select = document.getElementById('situacao_cadastral');
        const situacao = select.value.trim();

        if (situacao && !selectedSituacoes.includes(situacao)) {
            selectedSituacoes.push(situacao);
            select.value = '';
            updateSituacoesList();
        }
    }

    function removeSituacao(situacao) {
        selectedSituacoes = selectedSituacoes.filter(s => s !== situacao);
        updateSituacoesList();
    }

    function updateSituacoesList() {
        const container = document.getElementById('situacoes-list');
        if (!container) return;

        container.innerHTML = selectedSituacoes.map(situacao =>
            `<span class="situacao-tag">
                ${situacao}
                <button type="button" class="remove-situacao" onclick="removeSituacao('${situacao.replace(/'/g, "\\\'")}')" title="Remover">
                    <i class="fas fa-times"></i>
                </button>
            </span>`
        ).join('');
        updateFilterSummaryUI();
    }

    function getSituacoesString() {
        return selectedSituacoes.join(',');
    }

    function filterMunicipios(query) {
        if (!query || query.length < 2) return [];

        return allMunicipios.filter(municipio => {
            const nome = municipio.toLowerCase();
            const normalizado = municipio.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
            const queryLower = query.toLowerCase();
            const queryNormalizado = query.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();

            return nome.includes(queryLower) ||
                   normalizado.includes(queryNormalizado) ||
                   nome.startsWith(queryLower) ||
                   normalizado.startsWith(queryNormalizado);
        }).slice(0, 10); // Limita a 10 resultados
    }

    function showMunicipioSuggestions(municipios) {
        const suggestions = document.getElementById('municipio-suggestions');

        if (municipios.length === 0) {
            suggestions.innerHTML = '<div class="municipio-suggestion-item">Nenhum município encontrado</div>';
        } else {
            suggestions.innerHTML = municipios.map(municipio =>
                `<div class="municipio-suggestion-item" data-municipio="${municipio}">
                    ${municipio}
                </div>`
            ).join('');

            // Adiciona event listeners para os itens
            suggestions.querySelectorAll('.municipio-suggestion-item').forEach(item => {
                item.addEventListener('click', function() {
                    const municipioNome = this.getAttribute('data-municipio');
                    if (municipioNome && municipioNome !== 'Nenhum município encontrado') {
                        document.getElementById('municipio').value = municipioNome;
                        addMunicipio();
                    }
                });
            });
        }

        suggestions.style.display = 'block';
    }

    function hideMunicipioSuggestions() {
        const suggestions = document.getElementById('municipio-suggestions');
        if (suggestions) {
            suggestions.style.display = 'none';
        }
    }

    function initializeMunicipioSearch() {
        const municipioInput = document.getElementById('municipio');
        const suggestions = document.getElementById('municipio-suggestions');

        if (!municipioInput || !suggestions) return;

        // Event listener para input de busca
        municipioInput.addEventListener('input', function(e) {
            const query = e.target.value.trim();

            if (query.length === 0) {
                hideMunicipioSuggestions();
                return;
            }

            if (query.length < 2) {
                return; // Só busca com 2+ caracteres
            }

            const filteredMunicipios = filterMunicipios(query);
            showMunicipioSuggestions(filteredMunicipios);
        });

        // Esconder sugestões quando clicar fora
        document.addEventListener('click', function(e) {
            if (!municipioInput.contains(e.target) && !suggestions.contains(e.target)) {
                hideMunicipioSuggestions();
            }
        });

        // Enter para adicionar município
        municipioInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                addMunicipio();
            }
        });

        // ESC para limpar
        municipioInput.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                municipioInput.value = '';
                hideMunicipioSuggestions();
            }
        });
    }
    function showLoading(shouldScroll = true) {
        const loadingSection = document.getElementById('loading-section');
        if (loadingSection) {
            loadingSection.style.display = 'block';
            if (shouldScroll) {
                loadingSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }
    }

    function hideLoading() {
        const loadingSection = document.getElementById('loading-section');
        if (loadingSection) loadingSection.style.display = 'none';
    }

    function toggleMapSection() {
        const mapSection = document.getElementById('mapa-section');
        const toggleBtn = document.getElementById('btn-toggle-mapa');
        const icon = document.getElementById('btn-toggle-mapa-icon');
        const text = document.getElementById('btn-toggle-mapa-text');

        if (mapSection && toggleBtn && icon && text) {
            // Verifica se está visível (considera tanto display: none quanto ausência de style)
            const computedStyle = window.getComputedStyle(mapSection);
            const isVisible = computedStyle.display !== 'none';

            mapSection.style.display = isVisible ? 'none' : 'block';

            if (isVisible) {
                icon.className = 'fas fa-map me-2';
                text.textContent = 'Mostrar Mapa';
            } else {
                icon.className = 'fas fa-map-slash me-2';
                text.textContent = 'Ocultar Mapa';

                // Trigger map resize if it exists
                if (window.map) {
                    setTimeout(() => window.map.invalidateSize(), 300);
                }
            }

            updateMapVisibilityStatus(!isVisible);
        }
    }

    // Função para inicializar o estado do botão do mapa
    function initializeMapToggleButton() {
        const mapSection = document.getElementById('mapa-section');
        const toggleBtn = document.getElementById('btn-toggle-mapa');
        const icon = document.getElementById('btn-toggle-mapa-icon');
        const text = document.getElementById('btn-toggle-mapa-text');

        if (mapSection && toggleBtn && icon && text) {
            const computedStyle = window.getComputedStyle(mapSection);
            const isVisible = computedStyle.display !== 'none';

            if (isVisible) {
                icon.className = 'fas fa-map-slash me-2';
                text.textContent = 'Ocultar Mapa';
            } else {
                icon.className = 'fas fa-map me-2';
                text.textContent = 'Mostrar Mapa';
            }

            updateMapVisibilityStatus(isVisible);
        }
    }
    function getFilters() {
        return {
            municipio: getMunicipiosString(),
            natureza_juridica: getNaturezasString(),
            palavras_chave: getKeywordsString(),
            palavras_excluir: getExcludeKeywordsString(),
            situacao_cadastral: getSituacoesString(),
            naturezas_ver: Array.from(document.getElementById('naturezas_ver').selectedOptions).map(option => option.value)
        };
    }

    function loadData(page = 1, shouldScroll = true) {
        console.log('Iniciando loadData, página:', page);
        showLoading(shouldScroll);

        currentFilters = getFilters();
        const data = {
            ...currentFilters,
            page: page,
            per_page: 50
        };

        console.log('Dados a serem enviados:', data);
        console.log('URL da API:', filterDataUrl);

        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        console.log('CSRF Token encontrado:', csrfToken ? 'Sim' : 'Não');

        fetch(filterDataUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return response.json();
        })
        .then(response => {
            hideLoading();

            if (response.error) {
                showToast('error', 'Erro: ' + response.error);
                return;
            }

            currentPage = response.page;
            totalPages = response.total_pages;
            totalRecords = response.total;

            // Verificar se não há resultados e há filtro de município
            if (response.total === 0 && currentFilters.municipio) {
                handleEmptyMunicipioResult(currentFilters.municipio);
                return;
            }

            updateTable(response.data);
            // Atualiza controles de paginação diretamente com valores do servidor
            // (evita sobreposição pelos valores do oscTable, que só conhece a página atual de 50 itens)
            {
                const perPage = response.per_page || 50;
                const startItem = totalRecords > 0 ? (currentPage - 1) * perPage + 1 : 0;
                const endItem = Math.min(currentPage * perPage, totalRecords);
                const infoPag = document.getElementById('info-paginacao');
                const paginaAt = document.getElementById('pagina-atual');
                const btnAnt = document.getElementById('btn-anterior');
                const btnProx = document.getElementById('btn-proximo');
                if (infoPag) infoPag.textContent = `Mostrando ${startItem} a ${endItem} de ${totalRecords} registros`;
                if (paginaAt) paginaAt.textContent = `Página ${currentPage} de ${totalPages}`;
                if (btnAnt) btnAnt.disabled = currentPage <= 1;
                if (btnProx) btnProx.disabled = currentPage >= totalPages;
            }
            updateStats(response.total);
            updateDashboardInsights(response.data);
            updateResultsStatus();

            if (response.total > 0) {
                showToast('success', `${response.data.length} registros carregados com sucesso!`);
            } else {
                showToast('info', 'Nenhum resultado encontrado com os filtros aplicados.');
            }
        })
        .catch(error => {
            hideLoading();
            console.error('Erro na requisição:', error);
            showToast('error', 'Erro ao carregar dados. Tente novamente.');
        });
    }
    function updateTable(data) {
        // Usar a nova implementação de tabela moderna
        if (oscTable) {
            oscTable.filterData(data);
        } else {
            console.warn('OSCTable não foi inicializada');
        }
    }
    function updatePaginationInfo() {
        // A paginação agora é gerenciada pela OSCTable
        // Esta função é mantida para compatibilidade, mas a lógica foi movida para OSCTable
        if (oscTable) {
            currentPage = oscTable.getCurrentPage();
            totalPages = oscTable.getTotalPages();
            totalRecords = oscTable.getTotalRecords();
        }
    }

    function exportData() {
        const exportBtn = document.getElementById('btn-exportar');
        const originalText = exportBtn.innerHTML;
        const exportFilters = normalizeFilters(currentFilters) === normalizeFilters({})
            ? getFilters()
            : currentFilters;

        // Desabilita o botão e mostra loading
        exportBtn.disabled = true;
        exportBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Exportando...';

        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        if (havePendingFilterChanges()) {
            showToast('info', 'Exportando conforme a última filtragem aplicada na tabela.');
        }

        fetch(exportDataUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(exportFilters)
        })
        .then(response => {
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return response.blob();
        })
        .then(blob => {
            // Cria link para download
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `OSCs_Parana_${new Date().toISOString().slice(0,10)}.xlsx`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            showToast('success', 'Arquivo exportado com sucesso!');
        })
        .catch(error => {
            console.error('Erro na exportação:', error);
            showToast('error', 'Erro ao exportar dados. Tente novamente.');
        })
        .finally(() => {
            // Restaura o botão
            exportBtn.disabled = false;
            exportBtn.innerHTML = originalText;
        });
    }
    // Event Listeners
    document.getElementById('btn-filtrar').addEventListener('click', function() {
        loadData(1);
    });

    document.getElementById('btn-exportar').addEventListener('click', function() {
        if (totalRecords === 0) {
            showToast('error', 'Nenhum dado para exportar. Execute uma pesquisa primeiro.');
            return;
        }
        exportData();
    });

    document.getElementById('btn-anterior').addEventListener('click', function() {
        if (currentPage > 1) {
            loadData(currentPage - 1);
        }
    });

    document.getElementById('btn-proximo').addEventListener('click', function() {
        if (currentPage < totalPages) {
            loadData(currentPage + 1);
        }
    });

    document.getElementById('btn-limpar').addEventListener('click', function() {
        clearAllFilters();

        // Reset stats
        updateStats(0);

        // Clear table
        const tbody = document.getElementById('tabela-body');
        tbody.innerHTML = `
            <tr>
                <td colspan="9" class="text-center text-muted py-5">
                    <i class="fas fa-search fa-2x mb-3 d-block"></i>
                    <h6>Nenhum dado carregado</h6>
                    <p class="mb-0">Clique em "Filtrar Dados" para carregar os resultados</p>
                </td>
            </tr>
        `;

        // Reset pagination
        currentPage = 1;
        totalPages = 0;
        totalRecords = 0;
        clearTableState();
        resetPaginationControls();
        updateDashboardInsights([]);
        updateResultsStatus();

        showToast('success', 'Filtros limpos com sucesso!');
    });

    document.getElementById('btn-toggle-mapa').addEventListener('click', toggleMapSection);

    // Event listeners para palavras-chave múltiplas
    const palavrasChaveInput = document.getElementById('palavras_chave');

    // Prevenir qualquer busca automática
    palavrasChaveInput.addEventListener('input', function(e) {
        // Não faz nada - apenas previne outros event listeners
        e.stopPropagation();
        updateFilterSummaryUI();
    });

    palavrasChaveInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            addKeyword();
        }
    });

    // Prevenir eventos de change que possam disparar busca
    palavrasChaveInput.addEventListener('change', function(e) {
        e.stopPropagation();
        updateFilterSummaryUI();
    });

    document.getElementById('btn-add-keyword').addEventListener('click', function() {
        addKeyword();
    });

    // Event listeners para naturezas jurídicas múltiplas
    document.getElementById('btn-add-natureza').addEventListener('click', function() {
        addNatureza();
    });

    // Permitir adicionar natureza com Enter
    document.getElementById('natureza_juridica').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            addNatureza();
        }
    });

    // Event listeners para palavras-chave de exclusão
    document.getElementById('btn-add-exclude-keyword').addEventListener('click', function() {
        addExcludeKeyword();
    });

    // Permitir adicionar palavra de exclusão com Enter
    document.getElementById('palavras_excluir').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            addExcludeKeyword();
        }
    });

    document.getElementById('palavras_excluir').addEventListener('input', function() {
        updateFilterSummaryUI();
    });

    // Event listeners para situações cadastrais múltiplas
    document.getElementById('btn-add-situacao').addEventListener('click', function() {
        addSituacao();
    });

    // Permitir adicionar situação com Enter
    document.getElementById('situacao_cadastral').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            addSituacao();
        }
    });

    // Event listeners para municípios múltiplos
    document.getElementById('btn-add-municipio').addEventListener('click', function() {
        addMunicipio();
    });

    document.getElementById('naturezas_ver').addEventListener('change', function() {
        updateFilterSummaryUI();
        updateDashboardInsights([]);
    });

    // Inicializar busca de municípios
    initializeMunicipioSearch();

    // Remover auto-search - agora só busca quando clicar em "Filtrar Dados"

    // Keyboard navigation for accessibility
    document.addEventListener('keydown', function(e) {
        // Ctrl+F to focus search
        if (e.ctrlKey && e.key === 'f') {
            e.preventDefault();
            document.getElementById('palavras_chave').focus();
        }

        // Escape to clear search
        if (e.key === 'Escape') {
            const searchInput = document.getElementById('palavras_chave');
            if (document.activeElement === searchInput) {
                searchInput.value = '';
                searchInput.blur();
                // Limpar todas as palavras-chave se não houver nenhuma no input
                if (keywords.length > 0) {
                    keywords = [];
                    updateKeywordsList();
                    // Não executa busca automática - só quando clicar em "Filtrar Dados"
                }
            }
        }
    });

    // Improve form accessibility
    const formElements = document.querySelectorAll('input, select, button');
    formElements.forEach(element => {
        // Add proper ARIA labels if missing
        if (!element.getAttribute('aria-label') && !element.getAttribute('aria-labelledby')) {
            const label = element.previousElementSibling;
            if (label && label.tagName === 'LABEL') {
                element.setAttribute('aria-labelledby', label.id || 'label-' + Math.random().toString(36).substr(2, 9));
            }
        }
    });

    // Performance monitoring
    if ('performance' in window) {
        window.addEventListener('load', function() {
            setTimeout(() => {
                const perfData = performance.getEntriesByType('navigation')[0];
                console.log('Dashboard carregado em:', Math.round(perfData.loadEventEnd - perfData.fetchStart), 'ms');
            }, 0);
        });
    }

    // Service Worker registration for offline support (optional)
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', function() {
            // Uncomment to enable service worker
            // navigator.serviceWorker.register('/sw.js').catch(err => console.log('SW registration failed'));
        });
    }

    // Inicializa o estado do botão do mapa
    initializeMapToggleButton();
    updateFilterSummaryUI();
    updateDashboardInsights([]);
    updateResultsStatus();

    console.log('Dashboard inicializado com sucesso!');

    // Carregar lista de municípios do template
    const municipiosScript = document.querySelector('script[data-municipios]');
    if (municipiosScript) {
        try {
            allMunicipios = JSON.parse(municipiosScript.textContent);
            console.log('Municípios carregados:', allMunicipios.length);
        } catch (e) {
            console.error('Erro ao carregar lista de municípios:', e);
            allMunicipios = [];
        }
    } else {
        console.warn('Lista de municípios não encontrada no template');
        allMunicipios = [];
    }

    // Carregar mapeamento CBH → municípios do template
    const cbhScript = document.querySelector('script[data-cbh-municipios]');
    if (cbhScript) {
        try {
            cbhData = JSON.parse(cbhScript.textContent);
            console.log('CBHs carregados:', Object.keys(cbhData).length);
        } catch (e) {
            console.error('Erro ao carregar dados CBH:', e);
            cbhData = {};
        }
    }

    // Event listener do seletor de CBH
    const cbhSelector = document.getElementById('cbh_selector');
    if (cbhSelector) {
        cbhSelector.addEventListener('change', function() {
            const cbh_id = this.value;
            if (cbh_id) {
                selectCBH(cbh_id);
            } else {
                clearCBH();
            }
        });
    }

    // Botão de limpar CBH
    const btnLimparCbh = document.getElementById('btn-limpar-cbh');
    if (btnLimparCbh) {
        btnLimparCbh.addEventListener('click', function(e) {
            e.preventDefault();
            clearCBH();
        });
    }

    // Inicializar a nova tabela moderna
    if (typeof OSCTable !== 'undefined') {
        oscTable = new OSCTable('tabela-oscs', {
            sortable: true,
            searchable: false, // Busca é feita externamente
            pagination: false, // Paginação é feita externamente
            pageSize: 50
        });

        console.log('OSCTable inicializada com sucesso!');
    } else {
        console.warn('OSCTable não está disponível. Verifique se o arquivo osc-table.js foi carregado.');
    }

    // Tornar funções globais para uso em onclick
    window.removeKeyword = removeKeyword;
    window.removeExcludeKeyword = removeExcludeKeyword;
    window.removeMunicipio = removeMunicipio;
    window.toggleMunicipiosExpansion = toggleMunicipiosExpansion;
    window.removeNatureza = removeNatureza;
    window.removeSituacao = removeSituacao;
});
