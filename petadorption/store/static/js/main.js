// document.addEventListener('DOMContentLoaded', function() {
    
//     const categories = document.querySelectorAll('.category');
//     categories.forEach(category => {
//         category.addEventListener('click', function(e) {
            
//             if (e.target.tagName === 'A') {
//                 return;
//             }
//             const link = this.querySelector('a');
//             if (link) {
//                 window.location.href = link.href;
//             }
//         });
//     });

//     const menuToggle = document.querySelector('.menu-toggle');
//     const navMenu = document.querySelector('.nav-menu');
    
//     if (menuToggle && navMenu) {
//         menuToggle.addEventListener('click', function() {
//             navMenu.classList.toggle('active');
//         });
//     }
// });



document.addEventListener('DOMContentLoaded', function() {
    // Improved category click handler
    document.querySelectorAll('.category').forEach(category => {
        category.addEventListener('click', function(e) {
            // Check if click was directly on a link
            if (e.target.tagName === 'A') {
                return true; // Allow default link behavior
            }
            
            // Find the nearest link in the category
            const link = this.querySelector('a');
            if (link) {
                e.preventDefault(); // Prevent any default behavior
                window.location.href = link.href;
            }
        });
    });

    // Mobile menu toggle (unchanged, but added null checks)
    const menuToggle = document.querySelector('.menu-toggle');
    const navMenu = document.querySelector('.nav-menu');
    
    if (menuToggle && navMenu) {
        menuToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
        });
    }
});