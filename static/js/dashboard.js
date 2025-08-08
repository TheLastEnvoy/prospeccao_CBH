// dashboard.js
// JS principal do dashboard: filtros, AJAX, tabela, paginação, exportação

document.addEventListener('DOMContentLoaded', function() {
    // Variáveis globais
    let currentPage = 1;
    let totalPages = 0;
    let totalRecords = 0;
    let currentFilters = {};

    // Utilitários
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

        if (statsFiltered) statsFiltered.textContent = filtered;
        if (totalOscs) totalOscs.textContent = filtered || totalRecords;
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
                <td colspan="8" class="text-center text-warning py-5">
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
        updatePaginationInfo();
    }

    function clearAllFilters() {
        document.getElementById('municipio').value = '';
        document.getElementById('natureza_juridica').value = '';
        document.getElementById('palavras_chave').value = '';
        document.getElementById('naturezas_ver').selectedIndex = -1;

        // Reset current filters
        currentFilters = {};
    }
    function showLoading() {
        const loadingSection = document.getElementById('loading-section');
        if (loadingSection) {
            loadingSection.style.display = 'block';
            loadingSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    function hideLoading() {
        const loadingSection = document.getElementById('loading-section');
        if (loadingSection) loadingSection.style.display = 'none';
    }

    function toggleMapSection() {
        const mapSection = document.getElementById('mapa-section');
        const toggleBtn = document.getElementById('btn-toggle-mapa');

        if (mapSection && toggleBtn) {
            // Verifica se está visível (considera tanto display: none quanto ausência de style)
            const computedStyle = window.getComputedStyle(mapSection);
            const isVisible = computedStyle.display !== 'none';

            mapSection.style.display = isVisible ? 'none' : 'block';

            const icon = toggleBtn.querySelector('i');
            const text = toggleBtn.childNodes[toggleBtn.childNodes.length - 1];

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
        }
    }

    // Função para inicializar o estado do botão do mapa
    function initializeMapToggleButton() {
        const mapSection = document.getElementById('mapa-section');
        const toggleBtn = document.getElementById('btn-toggle-mapa');

        if (mapSection && toggleBtn) {
            const computedStyle = window.getComputedStyle(mapSection);
            const isVisible = computedStyle.display !== 'none';

            const icon = toggleBtn.querySelector('i');
            const text = toggleBtn.childNodes[toggleBtn.childNodes.length - 1];

            if (isVisible) {
                icon.className = 'fas fa-map-slash me-2';
                text.textContent = 'Ocultar Mapa';
            } else {
                icon.className = 'fas fa-map me-2';
                text.textContent = 'Mostrar Mapa';
            }
        }
    }
    function getFilters() {
        return {
            municipio: document.getElementById('municipio').value,
            natureza_juridica: document.getElementById('natureza_juridica').value,
            palavras_chave: document.getElementById('palavras_chave').value,
            naturezas_ver: Array.from(document.getElementById('naturezas_ver').selectedOptions).map(option => option.value)
        };
    }

    function loadData(page = 1) {
        console.log('Iniciando loadData, página:', page);
        showLoading();

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
            updatePaginationInfo();
            updateStats(response.total);

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
        const tbody = document.getElementById('tabela-body');
        tbody.innerHTML = '';

        if (data.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="8" class="text-center text-muted py-5">
                        <i class="fas fa-search fa-2x mb-3 d-block"></i>
                        <h6>Nenhum resultado encontrado</h6>
                        <p class="mb-0">Tente ajustar os filtros de pesquisa</p>
                    </td>
                </tr>
            `;
            return;
        }

        data.forEach(function(osc, index) {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><span class="badge bg-primary">${osc.id_osc || '-'}</span></td>
                <td class="fw-semibold">${osc.nome || '-'}</td>
                <td>
                    ${osc.email ? `<a href="mailto:${osc.email}" class="text-decoration-none">${osc.email}</a>` : '-'}
                </td>
                <td>${osc.endereco || '-'}</td>
                <td>
                    ${osc.telefone ? `<a href="tel:${osc.telefone}" class="text-decoration-none">${osc.telefone}</a>` : '-'}
                </td>
                <td><span class="badge bg-secondary">${osc.natureza_juridica || '-'}</span></td>
                <td>
                    <span class="badge ${osc.situacao_cadastral === 'ATIVA' ? 'bg-success' : 'bg-warning'}">
                        ${osc.situacao_cadastral || '-'}
                    </span>
                </td>
                <td><i class="fas fa-map-marker-alt me-1"></i>${osc.edmu_nm_municipio || '-'}</td>
            `;
            tbody.appendChild(row);
        });
    }
    function updatePaginationInfo() {
        const start = totalRecords > 0 ? (currentPage - 1) * 50 + 1 : 0;
        const end = Math.min(currentPage * 50, totalRecords);
        const infoPaginacao = document.getElementById('info-paginacao');
        const paginaAtual = document.getElementById('pagina-atual');
        const btnAnterior = document.getElementById('btn-anterior');
        const btnProximo = document.getElementById('btn-proximo');

        if (infoPaginacao) {
            infoPaginacao.textContent = `Mostrando ${start} a ${end} de ${totalRecords} registros`;
        }

        if (paginaAtual) {
            paginaAtual.textContent = totalPages > 0 ? `Página ${currentPage} de ${totalPages}` : 'Página 0 de 0';
        }

        if (btnAnterior) {
            btnAnterior.disabled = currentPage <= 1;
        }

        if (btnProximo) {
            btnProximo.disabled = currentPage >= totalPages;
        }
    }

    function exportData() {
        const exportBtn = document.getElementById('btn-exportar');
        const originalText = exportBtn.innerHTML;

        // Desabilita o botão e mostra loading
        exportBtn.disabled = true;
        exportBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Exportando...';

        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        fetch(exportDataUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(currentFilters)
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
                <td colspan="8" class="text-center text-muted py-5">
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
        updatePaginationInfo();

        showToast('success', 'Filtros limpos com sucesso!');
    });

    document.getElementById('btn-toggle-mapa').addEventListener('click', toggleMapSection);

    // Enter key support for search
    document.getElementById('palavras_chave').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            loadData(1);
        }
    });

    // Debounced search for better performance
    let searchTimeout;
    document.getElementById('palavras_chave').addEventListener('input', function(e) {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            if (e.target.value.length >= 3 || e.target.value.length === 0) {
                // Auto-search when 3+ characters or empty
                loadData(1);
            }
        }, 500);
    });

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

    console.log('Dashboard inicializado com sucesso!');
});
