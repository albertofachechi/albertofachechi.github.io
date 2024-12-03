from bs4 import BeautifulSoup

# List of input HTML files
html_files = ["index.html"]  # Add your input files here

# Output TeX file
output_tex_file = "cv.tex"

# LaTeX document structure
latex_header = r"""
\documentclass[11pt,a4paper]{article}
\usepackage{cvstyle}

\begin{document}
"""

latex_footer = r"""
\end{document}
"""

# Function to process a single HTML file
def process_html_file(file):
    with open(file, "r", encoding="utf-8") as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, "html.parser")
    name = soup.find("h1").get_text(strip=True)
    overview_section = soup.find("section", id="overview")
    document_content = f"\\title{{{name}}}\n\\author{{}}\n\\date{{}}\n\\maketitle\n\n"

    # Parse overview content
    if overview_section:
        document_content += r"\makerubrichead{Overview}\n"
        boxes = overview_section.find_all("div", class_="box")
        for box in boxes:
            title = box.find("h2", class_="section-title").get_text(strip=True)
            document_content += f"\\paragraph{{{title}}}\n"  # Use \paragraph for subsections
            box_content = box.find("div", class_="box-content")
            if box_content:
                paragraphs = box_content.find_all("p")
                lists = box_content.find_all("ul")
                if paragraphs:
                    for para in paragraphs:
                        document_content += f"{para.get_text(strip=True)}\n\n"
                if lists:
                    for ul in lists:
                        document_content += "\\begin{itemize}\n"
                        for li in ul.find_all("li"):
                            document_content += f"  \\item {li.get_text(strip=True)}\n"
                        document_content += "\\end{itemize}\n\n"
    return document_content

# Compile content from all HTML files
latex_document = latex_header
for html_file in html_files:
    latex_document += process_html_file(html_file)
latex_document += latex_footer

# Write to a TeX file
with open(output_tex_file, "w", encoding="utf-8") as tex_file:
    tex_file.write(latex_document)

print(f"TeX file generated: {output_tex_file}")

