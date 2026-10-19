import numpy as np, json, base64, io
from PIL import Image
from scipy.ndimage import map_coordinates, gaussian_filter
Image.MAX_IMAGE_PIXELS=None
SRC="/mnt/user-data/uploads/Downloads"; OUT="/home/claude/tex3"
def merc_px(lon, lat, z, x0, y0):
    n=2**z*256; px=(lon+180)/360*n-x0*256
    lr=np.radians(np.clip(lat,-85,85)); py=(1-np.arcsinh(np.tan(lr))/np.pi)/2*n-y0*256; return px,py
CB=[-28.125, 56.25, -40.97, 40.97]   # lon0, lon1, lat0, lat1 of the z6 tile block
PPD=36
W,H=int((CB[1]-CB[0])*PPD), int((CB[3]-CB[2])*PPD)
lons=CB[0]+(np.arange(W)+0.5)/PPD; lats=CB[3]-(np.arange(H)+0.5)/PPD
LON,LAT=np.meshgrid(lons,lats)
px,py=merc_px(LON,LAT,6,27,24)
def bake(name, out, grade):
    a=np.asarray(Image.open(f"{SRC}/{name}").convert("RGB")).astype(np.float32)/255
    rgb=np.stack([map_coordinates(a[...,c],[py,px],order=1,mode='nearest') for c in range(3)],-1)
    rgb=grade(rgb)
    m=np.minimum.reduce([(LON-CB[0])/(CB[1]-CB[0]),(CB[1]-LON)/(CB[1]-CB[0]),(LAT-CB[2])/(CB[3]-CB[2]),(CB[3]-LAT)/(CB[3]-CB[2])])
    e=np.clip(m/0.09,0,1)[...,None]; e=e*e*(3-2*e); rgb=rgb*e+np.array([0.02,0.031,0.039])*(1-e)
    buf=io.BytesIO(); Image.fromarray((np.clip(rgb,0,1)*255).astype(np.uint8)).save(buf,"JPEG",quality=84,optimize=True,progressive=True)
    open(f"{OUT}/{out}","wb").write(buf.getvalue()); print(out,(W,H),len(buf.getvalue())//1024,"KB")
bake("bluemarble_ng_z6_x27-42_y24-39.jpg","bluemarble.jpg", lambda c: np.power(np.clip((c-0.01)*1.08,0,1),0.92))
bake("blackmarble_viirs_z6_x27-42_y24-39.jpg","blackmarble.jpg", lambda c: np.clip(c*1.15,0,1))
# continent heights at 0.25 deg
t=np.asarray(Image.open(f"{SRC}/terrarium_z5_x13-21_y12-19.png").convert("RGB")).astype(np.float32)
E=t[...,0]*256+t[...,1]+t[...,2]/256-32768
GP=4.0; HW,HH=int((CB[1]-CB[0])*GP)+1, int((CB[3]-CB[2])*GP)+1
lo=CB[0]+np.arange(HW)/GP; la=CB[3]-np.arange(HH)/GP; LO,LA=np.meshgrid(lo,la)
qx,qy=merc_px(LO,LA,5,13,12)
e=map_coordinates(E,[qy,qx],order=1,mode='nearest'); e=gaussian_filter(np.clip(e,0,6375),0.8)
open(f"{OUT}/cont_height.b64","w").write(base64.b64encode((e/25).astype(np.uint8).tobytes()).decode())
json.dump({"bounds":CB,"grid":[HW,HH],"gp":GP,"hscale":25}, open(f"{OUT}/cont_dims.json","w"))
print("cont grid",(HW,HH))
