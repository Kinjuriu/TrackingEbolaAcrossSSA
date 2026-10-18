// Run in the browser console on a page from https://s3.amazonaws.com (any tile URL works).
// Fetches free map tiles, stitches them on a canvas and saves one image per set.
// Sentinel-2 cloudless 2016 by EOX (CC BY 4.0) + Terrain Tiles on AWS (terrarium encoding).
async function stitch(name, urlFn, z, x0, x1, y0, y1, mime, q){
  const W=(x1-x0+1)*256, H=(y1-y0+1)*256, c=document.createElement('canvas'); c.width=W; c.height=H;
  const g=c.getContext('2d'); const jobs=[]; for(let y=y0;y<=y1;y++) for(let x=x0;x<=x1;x++) jobs.push([x,y]);
  async function worker(){ while(jobs.length){ const [x,y]=jobs.shift(); const r=await fetch(urlFn(z,x,y));
    const bm=await createImageBitmap(await r.blob(),{colorSpaceConversion:'none',premultiplyAlpha:'none'}); g.drawImage(bm,(x-x0)*256,(y-y0)*256); } }
  await Promise.all(Array.from({length:10},worker));
  const blob=await new Promise(res=>c.toBlob(res,mime,q)); const a=document.createElement('a'); a.href=URL.createObjectURL(blob); a.download=name; a.click();
}
const eox=(z,x,y)=>`https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless_3857/default/g/${z}/${y}/${x}.jpg`;
const dem=(z,x,y)=>`https://s3.amazonaws.com/elevation-tiles-prod/terrarium/${z}/${x}/${y}.png`;
// Region: 24W-52E, 16S-24N at zoom 7, plus detail patches (eastern DRC z9, Kasai z8, West Africa z8)
await stitch('s2cloudless2016_z7_x55-82_y55-69.jpg', eox, 7, 55, 82, 55, 69, 'image/jpeg', 0.92);
await stitch('terrarium_z7_x55-82_y55-69.png', dem, 7, 55, 82, 55, 69, 'image/png');
await stitch('terrarium_z9_x292-310_y250-261.png', dem, 9, 292, 310, 250, 261, 'image/png');
await stitch('terrarium_z8_x140-146_y128-133.png', dem, 8, 140, 146, 128, 133, 'image/png');
await stitch('terrarium_z8_x117-123_y119-125.png', dem, 8, 117, 123, 119, 125, 'image/png');
// detail imagery packed into one 4864x4864 file: z9 east at (0,0), z8 Kasai at (0,3072), z8 West Africa at (1792,3072)
