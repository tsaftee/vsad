#!/usr/bin/env python3
"""
Descarca pachetul Opera GX (.deb) folosind SeleniumBase.

Pasi:
  1. Acceseaza https://operagx.gg/brutallesaff
  2. Asteapta 10 secunde pentru incarcarea paginii
  3. Da click pe butonul "Download Opera GX" (<span class="cta">)
  4. Asteapta pana la 2 minute ca fisierul .deb sa apara in folderul
     default SeleniumBase: ./downloaded_files
"""
import glob
import os
import time

from seleniumbase import SB

URL = "https://operagx.gg/brutallesaff"
DOWNLOAD_DIR = "downloaded_files"  # folderul default folosit de SeleniumBase

# Ne asiguram ca folderul de download exista inainte de start.
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

with SB(browser="chrome", headless=True) as sb:
    print(f"[*] Accesam {URL} ...")
    sb.open(URL)
    sb.set_window_size(1280, 1024)

    print("[*] Asteptam 10 secunde pentru incarcarea completa a paginii ...")
    sb.sleep(10)

    # Butonul tinta: <span class="cta">Download Opera GX</span>
    # Incercam mai multi selectori in caz ca structura difera usor.
    print('[*] Dam click pe "Download Opera GX" ...')
    selectors = [
        "span.cta",
        "xpath=//span[contains(@class,'cta')]",
        "xpath=//*[contains(normalize-space(), 'Download Opera GX')]",
        "xpath=//a[contains(., 'Download Opera')]",
    ]
    clicked = False
    for sel in selectors:
        try:
            sb.click(sel, timeout=12)
            clicked = True
            print(f"[+] Click reusit cu selectorul: {sel}")
            break
        except Exception as e:
            print(f"[!] Selectorul {sel!r} a esuat: {e}")

    if not clicked:
        # Ultima varianta: click prin JavaScript (trece pe deasupra overlay-urilor)
        try:
            sb.js_click("span.cta")
            print("[+] Click reusit prin js_click pe span.cta")
        except Exception as e:
            print(f"[!] js_click a esuat de asemenea: {e}")

    print("[*] Asteptam pana la 2 minute pentru finalizarea downloadului .deb ...")
    deadline = time.time() + 120
    found = None
    while time.time() < deadline:
        candidates = [
            f for f in glob.glob(os.path.join(DOWNLOAD_DIR, "opera*.deb"))
            if not f.endswith(".crdownload")  # ignoram fisierele partiale Chrome
        ]
        if candidates:
            found = sorted(candidates)[0]
            break
        time.sleep(5)

    if found:
        print(f"[+] Download finalizat: {found}")
    else:
        print("[!] NU s-a gasit opera*.deb dupa 2 minute.")
        print("    Continut downloaded_files:", os.listdir(DOWNLOAD_DIR))
