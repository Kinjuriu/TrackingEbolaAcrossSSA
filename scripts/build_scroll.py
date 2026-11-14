import json, base64, math, os
# Run from anywhere: python3 scripts/build_scroll.py  (writes docs/index.html and docs/tex/*.webp)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def P(*a): return os.path.join(ROOT, *a)
TER, CON = P("data", "terrain"), P("data", "continent")
dims = json.load(open(f"{TER}/dims.json")); cd = json.load(open(f"{CON}/cont_dims.json"))
vec = json.load(open(f"{TER}/vectors.json"))

def lerp_keys(keys, x):
    if x <= keys[0][0]: return keys[0][1]
    for (x0, y0), (x1, y1) in zip(keys, keys[1:]):
        if x <= x1: return y0 + (y1-y0)*(x-x0)/(x1-x0)
    return keys[-1][1]

# story position T for each 2026 outbreak day (day 0 = 15 May 2026)
dayMap = [[16.8, 0], [17.6, 14], [18.6, 39], [19.6, 77], [20.5, 89], [21.4, 136], [22.2, 152], [22.6, 154], [26.2, 154], [27.4, 181], [40, 181]]
def T_of_day(d): return lerp_keys([[b, a] for a, b in dayMap], d)

drc_cases = [[0,0],[1,8],[14,225],[18,344],[23,550],[39,1138],[47,1460],[77,3532],[89,4665],[141,8544],[144,8728],[149,9066],[151,9144],[152,9277],[156,9552],[158,9704],[164,10141],[166,10274],[169,10351],[173,10741],[181,11197]]
drc_deaths = [[47,452],[77,1556],[89,2184],[141,4114],[144,4205],[149,4381],[151,4410],[152,4478],[156,4602],[158,4687],[164,4928],[166,4992],[169,5026],[173,5230],[181,5471]]
ituri_share = [[0,1.0],[89,0.853],[152,0.7337]]
oct14 = {"ituri":6806,"nkivu":1991,"haut":398,"tshopo":64,"basuele":13,"sudkivu":3,"sudubangi":2,"nordubangi":0}
oct26 = {"ituri":7247,"nkivu":2345,"haut":442,"tshopo":86,"basuele":13,"sudkivu":3,"sudubangi":2,"nordubangi":3}
rem14 = sum(v for k, v in oct14.items() if k != "ituri")
def prov_keys(pid):
    # up to 14 Oct: national curve split by Ituri's share, ending exactly on the 14 Oct province figures
    ks = []
    for d in range(0, 153, 2):
        nat = lerp_keys(drc_cases, d); sh = lerp_keys(ituri_share, d)
        v = nat*sh if pid == "ituri" else nat*(1-sh)*oct14[pid]/rem14
        ks.append([round(T_of_day(d), 4), round(v, 1)])
    ks[-1][1] = oct14[pid]
    # 14 Oct to 26 Oct: straight line between the two ECDC province reports, then hold
    for d in (156, 160, 164):
        v = oct14[pid] + (oct26[pid]-oct14[pid])*(d-152)/(164-152)
        ks.append([round(T_of_day(d), 4), round(v, 1)])
    ks.append([round(T_of_day(166), 4), oct26[pid]])
    ks.sort(key=lambda k: k[0]); return ks

Z, SU, BU = "Zaire ebolavirus", "Sudan virus", "Bundibugyo virus"
def sp(id, label, lon, lat, keys, deaths, virus, ease=True, overT=None, overText="", kind="", side="right", dy=0):
    return dict(id=id, label=label, lon=lon, lat=lat, keys=keys, deaths=deaths, virus=virus, ease=ease, overT=overT, overText=overText, kind=kind, side=side, dy=dy)
spikes = [
  sp("sle","Sierra Leone",-11.8,8.5,[[1.0,0],[2.2,14124]],3956,Z,overT=5.2,overText="March 17, 2016",kind="national total",side="left",dy=30),
  sp("lbr","Liberia",-9.4,6.5,[[2.8,0],[3.9,10678]],4810,Z,overT=5.4,overText="June 9, 2016",kind="national total",dy=64),
  sp("gin","Guinea",-10.1,8.6,[[2.8,0],[3.9,3814]],2544,Z,overT=5.3,overText="June 1, 2016",kind="national total",dy=-46),
  sp("nga","Nigeria",3.39,6.52,[[3.0,0],[3.6,20]],8,Z,overT=5.3),
  sp("mli","Mali",-8.0,12.64,[[3.0,0],[3.6,8]],6,Z,overT=5.3),
  sp("beni","North Kivu & Ituri provinces, DR Congo",29.47,0.49,[[8.8,0],[10.0,3470]],2287,Z,overT=11.0,overText="June 25, 2020"),
  sp("mub","Mubende District, Central Region, Uganda",31.39,0.56,[[11.9,0],[12.6,164]],77,SU,overT=13.6,overText="Jan. 11, 2023",side="left"),
  sp("kla25","Kampala, Central Region, Uganda",32.58,0.31,[[12.6,0],[13.1,14]],4,SU,overT=13.8,overText="April 26, 2025",dy=40),
  sp("kas","Bulape, Kasäi Province, DR Congo".replace("ä","ä").replace("ä","aï")[:0] or "Bulape, Kasïi Province, DR Congo",21.8,-4.6,[[14.4,0],[15.0,64]],45,Z,overT=15.9,overText="Dec. 2025"),
]
spikes[-1]["label"] = "Bulape, Kasaï Province, DR Congo"
for pid, label, lon, lat, side, dy in [("ituri","Ituri Province, DR Congo",30.25,1.56,"right",0),("nkivu","North Kivu Province, DR Congo",29.28,0.13,"left",30),
        ("haut","Haut-Uélé Province, DR Congo",27.62,2.77,"left",-20),("tshopo","Tshopo Province, DR Congo",25.19,0.52,"left",0),
        ("basuele","Bas-Uélé Province, DR Congo",24.73,2.80,"left",0),("sudkivu","South Kivu Province, DR Congo",28.86,-2.51,"left",0),
        ("sudubangi","Sud-Ubangi Province, DR Congo",19.77,3.25,"left",0),("nordubangi","Nord-Ubangi Province, DR Congo",21.01,4.28,"left",0)]:
    d = {"ituri":3388,"nkivu":1314,"haut":192,"tshopo":27,"basuele":4,"sudkivu":1,"sudubangi":1,"nordubangi":1}[pid]
    spikes.append(sp(pid, label, lon, lat, prov_keys(pid), d, BU, ease=False, side=side, dy=dy))
spikes.append(sp("kla26","Uganda, Kampala and border districts",32.42,0.48,[[T_of_day(0),0],[T_of_day(1),2],[T_of_day(48),20]],2,BU,ease=False,overT=23.4,overText="Aug. 2026",dy=36))
spikes.append(sp("nbo","Nairobi County, Kenya",36.82,-1.29,[[25.6,0],[25.8,1],[26.0,2],[26.2,3],[26.8,3],[27.4,9]],2,BU,ease=False,dy=30))
spikes.append(sp("nga","Abuja, Nigeria (imported)",7.49,9.06,[[26.9,0],[27.3,1]],0,BU,ease=False,side="right",dy=-60))

END = 32.4
WA = ["Sierra Leone","Liberia","Guinea"]; DRC = "Democratic Republic of the Congo"
phases = [
  {"t0":0,"t1":7.2,"date":"2014 to 2016 · West Africa","ids":["sle","lbr","gin"],"loc":WA},
  {"t0":7.2,"t1":11.4,"date":"2018 to 2020 · DR Congo","ids":["beni"],"loc":[DRC]},
  {"t0":11.4,"t1":14.0,"date":"2022 and 2025 · Uganda","ids":["mub","kla25"],"loc":["Uganda"]},
  {"t0":14.0,"t1":16.4,"date":"2025 · DR Congo","ids":["kas"],"loc":[DRC]},
  {"t0":16.4,"t1":24.8,"kind":"2026","loc":[DRC,"Uganda"]},
  {"t0":24.8,"t1":28.2,"kind":"2026","loc":[DRC,"Uganda","Kenya","Nigeria"]},
  {"t0":28.2,"t1":END+5,"date":"2014 to 2026 · every outbreak on this map","ids":"all","loc":[]},
]
O = []
def ol(key, t0, t1, color="active"): O.append({"key":key,"t0":t0,"t1":t1,"color":color})
ol("C:Sierra Leone",1.0,5.6); ol("C:Liberia",2.8,5.6); ol("C:Guinea",2.8,5.6)
for c in WA: ol("C:"+c,5.3,7.4,"over")
ol("C:DR Congo",7.3,9.8); ol("COD:North Kivu",9.0,11.7,"prov"); ol("COD:Ituri",9.0,11.7,"prov")
ol("C:Uganda",11.4,14.1); ol("UGA:Central Region",12.0,14.1,"prov")
ol("C:DR Congo",14.0,15.0); ol("COD:Kasai",14.4,16.5,"prov")
ol("C:DR Congo",16.4,17.6); ol("COD:Ituri",17.0,28.4,"prov"); ol("COD:North Kivu",18.4,28.4,"prov")
for k in ["COD:Upper Uele","COD:Tshopo","COD:Lower Uele","COD:South Kivu","COD:Sud-Ubangi"]: ol(k,21.4,23.3,"prov")
ol("C:Uganda",23.2,24.9,"over")
ol("C:Kenya",24.8,28.6); ol("KEN:Nairobi",25.4,28.6,"prov")
for c in WA: ol("C:"+c,28.8,END+5,"over")
ol("C:Uganda",28.8,END+5,"over"); ol("C:DR Congo",28.8,END+5); ol("C:Kenya",28.8,END+5)

callouts = [
  {"t0":1.4,"t1":3.0,"ids":["sle"]},{"t0":3.0,"t1":7.4,"ids":["sle","lbr","gin"]},
  {"t0":9.0,"t1":11.7,"ids":["beni"]},{"t0":12.0,"t1":14.2,"ids":["mub","kla25"]},
  {"t0":14.6,"t1":16.4,"ids":["kas"]},{"t0":17.2,"t1":22.0,"ids":["ituri","nkivu","kla26"]},
  {"t0":22.0,"t1":23.4,"ids":["ituri","nkivu","haut"]},{"t0":23.4,"t1":25.0,"ids":["kla26","ituri"]},
  {"t0":25.0,"t1":28.2,"ids":["nbo","ituri"]},{"t0":29.2,"t1":END+5,"ids":["ituri","nbo","nga"]},
]
cam = [[0,-11.0,8.6,30,64,0],[2.0,-11.8,8.6,13,58,0],[4.0,-10.6,8.3,20,62,0],[6.0,-10.6,8.3,22,64,2],
       [8.0,23.5,-2.5,40,70,0],[10.0,29.3,0.7,11,56,0],[11.0,29.6,0.7,12,58,0],
       [12.5,31.8,0.9,13,56,0],[13.6,31.8,0.8,13,58,3],[14.4,23.5,-2.5,38,70,0],[15.0,22.3,-4.4,15,60,0],[16.0,22.4,-4.3,15,62,-2],
       [17.6,29.8,0.9,15,56,0],[20.5,29.4,1.0,18,58,2],[22.2,27.5,0.8,24,62,0],[24.0,30.8,0.6,18,58,0],
       [26.2,32.4,0.3,22,56,0],[27.6,32.6,0.0,22,58,-3],[29.6,13.5,1.0,98,80,0],[END,13.5,1.0,94,84,0]]
route = [["Buta",24.73,2.80,24.95],["Kisangani",25.19,0.52,25.1],["Beni",29.47,0.49,25.3],[None,29.72,0.03,None],
         ["Kampala",32.58,0.31,25.5],[None,32.46,0.05,None],["Nairobi",36.82,-1.29,25.75]]

# country labels: Natural Earth label points for every African country
ad = [{"properties": dict(p, CONTINENT="Africa")} for p in json.load(open(P("data", "africa_label_points.json")))]
story = {"Sierra Leone","Liberia","Guinea","DR Congo","Uganda","Kenya"}
rename = {"Dem. Rep. Congo":"DR Congo","Central African Rep.":"Central African Rep.","S. Sudan":"South Sudan","Eq. Guinea":"Eq. Guinea","W. Sahara":None}
cl = []
for f in ad:
    p = f["properties"]
    if p.get("CONTINENT") != "Africa": continue
    n = rename.get(p["NAME"], p["NAME"])
    if not n or p.get("LABEL_X") is None: continue
    big = n in story
    cl.append({"name": n, "lon": round(p["LABEL_X"], 2), "lat": round(p["LABEL_Y"], 2), "big": big, "from": 0, "to": END+5, "dmin": 0, "dmax": 400 if big else 70})

def centroid(k, dx=0, dy=0):
    pts = [(l[i], l[i+1]) for l in vec["prov"][k] for i in range(0, len(l), 2)]
    return round(sum(p[0] for p in pts)/len(pts)+dx, 2), round(sum(p[1] for p in pts)/len(pts)+dy, 2)
pl = []
for k, name, dx, dy in [("COD:Ituri","Ituri Province",0.9,0.6),("COD:North Kivu","North Kivu Province",-1.0,-0.7),("COD:Kasai","Kasaï Province",0,0.9),
                         ("UGA:Central Region","Central Region",0.2,-0.7),("KEN:Nairobi","Nairobi County",0,0.55),("COD:Upper Uele","Haut-Uélé",0,0.4)]:
    lon, lat = centroid(k, dx, dy); pl.append({"key": k, "name": name, "lon": lon, "lat": lat})

afr = json.load(open(P("data", "africa_locator.geo.json")))
locc = []
for f in afr["features"]:
    g = f["geometry"]; polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    locc.append({"name": f["properties"]["name"], "rings": [[round(v, 1) for p in poly[0][::2] for v in p] for poly in polys if len(poly[0]) > 4]})

# data files the page fetches next to the HTML: elevation as raw bytes, map lines as 16-bit integers
import struct
DATADIR = P("docs", "data"); os.makedirs(DATADIR, exist_ok=True)
open(os.path.join(DATADIR, "height_det.bin"), "wb").write(base64.b64decode(open(f"{TER}/height.b64").read()))
open(os.path.join(DATADIR, "height_cont.bin"), "wb").write(base64.b64decode(open(f"{CON}/cont_height.b64").read()))
VQ = 400  # coordinates stored as round(degrees * 400), about 280 m
vec_pts, vec_index = [], {}
def vec_lines(lines):
    lens = []
    for l in lines:
        vec_pts.extend(int(round(v*VQ)) for v in l); lens.append(len(l)//2)
    return lens
vec_index["rivers"] = vec_lines(vec["rivers"]); vec_index["borders"] = vec_lines(vec["borders"])
vec_index["countries"] = {k: vec_lines(v) for k, v in vec["countries"].items()}
vec_index["prov"] = {k: vec_lines(v) for k, v in vec["prov"].items()}
open(os.path.join(DATADIR, "vectors.bin"), "wb").write(struct.pack("<%dh" % len(vec_pts), *vec_pts))

# the story position at which each satellite tile is first seen close up, so the page can fetch tiles a chapter ahead
def cam_at(t):
    k = cam
    if t <= k[0][0]: return k[0]
    for a, b in zip(k, k[1:]):
        if t <= b[0]:
            u = (t-a[0])/(b[0]-a[0]); u = u*u*(3-2*u)
            return [t] + [a[j]+(b[j]-a[j])*u for j in (1, 2)] + [math.exp(math.log(a[3])+(math.log(b[3])-math.log(a[3]))*u)]
    return k[-1]
def chunk_need(b):
    t = 0.0
    while t < 28.2:  # after this the camera pulls back to the whole continent and the tiles fade out
        _, lon, lat, d = cam_at(t)[:4]
        if d <= 26:  # further out, Blue Marble underneath (about 36 pixels per degree) is sharp enough
            hw, hh = d*0.6 + 1, d*0.45 + 1
            if b[0] < lon+hw and b[1] > lon-hw and b[2] < lat+hh and b[3] > lat-hh: return round(t, 2)
        t += 0.1
    return None

DATA = dict(
  det=dict(bounds=dims["bounds"], grid=dims["grid"], gp=dims["gp"], hscale=dims["hscale"]),
  cont=dict(bounds=cd["bounds"], grid=cd["grid"], gp=cd["gp"], hscale=cd["hscale"]),
  chunks=sorted([{"b": c["b"], "f": c["f"], "need": chunk_need(c["b"])} for c in dims["chunks"]], key=lambda c: 99 if c["need"] is None else c["need"]),
  vecIndex=vec_index, vecQ=VQ, spikes=spikes, phases=phases, outlines=O, callouts=callouts, cam=cam,
  route=route, routeT=[24.8, 25.8, 28.2], countryLabels=cl, provLabels=pl, loc={"bounds": [-19, 53, -36, 38], "countries": locc},
  dayMap=dayMap, kenDeaths=[[25.6,0],[25.8,1],[27.0,1],[27.4,2]], drcCases=drc_cases, drcDeaths=drc_deaths, uga=[[0,0],[1,2],[48,20]], ugaDeaths=[[0,0],[20,2]],
  march=[["Gu\u00e9ck\u00e9dou",-10.1,8.6,"2014",1],["Beni",29.47,0.49,"2018"],["Mubende",31.39,0.56,"2022"],["Bulape",21.8,-4.6,"2025",1],["Bunia",30.25,1.56,"2026"],["Nairobi",36.82,-1.29,"2026"]],
  marchT=[29.2, 30.9],
  pull=[28.2, 29.6], night=[31.0, 32.2], pullScale=3.2, end=END,
  credit="Imagery: Sentinel-2 cloudless 2024 by EOX, contains modified Copernicus Sentinel data · NASA Blue Marble and Black Marble via GIBS · Elevation: AWS Terrain Tiles · Boundaries: Natural Earth, geoBoundaries",
)

def tags(*v): return "".join(f'<span class="tag {c}">{t}</span>' for c, t in v)
TZ, TS, TB = ("z", "Zaire ebolavirus"), ("s", "Sudan virus"), ("b", "Bundibugyo virus")
ARROW = '<svg width="14" height="22" viewBox="0 0 14 22" aria-hidden="true"><path d="M7 1v19M1.5 14.5 7 20l5.5-5.5" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>'
steps = [
 (0, "hero", "", "<h1>Ebola in Africa: 2014 to 2026</h1>",
  "<p>This data tracks Ebola outbreaks across the African continent over a 12-year period, from the West African epidemic, which began in Guinea, to the cases in Nairobi in 2026; the disease itself was first recorded in 1976. The map visualizes outbreaks place by place. Active outbreaks are marked by rising spikes that correspond to confirmed cases of the Zaire, Sudan, and Bundibugyo viruses. Spikes turn grey when an outbreak is officially declared over.</p><p>" + tags(TZ, TS, TB) + '</p><div class="scrollcue">Scroll to begin' + ARROW + '</div>'),
 (2, "", "2014", "<h2>West Africa Epidemic</h2>",
  "<p>The largest Ebola epidemic on record reached Sierra Leone in 2014. Driven by the Zaire ebolavirus, the country recorded <b>14,124 cases</b> and <b>3,956 deaths</b>. This was the highest number of cases of any single country in the epidemic, although Liberia recorded more deaths.</p><p>" + tags(TZ) + "</p>"),
 (4, "", "2014 to 2016", "<h2>The Regional Toll</h2>",
  "<p>The epidemic originated near Guéckédou, Guinea, and rapidly escalated into a national crisis across three neighboring countries. The data visualizes the national totals rather than provincial numbers. Guinea reported <b>3,814 cases</b> and Liberia reported <b>10,678 cases</b>. Combined with Sierra Leone, the regional outbreak resulted in a total of <b>28,616 cases</b> and <b>11,310 deaths</b>.</p>"),
 (6, "", "2016", "<h2>Outbreaks Contained</h2>",
  "<p>The World Health Organization declared the final flare-up over in Sierra Leone on <b>March 17, 2016</b>. Guinea followed on <b>June 1</b>, and Liberia on <b>June 9</b>, at which point the map spikes turn grey.</p><p>Health officials declare an outbreak over only after 42 consecutive days pass with no new cases. However, the virus is never fully eradicated because it remains endemic in animal populations.</p>"),
 (8, "", "2018 · Democratic Republic of the Congo", "<h2>Resurgence in the East</h2>",
  "<p>In August 2018, after two smaller outbreaks elsewhere in the country in 2017 and May 2018, a new outbreak of the Zaire ebolavirus was declared in the far eastern region of the Democratic Republic of the Congo, a vast nation divided into 26 provinces.</p>"),
 (10, "", "2018 to 2020", "<h2>DR Congo Conflict Zone</h2>",
  "<p>The Zaire ebolavirus spread across North Kivu, Ituri, and South Kivu provinces. Operating within an active conflict zone, health workers recorded <b>3,470 cases</b> and <b>2,287 deaths</b>. The outbreak was officially declared over on <b>June 25, 2020</b>.</p><p>" + tags(TZ) + "</p>"),
 (12.5, "", "2022 and 2025", "<h2>Uganda Outbreaks</h2>",
  "<p>Uganda faced outbreaks of the Sudan virus, a separate species of Ebola virus for which there is currently no licensed vaccine. In 2022, the virus caused <b>164 cases</b> and 55 confirmed deaths in the Mubende District, with the outbreak declared over on January 11, 2023. A subsequent outbreak in Kampala caused <b>14 cases</b> and 4 deaths in 2025 and was declared over on April 26, 2025.</p><p>" + tags(TS) + "</p>"),
 (15, "", "2025", "<h2>South-Central DR Congo</h2>",
  "<p>A separate spillover event of the Zaire ebolavirus occurred in the Kasaï Province, distant from the eastern outbreaks. Centered around Bulape, this outbreak resulted in <b>64 cases</b> and <b>45 deaths</b> before being declared over on December 1, 2025.</p><p>" + tags(TZ) + "</p>"),
 (17.6, "", "May 2026", "<h2>Bundibugyo Virus in DR Congo</h2>",
  "<p>On May 15, 2026, health officials in DR Congo confirmed an outbreak of the <b>Bundibugyo virus</b> in Ituri Province. Epidemiological data suggests the virus had been circulating undetected for several weeks. There is currently no approved vaccine for the Bundibugyo virus.</p><p>" + tags(TB) + "</p>"),
 (20.5, "", "August 2026", "<h2>Rapid Escalation</h2>",
  "<p>By August 12, the Bundibugyo outbreak reached <b>4,665 confirmed cases</b>, with 85 percent concentrated in Ituri. In approximately eleven weeks, the case count surpassed the total number of infections from the entire 2018 to 2020 epidemic, making it the second-largest Ebola outbreak on record.</p>"),
 (22.2, "", "October 2026", "<h2>Expansion Across Seven Provinces</h2>",
  "<p>By October 14, the DR Congo outbreak expanded to seven provinces, totaling <b>9,277 cases</b>. The distribution included 6,806 cases in Ituri, 1,991 in North Kivu, 398 in Haut-Uélé, 64 in Tshopo, 13 in Bas-Uélé, three in South Kivu, and two in Sud-Ubangi.</p><p>The fatality rate remained at nearly 50 percent of all confirmed cases.</p>"),
 (24, "", "2026", "<h2>Uganda Containment</h2>",
  "<p>Uganda recorded <b>20 confirmed cases</b> of the Bundibugyo virus linked to the outbreak in neighboring DR Congo. Health authorities contained the spread and officially declared the Ugandan outbreak over in August 2026.</p><p>" + tags(TB) + "</p>"),
 (26.2, "", "October 2026", "<h2>Nairobi, Kenya</h2>",
  "<p>On October 3, a Kenyan national flew from Entebbe, Uganda, to Nairobi. The patient&rsquo;s travel history included transit from Buta in Bas-Uélé through Kisangani and Beni in DR Congo, before crossing the Ugandan border at Mpondwe. The patient died on October 5.</p><p>By October 16, Kenyan health officials confirmed <b>three cases</b> of the Bundibugyo virus, all directly linked to this initial patient.</p><p>" + tags(TB) + "</p>"),
 (27.4, "", "October to November 2026", "<h2>Kenya&rsquo;s Cluster Grows, and Nigeria Reports a Case</h2>",
  "<p>Kenya&rsquo;s count rose to <b>nine confirmed cases</b>, all in one cluster linked to the first patient, including three health workers who treated him. On October 23, the Ministry of Health reported a <b>second death</b>, a 65-year-old woman who was a close relative of the first patient. WHO&rsquo;s report of the same day lists the same nine cases.</p>"
  "<p>On October 20, Nigeria confirmed an imported case in Abuja, a woman who had travelled from Uganda; she was later evacuated to Switzerland for care.</p>"
  "<p>In DR Congo, the outbreak passed <b>10,000 confirmed cases</b> in October, across eight provinces after Nord-Ubangi recorded its first cases. By November 12, ECDC counted <b>11,197 cases</b> and <b>5,471 deaths</b>. Kenya reported its last case on October 20, and seven of its nine patients have recovered.</p><p>" + tags(TB) + "</p>"),
 (29.6, "", "2014 to 2026", "<h2>Continental Overview</h2>",
  "<p>Viewing the continent as a whole shows a clear eastward progression of active outbreaks. While the West African and Ugandan epidemics are resolved, the eastern DR Congo outbreak remains active, with a direct transmission link to Nairobi.</p><p>A dotted line connects each outbreak geographically in chronological order, from Guéckédou in 2014 to Nairobi in 2026. Most map points represent separate zoonotic transmission events from animals to humans; however, the 2026 path to Nairobi represents a single, continuous chain of human infection.</p><p>At this map scale, spike heights are calculated using the square root of total cases.</p>"),
 (END, "", "Africa at night", "<h2>Infrastructure and Transmission</h2>",
  "<p>NASA&rsquo;s Black Marble satellite imagery illuminates Africa&rsquo;s active urban centers and transportation networks at night. These connected transit routes facilitated the movement of the virus from eastern DR Congo to Nairobi.</p><p>Behind the data, every spike on the map represents an impacted community.</p>"),
]
# virus micrographs floated in each chapter card (files in media/virus/, credit NIAID)
import os
VIMG = {}
for key in ("zaire", "sudan", "bundibugyo"):
    f = P("media", "virus", f"{key}.jpg")
    if os.path.exists(f):
        from PIL import Image as _Iv
        os.makedirs(P("docs", "img"), exist_ok=True)
        _Iv.open(f).convert("RGB").resize((208, 208)).save(P("docs", "img", "virus-" + key + ".webp"), "WEBP", quality=82, method=6)
        VIMG[key] = "img/virus-" + key + ".webp"
VNAME = {"zaire": "Zaire ebolavirus", "sudan": "Sudan virus", "bundibugyo": "Bundibugyo virus"}
VCRED = {"zaire": ("NIAID via Wikimedia Commons", "https://commons.wikimedia.org/wiki/File:Ebola_Virus_-_Electron_Micrograph.tiff"),
         "sudan": ("NIAID on Unsplash", "https://unsplash.com/photos/mR-2J-e7Z5I"),
         "bundibugyo": ("NIAID on Unsplash", "https://unsplash.com/photos/e-h_wfP0OLk")}
def virus_of(t):
    if t <= 0 or t >= 29: return None
    if 12 <= t < 14: return "sudan"
    if t >= 16.4: return "bundibugyo"
    return "zaire"
def fig(t):
    v = virus_of(t)
    if not v or v not in VIMG: return ""
    return f'<figure class="vimg"><img class="vball" src="{VIMG[v]}" width="104" height="104" loading="lazy" alt="Coloured electron micrograph of Ebola virus particles"><figcaption>{VNAME[v]}<a href="{VCRED[v][1]}" target="_blank" rel="noopener">Image: {VCRED[v][0]}</a></figcaption></figure>'
steps = [(t, cls, k, h, fig(t) + body) for t, cls, k, h, body in steps]
def _step(t, cls, k, h, body):
    c = (" " + cls) if cls else ""
    kk = '<p class="k">' + k + '</p>' if k else ""
    return '    <section class="step' + c + '" data-t="' + str(t) + '"><div class="card' + c + '">' + kk + h + body + '</div></section>'
step_html = "\n".join(_step(*s_) for s_ in steps)
src = [
 ('https://www.ecdc.europa.eu/en/ebola-outbreak-democratic-republic-congo-and-uganda', 'ECDC', 'DRC cases and deaths by province to 26 Oct 2026; national totals to 31 Oct from the DRC Ministry of Health via Reuters'),
 ('https://www.who.int/emergencies/disease-outbreak-news/item/2026-DON615', 'WHO Disease Outbreak News', 'and WHO Africa weekly situation reports 21 and 22: 2026 milestones'),
 ('https://www.aljazeera.com/news/2026/10/16/kenya-reports-third-bundibugyo-strain-ebola-case', 'Al Jazeera', 'and the WHO Kenya week 41 report: Kenya cases and the travel route'),
 ('https://www.the-star.co.ke/news/2026-10-20-kenya-confirms-ninth-ebola-case', 'Kenya Ministry of Health', 'statements of 20 and 23 Oct 2026 via The Star and Capital FM: nine cases, two deaths'),
 ('https://www.who.int/emergencies/disease-outbreak-news/item/2026-DON622', 'WHO Disease Outbreak News 622', ': DR Congo, Kenya and Nigeria, 23 Oct 2026'),
 ('https://www.cdc.gov/ebola/situation-summary/index.html', 'US CDC situation summary', ': country totals to 28 Oct 2026'),
 ('https://www.afro.who.int/countries/kenya/news/who-supports-kenyas-ebola-response-third-case-found-early-quarantine', 'WHO Africa', ': Kenya&rsquo;s third case, 16 Oct 2026'),
 ('https://www.cdc.gov/ebola/outbreaks', 'US CDC outbreak history', ': outbreaks 2014 to 2025'),
 ('https://www.who.int/en/news-room/detail/17-03-2016-who-statement-on-end-of-ebola-flare-up-in-sierra-leone', 'WHO', 'statements on the end of transmission in Sierra Leone, Guinea and Liberia, 2016'),
 ('https://reliefweb.int/report/uganda/disease-outbreak-news-sudan-virus-disease-uganda-26-april-2025', 'WHO via ReliefWeb', ': Uganda 2025 declared over; ECDC for Uganda 2022'),
 ('https://allafrica.com/stories/202512020161.html', 'WHO via allAfrica', ': 2025 Kasaï outbreak, 64 cases and 45 deaths'),
 ('https://unsplash.com/@niaid', 'NIAID on Unsplash', 'and Wikimedia Commons: coloured electron micrographs of Ebola virus particles (Unsplash License; NIAID credit)'),
 ('https://s2maps.eu', 'Sentinel-2 cloudless 2024', 'by EOX IT Services (CC BY-NC-SA 4.0)'),
 ('https://earthdata.nasa.gov/gibs', 'NASA GIBS', ': Blue Marble Next Generation and VIIRS Black Marble'),
 ('https://registry.opendata.aws/terrain-tiles/', 'Terrain Tiles on AWS', '; Natural Earth and geoBoundaries (CC BY 4.0) for borders'),
]
src_html = "\n".join(f'        <li><a href="{u}" target="_blank" rel="noopener">{a}</a> {b}</li>' for u, a, b in src)

files = [c["f"] for c in dims["chunks"]] + ["bluemarble.jpg", "blackmarble.jpg"]
# textures ship as separate WebP files so the page text appears at once and images load in parallel and cache
from PIL import Image as _Im
TEXDIR = P("docs", "tex"); os.makedirs(TEXDIR, exist_ok=True)
texmap = {}
for f in files:
    w = f.rsplit(".", 1)[0] + ".webp"
    _Im.open(f"{CON if f in ('bluemarble.jpg', 'blackmarble.jpg') else TER}/{f}").convert("RGB").save(f"{TEXDIR}/{w}", "WEBP", quality=80, method=6)
    texmap[f] = "tex/" + w
html = open(P("scripts", "scroll_template.html")).read()
html = html.replace("__DASHBAND__", open(P("scripts", "dashband.html")).read()).replace("__STEPS__", step_html).replace("__SOURCES__", src_html)
DATA["tex"] = texmap
open(os.path.join(DATADIR, "story.json"), "w").write(json.dumps(DATA, ensure_ascii=False, separators=(",", ":")))
# preload the data and the first chapter's tiles so they download alongside three.js
pre = ['<link rel="preload" as="fetch" href="data/%s" crossorigin="anonymous">' % f for f in ("story.json", "height_det.bin", "height_cont.bin", "vectors.bin")]
# preload only Blue Marble: on slow links the sharp tiles must not compete with the data the live map needs first
pre += ['<link rel="preload" as="image" href="%s" crossorigin="anonymous">' % texmap["bluemarble.jpg"]]
html = html.replace("__PRELOAD__", "\n".join(pre))
open(P("docs", "index.html"), "w").write(html)
print("wrote docs/index.html", len(html), "bytes")
import sys
if "--no-stills" not in sys.argv:
    sys.path.insert(0, P("scripts")); import shoot_stills; shoot_stills.main()
