// Search functionality for BlakeTimber inventory
document.addEventListener('DOMContentLoaded', function() {
    // Check if Font Awesome loaded, if not show fallback
    setTimeout(function() {
        const searchIcon = document.querySelector('#search-toggle .fas.fa-search');
        const fallbackIcon = document.querySelector('#search-toggle .search-fallback');
        
        if (searchIcon && getComputedStyle(searchIcon, ':before').content === 'none') {
            searchIcon.style.display = 'none';
            fallbackIcon.classList.remove('d-none');
        }
    }, 100);

    const searchToggle = document.getElementById('search-toggle');
    const searchContainer = document.getElementById('search-container');
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');
    let searchTimeout;

    // Toggle search bar visibility
    searchToggle.addEventListener('click', function() {
        const isVisible = searchContainer.style.display !== 'none';
        
        if (isVisible) {
            searchContainer.style.display = 'none';
            searchResults.style.display = 'none';
        } else {
            searchContainer.style.display = 'block';
            searchInput.focus();
        }
    });

    // Hide search when clicking outside
    document.addEventListener('click', function(event) {
        if (!searchContainer.contains(event.target) && 
            !searchToggle.contains(event.target)) {
            searchResults.style.display = 'none';
        }
    });

    // Search functionality with debouncing
    searchInput.addEventListener('input', function() {
        const query = this.value.trim();
        
        // Clear previous timeout
        clearTimeout(searchTimeout);
        
        if (query.length < 2) {
            searchResults.style.display = 'none';
            return;
        }

        // Debounce search requests
        searchTimeout = setTimeout(function() {
            performSearch(query);
        }, 300);
    });

    // Handle keyboard navigation
    searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            searchResults.style.display = 'none';
            searchContainer.style.display = 'none';
        }
    });

    function performSearch(query) {
        // Show loading state
        searchResults.innerHTML = '<div class="search-loading">Searching...</div>';
        searchResults.style.display = 'block';
        
        // Get the search URL from the data attribute
        const searchUrl = document.querySelector('[data-search-url]').dataset.searchUrl;
        
        fetch(`${searchUrl}?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                displaySearchResults(data.products);
            })
            .catch(error => {
                console.error('Search error:', error);
                searchResults.innerHTML = '<div class="p-3 text-danger">Search error occurred</div>';
                searchResults.style.display = 'block';
            });
    }

    function displaySearchResults(products) {
        if (products.length === 0) {
            searchResults.innerHTML = '<div class="p-3 text-muted">No products found</div>';
        } else {
            const searchQuery = searchInput.value.trim();
            const searchTerms = searchQuery.split(/\s+/).filter(term => term.length > 0);
            
            let html = '';
            products.forEach(product => {
                const imageHtml = product.image_url 
                    ? `<img src="${product.image_url}" alt="${product.name}" class="me-3" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;">`
                    : `<div class="me-3 bg-light d-flex align-items-center justify-content-center" style="width: 50px; height: 50px; border-radius: 4px;"><span class="text-muted">📦</span></div>`;
                
                const optionText = product.option ? ` - ${product.option}` : '';
                const noteText = product.note ? ` (${product.note})` : '';
                
                html += `
                    <a href="${product.url}" class="text-decoration-none">
                        <div class="d-flex align-items-center p-3 border-bottom search-result-item">
                            ${imageHtml}
                            <div class="flex-grow-1">
                                <div class="fw-semibold text-dark">${product.name}${optionText}</div>
                                <div class="small text-muted">
                                    I/N: ${product.in_number} • $${product.price}${noteText}
                                </div>
                                <div class="small text-secondary">${product.category}</div>
                            </div>
                        </div>
                    </a>
                `;
            });
            searchResults.innerHTML = html;
        }
        searchResults.style.display = 'block';
    }
});
