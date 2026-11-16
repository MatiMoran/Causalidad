#!/usr/bin/env python3
"""Scrape bayesrulesbook.com into an agent-friendly markdown tree.

The online edition of "Bayes Rules! An Introduction to Applied Bayesian
Modeling" (Johnson, Ott & Dogucu, CC BY-NC-SA 4.0) is a bookdown site with one
HTML page per chapter. This script converts those pages into one markdown file
per chapter plus an ``indice.md`` map, preserving:

- heading hierarchy (H1/H2/H3) and the original section anchors,
- LaTeX math as ``$...$`` / ``$$...$$``,
- R code blocks with their language tag,
- tables as GFM pipe tables,
- figure captions and alt text, with images downloaded locally,
- intra-book links rewritten to the local files.

Usage:
    python scripts/scrape_bayes_rules.py [--out-dir DIR] [--force] [--only PAGES]

Requires: requests, beautifulsoup4, markdownify.
"""

from __future__ import annotations

import argparse
import re
import sys
import time
import urllib.parse
from datetime import date
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup, NavigableString, Tag
    from markdownify import markdownify as html_to_md
except ModuleNotFoundError as exc:  # pragma: no cover
    raise SystemExit(f"Missing dependency '{exc.name}'. Install it with: poetry install") from exc
BASE_URL = "https://www.bayesrulesbook.com"
USER_AGENT = "bayes-rules-offline-copy/1.0 (personal study archive)"

CHAPTERS = [f"/chapter-{i}" for i in range(1, 20)]
FRONT_MATTER = ["/foreword", "/preface", "/about-the-authors"]
PAGES = FRONT_MATTER + CHAPTERS + ["/references"]

# Book units as printed in the table of contents.
PARTS = [
    (1, 5, "I. Bayesian Foundations"),
    (6, 8, "II. Posterior Simulation & Analysis"),
    (9, 14, "III. Bayesian Regression & Classification"),
    (15, 19, "IV. Hierarchical Bayesian Models"),
]

# Curated concept -> chapter map. Keeps the index useful for an agent that
# needs to jump straight to a topic instead of guessing chapter numbers.
TOPICS = [
    ("Bayesian vs frequentist philosophy", "1"),
    ("Probability as plausibility; prior / data / posterior", "1, 2"),
    ("Bayes' rule for events and random variables", "2"),
    ("Beta-Binomial model", "3"),
    ("Prior tuning, balance and sequential updating", "4"),
    ("Conjugate families: Gamma-Poisson, Normal-Normal", "5"),
    ("Grid approximation", "6"),
    ("MCMC with rstan / Stan", "6, 7"),
    ("MCMC diagnostics: trace plots, ESS, R-hat", "6"),
    ("Metropolis-Hastings algorithm", "7"),
    ("Posterior estimation and credible intervals", "8"),
    ("Posterior hypothesis testing (one- and two-sided)", "8"),
    ("Posterior prediction", "8"),
    ("Simple Normal regression", "9"),
    ("rstanarm and default priors", "9"),
    ("Model checking and posterior predictive checks", "10"),
    ("Cross-validation and ELPD", "10, 11"),
    ("Multiple predictors, categorical predictors, interactions", "11"),
    ("Bias-variance trade-off", "11, 16"),
    ("Poisson and Negative Binomial regression", "12"),
    ("Logistic regression, odds and probabilities", "13"),
    ("Classification and naive Bayes", "14"),
    ("Complete / no / partial pooling", "15, 16"),
    ("Hierarchical models and shrinkage", "15, 16, 17"),
    ("Varying intercepts and slopes", "17"),
    ("Group-level predictors and multiple grouping variables", "19"),
    ("Data availability and ethics", "3"),
    ("Datasets from the bayesrules R package", "preface"),
]


class Converter:
    """HTML -> markdown conversion for one book page."""

    def __init__(self, soup: BeautifulSoup, content: Tag, page_path: str, images_dir: Path,
                 image_subdir: str, download_images: bool, session: requests.Session,
                 force: bool) -> None:
        self.soup = soup
        self.content = content
        self.page_path = page_path
        self.images_dir = images_dir
        self.image_subdir = image_subdir
        self.download_images = download_images
        self.session = session
        self.force = force
        self.placeholders: dict[str, str] = {}
        self.used_anchors: set[str] = set()
        self.image_count = 0

    # -- helpers ---------------------------------------------------------
    def hold(self, markdown: str) -> str:
        key = f"@@PH{len(self.placeholders):04d}@@"
        self.placeholders[key] = markdown
        return key

    def anchor(self, anchor_id: str | None) -> str:
        if not anchor_id or anchor_id in self.used_anchors:
            return ""
        self.used_anchors.add(anchor_id)
        return self.hold(f'<a id="{anchor_id}"></a>')

    def image_markdown(self, img: Tag) -> str:
        src = img.get("src", "")
        alt = (img.get("alt") or "").strip()
        if not src:
            return ""
        absolute = urllib.parse.urljoin(BASE_URL + self.page_path, src)
        if self.download_images:
            name = Path(urllib.parse.urlparse(absolute).path).name
            dest = self.images_dir / self.image_subdir / name
            if self.force or not dest.exists():
                dest.parent.mkdir(parents=True, exist_ok=True)
                response = self.session.get(absolute, timeout=60)
                response.raise_for_status()
                dest.write_bytes(response.content)
                time.sleep(0.1)
            self.image_count += 1
            target = f"images/{self.image_subdir}/{name}"
        else:
            target = absolute
        return f"![{alt}]({target})"

    # -- pre-pass --------------------------------------------------------
    def prepare(self, content: Tag) -> None:
        for tag in content.select("script, style, .navigation, a.footnote-back"):
            tag.decompose()

        self._normalize_whitespace(content)
        self._convert_math(content)
        self._convert_figures(content)
        self._insert_anchors(content)
        self._convert_goals(content)

    @staticmethod
    def _normalize_whitespace(content: Tag) -> None:
        """HTML collapses whitespace; markdownify copies source newlines, which
        would split every paragraph into one line per sentence."""
        for node in content.find_all(string=True):
            if node.parent and node.parent.name in ("pre", "code", "script", "style"):
                continue
            collapsed = re.sub(r"\s+", " ", str(node))
            if collapsed != str(node):
                node.replace_with(NavigableString(collapsed))

    def _convert_figures(self, content: Tag) -> None:
        for figure in content.select("div.figure"):
            img = figure.find("img")
            caption = figure.find("p", class_="caption")
            span = figure.find("span", id=True)
            parts = []
            if span is not None:
                parts.append(self.anchor(span.get("id")))
            if img is not None:
                parts.append(self.image_markdown(img))
            if caption is not None:
                text = caption.get_text(" ", strip=True)
                text = re.sub(r"^(FIGURE|TABLE)\s+([\d.]+):\s*", lambda m: f"**{m.group(1)} {m.group(2)}:** ", text)
                parts.append(text)
            block = "\n\n".join(p for p in parts if p)
            figure.replace_with(NavigableString("\n\n" + self.hold(block) + "\n\n"))

        # Inline images that are not wrapped in a figure block.
        for img in content.find_all("img"):
            markdown = self.image_markdown(img)
            if markdown:
                img.replace_with(NavigableString(self.hold(markdown)))

    def _convert_math(self, content: Tag) -> None:
        for span in content.select("span.math"):
            classes = span.get("class") or []
            tex = span.get_text()
            if "display" in classes:
                inner = tex.strip()
                if inner.startswith("\\[") and inner.endswith("\\]"):
                    inner = inner[2:-2]
                inner = inner.replace("\\begin{equation}", "").replace("\\end{equation}", "").strip()
                anchor = self.anchor(span.get("id"))
                prefix = f"\n\n{anchor}\n\n" if anchor else "\n\n"
                span.replace_with(NavigableString(self.hold(f"{prefix}$$\n{inner}\n$$\n\n")))
            else:
                inner = tex.strip()
                if inner.startswith("\\(") and inner.endswith("\\)"):
                    inner = inner[2:-2]
                span.replace_with(NavigableString(self.hold(f"${inner.strip()}$")))

    def _insert_anchors(self, content: Tag) -> None:
        # Section anchors: bookdown uses custom ids such as
        # "bayes-v-freq-probability", so GitHub's slugified headings are not
        # enough to keep cross-references working.
        for section in content.select("div.section[id]"):
            marker = self.soup.new_tag("p")
            marker.string = self.anchor(section["id"])
            section.insert(0, marker)

        # Table caption anchors (e.g. #tab:disease-population).
        for table in content.find_all("table"):
            caption = table.find("caption")
            if caption is None:
                continue
            span = caption.find("span", id=True)
            if span is None:
                continue
            marker = self.soup.new_tag("p")
            marker.string = self.anchor(span["id"])
            table.insert_before(marker)

        # Footnote anchors so in-text [1](#fn1) links resolve locally.
        for item in content.select('li[id^="fn"]'):
            item.insert(0, NavigableString(self.anchor(item["id"])))

        # Remaining inline anchors (exercise numbers such as #exr:ch3-tuning).
        # Skip the per-line code anchors (cb273-7) that bookdown emits: they
        # would end up as literal text inside fenced code blocks.
        for span in content.select("span[id]"):
            if span.find_parent(["pre", "code"]):
                continue
            marker = self.anchor(span["id"])
            if marker:
                span.insert(0, NavigableString(marker))

    def _convert_goals(self, content: Tag) -> None:
        for div in content.select("div.goals"):
            label = self.soup.new_tag("p")
            strong = self.soup.new_tag("strong")
            strong.string = "Learning goals"
            label.append(strong)
            div.insert(0, label)

    # -- render ----------------------------------------------------------
    def to_markdown(self) -> str:
        def language(el: Tag) -> str:
            for css in el.get("class") or []:
                if css not in ("sourceCode", "numberLines"):
                    return css
            return ""

        markdown = html_to_md(
            str(self.content),
            heading_style="ATX",
            bullets="*",
            code_language_callback=language,
        )

        # Restore held markdown (math, figures, anchors). Values may contain
        # other placeholders, so iterate until stable.
        for _ in range(6):
            if not any(key in markdown for key in self.placeholders):
                break
            for key, value in self.placeholders.items():
                markdown = markdown.replace(key, value)

        markdown = re.sub(r"[ \t]+\n", "\n", markdown)
        # Table captions come through as plain text; match the figure style.
        markdown = re.sub(r"^(TABLE|FIGURE) (\d+\.\d+): ", r"**\1 \2:** ", markdown, flags=re.MULTILINE)
        markdown = re.sub(r"\n{3,}", "\n\n", markdown)
        return markdown.strip() + "\n"


def fetch(session: requests.Session, path: str, cache_dir: Path, force: bool,
          delay: float) -> str:
    name = "index" if path == "/" else path.strip("/").replace("/", "_")
    cache_file = cache_dir / f"{name}.html"
    if cache_file.exists() and not force:
        return cache_file.read_text(encoding="utf-8")
    url = BASE_URL + path if path != "/" else BASE_URL + "/"
    response = session.get(url, timeout=60)
    response.raise_for_status()
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(response.text, encoding="utf-8")
    time.sleep(delay)
    return response.text


def slugify(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def parse_page(html: str) -> tuple[BeautifulSoup, Tag]:
    soup = BeautifulSoup(html, "html.parser")
    content = soup.select_one("div.page-inner")
    if content is None:
        raise RuntimeError("page-inner container not found")
    return soup, content


def page_metadata(content: Tag) -> tuple[str, list[dict]]:
    heading = content.find("h1")
    raw_title = heading.get_text(" ", strip=True) if heading else ""
    title = re.sub(r"^Chapter\s+\d+\s*", "", raw_title).strip()
    sections = []
    for div in content.select("div.section.level2[id], div.section.level3[id]"):
        head = div.find(["h2", "h3"])
        if head is None:
            continue
        sections.append({
            "level": int(head.name[1]),
            "id": div["id"],
            "title": head.get_text(" ", strip=True),
        })
    return title or raw_title, sections


def _summary_text(block: Tag) -> str:
    """Plain-ish text for index summaries: inline math stays readable, display
    math is dropped (it would be unreadable inside a markdown table cell)."""
    clone = BeautifulSoup(str(block), "html.parser")
    label = clone.find("strong")
    for span in clone.select("span.math"):
        classes = span.get("class") or []
        tex = span.get_text().strip()
        if "display" in classes:
            span.replace_with(NavigableString(""))
            continue
        if tex.startswith("\\(") and tex.endswith("\\)"):
            tex = tex[2:-2]
        span.replace_with(NavigableString(f"${tex.strip()}$"))
    text = clone.get_text(" ", strip=True)
    text = re.sub(r"\s+([.,;:)\]。])", r"\1", text)
    text = re.sub(r"\(\s+", "(", text)
    text = re.sub(r"\s+", " ", text).strip()
    # "Prior influence The less vague..." reads better as "Prior influence: ...".
    if label is not None:
        lab = label.get_text(" ", strip=True)
        if lab and text.startswith(lab) and not lab.endswith((":", ".", "?", "!")):
            text = lab + ": " + text[len(lab):].lstrip()
    return text


def chapter_summary(content: Tag) -> str:
    """One-line summary taken from the chapter's own summary section."""
    for div in content.select("div.section[id]"):
        if not div["id"].startswith("chapter-summary"):
            continue
        candidates = [_summary_text(b) for b in div.find_all(["p", "li"])]
        candidates = [c for c in candidates if len(c) >= 80]
        if not candidates:
            continue
        text = " ".join(candidates[:2]).strip().rstrip(" ,;:")
        if len(text) > 260:
            cut = text[:260]
            text = cut[: cut.rfind(" ")].rstrip(" ,;:.") + " ..."
        return text

    # Chapters without a summary section (e.g. chapter 19): use the intro.
    for paragraph in content.find_all("p"):
        text = _summary_text(paragraph)
        if len(text) > 100 and not paragraph.find_parent("div", class_="figure"):
            return text[:260].rstrip(" ,;:.") + " ..."
    return ""


def rewrite_links(markdown: str, path_map: dict[str, str]) -> str:
    def replace(match: re.Match[str]) -> str:
        target = match.group(1)
        absolute = urllib.parse.urljoin(BASE_URL, target)
        parsed = urllib.parse.urlparse(absolute)
        if parsed.netloc and parsed.netloc != urllib.parse.urlparse(BASE_URL).netloc:
            return match.group(0)
        path = parsed.path.rstrip("/") or "/"
        local = path_map.get(path)
        if local is None:
            return match.group(0)
        fragment = f"#{parsed.fragment}" if parsed.fragment else ""
        return f"]({local}{fragment})"

    return re.sub(r"\]\((/[^)\s]*|https://www\.bayesrulesbook\.com/[^)\s]*)\)", replace, markdown)


def part_for(chapter: int) -> str:
    for start, end, name in PARTS:
        if start <= chapter <= end:
            return name
    return ""


def write_chapter(meta: dict, body: str, out_dir: Path) -> None:
    chapter = int(meta["chapter"])
    for start, end, part in PARTS:
        if start <= chapter <= end:
            meta["part"] = part
            break
    sections = "\n".join(f'  - "{s["title"]}"' for s in meta["sections"]) or "  []"
    frontmatter = (
        "---\n"
        f'title: "{meta["title"].replace(chr(34), chr(39))}"\n'
        f"chapter: {chapter}\n"
        f'part: "{meta["part"]}"\n'
        "sections:\n"
        f"{sections}\n"
        f'source: "{BASE_URL}{meta["path"]}"\n'
        'license: "CC BY-NC-SA 4.0"\n'
        "---\n\n"
    )
    (out_dir / meta["file"]).write_text(frontmatter + body, encoding="utf-8")


def build_index(metas: list[dict], front_metas: list[dict], generated: str, out_dir: Path) -> None:
    lines: list[str] = []
    add = lines.append
    add("# Bayes Rules! An Introduction to Applied Bayesian Modeling")
    add("")
    add("> Authors: Alicia A. Johnson, Miles Q. Ott, Mine Dogucu  ")
    add(f"> Source: <{BASE_URL}/> (free online edition)  ")
    add("> License: [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)  ")
    add(f"> Local markdown copy generated on {generated} for personal study.")
    add("")
    add("This directory is an offline, agent-readable copy of the book. One file")
    add("per chapter, plus this index. Cross-references, equation numbers and")
    add("anchors from the original site are preserved.")
    add("")
    add("## How to navigate this copy")
    add("")
    add("1. Read this index to locate the topic you need.")
    add("2. Open the chapter file listed below (~15-25k tokens each).")
    add("3. Jump to a section with its anchor, e.g. `chapter-03-beta-binomial-bayesian-model.md#ch3-prior`.")
    add("4. For a global search, use `rg -n \"term\" full.md`.")
    add("")
    add("Conventions:")
    add("")
    add("- Inline math uses `$...$`, display math `$$...$$`; equation tags are `\\tag{n}`.")
    add("- `TABLE x.y` / `FIGURE x.y` captions are bolded; figure images live in `images/`.")
    add("- `<a id=\"...\"></a>` lines are the original bookdown anchors; they make links such as `#ch4-priors` work.")
    add("- Code blocks are R unless the fence says otherwise.")
    add("")
    add("## Files")
    add("")
    add("| File | Contents |")
    add("| --- | --- |")
    add("| `00-frontmatter.md` | Foreword, preface (setup, datasets), about the authors |")
    for meta in metas:
        if meta.get("chapter"):
            add(f'| `{meta["file"]}` | Chapter {meta["chapter"]}. {meta["title"]} |')
    add("| `20-references.md` | Full bibliography |")
    add("| `full.md` | Every chapter concatenated, for global grep |")
    add("")
    add("## Chapters at a glance")
    add("")
    add("| # | Chapter | Summary (from the book) |")
    add("| --- | --- | --- |")
    for meta in metas:
        if meta.get("chapter"):
            summary = (meta.get("summary") or "").replace("|", "\\|")
            add(f'| {meta["chapter"]} | [{meta["title"]}]({meta["file"]}) | {summary} |')
    add("")

    current_part = None
    add("## Detailed table of contents")
    add("")
    if front_metas:
        add("### Front matter")
        add("")
        for meta in front_metas:
            add(f'**{meta["title"]}** — [00-frontmatter.md](00-frontmatter.md)')
            add("")
            for section in meta["sections"]:
                indent = "  " if section["level"] == 3 else ""
                add(f'{indent}- [{section["title"]}](00-frontmatter.md#{section["id"]})')
            add("")
    for meta in metas:
        part = meta.get("part")
        if part and part != current_part:
            current_part = part
            add(f"### Part {part}")
            add("")
        if meta.get("chapter"):
            add(f'**{meta["chapter"]}. [{meta["title"]}]({meta["file"]})**')
            add("")
        for section in meta["sections"]:
            indent = "  " if section["level"] == 3 else ""
            add(f'{indent}- [{section["title"]}]({meta["file"]}#{section["id"]})')
        add("")

    add("## Concept index")
    add("")
    add("| Topic | Chapter(s) |")
    add("| --- | --- |")
    for topic, chapters in TOPICS:
        links = []
        for number in re.findall(r"\d+|preface", chapters):
            if number == "preface":
                links.append("[preface](00-frontmatter.md)")
                continue
            match = next((m for m in metas if m.get("chapter") == int(number)), None)
            links.append(f"[{number}]({match['file']})" if match else number)
        add(f"| {topic} | {', '.join(links)} |")
    add("")
    text = re.sub(r"\n{3,}", "\n\n", "\n".join(lines))
    (out_dir / "indice.md").write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", default="bibliografia/bayes-rules")
    parser.add_argument("--only", default="", help="Comma separated page paths, e.g. chapter-3,chapter-4")
    parser.add_argument("--force", action="store_true", help="Refetch HTML and images")
    parser.add_argument("--no-images", action="store_true", help="Keep remote image URLs")
    parser.add_argument("--delay", type=float, default=0.5, help="Seconds between requests")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    cache_dir = out_dir / ".cache"
    images_dir = out_dir / "images"
    out_dir.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT

    selected = [p.strip().lstrip("/") for p in args.only.split(",") if p.strip()]
    pages = []
    for path in PAGES:
        if selected and path.strip("/") not in selected:
            continue
        pages.append(path)

    # First pass: fetch, parse and convert every requested page, remembering
    # the file name of each so cross-links can be rewritten.
    path_map = {
        "/": "indice.md",
        "/references": "20-references.md",
    }
    metas: list[dict] = []
    front_metas: list[dict] = []
    bodies: dict[str, str] = {}
    front_parts: list[str] = []

    for path in pages:
        html = fetch(session, path, cache_dir, args.force, args.delay)
        soup, content = parse_page(html)
        title, sections = page_metadata(content)
        chapter = None
        if path.startswith("/chapter-"):
            chapter = int(path.split("-")[1])
            file_name = f"chapter-{chapter:02d}-{slugify(title)}.md"
        elif path == "/references":
            file_name = "20-references.md"
        else:
            file_name = "00-frontmatter.md"
        path_map[path] = file_name

        meta = {
            "path": path,
            "title": title,
            "chapter": chapter,
            "sections": sections,
            "file": file_name,
            "summary": chapter_summary(content),
            "part": part_for(chapter) if chapter else "Front matter",
        }
        if chapter:
            metas.append(meta)
        elif path != "/references":
            meta["part"] = "Front matter"
            front_metas.append(meta)

        converter = Converter(
            soup=soup,
            content=content,
            page_path=path,
            images_dir=images_dir,
            image_subdir=(
                f"chapter-{chapter:02d}" if chapter else
                {"references": "references"}.get(path.strip("/"), "front-matter")
            ),
            download_images=not args.no_images,
            session=session,
            force=args.force,
        )
        converter.prepare(content)
        body = converter.to_markdown()
        del soup

        if chapter:
            write_chapter(meta, body, out_dir)
            bodies[f"chapter-{chapter:02d}"] = body
            print(f"  chapter {chapter:>2}: {file_name} ({len(body):>7} bytes, {converter.image_count} images)")
        elif path == "/references":
            (out_dir / "20-references.md").write_text(
                "---\n"
                'title: "References"\n'
                f'source: "{BASE_URL}{path}"\n'
                'license: "CC BY-NC-SA 4.0"\n'
                "---\n\n" + body,
                encoding="utf-8",
            )
            print(f"  references: 20-references.md ({len(body)} bytes)")
        else:
            front_parts.append(body)
            print(f"  front: {path} ({len(body)} bytes)")

    if front_parts:
        combined = "\n\n---\n\n".join(front_parts)
        (out_dir / "00-frontmatter.md").write_text(
            "---\n"
            'title: "Front matter (foreword, preface, about the authors)"\n'
            f'source: "{BASE_URL}/preface"\n'
            'license: "CC BY-NC-SA 4.0"\n'
            "---\n\n" + combined,
            encoding="utf-8",
        )

    # Second pass: rewrite intra-book links now that every file name is known.
    for meta in metas:
        file_path = out_dir / meta["file"]
        text = file_path.read_text(encoding="utf-8")
        head, separator, body = text.partition("\n---\n\n")
        if not separator:
            continue
        next_link = ""
        number = int(meta["chapter"])
        if number < 19:
            nxt = next((m for m in metas if m.get("chapter") == number + 1), None)
            if nxt:
                next_link = f'\n\n---\n\nNext: [{number + 1}. {nxt["title"]}]({nxt["file"]})\n'
        file_path.write_text(
            head + separator + rewrite_links(body, path_map).rstrip() + next_link,
            encoding="utf-8",
        )

    for name in ("00-frontmatter.md", "20-references.md"):
        file_path = out_dir / name
        if file_path.exists():
            text = file_path.read_text(encoding="utf-8")
            head, separator, body = text.partition("\n---\n\n")
            if separator:
                file_path.write_text(head + separator + rewrite_links(body, path_map), encoding="utf-8")

    if bodies:
        ordered = [bodies[key] for key in sorted(bodies)]
        full = "\n\n---\n\n".join(rewrite_links(body, path_map) for body in ordered)
        (out_dir / "full.md").write_text(
            "# Bayes Rules! An Introduction to Applied Bayesian Modeling (full text)\n\n"
            f"Source: <{BASE_URL}/> · License: CC BY-NC-SA 4.0\n\n---\n\n" + full,
            encoding="utf-8",
        )

    if metas:
        build_index(metas, front_metas, date.today().isoformat(), out_dir)

    images = sorted(images_dir.rglob("*")) if images_dir.exists() else []
    image_files = [p for p in images if p.is_file()]
    print(f"\nDone: {len(metas)} chapters, {len(image_files)} images in {images_dir}")
    print(f"Index: {out_dir / 'indice.md'}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
