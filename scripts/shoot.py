import asyncio, sys, os
from playwright.async_api import async_playwright
V="/home/claude/vendor"
THREE=open(f"{V}/three-0.128.0/package/build/three.min.js","rb").read()
FONT_CSS = ""
for fam, files in {"Fira Sans":[(w,"normal",f"fira-sans-latin-{w}-normal") for w in ["300","400","500","600","700"]],
                   "Sacramento":[("400","normal","sacramento-latin-400-normal")]}.items():
    for w,st,f in files:
        FONT_CSS += f"@font-face{{font-family:'{fam}';font-style:{st};font-weight:{w};src:url(http://localfonts/{f}.woff2) format('woff2');}}\n"
def fontfile(name):
    for d in ["fontsource-fira-sans-5.0.20","fontsource-sacramento-5.0.19"]:
        p=f"{V}/{d}/package/files/{name}"
        if os.path.exists(p): return open(p,"rb").read()
body=open("/home/claude/ebola-rising.html").read()
open("/home/claude/render/page.html","w").write('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><style>body{margin:0}[hidden]{display:none!important}</style></head><body>'+body+'</body></html>')
async def main(width, height, times, prefix):
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--use-angle=swiftshader","--enable-unsafe-swiftshader","--ignore-gpu-blocklist"])
        pg = await b.new_page(viewport={"width":width,"height":height}, device_scale_factor=1)
        async def route(r):
            u=r.request.url
            if "three" in u and "cdnjs" in u: return await r.fulfill(body=THREE, content_type="application/javascript")
            if "fonts.googleapis.com" in u: return await r.fulfill(body=FONT_CSS, content_type="text/css")
            if "localfonts" in u: return await r.fulfill(body=fontfile(u.rsplit('/',1)[1]), content_type="font/woff2")
            return await r.continue_()
        await pg.route("**/*", route)
        msgs=[]; pg.on("console", lambda m: msgs.append(m.type+": "+m.text)); pg.on("pageerror", lambda e: msgs.append("PAGEERROR: "+str(e)))
        await pg.goto("file:///home/claude/render/page.html"); await pg.wait_for_timeout(5000)
        for t in times:
            await pg.evaluate(f"window.__renderAt({t})"); await pg.wait_for_timeout(150)
            await pg.screenshot(path=f"/home/claude/render/{prefix}_{t}.png")
        print("\n".join(msgs[:20]) or "no console messages")
        await b.close()
if __name__=="__main__":
    w,h=int(sys.argv[1]),int(sys.argv[2]); prefix=sys.argv[3]; times=[float(x) for x in sys.argv[4:]]
    asyncio.run(main(w,h,times,prefix))
