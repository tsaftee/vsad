"""Pas 1+2 din workflow:
1. Deschide https://operagx.gg/brutallesaff cu SeleniumBase (Chrome).
2. Asteapta 10 secunde.
3. Da click pe <span class="cta">Download Opera GX</span>.
4. Asteapta 2 minute (plus polling suplimentar) pentru a se completa download-ul.
   SeleniumBase descarca implicit in folderul: ./downloaded_files/
"""
import glob
import os
import sys
import time

from seleniumbase import SB

URL = "https://operagx.gg/brutallesaff"
PAUSE_BEFORE_CLICK = 20       # secunde de asteptare dupa incarcarea paginii
WAIT_AFTER_CLICK = 40        # asteptare fixa de 2 minute (conform cerintei)
EXTRA_POLL_SECONDS = 90       # polling suplimentar daca download-ul inca ruleaza
DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloaded_files")


def find_installer():
    """Returneaza cel mai recent 'opera*.exe' complet descarcat, sau None."""
    pattern = os.path.join(DOWNLOAD_DIR, "opera*.exe")
    files = [f for f in glob.glob(pattern) if not f.lower().endswith(".crdownload")]
    return max(files, key=os.path.getmtime) if files else None


def click_cta(sb):
    """Da click pe butonul cu <span class='cta'>Download Opera GX</span>,
    incercand mai multe selectoare + un fallback JavaScript."""
    attempts = [
        ("span.cta", lambda: sb.click("span.cta", timeout=15)),
        ("a:has(span.cta)", lambda: sb.click("a:has(span.cta)", timeout=10)),
        ("button:has(span.cta)", lambda: sb.click("button:has(span.cta)", timeout=10)),
        ('a[href*="download.opera.com"]', lambda: sb.click('a[href*="download.opera.com"]', timeout=10)),
    ]
    for label, action in attempts:
        try:
            action()
            print(f"   [OK] click reusit pe '{label}'")
            return
        except Exception as exc:
            print(f"   [warn] '{label}' esuat: {type(exc).__name__}")
    # Ultimul recurs: click JS direct pe span.cta (sau pe parintele lui clickable)
    print("   [warn] Selectoarele au esuat; incerc click JS pe span.cta")
    sb.execute_script(
        "var el = document.querySelector('span.cta');"
        "if (el) { (el.closest('a') || el.closest('button') || el).click(); }"
    )
    sb.sleep(5)


def main():
    print(f"[1] Deschid {URL}")
    with SB(uc=True, headed=True, locale="en") as sb:
        sb.open("https://www.twitch.tv/brutalles") 
        sb.sleep(PAUSE_BEFORE_CLICK)
        sb.open(URL)

        print(f"[2] Astept {PAUSE_BEFORE_CLICK} secunde...")
        sb.sleep(PAUSE_BEFORE_CLICK)

        print("[3] Caut butonul 'Download Opera GX' (span.cta)...")
        click_cta(sb)

        print(f"[4] Astept {WAIT_AFTER_CLICK} secunde (2 min) pentru descarcare...")
        sb.sleep(WAIT_AFTER_CLICK)

        installer = find_installer()
        if installer is None:
            print(f"[5] Fisierul inca nu e gata; polling pana la {EXTRA_POLL_SECONDS}s...")
            deadline = time.time() + EXTRA_POLL_SECONDS
            while time.time() < deadline and installer is None:
                time.sleep(3)
                installer = find_installer()

        if installer is None:
            print(f"EROARE: nu s-a gasit niciun 'opera*.exe' in {DOWNLOAD_DIR}",
                  file=sys.stderr)
            sys.exit(1)

        size_mb = os.path.getsize(installer) / (1024 * 1024)
        print(f"[5] Download complet: {installer} ({size_mb:.1f} MB)")

    print("[6] Browser inchis. Pasul SeleniumBase s-a terminat.")


if __name__ == "__main__":
    main()
