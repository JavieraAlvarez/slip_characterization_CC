#maneja las restricciones de baja resolucion de tsunami
import Tkinter,tkFileDialog
from tkinter import *
from tkinter import ttk
import os
import glob
import shutil 
import sys
import json
import numpy as np
import pandas as pd
#import modokada as mo 
#import modfallas as mf 
#import modrestricciones as mr
from geographiclib.geodesic import Geodesic
import gc 

gc.collect()



"""
INFO DE DIRECTORIOS
"""

dir_modelaciones   = "/media/rodrigo/KINGSTON/cyclo/Scripts/Scripts/Codigos_arbol/funciones/ctl_tsunami" # ruta al directorio donde se guardan los modelos
dir_data_input     = "/media/rodrigo/KINGSTON/cyclo/Scripts/Scripts/Codigos_arbol/funciones/ctl_tsunami"
dir_actual         = os.getcwd()     # ruta al directorio principal 


# se crea una lista de todos los directorios dentro de dir_modelaciones que tienen datos de modelos
lista_dir_modelaciones = [f for f in os.listdir(dir_modelaciones) if os.path.isdir(os.path.join(dir_modelaciones, f))]
n_dir_modelaciones     = len(lista_dir_modelaciones) # cantidad de directorios con modelaciones

"""
RECOPILACION DE INFORMACION PREVIA
"""

# funcion para elegir archivo de input de datos 
def seleccion_input_datos():
    os.chdir(dir_data_input)
    root = Tkinter.Tk()
    input_data = tkFileDialog.askopenfilenames(parent=root,multiple=False,title='Choose input data for LR restrictions')
    lista_input_data  = list(input_data) # se transforma a una lista
    input_file        = lista_input_data[0] # se obtiene el primer elemento de la lista, que es el archivo con su ruta completa
    #directorio_input  = os.path.split(input_file)[0] # directorio donde se encuentra el archivo
    nombre_input_file = os.path.split(input_file)[1] # nombre del archivo solo
    root.destroy()
    assert nombre_input_file.endswith(".csv")
    nombres_columnas = ["Evento","Longitud","Latitud","T o NT","Altura","Pleamar","Bajamar", "Fuente", "Localidad"]
    paleo_registros  = pd.read_csv(input_file, skiprows = [0], names = nombres_columnas)
    #agno_evento  = np.asarray(paleo_registros.Evento.tolist())
    lon_medicion = np.asarray(paleo_registros.Longitud.tolist())
    lat_medicion = np.asarray(paleo_registros.Latitud.tolist())
    altura_ola   = np.asarray(paleo_registros.Altura.tolist())
    altura_ola[altura_ola=="-"]="nan"
    pleamar      = np.asarray(paleo_registros.Pleamar.tolist())
    bajamar      = np.asarray(paleo_registros.Bajamar.tolist())
    os.chdir(dir_actual)
    return altura_ola, lon_medicion, lat_medicion, pleamar, bajamar

# leer el archivo de datos de restricciones
altura_ola, lon_medicion, lat_medicion, pleamar, bajamar = seleccion_input_datos()
# arreglar valores a valores utilizables
plea = np.ones(len(pleamar))
baja = np.ones(len(bajamar))
for idx in range(len(pleamar)):
    plea[idx] = pleamar.split("+")[0]
    baja[idx] = bajamar.split("+")[0]
n_observaciones = len(altura_ola)

# funcion para leer ts_location

def leer_ts_locations():
    """
    ENTRADA:
    dir_modelaciones: directorio donde se encuentran todos los archvios de control y  subdirectorios con modelaciones
    dir_actual: directorio parental desde donde se esta trabajando
    """
    os.chdir(dir_modelaciones)
    coords = np.genfromtxt("ts_locations.dat", usecols=(0,1)) # se lee el archivo de ts_locations
    lon_ts = coords[:,0] # se obtienen las longitudes
    lat_ts = coords[:,1] # se obtienen las latitudes
    n_ts   = len(lat_ts) # numero total de series
    os.chdir(dir_actual)
    return lon_ts, lat_ts, n_ts

# leer ts_records
lon_ts, lat_ts, n_ts = leer_ts_locations()

# se asegura que la cantidad de datos sea menor o igual que la cantidad de mediciones, para asegurar una comparacion uno a uno
assert n_ts >= len(altura_ola) 

"""
APLICACION DE RESTRICCIONES
"""

# funcion para recorrer todos los subdirectorios, leer los ts_records y restringir

def restringir_con_altura_de_olas():
    """
    ENTRADAS
    lista_dir_modelaciones: lista con todos los subdirectorios que contienen records 
    """
    for subdir, dirs, files in os.walk(dir_modelaciones):
        lista_records_path = []
        lista_records      = []
        lista_subdir       = []
        for archivo in files:
            if archivo.startswith("ts_record"):
                record = archivo
                record_path = os.path.join(subdir, record)
                lista_records.append(record)
                lista_records_path.append(record_path)
                lista_subdir.append(subdir)
        lista_records      = sorted(list(lista_records))      # lista ordenada con los ts_records por subdirectorio
        lista_subdir       = list(lista_subdir)               # lista con el subdirectorio correspondiente a cada ts_record
        lista_records_path = sorted(list(lista_records_path)) # lista ordenada con ruta total
        n_records = len(lista_records_path)
    # leer los ts_records y comparar
    # se lee un ts_record cualquiera para obtener el largo e inicializar un array del tamano correcto
    len_dummy_ts = len(np.genfromtxt(lista_records_path[0]))
    array_ts_columna = np.ones((n_records, len_dummy_ts)) # inicializacion array que contendra en cada columna los ts
    array_min_altura_ola = np.ones((n_records,1)) # array con el minimo de cada record
    array_max_altura_ola = np.ones((n_records,1)) # array con el maximo de cada recor
    cont = 0 # contador auxiliar
    for ts in lista_records_path:
        record = np.genfromtxt(ts)
        #array_ts_columna[cont,:]     = record # para muchos modelos este array ocupa MUCHA memoria, no descomentar a no ser que sea muy necesario
        array_min_altura_ola[cont,:] = min(record)
        array_max_altura_ola[cont,:] = max(record)
        cont += 1
    # comparacion
    flags_altura = np.ones(n_records)
    for idx in xrange(n_records):
        if array_max_altura_ola[idx][0] > (altura_ola[idx%n_observaciones]+plea[idx%n_observaciones]) or array_max_altura_ola[idx][0] > (altura_ola[idx%n_observaciones]+baja[idx%n_observaciones]):
            flags_altura[idx] = 1
        else:
            flags_altura[idx] = 0
    #return lista_records, lista_records_path, lista_subdir
    return flags_altura