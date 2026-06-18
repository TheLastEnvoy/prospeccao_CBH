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
        tr.className = 'osc-row';
        
        // Função para escapar HTML
        const escapeHtml = (text) => {
            if (!text) return '-';
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        };

        const formatValue = (value, fallback = '-') => value ? escapeHtml(value) : fallback;
        const situacaoAtiva = osc.situacao_cadastral === 'ATIVA';
        
        // Criar células com conteúdo específico para OSCs
        const cells = [
            {
                content: `<span class="osc-id-badge">${escapeHtml(osc.id_osc)}</span>`,
                className: 'text-center'
            },
            {
                content: `
                    <div class="osc-name-cell">
                        <span class="osc-name">${formatValue(osc.nome)}</span>
                        <span class="osc-subline">
                            <i class="fas fa-location-dot"></i>${formatValue(osc.edmu_nm_municipio)}
                        </span>
                    </div>
                `,
                className: '',
                style: 'min-width: 240px; max-width: 300px;',
                title: osc.nome || ''
            },
            {
                content: osc.email ? 
                    `
                    <div class="osc-contact-cell">
                        <a href="mailto:${escapeHtml(osc.email)}" class="text-decoration-none osc-contact-link">${escapeHtml(osc.email)}</a>
                        <span class="osc-subline"><i class="fas fa-envelope-open-text"></i>contato principal</span>
                    </div>
                    ` : 
                    '<span class="osc-muted">Sem e-mail informado</span>',
                className: '',
                style: 'min-width: 180px; max-width: 240px;',
                title: osc.email || ''
            },
            {
                content: osc.endereco
                    ? `
                    <div class="osc-location-cell">
                        <span class="osc-address">${escapeHtml(osc.endereco)}</span>
                        <span class="osc-subline"><i class="fas fa-route"></i>endereço cadastrado</span>
                    </div>
                    `
                    : '<span class="osc-muted">Sem endereço informado</span>',
                className: '',
                style: 'min-width: 220px; max-width: 300px;',
                title: osc.endereco || ''
            },
            {
                content: osc.telefone ? 
                    `
                    <div class="osc-contact-cell">
                        <a href="tel:${escapeHtml(osc.telefone)}" class="text-decoration-none osc-contact-link">${escapeHtml(osc.telefone)}</a>
                        <span class="osc-subline"><i class="fas fa-phone-volume"></i>canal telefônico</span>
                    </div>
                    ` : 
                    '<span class="osc-muted">Sem telefone informado</span>',
                className: '',
                style: 'min-width: 150px; max-width: 180px;',
                title: osc.telefone || ''
            },
            {
                content: `<span class="osc-chip osc-chip--neutral">${formatValue(osc.natureza_juridica)}</span>`,
                className: '',
                style: 'min-width: 180px; max-width: 220px;',
                title: osc.natureza_juridica || ''
            },
            {
                content: `<span class="osc-chip ${situacaoAtiva ? 'osc-chip--success' : 'osc-chip--warning'}">${formatValue(osc.situacao_cadastral)}</span>`,
                className: '',
                style: 'min-width: 135px; max-width: 160px;',
                title: osc.situacao_cadastral || ''
            },
            {
                content: `
                    <div class="osc-location-cell">
                        <span class="osc-name">${formatValue(osc.edmu_nm_municipio)}</span>
                        <span class="osc-subline"><i class="fas fa-map"></i>território da organização</span>
                    </div>
                `,
                className: '',
                style: 'min-width: 170px; max-width: 200px;',
                title: osc.edmu_nm_municipio || ''
            },
            {
                content: osc.cbh && osc.cbh !== '-'
                    ? `<span class="osc-chip osc-chip--info osc-cbh">${escapeHtml(osc.cbh)}</span>`
                    : '<span class="osc-muted">Sem vinculação</span>',
                className: '',
                style: 'min-width: 190px; max-width: 240px;',
                title: osc.cbh || ''
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
