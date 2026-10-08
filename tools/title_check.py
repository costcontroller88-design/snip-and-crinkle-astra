"""Flag a title that repeats an earlier one (template risk, hard rule 5; agent ratings 8 Oct, fix 5).

    python3 tools/title_check.py reviews/ep11_short_transform_upload.md   (packaging, before returning)
    python3 tools/title_check.py --title "Pip's Pumpkin Glows! ..."       (growth-analyst, any title)

Exits 1 when the sheet has no `**Title:**` line. In --title mode an old title with the same core words is skipped
(the live title is quoted in the log and its own sheet). Compares each `**Title:**` line of the sheet with the titles of the last 5 other upload sheets and the quoted titles
in docs/analytics-log.md. FAIL (exit 1) when, after dropping the brand and emoji: the word sets overlap ≥50%; the
first two words are the same; or its shape (length band, end mark, opening name) matches ≥3 of the last 5.
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAMES = ("snip", "crinkle", "pip")


def core(t):
    t = t.split("|")[0]
    return re.sub(r"[^\w\s'?!]", " ", t).lower().split()


def shape(ws):
    end = "?" if ws and ws[-1].endswith("?") else "!" if any(w.endswith("!") for w in ws) else "."
    return (min(len(ws) // 3, 3), end, ws[0].strip("'s!?") in NAMES if ws else False)


def titles_in(path):
    return re.findall(r"^\*\*Title:\*\*\s*(.+)$", open(path, encoding="utf-8").read(), re.M)


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    if args[0] == "--title":
        new, own = [" ".join(args[1:])], None
    else:
        own = os.path.abspath(args[0])
        new = titles_in(own)
        if not new:
            print("title_check: FAIL no `**Title:**` line in the sheet (write each option as `**Title:** <text>`, your pick first)")
            sys.exit(1)
    sheets = sorted((p for p in glob.glob(os.path.join(ROOT, "reviews", "*_upload.md")) if os.path.abspath(p) != own),
                    key=os.path.getmtime)[-5:]
    old = [t for p in sheets for t in titles_in(p)[:1]]   # the first title in a sheet is its pick
    log = os.path.join(ROOT, "docs", "analytics-log.md")
    if os.path.exists(log):
        old += re.findall(r"\"([^\"]{4,80})\"", open(log, encoding="utf-8").read())
    old = list(dict.fromkeys(old))
    fails = []
    for t in new:
        w = core(t)
        for o in old:
            v = core(o)
            if not w or not v:
                continue
            if own is None and set(w) == set(v):
                continue   # --title: the live title's own quote in the log or sheet is not a repeat
            overlap = len(set(w) & set(v)) / min(len(set(w)), len(set(v)))
            if overlap >= 0.5:
                fails.append(f"'{t[:50]}' shares {overlap:.0%} of its words with '{o[:50]}'")
            elif w[:2] == v[:2]:
                fails.append(f"'{t[:50]}' opens like '{o[:50]}'")
        same = sum(shape(core(o)) == shape(w) for o in old[-5:])
        if same >= 3:
            fails.append(f"'{t[:50]}' has the same shape as {same} of the last 5 titles")
    for f in fails:
        print("FAIL", f)
    print(f"title_check: compared with {len(old)} titles;", "PASS" if not fails else f"{len(fails)} failure(s)")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
