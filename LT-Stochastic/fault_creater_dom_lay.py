###################################################################################################
#  Fault creator, stochastic models based on Cifuentes-Lobos et al. (2023); LeVeque et al. (2017).#
###################################################################################################

import numpy as np
import modokada as mo 
import modfallas as mf 
import modrestricciones as mr
import matplotlib.pyplot as plt
import os
from scipy.interpolate import RegularGridInterpolator, interp1d, interp2d ,griddata
from geographiclib.geodesic import Geodesic
import json
import gc 

gc.collect()

"""
Save deformations
"""
#okada = raw_input("Calculate deformation / vertical displacements? [s/n] (yes/no) ")
okada = "s"

"""
Output
"""
ruta_out = "/home/ignacia/Documentos/Javiera2/1906/bundle/fallas"

"""
Aux functions
"""

# From Ms to Mw according to kausel and ramirez formula 1997
def Mw_kauselramirez(ms):
    logm0kauselramirez = 1.5*ms+16.30
    Mw_calcs = 2.0/3.0*logm0kauselramirez-10.7 
    Mw_calcs = np.round(Mw_calcs,1) # un decimal
    return Mw_calcs


"""
LOGIC TREE INTERVALS DEFINITION
"""
N_arbol         = np.array([14,16,18,20])       # complejidad
#Mw_arbol        = np.array(9.0)        # magnitud 
Mw_arbol	= np.linspace(8.0,8.2,3) # magnitud ya transformada a Mw
LN_arbol        = np.array([-31.633])    # Limite norte
LS_arbol        = np.array([-37.00])    # Limite sur todo con array x mientras tengo los datos
sflats_arbol    = np.array([40.])               # cantidad de subfallas en latitud (along strike) para setear razon de aspecto  6x3 para modelo tsunami
dist_fosa_arbol = np.array([0.,20.,40.,60.]) # distancias (en km) del limite oeste de la ruptura con respecto de la fosa
niterslips      = 25                         # cantidad de modelos de slip creados para cada combinacion de parametros

"""
Upload Slab data
"""

# trench file
ruta_fosa = "/home/ignacia/Documentos/Javiera2/1906/bundle/Slab/"
# [longitudes ; latitudes]
arc_fosa  = ruta_fosa + "SAM2.txt"
# load trench using modfallas function
lonfosa, latfosa  = mf.carga_fosa(arc_fosa)
# SLAB2.0 Hayes, 2018
directorio = "/home/ignacia/Documentos/Javiera2/1906/bundle/Slab/"
# depth, dip, strike and rake files of Slab
proffile   = directorio + "sam_slab2_dep_02.23.18.xyz"
slabprof   = np.genfromtxt(proffile, delimiter = ",") # array
dipfile    = directorio + "sam_slab2_dip_02.23.18.xyz"
slabdip    = np.genfromtxt(dipfile, delimiter = ",") 
strfile    = directorio + "sam_slab2_str_02.23.18.xyz"
slabstrike = np.genfromtxt(strfile, delimiter = ",")
rakefile   = directorio + "sam_rake.xyz"
slabrake   = np.genfromtxt(rakefile, delimiter = ",")

"""
DATA PRECONDITIONING FOR SUBSEQUENT ANALYSES
"""

# longitudes from 0 - 360 to -180 - 180 format
slabprof[:,0]   = slabprof[:,0]   - 360
slabdip[:,0]    = slabdip[:,0]    - 360
slabstrike[:,0] = slabstrike[:,0] - 360

# longitudes and latitudes of the model
lonmod = slabprof[:,0]
latmod = slabprof[:,1]
# change
lonunimod = np.unique(lonmod) # x
latunimod = np.unique(latmod) # y
# grids creation of arrays
lonmodgrid, latmodgrid = np.meshgrid(lonunimod, np.flip(latunimod)) # X, Y datos grillados para graficar modelo completo

# depth, dip & strike of the models
profmod   = slabprof[:,2]*-1000. # positive meters downward
dipmod    = slabdip[:,2]
strikemod = slabstrike[:,2]
# grids
profmod   = np.reshape(profmod,np.shape(lonmodgrid))
dipmod    = np.reshape(dipmod,np.shape(lonmodgrid))
strikemod = np.reshape(strikemod,np.shape(lonmodgrid))
# In case, we use this aux to change from Nan to 0 on the data
idx_nan_prof_mod   = np.isnan(profmod)
idx_nan_dip_mod    = np.isnan(dipmod)
idx_nan_strike_mod = np.isnan(strikemod)
profmod[idx_nan_prof_mod]     = 0
dipmod[idx_nan_dip_mod]       = 0
strikemod[idx_nan_strike_mod] = 0

"""
Slip maps creation (general mode)
"""

# initial number of identifiers (default should be 1, if required it can be increased so as not to overwrite pre-existing files)
nslips = 1
for ln in range(len(LN_arbol)):
    for ls in range(len(LS_arbol)):
        for sf in range(len(sflats_arbol)):
            for df in range(len(dist_fosa_arbol)):    
                # size of subfault
                # aspect ratio of subfaults (length/width)
                razon_aspecto        = 7./2.
                # number of subfaults
                n_subfallas_lons      = 20. # number of subfaults along dip, with to sflats_arbol[sf] that define the aspect ratio
                n_subfallas_lats      =  sflats_arbol[sf] #np.floor(n_subfallas_lons*razon_aspecto)
                #np.floor(n_subfallas_lats/razon_aspecto)
                print(n_subfallas_lats, n_subfallas_lons)
                lats_subfallas      = np.flip(np.linspace(LS_arbol[ls], LN_arbol[ln], int(n_subfallas_lats)))
                #
                largo_falla = mf.dist_sf_alt(-72., -72., LN_arbol[ln], LS_arbol[ls])
                largo_subfallas = largo_falla / n_subfallas_lats
                # square subfaults (if you want)
                ancho_subfallas = largo_subfallas
                ancho_falla     = ancho_subfallas * n_subfallas_lons

                # Arrange to improve to a realistic results of slip
                # interpolation of trench longitude for boundary latitudes
                interpolador_lons_fosa   = interp1d(latfosa, lonfosa)
                interpolador_lats_fosa   = interp1d(lonfosa, latfosa)
                # longitude of the trench at the latitude of each subfault
                lons_fosa_para_subfallas = interpolador_lons_fosa(lats_subfallas) 
                # west boundary displacement of the subfaults (eastward displacement, away from the trench) according to the distance to the trench 
                for idxlon in range(len(lons_fosa_para_subfallas)):
                    lons_fosa_para_subfallas[idxlon] = Geodesic.WGS84.Direct(lats_subfallas[idxlon], lons_fosa_para_subfallas[idxlon], 90, dist_fosa_arbol[df]*1000)[ "lon2" ]
                # Western fault boundary defined by trench coordinates at subfault latitudes
                # Eastern boundary needs to be computed. Given the known fault width,
                # we can project the eastern longitude for each latitude point
                lons_limite_este = np.ones(np.shape(lons_fosa_para_subfallas))

                for ilon in range(len(lons_limite_este)):
                    lons_limite_este[ilon] = Geodesic.WGS84.Direct(lats_subfallas[ilon], lons_fosa_para_subfallas[ilon], 90, ancho_falla)[ "lon2" ]

                # Having established both boundaries (E-W), calculate intermediate subfault longitudes

                array_lons = np.ones((int(n_subfallas_lats),int(n_subfallas_lons)))  # lon subfaults
                for jlat in range(int(n_subfallas_lats)):
                    array_lons[jlat,:] = np.linspace(lons_fosa_para_subfallas[jlat],lons_limite_este[jlat],int(n_subfallas_lons))

                array_lats = np.tile(np.reshape(lats_subfallas,(int(n_subfallas_lats),1)),int(n_subfallas_lons)) # lat subfaults
                #print("latitudes y longitudes de fallas creadas")
                #print(LS_arbol[ls], LN_arbol[ln])
                """
                ADD ATTRIBUTES
                """
                

                """
                INTERP
                """

              # Initialize interpolator: restrict Slab2.0 model domain to target area + buffer zone for computational efficiency
              # Extract/crop full model to region of interest

                latnorte = LN_arbol[ln]     + 1.
                latsur   = LS_arbol[ls]     - 1.
                loneste  = array_lons.max() + 1. 
                lonoeste = array_lons.min() - 1.

                idx_mascara_lons = np.argwhere( (lonmodgrid > lonoeste) & (lonmodgrid < loneste) )
                idx_mascara_lats = np.argwhere( (latmodgrid > latsur) & ( latmodgrid < latnorte) )


                def coincidencias_filas(A,B):
                    coincidencias  =  [i for i in range(B.shape[0]) if np.any(np.all(A==B[i],axis=1))]
                    if len(coincidencias)==0:
                        return B[coincidencias]
                    return np.unique(B[coincidencias],axis=0)

                mascara = coincidencias_filas(idx_mascara_lons, idx_mascara_lats)
                # the number of columns and rows of the cut is calculated.
                primer_elemento_mascara = mascara[0,0]
                n_columnas_area_interes = np.shape(mascara[mascara[:,0]==primer_elemento_mascara,:])[0]
                n_filas_area_interes    = np.shape(mascara)[0]/n_columnas_area_interes
                # mask dimensions
                dim_mascara          = np.shape(mascara)
                dim_mascara_filas    = dim_mascara[0]
                dim_mascara_columnas = dim_mascara[1]
                # cut longitude
                lonmodgrid_cortado = np.ones((dim_mascara_filas,1))
                for i in range(dim_mascara_filas):
                    lonmodgrid_cortado[i] = lonmodgrid[mascara[i,0],mascara[i,1]]

                # cut latitude
                latmodgrid_cortado = np.ones((dim_mascara_filas,1))
                for j in range(dim_mascara_filas):
                    latmodgrid_cortado[j] = latmodgrid[mascara[j,0],mascara[j,1]]

                # cut grid
                lonmodgrid_cortado_grilla, latmodgrid_cortado_grilla = np.meshgrid(lonmodgrid_cortado, latmodgrid_cortado)

                # depth of the cut model in the main area
                profmod_cortado = np.ones((dim_mascara_filas,1))
                for h in range(dim_mascara_filas):
                    profmod_cortado[h] = profmod[mascara[h,0],mascara[h,1]]

                # change to the new dimensions
                profmod_cortado = np.reshape(profmod_cortado,(n_filas_area_interes, n_columnas_area_interes))

                # dip
                dipmod_cortado = np.ones((dim_mascara_filas,1))
                for d in range(dim_mascara_filas):
                    dipmod_cortado[d] = dipmod[mascara[d,0],mascara[d,1]]
                dipmod_cortado = np.reshape(dipmod_cortado,(n_filas_area_interes, n_columnas_area_interes))

                # strike
                strikemod_cortado = np.ones((dim_mascara_filas,1))
                for s in range(dim_mascara_filas):
                    strikemod_cortado[s] = strikemod[mascara[s,0],mascara[s,1]]
                strikemod_cortado = np.reshape(strikemod_cortado, (n_filas_area_interes, n_columnas_area_interes))

                # grid
                lonmodgrid_cortado_area = np.reshape(lonmodgrid_cortado, (n_filas_area_interes, n_columnas_area_interes))
                latmodgrid_cortado_area = np.reshape(latmodgrid_cortado, (n_filas_area_interes, n_columnas_area_interes))


                """
                INTERPOLATORS
                """

                # in terms of depth
                interpolador_prof   = interp2d(lonmodgrid_cortado_area[0,:], latmodgrid_cortado_area[:,0], profmod_cortado, kind='cubic')

                # in terms od dip
                interpolador_dip    = interp2d(lonmodgrid_cortado_area[0,:], latmodgrid_cortado_area[:,0], dipmod_cortado, kind='cubic')

                # in terms of strike
                interpolador_strike = interp2d(lonmodgrid_cortado_area[0,:], latmodgrid_cortado_area[:,0], strikemod_cortado, kind='cubic')

                # in terms of rake
                interpolador_rake   = interp2d(slabrake[:,0], slabrake[:,1], slabrake[:,2], kind = 'cubic')

                ###################
                #     interp      #
                ###################

                # depth
                prof_subfallas_int  = np.ones(np.shape(array_lons))
                for i in range(np.shape(array_lons)[0]):
                    for j in range(np.shape(array_lons)[1]):
                        prof_subfallas_int[i,j]   = interpolador_prof(array_lons[i,j], array_lats[i,j])
                prof_subfallas_int = np.abs(prof_subfallas_int)
                # dip
                dip_subfallas_int   = np.ones(np.shape(array_lons))
                for i in range(np.shape(array_lons)[0]):
                    for j in range(np.shape(array_lons)[1]):
                        dip_subfallas_int[i,j]    = interpolador_dip(array_lons[i,j], array_lats[i,j])

                # strike
                strike_subfallas_int = np.ones(np.shape(array_lons))
                for i in range(np.shape(array_lons)[0]):
                    for j in range(np.shape(array_lons)[1]):
                        strike_subfallas_int[i,j] = interpolador_strike(array_lons[i,j], array_lats[i,j])

                # rake
                rake_subfallas_int   = np.ones(np.shape(array_lons))
                for i in range(np.shape(array_lons)[0]):
                    for j in range(np.shape(array_lons)[1]):
                        rake_subfallas_int[i,j] = interpolador_rake(array_lons[i,j], array_lats[i,j])

                assert not np.isnan(np.sum(prof_subfallas_int)), "in case of an error in the interpolation process"
                print("interpolacion completa")

                
                """
                SLIP CALCULATION
                """
                # mean matrix
                mu   = mf.matriz_medias(11, prof_subfallas_int)
                # std matrix
                C    = mf.matriz_covarianza(dip_subfallas_int, prof_subfallas_int, array_lons, array_lats)
                if np.isnan(C).any() or np.isinf(C).any(): # in case
                    continue
                # slip map creation process    
                for comp in range(len(N_arbol)):
                    for mag in range(len(Mw_arbol)):
                        for i in range(niterslips):        
                            print(nslips, "ln: ", LN_arbol[ln], "ls: ", LS_arbol[ls], "Mw: ", Mw_arbol[mag] , "Complejidad: ", N_arbol[comp], "Dist. Fosa: ", dist_fosa_arbol[df])
                            Slip    = mf.distribucion_slip(C, mu, int(N_arbol[comp])) # distribution of slip
                            # slip taper
                            Mw = Mw_arbol[mag]
                            ventana = mf.ventana_taper_slip_fosa(Slip, array_lons, array_lats,2) # window
                            Slip    = mf.taper_slip_fosa(Slip,ventana)
                            Slip    = mf.escalar_magnitud_momento(Mw+0.1, Slip, prof_subfallas_int, array_lons, array_lats) # real magnitude estimation along with ---------> final Slip
                            # just for test the data 
                            #fig = plt.figure()
                            #ax = fig.add_subplot(111)
                            #im = ax.imshow(Slip)
                            #fig.colorbar(im)
                            #plt.show()
                            
                            """
                           OUTPUT
                            """
                            #fault data
                            nombre_archivo = "falla_%d" %(nslips) 
                            archivo_salida = os.path.join(ruta_out, nombre_archivo)
                            # dictionary of parameters
                            readme_nombre  = "readme_%d.json" %(nslips)
                            readme_salida  = os.path.join(ruta_out, readme_nombre)
                            # dictionary of Logic Tree (LT)
                            dict_ramas     = {"N": N_arbol[comp],
                                            "Mw": Mw,
                                            "LN": LN_arbol[ln],
                                            "LS": LS_arbol[ls],
                                            "AR": np.floor(n_subfallas_lats/n_subfallas_lons) } 
                            json_ramas   = json.dumps(dict_ramas)      # json file
                            json_archivo = open(readme_salida,'w')     # dictionary output
                            json_archivo.write(json_ramas)             # json dictionary
                            json_archivo.close()                       # end 
                            np.savez(archivo_salida,Slip=Slip,array_lons=array_lons,array_lats=array_lats,
                                                        dip_subfallas_int=dip_subfallas_int,strike_subfallas_int=strike_subfallas_int,
                                                        rake_subfallas_int=rake_subfallas_int, prof_subfallas_int=prof_subfallas_int,largo_falla=largo_falla) # output with fault arrays
                            if okada == "s" or okada == "S":
                                falla = mo.crea_falla_dtopo( array_lons, array_lats, razon_aspecto, strike_subfallas_int, dip_subfallas_int, 
                                                            prof_subfallas_int, rake_subfallas_int, Slip, largo_falla)                 
                                dtopo = mo.okada_solucion( array_lons, array_lats, razon_aspecto, strike_subfallas_int, dip_subfallas_int, prof_subfallas_int, rake_subfallas_int,
                                                            Slip, largo_falla, resolucion = 1/30., tamano_buffer = 1., verbose = True ) # deformation / vertical displacement calculations
                                #falla.plot_subfaults( slip_color = True )
                                # 
                                if not np.isnan(dtopo.dZ_max()):
                                    nombre_archivo_def = "deformacion_%d.tt3" % (nslips)
                                    nombre_out_def = os.path.join(ruta_out, nombre_archivo_def)
                                    # save in deformation file in "fallas"
                                    dtopo.write(nombre_out_def, dtopo_type = 3)
                                else:
                                    continue        
                            nslips += 1
                    
plt.show()
