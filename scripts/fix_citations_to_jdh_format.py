"""Convert empty <cite data-cite="LIB/KEY"></cite> tags to JDH-official format.

Reads the bibliography section in-place to build a key -> "(Author Year)" map,
then rewrites every empty cite tag to:
    <cite id="RANDOM5"><a href="#zotero|LIB/KEY">(Author Year)</a></cite>
Also renames the BIBLIOGRAPHY START/END markers so jupyterlab-citation-manager
stops trying to manage the bibliography and wipe it.

One-shot script. Edits work/shelters-for-all.ipynb in place.
"""
import json
import random
import re
import string
from pathlib import Path

NB_PATH = Path("/c/Users/Adela/JDH_SpatialEquity/work/shelters-for-all.ipynb")
if not NB_PATH.exists():
    NB_PATH = Path("work/shelters-for-all.ipynb")

YEAR_RE = re.compile(r"\b(1[89]\d\d|20\d\d)\b|\bn\.?\s*d\.?\b")
ENTRY_RE = re.compile(r'<i id="zotero\|([^"]+)"></i>(.*?)(?:</div>|<div )', re.DOTALL)
CITE_RE = re.compile(r'<cite data-cite="([^"]+)"></cite>')


def parse_author_year(entry_body: str) -> str | None:
    """From a bibliography entry body, build a Chicago in-text citation."""
    ym = YEAR_RE.search(entry_body)
    if not ym:
        return None
    year_text = ym.group(0)
    if "n" in year_text.lower():
        year_text = "n.d."

    author_block = entry_body[: ym.start()].strip().rstrip(".,").strip()
    if not author_block:
        return None

    # Extract first family name: text before first comma OR first period
    fc = author_block.find(",")
    fp = author_block.find(".")
    if fc > 0 and (fp < 0 or fc < fp):
        first_family = author_block[:fc]
    elif fp > 0:
        first_family = author_block[:fp]
    else:
        first_family = author_block
    first_family = first_family.strip()

    if re.search(r"\bet\s+al\.?", author_block, re.IGNORECASE):
        return f"{first_family} et al. {year_text}"

    if " and " in author_block:
        n_commas = author_block.count(",")
        if n_commas <= 2:
            # Two authors: "Last1, First1, and First2 Last2."
            after = author_block.rsplit(" and ", 1)[1]
            second_family = after.strip().split()[-1].rstrip(".,;")
            return f"{first_family} and {second_family} {year_text}"
        return f"{first_family} et al. {year_text}"

    return f"{first_family} {year_text}"


def gen_id(seen: set) -> str:
    pool = string.ascii_lowercase + string.digits
    while True:
        s = "".join(random.choices(pool, k=5))
        if s not in seen:
            seen.add(s)
            return s


def main():
    nb = json.loads(NB_PATH.read_text(encoding="utf-8"))

    # Collect bibliography text from cells containing BIBLIOGRAPHY START
    bib_text = ""
    for cell in nb["cells"]:
        src = cell.get("source", "")
        src_str = "".join(src) if isinstance(src, list) else src
        if "BIBLIOGRAPHY START" in src_str or "csl-bib-body" in src_str:
            bib_text += src_str

    key_to_label: dict[str, str] = {}
    for m in ENTRY_RE.finditer(bib_text):
        key = m.group(1)
        body = m.group(2)
        label = parse_author_year(body)
        if label:
            key_to_label[key] = label

    print(f"bibliography entries parsed: {len(key_to_label)}")
    sample = list(key_to_label.items())[:5]
    for k, v in sample:
        print(f"  {k} -> {v}")

    # Collect all cite keys used inline
    all_cite_keys: set[str] = set()
    for cell in nb["cells"]:
        src = cell.get("source", "")
        src_str = "".join(src) if isinstance(src, list) else src
        for m in CITE_RE.finditer(src_str):
            all_cite_keys.add(m.group(1))
    missing = [k for k in all_cite_keys if k not in key_to_label]
    print(f"cites used inline: {len(all_cite_keys)}, missing labels: {len(missing)}")
    for k in missing[:10]:
        print(f"  MISSING: {k}")

    # Rewrite cells
    seen_ids: set[str] = set()
    rewrites = 0
    for cell in nb["cells"]:
        src = cell.get("source", "")
        src_list = src if isinstance(src, list) else [src]
        new_lines: list[str] = []
        changed = False
        for line in src_list:
            def repl(m):
                nonlocal changed
                key = m.group(1)
                label = key_to_label.get(key, key.split("/")[-1])
                cid = gen_id(seen_ids)
                changed = True
                return f'<cite id="{cid}"><a href="#zotero|{key}">({label})</a></cite>'
            new_line, n = CITE_RE.subn(repl, line)
            rewrites += n
            new_lines.append(new_line)
        if changed:
            # Also rename bibliography markers in this cell
            joined = "".join(new_lines)
            joined = joined.replace("<!-- BIBLIOGRAPHY START -->", "<!-- JDH-STATIC-BIBLIOGRAPHY START -->")
            joined = joined.replace("<!-- BIBLIOGRAPHY END -->", "<!-- JDH-STATIC-BIBLIOGRAPHY END -->")
            # also rewrite in case any cell didn't have a cite but still has markers
            cell["source"] = [joined] if isinstance(src, str) else joined.splitlines(keepends=True)
        else:
            # still apply marker rename to bibliography-only cells
            joined = "".join(new_lines)
            if "BIBLIOGRAPHY START" in joined or "BIBLIOGRAPHY END" in joined:
                joined = joined.replace("<!-- BIBLIOGRAPHY START -->", "<!-- JDH-STATIC-BIBLIOGRAPHY START -->")
                joined = joined.replace("<!-- BIBLIOGRAPHY END -->", "<!-- JDH-STATIC-BIBLIOGRAPHY END -->")
                cell["source"] = [joined] if isinstance(src, str) else joined.splitlines(keepends=True)

    print(f"total cite rewrites: {rewrites}")

    NB_PATH.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {NB_PATH}")


if __name__ == "__main__":
    main()
