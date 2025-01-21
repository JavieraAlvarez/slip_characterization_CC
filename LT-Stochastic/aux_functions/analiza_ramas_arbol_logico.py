import os
import glob
import shutil 
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import gc 
from scipy.stats import mode
import json
import seaborn as sns

gc.collect()

"""
PARAMETROS DE DIRECTORIO
"""
# directorio actual
dir_actual = os.getcwd()
# ruta directorio diccionarios
ruta_json = "/Users/javieraalvarezvargas/Desktop/suite/fallas"
os.chdir(ruta_json)
# ruta directorio figuras (relativo a directorio de modelos restringidos)
ruta_dir_figs = "../figanalisis"


"""
CARGA DATOS
"""
# se crea una lista con los diccionarios con info de las ramas
lista_json = glob.glob("*.json")      # lista con diccionarios de parametros por modelo
#print(lista_json)
"""
INICIALIZACION DE LISTAS PARA GUARDAR INFO DE RAMAS
"""
lista_mw = [] # magnitudes
lista_ar = [] # razones de aspecto
lista_ls = [] # limites norte
lista_ln = [] # limites sur
lista_N  = [] # complejidades

"""
LOOP PARA LEER INFO
"""

for i in lista_json:
    with open(i) as ramas:
        ramas_objeto = json.load(ramas)
        mw = ramas_objeto['Mw']
        ar = ramas_objeto['AR']
        ls = ramas_objeto['LS']
        ln = ramas_objeto['LN']
        N  = ramas_objeto['N']
        lista_mw.append(mw)
        lista_ar.append(ar)
        lista_ls.append(ls)
        lista_ln.append(ln)
        lista_N.append(N)
    ramas.close()
#print(lista_json)
#print(mw)
#print(lista_mw)
"""
GUARDAR REGISTRO DE PARAMETROS MAS PROBABLES
"""
# encontrar modas
moda_mw = mode(lista_mw)[0]
print(moda_mw)
moda_ar = mode(lista_ar)[0]
print(moda_ar)
moda_ln = mode(lista_ln)[0]
print(moda_ln)
moda_ls = mode(lista_ls)[0]
print(moda_ls)
moda_N  = mode(lista_N)[0]
print(moda_N)
# crear json con modelos más probables

def convertir_a_nativo(valor):
    if isinstance(valor, (np.int64, np.float64)):
        return valor.item()
    return valor

# crear json con modelos más probables
dict_mas_prob = {
    "Mw": convertir_a_nativo(moda_mw),
    "AR": convertir_a_nativo(moda_ar),
    "LN": convertir_a_nativo(moda_ln),
    "LS": convertir_a_nativo(moda_ls),
    "N":  convertir_a_nativo(moda_N)
}

archivo_parametros_al = "parametros_AL_mas_probables.json"
json_mas_prob = json.dumps(dict_mas_prob)
with open(archivo_parametros_al, 'w') as json_archivo:
    json_archivo.write(json_mas_prob)

"""
GRAFICOS
"""
# histograma magnitudes

# Configuración de estilo
sns.set(style="whitegrid")

# Crear la figura y el eje
plt.figure(figsize=(10, 6))

# Histograma con línea KDE
sns.histplot(lista_mw, bins='auto', kde=False, color='#0504aa', alpha=0.7)

# Añadir etiquetas y título
plt.xlabel('Mw', fontsize=14)
plt.ylabel('Frequency', fontsize=14)
plt.title('Magnitude Frequency', fontsize=16)
plt.grid(axis='y', alpha=0.75)

# Guardar la figura
plt.savefig('histo_mags.png', transparent=True)
plt.show()
# histograma razones de aspecto

n, bins, patches = plt.hist(x=lista_ar, bins='auto', color='#0504aa',
                            alpha=0.7)
plt.grid(axis='y', alpha=0.75)
plt.xlabel('Southern limit')
plt.ylabel('Frequency')
plt.title('Aspect ratio frequency')
plt.savefig('histo_ar.png', transparent = True)


# histograma limite sur

n, bins, patches = plt.hist(x=lista_ls, bins='auto', color='#0504aa',
                            alpha=0.7)
plt.grid(axis='y', alpha=0.75)
plt.xlabel('Southern limit')
plt.ylabel('Frequency')
plt.title('Southern limit frequency')
plt.savefig('histo_ls.png', transparent = True)

# histograma limite norte

n, bins, patches = plt.hist(x=lista_ln, bins='auto', color='#0504aa',
                            alpha=0.7)
plt.grid(axis='y', alpha=0.75)
plt.xlabel('Southern limit')
plt.ylabel('Frequency')
plt.title('Northern limit frequency')
plt.savefig('histo_ln.png', transparent = True)

# mover figuras
lista_figs = glob.glob("*.png")
for fig in lista_figs:
    shutil.move(fig, ruta_dir_figs)

# volver al directorio principal
os.chdir(dir_actual)