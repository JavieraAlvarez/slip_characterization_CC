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
ruta_fosa = "/home/ignacia/Documentos/Javiera2/1906/bundle/Slab/"
# archivo fosa ( primera columna: longitudes, segunda columna: latitudes)
arc_fosa  = ruta_fosa + "SAM2.txt"
# carga de fosa usando funcion del modulo modfallas
lonfosa, latfosa  = mf.carga_fosa(arc_fosa)


# ruta datos de deformacion
ruta_paleodatos = "/home/ignacia/Documentos/Javiera2/1906/bundle/input/" # ruta relativa a directorio con fallas
arch_paleodatos = "def_magnitud_1906.xyz"
paleodatos      = ruta_paleodatos + arch_paleodatos
agno = 1906
"""
INFO DE DIRECTORIOS
"""
dir_destino = "/home/ignacia/Documentos/Javiera2/1906/bundle/fallas/modelos_restringidos_magnitud"
dir_actual  = os.getcwd()
path_fallas="/home/ignacia/Documentos/Javiera2/1906/bundle/fallas/"
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

print("%s archivos de fallas leidos" % len(lista_def))



"""
LECTURA PALEODATOS
"""
# chequear si datos vienen en csv
assert paleodatos.endswith(".xyz")

"""
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
"""


# leer de .xyz en lugar de .csv
# formato columnas "? lon lat def lugar"
paleo_registros = np.genfromtxt(paleodatos, usecols=(1,2,3))
lon_med_int     = paleo_registros[:,0]
lat_med_int     = paleo_registros[:,1]
mov_vert_int    = paleo_registros[:,2]



# todas comparten las mismas subfallas

datadef = mo.leer_okada(lista_def[0])
lonsdef = datadef.X
latsdef = datadef.Y 

# # preparacion para interpolaciones
# lons_unicas = np.unique(lonsdef)
# lats_unicas = np.unique(latsdef)

# # se chequea si son crecientes monotonos, util para interpolacion 
# if all( x < y for x, y in zip( lons_unicas, lons_unicas[1:] ) ):
#     lons_unicas = lons_unicas
# else:
#     lons_unicas = lons_unicas[::-1]

# # latitudes
# # se chequea si son crecientes monotonos, util para interpolacion 
# if all( x < y for x, y in zip( lats_unicas, lats_unicas[1:] ) ):
#     lats_unicas = lats_unicas
# else:
#     lats_unicas = lats_unicas[::-1]


idxlon = []
idxlat = []
for i in range(len(mov_vert_int)):
    x = np.abs(lonsdef - lon_med_int[i])
    y = np.abs(latsdef - lat_med_int[i])
    idxlon.append(divmod(np.abs(x).argmin(),x.shape[1]))
    idxlat.append(divmod(np.abs(y).argmin(),y.shape[1]))
    idxlon[i] = idxlon[i][1]
    idxlat[i] = idxlat[i][0]


"""
LOOP DE RESTRICCION
"""
flag_tipo  = 0                  # switch para controlar si se quiere restringir con coincidencia de signos o con valores de deformacion
# 1: coincidencia
# 0: valores de deformacion
lista_modelos_restringidos = [] # inicializacion de lista donde se guardara los nombres de los modelos restringidos (nuevo)
tol        = 4                  # tolerancia de datos
tol_metros = 0.5               # tolerancia en metros de rango de restriccion
c          = 0                  # contador de modelos
for d in lista_def:
    print("analizando modelo %d" %(c))
    datadef   = mo.leer_okada(d)
    deltaZ    = np.squeeze(datadef.dZ)
    lonsdef = datadef.X
    latsdef = datadef.Y 
    cont      = 0  # contador de elementos distintos de 0
    cont_coin = 0  # contador de coincidencias

    # preparacion para interpolaciones
    lons_unicas = np.unique(lonsdef)
    lats_unicas = np.unique(latsdef)


    # se chequea si son crecientes monotonos, util para interpolacion 
    if all( x < y for x, y in zip( lons_unicas, lons_unicas[1:] ) ):
        lons_unicas = lons_unicas
    else:
        lons_unicas = lons_unicas[::-1]

    # latitudes
    # se chequea si son crecientes monotonos, util para interpolacion 
    if all( x < y for x, y in zip( lats_unicas, lats_unicas[1:] ) ):
        lats_unicas = lats_unicas
    else:
        lats_unicas = lats_unicas[::-1]



    # objeto de interpolacion de deformaciones
    def_int = RegularGridInterpolator( ( lats_unicas, lons_unicas ), deltaZ )
    # inicializacion valores interpolados de deformacion
    valores_def_interp = np.ones(len(mov_vert_int))
    # interpolacion
    for i in range(len(mov_vert_int)):
        valores_def_interp[i] = def_int((lat_med_int[i], lon_med_int[i]))
    # loop de restriccion
    if flag_tipo:
        for i in range(len(mov_vert_int)):
            if mov_vert_int[i] != 0:
                cont += 1
                if np.sign(mov_vert_int[i]) == np.sign(valores_def_interp[i]):
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
    if not flag_tipo:
        for i in range(len(mov_vert_int)):
            if mov_vert_int[i] != 0:
                cont += 1
                if (mov_vert_int[i] > 0) and (mov_vert_int[i] < valores_def_interp[i]+tol_metros) and (mov_vert_int[i] > valores_def_interp[i]-tol_metros):
                    cont_coin += 1
                elif (mov_vert_int[i] < 0) and (mov_vert_int[i] < valores_def_interp[i]+tol_metros ) and (mov_vert_int[i] > valores_def_interp[i]-tol_metros):
                    cont_coin += 1
        if cont_coin >= 1:
            print(cont)
            print(cont_coin)
        if cont - tol <= cont_coin:
            shutil.copy(lista_def[c],dir_destino)
            shutil.copy(lista_json[c],dir_destino)
            shutil.copy(lista_npz[c],dir_destino)
            print("copiado el modelo %d" % (c))
            lista_modelos_restringidos.append(c) # (nuevo)
        c += 1

"""
CREACION DE LISTA CON LOS INDICES IDENTIFICADORES DE LOS MODELOS RESTRINGIDOS PARA TRACKEO
"""

nombre_lista_idx = "lista_idx_modelos_restringidos_magnitud.txt"
f = open(nombre_lista_idx,"w")
for idx in lista_modelos_restringidos:
    f.write(str(idx)+"\n")
f.close()
shutil.copy(nombre_lista_idx,dir_destino)
print("Creada lista con identificadores de modelos restringidos")
print("Guardada en dir_destino")

# volver al directorio actual 
os.chdir(dir_actual)
