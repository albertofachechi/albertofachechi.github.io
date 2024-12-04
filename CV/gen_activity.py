import os
from bs4 import BeautifulSoup, Comment

# Function to escape special LaTeX characters except for \textbf and other LaTeX commands
def escape_latex(text):
    special_chars = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
        '\n': r'\\',  # Replace newline with LaTeX line break
    }
    for char, replacement in special_chars.items():
        text = text.replace(char, replacement)
    return text.strip()

# Function to extract content from the HTML comment
def extract_comment_content(soup, comment_tag):
    # Find the comment containing the specified tag
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    for comment in comments:
        if comment_tag in comment:
            # Extract the content and remove the tag
            content = comment.replace(comment_tag, '').strip()
            return content
    return None

# Function to process and format the LaTeX content
def process_comment_content(content):
    # Escape special LaTeX characters for the content
    escaped_content = escape_latex(content)
    # Replace blank lines with LaTeX paragraph breaks
    formatted_content = escaped_content.replace(r'\\\s*\\', r'\par')
    return formatted_content

# Function to generate LaTeX file from the extracted content
def generate_activity_tex(html_file, tex_file):
    # Read the HTML content
    with open(html_file, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract the content from the "FOR CV" comment
    comment_content = extract_comment_content(soup, "FOR CV")
    if not comment_content:
        print("Comment tagged 'FOR CV' not found in the HTML file.")
        return

    # Process and format the extracted content for LaTeX
    formatted_content = process_comment_content(comment_content)

    # Generate the LaTeX content without extra curly braces
    tex_content = (
        "\\begin{rubric}{Activity and research interests}\\begin{minipage}{\\textwidth}\n"
        f"{formatted_content}\n"
        "\\end{minipage}\\end{rubric}"
    )

    # Write the LaTeX content to the output file
    with open(tex_file, 'w', encoding='utf-8') as file:
        file.write(tex_content)
    print(f"LaTeX file '{tex_file}' created successfully.")

# Main script
if __name__ == "__main__":
    # Get the path to the mother directory
    mother_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # Input HTML file in the mother directory
    html_file = os.path.join(mother_dir, 'index.html')
    
    # Output LaTeX file in the current directory
    tex_file = "activity.tex"
    
    generate_activity_tex(html_file, tex_file)

