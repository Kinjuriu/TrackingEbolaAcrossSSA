"""Build docs/article.html, the long-form article that accompanies the storyboard and dashboard.

Run from the repository root:  python3 scripts/build_article.py
Maths is rendered to static HTML with KaTeX through Node; set KATEX_PATH to a folder holding
the katex npm package (default /tmp/katex), e.g.  npm pack katex@0.16.11 && tar xzf katex-0.16.11.tgz

The article text lives in this file. Light markup inside it:
  [@key]  or [@key1; @key2]   author-year citation with a hover card
  $...$  and  $$...$$          inline and display maths
  [^ text ]                     numbered note: in the margin on wide screens, in Notes on narrow ones
  {{margin: text}}              unnumbered margin note
"""
import csv, html, json, math, os, re, subprocess
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://kinjuriu.github.io/TrackingEbolaAcrossSSA'
GITHUB = 'https://github.com/Kinjuriu'
REPO = 'https://github.com/Kinjuriu/TrackingEbolaAcrossSSA'
LINKEDIN = 'https://www.linkedin.com/in/REPLACE-WITH-YOUR-LINKEDIN'   # TODO Stephane: paste your LinkedIn profile URL
PUBLISHED = '18 November 2026'
TITLE = 'Ebola reached Nairobi. How much further can it go?'
SUBTITLE = ('Where Ebola has appeared in Africa since 1976, how an outbreak grows or dies out, '
            'and what the figures from the 2026 outbreak in DR Congo tell us so far')

Z, S, B = '#9a6a12', '#2a6fb8', '#c0392b'   # Zaire, Sudan, Bundibugyo: the same hues as the storyboard and dashboard

# ---------------------------------------------------------------- references
REFS = {
 'who2026a': ('WHO 2026a', 'World Health Organization. 2026a. &ldquo;Disease Outbreak News: Ebola Disease Caused by Bundibugyo Virus, Democratic Republic of the Congo, Kenya and Nigeria (DON622).&rdquo; 23 October 2026.', 'https://www.who.int/emergencies/disease-outbreak-news/item/2026-DON622'),
 'who2026b': ('WHO 2026b', 'World Health Organization. 2026b. &ldquo;Disease Outbreak News: Ebola Disease Caused by Bundibugyo Virus, Democratic Republic of the Congo (DON615).&rdquo; 14 August 2026.', 'https://www.who.int/emergencies/disease-outbreak-news/item/2026-DON615'),
 'ecdc2026': ('ECDC 2026', 'European Centre for Disease Prevention and Control. 2026. &ldquo;Ebola Disease Outbreak, Democratic Republic of the Congo and Uganda.&rdquo; Updated 16 November 2026, accessed 18 November 2026.', 'https://www.ecdc.europa.eu/en/ebola-outbreak-democratic-republic-congo-and-uganda'),
 'gulfnews2026': ('Gulf News 2026', 'Gulf News. 2026. &ldquo;Saudi Arabia Suspends Travel to Kenya, Bans Visas and Entry over Ebola Concerns.&rdquo; Citing the Saudi Press Agency, 31 October 2026.', 'https://gulfnews.com/world/gulf/saudi/saudi-arabia-suspends-travel-to-kenya-bans-visas-and-entry-over-ebola-concerns-1.500730401'),
 'cdc2026': ('CDC 2026', 'US Centers for Disease Control and Prevention. 2026. &ldquo;History of Ebola Disease Outbreaks.&rdquo; Accessed 14 November 2026.', 'https://www.cdc.gov/ebola/outbreaks/index.html'),
 'who2025': ('WHO 2025', 'World Health Organization. 2025. &ldquo;Ebola Disease.&rdquo; Fact sheet, 24 April 2025.', 'https://www.who.int/news-room/fact-sheets/detail/ebola-disease'),
 'towner2008': ('Towner et al. 2008', 'Towner, Jonathan S., Tara K. Sealy, Marina L. Khristova, et al. 2008. &ldquo;Newly Discovered Ebola Virus Associated with Hemorrhagic Fever Outbreak in Uganda.&rdquo; <i>PLoS Pathogens</i> 4 (11): e1000212.', 'https://doi.org/10.1371/journal.ppat.1000212'),
 'marisaez2015': ('Mar&iacute; Sa&eacute;z et al. 2015', 'Mar&iacute; Sa&eacute;z, Almudena, Sabrina Weiss, Kathrin Nowak, et al. 2015. &ldquo;Investigating the Zoonotic Origin of the West African Ebola Epidemic.&rdquo; <i>EMBO Molecular Medicine</i> 7 (1): 17&ndash;23.', 'https://doi.org/10.15252/emmm.201404792'),
 'keita2021': ('Keita et al. 2021', 'Keita, Alpha K., Fara R. Koundouno, Martin Faye, et al. 2021. &ldquo;Resurgence of Ebola Virus in 2021 in Guinea Suggests a New Paradigm for Outbreaks.&rdquo; <i>Nature</i> 597 (7877): 539&ndash;43.', 'https://doi.org/10.1038/s41586-021-03901-9'),
 'whoert2014': ('WHO Ebola Response Team 2014', 'WHO Ebola Response Team. 2014. &ldquo;Ebola Virus Disease in West Africa: The First 9 Months of the Epidemic and Forward Projections.&rdquo; <i>New England Journal of Medicine</i> 371 (16): 1481&ndash;95.', 'https://doi.org/10.1056/NEJMoa1411100'),
 'cori2013': ('Cori et al. 2013', 'Cori, Anne, Neil M. Ferguson, Christophe Fraser, and Simon Cauchemez. 2013. &ldquo;A New Framework and Software to Estimate Time-Varying Reproduction Numbers During Epidemics.&rdquo; <i>American Journal of Epidemiology</i> 178 (9): 1505&ndash;12.', 'https://doi.org/10.1093/aje/kwt133'),
 'wallinga2007': ('Wallinga and Lipsitch 2007', 'Wallinga, Jacco, and Marc Lipsitch. 2007. &ldquo;How Generation Intervals Shape the Relationship Between Growth Rates and Reproductive Numbers.&rdquo; <i>Proceedings of the Royal Society B</i> 274 (1609): 599&ndash;604.', 'https://doi.org/10.1098/rspb.2006.3754'),
 'blumberg2013': ('Blumberg and Lloyd-Smith 2013', 'Blumberg, Seth, and James O. Lloyd-Smith. 2013. &ldquo;Comparing Methods for Estimating R0 from the Size Distribution of Subcritical Transmission Chains.&rdquo; <i>Epidemics</i> 5 (3): 131&ndash;45.', 'https://doi.org/10.1016/j.epidem.2013.05.002'),
 'lloydsmith2005': ('Lloyd-Smith et al. 2005', 'Lloyd-Smith, James O., Sebastian J. Schreiber, P. Ekkehard Kopp, and Wayne M. Getz. 2005. &ldquo;Superspreading and the Effect of Individual Variation on Disease Emergence.&rdquo; <i>Nature</i> 438: 355&ndash;59.', 'https://doi.org/10.1038/nature04153'),
 'fraser2004': ('Fraser et al. 2004', 'Fraser, Christophe, Steven Riley, Roy M. Anderson, and Neil M. Ferguson. 2004. &ldquo;Factors That Make an Infectious Disease Outbreak Controllable.&rdquo; <i>Proceedings of the National Academy of Sciences</i> 101 (16): 6146&ndash;51.', 'https://doi.org/10.1073/pnas.0307506101'),
 'henao2017': ('Henao-Restrepo et al. 2017', 'Henao-Restrepo, Ana Maria, Anton Camacho, Ira M. Longini, et al. 2017. &ldquo;Efficacy and Effectiveness of an rVSV-Vectored Vaccine in Preventing Ebola Virus Disease: Final Results from the Guinea Ring Vaccination, Open-Label, Cluster-Randomised Trial (Ebola &Ccedil;a Suffit!).&rdquo; <i>The Lancet</i> 389 (10068): 505&ndash;18.', 'https://doi.org/10.1016/S0140-6736(16)32621-6'),
 'mooring2026': ('Mooring et al. 2026', 'Mooring, Eric Q., Wendy T. Koval, Isobel Routledge, et al. 2026. &ldquo;Modeled Scenario Projections for the Ebola Disease Outbreak Caused by Bundibugyo Virus, 2026.&rdquo; <i>Morbidity and Mortality Weekly Report</i> 75 (22): 285&ndash;89.', 'https://www.cdc.gov/mmwr/volumes/75/wr/mm7522e1.htm'),
 'verheyden2026': ('Verheyden, Nzanzu Mudogo, and Jacquet 2026', 'Verheyden, J. G. L., C. Nzanzu Mudogo, and W. Jacquet. 2026. &ldquo;Sub-National Heterogeneity in the Time-Varying Reproduction Number During the 2026 Bundibugyo Virus Disease Outbreak in the Democratic Republic of the Congo: A Hierarchical Bayesian Analysis.&rdquo; <i>medRxiv</i> preprint, version 2, 11 September 2026.', 'https://www.medrxiv.org/content/10.64898/2026.08.19.26360792v2.full'),
 'virological2026': ('Virological 2026', 'Virological. 2026. &ldquo;Reproduction Number of the 2026 Bundibugyo Virus Disease Outbreak over Time: Phylodynamic Estimates from Genomes Collected up to 5 October 2026.&rdquo; Forum post, October 2026.', 'https://virological.org/t/reproduction-number-of-the-2026-bundibugyo-virus-disease-outbreak-over-time-phylodynamic-estimates-from-genomes-collected-up-to-5-october-2026/1051'),
 'vanzandvoort2026': ('van Zandvoort et al. 2026', 'van Zandvoort, Kevin, Simon R. Procter, Jose M. Azam, Katharine Sherratt, and Nicholas G. Davies. 2026. &ldquo;The Risk of Global Ebola Virus Spread Is Low: Epidemiology of Ebola Disease Cases Outside Africa, 1976 to May 2026.&rdquo; <i>Eurosurveillance</i> 31 (24).', 'https://doi.org/10.2807/1560-7917.ES.2026.31.24.2600508'),
 'chevalier2014': ('Chevalier et al. 2014', 'Chevalier, Michelle S., Wendy Chung, Jason Smith, et al. 2014. &ldquo;Ebola Virus Disease Cluster in the United States: Dallas County, Texas, 2014.&rdquo; <i>Morbidity and Mortality Weekly Report</i> 63 (46): 1087&ndash;88.', 'https://www.cdc.gov/mmwr/preview/mmwrhtml/mm6346a11.htm'),
 'who2014': ('WHO 2014', 'World Health Organization. 2014. &ldquo;Disease Outbreak News: Ebola Virus Disease, Spain.&rdquo; 9 October 2014.', 'https://www.who.int/emergencies/disease-outbreak-news/item/09-october-2014-ebola-en'),
 'worldbank': ('World Bank n.d.', 'World Bank. n.d. &ldquo;Current Health Expenditure per Capita (Current US$), SH.XPD.CHEX.PC.CD.&rdquo; From the WHO Global Health Expenditure Database; 2022 values.', 'https://data.worldbank.org/indicator/SH.XPD.CHEX.PC.CD?locations=KE-US-ES'),
 'poletto2014': ('Poletto et al. 2014', 'Poletto, Chiara, Marcelo F. Gomes, Ana Pastore y Piontti, et al. 2014. &ldquo;Assessing the Impact of Travel Restrictions on International Spread of the 2014 West African Ebola Epidemic.&rdquo; <i>Eurosurveillance</i> 19 (42): 20936.', 'https://doi.org/10.2807/1560-7917.ES2014.19.42.20936'),
 'bogoch2015': ('Bogoch et al. 2015', 'Bogoch, Isaac I., Maria I. Creatore, Martin S. Cetron, et al. 2015. &ldquo;Assessment of the Potential for International Dissemination of Ebola Virus via Commercial Air Travel During the 2014 West African Outbreak.&rdquo; <i>The Lancet</i> 385 (9962): 29&ndash;35.', 'https://doi.org/10.1016/S0140-6736(14)61828-6'),
 'google': ('Google n.d.', 'Google. n.d. &ldquo;FAQ about Google Trends Data.&rdquo; Accessed 7 November 2026.', 'https://support.google.com/trends/answer/4365533?hl=en'),
 'alicino2015': ('Alicino et al. 2015', 'Alicino, Cristiano, Nicola Luigi Bragazzi, Valeria Faccio, et al. 2015. &ldquo;Assessing Ebola-Related Web Search Behaviour: Insights and Implications from an Analytical Study of Google Trends-Based Query Volumes.&rdquo; <i>Infectious Diseases of Poverty</i> 4: 54.', 'https://doi.org/10.1186/s40249-015-0090-9'),
 'towers2015': ('Towers et al. 2015', 'Towers, Sherry, Shehzad Afzal, Gilbert Bernal, et al. 2015. &ldquo;Mass Media and the Contagion of Fear: The Case of Ebola in America.&rdquo; <i>PLoS One</i> 10 (6): e0129179.', 'https://doi.org/10.1371/journal.pone.0129179'),
}

# ---------------------------------------------------------------- data
def read_reports():
    with open(os.path.join(ROOT, 'docs/data/drc_2026_reports.csv'), newline='') as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r['day'] = date.fromisoformat(r['date']); r['confirmed'] = int(r['confirmed'])
        r['deaths'] = int(r['deaths']) if r['deaths'] else None
    return rows

REPORTS = read_reports()
LAST = REPORTS[-1]

OUTBREAKS = [  # place, years, virus, cases (for figure 1)
 ('West Africa', '2014 to 2016', 'Zaire', 28600), ('DR Congo', '2026, to 15 Nov', 'Bundibugyo', LAST['confirmed']),
 ('DR Congo (North Kivu, Ituri)', '2018 to 2020', 'Zaire', 3470), ('Uganda (Gulu)', '2000', 'Sudan', 425),
 ('DR Congo (Yambuku)', '1976', 'Zaire', 318), ('Uganda (Mubende)', '2022', 'Sudan', 164),
 ('Uganda (Bundibugyo)', '2007', 'Bundibugyo', 149), ('DR Congo (Kasa&iuml;)', '2025', 'Zaire', 64),
 ('DR Congo (Isiro)', '2012', 'Bundibugyo', 62)]
VCOL = {'Zaire': Z, 'Sudan': S, 'Bundibugyo': B}

def fmt(n): return f'{n:,}'

# ---------------------------------------------------------------- figures (static SVG, readable with JavaScript off)
FONT = "font-family='Source Sans 3, Source Sans Pro, system-ui, sans-serif'"

def fig_sizes():
    W, x0, w, y0, rh = 760, 300, 330, 14, 32
    mx = max(o[3] for o in OUTBREAKS); H = y0 + rh * len(OUTBREAKS) + 8
    out = [f"<svg viewBox='0 0 {W} {H}' role='img' aria-labelledby='fig-sizes-cap' {FONT} font-size='14'>"]
    for i, (pl, yr, v, c) in enumerate(OUTBREAKS):
        y = y0 + i * rh; bw = max(c / mx * w, 2)
        out.append(f"<g><title>{pl}, {yr}: {fmt(c)} cases, {v} virus</title>"
                   f"<text x='{x0-10}' y='{y+14}' text-anchor='end' fill='#1d2330'>{pl}, {yr}</text>"
                   f"<rect x='{x0}' y='{y}' width='{bw:.1f}' height='19' fill='{VCOL[v]}'/>"
                   f"<text x='{x0+bw+7:.1f}' y='{y+14}' fill='#1d2330'><tspan font-weight='600'>{fmt(c)}</tspan>"
                   f"<tspan fill='#5b6472'>  {v}</tspan></text></g>")
    out.append(f"<line x1='{x0}' x2='{x0}' y1='{y0-6}' y2='{H-8}' stroke='#1d2330'/></svg>")
    return ''.join(out)

def xscale(d, x0=56, x1=740, d0=date(2026, 5, 15), d1=date(2026, 11, 18)):
    return x0 + (d - d0).days / (d1 - d0).days * (x1 - x0)

def month_axis(y):
    o = []
    for m in range(6, 12):
        d = date(2026, m, 1)
        o.append(f"<text x='{xscale(d):.1f}' y='{y}' text-anchor='middle' fill='#5b6472'>{d.strftime('%b')}</text>")
    return ''.join(o)

def fig_cumulative():
    W, H, ytop, ybot, ymax = 760, 330, 16, 290, 12000
    y = lambda v: ybot - v / ymax * (ybot - ytop)
    o = [f"<svg viewBox='0 0 {W} {H}' role='img' aria-labelledby='fig-cum-cap' {FONT} font-size='14'>"]
    for t in (0, 4000, 8000, 12000):
        o.append(f"<line x1='56' x2='740' y1='{y(t):.1f}' y2='{y(t):.1f}' stroke='{'#1d2330' if t == 0 else '#e3e6ea'}'/>"
                 f"<text x='48' y='{y(t)+5:.1f}' text-anchor='end' fill='#5b6472'>{fmt(t)}</text>")
    xn = xscale(date(2026, 10, 3))
    o.append(f"<line x1='{xn:.1f}' x2='{xn:.1f}' y1='{ytop}' y2='{ybot}' stroke='#5b6472' stroke-dasharray='3 4'/>"
             f"<text x='{xn-8:.1f}' y='{ytop+14}' text-anchor='end' fill='#5b6472'>First case in Nairobi, 3 Oct</text>")
    for key, col, lab, dy in (('deaths', '#4a5260', 'deaths', 30), ('confirmed', B, 'confirmed cases', -14)):
        pts = [r for r in REPORTS if r[key] is not None]
        path = ' '.join(f"{'M' if i == 0 else 'L'}{xscale(r['day']):.1f},{y(r[key]):.1f}" for i, r in enumerate(pts))
        o.append(f"<path d='{path}' fill='none' stroke='{col}' stroke-width='2.5'/>")
        for r in pts:
            o.append(f"<circle cx='{xscale(r['day']):.1f}' cy='{y(r[key]):.1f}' r='3.5' fill='{col}'>"
                     f"<title>{r['day'].strftime('%-d %b %Y')}: {fmt(r[key])} {lab} ({r['source']})</title></circle>")
        last = pts[-1]
        o.append(f"<text x='{xscale(last['day']):.1f}' y='{y(last[key])+dy:.1f}' text-anchor='end' font-weight='600' fill='{col}'>{fmt(last[key])} {lab}</text>")
    o.append(month_axis(H - 12) + '</svg>')
    return ''.join(o)

def daily_bars():
    out = []
    for p, r in zip(REPORTS, REPORTS[1:]):
        days = (r['day'] - p['day']).days; n = r['confirmed'] - p['confirmed']
        out.append(dict(p=p, r=r, days=days, n=n, rate=n / days))
    return out

def fig_daily():
    W, H, ytop, ybot, ymax = 760, 300, 16, 262, 90
    y = lambda v: ybot - v / ymax * (ybot - ytop)
    bars = daily_bars()
    o = [f"<svg viewBox='0 0 {W} {H}' role='img' aria-labelledby='fig-daily-cap' {FONT} font-size='14'>"]
    for t in (0, 20, 40, 60, 80):
        o.append(f"<line x1='56' x2='740' y1='{y(t):.1f}' y2='{y(t):.1f}' stroke='{'#1d2330' if t == 0 else '#e3e6ea'}'/>"
                 f"<text x='48' y='{y(t)+5:.1f}' text-anchor='end' fill='#5b6472'>{t}</text>")
    for i, b in enumerate(bars):
        xa, xb = xscale(b['p']['day']) + 1, xscale(b['r']['day']) - 1
        op = 1 if i == len(bars) - 1 else 0.55
        o.append(f"<rect x='{xa:.1f}' y='{y(b['rate']):.1f}' width='{max(xb-xa,2):.1f}' height='{ybot-y(b['rate']):.1f}' fill='{B}' fill-opacity='{op}'>"
                 f"<title>{b['p']['day'].strftime('%-d %b')} to {b['r']['day'].strftime('%-d %b')}: {b['rate']:.0f} new confirmed cases a day "
                 f"({fmt(b['n'])} cases over {b['days']} days)</title></rect>")
        if xb - xa >= 18:
            o.append(f"<text x='{(xa+xb)/2:.1f}' y='{y(b['rate'])-6:.1f}' text-anchor='middle' fill='#1d2330' font-size='13'>{b['rate']:.0f}</text>")
    o.append(month_axis(H - 12) + '</svg>')
    return ''.join(o)

# ---------------------------------------------------------------- R code with outputs (outputs match what R prints)
def r_dataframe(rows, cols):
    """Mimic R's print.data.frame for the reports table."""
    def cell(v, dec=None):
        if v is None: return 'NA'
        return f'{v:.{dec}f}' if dec is not None else str(v)
    table = [[cell(r[c], d) for c, d in cols] for r in rows]
    heads = [c for c, _ in cols]
    widths = [max(len(h), *(len(t[i]) for t in table)) for i, h in enumerate(heads)]
    rn = [str(i + 1) for i in range(len(rows))]; rw = max(len(x) for x in rn)
    lines = [' ' * rw + ' ' + ' '.join(h.rjust(w) for h, w in zip(heads, widths))]
    for name, t in zip(rn, table):
        lines.append(name.ljust(rw) + ' ' + ' '.join(v.rjust(w) for v, w in zip(t, widths)))
    return '\n'.join(lines)

def code_daily():
    rows = []
    prev = None
    for r in REPORTS:
        d = dict(date=r['date'], confirmed=r['confirmed'], days=None, new=None, per_day=None)
        if prev:
            d['days'] = (r['day'] - prev['day']).days; d['new'] = r['confirmed'] - prev['confirmed']
            d['per_day'] = round(d['new'] / d['days'], 1)
        rows.append(d); prev = r
    code = f'''# Average new confirmed cases per day between reports, DR Congo, 2026
reports <- read.csv("{SITE}/data/drc_2026_reports.csv")
reports$date    <- as.Date(reports$date)
reports$days    <- c(NA, diff(reports$date))       # days since the previous report
reports$new     <- c(NA, diff(reports$confirmed))  # new confirmed cases since then
reports$per_day <- round(reports$new / reports$days, 1)
reports[, c("date", "confirmed", "days", "new", "per_day")]'''
    out = r_dataframe(rows, [('date', None), ('confirmed', None), ('days', None), ('new', None), ('per_day', 1)])
    return code, out

CODE_GROWTH = ('''# Daily growth rate and doubling time from R and the generation time
# (Wallinga and Lipsitch 2007); generation time from WHO Ebola Response Team (2014)
T_gen    <- 15.3
R        <- c(2, 1.4)
r        <- log(R) / T_gen
doubling <- log(2) / r
data.frame(R, r = round(r, 4), doubling = round(doubling, 1))''',
'''    R      r doubling
1 2.0 0.0453     15.3
2 1.4 0.0220     31.5''')

CODE_CHAINS = ('''# Expected size of a chain started by one case when R is below 1
chain_size <- function(R) 1 / (1 - R)
chain_size(c(0.5, 0.8))

# Chance that a chain dies out on its own when R = 2, if the number of people
# each case infects follows a Poisson distribution: the smallest root of q = exp(R(q - 1))
q <- uniroot(function(q) q - exp(2 * (q - 1)), c(0, 0.99))$root
round(q, 3)''',
'''[1] 2 5
[1] 0.203''')

CODE_EXPORTS = (f'''# Expected cases outside Africa on the historical rate (van Zandvoort et al. 2026)
rate     <- 0.17 / 1000        # cases outside Africa per case reported in Africa, since 2000
cases    <- {LAST['confirmed']}            # confirmed cases in DR Congo, {LAST['day'].strftime('%-d %B %Y')}
expected <- rate * cases
round(expected, 2)
round(dpois(0, expected), 2)  # chance of no unplanned arrival at all

# Health spending per person in 2022, as a multiple of Kenya's (World Bank)
spend <- c(Kenya = 91, Spain = 2950, `United States` = 12600)
round(spend / spend["Kenya"])''',
f'''[1] {round(0.17/1000*LAST['confirmed'], 2)}
[1] {round(math.exp(-0.17/1000*LAST['confirmed']), 2)}
        Kenya         Spain United States
            1            32           138 ''')

def r_highlight(src):
    src = html.escape(src)
    toks = re.compile(r'(#[^\n]*)|(&quot;.*?&quot;)|(`[^`]*`)|(\b\d+(?:\.\d+)?\b)|(\b[A-Za-z_.][A-Za-z0-9_.]*(?=\())|(&lt;-|\$)')
    def rep(m):
        if m.group(1): return f'<span class="co">{m.group(1)}</span>'
        if m.group(2): return f'<span class="st">{m.group(2)}</span>'
        if m.group(3): return f'<span class="st">{m.group(3)}</span>'
        if m.group(4): return f'<span class="dv">{m.group(4)}</span>'
        if m.group(5): return f'<span class="fu">{m.group(5)}</span>'
        return f'<span class="op">{m.group(6)}</span>'
    return toks.sub(rep, src)

def code_block(code, out, label='Code'):
    return (f'<details class="code"><summary>{label}</summary><pre class="r"><code>{r_highlight(code)}</code></pre></details>'
            f'<pre class="out"><code>{html.escape(out)}</code></pre>')

# ---------------------------------------------------------------- the article text
DRAFT_S = ('<div class="draft"><b>Draft note for Stephane.</b> One or two sentences in your own words about that week in Nairobi: '
           'what you saw, heard or were asked by family. Delete this box if you would prefer to leave it out.</div>')
DRAFT_L = ('<div class="draft"><b>Draft note for Lianne.</b> A sentence or two in your own words on what the response teams in Ituri '
           'are up against, or on whether the simplified isolation formula above is fair to use here.</div>')

dcode, dout = code_daily()
bars = daily_bars()
since_july = [b for b in bars if b['p']['day'] >= date(2026, 7, 1)]
lo, hi = round(min(b['rate'] for b in since_july)), round(max(b['rate'] for b in since_july))
cfr = round(LAST['deaths'] / LAST['confirmed'] * 100)
NTEX = f"{LAST['confirmed']:,}".replace(',', '{,}')

SECTIONS = [
('intro', 'A case in Nairobi', f'''
<p>On 3 October 2026, a man who had been ill for about a month, and who had already been treated at several hospitals in the eastern Democratic Republic of the Congo (DR Congo), travelled by road into Uganda and then flew to Nairobi, where hospital staff isolated him as soon as he arrived. The World Health Organization (WHO) reports that samples taken two days later tested positive for Bundibugyo virus, one of the three viruses known to cause large outbreaks of Ebola disease in people, and that he died the same day [@who2026a].</p>
{DRAFT_S}
<p>Eight more people in Kenya later tested positive, and all eight had been close to him: four were members of his family and four were health and care workers, and one of the eight died [@who2026a]. Every one of them was already in quarantine, meaning that they were being kept apart from other people and checked each day for symptoms, by the time they fell ill, and this is why the count stopped at nine. The European Centre for Disease Prevention and Control (ECDC), the public health agency of the European Union, reports that Kenya recorded its last case on 20 October, that seven of the nine patients had recovered by 11 November, and that every person traced as a contact had finished 21 days of monitoring without falling ill [@ecdc2026].{{{{margin: A <b>contact</b> is anyone who has touched a patient, their body fluids or their bedding, or shared a household or ward with them, since the patient&rsquo;s symptoms began.}}}}</p>
<p>The containment of the Nairobi cluster did little to calm the alarm that the case set off abroad. Gulf News, citing the Saudi Press Agency, reported that on 30 October Saudi Arabia suspended visas for travellers from Kenya and barred them from entering the kingdom [@gulfnews2026],[^ The suspension also covers anyone who has been in another affected country in the previous 21 days, the longest time that symptoms can take to appear. ] which brought the number of countries that had restricted travel from the region since May to at least twelve; the <a href="./dashboard.html#travel">dashboard</a> lists each restriction with its date and source.</p>
<p>The outbreak that the traveller carried with him is far larger than the cluster it seeded in Kenya: DR Congo&rsquo;s health ministry declared it in Ituri province, in the far north-east of the country, on 15 May 2026, and WHO declared it a public health emergency of international concern, its highest level of alert, two days later [@who2026a; @who2026b]. By {LAST['day'].strftime('%-d %B')}, ECDC counted {fmt(LAST['confirmed'])} confirmed cases and {fmt(LAST['deaths'])} deaths across eight of DR Congo&rsquo;s provinces, which makes it the largest Ebola outbreak since the West African epidemic of 2014 to 2016 [@ecdc2026].</p>
<p>We began this article by asking whether a disease that has now reached a city with direct flights to the Gulf, Europe and Asia will go on to reach the rest of the world. The evidence in the sections that follow shows that it already has, in small numbers, so the more useful question is what happens after an infected person arrives somewhere new, and the answer depends on how many people each patient infects and on how quickly health workers find and isolate those patients.</p>
'''),
('old-virus', 'An old virus', '''
<p>Ebola is far older than the twelve years our <a href="./">storyboard</a> covers, and starting the record in 2014 can make it look like a disease that began in West Africa and moved east. The US Centers for Disease Control and Prevention (CDC) and WHO both record that the virus was first identified in 1976, in two outbreaks a few months and several hundred kilometres apart: one around Yambuku, a village near the Ebola River in what is now DR Congo, where 318 people fell ill and 280 died, and one in Nzara, in what is now South Sudan [@cdc2026; @who2025]. East Africa also met the disease long before 2014, since an outbreak of Sudan virus around Gulu, in northern Uganda, infected 425 people in 2000 and remained the largest Ebola outbreak on record until the West African epidemic [@cdc2026].</p>
<p>The name Ebola covers six related viral species, meaning six distinct kinds of virus within the same family, and three of them have caused large outbreaks in people: Ebola virus itself, often called Zaire virus after the former name of DR Congo; Sudan virus; and Bundibugyo virus [@who2025]. All three cause the same illness, which begins suddenly with fever, exhaustion, muscle pain and a sore throat and can go on to vomiting, diarrhoea and failing kidneys and liver; across past outbreaks about half of all patients have died, although the share has ranged from 25 to 90 percent depending on the virus and on the care that patients received [@who2025].</p>
<p>The differences between the three viruses matter most for medicine, since the two approved vaccines and the two antibody treatments that exist were all developed against Zaire virus, and none of them is approved for use against Sudan or Bundibugyo virus [@who2025]. Bundibugyo virus is also the least studied of the three, as it had caused only two outbreaks before this year: the first in 2007, in the Bundibugyo district of western Uganda, which WHO counted at 149 cases and CDC at 131,[^ Counts of the same outbreak often differ between agencies, because each decides differently which suspected and probable cases to include and when to close the count. ] and the second in 2012, around Isiro in north-eastern DR Congo, where CDC counted 62 cases [@towner2008; @cdc2026; @who2025]. The 2026 outbreak has already passed 11,000 confirmed cases, about 76 times the size of the first, and health workers are fighting it without a licensed vaccine or drug; WHO reports that a trial of candidate vaccines began enrolling volunteers in Bunia, the capital of Ituri, on 23 October [@who2026a].</p>
<p>Every outbreak starts with what scientists call a spillover, meaning the moment a person catches the virus from an infected animal, most likely through contact with the blood or meat of a fruit bat or of another wild animal [@who2025]. Mar&iacute; Sa&eacute;z and colleagues traced the West African epidemic to a two-year-old boy in Meliandou, a village in southern Guinea, who fell ill in December 2013 and may have been infected while playing in a hollow tree that housed a colony of insect-eating bats [@marisaez2015].</p>
<p>Once the virus is in a person, it passes to others through direct contact with the blood or body fluids of someone who is sick or has died, or with bedding and clothing soiled by those fluids [@who2025]. Three groups of people therefore face the highest risk of infection: relatives who nurse a patient at home, health workers who care for patients without full protective equipment, and mourners who wash and touch the body before burial. The eight people infected in Kenya, four relatives and four care workers, came from the first two of these groups.</p>
<p>Two features of the illness decide how an outbreak can be stopped: symptoms take between 2 and 21 days to appear after a person is infected, and according to WHO a person cannot pass the virus on until those symptoms appear [@who2025]. The virus can still survive for months in some parts of the body after a patient recovers, particularly in semen, and Keita and colleagues showed that the 2021 outbreak in Guinea began this way, since the genomes of the virus taken from its patients sat within the family tree of the 2014 to 2016 virus and showed no sign of a new spillover from an animal [@keita2021].</p>
'''),
('map', 'What the storyboard shows, and what it hides', f'''
<p>Our <a href="./">storyboard</a> draws each outbreak since 2014 as a spike on satellite imagery, with the height of each spike set by its number of cases and its colour set by the virus that caused it, and it turns a spike grey once the outbreak is declared over; the <a href="./dashboard.html">dashboard</a> holds the same outbreaks in a table that readers can filter by year, country, virus and status. Scrolled from start to finish, the storyboard&rsquo;s spikes move from the Atlantic coast of West Africa to the Great Lakes region of East and Central Africa, and it is easy to read that movement as one disease travelling across the continent. Figure 1 sets the sizes of the largest outbreaks side by side, including the older ones that the storyboard leaves out.</p>
<figure class="fig" id="fig-1">{fig_sizes()}<figcaption id="fig-sizes-cap"><b>Figure 1:</b> The 2026 Bundibugyo outbreak is the second largest Ebola outbreak on record. Cases in selected outbreaks since 1976, coloured by virus: <span class="k" style="--c:{Z}">Zaire</span>, <span class="k" style="--c:{S}">Sudan</span> and <span class="k" style="--c:{B}">Bundibugyo</span>. The 2026 count is confirmed cases only; older counts include probable and suspected cases. Sources: CDC (2026), WHO (2025), ECDC (2026).</figcaption></figure>
<details class="callout"><summary>Confirmed, probable and suspected cases: why the counts in Figure 1 are not quite alike</summary>
<p>Health agencies sort patients into three groups. A <b>confirmed</b> case has tested positive in a laboratory; a <b>probable</b> case was never tested, often because the person died before a sample could be taken, but had the symptoms and a clear link to a confirmed case; and a <b>suspected</b> case has symptoms and a possible exposure but is still waiting for a result. The final totals for older outbreaks add the probable cases, and for West Africa the suspected ones as well, whereas the running count for 2026 includes confirmed cases only, so the 2026 bar in Figure 1 understates that outbreak when it is set against the others.</p></details>
<p>The West African epidemic remains the largest by far: between 2014 and 2016, Zaire virus spread from Meliandou through Guinea, Liberia and Sierra Leone, reached all three capital cities, and infected more than 28,600 people, of whom more than 11,300 died, according to CDC figures that include suspected and probable cases as well as cases confirmed in a laboratory [@cdc2026]. Travellers and evacuated patients carried a small number of cases from the region to Nigeria, Mali, Senegal, the United States, Spain, the United Kingdom and Italy [@cdc2026].</p>
<p>The next large outbreak began in 2018 in North Kivu and Ituri, in eastern DR Congo, where fighting between armed groups often kept health workers from reaching patients and the people those patients had been in contact with; it lasted almost two years and ended with 3,470 cases and 2,287 deaths [@cdc2026]. Smaller outbreaks followed in Guinea in 2021, in DR Congo, including 64 cases in Kasa&iuml; province in 2025, and in Uganda, where Sudan virus caused 164 cases around Mubende in 2022 and 14 in Kampala in 2025 [@cdc2026].</p>
<p>The Bundibugyo outbreak that began in Ituri in May 2026 has since spread to eight of DR Congo&rsquo;s provinces and has crossed international borders three times that we know of: into Uganda, where 20 cases were confirmed before that chain of infection was declared over in August; into Kenya, with the traveller who flew to Nairobi; and to Nigeria, where a person who had travelled from Uganda fell ill in Abuja in October [@who2026a; @ecdc2026].</p>
<p>What the map hides is that the spikes in West Africa and the spikes in DR Congo are separate events, since each began with its own spillover from animals, years apart and thousands of kilometres from each other, and the outbreaks in Uganda and this year&rsquo;s outbreak in DR Congo were caused by different viruses altogether. The only stretch of the line from west to east that is a single chain of infection, passed from one person to the next, is the last one, from Ituri to Nairobi, and starting the clock in 2014 makes the pattern look neater than it is, since Central and East Africa had already been dealing with Ebola for almost forty years by then.</p>
<p>The map is therefore best read as a record of where the virus has surfaced, and each time it surfaces, the same two things decide how large the outbreak becomes: how many people each patient infects, and how quickly health workers find and isolate those patients.</p>
'''),
('arithmetic', 'The arithmetic of an outbreak', f'''
<p>Epidemiologists, meaning scientists who study how diseases spread through populations, summarise the growth of an outbreak with the reproduction number, written $R$, which is the average number of people that one infected person goes on to infect. If we call the first patient generation zero, the people that patient infects generation one, and the people they in turn infect generation two, then with each case infecting $R$ others on average, the expected number of new cases in generation $n$ is</p>
$$E[C_n] = R^{{\\,n}}$$
<p>When $R$ is above 1, each generation is larger than the one before and the outbreak grows; when $R$ is below 1, each generation is smaller and the outbreak shrinks until it runs out of people to infect. At the start of an outbreak, before anyone has responded, the value is written $R_0$ and called the basic reproduction number, and the WHO Ebola Response Team estimated it at 1.71 in Guinea, 1.83 in Liberia and 2.02 in Sierra Leone during the West African epidemic, meaning that each patient infected roughly two others before control measures took hold [@whoert2014]. Once a response is under way, the value on a given day is written $R_t$ and called the effective reproduction number,[^ The small $t$ stands for time: $R_t$ is the value on day $t$, and it changes as people are isolated, treated or vaccinated. ] and health agencies most often estimate it from daily case counts with a method developed by Cori and colleagues [@cori2013].</p>
<p>The speed at which one generation follows another depends on the generation time, meaning the average gap between one person falling ill and the people they infect falling ill, which the WHO Ebola Response Team measured at 15.3 days in West Africa [@whoert2014]. Wallinga and Lipsitch showed how the daily growth rate $r$ and the doubling time $T_d$, meaning the number of days it takes for case numbers to double, follow from $R$ and the generation time $T$ [@wallinga2007]:</p>
$$r = \\frac{{\\ln R}}{{T}}, \\qquad T_d = \\frac{{\\ln 2}}{{r}}$$
<p>With $R$ at 2 and $T$ at 15.3 days, cases double every 15.3 days, which means sixteen times as many new cases after two months.[^ Two months is about four generations of 15.3 days, and four doublings give $2^4 = 16$. ] With $R$ at 1.4, the doubling time stretches to about 31 days, close to the 30.2 days that the WHO Ebola Response Team measured in Sierra Leone in September 2014, when it estimated that the reproduction number there had already fallen from 2.02 to 1.38 [@whoert2014].</p>
{code_block(*CODE_GROWTH)}
<p>The same arithmetic explains why most introductions of the virus into a new place go nowhere. Blumberg and Lloyd-Smith describe how, if $R$ is held below 1 where an infected traveller arrives, the expected size of the whole chain that the traveller starts, counting the traveller, is the sum of every generation [@blumberg2013]:</p>
$$\\mu = 1 + R + R^2 + R^3 + \\dots = \\frac{{1}}{{1-R}}, \\qquad R < 1$$
<p>With $R$ at 0.5 the chain comes to two cases on average, and with $R$ at 0.8 it comes to five. Chance also works in the response&rsquo;s favour, since even with $R$ at 2 and no response at all, about one introduction in five dies out by itself when the first patient happens to infect no one. Lloyd-Smith and colleagues showed that real outbreaks are even more uneven than these averages suggest, as most patients infect nobody while a few infect many; this pattern, called superspreading, makes a new introduction more likely to die out and makes the outbreaks that do take off grow faster [@lloydsmith2005].</p>
{code_block(*CODE_CHAINS)}
<p>The cluster in Nairobi followed this pattern closely: one man infected up to eight people, far more than the average of two, and those eight infected nobody, since all of them were already in quarantine when they became able to pass the virus on, so the chain ended at nine.</p>
<p>Isolating patients works far better against Ebola than against influenza, and Fraser and colleagues showed that the reason lies in how much transmission happens before a person feels ill [@fraser2004]. For Ebola that share is close to zero, so if health workers find and isolate a fraction $c$ of cases soon after their symptoms begin, the reproduction number that remains is roughly</p>
$$R_{{\\text{{eff}}}} = R_0\\,(1 - c)$$
<p>With $R_0$ at 2, the outbreak therefore shrinks once health workers promptly isolate more than half of all cases and the dead are buried safely. Influenza spreads before people know they are ill, so isolating the sick cannot do the same job against it, and Fraser and colleagues found that SARS and smallpox could be controlled in this way while pandemic influenza and HIV could not [@fraser2004].{{{{margin: Fraser and colleagues write the share of transmission that happens before symptoms as &theta;. The formula above is their result with &theta; set to zero.}}}}</p>
<p>A vaccine adds a second line of defence by protecting people before they are exposed to the virus. In Guinea in 2015, the <i>Ebola &ccedil;a Suffit</i> trial, reported by Henao-Restrepo and colleagues, vaccinated the contacts of each new case, and the contacts of those contacts, either at once or after a three-week delay; among the people vaccinated at once, nobody developed Ebola from ten days after their ring was enrolled, while the rings vaccinated after the delay had 16 cases [@henao2017]. That vaccine was developed against Zaire virus, and no equivalent exists yet for Bundibugyo virus, which leaves the response teams in Ituri and North Kivu to rely on isolation, contact tracing and safe burial.</p>
{DRAFT_L}
'''),
('numbers', 'What the 2026 numbers say', f'''
<p>Three groups have published estimates of the reproduction number for this outbreak, and together they suggest that it started at around 2 or a little higher and fell to around 1 within a few months; Table 1 sets them side by side.</p>
<figure class="tbl" id="tbl-1"><figcaption><b>Table 1:</b> Published estimates of the reproduction number for the 2026 Bundibugyo outbreak. None covers October or November.</figcaption>
<table><thead><tr><th>Study</th><th>Method</th><th>Period</th><th class="n">Estimate</th><th>Peer reviewed</th></tr></thead><tbody>
<tr><td>CDC modelling team [@mooring2026]</td><td>Scenario model</td><td>Start of outbreak</td><td class="n">about 2.5</td><td>Yes</td></tr>
<tr><td>Preprint [@verheyden2026]</td><td>Confirmed case counts, national</td><td>Mid-August</td><td class="n">1.01</td><td>No, preprint</td></tr>
<tr><td></td><td></td><td>26 August</td><td class="n">0.94</td><td></td></tr>
<tr><td>Genome analysis, Ituri [@virological2026]</td><td>Virus family tree</td><td>Mid-May to mid-June</td><td class="n">1.27</td><td>No, forum post</td></tr>
<tr><td></td><td></td><td>Mid-June to late September</td><td class="n">0.86</td><td></td></tr>
</tbody></table></figure>
<p>The last two have not yet been peer reviewed, meaning that other scientists have not yet formally checked their methods, and none of the three covers October or November, so what follows is our own rough reading of the more recent case counts, which readers should treat as a sketch. Figure 2 shows how the confirmed cases and deaths reported by WHO and ECDC have added up since May.</p>
<figure class="fig" id="fig-2">{fig_cumulative()}<figcaption id="fig-cum-cap"><b>Figure 2:</b> Confirmed cases in DR Congo passed 11,000 in November, and about half of patients have died. Cumulative <span class="k" style="--c:{B}">confirmed cases</span> and <span class="k" style="--c:#4a5260">deaths</span> as reported by WHO and ECDC; markers are reports and lines join them. Data: <a href="./data/drc_2026_reports.csv">drc_2026_reports.csv</a>.</figcaption></figure>
<p>DR Congo had 4,665 confirmed cases on 12 August and 9,277 on 14 October, an average of about 73 new confirmed cases a day over those nine weeks, and between 14 October and {LAST['day'].strftime('%-d %B')} the count rose to {fmt(LAST['confirmed'])}, an average of about 66 a day [@ecdc2026; @who2026b]. Nine weeks covers roughly four generations of Ebola, so if $R$ had still been near 2, the daily figure would have doubled four times in that stretch and passed 1,000 by mid-October; Figure 3 shows that it stayed at about the same level the whole time instead, between {lo} and {hi} new confirmed cases a day since July.</p>
<figure class="fig" id="fig-3">{fig_daily()}<figcaption id="fig-daily-cap"><b>Figure 3:</b> New confirmed cases have held level since July, with a small fall in November. Each bar spans the days between two reports, and its height is the new confirmed cases in that span divided by its days; the latest span is shown in full colour. Same data as Figure 2.</figcaption></figure>
{code_block(dcode, dout, 'Code: new cases per day between reports')}
<p>A daily count that holds level for months is what an $R_t$ close to 1 looks like, meaning that each case is replacing itself, so the outbreak is neither growing nor ending while about 60 to 70 more people test positive every day. WHO&rsquo;s description in late October supports this reading, since it reported transmission continuing at a high level, with new cases in 50 of the 66 affected health zones over the previous three weeks and only about 80 percent of known contacts being followed up, against a target of 95 percent [@who2026a].{{{{margin: A <b>health zone</b> is the basic unit of DR Congo&rsquo;s health system, a district served by one general hospital and its clinics.}}}}</p>
<details class="callout"><summary>Three limits on the data, and why they call for caution</summary>
<p>The figures count confirmed cases only, so the daily number can be capped by how many samples laboratories are able to test, and a flat line in Figure 3 might partly reflect a limit on testing as well as a steady outbreak. Reports also arrive late and are often revised. Finally, we have borrowed the 15-day generation time from Zaire virus in West Africa, since we have not found a published measure of it for Bundibugyo virus, and a shorter or longer generation time would change how many generations fit into nine weeks.</p></details>
<p>The death rate calls for the same care. On the reported figures, {fmt(LAST['deaths'])} of {fmt(LAST['confirmed'])} confirmed patients have died, or {cfr} percent [@ecdc2026],[^ Epidemiologists call this share the case fatality ratio: deaths divided by confirmed cases. ] against between 25 and 32 percent in Uganda in 2007, depending on whose count is used, and 55 percent around Isiro in 2012 [@cdc2026; @who2025], so this outbreak sits near the top of a very short record. A ratio taken in the middle of an outbreak can be wrong in both directions, however, since some recent patients have not yet recovered or died, and many people with mild illness are never tested.</p>
'''),
('beyond', 'Beyond Africa', f'''
<p>Ebola has already left Africa this year: ECDC counts four cases linked to the outbreak in the European Union, made up of two patients flown to Germany and one to the Netherlands for specialist care, and a humanitarian doctor who fell ill after returning to France in July [@ecdc2026]. All four had been working in health care or aid in the affected areas, and the patient in Nigeria was later flown to Switzerland, where the patient was discharged on 11 November, the same day that all 62 of the patient&rsquo;s contacts in Nigeria finished their monitoring [@ecdc2026].</p>
<p>This year&rsquo;s cases are in line with history, as van Zandvoort and colleagues found in June when they reviewed every known case of Ebola outside Africa since 1976: they counted 28 confirmed cases linked to African outbreaks, most of them health and aid workers flown home on purpose for treatment, and only four travellers who crossed a border feeling well and fell ill afterwards [@vanzandvoort2026]. Leaving out the planned evacuations, they put the rate since 2000 at about 0.17 cases outside Africa for every 1,000 cases reported in Africa, which, applied to this outbreak as a rough guide, gives</p>
$$\\frac{{0.17}}{{1000}} \\times {NTEX} \\approx {0.17/1000*LAST['confirmed']:.1f}$$
<p>On past form, then, we would expect about two unplanned arrivals on another continent by now, with roughly a one in seven chance of none, and there has been one, the humanitarian doctor who fell ill after returning to France.</p>
<p>Arriving is only the first step, since for Ebola to take hold somewhere new, the person who arrives has to infect others, and those people have to keep infecting others faster than health workers can find them; van Zandvoort and colleagues found that this has never happened outside Africa in fifty years of records [@vanzandvoort2026].</p>
<p>The closest it has come was in Dallas, in the United States, in 2014, where, as Chevalier and colleagues describe, a man who had flown in from Liberia went to a hospital emergency department with a fever on 25 September and was sent home, came back by ambulance, was confirmed to have Ebola on 30 September and died on 8 October; two nurses who cared for him were infected and both recovered, and all 177 people traced as contacts of the three patients finished their 21 days of monitoring without another case [@chevalier2014]. In the same year, a nursing assistant in Madrid caught the virus from a patient evacuated from Sierra Leone, the first time Ebola was known to have passed from one person to another outside Africa, and WHO reports that it went no further [@who2014].</p>
<p>Nairobi now belongs on the same list, and it stands out once health budgets are compared: World Bank figures show that in 2022 Kenya spent about 91 US dollars on health for each person, against about 2,950 dollars in Spain and about 12,600 dollars in the United States, so Kenya held its chain to nine cases while spending less than a thirtieth of what Spain spent per person and less than a hundredth of what the United States spent [@worldbank]. In all three cities, the first patient infected people who lived with or cared for that patient, and once health workers recognised the case, they cut the chain within one generation.</p>
{code_block(*CODE_EXPORTS)}
<p>Travel bans target the first step, arrival, and the evidence that they help is thin: Poletto and colleagues modelled the 2014 epidemic and found that even deep cuts in flights from the affected countries delayed the virus&rsquo;s arrival in new countries by a few weeks at most [@poletto2014]. Similarly, Bogoch and colleagues estimated that, without screening at departure, about 2.8 infected travellers a month would have boarded international flights from Guinea, Liberia and Sierra Leone, and they concluded that screening passengers as they leave, together with controlling the epidemic at its source, protects other countries far better than screening passengers when they arrive [@bogoch2015].</p>
<p>WHO&rsquo;s advice this year follows the same evidence, as its updates in August and October rated the risk as very high inside DR Congo, high for the countries that share a land border with it and low for the rest of the world, and it advises countries against restricting travel or trade [@who2026a; @who2026b]. ECDC, for its part, rates the likelihood of infection for people living in Europe as very low [@ecdc2026].</p>
'''),
('risk', 'The risk people feel', '''
<p>Saudi Arabia closed its borders to travellers from Kenya over nine cases in a cluster that was already contained, and that decision shows how far the risk people feel can drift from the risk that case counts measure.</p>
<p>Researchers have measured that gap using Google Trends, a free tool that scores a search term from 0 to 100 according to its share of all searches made in a given place and period; according to Google, the score shows how much attention a topic received and says nothing about how many people searched or how worried they were [@google]. Using this tool, Alicino and colleagues found that worldwide searches for &ldquo;Ebola&rdquo; in October 2014 were about 76 times higher than in March 2014, and that the single highest day, 16 October, came as President Obama called on National Guard reserves to help contain the virus [@alicino2015]. Interest was highest in Liberia and Sierra Leone, where people were dying, while in the United States, Spain, the United Kingdom and Italy it was far lower and followed news coverage more closely than case counts. Towers and colleagues found the same pattern within the United States, where each Ebola news video was followed by tens of thousands of searches and tweets, although only a handful of people in the country were ever infected [@towers2015].</p>
<p>We have not yet repeated this analysis for 2026; we plan to compare searches in Kenya, Uganda and DR Congo with searches in the United States, the United Kingdom and France, and we will add the results to this article and to the <a href="./dashboard.html">dashboard</a>.</p>
'''),
('closing', 'Who carries the risk', '''
<p>Ebola will keep reaching other continents now and then, on a medical flight or with a returning aid worker, and fifty years of records show that a prepared hospital can stop it there; Nairobi has now shown that a hospital in Africa, working with far less money, can do the same.</p>
<p>The people who cannot count on that protection live in Ituri and North Kivu, where about 60 new cases are still being confirmed every day, about half of all confirmed patients have died, and the vaccines that might break the chain are only now entering trials. If $R_t$ there is close to 1, as both the published estimates and the case counts suggest, the outbreak is balanced on what the response teams can manage from week to week, and a gap in funding or a new round of fighting could be enough to push it back into growth.</p>
<p>Everyone else&rsquo;s safety is decided in Ituri and North Kivu as well, since a visa ban on travellers from Kenya does nothing to lower the daily count in Bunia, whereas money for tracing teams, isolation beds, safe burials and the vaccine trial does, and that spending protects people in Nairobi or Riyadh in the same way that it protects people in Bunia.</p>
<p>We will keep the <a href="./">storyboard</a> and the <a href="./dashboard.html">dashboard</a> updated as WHO and ECDC publish new figures.</p>
'''),
]

# ---------------------------------------------------------------- markup processing
def render_math(items):
    """Render [(tex, display), ...] with KaTeX through Node; returns a list of HTML strings."""
    kp = os.environ.get('KATEX_PATH', '/tmp/katex')
    js = ("const k=require(process.argv[1]);let s='';process.stdin.on('data',d=>s+=d).on('end',()=>{"
          "const a=JSON.parse(s);process.stdout.write(JSON.stringify(a.map(([t,d])=>k.renderToString(t,{displayMode:d,throwOnError:true,output:'html'}))))});")
    res = subprocess.run(['node', '-e', js, kp], input=json.dumps(items), capture_output=True, text=True, check=True)
    return json.loads(res.stdout)

USED = []      # citation keys in order of first use
NOTES = []     # numbered notes

def cite(m):
    keys = [k.strip().lstrip('@') for k in m.group(1).split(';')]
    parts = []
    for k in keys:
        if k not in REFS: raise SystemExit(f'unknown citation key {k}')
        if k not in USED: USED.append(k)
        parts.append(f'<a class="cite" href="#ref-{k}" data-ref="{k}">{REFS[k][0]}</a>')
    return '(' + '; '.join(parts) + ')'

def note(m):
    NOTES.append(m.group(1).strip()); n = len(NOTES)
    return (f'<sup class="fn-ref"><a href="#fn-{n}" id="fnref-{n}" aria-label="Note {n}">{n}</a></sup>'
            f'<span class="sidenote" aria-hidden="true"><sup>{n}</sup> {m.group(1).strip()}</span>')

def margin(m):
    return f'<span class="marginnote">{m.group(1).strip()}</span>'

def process(text):
    # protect code blocks from markup processing
    keep = []
    def stash(m): keep.append(m.group(0)); return f'\x00{len(keep)-1}\x00'
    text = re.sub(r'<details class="code">.*?</pre>\s*<pre class="out">.*?</pre>', stash, text, flags=re.S)
    text = re.sub(r'\[\^(.+?)\]', note, text, flags=re.S)
    text = re.sub(r'\{\{margin:(.+?)\}\}', margin, text, flags=re.S)
    text = re.sub(r'\[(@[^\]]+)\]', cite, text)
    return text, keep

def build():
    body_parts, all_keep = [], []
    for sid, title, text in SECTIONS:
        t, keep = process(text)
        off = len(all_keep); all_keep += keep
        t = re.sub(r'\x00(\d+)\x00', lambda m: f'\x00{int(m.group(1))+off}\x00', t)
        body_parts.append(f'<section id="{sid}"><h2>{title}</h2>{t}</section>')
    body = '\n'.join(body_parts)
    # maths: display first, then inline (inside notes too)
    found = []
    def grab(disp):
        def f(m): found.append((html.unescape(m.group(1)), disp)); return f'\x01{len(found)-1}\x01'
        return f
    body = re.sub(r'\$\$(.+?)\$\$', grab(True), body, flags=re.S)
    body = re.sub(r'(?<![\w$])\$([^$\n]+?)\$', grab(False), body)
    notes_html = '\n'.join(f'<li id="fn-{i+1}">{n} <a href="#fnref-{i+1}" class="back" aria-label="Back to the text">&#8617;</a></li>' for i, n in enumerate(NOTES))
    notes_html = re.sub(r'(?<![\w$])\$([^$\n]+?)\$', grab(False), notes_html)
    rendered = render_math(found)
    def put(m):
        i = int(m.group(1)); h = rendered[i]
        return f'<div class="math-display">{h}</div>' if found[i][1] else h
    body = re.sub(r'\x01(\d+)\x01', put, body); notes_html = re.sub(r'\x01(\d+)\x01', put, notes_html)
    body = re.sub(r'\x00(\d+)\x00', lambda m: all_keep[int(m.group(1))], body)
    refs = sorted(USED, key=lambda k: re.sub(r'&[a-z]+;', '', REFS[k][1]).lower())
    refs_html = '\n'.join(f'<li id="ref-{k}">{REFS[k][1]} <a href="{REFS[k][2]}">{html.escape(REFS[k][2])}</a></li>' for k in refs)
    toc = '\n'.join(f'<li><a href="#{sid}">{title}</a></li>' for sid, title, _ in SECTIONS)
    toc += '\n<li class="notes-link"><a href="#notes">Notes</a></li><li><a href="#references">References</a></li><li><a href="#citation">Citation</a></li>'
    bib = f'''@article{{ngugi2026ebola,
  author = {{Ngugi, Stephane and Mugure, Lianne}},
  title  = {{{TITLE}}},
  date   = {{2026-11-18}},
  url    = {{{SITE}/article.html}},
  langid = {{en}}
}}'''
    page = TEMPLATE.format(TITLE=html.escape(TITLE), SUBTITLE=SUBTITLE, PUBLISHED=PUBLISHED, TOC=toc, BODY=body,
                           NOTES=notes_html, REFS=refs_html, BIB=html.escape(bib), SITE=SITE, GITHUB=GITHUB,
                           REPO=REPO, LINKEDIN=LINKEDIN, HEADER=header('article'), FOOTER=footer())
    out = os.path.join(ROOT, 'docs/article.html')
    with open(out, 'w', encoding='utf-8') as f: f.write(page)
    print('wrote', out, f'({len(page)//1024} KB, {len(USED)} references, {len(NOTES)} notes, {len(found)} formulas)')

# ---------------------------------------------------------------- shared header and footer (also used by the dashboard build)
ICON_GH = '<svg viewBox="0 0 16 16" width="18" height="18" aria-hidden="true" fill="currentColor"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>'
ICON_IN = '<svg viewBox="0 0 16 16" width="18" height="18" aria-hidden="true" fill="currentColor"><path d="M0 1.15C0 .52.52 0 1.18 0h13.64C15.48 0 16 .52 16 1.15v13.7c0 .63-.52 1.15-1.18 1.15H1.18C.52 16 0 15.48 0 14.85V1.15zm4.94 12.24V6.17H2.54v7.22h2.4zm-1.2-8.2c.84 0 1.36-.56 1.36-1.25-.02-.71-.52-1.25-1.34-1.25-.82 0-1.36.54-1.36 1.25 0 .69.52 1.25 1.33 1.25h.01zm4.91 8.2V9.36c0-.22.02-.43.08-.59.17-.43.57-.88 1.23-.88.87 0 1.22.66 1.22 1.63v3.86h2.4V9.25c0-2.22-1.18-3.25-2.76-3.25-1.27 0-1.84.7-2.16 1.19v.03h-.02l.02-.03V6.17h-2.4c.03.68 0 7.22 0 7.22h2.4z"/></svg>'

def header(active):
    links = [('storyboard', './', 'Storyboard'), ('dashboard', './dashboard.html', 'Dashboard'),
             ('article', './article.html', 'Article'), ('code', REPO, 'Code')]
    nav = ''.join(f'<a href="{h}"{" aria-current=\"page\"" if k == active else ""}>{t}</a>' for k, h, t in links)
    return (f'<header class="site"><div class="site-in"><a class="brand" href="./">Ebola in Africa</a>'
            f'<span class="social"><a href="{GITHUB}" aria-label="Stephane Ngugi on GitHub">{ICON_GH}</a>'
            f'<a href="{LINKEDIN}" aria-label="Stephane Ngugi on LinkedIn">{ICON_IN}</a></span>'
            f'<nav aria-label="Site">{nav}</nav></div></header>')

def footer():
    return (f'<footer class="site"><div class="site-in"><span>Built by Stephane Ngugi</span>'
            f'<span class="social"><a href="{GITHUB}" aria-label="GitHub">{ICON_GH}</a><a href="{LINKEDIN}" aria-label="LinkedIn">{ICON_IN}</a></span>'
            f'<nav aria-label="Site, again"><a href="./">Storyboard</a><a href="./dashboard.html">Dashboard</a><a href="./article.html">Article</a><a href="{REPO}">Code and data</a></nav></div></footer>')

HEADER_CSS = '''
@font-face{font-family:"Source Sans 3";src:url(./fonts/source-sans-3-latin-400-normal.woff2) format("woff2");font-weight:400;font-display:swap}
@font-face{font-family:"Source Sans 3";src:url(./fonts/source-sans-3-latin-600-normal.woff2) format("woff2");font-weight:600;font-display:swap}
@font-face{font-family:"Source Sans 3";src:url(./fonts/source-sans-3-latin-700-normal.woff2) format("woff2");font-weight:700;font-display:swap}
header.site,footer.site{background:#17212e;color:#e8ecf1;font-family:"Source Sans 3","Source Sans Pro",system-ui,sans-serif}
.site-in{max-width:1440px;margin:0 auto;padding:0 28px;display:flex;align-items:center;gap:22px;min-height:60px;flex-wrap:wrap}
header.site .brand{color:#fff;font-size:21px;font-weight:600;text-decoration:none;letter-spacing:.01em}
.site .social{display:flex;gap:14px}.site .social a{color:#c9d2dd;display:inline-flex}.site .social a:hover{color:#fff}
.site nav{margin-left:auto;display:flex;gap:24px;flex-wrap:wrap}
.site nav a{color:#e8ecf1;text-decoration:none;text-transform:uppercase;font-weight:600;font-size:15px;letter-spacing:.06em;padding:4px 0;border-bottom:2px solid transparent}
.site nav a:hover{border-bottom-color:#c9d2dd}.site nav a[aria-current=page]{border-bottom-color:#e8b04b}
footer.site{margin-top:64px;font-size:15px}footer.site .site-in{min-height:72px}
@media (max-width:640px){.site-in{padding:10px 16px;gap:10px 16px}.site nav{margin-left:0;gap:16px;width:100%}.site nav a{font-size:13px}}
'''

TEMPLATE = '''<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TITLE}</title>
<meta name="description" content="{SUBTITLE}.">
<meta name="author" content="Stephane Ngugi and Lianne Mugure">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{SUBTITLE}.">
<meta property="og:type" content="article">
<link rel="stylesheet" href="./vendor/katex/katex.min.css">
<style>
@font-face{{font-family:"Source Serif 4";src:url(./fonts/source-serif-4-latin-400-normal.woff2) format("woff2");font-weight:400;font-display:swap}}
@font-face{{font-family:"Source Serif 4";src:url(./fonts/source-serif-4-latin-400-italic.woff2) format("woff2");font-weight:400;font-style:italic;font-display:swap}}
@font-face{{font-family:"Source Serif 4";src:url(./fonts/source-serif-4-latin-600-normal.woff2) format("woff2");font-weight:600;font-display:swap}}
@font-face{{font-family:"Source Serif 4";src:url(./fonts/source-serif-4-latin-600-italic.woff2) format("woff2");font-weight:600;font-style:italic;font-display:swap}}
@font-face{{font-family:"Source Serif 4";src:url(./fonts/source-serif-4-latin-700-normal.woff2) format("woff2");font-weight:700;font-display:swap}}
''' + HEADER_CSS.replace('{', '{{').replace('}', '}}') + '''
:root{{--ink:#1d2330;--muted:#5b6472;--rule:#e1e4e8;--link:#1f5fbf;--hover:#2e7d32;--accent:#7a2e3a;--serif:"Source Serif 4",Charter,Georgia,serif;--sans:"Source Sans 3","Source Sans Pro",system-ui,sans-serif}}
*{{box-sizing:border-box}}
html{{scroll-behavior:smooth}}@media (prefers-reduced-motion:reduce){{html{{scroll-behavior:auto}}}}
body{{margin:0;background:#fff;color:var(--ink);font-family:var(--serif);font-size:19px;line-height:1.62;-webkit-font-smoothing:antialiased}}
a{{color:var(--link);text-decoration:none}}a:hover{{color:var(--hover);text-decoration:underline}}
.title-block{{max-width:1100px;margin:0 auto;padding:46px 28px 8px;text-align:center}}
.title-block h1{{font-family:var(--sans);font-weight:700;font-size:clamp(30px,4.4vw,46px);line-height:1.12;color:var(--accent);margin:0 0 14px}}
.title-block .subtitle{{font-family:var(--sans);font-size:19px;line-height:1.45;color:var(--ink);margin:0 auto 18px;max-width:820px}}
.tags{{display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin:0 0 6px}}
.tags span{{font-family:var(--sans);font-size:13px;letter-spacing:.06em;text-transform:uppercase;color:var(--accent);border:1px solid var(--accent);padding:3px 10px;border-radius:2px}}
.meta{{max-width:1100px;margin:34px auto 8px;padding:0 28px;display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:22px 40px;font-family:var(--sans)}}
.meta h3{{font-size:13px;letter-spacing:.08em;text-transform:uppercase;font-weight:600;color:var(--muted);margin:0 0 4px}}
.meta p{{margin:0;font-size:18px;line-height:1.4}}.meta .role{{display:block;font-size:15px;color:var(--muted)}}
.meta .social a{{color:var(--muted);margin-right:8px;display:inline-flex;vertical-align:-3px}}.meta .social a:hover{{color:var(--ink)}}
.backlinks{{max-width:1100px;margin:22px auto 0;padding:14px 28px 0;border-top:1px solid var(--rule);font-family:var(--sans);font-size:16px;display:flex;gap:22px;flex-wrap:wrap}}
.layout{{max-width:1440px;margin:0 auto;padding:30px 28px 0;display:grid;grid-template-columns:210px minmax(0,740px) 1fr;gap:0 48px}}
.toc{{position:sticky;top:20px;align-self:start;font-family:var(--sans);font-size:16px;line-height:1.35;max-height:calc(100vh - 40px);overflow:auto}}
.toc h2{{font-size:15px;font-weight:600;color:var(--accent);margin:0 0 10px;letter-spacing:.02em}}
.toc ol{{list-style:none;margin:0;padding:0 0 0 14px;border-left:1px solid var(--rule)}}
.toc li{{margin:0 0 9px}}.toc a{{color:var(--ink)}}.toc a:hover{{color:var(--link);text-decoration:none}}
.toc a.on{{color:var(--accent);box-shadow:-15px 0 0 -13px var(--accent)}}
main{{min-width:0}}
main h2{{font-family:var(--sans);font-weight:600;font-size:30px;line-height:1.2;color:var(--accent);margin:46px 0 16px;padding-bottom:8px;border-bottom:1px solid var(--rule)}}
main section:first-child h2{{margin-top:0}}
main p{{margin:0 0 20px}}
.cite{{color:var(--link)}}.cite:hover,.cite:focus{{color:var(--hover);text-decoration:none}}
.refcard{{position:absolute;z-index:20;max-width:520px;background:#fff;border:1px solid #d5d9df;box-shadow:0 6px 24px rgba(20,30,45,.14);padding:12px 16px;font-size:16px;line-height:1.45;font-family:var(--serif);text-indent:-1.4em;padding-left:calc(16px + 1.4em)}}
.fn-ref a{{font-family:var(--sans);font-size:.72em;font-weight:600;padding:0 1px}}
.sidenote,.marginnote{{float:right;clear:right;width:250px;margin:4px -298px 14px 0;font-family:var(--sans);font-size:15px;line-height:1.45;color:var(--muted)}}
.sidenote sup{{font-weight:600;color:var(--ink)}}.marginnote b,.sidenote b{{color:var(--ink);font-weight:600}}
.math-display{{overflow-x:auto;overflow-y:hidden;margin:-4px 0 20px;padding:4px 0}}
.katex{{font-size:1.06em}}
figure{{margin:30px 0 30px}}figure svg{{display:block;width:100%;height:auto}}
figcaption{{font-family:var(--sans);font-size:16px;line-height:1.45;color:var(--muted);margin-top:10px}}
figcaption b{{color:var(--ink)}}
.k{{white-space:nowrap;color:var(--ink)}}.k::before{{content:"";display:inline-block;width:11px;height:11px;margin-right:5px;background:var(--c);vertical-align:-1px}}
figure.tbl figcaption{{text-align:center;color:var(--ink);font-family:var(--serif);font-size:18px;margin:0 0 10px}}
table{{width:100%;border-collapse:collapse;font-family:var(--sans);font-size:16px;line-height:1.4}}
th{{text-align:left;font-weight:600;border-bottom:2px solid var(--ink);padding:8px 10px}}
td{{border-bottom:1px solid var(--rule);padding:8px 10px;vertical-align:top}}tbody tr:nth-child(odd){{background:#f6f7f8}}
.n{{text-align:right;font-variant-numeric:tabular-nums}}
.tbl{{overflow-x:auto}}
details.callout{{border-left:5px solid #4a7fd1;background:#fff;margin:28px 0;border-radius:3px;box-shadow:0 0 0 1px #dfe6f1 inset}}
details.callout>summary{{cursor:pointer;list-style:none;background:#eef3fb;padding:11px 16px 11px 44px;font-family:var(--sans);font-size:18px;font-weight:600;position:relative}}
details.callout>summary::-webkit-details-marker{{display:none}}
details.callout>summary::before{{content:"i";position:absolute;left:14px;top:12px;width:19px;height:19px;border:1.5px solid #4a7fd1;border-radius:50%;color:#4a7fd1;font-size:13px;line-height:16px;text-align:center;font-weight:700;font-family:var(--serif)}}
details.callout>summary::after{{content:"";position:absolute;right:18px;top:18px;width:8px;height:8px;border-right:2px solid var(--muted);border-bottom:2px solid var(--muted);transform:rotate(-45deg);transition:transform .15s}}
details.callout[open]>summary::after{{transform:rotate(45deg)}}
details.callout>p{{margin:14px 18px 16px}}
details.code{{margin:6px 0 0}}
details.code>summary{{cursor:pointer;font-family:var(--sans);font-size:17px;color:var(--muted);padding:4px 0}}
pre{{margin:0;overflow-x:auto;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:14.5px;line-height:1.55}}
pre.r{{background:#f1f3f5;border-left:4px solid #5aa9e6;border-radius:3px;padding:14px 18px;margin:6px 0 0}}
pre.out{{padding:12px 18px;margin:0 0 26px;color:#1d2330;border-left:4px solid transparent}}
pre .co{{color:#8f5902;font-style:italic}}pre .st{{color:#2c7a2c}}pre .dv{{color:#1750eb}}pre .fu{{color:#204a87;font-weight:600}}pre .op{{color:#b5530d}}
.draft{{background:#fff6d6;border:1px solid #ecd27a;padding:12px 16px;margin:0 0 20px;font-family:var(--sans);font-size:16px;line-height:1.45}}
.endmatter{{max-width:740px}}
.endmatter h2{{font-size:24px}}
.endmatter ol{{padding-left:22px;font-size:16px;line-height:1.5;font-family:var(--sans)}}
.endmatter li{{margin-bottom:8px}}
.endmatter .back{{margin-left:4px}}
ol.refs{{list-style:none;padding:0;font-family:var(--serif);font-size:17px}}
ol.refs li{{padding-left:1.6em;text-indent:-1.6em;margin-bottom:10px}}
ol.refs a{{word-break:break-all}}
.citebox pre{{background:#f1f3f5;padding:14px 18px;border-radius:3px;white-space:pre-wrap}}
.citebox p{{font-size:17px}}
@media (max-width:1359px){{.layout{{grid-template-columns:210px minmax(0,1fr);gap:0 40px}}.sidenote,.marginnote{{display:none}}}}
@media (min-width:1360px){{#notes{{display:none}}.toc li.notes-link{{display:none}}}}
@media (max-width:900px){{.layout{{display:block;padding:20px 18px 0}}.toc{{position:static;max-height:none;margin:0 0 26px;border:1px solid var(--rule);padding:14px 16px}}
  body{{font-size:18px}}.title-block{{padding:30px 18px 4px}}.meta,.backlinks{{padding-left:18px;padding-right:18px}}main h2{{font-size:26px}}}}
@media print{{header.site,footer.site,.toc,.backlinks{{display:none}}.layout{{display:block}}details.callout,details.code{{display:block}}}}
</style>
</head>
<body>
{HEADER}
<div class="title-block">
  <h1>{TITLE}</h1>
  <p class="subtitle">{SUBTITLE}.</p>
  <div class="tags"><span>Epidemiology</span><span>Outbreak data</span><span>East Africa</span></div>
</div>
<div class="meta">
  <div><h3>Authors</h3>
    <p>Stephane Ngugi <span class="social"><a href="{GITHUB}" aria-label="GitHub">''' + ICON_GH.replace('{', '{{').replace('}', '}}') + '''</a><a href="{LINKEDIN}" aria-label="LinkedIn">''' + ICON_IN.replace('{', '{{').replace('}', '}}') + '''</a></span><span class="role">Senior Data Analyst &amp; Researcher</span></p>
    <p style="margin-top:12px">Lianne Mugure<span class="role">Epidemiologist and Researcher, <a href="https://www.afidep.org/">AFIDEP</a></span></p></div>
  <div><h3>Published</h3><p>{PUBLISHED}</p><h3 style="margin-top:16px">Data to</h3><p>15 November 2026 (ECDC)</p></div>
  <div><h3>Keywords</h3><p style="font-size:16px">Ebola, Bundibugyo virus, DR Congo, Kenya, reproduction number, outbreak analytics, travel restrictions</p></div>
</div>
<div class="backlinks"><a href="./">&larr; Back to the storyboard</a><a href="./dashboard.html">Open the dashboard</a><a href="{REPO}">Code and data on GitHub</a></div>
<div class="layout">
  <nav class="toc" aria-label="Contents"><h2>Contents</h2><ol>{TOC}</ol></nav>
  <main id="top">
{BODY}
  <div class="endmatter">
    <section id="notes"><h2>Notes</h2><ol>{NOTES}</ol></section>
    <section id="references"><h2>References</h2><ol class="refs">{REFS}</ol></section>
    <section id="citation" class="citebox"><h2>Reuse and citation</h2>
      <p><b>Reuse.</b> Text and figures are licensed under <a href="https://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution CC BY 4.0</a>; please credit the authors when you reuse them. Figures drawn from WHO, ECDC and CDC data remain subject to those sources&rsquo; own terms.</p>
      <p><b>Citation.</b> For attribution, please cite this work as:</p>
      <p>Ngugi, Stephane, and Lianne Mugure. 2026. &ldquo;{TITLE}&rdquo; 18 November 2026. <a href="{SITE}/article.html">{SITE}/article.html</a>.</p>
      <p>BibTeX citation:</p><pre><code>{BIB}</code></pre>
      <p>Code and data: <a href="{REPO}">{REPO}</a>. Contact: <a href="{GITHUB}">GitHub</a> &middot; <a href="{LINKEDIN}">LinkedIn</a>.</p>
    </section>
    <p class="backlinks" style="margin:30px 0 0;padding:16px 0 0"><a href="./">&larr; Back to the storyboard</a><a href="./dashboard.html">Open the dashboard</a><a href="#top">Back to the top</a></p>
  </div>
  </main>
</div>
{FOOTER}
<script>
// citation hover cards: the reference text appears beside the citation
(() => {{
  let card = null;
  const close = () => {{ if (card) {{ card.remove(); card = null; }} }};
  const open = (a) => {{
    close(); const li = document.getElementById('ref-' + a.dataset.ref); if (!li) return;
    card = document.createElement('div'); card.className = 'refcard'; card.setAttribute('role', 'tooltip'); card.innerHTML = li.innerHTML;
    document.body.appendChild(card);
    const r = a.getBoundingClientRect(), w = Math.min(520, innerWidth - 24);
    card.style.maxWidth = w + 'px';
    card.style.left = Math.max(12, Math.min(scrollX + r.left, scrollX + innerWidth - w - 12)) + 'px';
    card.style.top = (scrollY + r.bottom + 8) + 'px';
  }};
  document.querySelectorAll('a.cite').forEach((a) => {{
    a.addEventListener('mouseenter', () => open(a)); a.addEventListener('focus', () => open(a));
    a.addEventListener('mouseleave', () => setTimeout(() => {{ if (card && !card.matches(':hover')) close(); }}, 120));
    a.addEventListener('blur', close);
  }});
  document.addEventListener('mouseover', (e) => {{ if (card && !e.target.closest('.refcard') && !e.target.closest('a.cite')) close(); }});
  document.addEventListener('keydown', (e) => {{ if (e.key === 'Escape') close(); }});
}})();
// table of contents: mark the section being read
(() => {{
  const links = [...document.querySelectorAll('.toc a')], map = new Map(links.map((a) => [a.getAttribute('href').slice(1), a]));
  const obs = new IntersectionObserver((es) => es.forEach((e) => {{ if (e.isIntersecting) {{ links.forEach((a) => a.classList.remove('on')); const a = map.get(e.target.id); if (a) a.classList.add('on'); }} }}), {{ rootMargin: '-15% 0px -75% 0px' }});
  document.querySelectorAll('main section[id]').forEach((s) => obs.observe(s));
}})();
</script>
</body>
</html>
'''

if __name__ == '__main__':
    build()
