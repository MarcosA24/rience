#a collection of useful functions that can be applied in PyQGIS, to automatize processes
import sys,os
import pandas as pd
import Omni



def getFields(source,lyname=''):
    def getSc(source,lyname=''):
        #lyname must be a list, even if it's only 1 layer
        if source=='layer_name': #by calling the name, then marking with instance
            if len(lyname)==1: ly= QgsProject.instance().mapLayersByName(lyname[0])[0]
            elif len(lyname)>1: 
                ly=[]
                for l in lyname: 
                    layer= QgsProject.instance().mapLayersByName(l)[0]
                    print(layer.name)
                    ly.append(layer)
            return ly
        elif source =='activeLayer': #or by choosing the current active layer
            ly= iface.activeLayer()
            return ly
        elif source=='externalFile': #by choosing an external file, not necessarily uploaded in the QGIS map
            ly = QgsVectorLayer(".shp", "airports", "ogr")
            return ly
    layers= getSc(source,lyname)
    df= pd.DataFrame({'layer':[],'field':[],'type':[],'values':[]})
    
    if type(layers)==list:
        if True: #to get the attribute fields names
            for l in layers:
                for field in l.fields(): 
                    #print(field.name(), field.typeName())
                    nrow={'layer':l.name(),'field':field.name(),'type':field.typeName()}
                    df.loc[len(df)] = nrow
                    df = df.reset_index(drop=True)
        if False: #to get all the geometries(features), and work with them
            for l in layers: 
                for feat in l.getFeatures(): print(feat)                
    elif type(layers)!=list:
        l=layers
        if True: #to get the attribute fields names
            for field in l.fields(): 
                #print(field.name(), field.typeName())
                nrow={'layer':l.name(),'field':field.name(),'type':field.typeName()}
                df.loc[len(df)] = nrow
                df = df.reset_index(drop=True)
        if False: #to get all the geometries(features), and work with them
            for feat in l.getFeatures(): print(feat)     
    return df
