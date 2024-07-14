
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

/* for the bibliography */document.addEventListener('DOMContentLoaded', function() {
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

    const ol = document.createElement('ol'); // Create an ordered list

    publications.forEach((pub) => {
        const listItem = document.createElement('li'); // Create a list item

        // Replace $$...$$ with \(...\)
        const displayDetails = pub.journal + 
            ', ' + pub.volume + 
            ', ' + pub.pages + 
            ' (' + pub.year + ')';
        
        const formattedDetails = displayDetails.replace(/\$\$(.*?)\$\$/g, '\\($1\\)');

        listItem.innerHTML = `
            <p class="pub-title"><em>${pub.title}</em></p>
            <p class="pub-authors">${formatAuthors(pub.author)}</p>
            <p class="pub-details">${formattedDetails}</p>
            <p class="pub-link"><a href="${pub.url || '#'}" target="_blank">View Article</a></p>
        `;
        
        ol.appendChild(listItem); // Add the list item to the ordered list
    });

    listContainer.appendChild(ol); // Append the ordered list to the container

    // Reprocess the content with MathJax
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
