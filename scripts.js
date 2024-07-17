
MathJax = {
    tex: {
      inlineMath: [['$', '$'], ['\\(', '\\)']],
      tags: 'ams'
    }
  };

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
    fetch('news.json')
        .then(response => response.json())
        .then(data => {
            const newsContainer = document.getElementById('news-container');
            const moreButton = document.createElement('button');
            moreButton.textContent = 'More';
            moreButton.className = 'more-button';  // Add class name
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


/* load all news */
document.addEventListener('DOMContentLoaded', function() {
    fetch('news.json')
        .then(response => response.json())
        .then(data => {
            const allNewsContainer = document.getElementById('all-news-container');
            data.forEach(news => {
                const newsItem = document.createElement('div');

                const newsDate = document.createElement('p');
                newsDate.className = 'news-date';
                
                // Create a strong element for bold text
                const boldDate = document.createElement('strong');
                boldDate.textContent = news.date;
                
                // Append the bold date to the newsDate paragraph
                newsDate.appendChild(boldDate);

                const newsContent = document.createElement('p');
                newsContent.textContent = news.content;

                newsItem.appendChild(newsDate);
                newsItem.appendChild(newsContent);
                allNewsContainer.appendChild(newsItem);
            });
        })
        .catch(error => console.error('Error fetching news:', error));
});

const form = document.getElementById("form");
const result = document.getElementById("result");

form.addEventListener("submit", function (e) {
  const formData = new FormData(form);
  e.preventDefault();
  var object = {};
  formData.forEach((value, key) => {
    object[key] = value;
  });
  var json = JSON.stringify(object);
  result.innerHTML = "Please wait...";

  fetch("https://api.web3forms.com/submit", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json"
    },
    body: json
  })
    .then(async (response) => {
      let json = await response.json();
      if (response.status == 200) {
        result.innerHTML = json.message;
        result.classList.remove("text-gray-500");
        result.classList.add("text-green-500");
      } else {
        console.log(response);
        result.innerHTML = json.message;
        result.classList.remove("text-gray-500");
        result.classList.add("text-red-500");
      }
    })
    .catch((error) => {
      console.log(error);
      result.innerHTML = "Something went wrong!";
    })
    .then(function () {
      form.reset();
      setTimeout(() => {
        result.style.display = "none";
      }, 5000);
    });
});
