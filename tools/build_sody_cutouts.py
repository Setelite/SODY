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

home=Image.open(ROOT/"sody-approved-home.webp").convert("RGB").crop((475,390,875,990))
rgb=np.asarray(home, dtype=np.float32)
h,w=rgb.shape[:2]
# True shaped silhouette derived from the approved product render,
# without preserving the original screenshot's rectangular green background.
outline=[(42,92),(44,76),(57,61),(75,47),(100,38),(145,31),
(204,24),(238,26),(259,33),(273,45),(279,60),(281,86),
(272,105),(257,120),(258,130),(286,143),(310,159),
(321,184),(330,205),(342,250),(350,297),(362,347),
(373,413),(383,465),(390,512),(390,533),(376,552),
(345,568),(310,575),(248,584),(182,592),(145,589),
(121,580),(105,568),(95,542),(89,509),(80,461),(70,413),
(57,343),(48,294),(38,249),(34,225),(34,196),(39,175),
(49,151),(59,136),(61,123),(51,111)]
mask=np.zeros((h,w),np.uint8)
cv2.fillPoly(mask,[np.asarray(outline,np.int32)],255)
dist=cv2.distanceTransform(mask,cv2.DIST_L2,3)
left=np.median(rgb[:,:20,:],axis=1)
right=np.median(rgb[:,-20:,:],axis=1)
x=np.linspace(0,1,w,dtype=np.float32)[None,:,None]
background=left[:,None,:]*(1-x)+right[:,None,:]*x
color_delta=np.linalg.norm(rgb-background,axis=2)
edge_opacity=np.clip((color_delta-13)/32,0,1)
interior=np.clip((dist-5)/16,0,1)
alpha=(mask/255)*(edge_opacity*(1-interior)+interior)
alpha=cv2.GaussianBlur(np.uint8(np.clip(alpha*255,0,255)),(5,5),1.1)
bottle=home.convert("RGBA")
bottle.putalpha(Image.fromarray(alpha,"L"))
bottle.save(ROOT/"sody-bottle-cut.webp","WEBP",quality=92,method=6)

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
