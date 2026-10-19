import asyncio, os, subprocess, json
from playwright.async_api import async_playwright
exec(open("/home/claude/render/shoot.py").read().split("body=open")[0])
body=open("/home/claude/ebola-scroll.html").read()
open("/home/claude/render/scroll.html","w").write('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><style>body{margin:0}[hidden]{display:none!important}</style></head><body>'+body+'</body></html>')
FPS,W,H=25,1600,900
HOLD,MOVE=2.2,2.0           # seconds held on each card, seconds moving to the next
os.makedirs("vframes",exist_ok=True)
for f in os.listdir("vframes"): os.remove("vframes/"+f)
async def run():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=["--use-angle=swiftshader","--enable-unsafe-swiftshader","--ignore-gpu-blocklist"])
        pg=await b.new_page(viewport={"width":W,"height":H})
        async def route(r):
            u=r.request.url
            if "three" in u and "cdnjs" in u: return await r.fulfill(body=THREE, content_type="application/javascript")
            if "fonts.googleapis.com" in u: return await r.fulfill(body=FONT_CSS, content_type="text/css")
            if "localfonts" in u: return await r.fulfill(body=fontfile(u.rsplit('/',1)[1]), content_type="font/woff2")
            return await r.continue_()
        await pg.route("**/*", route)
        await pg.goto("file:///home/claude/render/scroll.html"); await pg.add_style_tag(content=".after{display:none!important}"); await pg.wait_for_timeout(7000)
        steps=await pg.evaluate("""[...document.querySelectorAll('.step')].map(s=>{const r=s.getBoundingClientRect(); return {t:+s.dataset.t, c:r.top+window.scrollY+r.height/2};})""")
        # timeline: hold on each step, then glide to the next (story time and scroll move together)
        seq=[]
        for i,s in enumerate(steps):
            hold = HOLD+1.0 if i in (0,len(steps)-1) else HOLD
            seq += [(s["t"], s["c"])]*int(hold*FPS)
            if i<len(steps)-1:
                n=steps[i+1]; k=int(MOVE*FPS)
                for j in range(1,k+1):
                    u=j/k; u=u*u*(3-2*u); seq.append((s["t"]+(n["t"]-s["t"])*u, s["c"]+(n["c"]-s["c"])*u))
        print("frames", len(seq), "seconds", len(seq)/FPS, flush=True)
        for i,(t,c) in enumerate(seq):
            await pg.evaluate(f"window.scrollTo(0,{c}-{H}*0.55); window.__renderAt({t});")
            await pg.screenshot(path=f"vframes/f{i:05d}.png")
            if i%200==0: print("frame",i,flush=True)
        await b.close()
asyncio.run(run())
subprocess.run(["ffmpeg","-y","-loglevel","error","-framerate",str(FPS),"-i","vframes/f%05d.png","-c:v","libx264","-preset","slow","-crf","22","-pix_fmt","yuv420p","-profile:v","high","-movflags","+faststart","/home/claude/ebola-across-africa.mp4"],check=True)
print("DONE", os.path.getsize("/home/claude/ebola-across-africa.mp4"))
