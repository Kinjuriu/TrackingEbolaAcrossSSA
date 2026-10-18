import asyncio, os, subprocess
from playwright.async_api import async_playwright
exec(open("shoot.py").read().split("async def main")[0])   # reuse routes/fonts/page.html setup
FPS, END, W, H = 25, 53.0, 1600, 900
os.makedirs("frames", exist_ok=True)
CSS = """.page{max-width:none!important;padding:0!important}.page>:not(.stage){display:none!important}
.stage{width:1600px!important;height:900px!important;aspect-ratio:auto!important;border:0!important;border-radius:0!important}"""
async def run():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--use-angle=swiftshader","--enable-unsafe-swiftshader","--ignore-gpu-blocklist"])
        pg = await b.new_page(viewport={"width":W,"height":H}, device_scale_factor=1)
        async def route(r):
            u=r.request.url
            if "three" in u and "cdnjs" in u: return await r.fulfill(body=THREE, content_type="application/javascript")
            if "fonts.googleapis.com" in u: return await r.fulfill(body=FONT_CSS, content_type="text/css")
            if "localfonts" in u: return await r.fulfill(body=fontfile(u.rsplit('/',1)[1]), content_type="font/woff2")
            return await r.continue_()
        await pg.route("**/*", route)
        await pg.goto("file:///home/claude/render/page.html"); await pg.add_style_tag(content=CSS); await pg.wait_for_timeout(6000)
        stage = await pg.query_selector("#stage")
        n = int(END*FPS)+FPS   # hold the last frame for one extra second
        for i in range(n):
            t = min(END, i/FPS)
            await pg.evaluate(f"window.__renderAt({t})")
            await stage.screenshot(path=f"frames/f{i:05d}.png")
            if i % 100 == 0: print("frame", i, "/", n, flush=True)
        await b.close()
asyncio.run(run())
subprocess.run(["ffmpeg","-y","-loglevel","error","-framerate",str(FPS),"-i","frames/f%05d.png","-c:v","libx264","-pix_fmt","yuv420p","-crf","18","-preset","slow","-movflags","+faststart","/home/claude/ebola-rising.mp4"], check=True)
print("DONE", os.path.getsize("/home/claude/ebola-rising.mp4"))
