/**
 * OSC Table - Implementação específica da tabela de OSCs
 * Estende ModernTable com funcionalidades específicas para OSCs
 */

class OSCTable extends ModernTable {
    constructor(tableId, options = {}) {
        super(tableId, {
            sortable: true,
            searchable: true,
            pagination: true,
            pageSize: 50,
            ...options
        });
        
        this.initEventListeners();
    }
    
    initEventListeners() {
        // Escutar eventos de atualização da tabela
        this.table.addEventListener('tableUpdated', (event) => {
            this.updatePaginationControls(event.detail);
        });
    }
    
    createRow(osc) {
        const tr = document.createElement('tr');
        
        // Função para escapar HTML
        const escapeHtml = (text) => {
            if (!text) return '-';
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        };
        
        // Criar células com conteúdo específico para OSCs
        const cells = [
            {
                content: `<span class="badge bg-primary">${escapeHtml(osc.id_osc)}</span>`,
                className: ''
            },
            {
                content: `<span class="fw-semibold">${escapeHtml(osc.nome)}</span>`,
                className: 'text-truncate',
                style: 'max-width: 200px;',
                title: osc.nome || ''
            },
            {
                content: osc.email ? 
                    `<a href="mailto:${escapeHtml(osc.email)}" class="text-decoration-none">${escapeHtml(osc.email)}</a>` : 
                    '-',
                className: 'text-truncate',
                style: 'max-width: 150px;',
                title: osc.email || ''
            },
            {
                content: escapeHtml(osc.endereco),
                className: 'text-truncate',
                style: 'max-width: 200px;',
                title: osc.endereco || ''
            },
            {
                content: osc.telefone ? 
                    `<a href="tel:${escapeHtml(osc.telefone)}" class="text-decoration-none">${escapeHtml(osc.telefone)}</a>` : 
                    '-',
                className: 'text-truncate',
                style: 'max-width: 120px;',
                title: osc.telefone || ''
            },
            {
                content: `<span class="badge bg-secondary">${escapeHtml(osc.natureza_juridica)}</span>`,
                className: 'text-truncate',
                style: 'max-width: 150px;',
                title: osc.natureza_juridica || ''
            },
            {
                content: `<span class="badge ${osc.situacao_cadastral === 'ATIVA' ? 'bg-success' : 'bg-warning'}">${escapeHtml(osc.situacao_cadastral)}</span>`,
                className: 'text-truncate',
                style: 'max-width: 120px;',
                title: osc.situacao_cadastral || ''
            },
            {
                content: `<i class="fas fa-map-marker-alt me-1"></i>${escapeHtml(osc.edmu_nm_municipio)}`,
                className: 'text-truncate',
                style: 'max-width: 150px;',
                title: osc.edmu_nm_municipio || ''
            }
        ];
        
        cells.forEach(cellData => {
            const td = document.createElement('td');
            td.innerHTML = cellData.content;
            
            if (cellData.className) {
                td.className = cellData.className;
            }
            
            if (cellData.style) {
                td.style.cssText = cellData.style;
            }
            
            if (cellData.title) {
                td.title = cellData.title;
            }
            
            tr.appendChild(td);
        });
        
        // Adicionar efeitos de hover
        tr.addEventListener('mouseenter', () => {
            tr.style.backgroundColor = 'rgba(52, 152, 219, 0.1)';
        });
        
        tr.addEventListener('mouseleave', () => {
            tr.style.backgroundColor = '';
        });
        
        return tr;
    }
    
    updatePaginationControls(paginationInfo) {
        const {
            totalRecords,
            totalPages,
            currentPage,
            start,
            end,
            pageSize
        } = paginationInfo;
        
        // Atualizar informações de paginação
        const infoPaginacao = document.getElementById('info-paginacao');
        if (infoPaginacao) {
            infoPaginacao.textContent = `Mostrando ${start} a ${end} de ${totalRecords} registros`;
        }
        
        const paginaAtual = document.getElementById('pagina-atual');
        if (paginaAtual) {
            paginaAtual.textContent = `Página ${currentPage} de ${totalPages}`;
        }
        
        // Atualizar botões de navegação
        const btnAnterior = document.getElementById('btn-anterior');
        const btnProximo = document.getElementById('btn-proximo');
        
        if (btnAnterior) {
            btnAnterior.disabled = currentPage <= 1;
        }
        
        if (btnProximo) {
            btnProximo.disabled = currentPage >= totalPages;
        }
        
        // Atualizar estatísticas
        this.updateStats(totalRecords);
    }
    
    updateStats(filtered = 0) {
        const statsFiltered = document.getElementById('stats-filtered');
        const totalOscs = document.getElementById('total-oscs');
        
        if (statsFiltered) {
            statsFiltered.textContent = filtered;
        }
        
        if (totalOscs) {
            totalOscs.textContent = filtered;
        }
    }
    
    // Método para filtrar dados externamente (mantém compatibilidade)
    filterData(data) {
        this.setData(data);
    }
    
    // Método para obter página atual (mantém compatibilidade)
    getCurrentPageData() {
        const startIndex = (this.currentPage - 1) * this.options.pageSize;
        const endIndex = startIndex + this.options.pageSize;
        return this.filteredData.slice(startIndex, endIndex);
    }
    
    // Método para exportar dados filtrados
    getExportData() {
        return this.filteredData;
    }
}

// Função utilitária para copiar texto para clipboard
function copyToClipboard(text, successMessage = 'Copiado!') {
    if (navigator.clipboard && window.isSecureContext) {
        // Usar API moderna do clipboard
        navigator.clipboard.writeText(text).then(() => {
            showToast('success', successMessage);
        }).catch(err => {
            console.error('Erro ao copiar:', err);
            fallbackCopyToClipboard(text, successMessage);
        });
    } else {
        // Fallback para navegadores mais antigos
        fallbackCopyToClipboard(text, successMessage);
    }
}

function fallbackCopyToClipboard(text, successMessage) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showToast('success', successMessage);
    } catch (err) {
        console.error('Erro ao copiar:', err);
        showToast('error', 'Erro ao copiar texto');
    }
    
    document.body.removeChild(textArea);
}

// Função para mostrar toast (deve existir no dashboard.js)
function showToast(type, message) {
    const toastElement = document.getElementById(`toast-${type}`);
    const messageElement = document.getElementById(`toast-${type}-message`);

    if (toastElement && messageElement) {
        messageElement.textContent = message;
        const toast = new bootstrap.Toast(toastElement);
        toast.show();
    }
}

// Exportar para uso global
window.OSCTable = OSCTable;
window.copyToClipboard = copyToClipboard;
