from PIL import Image, ImageDraw, ImageFilter
from pathlib import Path
import numpy as np
import cv2

ROOT=Path("assets")
ROOT.mkdir(exist_ok=True)

def rounded_mask(im, polygon, sigma):
    m=Image.new("L", im.size, 0)
    ImageDraw.Draw(m).polygon(polygon,fill=255)
    return m.filter(ImageFilter.GaussianBlur(sigma))

home=Image.open(ROOT/"sody-approved-home.webp").convert("RGBA")
rgb=np.asarray(home.convert("RGB"), dtype=np.float32)
height,width=rgb.shape[:2]
# A precise silhouette + per-row background subtraction. The old polygon alone
# kept the green screenshot behind the bottle as a rectangular-looking halo.
bottle_coords=[(530,449),(545,430),(558,422),(621,409),(682,400),(711,418),
(734,449),(744,488),(743,513),(724,524),(733,531),(771,542),(798,573),
(816,632),(834,745),(850,842),(852,889),(839,925),(813,949),(755,971),
(649,978),(590,957),(553,943),(537,914),(526,874),(519,803),(504,708),
(500,638),(509,590),(528,555),(541,537),(520,520),(506,490)]
mask=np.asarray(rounded_mask(home,bottle_coords,2.8), dtype=np.float32)
left=np.median(rgb[:,414:465,:],axis=1)
right=np.median(rgb[:,900:937,:],axis=1)
interp=np.clip((np.arange(width,dtype=np.float32)-440)/475,0,1)
background=left[:,None,:]*(1-interp[None,:,None])+right[:,None,:]*interp[None,:,None]
delta=np.linalg.norm(rgb-background,axis=2)
alpha=np.uint8(np.clip(mask*np.clip((delta-14)/37,0,1),0,255))
home.putalpha(Image.fromarray(alpha,"L"))
home=home.crop((475,390,875,990))
home.save(ROOT/"sody-bottle-cut.webp","WEBP",quality=92,method=6)

im=Image.open(ROOT/"sody-approved-body.webp").convert("RGBA")
arr=np.array(im).astype(np.float32)
height,width=arr.shape[:2]
rgb=arr[:,:,:3]
lum=rgb[:,:,1]*.62+rgb[:,:,0]*.2+rgb[:,:,2]*.18
smooth=cv2.GaussianBlur(lum,(0,0),sigmaX=85,sigmaY=85)
polygon=[(620,64),(731,61),(809,80),(854,119),(872,187),(873,252),
(828,329),(809,373),(856,393),(893,457),(911,525),(923,802),(908,1090),
(867,1220),(839,1267),(799,1248),(791,1127),(756,1052),(724,1014),
(699,1127),(650,1282),(592,1366),(497,1337),(446,1254),(402,1153),
(353,1071),(316,1007),(351,906),(400,786),(411,668),(410,553),
(421,472),(464,418),(526,382),(544,331),(505,282),(517,226),
(528,177),(565,125)]
mask=rounded_mask(im,polygon,17)
sp=np.asarray(mask,dtype=np.float32)/255.0
bright=np.maximum(rgb[:,:,1]-rgb[:,:,0]*.95,0)*.4+np.maximum(lum-smooth,0)
alpha=np.clip((bright-3)*5.5,0,242)*sp
ys=np.arange(height,dtype=np.float32)[:,None]
alpha*=np.clip((1240-ys)/140,0,1)
xs=np.arange(width,dtype=np.float32)[None,:]
# Remove lettering on the far left of the original approved screenshot
alpha*=np.where(ys>840,np.clip((xs-400)/65,0,1),1)
arr[:,:,3]=np.clip(alpha,0,255)
woman=Image.fromarray(np.uint8(arr),"RGBA").crop((310,65,933,1380))
woman.save(ROOT/"sody-woman-cut.webp","WEBP",quality=90,method=6)

for path in [ROOT/"sody-bottle-cut.webp",ROOT/"sody-woman-cut.webp"]:
    check=Image.open(path)
    assert check.mode=="RGBA" and check.getbbox()
    print(path, check.size, path.stat().st_size)
