#!/usr/bin/env python3
"""
build_cv.py — Rigenera il CV LaTeX a partire dalle pagine del sito personale.

Legge index.html, cv.html, teaching.html e publications.html (dalla cartella
madre del repo oppure, con --url, dal sito online), scrive i file ausiliari
che CV_Fachechi.tex include con \\makerubric{...} e \\input{publications},
genera publications.bib e compila (latexmk, oppure pdflatex+biber+pdflatex).

Il template CV_Fachechi.tex NON viene toccato.

Uso:
    python3 build_cv.py                 # sorgente: cartella madre del repo
    python3 build_cv.py --url           # sorgente: https://albertofachechi.com
    python3 build_cv.py --source DIR    # sorgente: cartella DIR
    python3 build_cv.py --no-compile    # genera solo i file .tex/.bib

    python3 build_cv.py --backend bibtex  # bibliografia con bibtex invece di biber

Dipendenze: beautifulsoup4 (pip install beautifulsoup4), una distribuzione
TeX con biblatex-ieee, curve, fontawesome5, cochineal, cabin, inconsolata
e biber (o bibtex).

Errore "Found biblatex control file version X, expected version Y":
biber e biblatex vengono da installazioni diverse (es. biber di apt e
TeX Live di tlmgr). Lo script ripiega da solo su bibtex; per usare biber
fai in modo che il biber nel PATH sia quello della stessa TeX Live
(`which -a biber`, `kpsewhich biblatex.sty`, eventualmente
`tlmgr update --self biber biblatex`, oppure rimuovi il pacchetto apt biber).
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import unicodedata
import urllib.request

try:
    from bs4 import BeautifulSoup, Comment, NavigableString, Tag
except ImportError:
    sys.exit("Serve BeautifulSoup: pip install beautifulsoup4")


# ---------------------------------------------------------------------------
# CONFIGURAZIONE
# ---------------------------------------------------------------------------

SITE_URL = "https://albertofachechi.com"
TEMPLATE = "CV_Fachechi.tex"

# Rubrica del template -> (titolo nel CV, [(pagina, titolo della box nel sito), ...]).
# Se una rubrica ha più box, ognuna diventa una \subrubric col titolo del sito
# (o con quello indicato come terzo elemento della tupla).
RUBRICS = {
    "employment":   ("Positions",
                     [("cv.html", "Positions")]),
    "education":    ("Education",
                     [("cv.html", "Education")]),
    "groups":       ("Research groups and collaborations",
                     [("cv.html", "Communities", "Scientific communities"),
                      ("cv.html", "Collaborations")]),
    "teaching":     ("Teaching",
                     [("teaching.html", "Courses")]),
    "supervising":  ("Supervising",
                     [("teaching.html", "Supervising")]),
    "projects":     ("Funded projects",
                     [("cv.html", "Funded projects")]),
    "others":       ("Other activities",
                     [("cv.html", "Organization"),
                      ("cv.html", "Other roles"),
                      ("cv.html", "Visiting periods")]),
    "recognitions": ("Recognitions",
                     [("cv.html", "Recognitions")]),
    "talks":        ("Selected talks, invited talks and courses",
                     [("cv.html", "Selected talks to conferences, invited talks and courses")]),
}

ACTIVITY_TITLE = "Activity and research interests"
SUMMARY_TITLE = "Summary of scientific production"
# Righe della tabella metriche (testo normalizzato: solo a-z0-9) che ricevono
# il rimando ^1 alla nota "Source: GoogleScholar" del template.
SCHOLAR_METRICS = ("totalnumberofcitations", "hindex", "i10index")

# Rubriche da non stampare: il file viene scritto vuoto, così il
# \makerubric{...} del template non produce nulla.
DISABLED_RUBRICS = ("recognitions",)

# Righe da omettere, per rubrica: righe il cui testo inizia con questi prefissi.
DROP_LINES = {
    "education": ("Ref",),                     # "Ref:" / "Refs:"
    "teaching": ("Course shared with", "Ref"),
}

# Voci da omettere, per rubrica: la riga in grassetto (position) contiene
# una di queste stringhe (minuscolo).
DROP_ENTRIES = {
    "others": ("evalu",                        # "evaluation committees" (sul sito: "evalution")
               "department assembly",
               "review editor"),
}

# Rubriche sostituite da un riepilogo invece della lista delle voci.
SUMMARIZE = {"supervising"}

# Impaginazione compatta: righe brevi della stessa voce unite con virgole.
COMPACT = True
LONG_LINE = 110          # oltre questa lunghezza una riga va sempre a capo
OWN_LINE_PREFIXES = ("Thesis", "Essay", "Ref", "Supervisor", "Other lecturer",
                     "Course shared", "SSD", "Role", "Coordinators", "Section of",
                     "Subsection", "Member")

# Me stesso, per il grassetto nella bibliografia (deve combaciare con \mynames).
MY_FAMILY, MY_GIVEN = "Fachechi", "Alberto"

# Cognomi composti, così biblatex non li spezza.
COMPOUND_SURNAMES = ["Duarte Mourão", "Duarte Mourao", "Delle Cave", "Del Mercato",
                     "Franceschi Vento"]

MONTHS = {m: m[:3] for m in ["January", "February", "March", "April", "May", "June",
                              "July", "August", "September", "October", "November",
                              "December"]}
MONTHS.update({"Octobre": "Oct", "Sept": "Sep"})


# ---------------------------------------------------------------------------
# Lettura sorgenti
# ---------------------------------------------------------------------------

def load_page(name, source_dir=None, url=None):
    if url:
        req = urllib.request.Request(f"{url.rstrip('/')}/{name}",
                                     headers={"User-Agent": "build_cv.py"})
        with urllib.request.urlopen(req, timeout=30) as r:
            html = r.read().decode("utf-8")
    else:
        with open(os.path.join(source_dir, name), encoding="utf-8") as f:
            html = f.read()
    return BeautifulSoup(html, "html.parser")


def find_box(soup, title):
    """Restituisce il .box-content della box il cui h2.section-title è `title`."""
    for h2 in soup.select("h2.section-title"):
        if h2.get_text(strip=True) == title:
            box = h2.find_parent("div", class_="box")
            return box.find("div", class_="box-content")
    raise KeyError(f"Box '{title}' non trovata")


# ---------------------------------------------------------------------------
# HTML -> LaTeX
# ---------------------------------------------------------------------------

_SPECIALS = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
             "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
             "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
_MATH = re.compile(r"\\\((.+?)\\\)|\\\[(.+?)\\\]", re.S)


def escape_text(s):
    """Escape LaTeX, lasciando intatta la matematica MathJax \\( ... \\)."""
    out, pos = [], 0
    for m in _MATH.finditer(s):
        out.append("".join(_SPECIALS.get(c, c) for c in s[pos:m.start()]))
        out.append("$" + (m.group(1) or m.group(2)).strip() + "$")
        pos = m.end()
    out.append("".join(_SPECIALS.get(c, c) for c in s[pos:]))
    s = re.sub(r"\s+", " ", "".join(out))
    return re.sub(r'"([^"]*)"', r"``\1''", s)      # virgolette dritte -> LaTeX


def to_latex(node):
    """Converte ricorsivamente un nodo HTML (inline) in LaTeX."""
    if isinstance(node, Comment):
        return ""
    if isinstance(node, NavigableString):
        return escape_text(str(node))
    if not isinstance(node, Tag):
        return ""
    inner = "".join(to_latex(c) for c in node.children)
    name = node.name
    if name in ("b", "strong"):
        return r"\textbf{" + inner.strip() + "}"
    if name in ("i", "em"):
        return r"\emph{" + inner.strip() + "}"
    if name == "a" and node.get("href", "").startswith("http"):
        href = node["href"].replace("%", r"\%").replace("#", r"\#")
        return r"\href{" + href + "}{" + inner.strip() + "}"
    if name == "br":
        return " "
    return inner


def clean(s):
    return re.sub(r"\s+", " ", s).strip()


def fmt_date(s):
    s = clean(s)
    for full, short in MONTHS.items():
        s = re.sub(rf"\b{full}\b", short, s)
    s = re.sub(r"\s*-\s*", " -- ", s)          # trattini dei periodi
    s = s.replace("Today", "today")
    return escape_text(s)


# ---------------------------------------------------------------------------
# Liste "date-position-location-list"
# ---------------------------------------------------------------------------

def parse_entries(box):
    """
    Raggruppa gli <span> in voci: ogni span.date apre una voce nuova.
    Robusto agli <li> annidati/non chiusi presenti nell'HTML.
    """
    entries = []
    for span in box.find_all("span"):
        cls = span.get("class") or []
        if span.find_parent("span"):           # span annidati: già inclusi nel padre
            continue
        if "date" in cls:
            entries.append({"date": span.get_text(), "position": [], "lines": []})
        elif entries:
            target = "position" if "position" in cls else "lines"
            entries[-1][target].append(span)
    return entries


def entry_to_latex(e):
    parts = []
    for p in e["position"]:
        txt = clean(to_latex(p))
        if txt:
            parts.append(txt if txt.startswith(r"\textbf") else r"\textbf{" + txt + "}")
    # Le righe brevi consecutive (dipartimento, università, città, ...) vengono
    # unite con virgole; le righe "etichettate" o lunghe restano a capo.
    group = []
    for l in e["lines"]:
        txt = clean(to_latex(l))
        if not txt:
            continue
        plain = clean(l.get_text())
        own_line = (not COMPACT or len(plain) > LONG_LINE
                    or plain.startswith(OWN_LINE_PREFIXES))
        if own_line:
            if group:
                parts.append(", ".join(group))
                group = []
            parts.append(txt)
        else:
            group.append(txt.rstrip("."))
    if group:
        parts.append(", ".join(group))
    body = r"\par ".join(parts)
    return f"\\entry*[{fmt_date(e['date'])}]\n  {body}\n"


def apply_filters(fname, entries):
    drop_lines = DROP_LINES.get(fname, ())
    drop_entries = DROP_ENTRIES.get(fname, ())
    out = []
    for e in entries:
        pos = " ".join(clean(p.get_text()) for p in e["position"]).lower()
        if any(k in pos for k in drop_entries):
            continue
        e = dict(e, lines=[l for l in e["lines"]
                           if not clean(l.get_text()).startswith(drop_lines)])
        out.append(e)
    return out


_LEVELS = (("B.Sc.", "B.Sc."), ("M.Sc.", "M.Sc."), ("PhD", "Ph.D."))


def write_supervision_summary(fname, title, entries, warnings):
    """Conta le tesi (B.Sc./M.Sc./Ph.D.) seguite come supervisore o co-supervisore.
    Ogni studente è contato una sola volta per livello (sul sito alcune
    tesi compaiono con due periodi diversi). Gli ACU non sono tesi e sono esclusi."""
    seen, ongoing = {}, set()
    for e in entries:
        lines = [clean(l.get_text()) for l in e["lines"]]
        if not lines:
            continue
        student = lines[0]
        for code, label in _LEVELS:
            if any(re.search(rf"\b{re.escape(code)}\s+thesis", l) for l in lines):
                key = (student, label)
                if key in seen:
                    warnings.append(f"supervising: {student} ({label}) compare più "
                                    "volte sul sito, contato una volta")
                seen[key] = True
                if "today" in e["date"].lower():
                    ongoing.add(key)
                break
    counts = {label: sum(1 for (_, l) in seen if l == label) for _, label in _LEVELS}
    parts = [f"{n} {label}" for label, n in counts.items() if n]
    if len(parts) > 1:
        listing = ", ".join(parts[:-1]) + " and " + parts[-1]
    else:
        listing = parts[0] if parts else "0"
    total = sum(counts.values())
    text = (f"Supervisor or co-supervisor of {listing} {'theses' if total != 1 else 'thesis'}"
            + (f" ({len(ongoing)} ongoing)" if ongoing else "") + ".")
    with open(fname, "w", encoding="utf-8") as f:
        f.write("% Generato da build_cv.py — non modificare a mano\n"
                f"\\begin{{rubric}}{{{title}}}\n\\entry*[]\n  {text}\n\\end{{rubric}}\n")
    return text


def write_rubric(fname, title, sections):
    """sections: lista di (sottotitolo o None, voci)."""
    lines = [f"% Generato da build_cv.py — non modificare a mano\n",
             f"\\begin{{rubric}}{{{title}}}\n"]
    for sub, entries in sections:
        if sub:
            lines.append(f"\\subrubric{{{escape_text(sub)}}}\n")
        lines.extend(entry_to_latex(e) for e in entries)
    lines.append("\\end{rubric}\n")
    with open(fname, "w", encoding="utf-8") as f:
        f.writelines(lines)


# ---------------------------------------------------------------------------
# Rubriche speciali
# ---------------------------------------------------------------------------

def build_activity(index_soup):
    for c in index_soup.find_all(string=lambda t: isinstance(t, Comment)):
        if "FOR CV" in c:
            text = c.replace("FOR CV", "")
            paras = [escape_text(p) for p in re.split(r"\n\s*\n", text) if p.strip()]
            body = "\n\n".join(clean(p) for p in paras)
            with open("activity.tex", "w", encoding="utf-8") as f:
                # Niente pallino: \@prefix di curve è globale, quindi lo
                # svuoto per questa rubrica e lo ripristino subito dopo.
                f.write("% Generato da build_cv.py — non modificare a mano\n"
                        "\\makeatletter\\let\\cvsavedprefix\\@prefix\\makeatother\n"
                        "\\prefix{}\n"
                        f"\\begin{{rubric}}{{{ACTIVITY_TITLE}}}\n"
                        f"\\entry*[]\n  {body}\n\\end{{rubric}}\n"
                        "\\makeatletter\\global\\let\\@prefix\\cvsavedprefix\\makeatother\n")
            return
    raise KeyError("Commento 'FOR CV' non trovato in index.html")


def build_summary(pub_soup):
    box = find_box(pub_soup, "Summary of scientific production")
    rows = []
    for tr in box.select("table tr"):
        tds = tr.find_all("td")
        if len(tds) != 2:
            continue
        label = clean(to_latex(tds[0]))
        value = clean(tds[1].get_text())
        plain = re.sub(r"[^a-z0-9]", "", tds[0].get_text().lower())
        mark = plain in SCHOLAR_METRICS
        rows.append(f"\\entry*[{label}{'${}^1$' if mark else ''}] {escape_text(value)}\n")
    with open("summary.tex", "w", encoding="utf-8") as f:
        f.write("% Generato da build_cv.py — non modificare a mano\n"
                f"\\begin{{rubric}}{{{SUMMARY_TITLE}}}\n" + "".join(rows) +
                "\\end{rubric}\n")


# ---------------------------------------------------------------------------
# Pubblicazioni -> publications.bib + publications.tex
# ---------------------------------------------------------------------------

_DOI = re.compile(r"(10\.\d{4,9}/[^\s?#]+)")
_JOURNAL = re.compile(
    r"^(?P<journal>.+?)\s+(?P<volume>\d+)\s*(?:\((?P<number>\d+)\))?\s*,?\s*"
    r"(?P<pages>[A-Za-z]?\d[\w\-–]*)?\s*\((?P<year>\d{4})\)$")
_ARXIV = re.compile(r"arxiv[^0-9]*(\d{4}\.\d{4,5})", re.I)


bib_escape = escape_text


def split_name(full):
    full = clean(full)
    if MY_FAMILY in full:
        return f"{MY_FAMILY}, {MY_GIVEN}"
    for sur in COMPOUND_SURNAMES:
        if full.endswith(" " + sur):
            return f"{{{sur}}}, {initials(full[:-len(sur)].strip())}"
    parts = full.split(" ")
    if len(parts) == 1:
        return parts[0]
    return f"{parts[-1]}, {initials(' '.join(parts[:-1]))}"


def initials(given):
    """'J' -> 'J.', 'LF' -> 'L. F.', 'L L' -> 'L. L.'; i nomi per esteso restano."""
    out = []
    for tok in given.split():
        if tok.isalpha() and tok.isupper() and len(tok) <= 3:
            out.extend(c + "." for c in tok)
        else:
            out.append(tok)
    return " ".join(out)


def parse_authors(p):
    txt = clean(p.get_text(" "))
    names = [n for n in re.split(r",|\band\b", txt) if n.strip()]
    return " and ".join(split_name(n) for n in names)


def make_key(author_field, year, title, used):
    first = author_field.split(" and ")[0].split(",")[0].strip("{} ")
    first = unicodedata.normalize("NFKD", first).encode("ascii", "ignore").decode()
    word = next((w for w in re.findall(r"[A-Za-z]{4,}", title)), "paper")
    key = f"{first}{year}{word}".lower()
    base, i = key, 1
    while key in used:
        i += 1
        key = f"{base}{chr(96 + i)}"
    used.add(key)
    return key


def build_publications(pub_soup, warnings):
    items = pub_soup.select("div.publication-item")
    entries, used, last_year = [], set(), None
    for it in items:
        title = clean(it.find("p", class_="title").get_text())
        authors = parse_authors(it.find("p", class_="authors"))
        det = it.find("p", class_="journal-details")
        det_parts = [clean(x) for x in det.get_text("\n").split("\n") if clean(x)]
        details, note = det_parts[0], " ".join(det_parts[1:])
        a = it.select_one("p.url a")
        url = a["href"] if a else None
        f = {"author": authors, "title": "{" + bib_escape(title) + "}",
             "options": "maxnames=99"}   # mai "et al.": il mio nome deve comparire

        arx = _ARXIV.search(details)
        m = _JOURNAL.match(details)
        if arx:
            etype = "misc"
            eid = arx.group(1)
            year = "20" + eid[:2]
            f.update(eprint=eid, eprinttype="arxiv", howpublished="arXiv preprint")
        elif m:
            year = m["year"]
            venue = m["journal"].strip(" ,")
            if "International Conference" in venue:
                etype = "inproceedings"
                f["booktitle"] = bib_escape(venue)
            else:
                etype = "article"
                f["journaltitle"] = bib_escape(venue)
            f["volume"] = m["volume"]
            if m["number"]:
                f["number"] = m["number"]
            if m["pages"]:
                f["pages"] = m["pages"].replace("–", "-").replace("-", "--")
        else:
            etype = "article"
            f["journaltitle"] = bib_escape(details)
            year = last_year
            warnings.append(f"Pubblicazione senza volume/anno, anno dedotto ({year}): {title}")
        if year is None:
            year = "2000"
        last_year = year
        f["year"] = year

        if url:
            d = _DOI.search(url)
            if d:
                doi = re.sub(r"/(meta|full|abstract|pdf)$", "", d.group(1))
                f["doi"] = doi
            elif etype != "misc":
                f["url"] = url
        if note:
            f["note"] = bib_escape(note)

        key = make_key(authors, year, title, used)
        body = ",\n".join(f"  {k} = {{{v}}}" for k, v in f.items())
        entries.append(f"@{etype}{{{key},\n{body}\n}}\n")

    with open("publications.bib", "w", encoding="utf-8") as fh:
        fh.write("% Generato da build_cv.py — non modificare a mano\n\n" + "\n".join(entries))

    types = {e.split("{", 1)[0][1:] for e in entries}
    blocks = [r"\makerubrichead{Publications}", r"\nocite{*}"]
    for t, name in (("article", "Journal articles"),
                    ("inproceedings", "Conference proceedings"),
                    ("misc", "Preprints")):
        if t in types:
            blocks.append(rf"\printbibliography[heading=subbibliography,"
                          rf"title={{{name}}},type={t}]")
    with open("publications.tex", "w", encoding="utf-8") as fh:
        fh.write("% Generato da build_cv.py — non modificare a mano\n" +
                 "\n".join(blocks) + "\n")
    return len(entries)


# ---------------------------------------------------------------------------
# Compilazione
# ---------------------------------------------------------------------------

class BuildError(Exception):
    def __init__(self, cmd, output):
        super().__init__(" ".join(cmd))
        self.output = output


def run(cmd, ok=(0,)):
    print("  $", " ".join(cmd[:4]) + (" ..." if len(cmd) > 4 else ""))
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       text=True, encoding="utf-8", errors="replace")
    if r.returncode not in ok:
        raise BuildError(cmd, r.stdout)
    return r.stdout


def clean_aux(stem):
    """Rimuove gli ausiliari: un .bcf/.bbl vecchio (anche di un'altra
    installazione TeX, o committato nel repo) basta a far fallire biber."""
    for ext in ("aux", "bbl", "bcf", "blg", "run.xml", "out", "fls",
                "fdb_latexmk", "log"):
        try:
            os.remove(f"{stem}.{ext}")
        except FileNotFoundError:
            pass


def latex_passes(template, stem, backend):
    if backend == "bibtex":
        # Imposta backend=bibtex senza toccare il template.
        # maxnames globale: con bibtex l'opzione per-voce viene ignorata.
        src = (r"\PassOptionsToPackage{backend=bibtex,maxnames=99}{biblatex}"
               rf"\input{{{template}}}")
        latex = ["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
                 f"-jobname={stem}", src]
        bib = ["bibtex", stem]
    else:
        latex = ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", template]
        bib = ["biber", stem]
    run(latex)
    run(bib, ok=(0, 1) if backend == "bibtex" else (0,))   # bibtex: 1 = solo warning
    run(latex)
    run(latex)


def compile_cv(template, backend="auto"):
    stem = os.path.splitext(template)[0]
    clean_aux(stem)
    if backend in ("auto", "biber"):
        try:
            latex_passes(template, stem, "biber")
            print(f"PDF: {os.path.abspath(stem + '.pdf')}")
            return
        except BuildError as e:
            incompatible = "control file version" in e.output or "incompatible" in e.output
            if backend == "biber" or not incompatible:
                print(e.output[-3000:])
                sys.exit(f"Comando fallito: {e}")
            print("\nATTENZIONE: biber e biblatex installati hanno versioni incompatibili:")
            for line in e.output.splitlines():
                if "version" in line and ("ERROR" in line or "incompatible" in line):
                    print("   ", line.strip())
            print("  Ripiego sul backend bibtex. Per usare biber, allinea le versioni\n"
                  "  (vedi il commento in testa allo script).\n")
            clean_aux(stem)
    try:
        latex_passes(template, stem, "bibtex")
    except BuildError as e:
        print(e.output[-3000:])
        sys.exit(f"Comando fallito: {e}")
    print(f"PDF: {os.path.abspath(stem + '.pdf')}")


# ---------------------------------------------------------------------------

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", default=os.path.join(here, ".."),
                    help="cartella con le pagine HTML (default: cartella madre)")
    ap.add_argument("--url", nargs="?", const=SITE_URL, default=None,
                    help=f"scarica le pagine dal sito (default {SITE_URL})")
    ap.add_argument("--template", default=TEMPLATE)
    ap.add_argument("--no-compile", action="store_true")
    ap.add_argument("--backend", choices=("auto", "biber", "bibtex"), default="auto",
                    help="auto: biber, e se è incompatibile con biblatex ripiega su bibtex")
    args = ap.parse_args()

    os.chdir(here)
    src = dict(source_dir=os.path.abspath(args.source), url=args.url)
    print("Sorgente:", args.url or src["source_dir"])
    pages = {n: load_page(n, **src) for n in
             ("index.html", "cv.html", "teaching.html", "publications.html")}
    warnings = []

    build_activity(pages["index.html"])
    for fname, (title, boxes) in RUBRICS.items():
        if fname in DISABLED_RUBRICS:
            with open(f"{fname}.tex", "w", encoding="utf-8") as f:
                f.write("% Rubrica disattivata in build_cv.py (DISABLED_RUBRICS)\n")
            print(f"  {fname}.tex: disattivata")
            continue
        sections = []
        for b in boxes:
            page, box_title = b[0], b[1]
            sub = b[2] if len(b) > 2 else box_title
            try:
                entries = parse_entries(find_box(pages[page], box_title))
            except KeyError as e:
                warnings.append(f"{fname}: {e}")
                continue
            sections.append((sub if len(boxes) > 1 else None,
                             apply_filters(fname, entries)))
        if fname in SUMMARIZE:
            allentries = [e for _, es in sections for e in es]
            text = write_supervision_summary(f"{fname}.tex", title, allentries, warnings)
            print(f"  {fname}.tex: {text}")
            continue
        write_rubric(f"{fname}.tex", title, sections)
        print(f"  {fname}.tex: {sum(len(s[1]) for s in sections)} voci")
    build_summary(pages["publications.html"])
    n = build_publications(pages["publications.html"], warnings)
    print(f"  publications.bib: {n} voci")

    for w in warnings:
        print("ATTENZIONE:", w)
    if not args.no_compile:
        compile_cv(args.template, args.backend)


if __name__ == "__main__":
    main()
