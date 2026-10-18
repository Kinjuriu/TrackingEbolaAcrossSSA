# Tracking Ebola Across Sub-Saharan Africa

An animated 3D spike map that follows Ebola from the West African epidemic of 2014 to the Bundibugyo-virus outbreak in eastern DR Congo, which crossed into Uganda and, in October 2026, reached Nairobi. It plays like a 53-second film over real satellite relief, and every spike rises with confirmed cases.

- **Live page:** `docs/index.html` (turn on GitHub Pages from the `docs` folder to publish it)
- **Video:** `media/ebola-rising.mp4` (1600×900, 25 fps, 54 seconds)
- **Story data:** `data/outbreaks.json`

## What the film shows

| Chapter | Outbreak | Confirmed cases | Deaths |
|---|---|---|---|
| 2014–2016 | West Africa (Guinea, Liberia, Sierra Leone) | 28,616 | 11,310 |
| 2018–2020 | Eastern DRC (North Kivu and Ituri) | 3,470 | 2,287 |
| 2022 | Mubende, Uganda (Sudan virus) | 164 | 77 |
| 2025 | Bulape, Kasaï, DRC | 64 | 45 |
| 2026 | DRC, Uganda and Kenya (Bundibugyo virus), data to 14 to 16 Oct 2026 | DRC 9,277 · Uganda 20 · Kenya 3 | DRC 4,478 · Uganda 2 · Kenya 1 |

Spike height is proportional to confirmed cases on one scale for the whole film, so 2014 towers over everything and Kenya's three cases barely leave the ground. The 2026 spikes sit on one town per affected province, because province totals were the finest level I could find. Totals come from reporting dates; between those dates the curve, and each province's share of it, is interpolated. Figures for 2026 are provisional.

## How it was built

1. **Imagery and elevation.** Free map tiles were fetched in the browser and stitched into mosaics (`scripts/fetch_tiles_in_browser.js`): Sentinel-2 cloudless 2016 for colour, and Terrain Tiles on AWS for elevation. Sharper tiles cover the three places the camera zooms into: eastern DRC to Nairobi, Kasaï, and West Africa.
2. **Terrain baking.** `scripts/terrain2.py` reprojects the tiles to a flat latitude/longitude grid, shades relief from the elevation, draws lakes and coastlines from Natural Earth, and cuts the result into 32 texture chunks plus a height grid (`data/terrain/`).
3. **Map layers.** `scripts/vectors2.py` simplifies rivers, borders and province outlines: Natural Earth for rivers, lakes and countries, and geoBoundaries for the current 26 DRC provinces, Ugandan regions and Nairobi County.
4. **The page.** `scripts/rising2_template.html` is the three.js scene (terrain chunks, draped borders, glowing spikes, a scripted camera and a locator map). `scripts/build_rising.py` holds the story data and `scripts/build_rising2.py` puts everything into one self-contained HTML file.
5. **The video.** `scripts/video.py` steps through the film frame by frame in headless Chromium and encodes it with ffmpeg.

The annotations follow the field-guide look of the documentary *How to Live on Earth*: Fira Sans for labels, Sacramento for the handwritten notes, and dotted leader lines with small open circles.

The scripts were written for one working session and use absolute paths; change the paths at the top of each script before running them yourself. The raw tile mosaics (about 70 MB) are not in the repo; re-create them with the browser script.

## Sources

**Case data**
- ECDC, Ebola outbreak in DRC and Uganda: DRC confirmed cases and deaths by province, data to 14 Oct 2026. https://www.ecdc.europa.eu/en/ebola-outbreak-democratic-republic-congo-and-uganda
- WHO Disease Outbreak News and WHO African Region situation reports: 2026 milestones, May to October. https://www.who.int/emergencies/disease-outbreak-news/item/2026-DON615
- Al Jazeera and AP: Kenya, 3 cases and 1 death by 16 Oct 2026. https://www.aljazeera.com/news/2026/10/16/kenya-reports-third-bundibugyo-strain-ebola-case
- US CDC outbreak history: 2014–16 West Africa, 2018–20 DRC, 2022 Uganda. https://www.cdc.gov/ebola/outbreaks
- WHO via allAfrica: 2025 Kasaï outbreak, 64 cases and 45 deaths. https://allafrica.com/stories/202512020161.html

**Map data (all free)**
- Sentinel-2 cloudless 2016 by EOX IT Services GmbH, contains modified Copernicus Sentinel data 2016 & 2017, CC BY 4.0. https://s2maps.eu
- Terrain Tiles on AWS (Mapzen/Tilezen; sources include SRTM and ETOPO1). https://registry.opendata.aws/terrain-tiles/
- Natural Earth, public domain. https://www.naturalearthdata.com/
- geoBoundaries, CC BY 4.0. https://www.geoboundaries.org/

## Credit

Built by Stephane ([@Kinjuriu](https://github.com/Kinjuriu)) with Claude, for a Claude community meetup, October 2026.
