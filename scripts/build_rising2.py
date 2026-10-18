import json, base64, math
# reuse the story data (spikes, timeline, camera, phases) from the first builder
src = open("/home/claude/build_rising.py").read().split("data_json =")[0]
src = src.replace('_dims = json.load(open(f"{TEX}/dims.json"))', '_dims = json.load(open("/home/claude/tex2/dims.json"))')
ns = {}; exec(src, ns)
DATA = ns["DATA"]; END = ns["END"]
T2 = "/home/claude/tex2"
dims = json.load(open(f"{T2}/dims.json"))
vec = json.load(open(f"{T2}/vectors.json"))

# Kasai 2025: correct final WHO total was already applied in the first builder (64 / 45)
# camera: open wide on West Africa; pull back for Bulape so the whole DRC is in view
cam = DATA["cam"]
for k in cam:
    if abs(k[0]-22.6) < 0.01: k[1:] = [23.0, -3.2, 27.0, 62, 0]
    if abs(k[0]-24.8) < 0.01: k[1:] = [22.3, -4.2, 14.0, 60, -2]
cam.sort(key=lambda k: k[0])

hand = {"2014–2016": "the largest Ebola outbreak ever recorded",
        "2018–2020": "the second largest, until 2026",
        "2021–2022": "Sudan virus, no licensed vaccine",
        "2025": "a separate spillover, declared over in December"}
loc = {"2014–2016": (["Guinea", "Liberia", "Sierra Leone"], "Guinea, Liberia & Sierra Leone", [-10.8, 8.0]),
       "2018–2020": (["Democratic Republic of the Congo"], "North Kivu & Ituri, far eastern DRC", [29.4, 0.6]),
       "2021–2022": (["Uganda"], "Mubende, central Uganda", [31.4, 0.56]),
       "2025": (["Democratic Republic of the Congo"], "Kasaï Province, south-central DRC", [21.8, -4.6]),
       "2026": (["Democratic Republic of the Congo", "Uganda"], "Ituri & North Kivu, eastern DRC", [30.25, 1.56])}
for ph in DATA["phases"]:
    ph["hand"] = hand.get(ph["date"], "")
    ph["loc"], ph["locNote"], ph["dot"] = loc[ph["date"]]

def hav(a, b):
    R = 6371; p1, p2 = math.radians(a[1]), math.radians(b[1]); dl = math.radians(b[0]-a[0])
    return 2*R*math.asin(math.sqrt(math.sin((p2-p1)/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2))
km = hav((30.25, 1.56), (36.82, -1.29))
DATA["kenyaNote"] = f"Bunia to Nairobi, about {int(round(km, -2)):,} km"

# province highlights per stretch of the story (keys are "ISO:name")
DATA["provFocus"] = [
  {"t0": 11.2, "t1": 16.4, "keys": ["COD:North Kivu", "COD:Ituri"]},
  {"t0": 17.0, "t1": 21.0, "keys": ["UGA:Central Region"]},
  {"t0": 21.4, "t1": 25.2, "keys": ["COD:Kasai"]},
  {"t0": 26.5, "t1": END+2, "keys": ["COD:Ituri", "COD:North Kivu"]},
  {"t0": 44.0, "t1": END+2, "keys": ["KEN:Nairobi"]},
]
labels = {"COD:North Kivu": "North Kivu", "COD:Ituri": "Ituri", "UGA:Central Region": "Central Region", "COD:Kasai": "Kasaï"}
offset = {"COD:Ituri": (0.9, 0.5), "COD:North Kivu": (-0.9, -0.6), "COD:Kasai": (0.0, 0.9), "UGA:Central Region": (0.3, -0.6), "KEN:Nairobi": (0.0, 0.45)}
pl = []
for k, name in labels.items():
    pts = [(l[i], l[i+1]) for l in vec["prov"][k] for i in range(0, len(l), 2)]
    lon = sum(p[0] for p in pts)/len(pts) + offset[k][0]; lat = sum(p[1] for p in pts)/len(pts) + offset[k][1]
    pl.append({"key": k, "name": name, "lon": round(lon, 2), "lat": round(lat, 2)})
DATA["provLabels"] = pl
DATA["vec"] = vec
DATA["bounds"], DATA["grid"], DATA["gp"], DATA["hscale"] = dims["bounds"], dims["grid"], dims["gp"], dims["hscale"]
DATA["chunks"] = [{"b": c["b"], "f": c["f"]} for c in dims["chunks"]]
DATA.pop("borders", None)
# country labels in Fira Sans; keep the list, drop Sierra Leone (spike names it)
# Kenya's note on the Nairobi callout
for s in DATA["spikes"]:
    if s["id"] == "nbo": s["note"] = "first case Oct. 6"
    if s["id"] == "kas": s["note"] = "south-central DRC"
    if s["id"] == "mub": s["note"] = "Sudan virus"
    if s["id"] == "ituri": s["note"] = "the epicentre"; s["side"] = "right"

# locator: Africa outline from the 110m file, simplified rings
afr = json.load(open("/tmp/claude-0/-home-claude/682b7276-4f53-5c14-ac7d-b6310ac269f9/scratchpad/africa.geo.json"))
cs = []
for f in afr["features"]:
    g = f["geometry"]; polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    rings = [[round(v, 1) for p in poly[0][::2] for v in p] for poly in polys if len(poly[0]) > 4]
    cs.append({"name": f["properties"]["name"], "rings": rings})
DATA["loc"] = {"bounds": [-19, 53, -36, 38], "countries": cs}

texmap = {c["f"]: "data:image/jpeg;base64," + base64.b64encode(open(f"{T2}/{c['f']}", "rb").read()).decode() for c in dims["chunks"]}
html = open("/home/claude/rising2_template.html").read()
html = html.replace("__DATA__", json.dumps(DATA, ensure_ascii=False, separators=(",", ":")))
html = html.replace("__TEXMAP__", json.dumps(texmap, separators=(",", ":")))
html = html.replace("__HEIGHT__", open(f"{T2}/height.b64").read())
open("/home/claude/ebola-rising.html", "w").write(html)
print("ebola-rising.html", len(html)//1024, "KB;", DATA["kenyaNote"])
