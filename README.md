# Tracking Ebola Across Sub-Saharan Africa

Twelve years of Ebola outbreaks, told place by place, from Sierra Leone in 2014 to Nairobi in 2026. The project has three parts:

- **The story** (`docs/index.html`): a scroll story over real satellite imagery. A 3D map stays on screen while short chapters scroll past; the camera flies to each country, outlines its border, then moves in to the affected province or district. Spikes rise with confirmed cases and turn grey when an outbreak is declared over. It ends by pulling back over the whole continent on NASA Blue Marble, with a dotted line joining each outbreak in the order it began, then fades to NASA Black Marble at night.
- **The dashboard** (`docs/dashboard.html`): filter every outbreak since 2014 by period, country, virus and status, with the 2026 growth curve, a dot map of Africa and a searchable table.
- **The film** (`docs/film.html`, and `media/ebola-across-africa.mp4` for slides and social media).

Live at **https://kinjuriu.github.io/TrackingEbolaAcrossSSA/** once GitHub Pages is turned on (Settings → Pages → Deploy from a branch → `main` / `docs`).

## What the story shows

| Chapter | Place | Virus | Confirmed cases | Deaths | Status |
|---|---|---|---|---|---|
| 2014–2016 | Sierra Leone (national total) | Zaire ebolavirus | 14,124 | 3,956 | Over, 17 March 2016 |
| 2014–2016 | Liberia (national total) | Zaire ebolavirus | 10,678 | 4,810 | Over, 9 June 2016 |
| 2014–2016 | Guinea (national total, began in Guéckédou) | Zaire ebolavirus | 3,814 | 2,544 | Over, 1 June 2016 |
| 2018–2020 | North Kivu & Ituri provinces, DR Congo | Zaire ebolavirus | 3,470 | 2,287 | Over, 25 June 2020 |
| 2022 | Mubende District, Central Region, Uganda | Sudan virus | 164 | 77 | Over, 11 January 2023 |
| 2025 | Kampala, Central Region, Uganda | Sudan virus | 14 | 4 | Over, 26 April 2025 |
| 2025 | Bulape, Kasaï Province, DR Congo | Zaire ebolavirus | 64 | 45 | Over, December 2025 |
| 2026 | Seven DR Congo provinces (Ituri 6,806; North Kivu 1,991; Haut-Uélé 398; Tshopo 64; Bas-Uélé 13; South Kivu 3; Sud-Ubangi 2) | Bundibugyo virus | 9,277 | 4,478 | Active (data to 14 Oct 2026) |
| 2026 | Uganda | Bundibugyo virus | 20 | 2 | Over, August 2026 |
| 2026 | Nairobi County, Kenya | Bundibugyo virus | 3 | 1 | Active (16 Oct 2026) |

**How to read it.** West African spikes are national totals, one per country; 2026 spikes are province totals placed on each province's main town. Spike height is proportional to confirmed cases; in the two whole-continent chapters heights follow the square root of cases so small outbreaks stay visible. Between reporting dates, the 2026 curve and each province's share of it are interpolated. Most outbreaks were separate jumps from animals to people; the dotted line on the continent shows the order they began, not a chain of infection. Only the 2026 route from eastern DR Congo through Uganda to Nairobi, taken from the WHO Kenya week 41 report, was one chain. Ebola is never eradicated, because the virus survives in animals; WHO declares an outbreak over after 42 days with no new cases.

2026 figures are confirmed cases and provisional. Earlier outbreaks show final totals, which for 2014–16, 2018–20 and 2022 include probable cases.

## How it was built

1. **Free imagery and elevation**, fetched in the browser and stitched into mosaics (`scripts/fetch_tiles_in_browser.js`): Sentinel-2 cloudless 2024 for the sharp ground, NASA Blue Marble Next Generation and VIIRS Black Marble for the whole continent, and AWS Terrain Tiles for relief.
2. **Terrain baking** (`scripts/terrain3.py`, `scripts/continent3.py`): reprojected to a latitude/longitude grid, natural colour, hillshade from elevation, water from Natural Earth, cut into texture chunks (`data/terrain/`, `data/continent/`).
3. **Map layers** (`scripts/vectors3.py`): rivers and country borders from Natural Earth; current DR Congo provinces, Ugandan regions and Nairobi County from geoBoundaries.
4. **The story page** (`scripts/scroll_template.html`, `scripts/build_scroll.py`): a three.js scene with draped borders, glowing spikes, a scripted camera, a locator map and the travel route, driven by scroll position. The builder holds the story data and puts everything into one self-contained HTML file.
5. **The dashboard** (`docs/dashboard.html`): d3, with the data in `data/outbreaks.json`, `data/timeline_2026.json` and `data/africa_grid.json`. Palette picked from NASA Earthdata.
6. **The video** (`scripts/video_scroll.py`): steps through the story frame by frame in headless Chromium and encodes it with ffmpeg.

Annotations follow the field-guide look of the documentary *How to Live on Earth*: Fira Sans labels in light italic and dotted leader lines.

The scripts were written for one working session and use absolute paths; change the paths at the top of each before running them yourself. Raw tile mosaics are not in the repo; re-create them with the browser script.

## Sources

**Case data**
- ECDC, Ebola outbreak in DRC and Uganda: confirmed cases and deaths by province, data to 14 Oct 2026. https://www.ecdc.europa.eu/en/ebola-outbreak-democratic-republic-congo-and-uganda
- WHO Disease Outbreak News, and WHO Africa weekly situation reports 21 and 22 (data to 4 and 11 Oct 2026). https://www.who.int/emergencies/disease-outbreak-news/item/2026-DON615
- WHO Kenya Emergency Preparedness and Response weekly situation report, week 41 (5–16 Oct 2026): the Kenyan case's travel route.
- Al Jazeera, Kenya's third case, 16 Oct 2026. https://www.aljazeera.com/news/2026/10/16/kenya-reports-third-bundibugyo-strain-ebola-case
- US CDC outbreak history. https://www.cdc.gov/ebola/outbreaks
- WHO statements on the end of transmission in Sierra Leone (17 Mar 2016), Guinea (1 Jun 2016) and Liberia (9 Jun 2016). https://www.who.int/en/news-room/detail/17-03-2016-who-statement-on-end-of-ebola-flare-up-in-sierra-leone · https://www.afro.who.int/news/end-ebola-transmission-guinea · https://afro.who.int/news/who-declares-end-most-recent-ebola-virus-disease-outbreak-liberia
- ECDC, Uganda 2022–23; WHO via ReliefWeb, Uganda 2025. https://www.ecdc.europa.eu/en/news-events/ebola-outbreak-uganda · https://reliefweb.int/report/uganda/disease-outbreak-news-sudan-virus-disease-uganda-26-april-2025
- WHO via allAfrica, Kasaï 2025. https://allafrica.com/stories/202512020161.html

**Map data (all free)**
- Sentinel-2 cloudless 2024 by EOX IT Services GmbH, contains modified Copernicus Sentinel data, CC BY-NC-SA 4.0. https://s2maps.eu
- NASA Blue Marble Next Generation and VIIRS Black Marble, via NASA GIBS. https://earthdata.nasa.gov/gibs
- Terrain Tiles on AWS. https://registry.opendata.aws/terrain-tiles/
- Natural Earth (public domain) and geoBoundaries (CC BY 4.0).

Non-commercial use only, because of the Sentinel-2 2024 licence.

## Credit

Built by Stephane ([@Kinjuriu](https://github.com/Kinjuriu)) with Claude, for a Claude community meetup, October 2026.
