"""Stills the site needs, taken with headless Chrome and saved as WebP in docs/img/:

- poster-wide.webp, poster-tall.webp: the story's first frame, shown while the 3D map loads
- dashboard-preview.webp: the top of the dashboard as it is now, for the band at the end of the story

build_scroll.py runs this after every build; run it on its own after editing docs/dashboard.html:
    python3 scripts/shoot_stills.py
Set CHROME to the browser binary if it is not in a standard place.
"""
import functools, http.server, os, shutil, subprocess, tempfile, threading
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
IMG = os.path.join(DOCS, "img")


def chrome():
    for c in [os.environ.get("CHROME"), "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
              "/Applications/Chromium.app/Contents/MacOS/Chromium"] + [shutil.which(n) for n in ("google-chrome", "chromium", "chromium-browser")]:
        if c and os.path.exists(c):
            return c
    return None


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def shoot(browser, url, w, h, scale, out_png):
    subprocess.run([browser, "--headless=new", "--hide-scrollbars", "--use-angle=swiftshader", "--enable-unsafe-swiftshader",
                    "--window-size=%d,%d" % (w, h), "--force-device-scale-factor=%s" % scale,
                    "--virtual-time-budget=20000", "--screenshot=" + out_png, url],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main(which=("posters", "preview")):
    browser = chrome()
    if not browser:
        print("shoot_stills: Chrome not found, stills not updated (set CHROME=/path/to/chrome)")
        return False
    os.makedirs(IMG, exist_ok=True)
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=DOCS))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = "http://127.0.0.1:%d/" % srv.server_address[1]
    tmp = tempfile.mkdtemp()
    jobs = []
    if "posters" in which:
        jobs += [("index.html?poster", 1440, 900, 1, "poster-wide.webp", 70),
                 ("index.html?poster", 390, 844, 2, "poster-tall.webp", 70)]
    if "preview" in which:
        jobs += [("dashboard.html", 1100, 890, 1, "dashboard-preview.webp", 82)]
    try:
        for path, w, h, scale, name, q in jobs:
            png = os.path.join(tmp, name + ".png")
            shoot(browser, base + path, w, h, scale, png)
            Image.open(png).convert("RGB").save(os.path.join(IMG, name), "WEBP", quality=q, method=6)
            print("shoot_stills: wrote docs/img/" + name)
    finally:
        srv.shutdown()
        shutil.rmtree(tmp, ignore_errors=True)
    return True


if __name__ == "__main__":
    main()
