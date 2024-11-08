document.addEventListener('DOMContentLoaded', function() {
    const hamburgerMenu = document.getElementById('hamburger-menu');
    const exploreButton = document.getElementById('explore-button');
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

    const links = document.querySelectorAll('.category-links a');
    const activeLink = localStorage.getItem('activeLink');

    function toggleSidePanel() {
        if (sidePanel) {
            console.log('sidePanel found');
            sidePanel.classList.toggle('show');
            contentSections.forEach(section => {
                section.classList.toggle('shifted');
            });
        } else {
            console.log('sidePanel not found');
        }
    }
    
    function navigateWithTransition(url) {
        document.body.classList.add('fade-out');
        setTimeout(() => {
            window.location.href = url;
        }, 500); // Match the duration of the CSS transition
    }

    if (hamburgerMenu) {
        console.log('hamburgerMenu found');
        hamburgerMenu.addEventListener('click', toggleSidePanel);
    } else {
        console.log('hamburgerMenu not found');
    }

    if (exploreButton) {
        exploreButton.addEventListener('click', () => {
            navigateWithTransition('../basic.html');
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
    
    if (activeLink) {
        const activeElement = document.querySelector(`.category-links a[href="${activeLink}"]`);
        if (activeElement) {
            activeElement.classList.add('active');
        }
    }

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

    document.getElementById('password').addEventListener('input', function() {
        let password = document.getElementById('password').value;
        let passwordHelp = document.getElementById('passwordHelp');
        if (password.length < 8) {
            passwordHelp.style.display = 'block';
        } else {
            passwordHelp.style.display = 'none';
        }
    });

    document.getElementById('closePopup').addEventListener('click', function() {
        document.getElementById('overlay').style.display = 'none';
        document.getElementById('popup').style.display = 'none';
        document.querySelector('header').classList.remove('grayed-out');
    });
    
    document.getElementById('overlay').addEventListener('click', function() {
        document.getElementById('overlay').style.display = 'none';
        document.getElementById('popup').style.display = 'none';
    });

    // Show the pop-up and gray out the header when the page loads or when a specific event occurs
    document.addEventListener('DOMContentLoaded', function() {
        document.getElementById('overlay').style.display = 'block';
        document.getElementById('popup').style.display = 'block';
    }); 

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

    document.getElementById('save-button').addEventListener('click', function() {
        // Get the input elements
        let contactEmail = document.getElementById('contact-email');
        let currentPassword = document.getElementById('current-password');
        let newPassword = document.getElementById('new-password');
    
        // Update the placeholder only if the input has a value
        if (contactEmail.value) {
            contactEmail.placeholder = contactEmail.value;
            contactEmail.value = '';
        }
        if (currentPassword.value) {
            currentPassword.placeholder = currentPassword.value;
            currentPassword.value = '';
        }
        if (newPassword.value) {
            newPassword.placeholder = newPassword.value;
            newPassword.value = '';
        }
    });



});