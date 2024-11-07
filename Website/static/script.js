document.addEventListener('DOMContentLoaded', function() {
    const hamburgerMenu = document.getElementById('hamburger-menu');
    const exploreButton = document.getElementById('explore-button');
    const homeButton = document.querySelector('a[href="basic.html"]');
    const favouritesButton = document.querySelector('a[href="favourites.html"]');
    const settingsButton = document.querySelector('a[href="settings.html"]');
    const profileButton = document.querySelector('a[href="profile.html"]');
    const sidePanel = document.getElementById('side-panel');
    const contentSections = document.querySelectorAll('.content');
    const uploadInput = document.getElementById('upload');
    const profilePicture = document.getElementById('profile-picture');
    const cropperModal = document.getElementById('cropperModal');
    const cropperImage = document.getElementById('cropper-image');
    const cropButton = document.getElementById('crop-button');
    const closeModal = document.querySelector('.close');
    const deleteButton = document.getElementById('delete-btn');
    const defaultIcon = document.getElementById('default-icon');
    let cropper;

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

    if (hamburgerMenu){
        hamburgerMenu.addEventListener('click', toggleSidePanel);
    }

    if (exploreButton) {
        exploreButton.addEventListener('click', () => {
            navigateWithTransition('../basic.html');
        });
    }

    if (homeButton) {
        homeButton.addEventListener('click', () => {
            navigateWithTransition('basic.html');
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

    function toggleDefaultIcon() {
        if (profilePicture.src && profilePicture.src !== window.location.href) {
            defaultIcon.classList.add('hidden');
            profilePicture.style.display = 'block';
        } else {
            defaultIcon.classList.remove('hidden');
            profilePicture.style.display = 'none';
        }
    }

    // Initial check
    toggleDefaultIcon();

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

    closeModal.addEventListener('click', function() {
        if (cropper) {
            cropperModal.style.display = 'none';
            cropper.destroy();
            cropper = null; // Reset cropper
        }
    });

    window.addEventListener('click', function(event) {
        if (event.target == cropperModal) {
            if (cropper) {
                cropperModal.style.display = 'none';
                cropper.destroy();
                cropper = null; // Reset cropper
            }
        }
    });

    deleteButton.addEventListener('click', function() {
        profilePicture.src = '';
        profilePicture.style.display = 'none';
        defaultIcon.style.display = 'block';
        toggleDefaultIcon();
    });

});