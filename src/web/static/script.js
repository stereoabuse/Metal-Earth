// src/web/static/script.js
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search');
    const searchResults = document.getElementById('search-results');
    const bandDisplay = document.getElementById('band-display');
    let debounceTimer;

    function displayBand(band) {
        const bandCard = document.createElement('div');
        bandCard.className = 'band-card searched-band';
        bandCard.innerHTML = `
            <div class="band-header">
                <h3>${band['Band Name']}</h3>
                <span class="origin-name">${band['Search Name']}</span>
            </div>
            
            <div class="band-details">
                <div class="detail-group">
                    <span class="label">Genre</span>
                    <span class="value">${band['Genre'] || 'Unknown'}</span>
                </div>
                
                ${band['Themes'] && band['Themes'] !== 'N/A' ? `
                    <div class="detail-group">
                        <span class="label">Themes</span>
                        <span class="value">${band['Themes']}</span>
                    </div>
                ` : ''}
                
                <div class="detail-group">
                    <span class="label">Country</span>
                    <span class="value">${band['Country'] || 'Unknown'}</span>
                </div>
                
                <div class="detail-group">
                    <span class="label">Formed</span>
                    <span class="value">${band['Formed'] || 'Unknown'}</span>
                </div>
            </div>
            
            <a href="${band['URL']}" 
               target="_blank" 
               class="ma-link"
               rel="noopener noreferrer">
                View on Metal Archives
            </a>
        `;
        
        bandDisplay.innerHTML = '';
        bandDisplay.appendChild(bandCard);
        bandCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    searchInput.addEventListener('input', function() {
        clearTimeout(debounceTimer);
        const query = this.value.trim();

        if (query.length < 2) {
            searchResults.style.display = 'none';
            return;
        }

        debounceTimer = setTimeout(() => {
            fetch(`/search?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    searchResults.innerHTML = '';
                    
                    if (data && data.length > 0) {
                        data.forEach(band => {
                            const div = document.createElement('div');
                            div.className = 'search-result-item';
                            
                            div.innerHTML = `
                                <strong>${band['Band Name']}</strong>
                                <br>
                                <span style="color: var(--text-secondary)">
                                    ${band['Genre'] || 'Unknown Genre'} • ${band['Country'] || 'Unknown Country'}
                                </span>
                            `;
                            
                            div.addEventListener('click', () => {
                                displayBand(band);
                                searchResults.style.display = 'none';
                                searchInput.value = '';
                            });
                            
                            searchResults.appendChild(div);
                        });
                        searchResults.style.display = 'block';
                    } else {
                        const div = document.createElement('div');
                        div.className = 'search-result-item';
                        div.textContent = 'No matching bands found';
                        searchResults.appendChild(div);
                        searchResults.style.display = 'block';
                    }
                })
                .catch(error => {
                    console.error('Search error:', error);
                    searchResults.innerHTML = `
                        <div class="search-result-item">
                            An error occurred while searching
                        </div>
                    `;
                    searchResults.style.display = 'block';
                });
            }, 300);
        });
        
            // Hide search results when clicking outside
            document.addEventListener('click', function(e) {
                if (!searchResults.contains(e.target) && e.target !== searchInput) {
                    searchResults.style.display = 'none';
                }
            });
        
            // Add keyboard navigation for search results
            document.addEventListener('keydown', function(e) {
                if (!searchResults.style.display || searchResults.style.display === 'none') {
                    return;
                }
        
                const items = searchResults.querySelectorAll('.search-result-item');
                const activeItem = searchResults.querySelector('.search-result-item.active');
                
                switch(e.key) {
                    case 'ArrowDown':
                        e.preventDefault();
                        if (!activeItem) {
                            items[0].classList.add('active');
                        } else {
                            const nextItem = activeItem.nextElementSibling;
                            if (nextItem) {
                                activeItem.classList.remove('active');
                                nextItem.classList.add('active');
                            }
                        }
                        break;
                    
                    case 'ArrowUp':
                        e.preventDefault();
                        if (activeItem) {
                            const prevItem = activeItem.previousElementSibling;
                            if (prevItem) {
                                activeItem.classList.remove('active');
                                prevItem.classList.add('active');
                            }
                        }
                        break;
                    
                    case 'Enter':
                        if (activeItem) {
                            activeItem.click();
                        }
                        break;
                    
                    case 'Escape':
                        searchResults.style.display = 'none';
                        searchInput.blur();
                        break;
                }
            });
        });