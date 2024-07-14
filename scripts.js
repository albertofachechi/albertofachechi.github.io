
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

/* for the bibliography */
document.addEventListener('DOMContentLoaded', function() {
    fetch('publications.bib') // Ensure this path is correct
    .then(response => response.text())
    .then(bibtex => {
        const publications = parseBibTeX(bibtex);
        displayPublications(publications);
    })
    .catch(error => console.error('Error fetching BibTeX file:', error));
});

function parseBibTeX(bibtex) {
const entries = bibtex.split('@').slice(1);
const publications = [];

entries.forEach(entry => {
    const lines = entry.split('\n').filter(line => line.trim() !== '');
    let publication = {};
    
    lines.forEach(line => {
        const [key, value] = line.split('=').map(item => item.trim().replace(/[{()}]/g, ''));
        if (key && value) {
            // Remove trailing commas if any
            publication[key] = value.replace(/"/g, '').replace(/,$/, '').trim();
        }
    });

    if (publication.title && publication.author && publication.journal) {
        publications.push(publication);
    }
});

return publications;
}

function displayPublications(publications) {
    const listContainer = document.querySelector('.publication-list');
    listContainer.innerHTML = ''; // Clear previous content

    publications.forEach((pub) => {
        const itemDiv = document.createElement('div'); // Create a div for each publication
        itemDiv.classList.add('publication-item'); // Add class for styling

        let details = ''; // Initialize details

        // Title
        if (pub.title) {
            details += `<p class="pub-title"><em>${pub.title}</em></p>`;
        }

        // Authors
        if (pub.author) {
            details += `<p class="pub-authors">${formatAuthors(pub.author)}</p>`;
        }

        // Book title / Journal name
        if (pub.booktitle) {
            details += `<p class="pub-details">${pub.booktitle}`;
        } else if (pub.journal) {
            details += `<p class="pub-details">${pub.journal}`;
        }

        // Volume
        if (pub.volume) {
            details += `, ${pub.volume}`;
        }

        // Add pages if available
        if (pub.pages) {
            details += `, ${pub.pages}`;
        }

        // Add year if available
        if (pub.year) {
            details += ` (${pub.year})`;
        }

        // Close the details paragraph if any details were added
        if (pub.booktitle || pub.journal) {
            details += `</p>`;
        }

        // Set the inner HTML only if there are details to display
        if (details) {
            itemDiv.innerHTML = details;
            listContainer.appendChild(itemDiv); // Append to the container
        }
    });

    // Reprocess the content with MathJax if needed
    MathJax.typeset();
}



function formatAuthors(authorString) {
    const authors = authorString.split('and').map(author => author.trim());
    return authors.map(author => {
        const [lastName, firstName] = author.split(',');
        const firstNameInitial = firstName ? firstName.trim().charAt(0) + '.' : '';

        // Check for "Fachechi" and make it bold
        if (lastName.trim() === "Fachechi") {
            return `<strong>${firstNameInitial} ${lastName.trim()}</strong>`;
        }

        return `${firstNameInitial} ${lastName.trim()}`;
    }).join(', ');
}
