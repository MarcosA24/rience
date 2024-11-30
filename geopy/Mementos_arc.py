import os,sys
#arcpy only works with the interpreted installed inside the ArcGis Pro. version 3.9.18
sys.path.insert(./Aureum)
import arcpy
import pandas as pd
import Omni
from Mementos_au import ExcelOpen, ExcelExport

def OpenProject(aprx_route):
    #returns a dictionary with layers grouped by the map they're in.
    glob_layers={}
    nom_layers={}
    maps = aprx.listMaps()
    for map in maps:
        layers= map.listLayers()
        glob_layers[map.name]= layers
        map_layers=[]
        for layer in layers:
            map_layers.append(layer.name)
        nom_layers[map.name]= map_layers
    return glob_layers, nom_layers

def GetFields(fc):#extracts the fields of a feature class
    featureFields = arcpy.ListFields(fc)
    fcFields = []
    for field in featureFields:
        fcFields.append(field.name)
        
        #if instead of field.name you append field, all the object will be appended.
        #print(f"{field.name} has a type of {field.type} with a length of {field.length}")
    return fcFields

def getGDB(input_gdb): #get the files stored in a gdb
    gdb_list= []
    arcpy.env.workspace= input_gdb
    fc_list=  arcpy.ListFeatureClasses()
    rast_list= arcpy.ListRasters()
    if fc_list:
        for fc in fc_list: gdb_list.append(fc)
    if rast_list:
        for r in rast_list: gdb_list.append(r)
    return gdb_list

def checkGDB(output_folder, output_gdb): #checks if there's an existing file gdb with same url. 
    if not output_gdb.endswith('.gdb'):      
        output_gdb= output_gdb+'.gdb'
        if output_folder:
            output_gdb= output_folder+'\\'+output_gdb
            return output_gdb
        else: return output_gdb
    else: 
        if output_folder:
            output_gdb= output_folder+'\\'+output_gdb
            return output_gdb
        else: return output_gdb

def checkGPKG(output_folder, output_gpkg): #checks if there's a geopackage (sqlite3 database) in the route
    if not output_gpkg.endswith('.gpkg'):      
        output_gpkg= output_gpkg+'.gpkg'
        if output_folder:
            output_gpkg= output_folder+'\\'+output_gpkg
            return output_gpkg
        else: return output_gpkg
    else: 
        if output_folder:
            output_gpkg= output_folder+'\\'+output_gpkg
            return output_gpkg
        else: return output_gpkg

def exportRaster(env, output_folder):  #exort raster files from a gdb into a folder
    arcpy.env.workspace= env
    gdb_rasters= arcpy.ListRasters()
    raster_folder= output_folder+'\\rasters'
    if os.path.isdir(raster_folder): pass
    else: os.mkdir(raster_folder)

    for r in gdb_rasters:
        arcpy.management.CopyRaster(r,raster_folder+'\\'+r+'.tif',None,None,-9999,None,None,'32_BIT_FLOAT',None,None,'TIFF',None)

def raster_intoGpkg(environment, gpkg):
    #environment és la ruta del projecte, o el directori, o la .gdb on estan les capes rasters
    #gpkg és el geopackage de sortida
    #introdueix capes raster en un geopackage JA EXISTENT.
    #El geopackage s'ha de crear amb el QGis
    arcpy.env.workspace= environment
    rast_list= arcpy.ListRasters()

    if len(rast_list)!=0:
        for raster in rast_list:
            nom= raster.encode('ascii','ignore')    #passem del unicode que dona el ListRaster a una string, per definir el nom
            print(nom)
            #properties= arcpy.GetRasterProperties_management(raster,'')
            arcpy.AddRasterToGeoPackage_conversion(raster,gpkg, nom)

def gdb_to_gpkg(env, output_folder, nom_gpkg): #clone a gdb into a geopackage. vector layers only
    arcpy.env.workspace= env
    fcs= arcpy.ListFeatureClasses()
    output_gpkg= checkGPKG(output_folder, nom_gpkg)
    if os.path.isfile(output_gpkg) == False:
        arcpy.management.CreateSQLiteDatabase(output_gpkg,'GEOPACKAGE_1.3' )
        for fc in gdb_features:
            arcpy.management.CopyFeatures(output_gdb+'\\'+fc,output_gpkg+'\\'+fc)
    print('GPKG creat')       


#prepared to be made as a tool in arcgisPro
def setName(environment, nom_gdb, output_folder='',map_name=''): #rename files in a geodatabase in the order that they are in the original source(.gdb / .aprx)
    #l'environment és l'entorn del que surten les dades originalment. pot ser o (.gdb) o (.aprx)
    #output_gdb demana el nom de la ruta de sortida de la geodatabase resultant   
    output_gdb= checkGDB(output_folder, nom_gdb)
    arcpy.CreateFileGDB_management(output_folder,nom_gdb)
    if os.path.isfile(output_gdb) == False:
        new_list= []

        if environment.endswith('.gdb'):
            arcpy.Copy_management(environment, output_gdb)
            gdb_list= getGDB(output_gdb)
            new_list= gdb_list
            
        elif environment.endswith('.aprx'):           
            aprx= arcpy.mp.ArcGISProject(environment)
            #print('Default geodatabase:',type(aprx.defaultGeodatabase))
            #arcpy.Copy_management(aprx.defaultGeodatabase, output_gdb)  
            if map_name=='': map = aprx.listMaps()[0]
            else: map = aprx.listMaps(map_name)[0]
            layers= map.listLayers()
            arcpy.env.workspace= aprx.defaultGeodatabase
            for fc in arcpy.ListFeatureClasses():
                print(fc)
                for lyrx in layers: 
                    if lyrx.isFeatureLayer or lyrx.isRasterLayer:
                        if lyrx.name==fc:
                            print(lyrx.name)
                            new_list.append(lyrx.name)
                            arcpy.conversion.FeatureClassToGeodatabase(fc,output_gdb)
                    elif lyrx.isBasemapLayer: continue

            gdb_list= getGDB(aprx.defaultGeodatabase)
            #export layer package of many layers
            #if map_name!='': arcpy.PackageLayer_management(layers, output_folder+'\\'+map_name+'.lpkx')
            #else: arcpy.PackageLayer_management(layers, output_folder+'\\'+nom_gdb+'.lpkx')
        
        def renameLayers(env, gdb_list, new_list):
        #with the given environment and the list of files inside gdb, we can rename the layers by their order
        #renames the layers of the gdb according to the order of these layers in the new_list. they must have the same name in both lists to be changed
        gdb_list= getGDB(aprx.defaultGeodatabase)
        n=0
        for i in new_list:
            for file in gdb_list:
                if i == file:
                    n+=1
                    if n<10: arcpy.Rename_management(file, '_0'+str(n)+'_'+file)    #print('New FC:', '_0'+str(n)+'_'+i)
                    else: arcpy.Rename_management(file, '_'+str(n)+'_'+file)        #print('New FC:', '_'+str(n)+'_'+i)

        arcpy.env.workspace= output_gdb
        print('Llista de la geodatabase:\n',gdb_list)
        print('Nova_Llista:\n',new_list)
        
        renameLayers(env= output_gdb, gdb_list, new_list)
        exportRaster(output_gdb, output_folder)
        gdb_to_gpkg(output_gdb, output_folder)

    else: print('GDB ',output_gdb, ' already exists')


def shp2_excel(shp, out_fields, out_excel): #get the info of a shape into a dataframe
        fields= GetFields(shp)
        att= arcpy.Describe(shp)
        print(u'{0},\n {1}'.format(att.name, fields))
        df= pd.DataFrame({out_fields[0]:[], out_fields[1]:[], out_fields[2]:[], out_fields[3]:[], out_fields[4]:[], out_fields[5]:[], out_fields[6]:[], out_fields[7]:[]})
        if True:
            with arcpy.da.SearchCursor(shp,field_names=out_fields) as cursor:
                i=-1
                for row in cursor:
                    i+=1
                    #change the pd.series name to extract attributes of layer
                    df.loc[i] = pd.Series({out_fields[0]: row[0], out_fields[1]:row[1], out_fields[2]:row[2], out_fields[3]:row[3], out_fields[4]:row[4], out_fields[5]:row[5], out_fields[6]:row[6], out_fields[7]:row[7]})
                    #print(u'{0}, {1}'.format(row[0], row[2]))
                    if i>10: break
                    
            codes= pd.Series({c: df[c].unique() for c in df})
            #print(df[:])
            #print(codes[:])

            #ExcelExport(df,R'C:\Users\Downloads')

def fc_inspect(wkspace): #returns all the geometries stored in a feature class, inside a pandas Dataframe
    arcpy.env.workspace= wkspace
    shp_list= arcpy.ListFeatureClasses()
    #To do: make automatically that it recognizes the fields, the headings, and it can be done instantly without specifying the head name of each column
    lyr_bp= pd.DataFrame({'OBJECTID':[],'IDABS':[],'CODI_CAS':[],'EPI_PUB':[],'DESCR_PROT':[],'ERA':[],'PERIODE':[],'EPOCA':[]})
    lyr_qp= pd.DataFrame({'OBJECTID':[],'IDABS':[], 'CODI_CAS':[], 'EPI_PUB':[], 'DESCRIPCIO':[], 'TIPUS_DIP':[], 'ERA':[], 'PERIODE':[], 'EPOCA':[]})

    #for shp in shp_list:
    shp2_excel(shp_list[0],out_fields=['OBJECTID','IDABS','CODI_CAS','EPI_PUB','DESCR_PROT','ERA','PERIODE','EPOCA'], 
               out_excel=R'C:\Users\becari.alex.marcos\OneDrive - Institut Cartogràfic i Geològic de Catalunya\basament.xlsx')

def ExportLayout(output_folder): #it only works when the environment is set to be the current project, so it must be used in the arcpy notebook
    aprx = arcpy.mp.ArcGISProject("CURRENT")
    for lyt in aprx.listLayouts():
        #lyt.exportToPDF(os.path.join(r"C:\Users\becari.alex.marcos\Documents\ArcGIS\Projects\Geologia_Visor", f"{lyt.name}"), clip_to_elements=False, compress_vector_graphics=False)
                    #output_as_image=True, jpeg_compression_quality=90, resolution=300 )
        lyt.exportToPNG(os.path.join(output_folder, f"{lyt.name}"),resolution =300, transparent_background=False)
        print(lyt.name)
        
        lyt.exportToSVG(os.path.join(output_folder, f"{lyt.name}"),resolution=300)
        print(done)

def synth_arcdf(shp,fields=''):
    #creates a df from a shp table
    if fields=='': fields= GetFields(shp)
    else: pass
    table=[]
    with arcpy.da.SearchCursor(shp,fields) as cursor:
        for row in cursor:
            table.append(row)
    df= pd.DataFrame(table,columns=fields)
