import json, math
LON0, LON1, LAT0, LAT1 = -28.0, 56.0, -40.5, 40.5
def inb(p, pad=0.0): return LON0-pad < p[0] < LON1+pad and LAT0-pad < p[1] < LAT1+pad
def simplify(pts, tol):
    # Douglas-Peucker
    if len(pts) < 3: return pts
    def rdp(a, b):
        (x1,y1),(x2,y2) = pts[a], pts[b]; dx,dy = x2-x1, y2-y1; L = math.hypot(dx,dy)
        idx, dmax = -1, 0
        for i in range(a+1, b):
            x0,y0 = pts[i]; d = (abs(dy*x0 - dx*y0 + x2*y1 - y2*x1)/L) if L > 1e-7 else math.hypot(x0-x1, y0-y1)
            if d > dmax: idx, dmax = i, d
        if dmax > tol: return rdp(a, idx)[:-1] + rdp(idx, b)
        return [pts[a], pts[b]]
    return rdp(0, len(pts)-1)
def lines_from(geom):
    t = geom["type"]; c = geom["coordinates"]
    if t == "LineString": return [c]
    if t == "MultiLineString": return c
    if t == "Polygon": return c
    if t == "MultiPolygon": return [r for p in c for r in p]
    return []
def pack(lines, tol, pad=0.0):
    out = []
    for ln in lines:
        seg = []
        for p in ln:
            if inb(p, pad): seg.append((p[0], p[1]))
            else:
                if len(seg) > 1: out.append(seg)
                seg = []
        if len(seg) > 1: out.append(seg)
    res = []
    for s in out:
        s = simplify(s, tol)
        if len(s) > 1: res.append([round(v, 3) for xy in s for v in xy])
    return res

rv = json.load(open("ne/ne_10m_rivers_lake_centerlines.geojson"))["features"]
rivers = pack([l for f in rv if f["geometry"] and (f["properties"].get("scalerank") or 9) <= 7 for l in lines_from(f["geometry"])], 0.02)
ad = json.load(open("ne/ne_10m_admin_0_countries.geojson"))["features"]
borders, countries = [], {}
want = {"SLE":"Sierra Leone","LBR":"Liberia","GIN":"Guinea","COD":"DR Congo","UGA":"Uganda","KEN":"Kenya"}
for f in ad:
    if f["properties"].get("CONTINENT") not in ("Africa",): continue
    ls = lines_from(f["geometry"]); borders += ls
    a3 = f["properties"].get("ADM0_A3")
    if a3 in want: countries[want[a3]] = pack(ls, 0.01, 0.5)
borders = pack(borders, 0.02)
drc = countries["DR Congo"]
prov = {}
keepmap = {"COD": ["Ituri","North Kivu","Kasai","Upper Uele","Tshopo","Lower Uele","South Kivu","Sud-Ubangi"], "KEN": ["Nairobi"], "UGA": ["Central Region"]}
for iso, keep in keepmap.items():
    g = json.load(open(f"ne/gb_{iso}.geojson"))["features"]
    for f in g:
        n = f["properties"]["shapeName"]
        if n not in keep: continue
        prov[f"{iso}:{n}"] = pack(lines_from(f["geometry"]), 0.01, 0.5)
out = {"rivers": rivers, "borders": borders, "drc": drc, "prov": prov, "countries": countries}
s = json.dumps(out, separators=(",", ":"))
open("tex3/vectors.json", "w").write(s)
print("rivers", len(rivers), "borders", len(borders), "countries", list(countries), "prov", list(prov), "KB", len(s)//1024)
