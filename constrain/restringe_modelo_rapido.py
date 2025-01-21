# aplica restricciones de datos de paleodeformacion
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
import matplotlib.pyplot as plt
from scipy.interpolate import RegularGridInterpolator, interp1d, interp2d ,griddata, Rbf
from geographiclib.geodesic import Geodesic
import gc 

gc.collect()


"""
CARGA DATOS
"""

# ruta del archivo de la fosa
ruta_fosa = "../../../../Slab/"
# archivo fosa ( primera columna: longitudes, segunda columna: latitudes)
arc_fosa  = ruta_fosa + "SAM2.txt"
# carga de fosa usando funcion del modulo modfallas
lonfosa, latfosa  = mf.carga_fosa(arc_fosa)


# ruta datos de deformacion
ruta_paleodatos = "../input/" # ruta relativa a directorio con fallas
arch_paleodatos = "restricciones.csv"
paleodatos      = ruta_paleodatos + arch_paleodatos
agno = 1960
"""
INFO DE DIRECTORIOS
"""
dir_destino = "modelos_restringidos"
dir_actual  = os.getcwd()
path_fallas="../fallas/"
os.chdir(path_fallas)
"""
CARGAR LISTAS
"""
# lista con todos los archivos npz sobre los que se iterara
lista_npz  = glob.glob("*.npz")       # lista con arrays de slip y coordenadas
lista_npz.sort(key=os.path.getctime)  # lista ordenada
lista_json = glob.glob("*.json")      # lista con diccionarios de parametros por modelo
lista_json.sort(key=os.path.getctime) # lista ordenada
lista_def = glob.glob("*.tt3")        # lista con info de deformacion 
lista_def.sort(key=os.path.getctime)  # lista ordenada

# se revisa que no haya errores en la carga de datos
#assert len(lista_npz)==len(lista_def)==len(lista_def)

print("%s archivos de fallas leidos") %(len(lista_def))



"""
LECTURA PALEODATOS
"""
# chequear si datos vienen en csv
assert paleodatos.endswith(".csv")
# nombre de columnas segun formato provisto por Saavedra, Cris
nombres_columnas = ["Evento","Longitud","Latitud","vertical","Deformacion","Direccion","Fuente","Localidad"]
# se lee el archivo 
paleo_registros  = pd.read_csv(paleodatos,skiprows = [0], names = nombres_columnas)
agno_evento  = paleo_registros.Evento.tolist()
lon_medicion = paleo_registros.Longitud.tolist()
lat_medicion = paleo_registros.Latitud.tolist()
mov_vertical = paleo_registros.vertical.tolist()

# se busca solo aquellos elementos correspondientes a mediciones del evento de interes
idx_evento   = np.where(np.asarray(agno_evento)==str(agno))
lon_med_int  = np.asarray(lon_medicion)[idx_evento]
lat_med_int  = np.asarray(lat_medicion)[idx_evento]
mov_vert_int = np.asarray(mov_vertical)[idx_evento]
mov_vert_int[mov_vert_int=='-']="0"
mov_vert_int = np.asarray(map(int, mov_vert_int))

# todas comparten las mismas subfallas

datadef = mo.leer_okada(lista_def[0])
lonsdef = datadef.X
latsdef = datadef.Y 

idxlon = []
idxlat = []
for i in range(len(mov_vert_int)):
    x = np.abs(lonsdef - lon_med_int[i])
    y = np.abs(latsdef - lat_med_int[i])
    idxlon.append(divmod(np.abs(x).argmin(),x.shape[1]))
    idxlat.append(divmod(np.abs(y).argmin(),y.shape[1]))
    idxlon[i] = idxlon[i][1]
    idxlat[i] = idxlat[i][0]
    #idxlon[i] = np.argwhere(x == np.min(x))
    #idxlat[i] = np.argwhere(y == np.min(y))

"""
LOOP DE RESTRICCION
"""
lista_modelos_restringidos = [] # inicializacion de lista donde se guardara los nombres de los modelos restringidos (nuevo)
tol = 3                         # tolerancia 
c   = 0                         # contador de modelos
for d in lista_def:
    print("analizando modelo %d") %(c)
    datadef   = mo.leer_okada(d)
    deltaZ    = np.squeeze(datadef.dZ)
    cont      = 0  # contador de elementos distintos de 0
    cont_coin = 0  # contador de coincidencias
    for i in range(len(mov_vert_int)):
        if mov_vert_int[i] != 0:
            cont += 1
            print(np.sign(deltaZ[idxlat[i]][idxlon[i]]),np.sign(mov_vert_int[i]))
            if np.sign(deltaZ[idxlat[i]][idxlon[i]]) == np.sign(mov_vert_int[i]):
                cont_coin += 1
    if cont_coin >= 1:
        print(cont)
        print(cont_coin)
    if cont - tol <= cont_coin:
        shutil.copy(lista_def[c],dir_destino)
        shutil.copy(lista_json[c],dir_destino)
        shutil.copy(lista_npz[c],dir_destino)
        print("copiado el modelo %d") % (c)
        lista_modelos_restringidos.append(c) # (nuevo)
    c += 1


"""
CREACION DE LISTA CON LOS INDICES IDENTIFICADORES DE LOS MODELOS RESTRINGIDOS PARA TRACKEO
"""

nombre_lista_idx = "lista_idx_modelos_restringidos.txt"
f = open(nombre_lista_idx,"w")
for id in lista_modelos_restringidos:
    f.write(str(id)+"\n")
f.close()
shutil.copy(nombre_lista_idx,dir_destino)
print("Creada lista con identificadores de modelos restringidos")
print("Guardada en dir_destino")

# volver al directorio actual 
os.chdir(dir_actual)