import os
from bs4 import BeautifulSoup

# Function to escape special LaTeX characters except for \textbf and other LaTeX commands
def escape_latex(text):
    special_chars = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        #'{': r'\{',
        #'}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
        #'\\': r'\textbackslash{}',
        '\n': ' ',
    }
    for char, replacement in special_chars.items():
        text = text.replace(char, replacement)
    return text.strip()

# Function to process the content with LaTeX formatting for \textbf
def process_html_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text(separator=' ')
    
    # Add \textbf to specific words, without escaping the LaTeX command
    text = text.replace('Contents:', r'\textbf{Contents}:')
    text = text.replace('Methods:', r'\textbf{Methods}:')
    text = text.replace('Other interests:', r'\textbf{Other interests}:')
    
    # Escape other special characters for LaTeX
    return escape_latex(text)

# Function to extract "My research interests" section and generate LaTeX file
def generate_activity_tex(html_file, tex_file):
    # Read the HTML content
    with open(html_file, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the "My research interests" section
    research_section = soup.find('h2', text='My research interests')
    if not research_section:
        print("Section 'My research interests' not found in the HTML file.")
        return
    
    # Get the corresponding content
    content_div = research_section.find_next('div', class_='box-content')
    if not content_div:
        print("Content for 'My research interests' not found.")
        return
    
    # Extract the raw HTML content of the list
    items = content_div.find_all('li')
    extracted_content = "\n".join(
        f"\\entry*[]{{{process_html_content(str(item))}}}" for item in items
    )

    # Generate the LaTeX content
    tex_content = f"""\\begin{{rubric}}{{Activity and research interests}}
{extracted_content}
\\end{{rubric}}"""

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

