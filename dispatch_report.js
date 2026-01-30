/**
 * Dispatch Report JavaScript
 * Handles API integration, filtering, pagination, sorting, and export
 */

// API Configuration
const API_BASE_URL = 'http://localhost:8000';
const API_ENDPOINT = `${API_BASE_URL}/reports/dispatched`;

// State Management
let currentState = {
    dateFrom: null,
    dateTo: null,
    filterType: 'dispatch',  // NEW: 'dispatch' or 'manifest'
    search: '',
    limit: 50,
    offset: 0,
    sortBy: 'date_dispatched',
    sortOrder: 'DESC',
    totalCount: 0,
    currentData: []
};

// Debounce timer
let searchDebounceTimer = null;
const DEBOUNCE_DELAY = 500; // ms

// DOM Elements
const elements = {
    // Filters
    dateFrom: document.getElementById('date-from'),
    dateTo: document.getElementById('date-to'),
    filterTypeInputs: document.getElementsByName('filter-type'),  // NEW
    searchInput: document.getElementById('search-input'),
    clearSearchBtn: document.getElementById('clear-search-btn'),
    applyFiltersBtn: document.getElementById('apply-filters-btn'),
    resetFiltersBtn: document.getElementById('reset-filters-btn'),

    // States
    loadingState: document.getElementById('loading-state'),
    errorState: document.getElementById('error-state'),
    emptyState: document.getElementById('empty-state'),
    tableContainer: document.getElementById('table-container'),

    // Table
    tableBody: document.getElementById('dispatch-table-body'),

    // Pagination
    paginationContainer: document.getElementById('pagination-container'),
    paginationInfo: document.getElementById('pagination-info-text'),
    firstPageBtn: document.getElementById('first-page-btn'),
    prevPageBtn: document.getElementById('prev-page-btn'),
    nextPageBtn: document.getElementById('next-page-btn'),
    lastPageBtn: document.getElementById('last-page-btn'),
    pageNumbers: document.getElementById('page-numbers'),
    pageSize: document.getElementById('page-size'),

    // Results
    resultsCount: document.getElementById('results-count'),
    resultsSummary: document.getElementById('results-summary'),  // NEW
    resultsSummaryText: document.getElementById('results-summary-text'),  // NEW

    // Export
    exportExcelBtn: document.getElementById('export-excel-btn'),
    exportPdfBtn: document.getElementById('export-pdf-btn'),

    // Navigation
    backBtn: document.getElementById('back-btn'),
    outstandingBtn: document.getElementById('outstanding-btn'),

    // Error
    errorMessage: document.getElementById('error-message'),
    retryBtn: document.getElementById('retry-btn')
};

/**
 * Initialize the application
 */
function init() {
    setupEventListeners();
    loadInitialData();
}

/**
 * Setup all event listeners
 */
function setupEventListeners() {
    // Filter controls
    elements.applyFiltersBtn.addEventListener('click', applyFilters);
    elements.resetFiltersBtn.addEventListener('click', resetFilters);

    // Filter type toggle
    elements.filterTypeInputs.forEach(input => {
        input.addEventListener('change', handleFilterTypeChange);
    });

    // Search with debouncing
    elements.searchInput.addEventListener('input', handleSearchInput);
    elements.clearSearchBtn.addEventListener('click', clearSearch);

    // Pagination
    elements.firstPageBtn.addEventListener('click', () => goToPage(0));
    elements.prevPageBtn.addEventListener('click', goToPreviousPage);
    elements.nextPageBtn.addEventListener('click', goToNextPage);
    elements.lastPageBtn.addEventListener('click', goToLastPage);
    elements.pageSize.addEventListener('change', handlePageSizeChange);

    // Table sorting
    document.querySelectorAll('th[data-sort]').forEach(th => {
        th.addEventListener('click', () => handleSort(th.dataset.sort));
    });

    // Navigation
    elements.backBtn.addEventListener('click', () => window.history.back());
    elements.outstandingBtn.addEventListener('click', () => window.location.href = 'outstanding_orders.html');

    // Retry button
    elements.retryBtn.addEventListener('click', loadData);

    // Export buttons (placeholders - show message)
    elements.exportExcelBtn.addEventListener('click', showExportPlaceholder);
    elements.exportPdfBtn.addEventListener('click', showExportPlaceholder);
}

/**
 * Handle search input with debouncing
 */
function handleSearchInput(e) {
    const value = e.target.value.trim();

    // Show/hide clear button
    if (value) {
        elements.clearSearchBtn.classList.remove('hidden');
    } else {
        elements.clearSearchBtn.classList.add('hidden');
    }

    // Clear existing timer
    if (searchDebounceTimer) {
        clearTimeout(searchDebounceTimer);
    }

    // Set new timer - only trigger search after user stops typing
    searchDebounceTimer = setTimeout(() => {
        currentState.search = value;
        currentState.offset = 0; // Reset to first page
        loadData();
    }, DEBOUNCE_DELAY);
}

/**
 * Clear search input
 */
function clearSearch() {
    elements.searchInput.value = '';
    elements.clearSearchBtn.classList.add('hidden');
    currentState.search = '';
    currentState.offset = 0;
    loadData();
}
/**
 * Handle filter type change (dispatch vs manifest)
 */
function handleFilterTypeChange(e) {
    currentState.filterType = e.target.value;
    currentState.offset = 0; // Reset to first page

    // Update date labels to reflect filter type
    updateDateLabels();

    loadData();
}

/**
 * Update date input labels based on filter type
 */
function updateDateLabels() {
    const fromLabel = document.querySelector('label[for="date-from"]');
    const toLabel = document.querySelector('label[for="date-to"]');

    if (currentState.filterType === 'dispatch') {
        fromLabel.textContent = 'Dispatch Date From';
        toLabel.textContent = 'Dispatch Date To';
    } else {
        fromLabel.textContent = 'Manifest Date From';
        toLabel.textContent = 'Manifest Date To';
    }
}


/**
 * Apply filters
 */
function applyFilters() {
    // Get raw values from inputs
    const rawDateFrom = elements.dateFrom.value;
    const rawDateTo = elements.dateTo.value;

    // Sanitize: only set if non-empty and valid YYYY-MM-DD format
    // HTML5 date inputs return YYYY-MM-DD or empty string
    currentState.dateFrom = (rawDateFrom && rawDateFrom.trim() !== '') ? rawDateFrom.trim() : null;
    currentState.dateTo = (rawDateTo && rawDateTo.trim() !== '') ? rawDateTo.trim() : null;

    // Validate date format (YYYY-MM-DD)
    const datePattern = /^\d{4}-\d{2}-\d{2}$/;
    if (currentState.dateFrom && !datePattern.test(currentState.dateFrom)) {
        console.warn('Invalid date_from format:', currentState.dateFrom);
        currentState.dateFrom = null;
    }
    if (currentState.dateTo && !datePattern.test(currentState.dateTo)) {
        console.warn('Invalid date_to format:', currentState.dateTo);
        currentState.dateTo = null;
    }

    console.log('Apply Filters - Sanitized dates:', {
        dateFrom: currentState.dateFrom,
        dateTo: currentState.dateTo
    });

    currentState.offset = 0; // Reset to first page
    loadData();
}

/**
 * Reset all filters
 */
function resetFilters() {
    elements.dateFrom.value = '';
    elements.dateTo.value = '';
    elements.searchInput.value = '';
    elements.clearSearchBtn.classList.add('hidden');

    currentState.dateFrom = null;
    currentState.dateTo = null;
    currentState.search = '';
    currentState.offset = 0;
    currentState.sortBy = 'date_dispatched';
    currentState.sortOrder = 'DESC';

    // Reset sort indicators
    document.querySelectorAll('th.sort-asc, th.sort-desc').forEach(th => {
        th.classList.remove('sort-asc', 'sort-desc');
    });

    loadData();
}

/**
 * Handle table column sorting
 */
function handleSort(sortBy) {
    // Toggle sort order if clicking same column
    if (currentState.sortBy === sortBy) {
        currentState.sortOrder = currentState.sortOrder === 'ASC' ? 'DESC' : 'ASC';
    } else {
        currentState.sortBy = sortBy;
        currentState.sortOrder = 'DESC';
    }

    currentState.offset = 0; // Reset to first page
    updateSortIndicators();
    loadData();
}

/**
 * Update sort indicators in table headers
 */
function updateSortIndicators() {
    document.querySelectorAll('th[data-sort]').forEach(th => {
        th.classList.remove('sort-asc', 'sort-desc');
        if (th.dataset.sort === currentState.sortBy) {
            th.classList.add(currentState.sortOrder === 'ASC' ? 'sort-asc' : 'sort-desc');
        }
    });
}

/**
 * Handle page size change
 */
function handlePageSizeChange(e) {
    currentState.limit = parseInt(e.target.value);
    currentState.offset = 0; // Reset to first page
    loadData();
}

/**
 * Go to specific page
 */
function goToPage(pageIndex) {
    currentState.offset = pageIndex * currentState.limit;
    loadData();
}

/**
 * Go to previous page
 */
function goToPreviousPage() {
    if (currentState.offset > 0) {
        currentState.offset = Math.max(0, currentState.offset - currentState.limit);
        loadData();
    }
}

/**
 * Go to next page
 */
function goToNextPage() {
    if (currentState.offset + currentState.limit < currentState.totalCount) {
        currentState.offset += currentState.limit;
        loadData();
    }
}

/**
 * Go to last page
 */
function goToLastPage() {
    const lastPageOffset = Math.floor((currentState.totalCount - 1) / currentState.limit) * currentState.limit;
    currentState.offset = lastPageOffset;
    loadData();
}

/**
 * Load initial data
 */
function loadInitialData() {
    loadData();
}

/**
 * Load data from API
 */
async function loadData() {
    showLoadingState();

    try {
        const params = new URLSearchParams();

        // LOG 1: Current state before building params
        console.log('=== LOAD DATA DEBUG ===');
        console.log('1. Current State:', {
            dateFrom: currentState.dateFrom,
            dateTo: currentState.dateTo,
            filterType: currentState.filterType,
            search: currentState.search,
            limit: currentState.limit,
            offset: currentState.offset
        });

        if (currentState.dateFrom) params.append('date_from', currentState.dateFrom);
        if (currentState.dateTo) params.append('date_to', currentState.dateTo);
        if (currentState.search) params.append('search', currentState.search);
        params.append('filter_type', currentState.filterType);  // NEW
        params.append('limit', currentState.limit);
        params.append('offset', currentState.offset);
        params.append('sort_by', currentState.sortBy);
        params.append('sort_order', currentState.sortOrder);

        const url = `${API_ENDPOINT}?${params.toString()}`;

        // LOG 2: Full API request URL
        console.log('2. API Request URL:', url);
        console.log('3. Query Parameters:', Object.fromEntries(params));

        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();

        // LOG 3: API Response
        console.log('4. API Response:', {
            invoices_count: data.invoices ? data.invoices.length : 0,
            total: data.total,
            page: data.page,
            limit: data.limit,
            filter_type_echo: data.filter_type,
            first_invoice: data.invoices && data.invoices.length > 0 ? data.invoices[0] : null
        });

        // Validate response data before storing
        if (!data.invoices || !Array.isArray(data.invoices)) {
            console.error('Invalid API response: invoices is not an array', data);
            throw new Error('Invalid API response format');
        }

        // Store data in state - CRITICAL: Don't clear before validation
        currentState.currentData = data.invoices;
        currentState.totalCount = data.total || 0;

        // LOG 4: State after update
        console.log('5. Updated State:', {
            currentData_length: currentState.currentData.length,
            totalCount: currentState.totalCount
        });

        // LOG 5: Pre-render validation
        console.log('6. Pre-render check:', {
            will_render_rows: currentState.currentData.length,
            sample_invoice: currentState.currentData[0] || null
        });

        // Render data
        renderTable(currentState.currentData);
        updatePagination();
        updateResultsCount();
        updateResultsSummary();

        // Show appropriate state
        if (currentState.currentData.length === 0) {
            console.log('7. Showing EMPTY state (no invoices)');
            showEmptyState();
        } else {
            console.log('7. Showing TABLE state (' + currentState.currentData.length + ' invoices)');
            showTableState();
        }

        console.log('=== END DEBUG ===\n');

    } catch (error) {
        console.error('Error loading data:', error);
        showErrorState(error.message);
    }
}

/**
 * Render table rows - INVOICE-LEVEL, not grouped
 */
function renderTable(invoices) {
    elements.tableBody.innerHTML = '';

    invoices.forEach(invoice => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${escapeHtml(invoice.invoice_number || 'N/A')}</td>
            <td>${escapeHtml(invoice.order_number || 'N/A')}</td>
            <td>${escapeHtml(invoice.manifest_number || 'N/A')}</td>
            <td>${escapeHtml(invoice.customer_name || 'N/A')}</td>
            <td>${formatDate(invoice.invoice_date)}</td>
            <td>${formatDate(invoice.date_dispatched)}</td>
            <td>${escapeHtml(invoice.driver || 'N/A')}</td>
            <td>${escapeHtml(invoice.assistant || 'N/A')}</td>
            <td>${escapeHtml(invoice.reg_number || 'N/A')}</td>
            <td>${escapeHtml(invoice.checker || 'N/A')}</td>
        `;
        elements.tableBody.appendChild(row);
    });
}

/**
 * Update pagination controls
 */
function updatePagination() {
    const currentPage = Math.floor(currentState.offset / currentState.limit);
    const totalPages = Math.ceil(currentState.totalCount / currentState.limit);

    // Update pagination info
    const start = currentState.totalCount === 0 ? 0 : currentState.offset + 1;
    const end = Math.min(currentState.offset + currentState.limit, currentState.totalCount);
    elements.paginationInfo.textContent = `Showing ${start}-${end} of ${currentState.totalCount}`;

    // Update button states
    elements.firstPageBtn.disabled = currentPage === 0;
    elements.prevPageBtn.disabled = currentPage === 0;
    elements.nextPageBtn.disabled = currentPage >= totalPages - 1;
    elements.lastPageBtn.disabled = currentPage >= totalPages - 1;

    // Render page numbers
    renderPageNumbers(currentPage, totalPages);
}

/**
 * Render page number buttons
 */
function renderPageNumbers(currentPage, totalPages) {
    elements.pageNumbers.innerHTML = '';

    if (totalPages <= 1) return;

    const maxVisible = 5;
    let startPage = Math.max(0, currentPage - Math.floor(maxVisible / 2));
    let endPage = Math.min(totalPages - 1, startPage + maxVisible - 1);

    // Adjust start if we're near the end
    if (endPage - startPage < maxVisible - 1) {
        startPage = Math.max(0, endPage - maxVisible + 1);
    }

    // First page
    if (startPage > 0) {
        addPageButton(0, currentPage);
        if (startPage > 1) {
            addEllipsis();
        }
    }

    // Visible pages
    for (let i = startPage; i <= endPage; i++) {
        addPageButton(i, currentPage);
    }

    // Last page
    if (endPage < totalPages - 1) {
        if (endPage < totalPages - 2) {
            addEllipsis();
        }
        addPageButton(totalPages - 1, currentPage);
    }
}

/**
 * Add page button
 */
function addPageButton(pageIndex, currentPage) {
    const btn = document.createElement('button');
    btn.className = 'page-btn' + (pageIndex === currentPage ? ' active' : '');
    btn.textContent = pageIndex + 1;
    btn.addEventListener('click', () => goToPage(pageIndex));
    elements.pageNumbers.appendChild(btn);
}

/**
 * Add ellipsis
 */
function addEllipsis() {
    const span = document.createElement('span');
    span.className = 'page-btn ellipsis';
    span.textContent = '...';
    elements.pageNumbers.appendChild(span);
}

/**
 * Update results summary text
 */
function updateResultsSummary() {
    if (currentState.totalCount === 0) {
        elements.resultsSummary.classList.add('hidden');
        return;
    }

    const start = currentState.offset + 1;
    const end = Math.min(currentState.offset + currentState.limit, currentState.totalCount);

    let dateRangeText = '';
    if (currentState.dateFrom && currentState.dateTo) {
        const fromDate = formatDate(currentState.dateFrom);
        const toDate = formatDate(currentState.dateTo);
        const filterTypeText = currentState.filterType === 'dispatch' ? 'dispatched' : 'added to manifests';
        dateRangeText = ` ${filterTypeText} between <strong>${fromDate}</strong> and <strong>${toDate}</strong>`;
    } else if (currentState.dateFrom) {
        const fromDate = formatDate(currentState.dateFrom);
        const filterTypeText = currentState.filterType === 'dispatch' ? 'dispatched' : 'added to manifests';
        dateRangeText = ` ${filterTypeText} on or after <strong>${fromDate}</strong>`;
    } else if (currentState.dateTo) {
        const toDate = formatDate(currentState.dateTo);
        const filterTypeText = currentState.filterType === 'dispatch' ? 'dispatched' : 'added to manifests';
        dateRangeText = ` ${filterTypeText} on or before <strong>${toDate}</strong>`;
    }

    elements.resultsSummaryText.innerHTML = `
        Showing <strong>${start}-${end}</strong> of <strong>${currentState.totalCount}</strong> invoices${dateRangeText}
    `;

    elements.resultsSummary.classList.remove('hidden');
}

/**
 * Update results count
 */
function updateResultsCount() {
    elements.resultsCount.textContent = `${currentState.totalCount} invoice${currentState.totalCount !== 1 ? 's' : ''} found`;
}

/**
 * Show loading state
 */
function showLoadingState() {
    elements.loadingState.classList.remove('hidden');
    elements.errorState.classList.add('hidden');
    elements.emptyState.classList.add('hidden');
    elements.tableContainer.classList.add('hidden');
    elements.paginationContainer.classList.add('hidden');

    // Disable interactive elements during loading
    elements.applyFiltersBtn.disabled = true;
    elements.resetFiltersBtn.disabled = true;
}

/**
 * Show error state
 */
function showErrorState(message) {
    elements.loadingState.classList.add('hidden');
    elements.errorState.classList.remove('hidden');
    elements.emptyState.classList.add('hidden');
    elements.tableContainer.classList.add('hidden');
    elements.paginationContainer.classList.add('hidden');

    elements.errorMessage.textContent = message || 'Failed to load dispatch records. Please check your connection and try again.';

    // Re-enable interactive elements
    elements.applyFiltersBtn.disabled = false;
    elements.resetFiltersBtn.disabled = false;
}

/**
 * Show empty state
 */
function showEmptyState() {
    elements.loadingState.classList.add('hidden');
    elements.errorState.classList.add('hidden');
    elements.emptyState.classList.remove('hidden');
    elements.tableContainer.classList.add('hidden');
    elements.paginationContainer.classList.add('hidden');

    // Re-enable interactive elements
    elements.applyFiltersBtn.disabled = false;
    elements.resetFiltersBtn.disabled = false;
}

/**
 * Show table state
 */
function showTableState() {
    elements.loadingState.classList.add('hidden');
    elements.errorState.classList.add('hidden');
    elements.emptyState.classList.add('hidden');
    elements.tableContainer.classList.remove('hidden');
    elements.paginationContainer.classList.remove('hidden');

    // Re-enable interactive elements
    elements.applyFiltersBtn.disabled = false;
    elements.resetFiltersBtn.disabled = false;
}

/**
 * Show export placeholder message
 */
function showExportPlaceholder() {
    alert('Export functionality is not yet implemented. This is a placeholder button.');
}

/**
 * Format date for display
 */
function formatDate(dateString) {
    if (!dateString || dateString === 'N/A') return 'N/A';
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
    } catch {
        return dateString;
    }
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    if (text === null || text === undefined) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
