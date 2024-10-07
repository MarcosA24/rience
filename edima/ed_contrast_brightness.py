import cv2
import numpy as np
import argparse


#https://www.geeksforgeeks.org/changing-the-contrast-and-brightness-of-an-image-using-python-opencv/

imageName = R"C:\Users\user\Pictures\safescreen\kieran.jpg"
# FunctionsGlossary -----------------------------------------
    
def on_trackbar(val):
    #real-time trackbar edition
    alpha = val / alpha_slider_max
    beta = ( 1.0 - alpha )
    dst = cv2.addWeighted(src1, alpha, src1, beta, 0.0)
    cv2.imshow(window_name, dst)

def valueScaling(value):
    #Defines the value scale of the trackbar
    min_value = 0
    max_value = 100
    new_min = 0
    new_max = 255
    scaled_value = (value - min_value) * (new_max - new_min) / (max_value - min_value) + new_min
    return int(scaled_value)

parser= argparse.ArgumentParser(description='final')
parser.add_argument('--input1',help='Path to first input image',default=imageName)
args = parser.parse_args()

src1= cv2.imread(cv2.samples.findFile(args.input1))
if src1 is None:
    print('Could not open or find the image',args.input1)
    exit(0)

def imageSetup(brightness=0):
    #prepare to change RT brightness and contrast
    brightness= cv2.getTrackbarPos('Brightness',window_name)
    contrast= cv2.getTrackbarPos('Contrast',window_name)
    effect= controller(img,brightness,contrast)
    cv2.imshow('Effect',effect)
    
    if cv2.waitKey(0) == ord('k'): cv2.imwrite(newName,effect)
    elif cv2.waitKey(0) != ord('k'): cv2.destroyAllWindows()
    
def controller(img,brightness=255,contrast=127):
    #get the trackbar position current in RealTime
    brightness= int((brightness - 0)*(255-(-255))/(510-0)+(-255))
    contrast= int((contrast - 0)*(127 -(-127))/ (254-0)+(-127))
    if brightness != 0:
        if brightness >0:
            shadow = brightness
            max=255
        else:
            shadow=0
            max= 255+brightness 
        alpha= (max - shadow) /255
        gamma = shadow
        #Addweighted calculates the wighted sum of two arrays
        calc= cv2.addWeighted(img,alpha,img, 0 , gamma)
        
    else:
        calc= img
        
    if contrast !=0:
        Alpa= float(131*(contrast+127))/(127*(131-contrast))
        Yamma= 127*(1-Alpa)
        
        calc= cv2.addWeighted(calc,Alpa,calc,0,Yamma)
    
    #text string in the image, for renders
    #cv2.putText(calc,'B:{},C:{}'.format(brightness,contrast), (10,30),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
    return calc

def resize(img):
    #-- Resize the image ----------------------------------------------------
    divisor= 2
    img= cv2.resize(img, (int(img.shape[1]/divisor), int(img.shape[0]/divisor)))
    #resgray= cv2.resize(gray, (int(img.shape[1]/divisor), int(img.shape[0]/divisor)))
    return img

def showImage(img,window_name):
    #-- Display the results -----------------------------
    alpha_slider_max= 100
    cv2.namedWindow(window_name)
    cv2.imshow(window_name, img)
    
    cv2.createTrackbar('Contrast', window_name, 255,2*255, imageSetup)
    cv2.createTrackbar('Brightness', window_name, 127,2*127, imageSetup)
    #cv2.createButton('Save image',cv2.imwrite('new.jpg',img),None,cv2.QT_PUSH_BUTTON,0)
    
    effect= imageSetup(0)


# --Main CODE **********************
if __name__ == '__main__':
    window_name= 'windowF'
    newName= imageName.split('.')[0] + '_new2.' +imageName.split('.')[1]
    img = cv2.imread(imageName)
    #gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    #-- Resize the image ----------------------------------------------------
    img= resize(img)
    #-- Display the contrast/brightness modulator -----------------------------
    
    showImage(img,window_name)
    
    
        



    