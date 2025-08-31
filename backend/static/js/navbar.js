document.addEventListener('click', function(event) {
    const nav = document.querySelector('.navbar-collapse');
    const hamburger = document.querySelector('.navbar-toggler');
    const isClickInsideNav = nav.contains(event.target);
    const isClickOnHamburger = hamburger.contains(event.target);

    if (nav.classList.contains('show') && !isClickInsideNav && !isClickOnHamburger) {
        // Klap het menu in door de 'show' class te verwijderen
        nav.classList.remove('show');
    }
});