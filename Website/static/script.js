document.addEventListener('DOMContentLoaded', function() {
    const exploreButton = document.getElementById('explore-button');
    const favouritesButton = document.querySelector('a[href="favourites.html"]');
    const settingsButton = document.querySelector('a[href="settings.html"]');
    const profileButton = document.querySelector('a[href="profile.html"]');
    const uploadInput = document.getElementById('upload');
    const profilePicture = document.getElementById('profile-picture');
    const cropperModal = document.getElementById('cropperModal');
    const cropperImage = document.getElementById('cropper-image');
    const cropButton = document.getElementById('crop-button');
    const closeModal = document.querySelector('.close');
    const deleteButton = document.getElementById('delete-btn');
    const defaultIcon = document.getElementById('default-icon');
    let cropper;

    const hamburgerMenu = document.getElementById('hamburger-menu');
    const sidePanel = document.getElementById('side-panel');
    const contentSections = document.querySelectorAll('.content');
    const chartGrid = document.querySelector('.chart-grid');
    const pageTitle = document.querySelector('.page-title');

    function toggleSidePanel() {
        if (sidePanel) {
            sidePanel.classList.toggle('show');
            contentSections.forEach(section => {
                section.classList.toggle('shifted');
            });
            if (chartGrid) {
                chartGrid.classList.toggle('shifted');
            }
            if (pageTitle) {
                pageTitle.classList.toggle('shifted');
            }
        }
    }

    if (hamburgerMenu) {
        hamburgerMenu.addEventListener('click', toggleSidePanel);
    }
    
    function navigateWithTransition(url) {
        document.body.classList.add('fade-out');
        setTimeout(() => {
            window.location.href = url;
        }, 500); // Match the duration of the CSS transition
    }

    function toggleDefaultIcon() {
        if (profilePicture && profilePicture.src && profilePicture.src !== window.location.href) {
            if (defaultIcon) {
                defaultIcon.classList.add('hidden');
            }
            if (profilePicture) {
                profilePicture.style.display = 'block';
            }
        } else {
            if (defaultIcon) {
                defaultIcon.classList.remove('hidden');
            }
            if (profilePicture) {
                profilePicture.style.display = 'none';
            }
        }
    }
    // Initial check
    toggleDefaultIcon();

    if (uploadInput) {
        uploadInput.addEventListener('change', function(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    profilePicture.src = e.target.result;
                    toggleDefaultIcon();
                    cropperImage.src = e.target.result;
                    cropperModal.style.display = 'block';
                    cropper = new Cropper(cropperImage, {
                        aspectRatio: 1,
                        viewMode: 1,
                    });
                };
                reader.readAsDataURL(file);
            }
        });
    }

    if (cropButton) {
        cropButton.addEventListener('click', function() {
            if (cropper) {
                const canvas = cropper.getCroppedCanvas({
                    width: 150,
                    height: 150,
                });
                profilePicture.src = canvas.toDataURL();
                profilePicture.style.display = 'block';
                defaultIcon.style.display = 'none';
                cropperModal.style.display = 'none';
                cropper.destroy();
                toggleDefaultIcon();
            } else {
                console.error('Cropper is not initialized');
            }
        });
    }

    if (closeModal) {
        closeModal.addEventListener('click', function() {
            if (cropper) {
                cropperModal.style.display = 'none';
                cropper.destroy();
                cropper = null; // Reset cropper
            }
        });
    }

    window.addEventListener('click', function(event) {
        if (event.target == cropperModal) {
            if (cropper) {
                cropperModal.style.display = 'none';
                cropper.destroy();
                cropper = null; // Reset cropper
            }
        }
    });

    if (deleteButton) {
        deleteButton.addEventListener('click', function() {
            profilePicture.src = '';
            profilePicture.style.display = 'none';
            defaultIcon.style.display = 'block';
            toggleDefaultIcon();
        });
    }

    if (exploreButton) {
        exploreButton.addEventListener('click', () => {
            navigateWithTransition('../login');
        });
    }

    if (favouritesButton) {
        favouritesButton.addEventListener('click', () => {
            navigateWithTransition('favourites.html');
        });
    }

    if (settingsButton) {
        settingsButton.addEventListener('click', () => {
            navigateWithTransition('settings.html');
        });
    }

    if (profileButton) {
        profileButton.addEventListener('click', () => {
            navigateWithTransition('profile.html');
        });
    }
    
    const activeLink = localStorage.getItem('activeLink');
    if (activeLink) {
        const activeElement = document.querySelector(`.category-links a[href="${activeLink}"]`);
        if (activeElement) {
            activeElement.classList.add('active');
        }
    }

    const links = document.querySelectorAll('.category-links a');
    links.forEach(link => {
        link.addEventListener('click', function(event) {
            event.preventDefault(); // Prevent the default link behavior
            links.forEach(l => l.classList.remove('active'));
            const href = this.getAttribute('href');
            console.log('Clicked link href:', href); // Debugging log
            if (href !== './' && href !== 'index.html') { // Check if the link is not the homepage
                this.classList.add('active');
                localStorage.setItem('activeLink', href);
            } else {
                localStorage.removeItem('activeLink'); // Clear activeLink for homepage
            }
            window.location.href = href; // Navigate to the link's href
        });
    });

    // Check if the current page is the homepage and remove the active class
    const currentPath = window.location.pathname;
    if (currentPath === '/' || currentPath.endsWith('index.html')) {
        links.forEach(link => link.classList.remove('active'));
    }

    const passwordInput = document.getElementById('password');
    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            let password = passwordInput.value;
            let passwordHelp = document.getElementById('passwordHelp');
            if (password.length < 8) {
                passwordHelp.style.display = 'block';
            } else {
                passwordHelp.style.display = 'none';
            }
        });
    }

    if (typeof flashedMessages !== 'undefined') {
        flashedMessages.forEach(([category, message]) => {
            if (category === 'error' && message.includes('Current password is invalid')) {
                const currentPassword = document.getElementById('current-password');
                const newPassword = document.getElementById('new-password');
                if (currentPassword) currentPassword.value = '';
                if (newPassword) newPassword.value = '';
            }
        });
    }

    const closePopupButton = document.getElementById('closePopup');

    if (closePopupButton) {
        closePopupButton.addEventListener('click', function() {
            document.getElementById('overlay').style.display = 'none';
            document.getElementById('popup').style.display = 'none';
            document.querySelector('header').classList.remove('grayed-out');
        });
    }
    
    const overlay = document.getElementById('overlay');
    const popup = document.getElementById('popup');
    if (overlay && popup) {
        // Show the pop-up and gray out the header when the page loads or when a specific event occurs
        overlay.style.display = 'block';
        popup.style.display = 'block';
    }

    const exploreLink = document.querySelector('.explore-link');
    if (exploreLink) {
        exploreLink.addEventListener('click', function(event) {
            event.preventDefault(); // Prevent the default link behavior
            navigateWithTransition('/signup'); // Use the correct URL for the signup page
        });
    }

    //favourites

    const rightButton = document.querySelector('.fav-right-btn');
    const leftButton = document.querySelector('.fav-left-btn');
    const cards = document.querySelectorAll('.fav-carousell > div');
    let currentIndex = 0;

    function updateCards() {
        cards.forEach((card, index) => {
            if (index === currentIndex) {
                card.style.zIndex = 3;
                card.style.transform = 'translateX(0)';
            } else if (index === (currentIndex + 1) % cards.length) {
                card.style.zIndex = 2;
                card.style.transform = 'translateX(100%)';
            } else if (index === (currentIndex + 2) % cards.length) {
                card.style.zIndex = 1;
                card.style.transform = 'translateX(200%)';
            } else {
                card.style.zIndex = 0;
                card.style.transform = 'translateX(-100%)';
            }
        });
    }

    if (rightButton) {
        rightButton.addEventListener('click', function() {
            currentIndex = (currentIndex + 1) % cards.length;
            updateCards();
        });
    }

    if (leftButton) {
        leftButton.addEventListener('click', function() {
            currentIndex = (currentIndex - 1 + cards.length) % cards.length;
            updateCards();
        });
    }

    updateCards(); // Initialize the positions
    
    const escButtons = document.querySelectorAll('.fav-card-esc');
    escButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            const parentCard = button.closest('.fav-card');
            if (parentCard) {
                parentCard.remove();
                updateCards(); // Update the positions after removing a card
            }
        });
    });

    const darkModeToggle = document.getElementById('dark-mode-toggle');
    const body = document.body;
    const modeLabel = document.getElementById('mode-label');
    const analyticGraph = document.getElementById('analytic-graph');
    const barChart = document.getElementById('bar-chart');
    const candleChart = document.getElementById('candlestick-chart');
    const lineChart = document.getElementById('line-chart');
    const orgChart = document.getElementById('org-chart');
    const pieChart = document.getElementById('pie-chart');

    // Function to update image source based on dark mode
    function updateImageSource() {
        if (analyticGraph) {
            if (body.classList.contains('dark-mode')) {
                analyticGraph.src = "/static/img/lighter-analytic-graph.png"; // Update with the correct path
            } else {
                analyticGraph.src = "/static/img/darker-analytic-graph.png"; // Update with the correct path
            }
        }
        if (barChart) {
            if (body.classList.contains('dark-mode')) {
                barChart.src = "/static/img/lighter-bar-chart.png"; // Update with the correct path
            } else {
                barChart.src = "/static/img/darker-bar-chart.png"; // Update with the correct path
            }
        }
        if (candleChart) {
            if (body.classList.contains('dark-mode')) {
                candleChart.src = "/static/img/lighter-candlestick-chart.png"; // Update with the correct path
            } else {
                candleChart.src = "/static/img/darker-candlestick-chart.png"; // Update with the correct path
            }
        }
        if (lineChart) {
            if (body.classList.contains('dark-mode')) {
                lineChart.src = "/static/img/lighter-line-chart.png"; // Update with the correct path
            } else {
                lineChart.src = "/static/img/darker-line-chart.png"; // Update with the correct path
            }
        }
        if (orgChart) {
            if (body.classList.contains('dark-mode')) {
                orgChart.src = "/static/img/lighter-organization-chart.png"; // Update with the correct path
            } else {
                orgChart.src = "/static/img/darker-organization-chart.png"; // Update with the correct path
            }
        }
        if (pieChart) {
            if (body.classList.contains('dark-mode')) {
                pieChart.src = "/static/img/lighter-pie-chart.png"; // Update with the correct path
            } else {
                pieChart.src = "/static/img/darker-pie-chart.png"; // Update with the correct path
            }
        }
    }
     // Check for saved user preference, if any, on load of the website
     if (localStorage.getItem('darkMode') === 'enabled') {
        body.classList.add('dark-mode');
        if (darkModeToggle) darkModeToggle.checked = true;
        if (modeLabel) modeLabel.textContent = 'Dark Mode';
    } else if (modeLabel) {
        modeLabel.textContent = 'Light Mode';
    }
    updateImageSource(); // Ensure the correct image is displayed on page load

    if (darkModeToggle) {
        darkModeToggle.addEventListener('change', function() {
            body.classList.toggle('dark-mode');
            if (body.classList.contains('dark-mode')) {
                localStorage.setItem('darkMode', 'enabled');
                if (modeLabel) modeLabel.textContent = 'Dark Mode';
            } else {
                localStorage.setItem('darkMode', 'disabled');
                if (modeLabel) modeLabel.textContent = 'Light Mode';
            }
            updateImageSource();
        });
    }

    /* search */
    const searchInput = document.getElementById('search-input');
    const searchSuggestions = document.getElementById('search-suggestions');

    searchInput.addEventListener('input', function() {
        const query = searchInput.value.trim();
        if (query.length > 0) {
            fetch(`/top_searches?query=${query}`)
                .then(response => response.json())
                .then(data => {
                    searchSuggestions.innerHTML = '';
                    if (data.length > 0) {
                        searchSuggestions.style.display = 'block';
                        data.forEach(item => {
                            const suggestion = document.createElement('a');
                            suggestion.href = `/search?query=${item.title}`;
                            suggestion.textContent = item.title;
                            searchSuggestions.appendChild(suggestion);
                        });
                        searchSuggestions.insertAdjacentHTML('beforeend', '<div class="dropdown-state">Based on top searches</div>');
                    } else {
                        fetch(`/alphabetical_searches?query=${query}`)
                            .then(response => response.json())
                            .then(data => {
                                searchSuggestions.innerHTML = '';
                                if (data.length > 0) {
                                    searchSuggestions.style.display = 'block';
                                    data.forEach(item => {
                                        const suggestion = document.createElement('a');
                                        suggestion.href = `/search?query=${item.title}`;
                                        suggestion.textContent = item.title;
                                        searchSuggestions.appendChild(suggestion);
                                    });
                                    searchSuggestions.insertAdjacentHTML('beforeend', '<div class="dropdown-state">Based on alphabetically</div>');
                                } else {
                                    searchSuggestions.style.display = 'none';
                                }
                            });
                    }
                });
        } else {
            searchSuggestions.style.display = 'none';
        }
    });

    document.addEventListener('click', function(event) {
        if (!searchInput.contains(event.target) && !searchSuggestions.contains(event.target)) {
            searchSuggestions.style.display = 'none';
        }
    });

    /* movie details fav */
    const movieDetailsFav = document.getElementById('movie-details-fav');

    if (movieDetailsFav) {
        movieDetailsFav.addEventListener('click', function() {
            const movieId = movieDetailsFav.getAttribute('data-movie-id');
            const isFavorite = movieDetailsFav.classList.contains('clicked');
            const url = isFavorite ? '/remove_from_favourites' : '/add_to_favourites';

            fetch(`${url}?movie_id=${movieId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    movieDetailsFav.classList.toggle('clicked'); // Toggle the 'clicked' class
                } else {
                    alert('Failed to update favourites.');
                }
            });
        });
    }
    
});