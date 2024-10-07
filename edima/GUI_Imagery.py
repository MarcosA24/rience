#https://towardsdev.com/create-a-simple-gui-image-processor-with-pyqt6-and-opencv-1821e1463691
import sys, os
from PyQt6.QtWidgets import (QApplication, QHBoxLayout, QMainWindow, QPushButton, QSpinBox, QVBoxLayout, QWidget, QFileDialog, QLabel, 
                            QErrorMessage, QLineEdit, QSlider, QTabBar, QTabWidget, QCheckBox)
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt
import cv2
import numpy as np
from PIL import Image


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

def resize_image(image_data, max_img_width, max_img_height):
    scale_percent = min(max_img_width / image_data.shape[1], max_img_height / image_data.shape[0])
    width = int(image_data.shape[1] * scale_percent)
    height = int(image_data.shape[0] * scale_percent)
    newSize = (width, height)
    image_resized = cv2.resize(image_data, newSize, None, None, None, cv2.INTER_AREA)
    og_shape= image_data.shape
    rsz_shape= image_resized.shape
    return image_resized, og_shape, rsz_shape
   
def pixmap_from_cv_image(cv_image): #convert from cv2 into pyqt6 format, pixelmap
    height, width, _ = cv_image.shape
    bytesPerLine = 3 * width
    qImg = QImage(cv_image.data, width, height, bytesPerLine, QImage.Format.Format_RGB888).rgbSwapped()
    return QPixmap(qImg)

def get_image_mask(img, blue_shade, diff): #apply the tracing process
    lower = np.array([max(0, val) for val in [blue_shade[2]-diff, blue_shade[1]-diff, blue_shade[0]-diff]], dtype=np.uint8)
    upper = np.array([min(255, val) for val in [blue_shade[2]+diff, blue_shade[1]+diff, blue_shade[0]+diff]], dtype=np.uint8)
    mask = cv2.inRange(img, lower, upper)
    percent_traced = np.sum(mask > 0) / (mask.shape[0] * mask.shape[1])
    return cv2.cvtColor(mask, cv2.COLOR_BGR2RGB), percent_traced

def pixelate(self, pixel_size):
        image = Image.open(self.source_file)
        image = image.resize((image.size[0] // pixel_size, image.size[1] // pixel_size),Image.NEAREST)
        image = image.resize((image.size[0] * pixel_size, image.size[1] * pixel_size),Image.NEAREST)
        #image.save(output_path)
        
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
        right_bottom= QHBoxLayout()
        right_layout.setSpacing(0)
        tabs.setFixedHeight(100)
        
        #Initial parameters
        self.source_file = None
        self.source_image_cv = None
        self.result_image_data = None
        self.escalated_image_data= None
        self.processed_image_data= None
        self.max_img_height= 400
        self.max_img_width= 600
        
        #first we define the buttons and link them to the functions that do the work.
    
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
        #Right_Menu ---< checkboxes
        tracing_box,scaling_box,enhancing_box = QCheckBox('Tracing'),QCheckBox('Scaling'),QCheckBox('Enhancing')
        for chbox,func in zip([tracing_box,scaling_box,enhancing_box],[self.tracing_image,self.Ratio,self.enhancer]):
            chbox.setFixedWidth(100)
            #chbox.setFont()
            chbox.setChecked(False)
            chbox.clicked.connect(func)
            right_menu.addWidget(chbox)
            
        right_layout.addLayout(right_menu)

        #Right_Tab1, parameters ---< It's where the parameters for the processing are
        def tab1(self):
            rgb_pane = QWidget(self)
            rgb_layout= QVBoxLayout()
            rgb_pane.setLayout(rgb_layout)
            rgb_param= QHBoxLayout()
            
            self.r_spinbox,self.g_spinbox,self.b_spinbox,self.threshold_spinbox = QSpinBox(),QSpinBox(),QSpinBox(),QSpinBox()
            self.r_slider,self.g_slider,self.b_slider,self.threshold_slider = QSlider(),QSlider(),QSlider(),QSlider()
                #Specify box and buttons characteristics.
            for start_val, prefix, spinbox in zip([100,100,100,80],[ 'R', 'G', 'B','Threshold'],
                                                [self.r_spinbox,self.g_spinbox,self.b_spinbox,self.threshold_spinbox]):
                spinbox.setPrefix(f'{prefix}:'),spinbox.setMinimum(0),spinbox.setMaximum(255),spinbox.setValue(start_val),spinbox.setFixedWidth(100)
            
            for start_val, slider in zip([100,100,100,80],[self.r_slider,self.g_slider,self.b_slider,self.threshold_slider]):
                slider.setMinimum(0), slider.setMaximum(255),slider.setValue(start_val),slider.setFixedHeight(70)
            for spinbox,slider in zip([self.r_spinbox,self.g_spinbox,self.b_spinbox,self.threshold_spinbox],
                        [self.r_slider,self.g_slider,self.b_slider,self.threshold_slider]):
                slider.valueChanged.connect(spinbox.setValue)
                spinbox.valueChanged.connect(slider.setValue)
                spinbox.valueChanged.connect(self.tracing_image)
                rgb_param.addWidget(spinbox)
                rgb_param.addWidget(slider)
            
            rgb_layout.addLayout(rgb_param)

            #Right_tab1_Processed Image ----<
            #self.result_image= ImageWidget()
            #self.result_image.setMaximumSize(self.max_img_width, self.max_img_height)
            #res_image.addWidget(QLabel('Result Image:'))
            #res_image.addWidget(self.result_image)
            #res_layout.addLayout(rgb_image)
            tabs.addTab(rgb_pane,'RGB_mask')
        tab1(self)
        
        #Right_Tab2, scale ----< Here, the size of the image can be modified according to different methods
        def tab2(self):
            scale_pane = QWidget(self)
            scale_layout= QVBoxLayout()
            scale_pane.setLayout(scale_layout)
            scale_param= QHBoxLayout()
            
            self.scaleNumber= QLabel()
            self.sliderScale= QSlider(Qt.Orientation.Horizontal)
            self.sliderScale.setMinimum(-20), self.sliderScale.setMaximum(20),self.sliderScale.setValue(1),self.sliderScale.setFixedWidth(300)
            self.sliderScale.valueChanged.connect(self.Ratio)
            scale_param.addWidget(QLabel('Scale Value: '))
            scale_param.addWidget(self.scaleNumber)
            scale_param.addWidget(self.sliderScale)
            scale_layout.addLayout(scale_param)
            
            tabs.addTab(scale_pane,'Scale')
        tab2(self)
        
        right_layout.addWidget(tabs)

        #Right processed Image. It depends on the checkboxes if the tabs affect it or not.
        self.result_image= ImageWidget()
        self.result_image.setMaximumSize(self.max_img_width, self.max_img_height)
        res_image.addWidget(QLabel('Result Image:'))
        res_image.addWidget(self.result_image)
        right_layout.addLayout(res_image)
        
        
        
        #Right_Bottom
        self.save_button= QPushButton('Save File')
        self.save_button.clicked.connect(self.recorder) #connects to the saving function
        self.save_button.setFixedWidth(100)
        self.result_image_shape= QLabel()
        self.percent_traced_label= QLabel()
        
        right_bottom.addWidget(self.result_image_shape,alignment=Qt.AlignmentFlag.AlignTop)
        right_bottom.addWidget(self.percent_traced_label,alignment=Qt.AlignmentFlag.AlignTop)
        right_bottom.addWidget(self.save_button,alignment=Qt.AlignmentFlag.AlignTop)
        right_layout.addLayout(right_bottom)
    
        #Aggregate all the layouts and their childs to define the MainWindow
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)
        
        widget= QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)
        
    def source_search(self):
        def path_validator():
            if self.source_path.text()!='':
                if os.path.exists(self.source_path.text()): self.source_file= self.source_path.text()
                else:
                    error_dialog= QErrorMessage()
                    error_dialog.showMessage('Image Path not valid.')
                    error_dialog.exec()
            else:
                self.source_file= QFileDialog.getOpenFileName()[0] #windows File explorer
        path_validator()
        self.source_image_cv= cv2.imread(self.source_file)
        self.original_image.setPixmap(pixmap_from_cv_image(self.source_image_cv))
        self.labelPath.setText(self.source_file)
        original_shape= self.source_image_cv.shape
        self.original_image_shape.setText(f'original shape: {original_shape}')
        
    def tracing_image(self):
        if self.source_image_cv is None:
            error_dialog= QErrorMessage()
            error_dialog.showMessage('No Image selected')
            error_dialog.exec()
        
        else:
            self.result_image_data, percent_traced = get_image_mask(self.source_image_cv,
                                                                   [self.r_spinbox.value(), self.g_spinbox.value(), self.b_spinbox.value()],
                                                                   self.threshold_spinbox.value())
            self.percent_traced_label.setText(f'Percent of image traced: {(percent_traced * 100):.3f}%')
            result_image_resized = resize_image(self.result_image_data, self.max_img_width, self.max_img_height)[0]
            self.result_image.setPixmap(pixmap_from_cv_image(result_image_resized))
            result_shape= resize_image(self.result_image_data, self.max_img_width, self.max_img_height)[2]
            self.result_image_shape.setText(f'Result shape: {result_shape}')

    def Ratio(self):
        def Rationum():
            if self.sliderScale.value()<0:return -1/self.sliderScale.value()
            elif self.sliderScale.value()>0: return self.sliderScale.value()
        divisor= Rationum()
        self.scaleNumber.setText(str(divisor))
        
    def enhancer(self):
        pass
    def recorder(self):
        if self.result_image_data is None:
            error_dialog = QErrorMessage()
            error_dialog.showMessage('No image processed')
            error_dialog.exec()
        else:
            out_file = QFileDialog.getSaveFileName(self, 'Save File')[0]
            if len(out_file) > 0: cv2.imwrite(out_file+'.png', self.result_image_data)
    
if __name__=='__main__':
    app = QApplication(sys.argv)

    imN= (R'C:\Users\user\Pictures\safescreen\Albedo_Skel.png')#,R'C:\Users\user\Pictures\safescreen\kieran.jpg')
    
    #DISPLAY RESULTS ###
    
    #MAIN WINDOW --->>
    if True:
        window = MainWindow()
        window.show()
        
        app.exec()   

