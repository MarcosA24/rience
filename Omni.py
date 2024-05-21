import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
from pdf2docx import parse

def pdf_docx(file):
    # transforms pdf to a word, or viceversa, depending on the input type of file
    if file.endswith('.pdf'):
        word= file.replace('.pdf','.docx')
        f= parse(file, word)
        return f
    elif file.endswith('.docx'):
        pass
    
def wordIns(file, word):
    with open(file, 'r') as ori:
        for horn in ori.readlines():            
            horn=horn.replace(',','',-1)
            hornL=horn.split()
            head= hornL[0]
            for c in horn:       
                if head == word:
                    if len(hornL) <2:
                        head = (word,'No Index')
                        break
                    elif len(hornL) >=2: 
                        zane = int(hornL[2])
                        Kel= '%4d' %(zane)
                        return Kel
                else: 
                    break

def csvIns(file,word):
    with open(file, 'r') as ori:
        for horn in ori.readlines():        
            hornL=horn.split()
            head= hornL[0]
            if head == word:
                if len(hornL) == 2: 
                    zane = float(hornL[1])
                    Kel= '%4d' %(zane)
                    return Kel
                else: 
                    return (word,'No Index')

def doHisto(ig='',size=''):
    #the size parameter is the shape of the image.we will use those for later
    #definir els histogrames abans del bucle de les 3 bandes
    histo=cv2.calcHist([ig],[0],None,[256],[0,256])
    histo= [int(i) for i in histo]
    fig,ax= plt.subplots(1,3,figsize=(12,4))
    #paleta de colors per cambiar els gràfics
    raoul= ['blue','green','red','blue','gray','purple']

    for b in range(size[2]):
        histo[b]= cv2.calcHist([ig[b]],[0],None,[256],[0,256])
        x= [int(i) for i in range(256)]
        sea= b

        x_data= np.reshape(x,(len(histo[b]),))
        y_data= np.reshape(histo[b],(len(histo[b]),))
        
        ax[sea].bar(x_data,y_data,color= raoul[b])
        ax[sea].set_title('band'+str(b+1))


#open any kind of file with pandas
def opSesame(route,separator='',sheet='',head=''):
    if route.endswith('.txt') or route.endswith('.ASC'):
        estadillo= pd.read_csv(route,sep=separator,header=[0],index_col=None)
        
        if False: 
            ccl = input('Estación Leica UPC? y/n')
            if ccl=='y':
                estadillo= estadillo.replace('<not defined>','NaN', regex=True)
                #erase automatically the spaces. can be done manually in txt with find/replace '  ' for ' '.
                #estadillo= estadillo.replace('  ',' ', regex=True)
            else: pass
        
        ccl2= input('float character in file: (, or .)')
        if ccl2==',':
            estadillo= estadillo.replace(',','.', regex=True)
        else: pass
        
        return estadillo
    
    elif route.endswith('.xlsx'):
        if not sheet:
            sheet= input('Sheet_Name: ')
        if not head:
            head= int(input('Nºlines of headers(int)'))
        headers=[]
        for r in range(head):
            headers.append(r)
        estadillo= pd.read_excel(route,sheet_name=sheet,header=headers,names=None)
        estadillo= estadillo.replace(',','.', regex=True)
        return estadillo
    else:
        print('File type does not exist')
        pass

#Pandas tutorials:

#pandas create dataframe
    #https://www.geeksforgeeks.org/different-ways-to-create-pandas-dataframe/
#pandas indexing
    #row indexing: estadillo.loc[0])  
    #col indexing:estadillo[['Estacion','PuntoVisado']]) 
    #print(trigEst.loc[0]['Slope']) 
#Pandas iterate over rows. -> 
            #for index, row in df.iterrows():
                #print(row['c1'], row['c2'])
                #print(dex.loc[index]['c1'])
#Pandas iterate over columns:| 
            #for column in dLect.columns:
                #print(dLect[column])
#pandas to numpy array specific column:
#column_to_numpy = df['col1'].to_numpy()
#pandas change type of a column(2 options):
    #estadillo= estadillo.astype({'ESPALDA':float,'FRENTE':float})
    #estadillo[['ESPALDA', 'FRENTE']] = estadillo[['ESPALDA', 'FRENTE']].apply(pd.to_numeric)
#pandas export df to excel:
    #with pd.ExcelWriter('C:/Users/Usuario/Documents/Crossroads/AjustesRed/Nivel_pr.xlsx') as writer:
        #nivEst.to_excel(writer)
#pandas dataframe sort:
    #df.sort_values(by=['column'], ascending='True/False' , na_position= 'first'/'last')
    #natural sort with the key argument ; key =lambda x: np.argsort(index_natsorted(df['column']))
#pandas replace values:
    # for column
        #df['column'] = df['column'].replace(np.nan, 0)
    # for whole dataframe
        #df = df.replace(np.nan, 0)
    # inplace
        #df.replace(np.nan, 0, inplace=True)
#pandas insert new rows:
    #df.loc['col'] = pd.Series({'c1':1, 'c2':5, 'c3':2})
#pandas get unique values of a whole dataframe, specifying each column: 
    #tp= pd.Series({c: df[c].unique() for c in df})
    
# ----------------PDF edition
#merge differents pdfs. 
    #from PyPDF2 import PdfFileReader, PdfMerger
    #pdfs = ['file1.pdf', 'file2.pdf']
    #merger = PdfMerger()
    #merger.append(pdfs[1], pages=(0,1))
    #merger.append(pdfs[0], pages=(0,4))
    #merger.append(pdfs[1], pages=(1,2))
    ##merger.write( R'E:\Universidad Alex\Cursos\obras\batch2_curvasCirc_MMA.pdf')
    #merger.close()
