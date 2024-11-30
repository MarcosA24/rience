import os,sys
import pandas as pd
from pdfquery import PDFQuery
import Omni

def ExcelOpen(excelroute, sheet):
    xl= Omni.opSesame(excelroute, sheet=sheet, head=1)
    xl_heads= []
    for h in xl.columns: xl_heads.append(h)
    
    return xl, xl_heads

def ExcelExport(df, excel_route, hoja=''):
    with pd.ExcelWriter(excel_route) as writer:
        if hoja:
            df.to_excel(writer, sheet_name=hoja)
        else:
            df.to_excel(writer, sheet_name='pred1')
            
def PDFOpen(pdf_route,method='LTTextLineHorizontal'):
    pdf = PDFQuery(pdf_route)
    pdf.load()
    if method=='LTTextLineHorizontal':
        text_elements= pdf.pq(method)
        text= [t.text for t in text_elements]
        return text
        
def Exchange_gpd(source, out_folder, ext='', layer='',out_gpkg=''): #export data between gpkg, shp, JSON, csv, xlsx, 
    #ext refers to the file extension we want for the output. '.shp','.json','.gpkg'
    #layer is in case we only want to work with a layer of a source geopackage
    #out_gpkg is only in case we want to import a new layer into an already existing geopackage. we must write the extension here
    if not ext.startswith('.'): ext='.'+ext
    if os.path.isdir(out_folder): pass          #check if there's a folder with the name, and if not it creates one
    else: os.mkdir(out_folder)

    def Driver(ext):
        #print(fiona.supported_drivers)
        if ext=='.shp': return 'ESRI Shapefile'
        elif ext=='.gpkg': return 'GPKG'
        elif ext=='.json': return 'GeoJSON'
        #elif ext=='.dxf' : return 'DXF'
        #elif ext=='.dgn' : return 'DGN'
        #elif ext=='.gpx' : return 'GPX'

    if not layer:
        for ly in fiona.listlayers(source):
            l= geopandas.read_file(source,layer=ly)
            if ext in ('.csv','.xlsx'): 
                print(l.columns)
                l["wkt"]= l.apply(lambda row:row['geometry'].wkt, axis=1)
                l = l.drop(columns=['geometry'])
                if ext=='.xlsx': ExcelExport(l,out_folder+'/'+layer+ext)
                elif ext=='.csv': l.to_csv(out_folder+'/'+layer+ext,sep=' ',header=True)
            else: 
                if ext!='.gpkg': l.to_file(out_folder+'/'+layer+ext,driver=Driver(ext))
                elif ext=='.gpkg': l.to_file(out_folder+'/'+out_gpkg,driver=Driver(ext),layer=ly)

    else:
        l= geopandas.read_file(source,layer=layer)
        if ext in ('.csv','.xlsx'):
            l["wkt"]= l.apply(lambda row:row['geometry'].wkt, axis=1)       #csv and excel don't accept spatial data, and so we do this step to make the geometry data into a WKT, to fit in the format capabilities
            l = l.drop(columns=['geometry'])                                 #and the geometry column is eliminated to avoid problems
            if ext=='.xlsx': ExcelExport(l,out_folder+'/'+layer+ext)
            elif ext=='.csv': l.to_csv(out_folder+'/'+layer+ext,sep=' ',header=True)
        else: 
            if ext!='.gpkg': l.to_file(out_folder+'/'+layer+ext,driver=Driver(ext))
            elif ext=='.gpkg': l.to_file(out_folder+'/'+out_gpkg,driver=Driver(ext),layer=layer)

def stats(df,graphic='',x='',y=[],ax='',stacked=False,row=''): #extracts the stats of a dataframe
    if ax=='':
        fig, ax = plt.subplots(figsize = (8,8))
    #graphic in ('line', 'bar', 'barh', 'kde', 'density', 'area', 'hist', 'box', 'pie', 'scatter', 'hexbin')
    # Y can be a list of values, and they will be plotted together
    def checkDF(df): #in case it's a geopandas gdf, convert into pandas df
        fields= [c for c in y]
        fields.append(x)
        if type(df)== geopandas.geodataframe.GeoDataFrame:
            df= pd.DataFrame(df[fields])
            return df
        else: return df
    df= checkDF(df)
    if graphic in('bar','barh'): df.plot(x,y,kind=graphic,ax=ax,stacked=stacked)
    elif graphic=='line': df.plot(x,y,kind=graphic,ax=ax)
    elif graphic=='scatter': df.plot(x,y,kind=graphic,ax=ax) #requires x,y coordinates to plot
    elif graphic=='pie':
        if not row=='': df.loc[row].plot.pie(y=y) #row is the iD row for which the pie chart will be made
        elif row=='': df.plot.pie(subplots=True) #plot the pie chart for an entire column
