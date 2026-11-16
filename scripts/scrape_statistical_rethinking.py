#!/usr/bin/env python3
"""Convert the "Statistical Rethinking" (2nd ed.) EPUB into agent-friendly markdown.

The EPUB is a bundle of XHTML documents: one per chapter, plus prefaces,
endnotes, bibliography and two term indexes.  This script turns them into a
directory tree that mirrors the convention used for ``bibliografia/bayes-rules``:

- one markdown file per chapter (``chapter-01-...`` .. ``chapter-17-...``),
- ``00-frontmatter.md`` with the copyright page and both prefaces,
- ``50-endnotes.md`` and ``60-bibliography.md`` for the back matter,
- ``indice.md`` with metadata, a chapter map and a curated concept index,
- ``full.md`` with every chapter concatenated, for global ``grep``,
- ``images/`` with the figures referenced by the text.

Conversion details that matter for the EPUB edition:

- the equations are MathML with a JPG fallback (``altimg``).  They are converted
  to LaTeX (``$...$`` / ``$$...$$``); if a construct cannot be converted the
  original image is linked instead and the failure is reported,
- consecutive equation+label tables are merged into a single ``aligned`` block,
- R code lives in ``div.pre`` blocks; code inside ``div.box``/``div.box1`` is
  tagged ``r``, free-standing blocks are tagged ``r`` or ``text`` (R output),
- R "Rethinking"/"Overthinking" boxes become blockquotes,
- fake bullets (``p.bullt``) and numbered paragraphs (``p.numlistb``) become
  real markdown lists,
- subsections printed as bold paragraphs (``2.2.1. A data story.``) are promoted
  to ``###`` headings with the original ``secN_M`` anchor,
- endnotes live at the end of the book; they are inlined per chapter as
  ``[^N.M]`` footnotes (so each chapter is self-contained) and also listed in
  ``50-endnotes.md``.

Usage:
    python scripts/scrape_statistical_rethinking.py [--out-dir DIR] [--only N,N]
        [--no-images] [--epub PATH]

Requires: beautifulsoup4, markdownify (both declared in pyproject.toml).
"""

from __future__ import annotations

import argparse
import posixpath
import re
import sys
import unicodedata
import zipfile
from datetime import date
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag
from markdownify import markdownify as html_to_md

DEFAULT_EPUB = (
    "/home/matias/Database/files/Books/Statistics/Bayes/"
    "McElreath, Richard_ - Statistical Rethinking_ A Bayesian Course with "
    "Examples in R and STAN-CRC Press LLC (2020).epub"
)

BOOK_TITLE = "Statistical Rethinking: A Bayesian Course with Examples in R and Stan"
BOOK_AUTHOR = "Richard McElreath"
BOOK_EDITION = "2nd edition (CRC Press, 2020)"

# Curated concept -> chapter map, so an agent can jump to a topic directly.
TOPICS = [
    ("Bayesian vs. frequentist inference; models as golems", "1"),
    ("Small worlds vs. large worlds; garden of forking data", "2"),
    ("Bayes' theorem as counting ways; prior and likelihood", "2"),
    ("Grid approximation and posterior sampling", "2, 3"),
    ("Sampling from the posterior; compatibility/credible intervals", "3"),
    ("HPDI, PI, point estimates and uncertainty", "3"),
    ("Posterior predictive simulation (sim)", "3"),
    ("Normal/Gaussian model and its maximum entropy justification", "4"),
    ("Linear regression, priors for alpha/beta/sigma", "4"),
    ("Polynomial and spline regression", "4"),
    ("Multiple regression; multicollinearity, post-treatment bias, colliders", "5, 6"),
    ("DAGs and causal inference; the haunted DAG", "6"),
    ("Information criteria: WAIC, PSIS, LOO, ELPD", "7"),
    ("Regularization priors and model comparison", "7"),
    ("Interactions in regression; categorical interactions", "8"),
    ("Markov chain Monte Carlo; Metropolis and Hamiltonian MC", "9"),
    ("NUTS, ulam, warmup, chains, ESS, R-hat, divergences", "9"),
    ("Maximum entropy and the generalized linear model", "10"),
    ("Link functions, linear models on other scales", "10"),
    ("Binomial (logistic) regression with logit link", "11"),
    ("Poisson regression with log link and offsets", "11"),
    ("Aggregated vs. disaggregated binomial data", "11"),
    ("Overdispersion; beta-binomial and gamma-Poisson models", "12"),
    ("Zero-inflated and hurdle models", "12"),
    ("Ordered categorical and mixture models", "12"),
    ("Multilevel models; varying intercepts and partial pooling", "13"),
    ("Shrinkage, pooling and clusters/populations", "13"),
    ("Varying slopes and correlated varying effects", "14"),
    ("Gaussian processes and phylogenetic regression", "14, 16"),
    ("Missing data; Bayesian imputation", "15"),
    ("Measurement error and latent variables", "15"),
    ("Categorical predictors and errors, misclassification", "15"),
    ("Survival analysis; hazards and censoring", "16"),
    ("Generalized linear madness; non-linear models", "16"),
    ("Model criticism, ethics and the limits of statistics", "17"),
    ("The rethinking R package: quap, ulam, precis, link, sim", "preface, 2, 4"),
    ("Practice exercises per chapter", "every chapter (last section)"),
]


# --------------------------------------------------------------------------
# MathML -> LaTeX
# --------------------------------------------------------------------------

GREEK = {
    "α": r"\alpha", "β": r"\beta", "γ": r"\gamma", "δ": r"\delta",
    "ε": r"\epsilon", "ϵ": r"\epsilon", "ζ": r"\zeta", "η": r"\eta",
    "θ": r"\theta", "ϑ": r"\vartheta", "ι": r"\iota", "κ": r"\kappa",
    "λ": r"\lambda", "μ": r"\mu", "ν": r"\nu", "ξ": r"\xi", "π": r"\pi",
    "ρ": r"\rho", "σ": r"\sigma", "ς": r"\varsigma", "τ": r"\tau",
    "υ": r"\upsilon", "φ": r"\phi", "ϕ": r"\phi", "χ": r"\chi",
    "ψ": r"\psi", "ω": r"\omega", "Γ": r"\Gamma", "Δ": r"\Delta",
    "Θ": r"\Theta", "Λ": r"\Lambda", "Ξ": r"\Xi", "Π": r"\Pi",
    "Σ": r"\Sigma", "Υ": r"\Upsilon", "Φ": r"\Phi", "Ψ": r"\Psi",
    "Ω": r"\Omega",
}

OP_MAP = {
    "−": "-", "–": "-", "×": r"\times", "·": r"\cdot", "∗": "*",
    "∝": r"\propto", "≈": r"\approx", "≤": r"\leq", "≥": r"\geq",
    "≠": r"\neq", "→": r"\to", "←": r"\leftarrow", "∈": r"\in",
    "∞": r"\infty", "∑": r"\sum", "∫": r"\int", "∏": r"\prod",
    "∂": r"\partial", "∼": r"\sim", "~": r"\sim", "±": r"\pm",
    "…": r"\dots", "⋯": r"\cdots", "≡": r"\equiv", "⊂": r"\subset",
    "∪": r"\cup", "∩": r"\cap", "∅": r"\emptyset", "∵": r"\because",
    "∴": r"\therefore", "′": "'", "″": "''", "∘": r"\circ",
    "∣": "|", "|": "|", "∶": ":", "√": r"\sqrt",
}

SPACED = {
    "=", "+", "-", "<", ">", "*", r"\times", r"\cdot", r"\propto",
    r"\approx", r"\leq", r"\geq", r"\neq", r"\to", r"\leftarrow",
    r"\in", r"\sim", r"\pm", r"\equiv", r"\subset", r"\cup", r"\cap",
    r"\because", r"\therefore",
}

ACCENTS = {
    "^": r"\hat", "ˆ": r"\hat", "¯": r"\bar", "‾": r"\bar",
    "˙": r"\dot", "¨": r"\ddot", "→": r"\vec", "~": r"\tilde",
    "˜": r"\tilde", "ˇ": r"\check", "´": r"\acute", "`": r"\grave",
}

TEXT_ESCAPES = {
    "\\": r"\textbackslash{}", "{": r"\{", "}": r"\}", "%": r"\%",
    "#": r"\#", "&": r"\&", "_": r"\_", "$": r"\$", "^": r"\^{}",
    "~": r"\~{}",
}


def _tex_text(text: str) -> str:
    return "".join(TEXT_ESCAPES.get(ch, ch) for ch in text)


def _clean_text(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    return text.replace("\u00a0", " ").replace("\u2003", " ").replace("\u2009", " ")


def _mi(el: Tag) -> str:
    text = _clean_text(el.get_text())
    text = unicodedata.normalize("NFKC", text).strip()
    if not text:
        return ""
    if len(text) == 1:
        if text in GREEK:
            return GREEK[text]
        if text.isalpha() or text.isdigit():
            return text
        if text in OP_MAP:
            return OP_MAP[text]
    if text in {"log", "exp", "ln", "max", "min"}:
        return "\\" + text
    if re.fullmatch(r"[A-Za-z][A-Za-z0-9]*", text):
        return rf"\mathrm{{{text}}}"
    return rf"\text{{{_tex_text(text)}}}"


def _mn(el: Tag) -> str:
    return unicodedata.normalize("NFKC", _clean_text(el.get_text())).strip()


def _mo(el: Tag) -> str:
    raw = unicodedata.normalize("NFC", _clean_text(el.get_text())).strip()
    if not raw:
        return ""
    if raw in OP_MAP:
        op = OP_MAP[raw]
    elif len(raw) == 1 and (raw.isalpha() or raw.isdigit()):
        op = GREEK.get(raw, raw)
    else:
        op = _tex_text(raw)
    if op in SPACED:
        return f" {op} "
    if op == ",":
        return ","
    return op


def _mfrac(el: Tag) -> str:
    parts = [c for c in el.find_all(recursive=False)]
    if len(parts) != 2:
        return _math_children(el)
    return rf"\frac{{{_math_node(parts[0])}}}{{{_math_node(parts[1])}}}"


def _msqrt(el: Tag) -> str:
    return rf"\sqrt{{{_math_children(el)}}}"


def _mroot(el: Tag) -> str:
    parts = [c for c in el.find_all(recursive=False)]
    if len(parts) != 2:
        return _math_children(el)
    return rf"\sqrt[{_math_node(parts[1])}]{{{_math_node(parts[0])}}}"


def _mtable(el: Tag) -> str:
    rows = []
    for row in el.find_all(["mtr", "mlabeledtr"], recursive=False):
        cells = [_math_children(cell) for cell in row.find_all("mtd", recursive=False)]
        rows.append(" & ".join(cells))
    if not rows:
        return _math_children(el)
    if len(rows) == 1 and " & " not in rows[0]:
        return rows[0]
    body = r" \\ ".join(rows)
    return rf"\begin{{aligned}}{body}\end{{aligned}}"


def _msub(el: Tag) -> str:
    parts = [c for c in el.find_all(recursive=False)]
    if len(parts) != 2:
        return _math_children(el)
    return f"{_math_node(parts[0])}_{{{_math_node(parts[1])}}}"


def _msup(el: Tag) -> str:
    parts = [c for c in el.find_all(recursive=False)]
    if len(parts) != 2:
        return _math_children(el)
    return f"{_math_node(parts[0])}^{{{_math_node(parts[1])}}}"


def _msubsup(el: Tag) -> str:
    parts = [c for c in el.find_all(recursive=False)]
    if len(parts) != 3:
        return _math_children(el)
    return (
        f"{_math_node(parts[0])}_{{{_math_node(parts[1])}}}"
        f"^{{{_math_node(parts[2])}}}"
    )


def _mover(el: Tag) -> str:
    parts = [c for c in el.find_all(recursive=False)]
    if len(parts) != 2:
        return _math_children(el)
    base, over = parts
    accent = (over.name == "mo" and len(_clean_text(over.get_text()).strip()) == 1)
    symbol = _clean_text(over.get_text()).strip()
    if accent and symbol in ACCENTS:
        return f"{ACCENTS[symbol]}{{{_math_node(base)}}}"
    return rf"\overset{{{_math_node(over)}}}{{{_math_node(base)}}}"


def _munder(el: Tag) -> str:
    parts = [c for c in el.find_all(recursive=False)]
    if len(parts) != 2:
        return _math_children(el)
    base, under = parts
    symbol = _clean_text(under.get_text()).strip()
    base_tex = _math_node(base)
    if symbol in {"_", "‾", "¯"} or el.get("accentunder") == "true":
        return rf"\underline{{{base_tex}}}"
    if base_tex in {r"\sum", r"\prod", r"\int", r"\max", r"\min", r"\lim"}:
        return f"{base_tex}_{{{_math_node(under)}}}"
    return rf"\underset{{{_math_node(under)}}}{{{base_tex}}}"


def _munderover(el: Tag) -> str:
    parts = [c for c in el.find_all(recursive=False)]
    if len(parts) != 3:
        return _math_children(el)
    base, under, over = parts
    base_tex = _math_node(base)
    if base_tex in {r"\sum", r"\prod", r"\int", r"\max", r"\min", r"\lim"}:
        return (
            f"{base_tex}_{{{_math_node(under)}}}"
            f"^{{{_math_node(over)}}}"
        )
    return (
        rf"\underset{{{_math_node(under)}}}"
        rf"{{\overset{{{_math_node(over)}}}{{{base_tex}}}}}"
    )


def _mtext(el: Tag) -> str:
    text = _clean_text(el.get_text()).strip()
    if text in {"log", "exp", "ln", "max", "min"}:
        return "\\" + text
    return rf"\text{{{_tex_text(text)}}}"


def _menclose(el: Tag) -> str:
    notation = el.get("notation") or ""
    inner = _math_children(el)
    if "updiagonalstrike" in notation or "downdiagonalstrike" in notation:
        return rf"\cancel{{{inner}}}"
    if "box" in notation or "roundedbox" in notation:
        return rf"\boxed{{{inner}}}"
    return inner


UNKNOWN_INLINE = {"mstyle", "mpadded", "merror", "mphantom", "mprescripts", "none"}


def _math_node(node) -> str:
    if isinstance(node, NavigableString):
        return _tex_text(str(node).strip())
    if not isinstance(node, Tag):
        return ""
    name = node.name.lower()
    if name == "mi":
        return _mi(node)
    if name == "mn":
        return _mn(node)
    if name == "mo":
        return _mo(node)
    if name == "mtext":
        return _mtext(node)
    if name == "mfrac":
        return _mfrac(node)
    if name == "msqrt":
        return _msqrt(node)
    if name == "mroot":
        return _mroot(node)
    if name == "mtable":
        return _mtable(node)
    if name == "msub":
        return _msub(node)
    if name == "msup":
        return _msup(node)
    if name == "msubsup":
        return _msubsup(node)
    if name == "mover":
        return _mover(node)
    if name == "munder":
        return _munder(node)
    if name == "munderover":
        return _munderover(node)
    if name == "menclose":
        return _menclose(node)
    if name == "mspace":
        return r"\ "
    if name == "malignmark":
        return ""
    if name == "semantics":
        first = node.find(recursive=False)
        return _math_node(first) if first is not None else ""
    if name in {"annotation", "annotation-xml"}:
        return ""
    if name in UNKNOWN_INLINE or name in {"mrow", "math", "mtd", "mtr"}:
        return _math_children(node)
    if name.startswith("m"):
        return _math_children(node)
    return _math_children(node)


def _math_children(el: Tag) -> str:
    parts = [_math_node(child) for child in el.children]
    out = ""
    for part in parts:
        if not part:
            continue
        if out and part[0].isalpha() and re.search(r"\\[A-Za-z]+$", out):
            out += " "
        out += part
    return out


def _space_control_word(match: re.Match) -> str:
    """Append a space to a control word that is directly followed by a letter."""
    following = match.string[match.end() : match.end() + 1]
    return match.group(0) + (" " if following.isalpha() else "")


def mathml_to_latex(el: Tag) -> str:
    """Convert a MathML <math> element to a LaTeX string (without $ delimiters)."""
    tex = _math_children(el)
    tex = re.sub(r"\s+", " ", tex).strip()
    # Drop redundant braces around single tokens: {p} -> p is NOT safe in
    # general (it changes sub/superscript grouping), so only trim outer spaces.
    tex = re.sub(r"\s*([,;:])\s*", r"\1 ", tex)
    # Some equations split a single word across consecutive <mtext> nodes
    # ("Normal(0, 1" + ".5)"); glue them back together first.
    for _ in range(3):
        tex = re.sub(r"\\text\{([^{}]*)\}\s*\\text\{([^{}]*)\}", r"\\text{\1\2}", tex)
    # Keep words separated: "\text{ways}p" -> "\text{ways} p".
    tex = re.sub(r"((?:\\(?:text|mathrm)\{[^{}]*\}))(?=[A-Za-z0-9\\])", r"\1 ", tex)
    tex = re.sub(r"(?<=[A-Za-z0-9])(\\(?:text|mathrm)\{)", r" \1", tex)
    # Never glue a control word to a following letter: "\beta" + "x" -> "\beta x".
    tex = re.sub(r"\\[A-Za-z]+", _space_control_word, tex)
    tex = re.sub(r" +", " ", tex)
    return tex.strip()


# --------------------------------------------------------------------------
# EPUB container
# --------------------------------------------------------------------------


class Epub:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.zip = zipfile.ZipFile(path)
        container = BeautifulSoup(self.read("META-INF/container.xml"), "html.parser")
        rootfile = container.find("rootfile")
        if rootfile is None:
            raise RuntimeError("container.xml has no rootfile")
        self.opf_path = rootfile["full-path"]
        opf = BeautifulSoup(self.read(self.opf_path), "html.parser")
        base = posixpath.dirname(self.opf_path)
        manifest = {}
        for item in opf.find_all("item"):
            if item.get("id") and item.get("href"):
                manifest[item["id"]] = posixpath.normpath(
                    posixpath.join(base, item["href"])
                )
        spine = opf.find("spine")
        if spine is None:
            raise RuntimeError("OPF has no spine")
        self.spine = [
            manifest[ref["idref"]]
            for ref in spine.find_all("itemref")
            if ref.get("idref") in manifest
        ]
        self.names = set(self.zip.namelist())

    def read(self, name: str) -> str:
        return self.zip.read(name).decode("utf-8", errors="replace")

    def read_bytes(self, name: str) -> bytes:
        return self.zip.read(name)


class ImageStore:
    """Writes only the images actually referenced by the text."""

    def __init__(self, epub: Epub, out_dir: Path, enabled: bool) -> None:
        self.epub = epub
        self.dir = out_dir / "images"
        self.enabled = enabled
        self.written: set[str] = set()
        self.missing: set[str] = set()

    def add(self, doc_path: str, src: str) -> str | None:
        if not self.enabled or not src:
            return None
        target = posixpath.normpath(posixpath.join(posixpath.dirname(doc_path), src))
        name = posixpath.basename(target)
        if target not in self.epub.names:
            self.missing.add(target)
            return None
        if name not in self.written:
            self.dir.mkdir(parents=True, exist_ok=True)
            (self.dir / name).write_bytes(self.epub.read_bytes(target))
            self.written.add(name)
        return f"images/{name}"


# --------------------------------------------------------------------------
# HTML -> markdown conversion for one document
# --------------------------------------------------------------------------


def collapse(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def next_tag(node: Tag) -> Tag | None:
    sibling = node.next_sibling
    while sibling is not None and not isinstance(sibling, Tag):
        sibling = sibling.next_sibling
    return sibling if isinstance(sibling, Tag) else None


def fence(text: str, language: str) -> str:
    marker = "```"
    while marker in text:
        marker += "`"
    return f"{marker}{language}\n{text.rstrip()}\n{marker}\n"


R_CALL = re.compile(
    r"^\s*(library|require|data|set\.seed|quap|ulam|precis|pairs|plot|sim|link|"
    r"rethinking|dnorm|rnorm|runif|sample|seq|rep|sapply|replicate|print|hist|"
    r"dens|curve|abline|points|mtext|concat|rangi2|col\.alpha|expand\.grid)\s*\("
)


def looks_like_r(text: str) -> bool:
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return False
    if "<-" in text or any(line.lstrip().startswith("#") for line in lines):
        return True
    return any(R_CALL.match(line) for line in lines)


class Converter:
    def __init__(
        self,
        root: Tag,
        doc_path: str,
        images: ImageStore,
        path_map: dict[str, str],
        uid: int,
    ) -> None:
        self.root = root
        self.doc_path = doc_path
        self.images = images
        self.path_map = path_map
        self.uid = uid
        self.placeholders: dict[str, str] = {}
        self.block_keys: set[str] = set()
        self.code_boxes: set[int] = set()
        self.equations_ok = 0
        self.equations_failed: list[str] = []

    # -- placeholders ----------------------------------------------------
    def hold(self, markdown: str, block: bool = False) -> str:
        key = f"@@PH{self.uid}{len(self.placeholders):04d}@@"
        self.placeholders[key] = markdown
        if block:
            self.block_keys.add(key)
        return key

    def expand(self, markdown: str) -> str:
        for _ in range(6):
            if not any(key in markdown for key in self.placeholders):
                break
            for key, value in self.placeholders.items():
                markdown = markdown.replace(key, value)
        return markdown

    def anchor(self, anchor_id: str | None) -> str:
        if not anchor_id:
            return ""
        return f'<a id="{anchor_id}"></a>'

    def image_markdown(self, img: Tag) -> str:
        alt = collapse(img.get("alt") or "")
        if alt.lower() == "image":
            alt = ""
        target = self.images.add(self.doc_path, img.get("src", ""))
        if target is None:
            return ""
        return f"![{alt}]({target})"

    # -- prepare ---------------------------------------------------------
    def prepare(self) -> None:
        root = self.root
        self._strip_noise(root)
        self._footnote_refs(root)
        self._sup_sub(root)
        self._rewrite_links(root)
        self._anchors(root)
        self._equation_tables(root)
        self._math(root)
        self._figures(root)
        self._inline_images(root)
        self._boxheads(root)
        self._code(root)
        self._lists(root)
        self._subheadings(root)
        self._headings(root)
        self._tables(root)
        self._boxes(root)
        self._whitespace(root)

    def _strip_noise(self, root: Tag) -> None:
        for tag in root.find_all(["script", "style", "link", "meta"]):
            tag.decompose()
        for span in root.find_all("span"):
            if span.attrs.get("epub:type") == "pagebreak":
                span.decompose()

    def _footnote_refs(self, root: Tag) -> None:
        for link in root.find_all("a", id=re.compile(r"^rfn")):
            match = re.match(r"^rfn(\d+)_(\d+)$", link["id"])
            if not match:
                continue
            chapter, number = match.groups()
            link.replace_with(NavigableString(f"[^{chapter}.{number}]"))

    def _sup_sub(self, root: Tag) -> None:
        for tag in list(root.find_all(["sup", "sub"])):
            text = collapse(tag.get_text(""))
            if not text:
                tag.decompose()
                continue
            marker = "^" if tag.name == "sup" else "_"
            tag.replace_with(NavigableString(self.hold(f"{marker}{{{text}}}")))

    def _rewrite_links(self, root: Tag) -> None:
        for link in root.find_all("a", href=True):
            href = link["href"]
            if href.startswith(("http://", "https://", "mailto:")):
                continue
            base, _, fragment = href.partition("#")
            target = self.path_map.get(posixpath.basename(base)) if base else None
            if target:
                link["href"] = target + (f"#{fragment}" if fragment else "")
            elif not base:
                continue
            else:
                del link["href"]

    def _anchors(self, root: Tag) -> None:
        for section in root.find_all("section", id=True):
            section.insert(0, NavigableString(self.hold(self.anchor(section["id"]))))
        for link in root.find_all("a", id=True):
            anchor = self.hold(self.anchor(link["id"]))
            heading = link.find_parent(["h1", "h2", "h3", "h4"])
            if heading is not None:
                heading.insert_before(NavigableString(anchor))
            else:
                link.insert_before(NavigableString(anchor))
            link.unwrap()

    # -- equations -------------------------------------------------------
    def _equation_tables(self, root: Tag) -> None:
        parents: list[Tag] = []
        for table in root.find_all("table"):
            parent = table.parent
            if isinstance(parent, Tag) and parent not in parents:
                parents.append(parent)
        for parent in parents:
            self._merge_equation_tables(parent)

    @staticmethod
    def _is_equation_table(tag) -> bool:
        if not isinstance(tag, Tag) or tag.name != "table":
            return False
        if "table1" not in (tag.get("class") or []):
            return False
        return tag.find("p", class_="eqn") is not None

    def _merge_equation_tables(self, parent: Tag) -> None:
        run: list[Tag] = []
        for child in list(parent.children) + [None]:
            if self._is_equation_table(child):
                run.append(child)
                continue
            if not run:
                continue
            if isinstance(child, NavigableString) and not str(child).strip():
                continue
            self._render_equation_run(run)
            run = []

    def _render_equation_run(self, tables: list[Tag]) -> None:
        entries: list[tuple[str | None, str, Tag]] = []
        for table in tables:
            for equation in table.find_all("p", class_="eqn"):
                math = equation.find("math")
                latex = None
                if math is not None:
                    try:
                        latex = mathml_to_latex(math)
                    except Exception:  # pragma: no cover - defensive
                        latex = None
                label_el = table.find("p", class_="eqnr")
                label = collapse(label_el.get_text(" ")) if label_el else ""
                entries.append((latex, label, table))
                break  # one equation per layout table in this edition

        failed = any(latex is None for latex, _, _ in entries)
        if failed:
            blocks = []
            for latex, label, table in entries:
                if latex is not None:
                    self.equations_ok += 1
                    text = latex + (f" \\qquad {_label_tex(label)}" if label else "")
                    blocks.append(f"$$\n{text}\n$$")
                    continue
                self.equations_failed.append(self.doc_path)
                math = table.find("math")
                alt = math.get("altimg") if math is not None else None
                target = self.images.add(self.doc_path, alt or "") if alt else None
                if target:
                    blocks.append(f"![equation]({target})")
                elif label:
                    blocks.append(f"*[equation: {label}]*")
            replacement = "\n\n".join(blocks)
        elif len(entries) == 1:
            latex, label, _ = entries[0]
            self.equations_ok += 1
            text = latex + (f" \\qquad {_label_tex(label)}" if label else "")
            replacement = f"$$\n{text}\n$$"
        else:
            rows = []
            for latex, label, _ in entries:
                assert latex is not None
                self.equations_ok += 1
                row = latex
                if label:
                    row += f" && {_label_tex(label)}"
                rows.append(row)
            body = " \\\\\n".join(rows)
            replacement = f"$$\n\\begin{{aligned}}\n{body}\n\\end{{aligned}}\n$$"

        first = tables[0]
        first.insert_before(
            NavigableString("\n\n" + self.hold(replacement, block=True) + "\n\n")
        )
        for table in tables:
            table.decompose()

    def _math(self, root: Tag) -> None:
        for math in list(root.find_all("math")):
            if math.parent is None:
                continue
            display = math.find_parent("p", class_="eqn") is not None
            try:
                latex = mathml_to_latex(math)
            except Exception:  # pragma: no cover - defensive
                latex = ""
            if not latex:
                self.equations_failed.append(self.doc_path)
                alt = math.get("altimg")
                target = self.images.add(self.doc_path, alt or "") if alt else None
                if target:
                    math.replace_with(NavigableString(self.hold(f"![equation]({target})")))
                else:
                    math.decompose()
                continue
            self.equations_ok += 1
            if display:
                math.replace_with(
                    NavigableString(
                        self.hold(f"\n\n$$\n{latex}\n$$\n\n", block=True)
                    )
                )
            else:
                math.replace_with(NavigableString(self.hold(f"${latex}$")))

    # -- figures and images ---------------------------------------------
    def _figures(self, root: Tag) -> None:
        for figure in root.find_all("figure"):
            parts = []
            if figure.get("id"):
                parts.append(self.anchor(figure["id"]))
            img = figure.find("img")
            if img is not None:
                markdown = self.image_markdown(img)
                if markdown:
                    parts.append(markdown)
            caption = figure.find("figcaption")
            if caption is not None:
                text = collapse(caption.get_text(""))
                text = re.sub(
                    r"^(FIGURE|TABLE)\s*([\d.]+)\s*[.:]\s*", r"**\1 \2.** ", text
                )
                if not text.startswith("**"):
                    text = f"*{text}*"
                parts.append(text)
            block = "\n\n".join(part for part in parts if part)
            figure.replace_with(
                NavigableString("\n\n" + self.hold(block, block=True) + "\n\n")
            )

    def _inline_images(self, root: Tag) -> None:
        for img in root.find_all("img"):
            markdown = self.image_markdown(img)
            img.replace_with(NavigableString(self.hold(markdown)))

    # -- code ------------------------------------------------------------
    def _boxheads(self, root: Tag) -> None:
        for head in root.find_all("p", class_="boxhead"):
            label = collapse(head.get_text(" "))
            following = next_tag(head)
            if following is not None and following.name == "div" and (
                {"box", "box1"} & set(following.get("class") or [])
            ):
                following.insert_before(
                    NavigableString(self.hold(f"**{label}**\n\n", block=True))
                )
                head.decompose()
            else:
                head.replace_with(NavigableString(self.hold(f"**{label}**", block=True)))

    def _code(self, root: Tag) -> None:
        for box in root.find_all("div"):
            if {"box", "box1"} & set(box.get("class") or []):
                if box.find("div", class_="pre") is not None:
                    self.code_boxes.add(id(box))
        for block in list(root.find_all("div", class_="pre")):
            if block.parent is None:
                continue
            text = self._pre_text(block)
            if not text.strip():
                block.decompose()
                continue
            inside_box = block.find_parent("div", class_=["box", "box1"]) is not None
            language = "r" if inside_box or looks_like_r(text) else "text"
            block.replace_with(
                NavigableString(self.hold("\n\n" + fence(text, language) + "\n", block=True))
            )

    @staticmethod
    def _pre_text(block: Tag) -> str:
        lines = []
        for paragraph in block.find_all("p"):
            text = paragraph.get_text()
            text = text.replace("\u2003", "  ").replace("\u00a0", " ")
            lines.append(text.rstrip())
        if not lines:
            text = block.get_text()
            text = text.replace("\u2003", "  ").replace("\u00a0", " ")
            return text.rstrip("\n")
        return "\n".join(lines)

    # -- containers ------------------------------------------------------
    def _lists(self, root: Tag) -> None:
        for div in list(root.find_all("div")):
            classes = set(div.get("class") or [])
            if "ulist" in classes:
                items = [self._list_item(p, bullet=True) for p in div.find_all("p")]
                items = [item for item in items if item]
                if items:
                    block = "\n".join(f"- {item}" for item in items)
                    div.replace_with(
                        NavigableString("\n\n" + self.hold(block, block=True) + "\n\n")
                    )
                else:
                    div.decompose()
            elif "olist" in classes:
                items = [self._list_item(p, bullet=False) for p in div.find_all("p")]
                items = [item for item in items if item]
                if items:
                    block = "\n".join(
                        f"{index}. {item}" for index, item in enumerate(items, 1)
                    )
                    div.replace_with(
                        NavigableString("\n\n" + self.hold(block, block=True) + "\n\n")
                    )
                else:
                    div.decompose()

        for paragraph in list(root.find_all("p", class_=["bullt", "bull"])):
            item = self._list_item(paragraph, bullet=True)
            if item:
                paragraph.replace_with(
                    NavigableString("\n\n" + self.hold(f"- {item}", block=True) + "\n\n")
                )
            else:
                paragraph.decompose()

    @staticmethod
    def _list_item(paragraph: Tag, bullet: bool) -> str:
        html = paragraph.decode_contents()
        markdown = html_to_md(html, heading_style="ATX").strip()
        markdown = collapse(markdown)
        if bullet:
            markdown = re.sub(r"^[•·]\s*", "", markdown)
        else:
            markdown = re.sub(r"^\((\d+)\)\s*", "", markdown)
        return markdown

    def _boxes(self, root: Tag) -> None:
        for box in list(root.find_all("div")):
            if not ({"box", "box1"} & set(box.get("class") or [])):
                continue
            if id(box) in self.code_boxes:
                continue
            if box.find(["table", "figure", "div"]) is not None:
                continue
            text = self.expand(html_to_md(str(box), heading_style="ATX")).strip()
            if not text:
                box.decompose()
                continue
            lines = [line.rstrip() for line in text.split("\n")]
            quoted = "\n".join(f"> {line}".rstrip() if line else ">" for line in lines)
            quoted = re.sub(r"\n(>\n)+", "\n>\n", quoted).strip()
            box.replace_with(
                NavigableString("\n\n" + self.hold(quoted, block=True) + "\n\n")
            )

    # -- headings --------------------------------------------------------
    def _subheadings(self, root: Tag) -> None:
        pattern = re.compile(r"^(\d+\.\d+\.\d+\.)\s*(.+)$")
        for paragraph in list(root.find_all("p")):
            bold = paragraph.find("b")
            if bold is None or bold.parent is not paragraph:
                continue
            title = collapse(bold.get_text(" "))
            match = pattern.match(title)
            if not match:
                continue
            heading = self.root_soup().new_tag("h3")
            heading.string = collapse(f"{match.group(1)} {match.group(2)}").rstrip(".")
            paragraph.insert_before(heading)
            bold.extract()
            if not collapse(paragraph.get_text(" ")):
                paragraph.decompose()

    def root_soup(self) -> BeautifulSoup:
        return self.root if isinstance(self.root, BeautifulSoup) else self.root.find_parent()

    def _headings(self, root: Tag) -> None:
        chapter = root.find("h1", class_="chno")
        if chapter is not None:
            number = chapter.find("span", class_="big")
            title = collapse(chapter.get_text(" "))
            if number is not None:
                digits = collapse(number.get_text(" "))
                number.extract()
                title = collapse(chapter.get_text(" "))
                title = re.sub(r"^\d+\s*", "", title)
                chapter.clear()
                chapter.append(NavigableString(f"{digits}. {title}"))
        for heading in root.find_all("h2", class_="fmtitle"):
            heading.name = "h1"
        for heading in root.find_all("h1", class_="head1"):
            heading.name = "h2"

    # -- data tables -----------------------------------------------------
    def _tables(self, root: Tag) -> None:
        for table in list(root.find_all("table")):
            markdown = self._table_markdown(table)
            if markdown:
                table.replace_with(
                    NavigableString("\n\n" + self.hold(markdown, block=True) + "\n\n")
                )
            else:
                table.decompose()

    def _table_markdown(self, table: Tag) -> str:
        rows: list[list[str]] = []
        header: list[str] | None = None
        head = table.find("thead")
        if head is not None:
            head_row = head.find("tr")
            if head_row is not None:
                header = self._table_row(head_row)
        body = table.find("tbody") or table
        for row in body.find_all("tr"):
            if head is not None and row.find_parent("thead") is not None:
                continue
            rows.append(self._table_row(row))
        rows = [row for row in rows if any(cell for cell in row)]
        if not rows and not header:
            return ""
        if header is None:
            header, rows = rows[0], rows[1:]
        width = max([len(header)] + [len(row) for row in rows]) if header else 0
        if width == 0:
            return ""
        header = header + [""] * (width - len(header))
        lines = [
            "| " + " | ".join(header) + " |",
            "| " + " | ".join("---" for _ in range(width)) + " |",
        ]
        for row in rows:
            row = row + [""] * (width - len(row))
            lines.append("| " + " | ".join(row) + " |")
        return "\n".join(lines)

    def _table_row(self, row: Tag) -> list[str]:
        cells = []
        for cell in row.find_all(["td", "th"], recursive=False):
            text = self.expand(html_to_md(self._cell_html(cell), heading_style="ATX"))
            text = re.sub(r"\s+", " ", text).strip()
            text = text.replace("|", r"\|")
            cells.append(text)
        return cells

    @staticmethod
    def _cell_html(cell: Tag) -> str:
        # The EPUB wraps every cell in <p class="tab1">; unwrap it so the
        # markdown does not get a spurious paragraph break.
        clone = BeautifulSoup(cell.decode_contents(), "html.parser")
        for paragraph in clone.find_all("p"):
            paragraph.unwrap()
        return clone.decode()

    # -- whitespace ------------------------------------------------------
    def _whitespace(self, root: Tag) -> None:
        for node in root.find_all(string=True):
            parent = node.parent
            if parent is None:
                continue
            if parent.name in {"pre", "code", "script", "style"}:
                continue
            if parent.find_parent("div", class_="pre") is not None:
                continue
            text = str(node)
            collapsed = re.sub(r"[ \t\r\n\u00a0\u2002\u2003\u2009]+", " ", text)
            if collapsed != text:
                node.replace_with(NavigableString(collapsed))

    # -- render ----------------------------------------------------------
    def to_markdown(self) -> str:
        markdown = html_to_md(str(self.root), heading_style="ATX", bullets="-")
        # markdownify collapses the whitespace between sibling text nodes, so
        # block placeholders can end up glued together on one line.  Force a
        # blank line around every block placeholder before expanding.
        for key in self.block_keys:
            markdown = re.sub(
                rf"[ \t]*{re.escape(key)}[ \t]*", f"\n\n{key}\n\n", markdown
            )
        markdown = self.expand(markdown)
        markdown = re.sub(r"[ \t]+\n", "\n", markdown)
        markdown = re.sub(r"\n{3,}", "\n\n", markdown)
        return markdown.strip() + "\n"


def _label_tex(label: str) -> str:
    label = label.strip().strip("[]").strip()
    return rf"\text{{[{_tex_text(label)}]}}"


# --------------------------------------------------------------------------
# Book metadata
# --------------------------------------------------------------------------


class Doc:
    def __init__(self, path: str, html: str) -> None:
        self.path = path
        self.name = posixpath.basename(path)
        self.soup = BeautifulSoup(html, "html.parser")
        self.body = self.soup.body or self.soup
        self.kind = "skip"
        self.chapter: int | None = None
        self.title = ""
        self.file = ""
        self.sections: list[dict] = []
        self.summary = ""
        self._classify()

    def _classify(self) -> None:
        name = self.name
        match = re.match(r"^\d+_Chapter(\d+)\.xhtml$", name)
        if match:
            self.kind = "chapter"
            self.chapter = int(match.group(1))
            self.title = self._chapter_title()
            return
        if name == "26_Endnotes.xhtml":
            self.kind = "endnotes"
            self.title = "Endnotes"
            return
        if name == "27_Bibliography.xhtml":
            self.kind = "bibliography"
            self.title = "Bibliography"
            return
        if name == "06_Contents.xhtml":
            self.kind = "contents"
            self.title = "Contents"
            return
        if name.startswith("05_Copyright"):
            self.kind = "front"
            self.title = "Copyright"
            return
        if name.startswith("07_Preface") or name.startswith("08_Preface"):
            self.kind = "front"
            heading = self.body.find(["h1", "h2"], class_="fmtitle")
            self.title = collapse(heading.get_text(" ")) if heading else "Preface"
            return

    def _chapter_title(self) -> str:
        heading = self.body.find("h1", class_="chno")
        if heading is None:
            return f"Chapter {self.chapter}"
        clone = BeautifulSoup(str(heading), "html.parser")
        number = clone.find("span", class_="big")
        if number is not None:
            number.extract()
        title = collapse(clone.get_text(" "))
        title = re.sub(r"^\d+\s*", "", title)
        return title or f"Chapter {self.chapter}"

    def collect_metadata(self) -> None:
        """Sections and summary, read before the DOM is mutated."""
        if self.kind in {"chapter", "front"}:
            self.sections = self._sections()
        if self.kind == "chapter":
            self.summary = self._summary()

    def _sections(self) -> list[dict]:
        sections = []
        for node in self.body.find_all(["h1", "h2", "p"]):
            if node.name == "p":
                bold = node.find("b")
                if bold is None or bold.parent is not node:
                    continue
                match = re.match(
                    r"^(\d+\.\d+\.\d+\.)\s*(.+)$", collapse(bold.get_text(" "))
                )
                if not match:
                    continue
                section = node.find_parent("section")
                anchor_id = section.get("id") if section else ""
                if not anchor_id:
                    continue
                sections.append(
                    {
                        "level": 4,
                        "id": anchor_id,
                        "title": collapse(
                            f"{match.group(1)} {match.group(2)}"
                        ).rstrip("."),
                    }
                )
                continue
            classes = set(node.get("class") or [])
            if "chno" in classes or "fmtitle" in classes:
                continue
            if "head1" not in classes and "head2" not in classes:
                continue
            anchor = node.find("a", id=True)
            anchor_id = anchor["id"] if anchor else node.get("id")
            if not anchor_id:
                section = node.find_parent("section")
                anchor_id = section.get("id") if section else ""
            if not anchor_id:
                continue
            sections.append(
                {
                    "level": 3,
                    "id": anchor_id,
                    "title": collapse(node.get_text(" ")),
                }
            )
        return sections

    def _summary(self) -> str:
        for heading in self.body.find_all("h2", class_="head2"):
            if not collapse(heading.get_text(" ")).lower().endswith("summary"):
                continue
            paragraph = heading.find_next("p")
            if paragraph is None:
                continue
            text = collapse(paragraph.get_text(" "))
            if len(text) >= 80:
                return _truncate(text)
        for paragraph in self.body.find_all("p"):
            text = collapse(paragraph.get_text(" "))
            if len(text) > 120 and paragraph.find_parent("figure") is None:
                return _truncate(text)
        return ""


def _truncate(text: str, limit: int = 260) -> str:
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = text.rstrip(" ,;:.")
    if len(text) <= limit:
        return text
    cut = text[:limit]
    return cut[: cut.rfind(" ")].rstrip(" ,;:.") + " ..."


def slugify(title: str) -> str:
    text = unicodedata.normalize("NFKD", title)
    text = text.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


# --------------------------------------------------------------------------
# Endnotes
# --------------------------------------------------------------------------


def parse_notes(doc: Doc, images: ImageStore, path_map: dict[str, str]) -> dict[str, str]:
    """Return {note_id: markdown} for the book-end notes."""
    notes: dict[str, str] = {}
    uid = 9000
    for paragraph in doc.body.find_all("p", class_="note"):
        anchor = paragraph.find("a", id=re.compile(r"^fn\d+_\d+$"))
        note_id = (anchor["id"] if anchor is not None else paragraph.get("id")) or ""
        match = re.match(r"^fn(\d+)_(\d+)$", note_id)
        if not match:
            continue
        clone = BeautifulSoup(str(paragraph), "html.parser")
        clone_paragraph = clone.find("p")
        if clone_paragraph is None:
            continue
        anchor = clone_paragraph.find("a", id=re.compile(r"^fn"))
        if anchor is not None:
            anchor.decompose()
        converter = Converter(clone_paragraph, doc.path, images, path_map, uid)
        uid += 1
        converter.prepare()
        text = converter.to_markdown()
        text = re.sub(r"^[\s.]*(?:\d+\.)?[\s.]*", "", text.strip())
        text = re.sub(r"\s+\[\d+\]\s*$", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            continue
        notes[note_id] = text
    return notes


# --------------------------------------------------------------------------
# Writers
# --------------------------------------------------------------------------


def yaml_quote(text: str) -> str:
    return text.replace('"', "'")


def chapter_with_notes(doc: Doc, body: str, notes: dict[str, str]) -> str:
    chapter_notes = {
        key: value
        for key, value in notes.items()
        if key.startswith(f"fn{doc.chapter}_")
    }
    if not chapter_notes:
        return body
    ordered = sorted(chapter_notes, key=lambda key: int(key.split("_")[1]))
    lines = ["", "---", "", "## Notes", ""]
    for key in ordered:
        number = key.split("_")[1]
        lines.append(f"[^{doc.chapter}.{number}]: {chapter_notes[key]}")
        lines.append("")
    return body.rstrip() + "\n" + "\n".join(lines)


def write_chapter(doc: Doc, body: str, notes: dict[str, str], out_dir: Path) -> None:
    body = chapter_with_notes(doc, body, notes)

    sections = "\n".join(f'  - "{yaml_quote(s["title"])}"' for s in doc.sections)
    frontmatter = (
        "---\n"
        f'title: "{yaml_quote(doc.title)}"\n'
        f"chapter: {doc.chapter}\n"
        'part: ""\n'
        "sections:\n"
        f"{sections or '  []'}\n"
        f'source: "EPUB: {yaml_quote(Path(DEFAULT_EPUB).name)} — {doc.name}"\n'
        f'book: "{BOOK_TITLE}"\n'
        f'author: "{BOOK_AUTHOR}"\n'
        f'edition: "{BOOK_EDITION}"\n'
        'license: "Copia personal para estudio (CRC Press, sin licencia abierta)"\n'
        "---\n\n"
    )
    (out_dir / doc.file).write_text(frontmatter + body, encoding="utf-8")


def write_frontmatter(docs: list[Doc], bodies: dict[str, str], out_dir: Path) -> None:
    parts = []
    for doc in docs:
        parts.append(f'<a id="front-{slugify(doc.title)}"></a>\n\n' + bodies[doc.name])
    text = (
        "---\n"
        'title: "Front matter (copyright, prefaces)"\n'
        f'book: "{BOOK_TITLE}"\n'
        f'author: "{BOOK_AUTHOR}"\n'
        f'edition: "{BOOK_EDITION}"\n'
        'license: "Copia personal para estudio (CRC Press, sin licencia abierta)"\n'
        "---\n\n" + "\n\n---\n\n".join(parts)
    )
    (out_dir / "00-frontmatter.md").write_text(text, encoding="utf-8")


def write_endnotes(notes: dict[str, str], out_dir: Path) -> None:
    lines = [
        "---",
        'title: "Endnotes"',
        f'book: "{BOOK_TITLE}"',
        f'author: "{BOOK_AUTHOR}"',
        'license: "Copia personal para estudio (CRC Press, sin licencia abierta)"',
        "---",
        "",
        "# Endnotes",
        "",
        "The notes are also inlined as `[^N.M]` footnotes at the end of each",
        "chapter file, so this list is only a convenience for global search.",
        "",
    ]
    current = None
    for key in sorted(notes, key=lambda k: (int(k.split("_")[0][2:]), int(k.split("_")[1]))):
        chapter = int(key.split("_")[0][2:])
        number = int(key.split("_")[1])
        if chapter != current:
            current = chapter
            lines.extend(["", f"## Chapter {chapter}", ""])
        lines.append(f"{number}. {notes[key]}")
    (out_dir / "50-endnotes.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_bibliography(body: str, out_dir: Path) -> None:
    text = (
        "---\n"
        'title: "Bibliography"\n'
        f'book: "{BOOK_TITLE}"\n'
        f'author: "{BOOK_AUTHOR}"\n'
        f'edition: "{BOOK_EDITION}"\n'
        'license: "Copia personal para estudio (CRC Press, sin licencia abierta)"\n'
        "---\n\n" + body
    )
    (out_dir / "60-bibliography.md").write_text(text, encoding="utf-8")


def write_index(chapters: list[Doc], front: list[Doc], out_dir: Path) -> None:
    generated = date.today().isoformat()
    lines: list[str] = []
    add = lines.append
    add(f"# {BOOK_TITLE}")
    add("")
    add(f"> Author: {BOOK_AUTHOR}  ")
    add(f"> Edition: {BOOK_EDITION}  ")
    add("> Source: local EPUB copy (CRC Press). No open license: personal study copy.  ")
    add(f"> Local markdown tree generated on {generated} for personal study.")
    add("")
    add("This directory is an offline, agent-readable copy of the book: one file")
    add("per chapter, plus this index. Cross-references, equation labels and")
    add("anchors from the original EPUB are preserved.")
    add("")
    add("## How to navigate this copy")
    add("")
    add("1. Read this index to locate the topic you need.")
    add("2. Open the chapter file listed below (~10-25k tokens each).")
    add(
        "3. Jump to a section with its anchor, e.g. "
        "`chapter-09-markov-chain-monte-carlo.md#sec9_2`."
    )
    add("4. For a global search, use `rg -n \"term\" full.md`.")
    add("")
    add("Conventions:")
    add("")
    add("- Inline math uses `$...$`, display math `$$...$$` (LaTeX converted from MathML).")
    add("- Equations that could not be converted keep the original image and are reported by the script.")
    add("- `**FIGURE x.y.**` lines are figure captions; images live in `images/`.")
    add("- R code is fenced ``` ```r ```; R output is fenced ``` ```text ```.")
    add("- `Rethinking:` / `Overthinking:` boxes are blockquotes.")
    add("- `<a id=\"...\"></a>` lines are the original EPUB anchors (`sec9_2`, `ch9`, ...).")
    add("- Book-end notes are inlined as `[^N.M]` footnotes at the end of each chapter.")
    add("")
    add("## Files")
    add("")
    add("| File | Contents |")
    add("| --- | --- |")
    add("| `00-frontmatter.md` | Copyright page and both prefaces |")
    for doc in chapters:
        add(f'| `{doc.file}` | Chapter {doc.chapter}. {doc.title} |')
    add("| `50-endnotes.md` | All endnotes, grouped by chapter |")
    add("| `60-bibliography.md` | Full bibliography |")
    add("| `full.md` | Every chapter concatenated, for global grep |")
    add("")
    add("## Chapters at a glance")
    add("")
    add("| # | Chapter | Summary (from the book) |")
    add("| --- | --- | --- |")
    for doc in chapters:
        summary = (doc.summary or "").replace("|", "\\|")
        add(f"| {doc.chapter} | [{doc.title}]({doc.file}) | {summary} |")
    add("")
    add("## Detailed table of contents")
    add("")
    if front:
        add("### Front matter")
        add("")
        for doc in front:
            add(f'**{doc.title}** — [00-frontmatter.md](00-frontmatter.md)')
            add("")
            for section in doc.sections:
                add(
                    f'- [{section["title"]}](00-frontmatter.md#{section["id"]})'
                )
            add("")
    for doc in chapters:
        add(f"**{doc.chapter}. [{doc.title}]({doc.file})**")
        add("")
        for section in doc.sections:
            indent = "  " if section["level"] == 4 else ""
            add(f'{indent}- [{section["title"]}]({doc.file}#{section["id"]})')
        add("")
    add("### Back matter")
    add("")
    add("- [Endnotes](50-endnotes.md)")
    add("- [Bibliography](60-bibliography.md)")
    add("")
    add("## Concept index")
    add("")
    add("Curated topic -> chapter map, for jumping straight to a subject.")
    add("")
    add("| Topic | Chapter(s) |")
    add("| --- | --- |")
    chapter_by_number = {doc.chapter: doc for doc in chapters}
    front_default = "00-frontmatter.md"
    for topic, chapters_text in TOPICS:
        links = []
        for token in re.findall(r"\d+|preface", chapters_text):
            if token == "preface":
                links.append(f"[preface]({front_default})")
                continue
            doc = chapter_by_number.get(int(token))
            links.append(f"[{token}]({doc.file})" if doc else token)
        if not links:
            links.append(chapters_text)
        add(f"| {topic} | {', '.join(links)} |")
    add("")
    add("## Usage notes for agents")
    add("")
    add("- Chapter order follows the book: 1-2 foundations, 3-4 sampling and")
    add("  Gaussian models, 5-8 regression and causal traps, 9 MCMC, 10-12 GLMs,")
    add("  13-14 multilevel models, 15 missing data, 16 survival/phylogeny,")
    add("  17 closing essay.")
    add("- Every chapter ends with a `Practice` section with the book exercises.")
    add("- The `rethinking` R package is the companion software; `quap` and `ulam`")
    add("  are introduced in the preface and developed through chapters 2-16.")
    (out_dir / "indice.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_full(chapters: list[Doc], bodies: dict[str, str], out_dir: Path) -> None:
    parts = [
        f'<a id="chapter-{doc.chapter}"></a>\n\n' + bodies[doc.name].rstrip()
        for doc in chapters
    ]
    text = (
        f"# {BOOK_TITLE} (full text)\n\n"
        f"Author: {BOOK_AUTHOR} · {BOOK_EDITION}\n\n"
        "Personal study copy (CRC Press). Generated from a local EPUB.\n\n---\n\n"
        + "\n\n---\n\n".join(parts)
    )
    (out_dir / "full.md").write_text(text, encoding="utf-8")


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--epub", default=DEFAULT_EPUB, help="Path to the EPUB file")
    parser.add_argument(
        "--out-dir",
        default="bibliografia/statistical-rethinking",
        help="Output directory",
    )
    parser.add_argument(
        "--only",
        default="",
        help="Comma separated chapter numbers to convert, e.g. 2,9",
    )
    parser.add_argument("--no-images", action="store_true", help="Skip image extraction")
    args = parser.parse_args()

    epub_path = Path(args.epub).expanduser()
    if not epub_path.exists():
        raise SystemExit(f"EPUB not found: {epub_path}")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    epub = Epub(epub_path)

    docs = [Doc(path, epub.read(path)) for path in epub.spine]
    docs = [doc for doc in docs if doc.kind != "skip"]

    contents = next((doc for doc in docs if doc.kind == "contents"), None)
    chapters = sorted(
        (doc for doc in docs if doc.kind == "chapter"), key=lambda doc: doc.chapter
    )
    front = [doc for doc in docs if doc.kind == "front"]
    endnotes_doc = next((doc for doc in docs if doc.kind == "endnotes"), None)
    bibliography_doc = next((doc for doc in docs if doc.kind == "bibliography"), None)

    selected = [int(token) for token in re.findall(r"\d+", args.only)]
    if selected:
        chapters = [doc for doc in chapters if doc.chapter in selected]

    for doc in chapters:
        doc.file = f"chapter-{doc.chapter:02d}-{slugify(doc.title)}.md"
    for doc in front:
        doc.file = "00-frontmatter.md"
    if endnotes_doc is not None:
        endnotes_doc.file = "50-endnotes.md"
    if bibliography_doc is not None:
        bibliography_doc.file = "60-bibliography.md"
    if contents is not None:
        contents.file = "indice.md"

    path_map = {doc.name: doc.file for doc in docs if doc.file}

    for doc in chapters + front:
        doc.collect_metadata()

    images = ImageStore(epub, out_dir, enabled=not args.no_images)
    notes: dict[str, str] = {}
    if endnotes_doc is not None:
        notes = parse_notes(endnotes_doc, images, path_map)
        print(f"  endnotes: {len(notes)} notes parsed")

    bodies: dict[str, str] = {}
    equations_ok = 0
    equation_failures: list[str] = []
    uid = 1
    for doc in chapters + front:
        converter = Converter(doc.body, doc.path, images, path_map, uid)
        uid += 1
        converter.prepare()
        body = converter.to_markdown()
        bodies[doc.name] = body
        equations_ok += converter.equations_ok
        equation_failures.extend(converter.equations_failed)
        if doc.kind == "chapter":
            write_chapter(doc, body, notes, out_dir)
            print(
                f"  chapter {doc.chapter:>2}: {doc.file} "
                f"({len(body):>7} bytes)"
            )
        else:
            print(f"  front: {doc.title} ({len(body)} bytes)")

    if front:
        write_frontmatter(front, bodies, out_dir)
        print("  frontmatter: 00-frontmatter.md")

    if endnotes_doc is not None:
        write_endnotes(notes, out_dir)
        print("  endnotes: 50-endnotes.md")

    if bibliography_doc is not None:
        converter = Converter(bibliography_doc.body, bibliography_doc.path, images, path_map, 8000)
        converter.prepare()
        write_bibliography(converter.to_markdown(), out_dir)
        print("  bibliography: 60-bibliography.md")

    if chapters:
        write_index(chapters, front, out_dir)
        full_bodies = {
            doc.name: chapter_with_notes(doc, bodies[doc.name], notes)
            for doc in chapters
        }
        write_full(chapters, full_bodies, out_dir)
        print(f"  index: {out_dir / 'indice.md'}")
        print(f"  full: {out_dir / 'full.md'}")

    print(
        f"\nDone: {len(chapters)} chapters, {equations_ok} equations converted, "
        f"{len(equation_failures)} fallbacks, {len(images.written)} images"
    )
    if images.missing:
        print(f"Missing images: {len(images.missing)}")
    if equation_failures:
        print("Equation fallbacks in:", ", ".join(sorted(set(equation_failures))))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
