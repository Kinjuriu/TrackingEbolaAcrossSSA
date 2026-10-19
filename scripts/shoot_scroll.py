import asyncio, sys, os
from playwright.async_api import async_playwright
exec(open("/home/claude/render/shoot.py").read().split("body=open")[0])
body=open("/home/claude/ebola-scroll.html").read()
open("/home/claude/render/scroll.html","w").write('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><style>body{margin:0}[hidden]{display:none!important}</style></head><body>'+body+'</body></html>')
async def main(w,h,ts,prefix):
    async with async_playwright() as p:
        b=await p.chromium.launch(args=["--use-angle=swiftshader","--enable-unsafe-swiftshader","--ignore-gpu-blocklist"])
        pg=await b.new_page(viewport={"width":w,"height":h})
        async def route(r):
            u=r.request.url
            if "three" in u and "cdnjs" in u: return await r.fulfill(body=THREE, content_type="application/javascript")
            if "fonts.googleapis.com" in u: return await r.fulfill(body=FONT_CSS, content_type="text/css")
            if "localfonts" in u: return await r.fulfill(body=fontfile(u.rsplit('/',1)[1]), content_type="font/woff2")
            return await r.continue_()
        await pg.route("**/*", route)
        msgs=[]; pg.on("console", lambda m: msgs.append(m.type+": "+m.text)); pg.on("pageerror", lambda e: msgs.append("PAGEERROR: "+str(e)))
        await pg.goto("file:///home/claude/render/scroll.html"); await pg.wait_for_timeout(6000)
        for t in ts:
            await pg.evaluate(f"""(()=>{{ const s=[...document.querySelectorAll('.step')].sort((a,b)=>Math.abs(a.dataset.t-{t})-Math.abs(b.dataset.t-{t}))[0]; s.scrollIntoView({{block:'center'}}); }})()""")
            await pg.wait_for_timeout(200)
            await pg.evaluate(f"window.__renderAt({t})"); await pg.wait_for_timeout(250)
            await pg.screenshot(path=f"/home/claude/render/{prefix}_{t}.png")
        print("\n".join(msgs[:20]) or "no console messages"); await b.close()
w,h=int(sys.argv[1]),int(sys.argv[2]); prefix=sys.argv[3]; ts=[float(x) for x in sys.argv[4:]]
asyncio.run(main(w,h,ts,prefix))
