let prev = document.getElementById('prev');
    let next = document.getElementById('next');
    let image = document.querySelector('.images');
    let items = document.querySelectorAll('.images .item');
    let contents = document.querySelectorAll('.content .item');
    
    let rotate = 0;
    let active = 0;
    let countItem = items.length;
    let rotateAdd = 360 / countItem;
    
    function nextSlider(){
        active = active + 1 > countItem - 1 ? 0 : active + 1;
        rotate = rotate + rotateAdd; 
        show();
    }
    function prevSlider(){
        active = active - 1 < 0 ? countItem - 1 : active - 1;
        rotate = rotate - rotateAdd; 
        show();     
         
    }
    function show(){
        image.style.setProperty("--rotate", rotate + 'deg');
        image.style.setProperty("--rotate", rotate + 'deg');
        contents.forEach((content, key) => {
            if(key == active){
                content.classList.add('active');
            }else{
                content.classList.remove('active');
            }
        })
    }
    next.onclick = nextSlider;
    prev.onclick = prevSlider;
    const autoNext = setInterval(nextSlider, 3000);
// JavaScript for Automatic Slider with Pause on Hover

document.addEventListener('DOMContentLoaded', function() {
    const images = document.querySelector('.images');
    const items = document.querySelectorAll('.images .item');
    const contents = document.querySelectorAll('.content .item');
    let currentIndex = 0;
    let sliderInterval;

    function showSlide(index) {
        items.forEach((item, i) => {
            item.classList.toggle('active', i === index);
            contents[i].classList.toggle('active', i === index);
        });
    }

    function startSlider() {
        sliderInterval = setInterval(() => {
            currentIndex = (currentIndex + 1) % items.length;
            showSlide(currentIndex);
        }, 3000); // Change every 3 seconds
    }

    function pauseSlider() {
        clearInterval(sliderInterval);
    }

    // Event listeners to pause/resume slider on hover
    images.addEventListener('mouseover', pauseSlider);
    images.addEventListener('mouseout', startSlider);

    // Start the slider
    startSlider();
});
