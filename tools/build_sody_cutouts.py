from PIL import Image
from pathlib import Path
import numpy as np
import cv2

ROOT = Path("assets")
ROOT.mkdir(exist_ok=True)

def save_image(image, name):
    path = ROOT / name
    image.save(path, "WEBP", quality=92, method=6)
    print("Published", name, image.size, path.stat().st_size)

# The approved bottle: a clean GrabCut silhouette eliminates the old
# rectangular patch of green screenshot background around the cap and base.
bottle_src = np.asarray(Image.open(ROOT / "sody-approved-home.webp").convert("RGB").crop((475,390,875,990)))
h,w=bottle_src.shape[:2]
outline=[(42,92),(44,76),(57,61),(75,47),(100,38),(145,31),(204,24),
(238,26),(259,33),(273,45),(279,60),(281,86),(272,105),(257,120),
(258,130),(286,143),(310,159),(321,184),(330,205),(342,250),(350,297),
(362,347),(373,413),(383,465),(390,512),(390,533),(376,552),(345,568),
(310,575),(248,584),(182,592),(145,589),(121,580),(105,568),(95,542),
(89,509),(80,461),(70,413),(57,343),(48,294),(38,249),(34,225),
(34,196),(39,175),(49,151),(59,136),(61,123),(51,111)]
shape=np.zeros((h,w),dtype=np.uint8)
cv2.fillPoly(shape,[np.asarray(outline,np.int32)],255)
inner=cv2.erode(shape,np.ones((27,27),np.uint8),iterations=1)
labels=np.where(shape==0,cv2.GC_BGD,cv2.GC_PR_FGD).astype(np.uint8)
labels[inner>0]=cv2.GC_FGD
b_model=np.zeros((1,65),np.float64)
f_model=np.zeros((1,65),np.float64)
cv2.grabCut(cv2.cvtColor(bottle_src,cv2.COLOR_RGB2BGR),labels,None,b_model,f_model,6,cv2.GC_INIT_WITH_MASK)
alpha=np.uint8((labels==cv2.GC_FGD)|(labels==cv2.GC_PR_FGD))*255
alpha=cv2.GaussianBlur(alpha,(3,3),.75)
bottle=Image.fromarray(np.dstack((bottle_src,alpha)),"RGBA")
save_image(bottle,"sody-bottle-cut.webp")

# Clean SODY molecular woman: preserve luminous nodes and facial silhouette,
# remove the flat original screenshot background (which appears as a dark shadow).
woman_img=Image.open(ROOT / "sody-approved-body.webp").convert("RGB")
arr=np.asarray(woman_img).astype(np.float32)
height,width=arr.shape[:2]
yy,xx=np.mgrid[:height,:width]
outline=[(617,65),(657,70),(714,64),(759,78),(806,103),(834,140),
(858,183),(865,230),(839,276),(812,301),(813,334),(846,360),
(885,404),(906,454),(914,520),(929,629),(927,797),(917,893),
(906,986),(887,1084),(856,1104),(838,1097),(828,1009),(812,948),
(789,887),(763,844),(743,868),(710,921),(680,998),(639,1097),
(597,1120),(544,1108),(509,1054),(477,1013),(448,948),(436,880),
(410,800),(415,706),(439,628),(452,551),(453,489),(476,432),
(518,402),(550,363),(565,317),(538,286),(532,255),(536,217),
(547,178),(573,134)]
mask=np.zeros((height,width),np.uint8)
cv2.fillPoly(mask,[np.asarray(outline,np.int32)],255)
mask=cv2.GaussianBlur(mask,(0,0),7)
brightness=arr[:,:,0]*.20+arr[:,:,1]*.65+arr[:,:,2]*.15
local=cv2.GaussianBlur(brightness,(0,0),26)
positive=np.maximum(0,brightness-local)
green=np.maximum(0,arr[:,:,1]-arr[:,:,0]*.96)
alpha=np.clip(-34+positive*11+green*.63+np.maximum(brightness-115,0)*.8,0,228)
# Retain smooth subtle facial features without reintroducing rectangular backplates.
face=np.zeros((height,width),np.uint8)
cv2.ellipse(face,(691,195),(137,112),-20,0,360,220,-1)
face=cv2.GaussianBlur(face,(0,0),13)
alpha=np.maximum(alpha,face*.52)
# Lower cropped portion is covered by SODY's actual HTML glass card.
alpha*=np.clip((1145-yy)/60,0,1)
alpha=np.uint8(np.clip(alpha*mask/255,0,255))
woman=Image.fromarray(np.uint8(np.clip(np.dstack((arr,alpha)),0,255)),"RGBA").crop((385,65,935,1120))
save_image(woman,"sody-woman-cut.webp")
