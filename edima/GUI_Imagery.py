#https://towardsdev.com/create-a-simple-gui-image-processor-with-pyqt6-and-opencv-1821e1463691
import sys, os, pyperclip
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import (QApplication, QHBoxLayout, QMainWindow, QPushButton, QSpinBox, QVBoxLayout, QWidget, QFileDialog, QLabel, QListWidget,
                            QErrorMessage, QLineEdit, QSlider, QTabBar, QTabWidget, QCheckBox,QComboBox, QGridLayout, QRadioButton)
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt
import cv2
import numpy as np
from PIL import Image, ImageQt


class ImageWidget(QLabel):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setScaledContents(True)
    
    #to adjust the image data to that readable by QWidget
    def hasHeightForWidth(self):
        return self.pixmap() is not None

    def heightForWidth(self, w):
        if self.pixmap():
            try:
                return int(w * (self.pixmap().height() / self.pixmap().width()))
            except ZeroDivisionError:
                return 0       

def clearLayout(layout):
  while layout.count():
    child = layout.takeAt(0)
    if child.widget():
      child.widget().deleteLater()
      
def resize_image(image_data, max_img_width, max_img_height):
    scale_percent = min(max_img_width / image_data.shape[1], max_img_height / image_data.shape[0])
    width = int(image_data.shape[1] * scale_percent)
    height = int(image_data.shape[0] * scale_percent)
    newSize = (width, height)
    image_resized = cv2.resize(image_data, newSize, None, None, None, cv2.INTER_AREA)
    og_shape= image_data.shape
    rsz_shape= image_resized.shape
    return image_resized, og_shape, rsz_shape

def cv_image_from_PIL_image(pil_img):
    cv2_img = np.array(pil_img)
    cv2_img = cv2.cvtColor(cv2_img, cv2.COLOR_RGB2BGR)
    return cv2_img

def pixmap_from_cv_image(cv_image): #convert from cv2 into pyqt6 format, pixelmap
    #height, width, _ = cv_image.shape          #it causes an error in images that don't fit the 3D shape(1,1,1)
    height, width= cv_image.shape[0], cv_image.shape[1]
    if cv_image.shape[2]==3:    
        bytesPerLine = 3 * cv_image.shape[1]
        qImg = QImage(cv_image.data, width, height, bytesPerLine, QImage.Format.Format_RGB888).rgbSwapped()
        return QPixmap(qImg)
    elif cv_image.shape[2]==4:
        bytesPerLine = 4 * cv_image.shape[1]
        qImg = QImage(cv_image.data, width, height, bytesPerLine, QImage.Format.Format_RGBA8888).rgbSwapped()
        return QPixmap(qImg)

def get_image_mask(img, blue_shade, diff): #apply the tracing process
    lower = np.array([max(0, val) for val in [blue_shade[2]-diff, blue_shade[1]-diff, blue_shade[0]-diff]], dtype=np.uint8)
    upper = np.array([min(255, val) for val in [blue_shade[2]+diff, blue_shade[1]+diff, blue_shade[0]+diff]], dtype=np.uint8)
    mask = cv2.inRange(img, lower, upper)
    percent_traced = np.sum(mask > 0) / (mask.shape[0] * mask.shape[1])
    return cv2.cvtColor(mask, cv2.COLOR_BGR2RGB), percent_traced

def click_ev(ev,x,y,flags,param):
    cut= art.copy()
    if ev == cv2.EVENT_LBUTTONDOWN:
        print(x,' ',y)
        cv2.circle(cut, (x,y), radius=2, color=(0, 0, 255), thickness=4)
        cv2.imshow(window,cut)
        
    if ev == cv2.EVENT_RBUTTONDOWN:
        print(x,' ',y)
        size= (144,144)     #size of the rectangle fixed
        sq= [(x-size[0],y-size[0]),(x+size[0],y+size[0])]
        print(sq[0],sq[1])
        if x-size[0]/2>0 and x+size[0]<cut.shape[0] and y-size[1]/2>0 and y+size[1]<cut.shape[1]:
            cv2.rectangle(cut,sq[0],sq[1],(0,255,255),1)
            cv2.imshow(window,cut)
        else:
            print('Cut out of bounds')
            


    
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        self.setWindowTitle("Image Editor")
        self.resize(1200,500)
        #List all the window contents/layouts
        main_layout= QHBoxLayout()

        left_layout= QVBoxLayout()
        left_menu= QHBoxLayout() 
        og_image_layout= QVBoxLayout()
        left_bottom= QHBoxLayout()
        
        #the right panel we will divide it into tabs
        right_layout= QVBoxLayout()
        right_menu = QHBoxLayout()
        tabs= QTabWidget()
        res_image= QVBoxLayout()
        right_bottom= QGridLayout()
        right_layout.setSpacing(0)
        tabs.setMaximumHeight(120)
        
        #Initial parameters
        self.source_file = None
        self.source_image_cv = None
        self.max_img_height= 700
        self.max_img_width= 700
        
        #Images modified by each of the specifics
        self.traced_image_data= None
        self.escalated_image_data= None
        self.enhanced_image_data= None
        self.advEdited_image_data= None
        #list of the result images, for combining purposes. And the boxes that will enable to combine effects
        self.result_images_list= [self.traced_image_data,self.enhanced_image_data,self.advEdited_image_data]
    
        self.tracing_box, self.scaling_box, self.enhancing_box, self.advEd_box= None, None, None, None
        self.saving_boxes_list= [self.tracing_box, self.scaling_box, self.enhancing_box, self.advEd_box]
        #final result with the combined effects
        self.result_image_data = None
        
    ##LEFT LAYOUT. Original Image
        #Menu ----<
        select_image_button = QPushButton('Select Image')
        select_image_button.setFixedHeight(30)
        select_image_button.clicked.connect(self.source_search)
        
        self.source_path= QLineEdit()
        self.source_path.setMaxLength(200)
        self.source_path.setPlaceholderText('enter image path')
        self.source_path.editingFinished.connect(self.source_search)
        
        copy_path = QPushButton('copy path')
        copy_path.setFixedHeight(30)
        copy_path.clicked.connect(self.copy)
        
        left_menu.addWidget(select_image_button)
        left_menu.addWidget(self.source_path)
        left_menu.addWidget(copy_path)
        left_layout.addLayout(left_menu)
                
        #Original Image ----<
        self.original_image= ImageWidget()
        self.original_image.setMaximumSize(self.max_img_width, self.max_img_height)
        self.labelPath= QLabel()
        og_image_layout.addWidget(QLabel('Original Image: '))
        og_image_layout.addWidget(self.labelPath)
        og_image_layout.addWidget(self.original_image)
        left_layout.addLayout(og_image_layout)
    
        #Bottom ---<
        self.information= None
        self.original_image_shape= QLabel()
        left_bottom.addWidget(QLabel('Information:'))
        left_bottom.addWidget(self.original_image_shape)
        left_layout.addLayout(left_bottom)
    
    ##RIGHT LAYOUT. processed image
        #Right_Menu
        #Right_Tab1, parameters ---< It's where the parameters for the processing are
        def tab1(self):
            rgb_pane = QWidget(self)
            rgb_layout= QVBoxLayout()
            rgb_pane.setLayout(rgb_layout)
            rgb_param= QHBoxLayout()

            self.r_spinbox,self.g_spinbox,self.b_spinbox,self.threshold_spinbox = QSpinBox(),QSpinBox(),QSpinBox(),QSpinBox()
            self.r_slider,self.g_slider,self.b_slider,self.threshold_slider = QSlider(),QSlider(),QSlider(),QSlider()
                #Specify box and buttons characteristics.
            for start_val, prefix, spinbox, slider in zip([100,100,100,80],[ 'R', 'G', 'B','Threshold'],
                                                [self.r_spinbox,self.g_spinbox,self.b_spinbox,self.threshold_spinbox],
                                                [self.r_slider,self.g_slider,self.b_slider,self.threshold_slider]):
                spinbox.setPrefix(f'{prefix}:'),spinbox.setMinimum(0),spinbox.setMaximum(255),spinbox.setValue(start_val),spinbox.setFixedWidth(100)
                slider.setMinimum(0), slider.setMaximum(255),slider.setValue(start_val),slider.setFixedHeight(70)
                slider.valueChanged.connect(spinbox.setValue)
                spinbox.valueChanged.connect(slider.setValue)
                spinbox.valueChanged.connect(self.tracing_image)
                rgb_param.addWidget(spinbox)
                rgb_param.addWidget(slider)
            rgb_layout.addLayout(rgb_param)
            tabs.addTab(rgb_pane,'RGB_mask')
        tab1(self)
        
        #Right_Tab2, scale ----< Here, the size of the image can be modified according to different methods
        def tab2(self):
            scale_pane = QWidget(self)
            scale_param= QGridLayout()
            scale_pane.setLayout(scale_param)
            
            self.scaleNumber= QLabel()
            self.sliderScale= QSlider(Qt.Orientation.Horizontal)
            self.sliderScale.setMinimum(-30), self.sliderScale.setMaximum(30),self.sliderScale.setValue(1),self.sliderScale.setFixedWidth(300)
            self.sliderScale.valueChanged.connect(self.Ratio)
            self.exactShape= QLineEdit()
            self.exactShape.setPlaceholderText('height,width')
            self.exactShape.editingFinished.connect(self.Ratio)
            
            scale_param.addWidget(QLabel('Scale Value: '),0,0)
            scale_param.addWidget(self.scaleNumber,0,1)
            scale_param.addWidget(self.sliderScale,0,2)
            scale_param.addWidget(QLabel('Shape: '),1,0)
            scale_param.addWidget(self.exactShape,1,1)
            scale_param.addWidget(QLabel('leave blank to use slider. Only input in the defined way'))
            
            tabs.addTab(scale_pane,'Scale')
        tab2(self)
        
        def tab3(self):
            enhance_pane = QWidget(self)
            enhance_param= QGridLayout()
            enhance_pane.setLayout(enhance_param)
            
            self.contrast,self.brightness= QLabel('Contrast: \u03b1='), QLabel('Brightness: \u03B2=')
            self.contrastNum,self.brightnesNum= QLabel(), QLabel()
            self.contrastSlider,self.brightnesSlider = QSlider(Qt.Orientation.Horizontal), QSlider(Qt.Orientation.Horizontal)
            enhance_param.addWidget(self.contrast,0,0)
            enhance_param.addWidget(self.brightness,1,0)
            n=-1
            for label, sliderE in zip([self.contrastNum, self.brightnesNum],
                                        [self.contrastSlider,self.brightnesSlider]):
                n+=1
                if sliderE==self.contrastSlider: sliderE.setMinimum(-50),sliderE.setMaximum(150),sliderE.setValue(10)
                if sliderE==self.brightnesSlider: sliderE.setMinimum(-80),sliderE.setMaximum(80),sliderE.setValue(20)
                sliderE.valueChanged.connect(self.enhancer)
                enhance_param.addWidget(label,n,1)
                enhance_param.addWidget(sliderE,n,2)

            tabs.addTab(enhance_pane,'Enhance')
        tab3(self)
        
        def tab4(self):
            advEd_pane = QWidget(self)
            advEd_param= QVBoxLayout()
            advEd_pane.setLayout(advEd_param)
            advEd_selector= QHBoxLayout()
            self.advEd_specs= QHBoxLayout()
            
            #ADVANCED EDITION selector
            self.advanced = QComboBox()
            self.advanced_editions= ["Nothing","Transparent_thresholding and masking", "Transparent_contours and cropping","Transparent_color range filter",
                                     "Transparent_GrabCut algorithm","Edges detection","Pixelate Image"]
            self.advanced.addItems(self.advanced_editions)
            self.advanced.setFixedWidth(400), self.advanced.setFixedHeight(25)
            self.advanced.currentIndexChanged.connect(self.advanced_edition)
            self.advanced.currentIndexChanged.connect(self.advanced_param)
            advEd_selector.addWidget(QLabel('Image Advanced Edition'),alignment=Qt.AlignmentFlag.AlignTop)
            advEd_selector.addWidget(self.advanced,alignment=Qt.AlignmentFlag.AlignTop)
            
            #ADVANCED EDITION parameters, according to the edition chosen in the combobox from the selector.
            #They must be defined here first, if not the functions will not recognite the widget. Then, in the advanced_param function they will appear in the tab depending on the selector.            
            self.pixel= QSpinBox()
            self.pixel.setValue(4), self.pixel.setMinimum(1), self.pixel.setMaximum(64), self.pixel.setFixedWidth(50)
            self.BLUR,self.CANNY_THRESH_1,self.CANNY_THRESH_2 = QSpinBox(), QSpinBox(), QSpinBox()
            self.BLUR.setValue(21), self.CANNY_THRESH_1.setValue(10), self.CANNY_THRESH_2.setValue(200)
            self.radio_black, self.radio_white= QRadioButton(' black background'), QRadioButton(' white background')
            
            advEd_param.addLayout(advEd_selector)
            advEd_param.addLayout(self.advEd_specs)
            
            tabs.addTab(advEd_pane,'Editions')
        tab4(self)
        right_layout.addWidget(tabs)
        
        #Right processed Image. It depends on the checkboxes if the tabs affect it or not.
        self.result_image= ImageWidget()
        self.result_image.setMaximumSize(self.max_img_width, self.max_img_height)
        res_image.addWidget(QLabel('Result Image:'))
        res_image.addWidget(self.result_image)
        right_layout.addLayout(res_image)
        
        #Right_Bottom
        # ---< checkboxes
        n=-1
        self.tracing_box,self.scaling_box,self.enhancing_box, self.advEd_box= QCheckBox('Tracing'),QCheckBox('Scaling'),QCheckBox('Enhancing'),QCheckBox('Advanced')
        for chbox in [self.tracing_box,self.scaling_box,self.enhancing_box,self.advEd_box]:
            n+=1
            chbox.setFixedWidth(100)
            #chbox.setFont()
            chbox.setChecked(False)
            right_bottom.addWidget(chbox,1,n)
        
        self.save_button= QPushButton('Save File')
        self.save_button.clicked.connect(self.recorder) #connects to the saving function
        self.save_button.setFixedWidth(100)
        self.result_image_shape= QLabel()
        self.percent_traced_label= QLabel()
        
        right_bottom.addWidget(self.result_image_shape,0,0)
        right_bottom.addWidget(self.percent_traced_label,0,2)
        right_bottom.addWidget(self.save_button,2,4)
        right_layout.addLayout(right_bottom)
    
        #Aggregate all the layouts and their childs to define the MainWindow
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)
        
        widget= QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)
    
    ##>> Recursive processes >>----------------------------
    def copy(self):
        pyperclip.copy(self.labelPath.text())
    
    def check_source(self):
        if self.source_image_cv is None:
                error_dialog= QErrorMessage()
                error_dialog.showMessage('No Image selected')
                error_dialog.exec()
        else: return True
            
    def source_search(self):
        def path_validator():
            if self.source_path.text()!='':
                if os.path.exists(self.source_path.text()): self.source_file= self.source_path.text()
                else:
                    error_dialog= QErrorMessage()
                    error_dialog.showMessage('Image Path not valid.')
                    error_dialog.exec()
            else:
                origin_path= QFileDialog.getOpenFileName()[0] #windows File explorer
                if os.path.exists(origin_path): self.source_file= origin_path
                else:
                    error_dialog= QErrorMessage()
                    error_dialog.showMessage('Image Path not valid.')
                    error_dialog.exec()
                    
        path_validator()
        self.source_image_cv= cv2.imread(self.source_file)
        self.original_image.setPixmap(pixmap_from_cv_image(self.source_image_cv))
        self.labelPath.setText(self.source_file)
        original_shape= self.source_image_cv.shape
        self.original_image_shape.setText(f'original shape: {original_shape}')
    
    def image_selector(self):
        img= self.source_image_cv
        for eff in self.result_images_list:
            if eff!= None: img= eff
        return img
        
    def advanced_param(self):
        if self.advanced.currentText()==self.advanced_editions[1] or self.advanced.currentText()==self.advanced_editions[2]:
            clearLayout(self.advEd_specs)
            for rad in [self.radio_black,self.radio_white]:
                rad.toggled.connect(self.advanced_edition)
                self.advEd_specs.addWidget(rad)
                
        elif self.advanced.currentText()==self.advanced_editions[5]: 
            clearLayout(self.advEd_specs)
            #EDGE detection parameters
            for pm,max_value,label in zip([self.BLUR,self.CANNY_THRESH_1,self.CANNY_THRESH_2],[100,200,200],
                                                    ['Blur','Canny_threshold_1','Canny_threshold_2']):
                pm.setMinimum(0), pm.setMaximum(max_value), pm.setFixedWidth(50)
                #pm.valueChanged.connect(self.advanced_edition)
                self.advEd_specs.addWidget(QLabel(label),alignment=Qt.AlignmentFlag.AlignLeft)
                self.advEd_specs.addWidget(pm,alignment=Qt.AlignmentFlag.AlignHCenter)
        elif self.advanced.currentText()==self.advanced_editions[6]:
            #PIXEL parameter
            clearLayout(self.advEd_specs)
            self.pixel.valueChanged.connect(self.advanced_edition)
            self.advEd_specs.addWidget(QLabel('Pixel Size'))
            self.advEd_specs.addWidget(self.pixel,alignment=Qt.AlignmentFlag.AlignLeft)
        else: clearLayout(self.advEd_specs)
    ##>> IMAGE EDITION MAIN FUNCTIONS >>----------------------------
    #>. RGB Mask
    def tracing_image(self):
        if self.check_source() is True:
            self.traced_image_data, percent_traced = get_image_mask(self.source_image_cv,
                                                                   [self.r_spinbox.value(), self.g_spinbox.value(), self.b_spinbox.value()],
                                                                   self.threshold_spinbox.value())
            self.percent_traced_label.setText(f'Percent of image traced: {(percent_traced * 100):.3f}%')
            self.result_image.setPixmap(pixmap_from_cv_image(resize_image(self.traced_image_data, self.max_img_width, self.max_img_height)[0]))
            result_shape= resize_image(self.traced_image_data, self.max_img_width, self.max_img_height)[1]
            self.result_image_shape.setText(f'Result shape: {result_shape}')

    #>.Image Scaling
    def Ratio(self):
        if self.check_source() is True:
            sh= self.exactShape.text()
            if sh=='':
                def Rationum():
                    if self.sliderScale.value()<0:return -1/self.sliderScale.value()
                    elif self.sliderScale.value()>0: return self.sliderScale.value()/10
                    elif self.sliderScale.value()==0: return 1
                divisor= Rationum()
                self.scaleNumber.setText(str(divisor))
                self.escalated_image_data= cv2.resize(self.source_image_cv, 
                                        (int(self.source_image_cv.shape[1]*divisor), int(self.source_image_cv.shape[0]*divisor)))
                #escalated_image_resized = resize_image(self.escalated_image_data, self.max_img_width, self.max_img_height)[0]
                #self.result_image.setPixmap(pixmap_from_cv_image(self.source_image_cv))
                result_shape= self.escalated_image_data.shape
                self.result_image_shape.setText(f'Result shape: {result_shape}')
            else:
                shape= sh.split(',')
                result_shape= (int(shape[1]),int(shape[0]))
                self.escalated_image_data= cv2.resize(self.source_image_cv, 
                                        result_shape)
                self.result_image_shape.setText(f'Result shape: {result_shape}')
    
    #>.Contrast & Brightness
    def enhancer(self):
        if self.check_source() is True:
            self.contrastNum.setText(str(self.contrastSlider.value()/10))
            self.brightnesNum.setText(str(self.brightnesSlider.value()))
            enh= np.zeros(self.source_image_cv.shape,self.source_image_cv.dtype)
            alpha= self.contrastSlider.value()/10
            beta= self.brightnesSlider.value()
            #Do the operation new_image(i,j) = alpha*image(i,j) + beta
            self.enhanced_image_data= cv2.convertScaleAbs(self.source_image_cv,alpha=alpha,beta=beta)
            #hist= cv2.calcHist(self.enhanced_image_data,[0],None,[256],[0,256])
            #plt.plot(hist,color='blue')
            #plt.show()
            self.image_selector()
            self.result_image.setPixmap(pixmap_from_cv_image(resize_image(self.enhanced_image_data, self.max_img_width, self.max_img_height)[0]))
            
            ''' The theory behind the ConvertScaleAbs
            for y in range(self.source_image_cv.shape[0]):
                for x in range(self.source_image_cv.shape[1]):
                    for c in range(self.source_image_cv.shape[2]):
                        enh[y,x,c]= np.clip(alpha*self.source_image_cv[y,x,c]+beta, 0, 255)
            '''
    
    #Crop a slice of the image
    def crop(self):
        pass
    
    #>.Advanced Edition: png transparent, edges detection, pixelate image(to be introduced inside)
    def advanced_edition(self):
        def backColor():
            if self.radio_black.isChecked(): return (1,cv2.THRESH_BINARY)
            elif self.radio_white.isChecked(): return (225,cv2.THRESH_BINARY_INV)
        
        if self.check_source() is True:
            if self.advanced.currentText()==self.advanced_editions[0]: pass
            #Transparent_ thresholding and masking
            #https://blog.finxter.com/5-best-ways-to-remove-black-background-and-make-it-transparent-using-opencv-python/
            elif self.advanced.currentText()==self.advanced_editions[1]:
                if self.radio_black.isChecked() or self.radio_white.isChecked():
                    gray = cv2.cvtColor(self.source_image_cv, cv2.COLOR_BGR2GRAY)
                    _, thresh = cv2.threshold(gray, backColor()[0], 225, backColor()[1])      # Set threshold to detect non-black pixels
                    alpha_channel = thresh                                           #Set the alpha channel to make black pixels(0,0,0) as transparent
                    #alpha_channel = cv2.bitwise_not(thresh)                         # Inverted threshold. If want to leave only the black pixels                           
                    b, g, r = cv2.split(self.source_image_cv)
                    rgba= cv2.merge((b,g,r,alpha_channel))                          # Add the alpha channel to the image
                    self.advEdited_image_data= rgba
                    self.result_image.setPixmap(pixmap_from_cv_image(resize_image(self.advEdited_image_data, self.max_img_width, self.max_img_height)[0])) #solve pixmap show error
            
            elif self.advanced.currentText()==self.advanced_editions[2]:
            #Transparent_contour detection and cropping
                if self.radio_black.isChecked() or self.radio_white.isChecked():
                    gray = cv2.cvtColor(self.source_image_cv, cv2.COLOR_BGR2GRAY)
                    _, thresh = cv2.threshold(gray, backColor()[0], 225, backColor()[1])
                    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # find contours
                    largest_contour = max(contours, key=cv2.contourArea)                                # Assume the largest external contour is the object to keep
                    x, y, w, h = cv2.boundingRect(largest_contour)
                    print(contours, largest_contour,x,y,w,h)
                    crop = self.source_image_cv[y:y+h, x:x+w]                                           # Crop the image using the dimensions of the bounding rectangle
                    alpha_channel = np.ones(crop.shape[:2], dtype='uint8') * 255                        # Create new alpha channel with same dimensions as cropped image
                    b, g, r = cv2.split(crop)
                    rgba = cv2.merge((b,g,r,alpha_channel))
                    self.advEdited_image_data= rgba
                    self.result_image.setPixmap(pixmap_from_cv_image(resize_image(self.advEdited_image_data, self.max_img_width, self.max_img_height)[0])) #solve pixmap show error
                
            elif self.advanced.currentText()==self.advanced_editions[3]:
            #Transparent_Color Range Filtering
                pass
            elif self.advanced.currentText()==self.advanced_editions[4]:
            #Transparent_GrabCut algorithm
                pass
            
            elif self.advanced.currentText()==self.advanced_editions[5]:
            #EDGES detection
                gray= cv2.resize(self.image_selector(), (int(self.image_selector().shape[1]), int(self.image_selector().shape[0])))
                gray = cv2.cvtColor(self.image_selector(),cv2.COLOR_BGR2GRAY)
                edges = cv2.Canny(gray, self.CANNY_THRESH_1.value(), self.CANNY_THRESH_2.value())
                edges = cv2.dilate(edges, None)
                edges = cv2.erode(edges, None)
                self.advEdited_image_data= edges
                self.result_image.setPixmap(pixmap_from_cv_image(resize_image(edges, self.max_img_width, self.max_img_height)[0])) #solve the problem to show it on the GUI
            
            elif self.advanced.currentText()==self.advanced_editions[6]:
            #Pixelate an image.
                pixel_size= self.pixel.value()
                px = Image.open(self.source_file)
                px = px.resize((px.size[0] // pixel_size, px.size[1] // pixel_size),Image.NEAREST)
                px = px.resize((px.size[0] * pixel_size, px.size[1] * pixel_size),Image.NEAREST)
                self.advEdited_image_data= cv_image_from_PIL_image(px)
                self.result_image.setPixmap(QPixmap.fromImage(ImageQt.ImageQt(px)))        #solve the problem of not showing in pixmap
                #for now, it return the data in the saved image, but does not show it in the GUI result_image
                
    ###>> SAVING THE RESULTS    >>----------------------------
    #>.#combine various effects to get the mixed final image
    def combiner(self): 
        final_image= self.source_image_cv
        for chbox in [self.tracing_box,self.enhancing_box,self.advEd_box,self.scaling_box]:
            if chbox.isChecked():
                if chbox==self.tracing_box: final_image= self.traced_image_data
                if chbox==self.enhancing_box: final_image= self.enhanced_image_data
                if chbox==self.advEd_box: final_image= self.advEdited_image_data
                if chbox==self.scaling_box: final_image= cv2.resize(final_image,(self.escalated_image_data.shape[1],self.escalated_image_data.shape[0]))
                else: pass
        return final_image

    #>.Recording function
    def recorder(self):
        self.result_image_data= self.combiner()
        if self.result_image_data is None:
            error_dialog = QErrorMessage()
            error_dialog.showMessage('No image processed. Please check one of the boxes on the left')
            error_dialog.exec()
        else:
            out_file = QFileDialog.getSaveFileName(self, 'Save File')[0]
            if len(out_file) > 0: cv2.imwrite(out_file+'.png', self.result_image_data)

if __name__=='__main__':
    app = QApplication(sys.argv)
    
    #MAIN WINDOW --->>
    if True:
        window = MainWindow()
        window.show()
        
        app.exec()   
        
