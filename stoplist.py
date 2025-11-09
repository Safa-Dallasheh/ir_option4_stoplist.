#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Option 4: Build a stop-list (Top-50 frequent words) from 10 English Wikipedia pages.

Usage (online, needs internet):
  python stoplist.py --n 10 --outdir wikis --topk 50 --out top50.txt

Usage (offline, no internet; use your own .txt files):
  python stoplist.py --offline --indir texts --topk 50 --out top50.txt
"""
import os, re, argparse
from collections import Counter

TOKEN = re.compile(r"[A-Za-z]+")

def tokenize_en(text: str):
    return [t.lower() for t in TOKEN.findall(text)]

def fetch_random_titles(n=10):
    import requests
    WIKI_API = "https://en.wikipedia.org/w/api.php"
    headers = {'User-Agent': 'IROption4Student/1.0 (contact: none)'}
    params = {"action": "query", "list": "random", "rnnamespace": 0, "rnlimit": n, "format": "json"}
    r = requests.get(WIKI_API, params=params, headers=headers, timeout=30)
    r.raise_for_status()
    return [x["title"] for x in r.json()["query"]["random"]]

def fetch_page_text(title: str):
    import requests
    WIKI_API = "https://en.wikipedia.org/w/api.php"
    headers = {'User-Agent': 'IROption4Student/1.0 (contact: none)'}
    params = {"action": "query", "prop": "extracts", "explaintext": 1, "titles": title, "format": "json", "redirects": 1}
    r = requests.get(WIKI_API, params=params, headers=headers, timeout=30)
    r.raise_for_status()
    pages = r.json()["query"]["pages"]
    return next(iter(pages.values())).get("extract", "")

def run_online(n=10, outdir="wikis"):
    os.makedirs(outdir, exist_ok=True)
    tokens = []
    titles = fetch_random_titles(n)
    for i, t in enumerate(titles, 1):
        txt = fetch_page_text(t)
        with open(os.path.join(outdir, f"w{i}.txt"), "w", encoding="utf-8") as f:
            f.write(txt)
        tokens.extend(tokenize_en(txt))
    return tokens

def run_offline(indir="texts"):
    tokens = []
    for fname in sorted(os.listdir(indir)):
        if not fname.endswith(".txt"): 
            continue
        with open(os.path.join(indir, fname), "r", encoding="utf-8", errors="ignore") as f:
            tokens.extend(tokenize_en(f.read()))
    return tokens

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=10, help="Number of random Wikipedia pages (online mode)")
    ap.add_argument("--outdir", default="wikis", help="Where to save fetched pages (online mode)")
    ap.add_argument("--topk", type=int, default=50, help="Top-K frequent words")
    ap.add_argument("--out", default="top50.txt", help="Output file for top-K")
    ap.add_argument("--offline", action="store_true", help="Offline mode (use --indir with local .txt files)")
    ap.add_argument("--indir", default="texts", help="Folder with .txt files (offline mode)")
    args = ap.parse_args()

    if args.offline:
        tokens = run_offline(args.indir)
    else:
        tokens = run_online(args.n, args.outdir)

    freq = Counter(tokens)
    top = freq.most_common(args.topk)

    with open(args.out, "w", encoding="utf-8") as f:
        for w, c in top:
            f.write(f"{w}\t{c}\n")

    print(f"Top {args.topk} words:")
    for w, c in top[:10]:
        print(f"{w:>15s}  {c}")
    print(f"\nSaved top list to: {args.out}")
    if not args.offline:
        print(f"Saved raw pages to: {args.outdir}")

if __name__ == "__main__":
    main()
  
