document.addEventListener('DOMContentLoaded', function() {
    const hamburgerMenu = document.getElementById('hamburger-menu');
    const exploreButton = document.getElementById('explore-button');
    const homeButton = document.querySelector('a[href="basic.html"]');
    const favouritesButton = document.querySelector('a[href="favourites.html"]');
    const settingsButton = document.querySelector('a[href="settings.html"]');
    const sidePanel = document.getElementById('side-panel');
    const contentSections = document.querySelectorAll('.content');

    function toggleSidePanel() {
        sidePanel.classList.toggle('show');
        contentSections.forEach(section => {
            section.classList.toggle('shifted');
        });
    }

    // Dont touch for future reference
    // function showSection(sectionId) {
    //     contentSections.forEach(section => {
    //         if (section.id === sectionId) {
    //             section.style.display = 'block';
    //         } else {
    //             section.style.display = 'none';
    //         }
    //     });
    // }

    function navigateWithTransition(url) {
        document.body.classList.add('fade-out');
        setTimeout(() => {
            window.location.href = url;
        }, 500); // Match the duration of the CSS transition
    }

    hamburgerMenu.addEventListener('click', toggleSidePanel);
    exploreButton.addEventListener('click', () => {
        navigateWithTransition('../basic.html');
    });
    homeButton.addEventListener('click', () => {
        navigateWithTransition('basic');
    });
    favouritesButton.addEventListener('click', () => {
        navigateWithTransition('favourites.html');
    });
    settingsButton.addEventListener('click', () => {
        navigateWithTransition('settings.html');
    });
});