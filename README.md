<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=30&pause=1000&color=00FF41&background=000000&center=true&vCenter=true&width=600&lines=WordForge+%F0%9F%94%A8;Advanced+Wordlist+Generator;Kali+Linux+%7C+Python+3;Ethical+Hacking+Tool" alt="WordForge Typing SVG" />

# WordForge — Advanced Wordlist Generator

**A fast, intelligent Python-based wordlist generator for authorized penetration testing, CTF challenges, and security research.**

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Kali Linux](https://img.shields.io/badge/Kali_Linux-Compatible-557C94?style=for-the-badge&logo=kalilinux&logoColor=white)](https://kali.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS-lightgrey?style=for-the-badge&logo=linux&logoColor=white)](https://github.com)
[![Ethical](https://img.shields.io/badge/Use-Ethical%20Hacking%20Only-red?style=for-the-badge)](https://github.com)

</div>

---

## What is WordForge?

**WordForge** is a Python 3 tool that transforms a small set of keywords into a **large, intelligent wordlist** ready for password auditing and security assessments. Unlike simple character-brute-force tools, WordForge understands patterns humans actually use when creating passwords — combining names, dates, leet-speak, and special characters in a smart, layered pipeline.

> Ideal for: **CTF competitions**, **red team engagements**, **Wi-Fi password auditing**, and **web login testing** on systems you own or have written authorization to test.

---

## Features

| Feature | Description |
|---|---|
| **Keyword Combinations** | Mixes all keywords in every order with separators (`_`, `-`, `.`, `@`, `#`) |
| **Capitalization Variants** | `lower`, `UPPER`, `Capitalize`, `Title`, `sWAPcASE` for every word |
| **Leet Speak** | `a→4`, `e→3`, `i→1`, `o→0`, `s→5`, `t→7` — full and partial substitution |
| **Numeric Suffixes** | Appends `1`, `123`, `007`, `99`, `2000–2026` and more |
| **Special Characters** | Appends `!`, `@`, `#`, `$`, `%`, `&`, `*`, `?` to every candidate |
| **Common Prefixes** | Prepends `admin`, `root`, `user`, `super`, `dev`, `mr`, `dr`, etc. |
| **Length Filter** | You control min/max word length — cut file size to what you need |
| **Zero Dependencies** | Pure Python 3 standard library — no pip install required |

---

## Demo

```
╔══════════════════════════════════════════════════════╗
║          WordForge - Wordlist Generator              ║
║          For authorized penetration testing only     ║
╚══════════════════════════════════════════════════════╝

Enter keywords separated by commas or spaces (e.g.: ahmed, 1995, cairo):
>>> ahmed, 1995, cairo

[*] Keywords: ['ahmed', '1995', 'cairo']
Minimum word length [default 4]: 4
Maximum word length [default 20]: 20

[*] Expanding individual keywords...
    10 words after expansion
[*] Combining keyword pairs...
    82 words after combination
[*] Applying numeric/special affixes...
    44,608 total before filtering
[*] Filtering: 4 ≤ length ≤ 20 ...
    34,156 words after filtering

[+] Saved 34,156 words → wordlist_ahmed_1995_cairo_20250101_120000.txt  (530.4 KB)

[+] Done! You can use it with:
    hydra -l admin -P wordlist_ahmed_1995_cairo_20250101_120000.txt <target> ssh
    hashcat -a 0 hash.txt wordlist_ahmed_1995_cairo_20250101_120000.txt
    medusa -u admin -P wordlist_ahmed_1995_cairo_20250101_120000.txt -h <target> -M ssh
```

### Sample Output Words

```
ahmed
4hm3d
AHMED
Ahmed123
ahmed2024!
ahmed_cairo
cairo_ahmed_1995
1995#ahmed@
4hm3d_c41r0
adminahmed!
Ahmed1995#
cairo2024!
ahmed@cairo
1995-ahmed-cairo
```

---

## Installation

**No installation needed.** WordForge uses only Python's standard library.

```bash
# Clone the repository
git clone https://github.com/MR-SHANKAR7/profile.git
cd profile

# Make executable (optional)
chmod +x wordlist_generator.py

# Run it
python3 wordlist_generator.py
```

**Requirements:**
- Python 3.8 or higher
- Linux / macOS / WSL (optimized for Kali Linux)

---

## Usage

### Interactive Mode

```bash
python3 wordlist_generator.py
```

You will be prompted to enter:
1. Keywords (comma or space separated)
2. Minimum word length (default: 4)
3. Maximum word length (default: 20)

### Inline Mode

```bash
python3 wordlist_generator.py target_name birth_year city_name
```

---

## Integration with Popular Tools

Once your wordlist is generated, plug it directly into your favorite tools:

```bash
# Hydra — SSH brute force
hydra -l admin -P wordlist_output.txt 192.168.1.1 ssh

# Hydra — Web login form
hydra -l admin -P wordlist_output.txt 192.168.1.1 http-post-form "/login:user=^USER^&pass=^PASS^:F=incorrect"

# Hashcat — Hash cracking (mode 0 = MD5, 400 = WPA, etc.)
hashcat -a 0 -m 0 hashes.txt wordlist_output.txt

# Medusa — Multi-protocol
medusa -u admin -P wordlist_output.txt -h 192.168.1.1 -M ssh

# John the Ripper
john --wordlist=wordlist_output.txt hashes.txt

# Aircrack-ng — Wi-Fi WPA
aircrack-ng -w wordlist_output.txt -b AA:BB:CC:DD:EE:FF capture.cap
```

---

## How It Works — Pipeline

```
Keywords Input
      │
      ▼
 ┌─────────────────────────┐
 │  1. Expand Each Keyword  │  lowercase, UPPER, Capitalize, swapCase
 │     + Leet Speak         │  a→4, e→3, i→1, o→0, s→5, t→7
 └──────────┬──────────────┘
            │
            ▼
 ┌─────────────────────────┐
 │  2. Combine Keywords     │  pairs & triplets, all permutations
 │     with Separators      │  _, -, ., @, #, (none)
 └──────────┬──────────────┘
            │
            ▼
 ┌─────────────────────────┐
 │  3. Apply Affixes        │  numeric suffixes (123, 2024, 007…)
 │                          │  special chars (!, @, #, $…)
 │                          │  prefixes (admin, root, user…)
 └──────────┬──────────────┘
            │
            ▼
 ┌─────────────────────────┐
 │  4. Deduplicate          │  remove all duplicate entries
 │  5. Filter by Length     │  keep only words within your range
 └──────────┬──────────────┘
            │
            ▼
     wordlist_output.txt
```

---

## Keyword Tips for Better Results

To get the most relevant wordlist, use keywords that reflect the target's personal info (during an authorized engagement):

| Category | Examples |
|---|---|
| Names | `john`, `admin`, `root`, `target_name` |
| Dates | `1990`, `2001`, `0101` |
| Locations | `london`, `cairo`, `newyork` |
| Interests | `football`, `music`, `python` |
| Company | `companyname`, `corp`, `inc` |
| Common patterns | `password`, `secure`, `login` |

> More meaningful keywords = more targeted wordlist = higher success rate.

---

## Performance

| Keywords | Words Generated | File Size |
|---|---|---|
| 2 keywords | ~8,000 words | ~120 KB |
| 3 keywords | ~34,000 words | ~530 KB |
| 5 keywords | ~150,000 words | ~2.5 MB |
| 8 keywords | ~900,000 words | ~15 MB |

---

## Legal Disclaimer

> **This tool is intended exclusively for:**
> - Authorized penetration testing engagements
> - CTF (Capture The Flag) competitions
> - Security research on systems you own
> - Educational purposes
>
> **Unauthorized use of this tool against systems you do not own or have explicit written permission to test is illegal and unethical.**
>
> The author assumes no liability for misuse or damage caused by this tool.

---

## Contributing

Pull requests are welcome! Ideas for improvement:

- [ ] Add Markov chain–based word generation
- [ ] Add `--language` flag for locale-specific patterns (Arabic, French, Spanish…)
- [ ] Add GUI interface (Tkinter / web UI)
- [ ] Add rule-based mutation engine (like hashcat rules)
- [ ] Add OSINT integration (scrape social media bio keywords)

---

## Author

**MR-SHANKAR7**
- GitHub: [@MR-SHANKAR7](https://github.com/MR-SHANKAR7)

---

<div align="center">

**If this tool helped you, please give it a ⭐ — it helps others find it!**

*Built for the security community with ❤️*

</div>
