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
    const advancedShiftedContainers = document.querySelectorAll('.advanced-shifted-container');
    const advancedPageTitles = document.querySelectorAll('.advanced-page-title');

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
            advancedShiftedContainers.forEach(container => {
                container.classList.toggle('shifted');
            });
            advancedPageTitles.forEach(title => {
                title.classList.toggle('shifted');
            });
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
    let cards = document.querySelectorAll('.fav-carousell > div');
    let currentIndex = 0;

    function updateCards() {
        const totalCards = cards.length;
        const visibleCards = 5; // Number of cards to display
        const halfVisible = Math.floor(visibleCards / 2);

        if (totalCards === 0) {
            displayNoMoreCardsMessage();
            return;
        }

        cards.forEach((card, index) => {
            card.classList.remove('active', 'adjacent-left', 'adjacent-right', 'left', 'right');
            const position = (index - currentIndex + totalCards) % totalCards;

            if (position === 0) {
                card.classList.add('active');
                card.style.transform = `translateX(0) scale(1.2)`;
            } else if (position === 1 || position === totalCards - 1) {
                card.classList.add(position === 1 ? 'adjacent-right' : 'adjacent-left');
                card.style.transform = `translateX(${position === 1 ? 150 : -150}px) scale(1)`;
            } else if (position === 2 || position === totalCards - 2) {
                card.classList.add(position === 2 ? 'right' : 'left');
                card.style.transform = `translateX(${position === 2 ? 300 : -300}px) scale(0.8)`;
            } else {
                card.style.transform = `translateX(${position > halfVisible ? 450 : -450}px) scale(0.6)`;
            }
        });
    }

    function handleCardClick(event) {
        const clickedCard = event.currentTarget;
        const clickedIndex = Array.from(cards).indexOf(clickedCard);
        if (clickedIndex !== -1) {
            currentIndex = clickedIndex;
            updateCards();
        }
    }
    
    cards.forEach(card => {
        card.addEventListener('click', handleCardClick);
    });

    const deleteButtons = document.querySelectorAll('.fav-card-delete');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            const parentCard = button.closest('.fav-card');
            const movieId = parentCard.getAttribute('data-movie-id');
            if (parentCard) {
                fetch(`/remove_from_favourites?movie_id=${movieId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        parentCard.remove();
                        cards = document.querySelectorAll('.fav-carousell > .fav-card'); // Update the cards NodeList
                        currentIndex = 0; // Reset currentIndex to 0
                        updateCards(); // Update the positions after removing a card
                    } else {
                        alert('Failed to delete the card.');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
            }
        });
    });

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

    function displayNoMoreCardsMessage() {
        const carousel = document.querySelector('.fav-carousell');
        if (!carousel) {
            console.error('Carousel element not found');
            return;
        }
        const messageCard = document.createElement('div');
        messageCard.classList.add('fav-card', 'active');
        messageCard.innerHTML = `
            <div class="fav-card-title">No more cards</div>
            <div class="fav-card-synopsis">You have removed all your favourite movies.</div>
            <button class="fav-card-btn" id="search-movies-btn">Search for Movies</button>
        `;
        carousel.appendChild(messageCard);

        const searchMoviesBtn = document.getElementById('search-movies-btn');
        searchMoviesBtn.addEventListener('click', function() {
            document.getElementById('search-input').focus();
            showPopupDialog();
        });
    }

    function showPopupDialog() {
        const searchInput = document.getElementById('search-input');
        const searchSuggestions = document.getElementById('search-suggestions');
    
        // Clear any existing suggestions
        searchSuggestions.innerHTML = '';
    
        // Create the dropdown message
        const message = document.createElement('div');
        message.classList.add('dropdown-state');
        message.textContent = 'Please type something to search';
    
        // Append the message to the search suggestions
        searchSuggestions.appendChild(message);
    
        // Show the search suggestions dropdown
        searchSuggestions.style.display = 'block';
    
        // Hide the dropdown when clicking outside
        document.addEventListener('click', function(event) {
            if (!searchInput.contains(event.target) && !searchSuggestions.contains(event.target)) {
                searchSuggestions.style.display = 'none';
            }
        });
    }

    updateCards(); // Initialize the positions

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

    updateImageSource(); // Ensure the correct image is displayed on page load

     // Check for saved user preference, if any, on load of the website
     if (localStorage.getItem('darkMode') === 'enabled') {
        body.classList.add('dark-mode');
        if (darkModeToggle) darkModeToggle.checked = true;
        if (modeLabel) modeLabel.textContent = 'Dark Mode';
    } else if (modeLabel) {
        modeLabel.textContent = 'Light Mode';
    }

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
                    console.log('Favorite status updated successfully.');
                } else {
                    alert('Failed to update favourites.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    }

    const searchForm = document.getElementById('search-form');
    const searchInput1 = document.querySelector('input[name="title1"]');
    const searchInput2 = document.querySelector('input[name="title2"]');
    const errorMessage = document.getElementById('error-message');

    if (searchForm) {
        searchForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const title1 = searchInput1.value.trim();
            const title2 = searchInput2.value.trim();

            if (!title1 || !title2) {
                errorMessage.style.display = 'block';
            } else {
                errorMessage.style.display = 'none';
                searchForm.submit();
            }
        });
    }

    const regionButtons = document.querySelectorAll('.region-button');
    const regionDescription = document.getElementById('region-description');

    const descriptions = {
        'north-america': 'North America is known for its prolific film industry, Hollywood, which produces a significant number of movies each year.',
        'europe': 'Europe has a rich history of cinema, with countries like France, Germany, and Italy contributing significantly to the global film industry.',
        'asia': 'Asia is home to some of the largest film industries in the world, including Bollywood in India and the rapidly growing film industry in China.',
        'south-america': 'South America has a vibrant film industry, with countries like Brazil and Argentina producing critically acclaimed movies.',
        'africa': 'Africa\'s film industry is growing, with Nollywood in Nigeria being one of the largest film producers in the world.',
        'oceania': 'Oceania, particularly Australia and New Zealand, has a thriving film industry known for producing high-quality movies.'
    };

    regionButtons.forEach(button => {
        button.addEventListener('click', function() {
            const region = this.getAttribute('data-region');
            regionDescription.innerHTML = `<p class="region-description-text">${descriptions[region]}</p>`;
        });
    });
});

