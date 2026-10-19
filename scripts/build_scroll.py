import json, base64, math
T3 = "/home/claude/tex3"
dims = json.load(open(f"{T3}/dims.json")); cd = json.load(open(f"{T3}/cont_dims.json"))
vec = json.load(open(f"{T3}/vectors.json"))

def lerp_keys(keys, x):
    if x <= keys[0][0]: return keys[0][1]
    for (x0, y0), (x1, y1) in zip(keys, keys[1:]):
        if x <= x1: return y0 + (y1-y0)*(x-x0)/(x1-x0)
    return keys[-1][1]

# story position T for each 2026 outbreak day (day 0 = 15 May 2026)
dayMap = [[16.8, 0], [17.6, 14], [18.6, 39], [19.6, 77], [20.5, 89], [21.4, 136], [22.2, 152], [22.6, 154]]
def T_of_day(d): return lerp_keys([[b, a] for a, b in dayMap], d)

drc_cases = [[0,0],[1,8],[14,225],[18,344],[23,550],[39,1138],[47,1460],[77,3532],[89,4665],[141,8544],[144,8728],[149,9066],[151,9144],[152,9277],[154,9277]]
drc_deaths = [[47,452],[77,1556],[89,2184],[141,4114],[144,4205],[149,4381],[151,4410],[152,4478],[154,4478]]
ituri_share = [[0,1.0],[89,0.853],[152,0.7337],[154,0.7337]]
final = {"nkivu":1991,"haut":398,"tshopo":64,"basuele":13,"sudkivu":3,"sudubangi":2}
rem = sum(final.values())
def prov_keys(pid):
    ks = []
    for d in list(range(0, 153, 2)) + [152, 154]:
        nat = lerp_keys(drc_cases, d); sh = lerp_keys(ituri_share, d)
        v = nat*sh if pid == "ituri" else nat*(1-sh)*final[pid]/rem
        if d == 152 and any(abs(k[0]-T_of_day(152))<1e-6 for k in ks): continue
        ks.append([round(T_of_day(d), 4), round(v, 1)])
    exact = {"ituri": 6806, **final}[pid]; ks[-2][1] = exact; ks[-1][1] = exact
    ks.sort(key=lambda k: k[0]); return ks

Z, SU, BU = "Zaire ebolavirus", "Sudan virus", "Bundibugyo virus"
def sp(id, label, lon, lat, keys, deaths, virus, ease=True, overT=None, overText="", kind="", side="right", dy=0):
    return dict(id=id, label=label, lon=lon, lat=lat, keys=keys, deaths=deaths, virus=virus, ease=ease, overT=overT, overText=overText, kind=kind, side=side, dy=dy)
spikes = [
  sp("sle","Sierra Leone",-11.8,8.5,[[1.0,0],[2.2,14124]],3956,Z,overT=5.2,overText="17 March 2016",kind="national total",side="left",dy=30),
  sp("lbr","Liberia",-9.4,6.5,[[2.8,0],[3.9,10678]],4810,Z,overT=5.4,overText="9 June 2016",kind="national total",dy=64),
  sp("gin","Guinea",-10.1,8.6,[[2.8,0],[3.9,3814]],2544,Z,overT=5.3,overText="1 June 2016",kind="national total",dy=-46),
  sp("nga","Nigeria",3.39,6.52,[[3.0,0],[3.6,20]],8,Z,overT=5.3),
  sp("mli","Mali",-8.0,12.64,[[3.0,0],[3.6,8]],6,Z,overT=5.3),
  sp("beni","North Kivu & Ituri provinces, DR Congo",29.47,0.49,[[8.8,0],[10.0,3470]],2287,Z,overT=11.0,overText="25 June 2020"),
  sp("mub","Mubende District, Central Region, Uganda",31.39,0.56,[[11.9,0],[12.6,164]],77,SU,overT=13.6,overText="11 Jan. 2023",side="left"),
  sp("kla25","Kampala, Central Region, Uganda",32.58,0.31,[[12.6,0],[13.1,14]],4,SU,overT=13.8,overText="26 April 2025",dy=40),
  sp("kas","Bulape, Kasäi Province, DR Congo".replace("ä","ä").replace("ä","aï")[:0] or "Bulape, Kasïi Province, DR Congo",21.8,-4.6,[[14.4,0],[15.0,64]],45,Z,overT=15.9,overText="Dec. 2025"),
]
spikes[-1]["label"] = "Bulape, Kasaï Province, DR Congo"
for pid, label, lon, lat, side, dy in [("ituri","Ituri Province, DR Congo",30.25,1.56,"right",0),("nkivu","North Kivu Province, DR Congo",29.28,0.13,"left",30),
        ("haut","Haut-Uélé Province, DR Congo",27.62,2.77,"left",-20),("tshopo","Tshopo Province, DR Congo",25.19,0.52,"left",0),
        ("basuele","Bas-Uélé Province, DR Congo",24.73,2.80,"left",0),("sudkivu","South Kivu Province, DR Congo",28.86,-2.51,"left",0),
        ("sudubangi","Sud-Ubangi Province, DR Congo",19.77,3.25,"left",0)]:
    d = {"ituri":3148,"nkivu":1133,"haut":167,"tshopo":24,"basuele":4,"sudkivu":1,"sudubangi":1}[pid]
    spikes.append(sp(pid, label, lon, lat, prov_keys(pid), d, BU, ease=False, side=side, dy=dy))
spikes.append(sp("kla26","Uganda, Kampala and border districts",32.42,0.48,[[T_of_day(0),0],[T_of_day(1),2],[T_of_day(48),20]],2,BU,ease=False,overT=23.4,overText="Aug. 2026",dy=36))
spikes.append(sp("nbo","Nairobi County, Kenya",36.82,-1.29,[[25.6,0],[25.8,1],[26.0,2],[26.2,3]],1,BU,ease=False,dy=30))

END = 32.4
WA = ["Sierra Leone","Liberia","Guinea"]; DRC = "Democratic Republic of the Congo"
phases = [
  {"t0":0,"t1":7.2,"date":"2014–2016 · West Africa","ids":["sle","lbr","gin"],"loc":WA},
  {"t0":7.2,"t1":11.4,"date":"2018–2020 · DR Congo","ids":["beni"],"loc":[DRC]},
  {"t0":11.4,"t1":14.0,"date":"2022 & 2025 · Uganda","ids":["mub","kla25"],"loc":["Uganda"]},
  {"t0":14.0,"t1":16.4,"date":"2025 · DR Congo","ids":["kas"],"loc":[DRC]},
  {"t0":16.4,"t1":24.8,"kind":"2026","loc":[DRC,"Uganda"]},
  {"t0":24.8,"t1":28.2,"kind":"2026","loc":[DRC,"Uganda","Kenya"]},
  {"t0":28.2,"t1":END+5,"date":"2014–2026 · every outbreak on this map","ids":"all","loc":[]},
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
  {"t0":25.0,"t1":28.2,"ids":["nbo","ituri"]},{"t0":29.2,"t1":END+5,"ids":["ituri","nbo"]},
]
cam = [[0,-11.0,8.6,30,64,0],[2.0,-11.8,8.6,13,58,0],[4.0,-10.6,8.3,20,62,0],[6.0,-10.6,8.3,22,64,2],
       [8.0,23.5,-2.5,40,70,0],[10.0,29.3,0.7,11,56,0],[11.0,29.6,0.7,12,58,0],
       [12.5,31.8,0.9,13,56,0],[13.6,31.8,0.8,13,58,3],[14.4,23.5,-2.5,38,70,0],[15.0,22.3,-4.4,15,60,0],[16.0,22.4,-4.3,15,62,-2],
       [17.6,29.8,0.9,15,56,0],[20.5,29.4,1.0,18,58,2],[22.2,27.5,0.8,24,62,0],[24.0,30.8,0.6,18,58,0],
       [26.2,32.4,0.3,22,56,0],[27.6,32.6,0.0,22,58,-3],[29.6,13.5,1.0,98,80,0],[END,13.5,1.0,94,84,0]]
route = [["Buta",24.73,2.80,24.95],["Kisangani",25.19,0.52,25.1],["Beni",29.47,0.49,25.3],[None,29.72,0.03,None],
         ["Kampala",32.58,0.31,25.5],[None,32.46,0.05,None],["Nairobi",36.82,-1.29,25.75]]

# country labels: Natural Earth label points for every African country
ad = json.load(open("/home/claude/ne/ne_10m_admin_0_countries.geojson"))["features"]
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

afr = json.load(open("/tmp/claude-0/-home-claude/682b7276-4f53-5c14-ac7d-b6310ac269f9/scratchpad/africa.geo.json"))
locc = []
for f in afr["features"]:
    g = f["geometry"]; polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    locc.append({"name": f["properties"]["name"], "rings": [[round(v, 1) for p in poly[0][::2] for v in p] for poly in polys if len(poly[0]) > 4]})

DATA = dict(
  det=dict(bounds=dims["bounds"], grid=dims["grid"], gp=dims["gp"], hscale=dims["hscale"], b64=open(f"{T3}/height.b64").read()),
  cont=dict(bounds=cd["bounds"], grid=cd["grid"], gp=cd["gp"], hscale=cd["hscale"], b64=open(f"{T3}/cont_height.b64").read()),
  chunks=[{"b": c["b"], "f": c["f"]} for c in dims["chunks"]], vec=vec, spikes=spikes, phases=phases, outlines=O, callouts=callouts, cam=cam,
  route=route, routeT=[24.8, 25.8, 28.2], countryLabels=cl, provLabels=pl, loc={"bounds": [-19, 53, -36, 38], "countries": locc},
  dayMap=dayMap, drcCases=drc_cases, drcDeaths=drc_deaths, uga=[[0,0],[1,2],[48,20]], ugaDeaths=[[0,0],[20,2]],
  march=[["Gu\u00e9ck\u00e9dou",-10.1,8.6,"2014",1],["Beni",29.47,0.49,"2018"],["Mubende",31.39,0.56,"2022"],["Bulape",21.8,-4.6,"2025",1],["Bunia",30.25,1.56,"2026"],["Nairobi",36.82,-1.29,"2026"]],
  marchT=[29.2, 30.9],
  pull=[28.2, 29.6], night=[31.0, 32.2], pullScale=3.2, end=END,
  credit="Imagery: Sentinel-2 cloudless 2024 by EOX, contains modified Copernicus Sentinel data · NASA Blue Marble and Black Marble via GIBS · Elevation: AWS Terrain Tiles · Boundaries: Natural Earth, geoBoundaries",
)

def tags(*v): return "".join(f'<span class="tag {c}">{t}</span>' for c, t in v)
TZ, TS, TB = ("z", "Zaire ebolavirus"), ("s", "Sudan virus"), ("b", "Bundibugyo virus")
steps = [
 (0, "hero", "Ebola in Africa · 2014–2026", "<h1>How Ebola moved across Africa</h1>",
  '<span class="hand">from Sierra Leone to Nairobi</span><p>Twelve years of outbreaks, told place by place. Each spike rises with confirmed cases; grey spikes are outbreaks that have been declared over.</p><p>' + tags(TZ, TS, TB) + '</p><div class="scrollcue">Scroll to begin</div>'),
 (2, "", "2014 · West Africa", "<h2>Sierra Leone</h2>",
  "<p>The largest Ebola epidemic ever recorded reached Sierra Leone in 2014. By the end it had <b>14,124 cases</b> and <b>3,956 deaths</b>, more than any other country.</p><p>" + tags(TZ) + "</p>"),
 (4, "", "2014–2016 · three countries", "<h2>Three spikes, three countries</h2>",
  "<p>Each spike here is one country&rsquo;s <b>national total</b>, not a province: Sierra Leone, <b>Liberia</b> with 10,678 cases, and <b>Guinea</b> with 3,814, where the epidemic began, around Guéckédou.</p><p>Together: <b>28,616 cases</b> and <b>11,310 deaths</b>.</p>"),
 (6, "", "2016", "<h2>Declared over</h2>",
  "<p>WHO declared Sierra Leone&rsquo;s last flare-up over on <b>17 March 2016</b>, Guinea on <b>1 June 2016</b> and Liberia on <b>9 June 2016</b>. The spikes turn grey.</p><p>Ebola is never eradicated, because the virus survives in animals. An outbreak is declared over after 42 days with no new cases.</p>"),
 (8, "", "2018 · DR Congo", "<h2>Four years later, eastern Congo</h2>",
  "<p>In August 2018 Ebola appeared again, in the far east of the Democratic Republic of the Congo, a country of 26 provinces.</p>"),
 (10, "", "2018–2020 · DR Congo", "<h2>North Kivu and Ituri provinces</h2>",
  "<p><b>3,470 cases</b> and <b>2,287 deaths</b> in a conflict zone, across North Kivu, Ituri and South Kivu. It was declared over on <b>25 June 2020</b>.</p><p>" + tags(TZ) + "</p>"),
 (12.5, "", "2022 & 2025 · Uganda", "<h2>Central Region, Uganda</h2>",
  "<p>A different virus. Sudan virus caused <b>164 cases</b> in Mubende District in 2022, declared over on 11 January 2023, and <b>14 cases</b> in Kampala in 2025, declared over on 26 April 2025.</p><p>There is no licensed vaccine for Sudan virus.</p><p>" + tags(TS) + "</p>"),
 (15, "", "2025 · DR Congo", "<h2>Kasaï Province, south-central DRC</h2>",
  "<p>A separate spillover, far from the east: <b>64 cases</b> and <b>45 deaths</b> around Bulape. It was declared over in December 2025.</p><p>" + tags(TZ) + "</p>"),
 (17.6, "", "May 2026 · DR Congo", "<h2>Ituri Province, with a new virus</h2>",
  "<p>On 15 May 2026, DR Congo confirmed an outbreak of <b>Bundibugyo virus</b> in Ituri Province. It had probably been spreading for weeks before anyone detected it, and there is no approved vaccine for it.</p><p>" + tags(TB) + "</p>"),
 (20.5, "", "August 2026", "<h2>The second largest on record</h2>",
  "<p>By 12 August there were <b>4,665 confirmed cases</b>, 85% of them in Ituri. The outbreak had passed the entire 2018&ndash;20 epidemic in about eleven weeks.</p>"),
 (22.2, "", "October 2026 · DR Congo", "<h2>Seven provinces, 9,277 cases</h2>",
  "<p>By 14 October: Ituri <b>6,806</b>, North Kivu <b>1,991</b>, Haut-Uélé <b>398</b>, Tshopo <b>64</b>, Bas-Uélé <b>13</b>, South Kivu <b>3</b> and Sud-Ubangi <b>2</b>.</p><p>Nearly half of confirmed cases have died.</p>"),
 (24, "", "2026 · Uganda", "<h2>Uganda contained its cases</h2>",
  "<p>Uganda recorded <b>20 confirmed cases</b> linked to Congo and declared its outbreak over in August 2026.</p><p>" + tags(TB) + "</p>"),
 (26.2, "", "October 2026 · Kenya", "<h2>Nairobi County, Kenya</h2>",
  "<p>A Kenyan man travelled from Buta in Bas-Uélé through Kisangani and Beni, crossed into Uganda at Mpondwe, and flew from Entebbe to Nairobi on 3 October. He died on 5 October.</p><p>By 16 October Kenya had confirmed <b>3 cases</b>, all linked to him.</p><p>" + tags(TB) + "</p>"),
 (29.6, "", "2014–2026", "<h2>Ebola&rsquo;s march east</h2>",
  "<p>Pulled back over the whole continent, the pattern is clear. West Africa&rsquo;s epidemic is over and Uganda&rsquo;s outbreaks are over; eastern Congo is still active, now with a link to Nairobi.</p><p>The dotted line joins each outbreak in the order it began, from Gu\u00e9ck\u00e9dou in 2014 to Nairobi in 2026. Most were separate jumps from animals to people; only the 2026 path to Nairobi was one chain of infection.</p><p>At this scale spike heights follow the square root of cases.</p>"),
 (END, "", "Africa at night", "<h2>Where people are connected</h2>",
  '<p>NASA&rsquo;s Black Marble shows Africa&rsquo;s lights at night: the cities and transport links that carried this virus from eastern Congo to Nairobi in two days.</p><span class="hand">every spike is a community</span>'),
]
step_html = "\n".join(f'    <section class="step{(" "+cls) if cls else ""}" data-t="{t}"><div class="card{(" "+cls) if cls else ""}"><p class="k">{k}</p>{h}{body}</div></section>' for t, cls, k, h, body in steps)
src = [
 ('https://www.ecdc.europa.eu/en/ebola-outbreak-democratic-republic-congo-and-uganda', 'ECDC', 'DRC cases and deaths by province, data to 14 Oct 2026'),
 ('https://www.who.int/emergencies/disease-outbreak-news/item/2026-DON615', 'WHO Disease Outbreak News', 'and WHO Africa weekly situation reports 21 and 22: 2026 milestones'),
 ('https://www.aljazeera.com/news/2026/10/16/kenya-reports-third-bundibugyo-strain-ebola-case', 'Al Jazeera', 'and the WHO Kenya week 41 report: Kenya cases and the travel route'),
 ('https://www.cdc.gov/ebola/outbreaks', 'US CDC outbreak history', ': outbreaks 2014 to 2025'),
 ('https://www.who.int/en/news-room/detail/17-03-2016-who-statement-on-end-of-ebola-flare-up-in-sierra-leone', 'WHO', 'statements on the end of transmission in Sierra Leone, Guinea and Liberia, 2016'),
 ('https://reliefweb.int/report/uganda/disease-outbreak-news-sudan-virus-disease-uganda-26-april-2025', 'WHO via ReliefWeb', ': Uganda 2025 declared over; ECDC for Uganda 2022'),
 ('https://allafrica.com/stories/202512020161.html', 'WHO via allAfrica', ': 2025 Kasaï outbreak, 64 cases and 45 deaths'),
 ('https://s2maps.eu', 'Sentinel-2 cloudless 2024', 'by EOX IT Services (CC BY-NC-SA 4.0)'),
 ('https://earthdata.nasa.gov/gibs', 'NASA GIBS', ': Blue Marble Next Generation and VIIRS Black Marble'),
 ('https://registry.opendata.aws/terrain-tiles/', 'Terrain Tiles on AWS', '; Natural Earth and geoBoundaries (CC BY 4.0) for borders'),
]
src_html = "\n".join(f'        <li><a href="{u}" target="_blank" rel="noopener">{a}</a> {b}</li>' for u, a, b in src)

files = [c["f"] for c in dims["chunks"]] + ["bluemarble.jpg", "blackmarble.jpg"]
texmap = {f: "data:image/jpeg;base64," + base64.b64encode(open(f"{T3}/{f}", "rb").read()).decode() for f in files}
html = open("/home/claude/scroll_template.html").read()
html = html.replace("__STEPS__", step_html).replace("__SOURCES__", src_html)
html = html.replace("__DATA__", json.dumps(DATA, ensure_ascii=False, separators=(",", ":"))).replace("__TEXMAP__", json.dumps(texmap, separators=(",", ":")))
open("/home/claude/ebola-scroll.html", "w").write(html)
print("ebola-scroll.html", len(html)//1024, "KB")
