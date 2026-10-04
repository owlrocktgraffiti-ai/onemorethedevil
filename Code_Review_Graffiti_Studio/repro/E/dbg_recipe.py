from common import *
import cv2
from photo_prepare import recipe
im,box=wall_with_panel()
for variant in ['plain','framed']:
    x=im.copy()
    if variant=='framed':
        d=ImageDraw.Draw(x);x0,y0,x1,y1=box;d.rectangle((x0,y0,x1,y1),outline=(20,20,20),width=10)
    image=x
    rgb=np.array(image.resize((min(900,image.width),round(image.height*min(900,image.width)/image.width))))
    gray=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY)
    edges=cv2.Canny(cv2.GaussianBlur(gray,(5,5),0),45,130)
    contours,_=cv2.findContours(edges,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
    h,w=gray.shape;best=[]
    for c in contours:
        q=cv2.approxPolyDP(c,.02*cv2.arcLength(c,True),True)
        area=cv2.contourArea(q)/(h*w)
        if area>.3:best.append((len(q),round(area,3),cv2.isContourConvex(q)))
    print(variant,len(contours),best[:10],recipe(x,'x.jpg')[1])
