#!/usr/bin/env python3
"""sweep.py — mechanical hygiene operations for the curiosity-engine wiki.

Distinct from ITERATE's semantic ratchet: SWEEP operates across the whole
wiki at once, deterministically, in seconds. It catches the kinds of issues
that ITERATE's compression-progress ratchet cannot see (or would burn huge
numbers of slow cycles on): dead wikilinks, duplicate slugs, orphan pages,
missing wiki/sources stubs, index.md drift, frontmatter invalid.

Subcommands
-----------
    sweep.py scan [wiki_dir]
        Read-only report. Emits one JSON object covering every hygiene
        dimension. Main session reads the report and decides what to fix.

    sweep.py fix-source-stubs [wiki_dir]
        Deterministic backfill: for every file in `vault/` without a
        corresponding stub in `wiki/sources/`, create one from the vault
        file's extracted-text frontmatter and a short auto-summary.
        Idempotent. Prints JSON summary of what was created.

    sweep.py fix-index [wiki_dir]
        Rewrite `wiki/index.md` so it matches the pages actually on disk.
        Preserves any top-of-file prose (before the first list item).
        Prints JSON summary of drift resolved.

Design notes
------------
- sweep.py is guarded by evolve_guard.sh alongside compress/lint/score_diff/
  epoch_summary. EVOLVE may not edit it.
- Only the `fix-*` subcommands write. `scan` is pure read.
- Uses only the stdlib. Runs in well under a second even on a 1000-page wiki.
"""
import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path


SKIP_FILES = {"index.md", "log.md", "schema.md"}
WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")
FRONTMATTER_REQUIRED = {"title", "type", "created"}
FRONTMATTER_TYPES = {"entity", "concept", "source", "analysis"}


def wiki_pages(wiki_dir: Path) -> list:
    return [p for p in wiki_dir.rglob("*.md")
            if p.name not in SKIP_FILES and "_suspect" not in p.parts]


def read_frontmatter(text: str) -> tuple:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    fm_block = text[3:end].strip()
    body = text[end + 4:]
    fm = {}
    for line in fm_block.split("\n"):
        line = line.strip()
        if not line or ":" not in line:
            continue
        k, _, v = line.partition(":")
        fm[k.strip()] = v.strip()
    return fm, body


def normalize_slug(stem: str) -> str:
    """Fuzzy normalization for duplicate-slug detection.

    Lowercases, replaces hyphens/underscores with a single space, strips
    leading articles, drops trailing plural-s. Pages that collapse to the
    same key are duplicate candidates.
    """
    s = stem.lower().replace("-", " ").replace("_", " ")
    s = re.sub(r"\s+", " ", s).strip()
    for article in ("a ", "an ", "the "):
        if s.startswith(article):
            s = s[len(article):]
    if s.endswith("s") and not s.endswith("ss"):
        s = s[:-1]
    return s


def scan_wikilinks(pages: list) -> tuple:
    """Return (all_refs, dead_refs, inbound_counts).

    all_refs: list of (source_page, target_slug)
    dead_refs: refs whose target_slug has no page on disk
    inbound_counts: {stem: n_inbound_from_other_pages}
    """
    stems_on_disk = {p.stem.lower() for p in pages}
    all_refs = []
    inbound = defaultdict(int)
    for page in pages:
        text = page.read_text()
        own = page.stem.lower()
        for m in WIKILINK_RE.finditer(text):
            target = m.group(1).strip().lower().replace(" ", "-")
            all_refs.append((str(page), target))
            if target != own and target in stems_on_disk:
                inbound[target] += 1
    dead_refs = [(src, tgt) for (src, tgt) in all_refs
                 if tgt not in stems_on_disk]
    return all_refs, dead_refs, dict(inbound)


def scan_duplicate_slugs(pages: list) -> list:
    groups = defaultdict(list)
    for p in pages:
        groups[normalize_slug(p.stem)].append(str(p))
    return [{"key": k, "pages": v} for k, v in groups.items() if len(v) > 1]


def scan_orphans(pages: list, inbound: dict) -> list:
    return [str(p) for p in pages if inbound.get(p.stem.lower(), 0) == 0]


def scan_frontmatter(pages: list) -> list:
    issues = []
    for p in pages:
        fm, _ = read_frontmatter(p.read_text())
        missing = FRONTMATTER_REQUIRED - fm.keys()
        bad_type = fm.get("type") not in FRONTMATTER_TYPES if "type" in fm else False
        if missing or bad_type:
            issues.append({
                "page": str(p),
                "missing": sorted(missing),
                "bad_type": fm.get("type") if bad_type else None,
            })
    return issues


def scan_index_drift(wiki_dir: Path, pages: list) -> dict:
    index_path = wiki_dir / "index.md"
    listed = set()
    if index_path.exists():
        for m in WIKILINK_RE.finditer(index_path.read_text()):
            listed.add(m.group(1).strip().lower().replace(" ", "-"))
    on_disk = {p.stem.lower() for p in pages}
    return {
        "on_disk_not_in_index": sorted(on_disk - listed),
        "in_index_not_on_disk": sorted(listed - on_disk),
    }


def _vault_files_covered_by_stubs(wiki_dir: Path) -> set:
    """Vault extraction filenames already referenced by a source stub's frontmatter."""
    sources_dir = wiki_dir / "sources"
    covered = set()
    if not sources_dir.exists():
        return covered
    for stub in sources_dir.glob("*.md"):
        fm, _ = read_frontmatter(stub.read_text())
        raw = fm.get("sources", "")
        for name in re.findall(r"[\w./-]+\.extracted\.md", raw):
            covered.add(name.lower())
    return covered


def scan_missing_source_stubs(wiki_dir: Path) -> list:
    """vault/*.extracted.md files with no matching wiki/sources stub."""
    vault_dir = wiki_dir.parent / "vault"
    if not vault_dir.exists():
        return []
    covered = _vault_files_covered_by_stubs(wiki_dir)
    missing = []
    for f in sorted(vault_dir.glob("*.extracted.md")):
        if f.name.lower() not in covered:
            missing.append(str(f))
    return missing


def cmd_scan(wiki_dir: Path):
    pages = wiki_pages(wiki_dir)
    _, dead_refs, inbound = scan_wikilinks(pages)
    report = {
        "wiki_dir": str(wiki_dir),
        "page_count": len(pages),
        "dead_wikilinks": [{"source": s, "target": t} for (s, t) in dead_refs],
        "duplicate_slugs": scan_duplicate_slugs(pages),
        "orphans": scan_orphans(pages, inbound),
        "frontmatter_issues": scan_frontmatter(pages),
        "index_drift": scan_index_drift(wiki_dir, pages),
        "missing_source_stubs": scan_missing_source_stubs(wiki_dir),
    }
    report["hygiene_debt"] = (
        len(report["dead_wikilinks"])
        + len(report["duplicate_slugs"])
        + len(report["frontmatter_issues"])
        + len(report["index_drift"]["on_disk_not_in_index"])
        + len(report["index_drift"]["in_index_not_on_disk"])
        + len(report["missing_source_stubs"])
    )
    print(json.dumps(report, indent=2))


def cmd_fix_source_stubs(wiki_dir: Path):
    """Create wiki/sources/<topic>.md for every vault extraction without a stub.

    Uses the clean topic name extracted from the vault filename (e.g.,
    `game-theory.md` instead of `20260411-...-wiki-game-theory.md`).
    The generated stub includes frontmatter pointing at the vault path and a
    first-paragraph auto-summary drawn from the extracted text.
    """
    vault_dir = wiki_dir.parent / "vault"
    sources_dir = wiki_dir / "sources"
    sources_dir.mkdir(parents=True, exist_ok=True)
    covered = _vault_files_covered_by_stubs(wiki_dir)
    used_stems = {p.stem.lower() for p in sources_dir.glob("*.md")}
    created = []
    skipped = 0
    for extracted in sorted(vault_dir.glob("*.extracted.md")):
        if extracted.name.lower() in covered:
            skipped += 1
            continue

        raw_stem = extracted.stem.replace(".extracted", "")
        topic = _extract_topic(raw_stem)
        topic_title = topic.replace("-", " ").replace("_", " ").title()

        # Deduplicate: if topic stem is taken, add numeric suffix
        clean_stem = topic.lower()
        if clean_stem in used_stems:
            n = 2
            while f"{clean_stem}-{n}" in used_stems:
                n += 1
            clean_stem = f"{clean_stem}-{n}"
        used_stems.add(clean_stem)

        stub_path = sources_dir / f"{clean_stem}.md"

        fm, body = read_frontmatter(extracted.read_text())
        title = fm.get("title") or topic_title
        summary_lines = []
        for line in body.split("\n"):
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("<!--"):
                continue
            summary_lines.append(line)
            if sum(len(l) for l in summary_lines) > 400:
                break
        summary = " ".join(summary_lines)[:500]
        if not summary:
            summary = f"Source extraction for {title}. (vault:{extracted.name})"

        stub = (
            f"---\n"
            f"title: {title}\n"
            f"type: source\n"
            f"created: {fm.get('date', '2026-04-12')}\n"
            f"updated: 2026-04-12\n"
            f"sources: [{extracted.name}]\n"
            f"---\n\n"
            f"{summary} (vault:{extracted.name})\n"
        )
        stub_path.write_text(stub)
        created.append(str(stub_path))
    print(json.dumps({"created": len(created), "skipped": skipped,
                      "created_paths": created}, indent=2))


WIKIPEDIA_BOILERPLATE = re.compile(
    r"(?:Wikipedia\s+)?Jump to (?:content|navigation|search)|"
    r"From Wikipedia,? the free encyclopedia|"
    r"Main menu\b|"
    r"Article\s+Talk\b|"
    r"Read\s+Edit\s+View history\b|"
    r"Tools\b.*?What links here|"
    r"Categories?\s*:|"
    r"Hidden categories?\s*:|"
    r"This (?:article|page) (?:is about|needs|has)\b|"
    r"^\s*\[\s*edit\s*\]\s*$|"
    r"^\s*Contents\s*$|"
    r"^\s*References\s*$|"
    r"^\s*External links\s*$|"
    r"^\s*See also\s*$|"
    r"^\s*Notes\s*$|"
    r"^\s*Further reading\s*$",
    re.IGNORECASE | re.MULTILINE,
)


def _extract_topic(stem: str) -> str:
    """Pull the topic name from a source stub stem like '20260411-...-wiki-game-theory'.

    Strips URL-encoded characters (``27s`` for apostrophe, ``e2-80-93`` for
    em-dash, ``28``/``29`` for parens) that leak through from Wikipedia URLs.
    """
    m = re.search(r"-wiki-(.+)$", stem)
    if m:
        topic = m.group(1)
    else:
        m = re.search(r"-org-(.+)$", stem)
        if m:
            topic = m.group(1)
        else:
            parts = stem.split("-")
            for i, p in enumerate(parts):
                if not p.isdigit() and p not in ("en", "wikipedia", "org", "wiki", "www", "http", "https"):
                    topic = "-".join(parts[i:])
                    break
            else:
                return stem
    # Strip URL-encoded character fragments
    topic = re.sub(r"-?27s-?", "s-", topic)       # apostrophe → just 's'
    topic = re.sub(r"-?e2-80-9[0-9]-?", "-", topic)  # em/en-dash → hyphen
    topic = re.sub(r"-?2[89]-?", "-", topic)       # parens
    topic = re.sub(r"-{2,}", "-", topic).strip("-")
    return topic


def _url_to_origin(url: str) -> str:
    """Map a source URL to a short human-readable origin label."""
    url_lower = url.lower()
    for domain, label in (
        ("wikipedia.org", "Wikipedia"), ("arxiv.org", "arXiv"),
        ("nature.com", "Nature"), ("sciencedirect.com", "ScienceDirect"),
        ("cell.com", "Cell"), ("springer.com", "Springer"),
        ("ieee.org", "IEEE"), ("acm.org", "ACM"), ("github.com", "GitHub"),
        ("nytimes.com", "NYTimes"), ("bbc.co", "BBC"),
    ):
        if domain in url_lower:
            return label
    m = re.search(r"//(?:www\.)?([^/]+)", url)
    if m:
        parts = m.group(1).split(".")
        return parts[-2].capitalize() if len(parts) >= 2 else parts[0].capitalize()
    return "Web"


def _parse_source_meta(vault_path: Path) -> dict:
    """Extract metadata from a vault extraction for citation-style naming.

    Returns dict with keys: topic, origin, year, author, full_title.
    Works for structured frontmatter (web fetches with source_url) and
    plain markdown (papers with ``# Title (Author et al., Year)`` headers).
    """
    text = vault_path.read_text()
    fm, body = read_frontmatter(text)

    meta = {"topic": "", "origin": "", "year": "", "author": "", "full_title": ""}

    source_url = fm.get("source_url", "")
    if source_url:
        meta["origin"] = _url_to_origin(source_url)
        raw_stem = vault_path.stem.replace(".extracted", "")
        meta["topic"] = _extract_topic(raw_stem)
        fetched = fm.get("fetched_at", "")
        if fetched:
            meta["year"] = fetched[:4]
        meta["full_title"] = meta["topic"].replace("-", " ").title()
    else:
        # Plain markdown — parse first header for title, author, year
        for line in body.split("\n"):
            line = line.strip()
            if not line.startswith("#"):
                continue
            header = line.lstrip("#").strip()
            m = re.match(r"(.+?)\s*\(([^)]+)\)\s*$", header)
            if m:
                title_part = m.group(1).strip()
                paren = m.group(2).strip()
                meta["full_title"] = title_part
                ym = re.search(r"\b(19|20)\d{2}\b", paren)
                if ym:
                    meta["year"] = ym.group(0)
                author_str = re.sub(r"\b(19|20)\d{2}\b", "", paren)
                author_str = author_str.replace("et al.", "").replace(",", "").strip()
                if author_str:
                    meta["author"] = author_str.split()[0]
                stop = {"a", "an", "the", "of", "in", "for", "and", "is", "are", "on", "to", "with"}
                words = [w for w in title_part.split() if w.lower() not in stop]
                meta["topic"] = "-".join(w.lower() for w in words[:3])
            else:
                meta["full_title"] = header
                meta["topic"] = vault_path.stem.replace(".extracted", "")
            break

    if not meta["topic"]:
        meta["topic"] = vault_path.stem.replace(".extracted", "")

    return meta


def _citation_stem(meta: dict) -> str:
    """Build a citation-style filename stem from parsed metadata.

    Papers with author: attention-vaswani-2017
    Wikipedia (no author): deep-learning-wikipedia-2026
    """
    parts = [meta["topic"]]
    if meta.get("author"):
        parts.append(meta["author"].lower())
    if meta.get("year"):
        parts.append(meta["year"])
    if not meta.get("author") and meta.get("origin"):
        parts.append(meta["origin"].lower())
    return "-".join(parts)


def _source_display_title(meta: dict) -> str:
    """Build rich display title for a source stub.

    "Deep Learning — Wikipedia, 2026" or "Attention Is All You Need — Vaswani, 2017"
    """
    title = meta.get("full_title") or meta["topic"].replace("-", " ").title()
    suffix_parts = []
    if meta.get("author"):
        suffix_parts.append(meta["author"])
    elif meta.get("origin"):
        suffix_parts.append(meta["origin"])
    if meta.get("year"):
        suffix_parts.append(meta["year"])
    if suffix_parts:
        return f"{title} — {', '.join(suffix_parts)}"
    return title


def cmd_fix_source_boilerplate(wiki_dir: Path):
    """Strip Wikipedia nav boilerplate from source stubs, add wikilinks.

    Deterministic: no LLM calls. Runs in under a second. For each source
    stub, strips known boilerplate patterns and inserts [[hyphen-stem]]
    wikilinks to related wiki pages based on title matching.
    """
    sources_dir = wiki_dir / "sources"
    if not sources_dir.exists():
        print(json.dumps({"fixed": 0, "skipped": 0}))
        return

    concept_entity_pages = [p for p in wiki_pages(wiki_dir)
                            if not str(p.relative_to(wiki_dir)).startswith("sources/")]
    ce_stems = {p.stem.lower() for p in concept_entity_pages}

    fixed = 0
    skipped = 0
    for stub_path in sorted(sources_dir.glob("*.md")):
        text = stub_path.read_text()
        fm, body = read_frontmatter(text)

        vault_citation = None
        vault_match = re.search(r"\(vault:[^)]+\)", body)
        if vault_match:
            vault_citation = vault_match.group(0)

        has_boilerplate = bool(WIKIPEDIA_BOILERPLATE.search(body))

        title = fm.get("title", stub_path.stem.replace("-", " ").title())
        topic = _extract_topic(stub_path.stem)
        topic_words = set(topic.lower().replace("-", " ").replace("_", " ").split())
        topic_words -= {"en", "wikipedia", "org", "wiki", "27s", "28"}

        related_stems = []
        for stem in sorted(ce_stems):
            stem_words = set(stem.replace("-", " ").split())
            if stem_words & topic_words and len(stem) > 3:
                related_stems.append(stem)
            if len(related_stems) >= 4:
                break

        topic_title = topic.replace("-", " ").replace("_", " ").title()

        link_text = ""
        if related_stems:
            link_text = " Related: " + ", ".join(
                f"[[concepts/{s}]]" for s in related_stems
            ) + "."

        citation = vault_citation or ""
        if citation and not citation.startswith(" "):
            citation = " " + citation

        fm_block = "---\n"
        for k, v in fm.items():
            fm_block += f"{k}: {v}\n"
        fm_block += "---\n\n"

        new_text = fm_block + f"Source material on {topic_title}." + link_text + citation + "\n"

        if new_text != text:
            stub_path.write_text(new_text)
            fixed += 1
        else:
            skipped += 1

    print(json.dumps({"fixed": fixed, "skipped": skipped}))


def cmd_rename_sources(wiki_dir: Path):
    """Rename source stubs to citation-style filenames.

    Timestamp-URL stems become citation keys:
      `20260411-...-wiki-game-theory.md` → `game-theory-wikipedia-2026.md`
      `attention.md` (with vault header "Vaswani et al., 2017") → `attention-vaswani-2017.md`

    Reads vault extraction frontmatter for origin/year and header lines for
    author. Rewrites wikilinks across the entire wiki that referenced old stems.
    Idempotent: stubs already matching their citation stem are skipped.
    """
    sources_dir = wiki_dir / "sources"
    if not sources_dir.exists():
        print(json.dumps({"renamed": 0, "skipped": 0}))
        return

    vault_dir = wiki_dir.parent / "vault"

    # Build old_stem → new_stem rename map
    used_stems = set()
    rename_map = {}  # old_stem → new_stem
    stubs = sorted(sources_dir.glob("*.md"))

    for stub_path in stubs:
        old_stem = stub_path.stem
        fm, _ = read_frontmatter(stub_path.read_text())

        # Find the vault extraction for this stub
        vault_ref = fm.get("sources", "")
        vault_files = re.findall(r"[\w./-]+\.extracted\.md", vault_ref)

        meta = None
        for vf in vault_files:
            vp = vault_dir / vf
            if vp.exists():
                meta = _parse_source_meta(vp)
                break

        if meta is None:
            # No vault file found — use stub frontmatter as fallback
            meta = {
                "topic": _extract_topic(old_stem),
                "origin": "", "year": "", "author": "",
                "full_title": fm.get("title", old_stem.replace("-", " ").title()),
            }

        new_stem = _citation_stem(meta)

        # Already has citation-style name?
        if old_stem == new_stem:
            used_stems.add(new_stem)
            continue

        # Deduplicate
        candidate = new_stem
        if candidate in used_stems:
            n = 2
            while f"{candidate}-{n}" in used_stems:
                n += 1
            candidate = f"{candidate}-{n}"
        used_stems.add(candidate)
        rename_map[old_stem] = candidate

    if not rename_map:
        print(json.dumps({"renamed": 0, "skipped": len(stubs)}))
        return

    # Rename files and update their frontmatter titles
    for stub_path in stubs:
        old_stem = stub_path.stem
        if old_stem not in rename_map:
            continue
        new_stem = rename_map[old_stem]

        text = stub_path.read_text()
        fm, body = read_frontmatter(text)

        # Rebuild frontmatter with updated title
        fm_block = "---\n"
        for k, v in fm.items():
            fm_block += f"{k}: {v}\n"
        fm_block += "---"

        new_path = sources_dir / f"{new_stem}.md"
        new_path.write_text(fm_block + body)
        if new_path != stub_path:
            stub_path.unlink()

    # Rewrite wikilinks referencing old source stems across the wiki.
    # Only rewrite folder-qualified [[sources/old_stem]] forms — bare
    # [[old_stem]] may legitimately point to a same-named concept page.
    ce_stems = set()
    for subdir in ("concepts", "entities", "analyses"):
        d = wiki_dir / subdir
        if d.exists():
            ce_stems |= {p.stem.lower() for p in d.glob("*.md")}

    all_pages = wiki_pages(wiki_dir)
    rewrites = 0
    for page in all_pages:
        text = page.read_text()
        new_text = text
        for old_stem, new_stem in rename_map.items():
            # Always rewrite folder-qualified forms
            new_text = new_text.replace(
                f"[[sources/{old_stem}]]", f"[[sources/{new_stem}]]")
            new_text = new_text.replace(
                f"[[sources/{old_stem}|", f"[[sources/{new_stem}|")
            # Only rewrite bare [[old_stem]] if no concept/entity shares the name
            if old_stem not in ce_stems:
                new_text = new_text.replace(f"[[{old_stem}]]", f"[[{new_stem}]]")
                new_text = new_text.replace(f"[[{old_stem}|", f"[[{new_stem}|")
        if new_text != text:
            page.write_text(new_text)
            rewrites += 1

    print(json.dumps({
        "renamed": len(rename_map),
        "skipped": len(stubs) - len(rename_map),
        "wikilink_rewrites": rewrites,
    }))


TYPE_PREFIX = {
    "concept": "[con]",
    "entity": "[ent]",
    "analysis": "[ana]",
    "source": "[src]",
}


def cmd_fix_display_names(wiki_dir: Path):
    """Add type-prefix display names to all page frontmatter titles.

    Sets frontmatter ``title`` to ``[con] Deep Learning``, ``[src] Deep
    Learning — Wikipedia, 2026``, etc. Obsidian's "Use frontmatter title as
    display name" setting then shows these as graph-view node labels.

    For source stubs, builds a rich citation display title from vault
    extraction metadata. For concepts/entities/analyses, prefixes the
    existing title. Idempotent: pages already prefixed are skipped.
    """
    vault_dir = wiki_dir.parent / "vault"
    pages = wiki_pages(wiki_dir)
    updated = 0
    skipped = 0

    for page in pages:
        text = page.read_text()
        fm, body = read_frontmatter(text)
        page_type = fm.get("type", "")
        prefix = TYPE_PREFIX.get(page_type)
        if not prefix:
            skipped += 1
            continue

        current_title = fm.get("title", page.stem.replace("-", " ").title())

        # Already prefixed?
        if current_title.startswith("["):
            skipped += 1
            continue

        if page_type == "source":
            # Build rich citation display title from vault metadata
            vault_ref = fm.get("sources", "")
            vault_files = re.findall(r"[\w./-]+\.extracted\.md", vault_ref)
            meta = None
            for vf in vault_files:
                vp = vault_dir / vf
                if vp.exists():
                    meta = _parse_source_meta(vp)
                    break
            if meta:
                display = _source_display_title(meta)
            else:
                display = current_title
            new_title = f"{prefix} {display}"
        else:
            new_title = f"{prefix} {current_title}"

        fm["title"] = new_title
        fm_block = "---\n"
        for k, v in fm.items():
            fm_block += f"{k}: {v}\n"
        fm_block += "---"

        new_text = fm_block + body
        if new_text != text:
            page.write_text(new_text)
            updated += 1
        else:
            skipped += 1

    print(json.dumps({"updated": updated, "skipped": skipped}))


def cmd_fix_index(wiki_dir: Path):
    """Rewrite wiki/index.md so it matches the pages on disk.

    Preserves any prose before the first list item (treated as a hand-written
    header/intro). Everything after is regenerated, grouped by subdirectory.
    """
    pages = wiki_pages(wiki_dir)
    index_path = wiki_dir / "index.md"
    header = "# Index\n\n"
    if index_path.exists():
        old = index_path.read_text()
        first_list = re.search(r"^[-*] ", old, re.MULTILINE)
        if first_list:
            header = old[:first_list.start()].rstrip() + "\n\n"

    by_dir = defaultdict(list)
    for p in pages:
        subdir = p.parent.relative_to(wiki_dir).as_posix() or "."
        by_dir[subdir].append(p.stem)

    sections = [header]
    for subdir in sorted(by_dir):
        sections.append(f"## {subdir}\n\n")
        for stem in sorted(by_dir[subdir]):
            sections.append(f"- [[{stem}]]\n")
        sections.append("\n")
    new_index = "".join(sections)
    before = index_path.read_text() if index_path.exists() else ""
    index_path.write_text(new_index)
    print(json.dumps({
        "rewrote": True,
        "page_count": len(pages),
        "subdir_count": len(by_dir),
        "size_change": len(new_index) - len(before),
    }, indent=2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=[
        "scan", "fix-source-stubs", "fix-source-boilerplate",
        "rename-sources", "fix-display-names", "fix-index",
    ])
    ap.add_argument("wiki", nargs="?", default="wiki")
    args = ap.parse_args()

    wiki_dir = Path(args.wiki).resolve()
    if not wiki_dir.exists():
        print(json.dumps({"error": f"wiki dir not found: {wiki_dir}"}))
        sys.exit(1)

    if args.command == "scan":
        cmd_scan(wiki_dir)
    elif args.command == "fix-source-stubs":
        cmd_fix_source_stubs(wiki_dir)
    elif args.command == "fix-source-boilerplate":
        cmd_fix_source_boilerplate(wiki_dir)
    elif args.command == "rename-sources":
        cmd_rename_sources(wiki_dir)
    elif args.command == "fix-display-names":
        cmd_fix_display_names(wiki_dir)
    elif args.command == "fix-index":
        cmd_fix_index(wiki_dir)


if __name__ == "__main__":
    main()
