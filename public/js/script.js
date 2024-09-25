const cards = document.querySelectorAll('.group2');
const card3Image = document.getElementById('img-3');

cards.forEach(card => {
    card.addEventListener('mouseover', () => {
        card3Image.classList.add('grayscale2');
    });

    card.addEventListener('mouseout', () => {
        card3Image.classList.remove('grayscale2');
    });
});