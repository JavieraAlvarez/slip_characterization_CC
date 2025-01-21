#########################################
# tsunami model with deformation data.  #
# Based on Cifuentes-Lobos et al. (2023)#
#########################################

import Tkinter,tkFileDialog
from tkinter import *
from tkinter import ttk
import subprocess
import os
import glob
import shutil 
import sys
import json
import numpy as np
import pandas as pd
import modokada as mo 
import modfallas as mf 
import modrestricciones as mr
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from scipy.interpolate import RegularGridInterpolator, interp1d, interp2d ,griddata, Rbf
from geographiclib.geodesic import Geodesic
from formato_comcotctl import crea_comcotctl
import gc 

gc.collect()



# path to constrain data

ruta_deformaciones = "/fallas/modelos_restringidos/csv_files"
dir_destino        = "/ctl_tsunami"
dir_comcot         = "/ctl_tsunami"
dir_modelacion     = "tsunami"
dir_grillas        = "grillas_comcot"
dir_actual         = os.getcwd()     # main patch 


"""
list
"""
os.chdir(ruta_deformaciones)
# npz files
lista_def  = glob.glob("deformacion*.csv") # list of arrays: deformation and coordinates
lista_def.sort(key=os.path.getctime)     
lista_slip = glob.glob("slip*.csv")   
lista_slip.sort(key=os.path.getctime) 

print("%s archivos de fallas leidos") %(len(lista_def))

"""
GRID SELECTION
"""

def seleccion_grillas():
    os.chdir(dir_grillas)
    root = Tkinter.Tk()
    grillas_seleccion = tkFileDialog.askopenfilenames(parent=root,multiple=True,title='Elija las grillas')
    lista_grillas  = list(grillas_seleccion) # list
    largo_ruta_grillas = len(dir_grillas) + 1 # size of strings
    lista_nombre_grillas = []
   
    for grilla in lista_grillas:
        nombre_grilla = grilla[largo_ruta_grillas:].strip()
        lista_nombre_grillas.append(nombre_grilla)
    root.destroy()
    print("%s grillas seleccionadas ") %(len(lista_nombre_grillas))
    print("")
    print(lista_nombre_grillas)
    return lista_nombre_grillas

print("Seleccionar grillas")
lista_nombre_grillas = seleccion_grillas()
decision_grillas = raw_input("Confirmar seleccion? [s/n]: ")
while decision_grillas == "n":
    seleccion_grillas()
    decision_grillas = raw_input("Confirmar seleccion? [s/n]: ")
if decision_grillas == "s":
    print("%s grillas correctamente seleccionadas: ") %(len(lista_nombre_grillas))
    print("")
    print(lista_nombre_grillas)
def limites_grillas(dir_grillas, lista_nombre_grillas):
    """
    INPUT:
    dir_grillas: path of original grids
    lista_nombre_grillas: new list of grids
    """
    # search for the grid boundaries
    ruta_grillas = []
    for grilla in lista_nombre_grillas:
        ruta = dir_grillas+"/"+grilla
        ruta_grillas.append(ruta)
    n_grillas = len(ruta_grillas)

    # array of 2x2xn_grillas array_limites
    array_limites = np.ones((2,2,n_grillas)) # init
    c = 0
    for grilla in ruta_grillas:
        x,y = np.loadtxt(grilla,usecols=(0,1), unpack=True)
        xmin = x.min()
        if xmin > 0:
            x -= 360.
        lonmin = x.min()
        array_limites[0,0,c] = lonmin
        lonmax = x.max()
        array_limites[0,1,c] = lonmax
        latmin = y.min()
        array_limites[1,0,c] = latmin
        latmax = y.max()
        array_limites[1,1,c] = latmax
        c += 1
    return array_limites


# grid resolution
def resolucion_grillas(dir_grillas, lista_nombre_grillas):
    """
    INPUT:
    dir_grillas: path of original grids
    lista_nombre_grillas: new list of grids
    """

    ruta_grillas = []
    for grilla in lista_nombre_grillas:
        ruta = dir_grillas+"/"+grilla
        ruta_grillas.append(ruta)
    n_grillas = len(ruta_grillas)

    # save in array_resolucion
    array_resolucion = np.ones((n_grillas))
    c = 0
    for grillas in ruta_grillas:
        x = np.loadtxt(grillas,usecols=(0), unpack=True)
        dif = round((x[1]-x[0])*60,3)
        array_resolucion[c] = dif
        c += 1
    
    return array_resolucion


# first view function
def grafica_mapa_grillas(dir_grillas, lista_nombre_grillas,flag_res = True):
    ruta_grillas = []
    for grilla in lista_nombre_grillas:
        ruta = dir_grillas+"/"+grilla
        ruta_grillas.append(ruta)
    n_grillas = len(ruta_grillas)

    fig = plt.figure()
    ax  = fig.add_subplot(111)
    map = Basemap(llcrnrlon=-84,llcrnrlat=-55,urcrnrlon=-66.,urcrnrlat=-17.,
             resolution='l', projection='merc')
    map.drawmapboundary(fill_color='#A6CAE0')
    map.fillcontinents(color='#e6b800',lake_color='#A6CAE0')
    map.drawparallels(np.arange(-50.,-15.,10.))
    map.drawmeridians(np.arange(-80.,-66.,4.))
    map.drawcountries(color="white")
    map.drawcoastlines()

    array_limites    = limites_grillas(dir_grillas, lista_nombre_grillas)

    #
    def dibuja_rectangulo_grilla(lons, lats, map, num_grilla):
        """
        INPUT:
        lons: lon [left left right right]
        lats:  [inf sup sup inf]
        map: basemap
        num_grilla: grid id
        """

        x, y = map(lons,lats)
        xy   = zip(x,y)
        rectangulo = Polygon(xy , facecolor = 'blue', alpha = 0.4, edgecolor = 'k', linewidth = 2 )
        plt.gca().add_patch(rectangulo)
        xid, yid = map(lons[-1], lats[1])
        id_str   = str(num_grilla)
        plt.annotate(id_str, xy=(xid,yid), weight = 'bold', xycoords='data', xytext=(xid,yid), textcoords='data')

    array_resolucion = resolucion_grillas(dir_grillas, lista_nombre_grillas)
     #
    if flag_res:
        def anota_resoluciones(map, num_grilla, array_resolucion):
            x, y = 1.2, 0.9-(num_grilla-1)*0.05
            resolucion = str(num_grilla) + ": " + str(array_resolucion[num_grilla-1]) + "'"
            plt.annotate(resolucion, xy=(x,y), weight = 'bold', xycoords='axes fraction', xytext=(x,y), textcoords='axes fraction')
            xtitle, ytitle = 1.2, 0.95
            plt.annotate("Res. grillas", xy=(xtitle,ytitle), weight = 'bold', xycoords='axes fraction', xytext=(xtitle,ytitle), textcoords='axes fraction')

    c_id = 1
    for i in range(n_grillas):
        lons = [array_limites[0,0,i], array_limites[0,0,i], array_limites[0,1,i], array_limites[0,1,i] ]
        lats = [array_limites[1,0,i], array_limites[1,1,i], array_limites[1,1,i], array_limites[1,0,i] ]
        dibuja_rectangulo_grilla(lons, lats, map, c_id)
        anota_resoluciones( map, c_id, array_resolucion)
        c_id += 1
    
    plt.show()

print("graficando...")

grafica_mapa_grillas(dir_grillas, lista_nombre_grillas)

decision_grillas2 = raw_input("Confirmar seleccion? [s/n]: ") #yes/no
# ask again
while decision_grillas2 == "n":
    seleccion_grillas()
    decision_grillas2 = raw_input("Confirmar seleccion? [s/n]: ")
if decision_grillas2 == "s":
    print("%s grillas correctamente seleccionadas: ") %(len(lista_nombre_grillas))
    print("Archivos:")
    print(lista_nombre_grillas)

"""
TS_LOCATION.DAT
"""
# tide gauge
def crea_tslocations_mapa(dir_grillas, lista_nombre_grillas):
    """
    INPUT:
    dir_grillas: path of original grids
    lista_nombre_grillas: new list of gridss
    """

    main = Tk()
    main.title("Seleccionar grillas")
    main.geometry("300x400")
    frame = ttk.Frame(main, padding=(3, 3, 12, 12))
    frame.grid(column=0, row=0, sticky=(N, S, E, W))

    valores = StringVar()
    valores.set(lista_nombre_grillas)

    lstbox = Listbox(frame, listvariable=valores, selectmode=MULTIPLE, width=35, height=30)
    lstbox.grid(column=0, row=0, columnspan=2)

    def seleccionar():
        lista_seleccionada = list()
        lista_seleccionada = [lstbox.get(i) for i in lstbox.curselection()]
        seleccionar.seleccion = lista_seleccionada
        main.destroy()

    btn = ttk.Button(frame, text="Seleccionar", command=seleccionar)
    btn.grid(column=1, row=1)

    main.mainloop()

    n_seleccion = len(seleccionar.seleccion)
    # selection
    lista_grillas_seleccionadas = []
    for i in range(n_seleccion):
        lista_grillas_seleccionadas.append(seleccionar.seleccion[i][:].split("'")[1])

    print(lista_grillas_seleccionadas)

    #  allows the user to enter virtual tide gauge locations either manually or through a graphical interface, verifies that they are within at least one grid.
    ruta_grillas = []
    for grilla in lista_grillas_seleccionadas:
        ruta = dir_grillas+"/"+grilla
        ruta_grillas.append(ruta)

    array_limites = limites_grillas(dir_grillas, lista_grillas_seleccionadas)

    print("graficando...")

    def onclick(event):
        global ix, iy
        global coords
        ix, iy = event.xdata, event.ydata
        #print 'x = %d, y = %d'%(ix, iy)
        coords.append((ix, iy))
        return coords
    
    lonts_aux = []
    latts_aux = []
    lonts     = []
    latts     = []
    n_clicks  = 0

    for i in range(n_seleccion):
        # map
        fig = plt.figure()
        ax  = fig.add_subplot(111)
        map = Basemap(llcrnrlon=array_limites[0,0,i], llcrnrlat=array_limites[1,0,i],
                        urcrnrlon=array_limites[0,1,i],urcrnrlat=array_limites[1,1,i],
                        resolution='h', projection='merc')
        map.drawmapboundary(fill_color='#A6CAE0')
        map.fillcontinents(color='#e6b800',lake_color='#A6CAE0')
        map.drawcountries(color="white")
        map.drawcoastlines()
        x, y = 0.3, 1.05
        titulo_grilla = lista_grillas_seleccionadas[i].split(".")[0]
        plt.annotate(titulo_grilla, xy=(x,y), weight = 'bold', 
            xycoords='axes fraction', xytext=(x,y), textcoords='axes fraction')
        cid = fig.canvas.mpl_connect('button_press_event', onclick)
        plt.show()
        for i in range(n_clicks,len(coords)):
            lonts_aux.append( map(coords[i][0], coords[i][1], inverse = True)[0])
            latts_aux.append( map(coords[i][0], coords[i][1], inverse = True)[1])
        lonts.append(lonts_aux)
        latts.append(latts_aux)
        lonts_aux, latts_aux = [], []
        n_clicks = len(coords)
        fig.canvas.mpl_disconnect(cid)
    return lonts, latts, lista_grillas_seleccionadas

#  create_tslocations_map
def guardar_tslocations(lonts, latts, dir_destino, dir_grillas ,lista_grillas_seleccionadas, flag_mapa = 0):
    """
    INPUT
    lonts: tide gauge lon
    latts: tide gauge lat
    dir_destino: output tide gauge path
    dir_grillas: output grid path 
    lista_grillas_seleccionadas: names of grids
    flag_mapa: switch to map [1] or not [0] (by defect)
    """

    if flag_mapa:
        ruta_grillas = []
        for grilla in lista_grillas_seleccionadas:
            ruta = dir_grillas+"/"+grilla
            ruta_grillas.append(ruta)
        n_grillas = len(ruta_grillas)

        array_limites = limites_grillas(dir_grillas, lista_grillas_seleccionadas)

        for i in range(n_grillas):
            fig = plt.figure()
            ax  = fig.add_subplot(111)
            map = Basemap(llcrnrlon=array_limites[0,0,i], llcrnrlat=array_limites[1,0,i],
                            urcrnrlon=array_limites[0,1,i],urcrnrlat=array_limites[1,1,i],
                            resolution='h', projection='merc')
            map.drawmapboundary(fill_color='#A6CAE0')
            map.fillcontinents(color='#e6b800',lake_color='#A6CAE0')
            map.drawcountries(color="white")
            map.drawcoastlines()
            x, y = 0.3, 1.05
            titulo_grilla = lista_grillas_seleccionadas[i].split(".")[0]
            plt.annotate(titulo_grilla, xy=(x,y), weight = 'bold', 
                xycoords='axes fraction', xytext=(x,y), textcoords='axes fraction')
            xi, yi = [], []
            for j in range(len(lonts[i])):
                xi.append(map(lonts[i][j], latts[i][j])[0])
                yi.append(map(lonts[i][j], latts[i][j])[1])
                map.plot(xi[j], yi[j], marker = 'v', color = 'r')
            plt.show()

    # output
    ts = open("ts_location.dat","a")
    for i in range(len(lonts)):
        for j in range(len(lonts[i])):
            ts.write(str(lonts[i][j]) + " " + str(latts[i][j]) + "\n")
    ts.close()


    

# select ts_locations (if exist)
def buscar_ts_locations():
    root = Tkinter.Tk()
    ts_seleccion = tkFileDialog.askopenfilenames(parent=root,title='Escoja archivo ts_locations.dat'
                    ,filetypes=(("archivos dat","*.dat"),("todos los archivos","*.*")))
    root.destroy()        
    return ts_seleccion

coords = []
decision_ts = raw_input("Desea agregar ts? [s/n] ")
if decision_ts == "s":
    flag_ts = True
    decision_ts2 = raw_input("Seleccionar archivo ts_locations.dat existente [1] o elegir ubicaciones en el mapa [2]: ")
    if decision_ts2 == "1":
        buscar_ts_locations()
    elif decision_ts2 == "2":
        lonts, latts, lista_grillas_seleccionadas = crea_tslocations_mapa(dir_grillas, lista_nombre_grillas)
        decision_visualizacion_ts = raw_input("Visualizar ubicaciones de mareografos? [s/n] ")
        if decision_visualizacion_ts == "s":
            flag_ts = 1
        else:
            flag_ts = 0
        guardar_tslocations(lonts, latts, dir_destino, dir_grillas, lista_grillas_seleccionadas, flag_mapa = flag_ts)
    decision_ts3 = raw_input("Desea guardar ts [1] o ts y Zmax [2]? ")
    if decision_ts3 == "1":
        salidas_gral = 1
    elif decision_ts3 == "2":
        salidas_gral = 2
    shutil.copy("ts_locations.dat",dir_destino)
    print("ts_locations.dat copiado a directorio de destino")
    



"""
main files (control files)
"""
print("creando archivos de control de COMCOT y archivos de entrada de def.")
for arc_def in lista_def:
    if flag_ts:
        crea_comcotctl(arc_def, ruta_deformaciones, lista_nombre_grillas, salidas_gral=salidas_gral)
    else:
        crea_comcotctl(arc_def, ruta_deformaciones, lista_nombre_grillas)
    def_if = str(arc_def.split("_")[1].split(".")[0])
    nombre_archivo_ctl = "comcot_"+def_if+".ctl"
    nombre_archivo_xyz = arc_def.replace("csv","xyz")
    shutil.move(nombre_archivo_ctl, dir_destino)
    shutil.move(nombre_archivo_xyz, dir_destino)
    print("modelo numero %s listo") %(def_if)

print("creacion de archivos de control lista")
print("copiando grillas seleccionadas")
for grilla in lista_nombre_grillas:
    shutil.copy(grilla, dir_destino)
print("grillas copiadas")



"""
MODELS
"""
print("cambiando a directorio de modelaciones")
os.chdir(dir_comcot)
#
lista_ctl  = glob.glob("comcot_*.ctl") # arrays
lista_ctl.sort(key=os.path.getctime)  

decision_dir_modelacion = raw_input("Guardar resultados en directorio ctl [1] u en directorio definido en inicio [2]? ")
if decision_dir_modelacion == "1":
    dir_modelacion = dir_comcot
else:
    dir_modelacion = dir_modelacion
print("comenzando creacion de directorios de modelacion")
for ctl in lista_ctl:

    dir_ctl = ctl.split(".")[0] 
    nid_ctl = ctl.split("_")[1].split(".")[0] 
    os.mkdir(dir_ctl) 
    # copy
    # 1) control file
    # 2)comcot.exe
    # 3) .xyz grids
    # 4) deformation - vertical displacement input
    # 5) if ... ts_location
    # 6) run model using wine

    # 1):
    shutil.copy(ctl, dir_ctl) 
    # 2): 
    shutil.copy("comcot.exe", dir_ctl)
    # 3):
    for grilla in list(set(glob.glob("*.xyz"))-set(glob.glob("deformacion_*.xyz"))):
        shutil.copy(grilla, dir_ctl)
    # 4):
    deformacion_input = "deformacion_" + nid_ctl + ".xyz"
    shutil.copy(deformacion_input, dir_ctl)
    # 5):
    if os.path.exists("ts_location.dat"):
        shutil.copy("ts_location.dat", dir_ctl)
    # 6):
    shutil.copy(dir_actual+"/corre_comcot.sh", dir_ctl)
    os.chdir(dir_ctl)
    os.rename(ctl, "comcot.ctl")
    os.chdir("..")
    print("creacion directorio para modelacion %s lista") % (nid_ctl)
print("creacion de directorios de modelacion lista")

# start model
for dir_ctl in glob.glob("comcot_*/"):
    os.chdir(dir_ctl)
    rc = subprocess.call("corre_comcot.sh")









