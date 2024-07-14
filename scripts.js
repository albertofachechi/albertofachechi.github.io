
/* script 1*/
document.addEventListener('DOMContentLoaded', function() {
    const menuToggle = document.getElementById('menu-toggle');
    const nav = document.getElementById('nav');
    const container = document.querySelector('.container');

    menuToggle.addEventListener('click', function() {
        nav.classList.toggle('open');
        container.classList.toggle('menu-open');
    });
});

/* script 2*/
document.addEventListener("DOMContentLoaded", function() {
    const boxes = document.querySelectorAll(".box");
    boxes.forEach(box => {
        const button = box.querySelector(".collapse-btn");
        const content = box.querySelector(".box-content");
        const header = box.querySelector(".box-header");
        const visible = box.getAttribute("data-visible") === "true";

        // Set initial visibility
        if (!visible) {
            box.setAttribute("data-visible", "false");
            button.textContent = "+";
        } else {
            button.textContent = "-";
        }

        // Add click event listener
        button.addEventListener("click", () => {
            if (box.getAttribute("data-visible") === "true") {
                box.setAttribute("data-visible", "false");
                button.textContent = "+";
            } else {
                box.setAttribute("data-visible", "true");
                button.textContent = "-";
            }
        });
    });
});

/* script 3 */
document.addEventListener('DOMContentLoaded', function() {
    fetch('latest-news.json')
        .then(response => response.json())
        .then(data => {
            const newsContainer = document.getElementById('news-container');
            const moreButton = document.createElement('button');
            moreButton.textContent = 'More';
            moreButton.onclick = function() {
                window.location.href = 'feed.html';
            };
            const lastThreeNews = data.slice(-3);
            lastThreeNews.forEach(news => {
                const newsItem = document.createElement('div');
                const newsDate = document.createElement('p');
                newsDate.className = 'news-date';
                newsDate.textContent = news.date;

                const newsContent = document.createElement('p');
                newsContent.textContent = news.content;

                newsItem.appendChild(newsDate);
                newsItem.appendChild(newsContent);
                newsContainer.appendChild(newsItem);
            });
            newsContainer.appendChild(moreButton);
        })
        .catch(error => console.error('Error fetching news:', error));
});