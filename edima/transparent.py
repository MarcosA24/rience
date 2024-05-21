import cv2
from PIL import Image
from PIL import ImageCms
import numpy as np
from matplotlib import pyplot as plt
#https://www.geeksforgeeks.org/removing-black-background-and-make-transparent-using-python-opencv/
#https://docs.opencv.org/3.4/d8/d83/tutorial_py_grabcut.html
# -------IMAGE FILE ROUTE
route= "E:/"
file = "goldenglobe_south"


imcv= cv2.imread(str(route)+str(file)+'.jpg',1)
#impil= Image.open(str(route)+str(file)+'.jpg')

#-- RESIZE 
divisor= 5
imcv= cv2.resize(imcv, (int(imcv.shape[1]/divisor), int(imcv.shape[0]/divisor)))
tmp = cv2.cvtColor(imcv,cv2.COLOR_BGR2GRAY)

#-- FUNCTIONS GLOSSARY
def white2transparent(imcv):
    imcv= imcv.convert('RGBA')
    data= imcv.getdata()
    
    newdata= []
    
    for item in data:
        if item[0] == 255 and item[1] ==255 and item[2]>=150:
            newdata.append((255,255,255,0))
        else:
            newdata.append(item)
    
    imcv.putdata(newdata)
    imcv.save(route+file+'trp.png',"PNG")
    print('saved in:',route)

def black2transparent(img):
    temp= cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    _, alpha = cv2.threshold(temp,0,255,cv2.THRESH_BINARY)
    b,g,r = cv2.split(img)
    imrgba= [b,g,r,alpha]
    dst= cv2.merge(imrgba,4)
    cv2.imshow('igra',dst)
    cv2.waitKey(0)
    cv2.imwrite('E:/second.png',dst)
    
#-- MAIN CODE

if __name__== '__main__':
    #imcv = cv2.cvtColor(imcv,cv2.COLOR_BGR2RGB)
    
    mask = np.zeros(imcv.shape[:2],np.uint8)
    bgdModel= np.zeros((1,65),np.float64)
    fgdModel= np.zeros((1,65),np.float64)
    
    print(imcv.shape[1],imcv.shape[0])
    rect= (0,0,imcv.shape[1]-1,imcv.shape[0])
    cv2.grabCut(imcv,mask,rect,bgdModel,fgdModel,5,cv2.GC_INIT_WITH_RECT)
    
    mask2= np.where((mask==2),0,1).astype('uint8')
    finale= imcv*mask2[:,:,np.newaxis]

    #Display the graphs -----------------------
    fig= plt.figure(figsize=(15,7))
    titles= ['mask1','mask2','final']
    graphs= [mask, mask2, finale]
    for g in range(3):
        print(g)
        fig.add_subplot(1,3,g+1)
        plt.imshow(graphs[g])
        plt.colorbar()
        plt.title(titles[g])
        #ax[g]= plt.imshow(graphs[g]), plt.colorbar()
    plt.show()
    
    black2transparent(finale)
    
    #cv2.imwrite('E:/transpGlobe_cv.png',imcv)




















'''
#threshold technique
_, alpha = cv2.threshold(tmp, 0,225, cv2.THRESH_BINARY)

b,g,r= cv2.split(imcv)
rgba = [b,g,r,alpha]

dst= cv2.merge(rgba,4)

cv2.imwrite(route+file+'_trp.png',dst)

print(impil.mode)
#imcv= cv2.cvtColor(numpy.array(imcv),cv2.COLOR_RGB2BGR)

gray= cv2.cvtColor(imcv,cv2.COLOR_BGR2GRAY)
cv2.imshow('g',gray)
_, threshold= cv2.threshold(gray,240,255,cv2.THRESH_BINARY_INV)

kernel= cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(11,11))
morphed= cv2.morphologyEx(threshold, cv2.MORPH_CLOSE,kernel)

cnts= cv2.findContours(morphed,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
cnt= sorted(cnts, key=cv2.contourArea)[-1]

x,y,w,h = cv2.boundingRect(cnt)
dst= imcv[y:y+h, x:x+w]

cv2.imshow('image',dst)
cv2.waitKey(0)
cv2.destroyAllWindows()

cv2.imwrite('E:/transparentglobe.png',dst)
'''