/**
 * Modern Table - Substituição nativa do DataTables
 * Implementa funcionalidades de tabela usando JavaScript vanilla moderno
 */

class ModernTable {
    constructor(tableId, options = {}) {
        this.table = document.getElementById(tableId);
        this.tbody = this.table.querySelector('tbody');
        this.thead = this.table.querySelector('thead');
        
        this.options = {
            sortable: true,
            searchable: true,
            pagination: true,
            pageSize: 50,
            ...options
        };
        
        this.data = [];
        this.filteredData = [];
        this.currentPage = 1;
        this.sortColumn = null;
        this.sortDirection = 'asc';
        this.searchTerm = '';
        
        this.init();
    }
    
    init() {
        if (this.options.sortable) {
            this.initSorting();
        }
        
        if (this.options.searchable) {
            this.initSearch();
        }
        
        if (this.options.pagination) {
            this.initPagination();
        }
    }
    
    initSorting() {
        const headers = this.thead.querySelectorAll('th[data-sortable]');
        headers.forEach((header, index) => {
            header.style.cursor = 'pointer';
            header.classList.add('sortable-header');
            
            // Adicionar ícone de ordenação
            const sortIcon = document.createElement('i');
            sortIcon.className = 'fas fa-sort ms-2 sort-icon';
            header.appendChild(sortIcon);
            
            header.addEventListener('click', () => {
                this.sort(index, header.dataset.sortable);
            });
        });
    }
    
    initSearch() {
        // Busca será implementada externamente via método search()
    }
    
    initPagination() {
        // Paginação será implementada externamente via métodos de página
    }
    
    setData(data) {
        this.data = [...data];
        this.filteredData = [...data];
        this.render();
    }
    
    search(term) {
        this.searchTerm = term.toLowerCase();
        
        if (!term) {
            this.filteredData = [...this.data];
        } else {
            this.filteredData = this.data.filter(row => {
                return Object.values(row).some(value => 
                    String(value).toLowerCase().includes(this.searchTerm)
                );
            });
        }
        
        this.currentPage = 1;
        this.render();
    }
    
    sort(columnIndex, columnKey) {
        // Atualizar direção da ordenação
        if (this.sortColumn === columnIndex) {
            this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            this.sortDirection = 'asc';
        }
        
        this.sortColumn = columnIndex;
        
        // Atualizar ícones visuais
        this.updateSortIcons();
        
        // Ordenar dados
        this.filteredData.sort((a, b) => {
            let aVal = a[columnKey] || '';
            let bVal = b[columnKey] || '';
            
            // Converter para string para comparação
            aVal = String(aVal).toLowerCase();
            bVal = String(bVal).toLowerCase();
            
            if (aVal < bVal) return this.sortDirection === 'asc' ? -1 : 1;
            if (aVal > bVal) return this.sortDirection === 'asc' ? 1 : -1;
            return 0;
        });
        
        this.render();
    }
    
    updateSortIcons() {
        // Resetar todos os ícones
        const icons = this.thead.querySelectorAll('.sort-icon');
        icons.forEach(icon => {
            icon.className = 'fas fa-sort ms-2 sort-icon';
        });
        
        // Atualizar ícone da coluna atual
        if (this.sortColumn !== null) {
            const currentIcon = icons[this.sortColumn];
            if (currentIcon) {
                currentIcon.className = `fas fa-sort-${this.sortDirection === 'asc' ? 'up' : 'down'} ms-2 sort-icon`;
            }
        }
    }
    
    goToPage(page) {
        const totalPages = Math.ceil(this.filteredData.length / this.options.pageSize);
        
        if (page < 1) page = 1;
        if (page > totalPages) page = totalPages;
        
        this.currentPage = page;
        this.render();
    }
    
    nextPage() {
        this.goToPage(this.currentPage + 1);
    }
    
    prevPage() {
        this.goToPage(this.currentPage - 1);
    }
    
    render() {
        // Calcular dados da página atual
        const startIndex = (this.currentPage - 1) * this.options.pageSize;
        const endIndex = startIndex + this.options.pageSize;
        const pageData = this.filteredData.slice(startIndex, endIndex);
        
        // Limpar tbody
        this.tbody.innerHTML = '';
        
        if (pageData.length === 0) {
            this.renderEmptyState();
            return;
        }
        
        // Renderizar dados usando DocumentFragment para performance
        const fragment = document.createDocumentFragment();
        
        pageData.forEach(row => {
            const tr = this.createRow(row);
            fragment.appendChild(tr);
        });
        
        this.tbody.appendChild(fragment);
        
        // Atualizar informações de paginação
        this.updatePaginationInfo();
    }
    
    createRow(data) {
        // Esta função deve ser sobrescrita pela implementação específica
        const tr = document.createElement('tr');
        Object.values(data).forEach(value => {
            const td = document.createElement('td');
            td.textContent = value || '-';
            tr.appendChild(td);
        });
        return tr;
    }
    
    renderEmptyState() {
        const colCount = this.thead.querySelectorAll('th').length;
        this.tbody.innerHTML = `
            <tr>
                <td colspan="${colCount}" class="text-center text-muted py-5">
                    <i class="fas fa-search fa-2x mb-3 d-block"></i>
                    <h6>Nenhum resultado encontrado</h6>
                    <p class="mb-0">Tente ajustar os filtros de pesquisa</p>
                </td>
            </tr>
        `;
    }
    
    updatePaginationInfo() {
        const totalRecords = this.filteredData.length;
        const totalPages = Math.ceil(totalRecords / this.options.pageSize);
        const start = totalRecords > 0 ? (this.currentPage - 1) * this.options.pageSize + 1 : 0;
        const end = Math.min(this.currentPage * this.options.pageSize, totalRecords);
        
        // Disparar evento customizado com informações de paginação
        const event = new CustomEvent('tableUpdated', {
            detail: {
                totalRecords,
                totalPages,
                currentPage: this.currentPage,
                start,
                end,
                pageSize: this.options.pageSize
            }
        });
        
        this.table.dispatchEvent(event);
    }
    
    // Métodos utilitários
    getFilteredData() {
        return this.filteredData;
    }
    
    getTotalRecords() {
        return this.filteredData.length;
    }
    
    getCurrentPage() {
        return this.currentPage;
    }
    
    getTotalPages() {
        return Math.ceil(this.filteredData.length / this.options.pageSize);
    }
}

// Exportar para uso global
window.ModernTable = ModernTable;
