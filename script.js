const pictures = [
    "/static/images/animal.jpg",
    "/static/images/cartoon.jpg",
    "/static/images/movie.jpg",
    "/static/images/nature.jpg",
    "/static/images/news.jpg"
];

let index = 0;

const img = document.getElementById("highlight");

setInterval(() => {
    index = (index + 1) % pictures.length;
    img.src = pictures[index];
}, 10000); 

const categoryButtons = document.querySelectorAll(".categories button");
const searchInput = document.querySelector(".search-box input");
const searchForm = document.querySelector(".search-box");

categoryButtons.forEach(button => {

    button.addEventListener("click", function () {

        const query = this.dataset.query;

        searchInput.value = query;

        setTimeout(() => {
            searchForm.requestSubmit();
        }, 100);

    });

});