import os

# Define the LaTeX CV structure
def generate_cv_tex(filename):
    content = r"""
\documentclass[a4paper,skipsamekey,11pt,english]{curve}
\PassOptionsToPackage{style=ieee,sorting=ydnt,uniquename=init,defernumbers=true}{biblatex}
\usepackage{settings}
\usepackage[utf8]{inputenc}
\usepackage{geometry}
\usepackage{hyperref}
\usepackage{titlesec}
\newcommand{\description}{}
\usepackage{enumitem}

\titleformat{\section}{\large\bfseries}{\thesection.}{1em}{}
\titleformat{\subsection}{\normalsize\bfseries}{\thesubsection.}{1em}{}


\DefineBibliographyStrings{english}{url={\textsc{url}}}
\addbibresource{publications.bib}

\mynames{Fachechi/Alberto}
%% MAKE SURE THERE IS NO SPACE AFTER THE FINAL NAME IN YOUR \mynames LIST


% Change the fonts if you want
\ifxetexorluatex % If you're using XeLaTeX or LuaLaTeX
  \usepackage{fontspec} 
  %% You can use \setmainfont etc; I'm just using these font packages here because they provide OpenType fonts for use by XeLaTeX/LuaLaTeX anyway
  \usepackage[p,osf,swashQ]{cochineal}
  \usepackage[medium,bold]{cabin}
  \usepackage[varqu,varl,scale=0.9]{zi4}
\else % If you're using pdfLaTeX or latex
  \usepackage[T1]{fontenc}
  \usepackage[p,osf,swashQ]{cochineal}
  \usepackage{cabin}
  \usepackage[varqu,varl,scale=0.9]{zi4}
\fi

\usepackage{hyperref}
\let\svthefootnote\thefootnote
\newcommand\freefootnote[1]{%
  \let\thefootnote\relax%
  \footnotetext{#1}%
  \let\thefootnote\svthefootnote%
}

% Change the page margins if you want
% \geometry{left=1cm,right=1cm,top=1.5cm,bottom=1.5cm}

% Change the colours if you want
% \definecolor{SwishLineColour}{HTML}{00FFFF}
% \definecolor{MarkerColour}{HTML}{0000CC}

% Change the item prefix marker if you want
% \prefixmarker{$\diamond$}

%% Photo is only shown if "fullonly" is included
\includecomment{fullonly}
% \excludecomment{fullonly}


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


\leftheader{%
  {\LARGE\bfseries\sffamily Alberto Fachechi}

  \makefield{\faEnvelope[regular]}{\href{mailto:alberto.fachechi@gmail.com}{\texttt{alberto.fachechi@gmail.com}}}
  %\makefield{\faTwitter}%{\href{https://twitter.com/overleaf_example}{\texttt{@overleaf\_example}}}
  %\makefield{\faLinkedin}
  %{\href{http://www.linkedin.com/in/example/}{\texttt{example}}}
  %% Next line
  \makefield{\faGlobe}{\url{http://albertofachechi.com}}

  % You can use a tabular here if you want to line up the fields.
}

\rightheader{~}
%\begin{fullonly}
%\photo[r]{photo}
%\photoscale{0.13}
%\end{fullonly}

\title{Curriculum Vitae}


\setlist[itemize]{left=0pt}

\begin{document}
\makeheaders[c]

\makerubric{activity}
\makerubric{employment}
\makerubric{education}
\makerubric{groups}
\makerubric{teaching}
\makerubric{supervising}
\makerubric{projects}
\makerubric{others}
\makerubric{recognitions}

\makerubric{summary}\freefootnote{${}^1$Source: GoogleScholar.}
\input{publications}
\makerubric{talks}

\end{document}
    """
    with open(filename, 'w') as file:
        file.write(content)
    print(f"LaTeX CV template written to {filename}")

# Function to compile the LaTeX file
def compile_tex(filename):
    os.system(f"pdflatex {filename}")

# Main script
if __name__ == "__main__":
    tex_filename = "CV_Fachechi.tex"
    generate_cv_tex(tex_filename)
    print("To compile the LaTeX file, run the following command in your terminal:")
    print(f"pdflatex {tex_filename}")
