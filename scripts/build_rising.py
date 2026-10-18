import json, base64

TEX = "/home/claude/tex"
terrain_b64 = base64.b64encode(open(f"{TEX}/terrain.jpg","rb").read()).decode()
height_b64 = open(f"{TEX}/height.b64").read()
africa = json.load(open("/tmp/claude-0/-home-claude/682b7276-4f53-5c14-ac7d-b6310ac269f9/scratchpad/africa.geo.json"))

_dims = json.load(open(f"{TEX}/dims.json"))
LON0, LON1, LAT0, LAT1 = _dims["bounds"]
HW, HH = _dims["grid"]

# ---- borders: keep segments inside the map window, compact as flat arrays ----
def inside(p):
    return LON0+0.2 < p[0] < LON1-0.2 and LAT0+0.2 < p[1] < LAT1-0.2
lines = []
for f in africa["features"]:
    g = f["geometry"]
    polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    for poly in polys:
        for ring in poly:
            seg = []
            for p in ring:
                if inside(p):
                    seg.extend([round(p[0],2), round(p[1],2)])
                else:
                    if len(seg) >= 4: lines.append(seg)
                    seg = []
            if len(seg) >= 4: lines.append(seg)

# ---- story timeline (seconds) ----
END = 53.0
T26_0, T26_1, DAYS = 26.0, 46.0, 154.0
def T_of_day(d): return T26_0 + d/DAYS*(T26_1-T26_0)

def lerp_keys(keys, x):
    if x <= keys[0][0]: return keys[0][1]
    for (x0,y0),(x1,y1) in zip(keys, keys[1:]):
        if x <= x1: return y0 + (y1-y0)*(x-x0)/(x1-x0)
    return keys[-1][1]

# DRC confirmed cases, day 0 = 15 May 2026 (WHO DON / WHO AFRO / ECDC milestones)
drc_cases = [[0,0],[1,8],[14,225],[18,344],[23,550],[39,1138],[47,1460],[77,3532],[89,4665],[136,8067],[144,8728],[149,9066],[152,9277],[154,9277]]
drc_deaths = [[47,452],[77,1556],[89,2184],[136,3901],[144,4205],[149,4381],[152,4478],[154,4478]]
ituri_share = [[0,1.0],[89,0.853],[152,0.7337],[154,0.7337]]
final = {"nkivu":1991,"haut":398,"tshopo":64,"basuele":13,"sudkivu":3,"sudubangi":2}
rem_total = sum(final.values())

def prov_series(pid):
    keys = []
    for d in list(range(0,153,2)) + [152,154]:
        nat = lerp_keys(drc_cases, d); sh = lerp_keys(ituri_share, d)
        if pid == "ituri": v = nat*sh
        else: v = nat*(1-sh)*final[pid]/rem_total
        keys.append([round(T_of_day(d),3), round(v,1)])
    # exact final provincial values (ECDC, data to 14 Oct)
    exact = {"ituri":6806, **final}[pid]
    keys[-2][1] = exact; keys[-1][1] = exact
    keys.sort(key=lambda k:k[0])
    return keys

def hist(t0, t1, n, op_at):
    return {"keys":[[t0,0],[t1,n]], "ease":True, "op":[[op_at,1],[op_at+1.2,0.28]]}

spikes = [
 # 2014-16 West Africa (WHO final totals by country)
 dict(id="sle", name="Sierra Leone", lon=-11.8, lat=8.5, side="left",  deaths=3956, **hist(2.4,7.5,14124,9.0)),
 dict(id="lbr", name="Liberia",      lon=-9.4,  lat=6.5, side="right", deaths=4810, **hist(1.8,7.5,10678,9.0)),
 dict(id="gin", name="Guéckédou, Guinea", lon=-10.1, lat=8.6, side="left", deaths=2544, **hist(1.0,7.5,3814,9.0)),
 dict(id="nga", name="Lagos, Nigeria", lon=3.39, lat=6.52, side="right", deaths=8, **hist(3.6,4.4,20,9.0)),
 dict(id="mli", name="Mali", lon=-8.0, lat=12.6, side="right", deaths=6, **hist(4.6,5.2,8,9.0)),
 # 2018-20 eastern DRC
 dict(id="beni", name="Beni, North Kivu", lon=29.47, lat=0.49, side="right", deaths=2287, **hist(11.5,14.8,3470,15.5)),
 # 2021 Guinea, 2022 Uganda
 dict(id="nze", name="Nzérékoré, Guinea", lon=-8.82, lat=7.75, side="right", deaths=12, **hist(17.0,18.5,16,20.5)),
 dict(id="mub", name="Mubende, Uganda", lon=31.39, lat=0.56, side="right", deaths=77, **hist(17.0,19.8,164,20.5)),
 # 2025 Kasai
 dict(id="kas", name="Bulape, Kasaï", lon=21.8, lat=-4.6, side="right", deaths=45, **hist(21.6,23.6,64,24.5)),
]
prov = [
 ("ituri","Bunia, Ituri",30.25,1.56,"left"),
 ("nkivu","Butembo, North Kivu",29.28,0.13,"left"),
 ("haut","Isiro, Haut-Uélé",27.62,2.77,"right"),
 ("tshopo","Kisangani, Tshopo",25.19,0.52,"left"),
 ("basuele","Buta, Bas-Uélé",24.73,2.80,"left"),
 ("sudkivu","Bukavu, South Kivu",28.86,-2.51,"left"),
 ("sudubangi","Gemena, Sud-Ubangi",19.77,3.25,"left"),
]
for pid,name,lon,lat,side in prov:
    spikes.append(dict(id=pid, name=name, lon=lon, lat=lat, side=side, keys=prov_series(pid), ease=False, op=[[0,1]]))
spikes.append(dict(id="kla", name="Kampala, Uganda", lon=32.58, lat=0.31, side="right",
                   keys=[[T_of_day(0),0],[T_of_day(1),2],[T_of_day(48),20]], ease=False, op=[[0,1]]))
spikes.append(dict(id="nbo", name="Nairobi, Kenya", lon=36.82, lat=-1.29, side="right", note="first case Oct. 6",
                   keys=[[T_of_day(143.2),0],[T_of_day(144),1],[T_of_day(149.5),1],[T_of_day(150),2],[T_of_day(153.6),2],[T_of_day(154),3]], ease=False, op=[[0,1]]))

# which callouts show in which stretch of the story
callouts = [
 {"t0":1.2,"t1":10.2,"ids":["sle","lbr","gin"]},
 {"t0":11.6,"t1":16.4,"ids":["beni"]},
 {"t0":17.2,"t1":21.0,"ids":["mub"]},
 {"t0":21.8,"t1":25.0,"ids":["kas"]},
 {"t0":26.2,"t1":42.5,"ids":["ituri","nkivu","kla"]},
 {"t0":42.5,"t1":END+1,"ids":["ituri","kla","nbo"]},
]
# camera keyframes: [T, lon, lat, dist, pitch, yaw]
cam = [
 [0.0, -13.6, 8.2, 20.0, 66, 0],
 [8.6, -13.4, 8.3, 25.0, 70, 3],
 [11.6, 29.4, 0.6, 10.0, 50, 0],
 [15.6, 29.5, 0.6, 9.0, 52, -3],
 [17.6, 30.6, 0.5, 6.2, 50, 0],
 [20.8, 30.7, 0.5, 5.8, 52, 3],
 [22.6, 22.2, -4.0, 6.5, 50, 0],
 [24.8, 22.3, -4.0, 6.2, 52, -2],
 [27.6, 29.6, 0.6, 15.5, 56, 0],
 [40.5, 29.9, 0.6, 16.5, 58, 4],
 [45.2, 32.8, 0.2, 21.0, 56, 0],
 [END, 32.2, 0.4, 22.5, 60, -7],
]
phases = [
 {"t0":0,"t1":10.2,"date":"2014–2016","place":"West Africa · Guinea, Liberia & Sierra Leone","ids":["sle","lbr","gin"],"note":"Zaire ebolavirus · the largest Ebola outbreak ever recorded"},
 {"t0":10.2,"t1":16.6,"date":"2018–2020","place":"Eastern DRC · North Kivu & Ituri","ids":["beni"],"note":"Zaire ebolavirus · until 2026, the second largest on record"},
 {"t0":16.6,"t1":21.2,"date":"2021–2022","place":"Mubende, Uganda","ids":["mub"],"note":"Sudan virus · plus a 16-case flare-up in Guinea in 2021"},
 {"t0":21.2,"t1":25.4,"date":"2025","place":"Kasaï, DRC","ids":["kas"],"note":"Zaire ebolavirus · a separate spillover, declared over in December"},
 {"t0":25.4,"t1":END+1,"date":"2026","place":"DRC · Uganda · Kenya","ids":[],"note":"Bundibugyo virus"},
]

DATA = dict(
  bounds=[LON0,LON1,LAT0,LAT1], grid=[HW,HH], end=END, t26=[T26_0,T26_1,DAYS],
  spikes=spikes, callouts=callouts, cam=cam, phases=phases,
  drcCases=drc_cases, drcDeaths=drc_deaths,
  uga=[[0,0],[1,2],[48,20]], ugaDeaths=[[0,0],[20,2]],
  ken=[[143.2,0],[144,1],[149.5,1],[150,2],[153.6,2],[154,3]], kenDeaths=[[143.2,0],[144,1]],
  chapters=[["2014",0.4],["2018",10.6],["2022",16.8],["2025",21.4],["2026",26.0],["Kenya",43.5]],
  labels=[
   ["DEMOCRATIC|REPUBLIC|OF CONGO",24.6,-0.8,30],["UGANDA",32.6,1.9,30],["RWANDA",29.9,-1.95,11],["BURUNDI",29.9,-3.5,11],
   ["KENYA",37.9,0.6,30],["TANZANIA",34.6,-6.3,30],["SOUTH SUDAN",30.4,7.4,30],["CENTRAL|AFRICAN REP.",20.4,6.6,30],
   ["GUINEA",-11.0,10.9,30],["LIBERIA",-9.0,5.6,30],["CÔTE D’IVOIRE",-5.5,7.6,30],
   ["NIGERIA",8.0,9.5,30],["ETHIOPIA",39.4,8.4,30],["CONGO",15.2,-0.9,30],["GABON",11.6,-0.8,30],["CAMEROON",12.6,5.6,30],["ANGOLA",17.0,-11.4,30],
  ],
  borders=lines,
)
data_json = json.dumps(DATA, ensure_ascii=False, separators=(",",":"))

HTML = open("/home/claude/rising_template.html").read()
HTML = HTML.replace("__DATA__", data_json).replace("__TERRAIN__", terrain_b64).replace("__HEIGHT__", height_b64)
open("/home/claude/ebola-rising.html","w").write(HTML)
print("ebola-rising.html", len(HTML), "bytes; borders", len(lines), "; spikes", len(spikes))
