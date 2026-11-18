#!/usr/bin/env python3
"""Build the offline, self-contained nextNEOpi API Reference HTML site.

The site is generated from the API reference Markdown plus **every** design
document under ``software_plan/`` so the ``html/`` directory can be copied and
browsed without the rest of the repository. Design goals:

* Clean build - the output tree is rebuilt from scratch on every run.
* Self-contained - all cross links resolve inside ``html/``. Raw Markdown is
  copied into ``html/_sources`` and the "view source" header links there.
  Links that point at the legacy pipeline (outside ``software_plan/``) are
  unwrapped to plain text because that code is intentionally not shipped.
* Inventory-driven navigation - the API groups are curated while the design
  groups are generated from the document tree, so no rendered page is orphaned.
* Reproducible - ``build-manifest.json`` records source digests and the Pandoc
  version used.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlsplit, urlunsplit

API_ROOT = Path(__file__).resolve().parent
PLAN_ROOT = API_ROOT.parent
OUTPUT_ROOT = API_ROOT / "html"
STATIC_ROOT = OUTPUT_ROOT / "_static"
SOURCES_ROOT = OUTPUT_ROOT / "_sources"

# Data files copied verbatim so "view schema"/example links stay inside html/.
COPIED_ASSETS: tuple[str, ...] = (
    "08_api_reference/interface-inventory.json",
    "04_specifications/schemas/run-config.schema.json",
    "04_specifications/schemas/site-profile.schema.json",
    "04_specifications/schemas/plugin-descriptor.schema.json",
    "04_specifications/schemas/artifact.schema.json",
    "04_specifications/schemas/result-envelope.schema.json",
    "04_specifications/schemas/case-manifest.schema.json",
    "04_specifications/examples/wes-dna-canonical.yaml",
    "04_specifications/examples/local-profile.yaml",
    "04_specifications/examples/slurm-profile.yaml",
    "04_specifications/examples/fastp-plugin-descriptor.json",
)
_ASSET_SET = frozenset(COPIED_ASSETS)

# Curated navigation for the Python API reference (labels are hand written).
API_NAV_GROUPS: tuple[tuple[str, tuple[tuple[str, str], ...]], ...] = (
    (
        "Reference",
        (
            ("Reference API", "08_api_reference/README.md"),
            ("API overview", "08_api_reference/api-overview.md"),
            ("API conventions", "08_api_reference/api-conventions.md"),
            ("API stability", "08_api_reference/stability.md"),
            ("Package layout", "08_api_reference/package-layout.md"),
            ("Typed edge matrix", "08_api_reference/typed-edge-matrix.md"),
            ("Implementation matrix", "08_api_reference/implementation-matrix.md"),
        ),
    ),
    (
        "Python API",
        (
            ("nextneopi", "08_api_reference/nextneopi.md"),
            ("nextneopi.config", "08_api_reference/nextneopi.config.md"),
            ("nextneopi.models", "08_api_reference/nextneopi.models.md"),
            ("nextneopi.application", "08_api_reference/nextneopi.application.md"),
            ("nextneopi.ports", "08_api_reference/nextneopi.ports.md"),
            ("nextneopi.plugins", "08_api_reference/nextneopi.plugins.md"),
            ("nextneopi.workflows", "08_api_reference/nextneopi.workflows.md"),
            ("nextneopi.errors", "08_api_reference/errors.md"),
            ("Type index", "08_api_reference/type-index.md"),
        ),
    ),
    (
        "Scientific capabilities",
        (
            ("input_reference", "08_api_reference/capabilities/input_reference.md"),
            ("reads_qc", "08_api_reference/capabilities/reads_qc.md"),
            ("alignment", "08_api_reference/capabilities/alignment.md"),
            ("variants", "08_api_reference/capabilities/variants.md"),
            ("annotation", "08_api_reference/capabilities/annotation_phasing.md"),
            ("hla", "08_api_reference/capabilities/hla.md"),
            ("copy_number", "08_api_reference/capabilities/copy_number.md"),
            ("ccf_tmb", "08_api_reference/capabilities/ccf_tmb.md"),
            ("rna", "08_api_reference/capabilities/rna.md"),
            ("events", "08_api_reference/capabilities/fusion_splicing.md"),
            ("neoantigens", "08_api_reference/capabilities/neoantigens.md"),
            ("immunity", "08_api_reference/capabilities/immunogenicity_repertoire.md"),
            ("reporting", "08_api_reference/capabilities/reporting.md"),
        ),
    ),
    (
        "Guides",
        (
            ("Quickstart", "08_api_reference/examples/quickstart.md"),
            ("Implement a plugin", "08_api_reference/examples/implement-plugin.md"),
        ),
    ),
)

# Plan-relative paths already surfaced through the curated API groups; they are
# skipped when the design navigation is generated from the document tree.
_API_NAV_RELS = frozenset(
    rel for _, items in API_NAV_GROUPS for _, rel in items
)

# Friendly, ordered group titles for the generated design navigation.
DESIGN_DIR_TITLES: tuple[tuple[str, str], ...] = (
    ("00_requirements", "Requirements"),
    ("01_architecture", "Architecture & ADRs"),
    ("02_modules", "Module map"),
    ("03_interfaces", "Interface contracts"),
    ("04_specifications", "Specifications & schemas"),
    ("05_testing", "Testing & equivalence"),
    ("06_quality", "Quality gates"),
    ("07_migration", "Migration"),
)


def plan_relative_output(plan_relative: Path) -> Path:
    """Map a software_plan-relative Markdown path to a site HTML path."""
    parts = plan_relative.parts
    if parts[0] == "08_api_reference":
        inner = Path(*parts[1:])
        if inner == Path("README.md"):
            return Path("index.html")
        return inner.with_suffix(".html")
    # Referenced design docs live under design/<original-structure>.html
    return Path("design") / plan_relative.with_suffix(".html")


def markdown_sources() -> list[Path]:
    """Every Markdown file under software_plan, excluding generated output."""
    return sorted(
        path
        for path in PLAN_ROOT.rglob("*.md")
        if OUTPUT_ROOT not in path.parents
    )


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pandoc_version(pandoc: str) -> str:
    out = subprocess.run([pandoc, "--version"], check=True, capture_output=True, text=True).stdout
    return out.splitlines()[0].strip() if out else "unknown"


def extract_title(markdown: str, fallback: str) -> str:
    match = re.search(r"^#\s+(.+?)\s*$", markdown, flags=re.MULTILINE)
    if not match:
        return fallback
    return html.unescape(re.sub(r"[`*_]", "", match.group(1))).strip()


def build_nav_model(titles: dict[str, str]) -> list[tuple[str, list[tuple[str, str]]]]:
    """Curated API groups first, then design groups generated per directory."""
    model: list[tuple[str, list[tuple[str, str]]]] = [
        (title, [(label, rel) for label, rel in items])
        for title, items in API_NAV_GROUPS
    ]

    design_rels = [
        rel
        for rel in titles
        if not rel.startswith("08_api_reference/") and rel not in _API_NAV_RELS
    ]

    overview = [rel for rel in design_rels if rel == "README.md"]
    if overview:
        model.append(("Overview", [(titles[overview[0]], overview[0])]))

    for directory, group_title in DESIGN_DIR_TITLES:
        prefix = f"{directory}/"
        members = sorted(rel for rel in design_rels if rel.startswith(prefix))
        if members:
            model.append((group_title, [(titles[rel], rel) for rel in members]))
    return model


def render_markdown(source: Path, pandoc: str) -> str:
    completed = subprocess.run(
        [pandoc, "--from=gfm", "--to=html5", "--wrap=none", "--no-highlight", str(source)],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return completed.stdout


def is_external(value: str) -> bool:
    scheme = urlsplit(value).scheme.lower()
    return scheme in {"http", "https", "mailto", "data", "javascript"} or value.startswith("//")


def mapped_link(value: str, source: Path, output: Path) -> str:
    """Rewrite a Markdown-relative link to its location in the site."""
    if not value or value.startswith("#") or is_external(value):
        return value
    parts = urlsplit(value)
    if not parts.path:
        return value

    target = (source.parent / unquote(parts.path)).resolve()
    try:
        plan_relative = target.relative_to(PLAN_ROOT)
    except ValueError:
        # Points outside software_plan (e.g. legacy pipeline files). Leave the
        # path as-is; offsite anchors are unwrapped to text in a later pass.
        mapped_target = target
    else:
        rel_posix = plan_relative.as_posix()
        if target.suffix.lower() == ".md":
            mapped_target = OUTPUT_ROOT / plan_relative_output(plan_relative)
        elif rel_posix in _ASSET_SET:
            mapped_target = OUTPUT_ROOT / "assets" / plan_relative.name
        else:
            mapped_target = target

    relative = Path(os.path.relpath(mapped_target, output.parent)).as_posix()
    return urlunsplit(("", "", relative, parts.query, parts.fragment))


def rewrite_links(fragment: str, source: Path, output: Path) -> str:
    pattern = re.compile(r"(?P<attr>href|src)=\"(?P<value>[^\"]+)\"")

    def repl(match: re.Match[str]) -> str:
        value = mapped_link(match.group("value"), source, output)
        return f'{match.group("attr")}="{html.escape(value, quote=True)}"'

    return pattern.sub(repl, fragment)


def unwrap_offsite_anchors(fragment: str, output: Path) -> str:
    """Convert links that resolve outside html/ into plain text.

    Cross links are already rewritten to point inside the site. Anything that
    still resolves outside ``html/`` targets code we do not ship (the legacy
    Nextflow pipeline), so we keep the label but drop the dead link.
    """
    anchor = re.compile(r'<a\b[^>]*?\shref="(?P<href>[^"]+)"[^>]*>(?P<label>.*?)</a>', re.DOTALL)

    def repl(match: re.Match[str]) -> str:
        href = match.group("href")
        if href.startswith("#") or is_external(href):
            return match.group(0)
        target = (output.parent / unquote(urlsplit(href).path)).resolve()
        try:
            target.relative_to(OUTPUT_ROOT)
        except ValueError:
            return match.group("label")
        return match.group(0)

    return anchor.sub(repl, fragment)


def wrap_tables(fragment: str) -> str:
    return re.sub(
        r"(<table(?:\s[^>]*)?>.*?</table>)",
        r'<div class="table-wrap">\1</div>',
        fragment,
        flags=re.DOTALL,
    )


def strip_tags(value: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", value)).strip()


def page_toc(fragment: str) -> str:
    headings = re.findall(
        r'<h(?P<level>[23])\s+id="(?P<id>[^"]+)"[^>]*>(?P<label>.*?)</h[23]>',
        fragment,
        flags=re.DOTALL,
    )
    if not headings:
        return '<p class="toc-empty">No sections</p>'
    items = [
        f'<li class="toc-level-{level}"><a href="#{html.escape(anchor, quote=True)}">{html.escape(strip_tags(label))}</a></li>'
        for level, anchor, label in headings
    ]
    return "<ol>" + "".join(items) + "</ol>"


def navigation(nav_model: list[tuple[str, list[tuple[str, str]]]], current_plan_relative: Path, output: Path) -> str:
    groups = []
    for title, items in nav_model:
        links = []
        for label, plan_rel in items:
            target = OUTPUT_ROOT / plan_relative_output(Path(plan_rel))
            href = Path(os.path.relpath(target, output.parent)).as_posix()
            active = Path(plan_rel) == current_plan_relative
            css = "nav-link active" if active else "nav-link"
            current = ' aria-current="page"' if active else ""
            search = html.escape(f"{label} {plan_rel}".lower(), quote=True)
            links.append(
                f'<li data-nav-item data-search="{search}"><a class="{css}" href="{html.escape(href, quote=True)}"{current}>{html.escape(label)}</a></li>'
            )
        groups.append(
            f'<section class="nav-group"><h2>{html.escape(title)}</h2><ul>{"".join(links)}</ul></section>'
        )
    return "".join(groups)


def breadcrumbs(plan_relative: Path, output: Path) -> str:
    home = Path(os.path.relpath(OUTPUT_ROOT / "index.html", output.parent)).as_posix()
    crumbs = [f'<a href="{html.escape(home, quote=True)}">Reference API</a>']
    label = "Reference API" if plan_relative.parts[0] == "08_api_reference" and plan_relative.name == "README.md" else plan_relative.as_posix()
    if label != "Reference API":
        crumbs.append(html.escape(label))
    return '<span class="crumb-separator">/</span>'.join(crumbs)


def html_document(*, plan_relative: Path, output: Path, title: str, fragment: str, nav_model) -> str:
    css = Path(os.path.relpath(STATIC_ROOT / "api.css", output.parent)).as_posix()
    script = Path(os.path.relpath(STATIC_ROOT / "api.js", output.parent)).as_posix()
    home = Path(os.path.relpath(OUTPUT_ROOT / "index.html", output.parent)).as_posix()
    source_link = Path(os.path.relpath(SOURCES_ROOT / plan_relative, output.parent)).as_posix()
    is_design = plan_relative.parts[0] != "08_api_reference"
    context_badge = '<span class="context-badge">Design context</span>' if is_design else ""
    return f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="nextNEOpi Reference API: {html.escape(title)}">
  <title>{html.escape(title)} — nextNEOpi Reference API</title>
  <link rel="stylesheet" href="{html.escape(css, quote=True)}">
  <script defer src="{html.escape(script, quote=True)}"></script>
</head>
<body>
  <a class="skip-link" href="#main-content">跳到正文</a>
  <header class="site-header">
    <a class="brand" href="{html.escape(home, quote=True)}"><span class="brand-mark">nN</span><span><strong>nextNEOpi</strong><small>Reference API</small></span></a>
    <div class="header-meta"><span class="version-badge">Design v0.2</span><a href="{html.escape(source_link, quote=True)}">查看源文档</a></div>
  </header>
  <div class="site-grid">
    <aside class="sidebar" aria-label="API navigation">
      <label class="search-label" for="api-search">搜索</label>
      <input id="api-search" type="search" placeholder="Filter pages…" autocomplete="off">
      <nav>{navigation(nav_model, plan_relative, output)}</nav>
    </aside>
    <main id="main-content" class="main-content">
      <div class="breadcrumbs">{breadcrumbs(plan_relative, output)}</div>
      {context_badge}
      <article class="api-content">{fragment}</article>
      <footer class="page-footer">nextNEOpi Software Plan · Design API，不表示实现已完成</footer>
    </main>
    <aside class="page-toc" aria-label="On this page"><h2>本页内容</h2>{page_toc(fragment)}</aside>
  </div>
</body>
</html>
'''


def build(pandoc: str) -> dict:
    if OUTPUT_ROOT.exists():
        shutil.rmtree(OUTPUT_ROOT)
    STATIC_ROOT.mkdir(parents=True, exist_ok=True)
    (OUTPUT_ROOT / "assets").mkdir(parents=True, exist_ok=True)
    SOURCES_ROOT.mkdir(parents=True, exist_ok=True)

    # Static assets are authored alongside the builder under _static_src.
    static_src = API_ROOT / "_static_src"
    for name in ("api.css", "api.js"):
        shutil.copyfile(static_src / name, STATIC_ROOT / name)

    manifest_sources: list[dict] = []

    for plan_rel in COPIED_ASSETS:
        src = PLAN_ROOT / plan_rel
        dst = OUTPUT_ROOT / "assets" / Path(plan_rel).name
        shutil.copyfile(src, dst)
        manifest_sources.append({"source": plan_rel, "output": f"assets/{Path(plan_rel).name}", "sha256": sha256_file(src)})

    sources = markdown_sources()

    # First pass: gather titles so navigation labels are available up front.
    titles: dict[str, str] = {}
    markdown_by_rel: dict[str, str] = {}
    for source in sources:
        rel = source.relative_to(PLAN_ROOT).as_posix()
        text = source.read_text(encoding="utf-8")
        markdown_by_rel[rel] = text
        titles[rel] = extract_title(text, source.stem)

    nav_model = build_nav_model(titles)

    pages = 0
    for source in sources:
        plan_relative = source.relative_to(PLAN_ROOT)
        rel = plan_relative.as_posix()
        output = OUTPUT_ROOT / plan_relative_output(plan_relative)
        output.parent.mkdir(parents=True, exist_ok=True)

        # Copy the raw Markdown so the "view source" link stays inside html/.
        raw_dst = SOURCES_ROOT / plan_relative
        raw_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, raw_dst)

        fragment = render_markdown(source, pandoc)
        fragment = rewrite_links(fragment, source, output)
        fragment = unwrap_offsite_anchors(fragment, output)
        fragment = wrap_tables(fragment)
        document = html_document(
            plan_relative=plan_relative,
            output=output,
            title=titles[rel],
            fragment=fragment,
            nav_model=nav_model,
        )
        output.write_text(document, encoding="utf-8")
        manifest_sources.append({
            "source": rel,
            "output": output.relative_to(OUTPUT_ROOT).as_posix(),
            "sha256": sha256_file(source),
        })
        pages += 1

    manifest = {
        "generator": "build_html.py",
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "pandoc": pandoc_version(pandoc),
        "page_count": pages,
        "asset_count": len(COPIED_ASSETS),
        "raw_sources_dir": "_sources",
        "sources": sorted(manifest_sources, key=lambda item: item["output"]),
    }
    (OUTPUT_ROOT / "build-manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Generated {pages} HTML pages, {len(COPIED_ASSETS)} assets, {pages} raw sources in {OUTPUT_ROOT}")
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pandoc", default=shutil.which("pandoc") or "pandoc")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not shutil.which(args.pandoc) and not Path(args.pandoc).is_file():
        raise SystemExit(f"Pandoc not found: {args.pandoc}")
    build(args.pandoc)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
