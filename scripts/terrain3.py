"""Bake sharp terrain chunks from Sentinel-2 cloudless (EOX, 2016, CC BY 4.0) and AWS Terrain Tiles.
Outputs equirectangular chunk textures (JPEG), a global height grid, and dims.json."""
import numpy as np, json, base64, os, io
from PIL import Image
from scipy.ndimage import map_coordinates, gaussian_filter
Image.MAX_IMAGE_PIXELS = None
SRC = "/mnt/user-data/uploads/Downloads"
OUT = "/home/claude/tex3"; os.makedirs(OUT, exist_ok=True)

LON0, LON1, LAT0, LAT1 = -24.0, 52.0, -16.0, 24.0
CLON = [-24, -14.5, -5, 4.5, 14, 23.5, 33, 42.5, 52]
CLAT = [-16, -6, 4, 14, 24]
LO_PPD, HI_PPD = 64, 160            # texture pixels per degree (base / detail chunks)

def merc_px(lon, lat, z, x0, y0):
    n = 2**z * 256
    px = (lon + 180) / 360 * n - x0*256
    lr = np.radians(np.clip(lat, -85, 85))
    py = (1 - np.arcsinh(np.tan(lr)) / np.pi) / 2 * n - y0*256
    return px, py

class Mosaic:
    def __init__(self, arr, z, x0, y0, ox=0, oy=0, w=None, h=None):
        self.a = arr; self.z, self.x0, self.y0, self.ox, self.oy = z, x0, y0, ox, oy
        self.w = w or arr.shape[1]; self.h = h or arr.shape[0]
    def sample(self, lon, lat, order=1):
        px, py = merc_px(lon, lat, self.z, self.x0, self.y0)
        inside = (px >= 1) & (px < self.w-2) & (py >= 1) & (py < self.h-2)
        # feather weight near the patch edge (in source pixels)
        edge = np.minimum.reduce([px, self.w-1-px, py, self.h-1-py])
        wgt = np.clip(edge/48.0, 0, 1) * inside
        X, Y = px + self.ox, py + self.oy
        a = self.a
        if a.ndim == 2:
            v = map_coordinates(a, [Y, X], order=order, mode='nearest')
        else:
            v = np.stack([map_coordinates(a[..., c], [Y, X], order=order, mode='nearest') for c in range(a.shape[2])], -1)
        return v, wgt

def terrarium(path):
    t = np.asarray(Image.open(path).convert("RGB")).astype(np.float32)
    return t[..., 0]*256 + t[..., 1] + t[..., 2]/256 - 32768

print("loading sources")
s2_base = Mosaic(np.asarray(Image.open(f"{SRC}/s2cloudless2024_z7_x55-82_y55-69.jpg").convert("RGB")).astype(np.float32)/255, 7, 55, 55)
pack = np.asarray(Image.open(f"{SRC}/s2cloudless2024_detail_pack.jpg").convert("RGB")).astype(np.float32)/255
s2_det = [Mosaic(pack, 9, 292, 250, 0, 0, 4864, 3072), Mosaic(pack, 8, 140, 128, 0, 3072, 1792, 1536), Mosaic(pack, 8, 117, 119, 1792, 3072, 1792, 1792)]
dem_base = Mosaic(terrarium(f"{SRC}/terrarium_z7_x55-82_y55-69.png"), 7, 55, 55)
dem_det = [Mosaic(terrarium(f"{SRC}/terrarium_z9_x292-310_y250-261.png"), 9, 292, 250),
           Mosaic(terrarium(f"{SRC}/terrarium_z8_x140-146_y128-133.png"), 8, 140, 128),
           Mosaic(terrarium(f"{SRC}/terrarium_z8_x117-123_y119-125.png"), 8, 117, 119)]
DET_BOX = [(25.31, 38.67, -4.21, 4.21), (16.87, 23.20, -8.41, 0.0), (-15.47, -5.62, 4.21, 12.55)]

def sample_all(lon, lat, base, dets):
    v, _ = base.sample(lon, lat)
    for d in dets:
        dv, w = d.sample(lon, lat)
        if w.max() == 0: continue
        ww = w[..., None] if v.ndim == 3 else w
        v = v*(1-ww) + dv*ww
    return v

def hillshade(e, ppd, z=3.2):
    # e in metres on an equirect grid with ppd pixels per degree
    e = gaussian_filter(e, 0.7)
    dx_m = 111320/ppd
    gy, gx = np.gradient(e*z, dx_m)
    az, alt = np.radians(315), np.radians(42)
    slope = np.arctan(np.hypot(gx, gy)); aspect = np.arctan2(-gx, gy)
    return np.clip(np.sin(alt)*np.cos(slope) + np.cos(alt)*np.sin(slope)*np.cos(az-aspect), 0, 1)

from PIL import ImageDraw
_lk = json.load(open("/home/claude/ne/ne_10m_lakes.geojson"))["features"]
_ad = json.load(open("/home/claude/ne/ne_10m_admin_0_countries.geojson"))["features"]
def _polys(feats):
    out=[]
    for f in feats:
        g=f["geometry"];
        if not g: continue
        P=g["coordinates"] if g["type"]=="MultiPolygon" else [g["coordinates"]]
        for poly in P:
            xs=[p[0] for p in poly[0]]; ys=[p[1] for p in poly[0]]
            if max(xs)<LON0-1 or min(xs)>LON1+1 or max(ys)<LAT0-1 or min(ys)>LAT1+1: continue
            out.append(poly)
    return out
LAKES=_polys(_lk); LAND=_polys(_ad)
def water_mask(lo0, la1, ppd, W, H):
    im=Image.new("L",(W,H),255); d=ImageDraw.Draw(im)
    tr=lambda ring:[((x-lo0)*ppd,(la1-y)*ppd) for x,y in ring]
    for poly in LAND:
        d.polygon(tr(poly[0]),fill=0)
        for hole in poly[1:]: d.polygon(tr(hole),fill=255)
    for poly in LAKES: d.polygon(tr(poly[0]),fill=255)
    return gaussian_filter(np.asarray(im).astype(np.float32)/255, 0.8)

def overlaps(c, box):
    return not (c[1] <= box[0] or c[0] >= box[1] or c[3] <= box[2] or c[2] >= box[3])

chunks = []
for j in range(len(CLAT)-1):
    for i in range(len(CLON)-1):
        lo0, lo1, la0, la1 = CLON[i], CLON[i+1], CLAT[j], CLAT[j+1]
        hi = any(overlaps((lo0, lo1, la0, la1), b) for b in DET_BOX)
        ppd = HI_PPD if hi else LO_PPD
        W, H = int(round((lo1-lo0)*ppd)), int(round((la1-la0)*ppd))
        # pad one pixel ring for hillshade gradients
        lons = lo0 + (np.arange(-1, W+1)+0.5)/ppd
        lats = la1 - (np.arange(-1, H+1)+0.5)/ppd
        LON, LAT = np.meshgrid(lons, lats)
        rgb = sample_all(LON, LAT, s2_base, s2_det if hi else [])
        dem = sample_all(LON, LAT, dem_base, dem_det if hi else [])
        sh = hillshade(dem, ppd)[1:-1, 1:-1]; rgb = rgb[1:-1, 1:-1]; demc = dem[1:-1, 1:-1]
        r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
        water = water_mask(lo0, la1, ppd, W, H)
        lum = 0.3*r + 0.59*g + 0.11*b
        sat = 0.95
        c = rgb*sat + lum[..., None]*(1-sat)
        c = np.clip((c-0.02)*1.12, 0, 1)
        c = np.power(c, 0.9)
        c = c*(0.55 + 0.62*sh[..., None])            # relief
        c = np.clip(c*1.0, 0, 1)
        ocean = np.array([0.028, 0.045, 0.055])
        c = c*(1-water[..., None]) + np.clip(rgb*0.75, 0, 1)*water[..., None]
        # fade outer rim of the whole map into the background
        LONc, LATc = LON[1:-1, 1:-1], LAT[1:-1, 1:-1]
        m = np.minimum.reduce([(LONc-LON0)/(LON1-LON0), (LON1-LONc)/(LON1-LON0), (LATc-LAT0)/(LAT1-LAT0), (LAT1-LATc)/(LAT1-LAT0)])
        edge = np.ones_like(m)[..., None]
        c = c*edge + np.array([0.020, 0.031, 0.031])*(1-edge)
        im = Image.fromarray((np.clip(c, 0, 1)*255).astype(np.uint8))
        buf = io.BytesIO(); im.save(buf, "JPEG", quality=82 if hi else 80, optimize=True, progressive=True)
        name = f"c{j}{i}.jpg"; open(f"{OUT}/{name}", "wb").write(buf.getvalue())
        chunks.append({"b": [lo0, lo1, la0, la1], "f": name, "hi": hi, "bytes": len(buf.getvalue())})
        print(name, (W, H), "hi" if hi else "lo", len(buf.getvalue())//1024, "KB")

# global height grid for geometry (0.08 deg), metres/25 in a byte
GP = 12.5
HW, HH = int((LON1-LON0)*GP)+1, int((LAT1-LAT0)*GP)+1
lons = LON0 + np.arange(HW)/GP; lats = LAT1 - np.arange(HH)/GP
LON, LAT = np.meshgrid(lons, lats)
E = sample_all(LON, LAT, dem_base, dem_det)
E = gaussian_filter(np.clip(E, 0, 6375), 0.6)
hb = np.clip(E/25, 0, 255).astype(np.uint8)
open(f"{OUT}/height.b64", "w").write(base64.b64encode(hb.tobytes()).decode())
json.dump({"bounds": [LON0, LON1, LAT0, LAT1], "grid": [HW, HH], "gp": GP, "hscale": 25, "chunks": chunks}, open(f"{OUT}/dims.json", "w"))
print("height grid", (HW, HH), "total tex KB", sum(c["bytes"] for c in chunks)//1024)
