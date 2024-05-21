import cv2
import numpy as np

#https://stackoverflow.com/questions/29313667/how-do-i-remove-the-background-from-this-kind-of-image?rq=3
#https://www.educative.io/answers/removing-background-using-opencv
#== Parameters =======================================================================
BLUR = 21
CANNY_THRESH_1 = 10
CANNY_THRESH_2 = 200
MASK_DILATE_ITER = 10
MASK_ERODE_ITER = 10
MASK_COLOR = (0.0,0.0,1.0) # In BGR format

image_path = R"E:\goldenglobe_south.jpg"
image = cv2.imread(image_path)

gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

#-- Resize the image ----------------------------------------------------
divisor= 5
img= cv2.resize(image, (int(image.shape[1]/divisor), int(image.shape[0]/divisor)))
resgray= cv2.resize(gray, (int(img.shape[1]/divisor), int(img.shape[0]/divisor)))




#-- Edge detection -------------------------------------------------------------------
edges = cv2.Canny(resgray, CANNY_THRESH_1, CANNY_THRESH_2)
edges = cv2.dilate(edges, None)
edges = cv2.erode(edges, None)

#-- Find contours in edges, sort by area ---------------------------------------------
contour_info = []
contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
# Previously, for a previous version of cv2, this line was: 
# _, contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
# Thanks to notes from commenters, I've updated the code but left this note
for c in contours:
    contour_info.append((c,cv2.isContourConvex(c),cv2.contourArea(c),))
contour_info = sorted(contour_info, key=lambda c: c[2], reverse=True)
max_contour = contour_info[0]

#-- Create empty mask, draw filled polygon on it corresponding to largest contour ----
# Mask is black, polygon is white
mask = np.zeros(edges.shape)
cv2.fillConvexPoly(mask, max_contour[0], (255))

#-- Smooth mask, then blur it --------------------------------------------------------
mask = cv2.dilate(mask, None, iterations=MASK_DILATE_ITER)
mask = cv2.erode(mask, None, iterations=MASK_ERODE_ITER)
mask = cv2.GaussianBlur(mask, (BLUR, BLUR), 0)
mask_stack = np.dstack([mask]*3)    # Create 3-channel alpha mask

#-- Blend masked img into MASK_COLOR background --------------------------------------
mask_stack  = mask_stack.astype('float32') / 255.0          # Use float matrices, 
img         = img.astype('float32') / 255.0                 #  for easy blending
masked = (mask_stack * img) + ((1-mask_stack) * MASK_COLOR) # Blend
masked = (masked * 255).astype('uint8')                     # Convert back to 8-bit 

cv2.imshow('img', masked)                                   # Display
cv2.waitKey()
'''
window_name = 'Background Removed'
cv2.namedWindow(window_name)

while True:
    gray = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)

    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    _, threshold_img = cv2.threshold(blur, blk_thresh, 255, cv2.THRESH_BINARY)

    mask = 255 - threshold_img

    result = cv2.bitwise_and(resized_image, resized_image, mask=mask)

    cv2.imshow(window_name, result)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
'''