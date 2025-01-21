"""
Modulo con funciones necesarias para la implementacion de restricciones fisicas y observacionales
a los modelos
"""


import numpy as np 
from numpy import linalg as la
import matplotlib.pyplot as plt 
import collections as col
from geopy import distance
import geographiclib as geo 
from geographiclib.geodesic import Geodesic
from scipy.interpolate import RegularGridInterpolator, interp1d
from scipy import signal
import scipy.ndimage.filters as filters
from clawpack.geoclaw import dtopotools, topotools
from multiprocessing import Pool, Process, cpu_count
import pandas as pd
from scipy.interpolate import RegularGridInterpolator, interp1d, interp2d ,griddata



# funcion para restringir tamano de fallas con respecto a magnitud
def restringir_largo(lons,lats,Mw):
    """
    Se restringe el largo de la falla con respecto a un coeficiente 0.57 pm 0.1 
    segun la ecuacion log10(L)=-2.37+0.57Mw (Blaser et al., 2010)
    Entradas:
    lons: matriz con longitudes de las subfallas
    lats: matriz con latitudes de las subfallas
    Mw: magnitud de momento del evento
    """

    # se calcula el largo de la falla
    latmax = np.max(lats)
    latmin = np.min(lats)
    lon    = -72.
    largo_falla = Geodesic.WGS84.Inverse(latmax, lon, latmin, lon )[ "s12" ]
    largo_falla = largo_falla/1000. # en km
    # ecuacion de blaser (log10_largo = lhs y rhs = -2.37+0.57Mw)
    log10_largo = np.log10(largo_falla) # lhs
    rhs         = -2.37+0.57*Mw
    if np.abs(log10_largo - rhs) < 0.1:
        flag = 1
    else:
        flag = 0
    return flag


# funcion para restringir tamano de fallas con respecto a magnitud
def restringir_ancho(lons,lats,Mw):
    """
    Se restringe el largo de la falla con respecto a un coeficiente 0.57 pm 0.1 
    segun la ecuacion log10(L)=-2.37+0.57Mw (Blaser et al., 2010)
    Entradas:
    lons: matriz con longitudes de las subfallas
    lats: matriz con latitudes de las subfallas
    Mw: magnitud de momento del evento
    """

    # se calcula el largo de la falla
    lonmax      = np.max(lons)
    lonmin      = np.min(lons)
    lat_unicas  = np.unique(lats)
    lat_mediana = np.median(lat_unicas)
    ancho_falla = Geodesic.WGS84.Inverse(lat_mediana, lonmax, lat_mediana, lonmin )[ "s12" ]
    ancho_falla = ancho_falla/1000. # en km
    # ecuacion de blaser (log10_ancho = lhs y rhs = -1.87+0.46Mw)
    log10_ancho = np.log10(ancho_falla) # lhs
    rhs         = -1.87+0.46*Mw
    if np.abs(log10_ancho - rhs) < 0.1:
        flag = 1
    else:
        flag = 0
    return flag

# restriccion de profundidad
def restringir_profundidad(slip,prof,hmax=60):
    """
    Funcion para restringir la profundidad maxima del evento generado.
    Se busca la profundidad del parche mas grande de slip para restringir
    Entradas:
    slip: matriz de slip
    prof: matriz de profundidades de cada subfalla
    hmax: profundidad maxima en kilometros aceptada. por defecto 60 km (de Becerra et al., 2020)
    """
    # eje z es positivo hacia arriba
    if prof.max() < 0:
        prof *= -1.

    # se revisa que la matriz de profundidades este en km
    if prof.max() > 1000. : 
        prof /= 1000.

    # se identifica el indice del maximo de slip
    idx_max_slip = zip(*np.where(slip == np.max(slip)))[0]

    # se busca la profundidad asociada a este maximo
    prof_slip_max = prof[idx_max_slip]

    # se chequea si es mayor o menor a la profundidad maxima deseada
    if prof_slip_max > hmax:
        flag = 0
    elif prof_slip_max < hmax:
        flag = 1

    return flag


# funcion que chequea si las deformaciones coinciden con las mediciones

def restringir_mediciones_deformacion(dtopo, paleodatos, agno, tol=1):
    """
    Funcion para restringir segun mediciones de paleodeformacion
    Entradas:
    dtopo: objeto dtopo resultado de okada
    paleodatos: archivo con informacion de paleodeformacion segun formato de Saavedra
    agno: agno del evento a estudiar.
    tol: tolerancia de diferencias entre mediciones y modelo aleatorio. por defecto 1
    """

    # informacion de la deformacion
    lonsdef     = dtopo.X              # longitudes
    latsdef     = dtopo.Y              # latitudes
    deformacion = np.squeeze(dtopo.dZ) # deformacion

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
    

    # se crea un interpolador para estimar la deformacion en el lugar de la medicion de acuerdo a la deformacion calculada
    interp_deformacion = interp2d(lonsdef,latsdef,deformacion,kind='cubic')
    # se estima la deformacion en todos los puntos de medicion del agno de interes
    def_interpolada    = np.ones(np.shape(lon_med_int))
    for i in range(len(def_interpolada)):
        def_interpolada[i] = interp_deformacion(lon_med_int[i], lat_med_int[i])
    
    # se chequea si se comparten todos los signos
    coincidencias = np.sign(def_interpolada) == np.sign(mov_vert_int)
    if sum(coincidencias) == len(coincidencias):
        flag = 1
    elif (len(coincidencias)-sum(coincidencias)) < tol:
        flag = 1
    else:
        flag = 0

    return flag



