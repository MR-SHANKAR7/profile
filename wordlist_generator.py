#!/usr/bin/env python3
"""
WordForge - Advanced Wordlist Generator for Penetration Testing
Usage: python3 wordlist_generator.py
"""

import itertools
import sys
import os
from datetime import datetime


# ─── Transformations ─────────────────────────────────────────────────────────

LEET_MAP = str.maketrans("aeiost", "431057")

SUFFIXES_NUMBERS = [
    "", "1", "12", "123", "1234", "12345", "123456",
    "0", "00", "000", "01", "007", "69", "99", "100",
    "21", "2000", "2001", "2002", "2003", "2004", "2005",
    "2006", "2007", "2008", "2009", "2010", "2011", "2012",
    "2013", "2014", "2015", "2016", "2017", "2018", "2019",
    "2020", "2021", "2022", "2023", "2024", "2025", "2026",
]

SUFFIXES_SPECIAL = ["", "!", "!!", "@", "#", "$", "%", "&", "*", "?", ".", "_"]

PREFIXES = ["", "the", "my", "its", "mr", "ms", "dr", "admin", "user",
            "super", "root", "dev", "test", "login", "pass"]

SEPARATORS = ["", "_", "-", ".", "@", "#"]


def capitalize_variants(word: str) -> list[str]:
    """Return multiple capitalization forms of a word."""
    return list(dict.fromkeys([
        word.lower(),
        word.upper(),
        word.capitalize(),
        word.title(),
        word[0].upper() + word[1:].lower() if len(word) > 1 else word.upper(),
        word.swapcase(),
    ]))


def leet_variants(word: str) -> list[str]:
    """Apply leet-speak substitutions."""
    base = word.lower()
    leet = base.translate(LEET_MAP)
    variants = [base, leet]
    # partial leet: only vowels
    partial = base.translate(str.maketrans("aeiо", "4310"))
    variants.append(partial)
    return list(dict.fromkeys(variants))


def expand_word(word: str) -> list[str]:
    """Generate all single-word transformations."""
    results = set()
    for cap in capitalize_variants(word):
        results.add(cap)
        for leet in leet_variants(cap):
            results.add(leet)
    return list(results)


def combine_words(words: list[str]) -> list[str]:
    """Combine pairs (and triplets) of words with separators."""
    combined = []
    for r in range(2, min(len(words) + 1, 4)):
        for perm in itertools.permutations(words, r):
            for sep in SEPARATORS:
                combined.append(sep.join(perm))
    return combined


def apply_affixes(base_words: list[str]) -> list[str]:
    """Add numeric/special suffixes and common prefixes."""
    results = set()
    for word in base_words:
        for num in SUFFIXES_NUMBERS:
            for sp in SUFFIXES_SPECIAL:
                candidate = word + num + sp
                if candidate:
                    results.add(candidate)
        for pre in PREFIXES:
            if pre:
                results.add(pre + word)
                results.add(pre + "_" + word)
    return list(results)


def generate_wordlist(keywords: list[str], min_len: int = 4, max_len: int = 20) -> list[str]:
    """Full pipeline: expand → combine → affix → filter by length."""
    print("\n[*] Expanding individual keywords...")
    expanded = []
    for kw in keywords:
        expanded.extend(expand_word(kw))
    expanded = list(dict.fromkeys(expanded))
    print(f"    {len(expanded):,} words after expansion")

    print("[*] Combining keyword pairs...")
    combined = combine_words(keywords)
    all_bases = list(dict.fromkeys(expanded + combined))
    print(f"    {len(all_bases):,} words after combination")

    print("[*] Applying numeric/special affixes...")
    with_affixes = apply_affixes(all_bases)
    full_list = list(dict.fromkeys(all_bases + with_affixes))
    print(f"    {len(full_list):,} total before filtering")

    print(f"[*] Filtering: {min_len} ≤ length ≤ {max_len} ...")
    filtered = [w for w in full_list if min_len <= len(w) <= max_len]
    print(f"    {len(filtered):,} words after filtering")

    return sorted(filtered)


# ─── I/O Helpers ─────────────────────────────────────────────────────────────

def banner():
    print("""
╔══════════════════════════════════════════════════════╗
║          WordForge - Wordlist Generator              ║
║          For authorized penetration testing only     ║
╚══════════════════════════════════════════════════════╝
""")


def get_keywords() -> list[str]:
    """Prompt user for keywords interactively or via CLI argument."""
    if len(sys.argv) > 1:
        raw = " ".join(sys.argv[1:])
    else:
        print("Enter keywords separated by commas or spaces (e.g.: ahmed, 1995, cairo):")
        raw = input(">>> ").strip()

    if not raw:
        print("[-] No keywords provided. Exiting.")
        sys.exit(1)

    # split on comma or whitespace
    keywords = [k.strip().lower() for k in raw.replace(",", " ").split() if k.strip()]
    keywords = list(dict.fromkeys(keywords))
    return keywords


def get_output_path(keywords: list[str]) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = "_".join(keywords[:3])
    return f"wordlist_{slug}_{timestamp}.txt"


def save_wordlist(words: list[str], path: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(words))
    size_kb = os.path.getsize(path) / 1024
    print(f"\n[+] Saved {len(words):,} words → {path}  ({size_kb:.1f} KB)")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    banner()

    keywords = get_keywords()
    print(f"\n[*] Keywords: {keywords}")

    # Optional: ask for length limits
    try:
        min_len = int(input("Minimum word length [default 4]: ").strip() or "4")
        max_len = int(input("Maximum word length [default 20]: ").strip() or "20")
    except (ValueError, EOFError):
        min_len, max_len = 4, 20

    wordlist = generate_wordlist(keywords, min_len, max_len)

    if not wordlist:
        print("[-] No words generated. Try shorter min_len or more keywords.")
        sys.exit(1)

    out_path = get_output_path(keywords)
    save_wordlist(wordlist, out_path)

    print("\n[+] Done! You can use it with:")
    print(f"    hydra -l admin -P {out_path} <target> ssh")
    print(f"    hashcat -a 0 hash.txt {out_path}")
    print(f"    medusa -u admin -P {out_path} -h <target> -M ssh")


if __name__ == "__main__":
    main()
