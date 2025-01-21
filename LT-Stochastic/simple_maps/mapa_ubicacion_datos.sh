#!/bin/bash

# mapa que muestra la ubicacion de los puntos con datos


region="mapa_datos"
bounds="-80/-68/-48/-34"
projection="M8.0"
pticks="a2f1SeWn"
sticks="a2f1SEwn"
portrait="-P"	
verbose="-V"
coastline="0.1p,0/0/0"
resolution="f"	
land="-G220"
lakes="-C255/255/255 -A0/2/4"
psfile="${region}.ps"
rests="input/restricciones.csv"
datatsunami="input/ubicaciondatostsunami.csv"
rosa="dg-78/-36+w1c+f+l,,,n"
########################################
#p delays
####################
#basemap and coast
gmt psbasemap -B${pticks} -J${projection} -R${bounds}  -X2 -Y6 ${portrait} ${verbose} -K > ${psfile}
gmt pscoast -B${pticks} -J${projection} -R${bounds} ${portrait} ${verbose} -D${resolution} -W${coastline} ${land} -O -K >> ${psfile}
gmt pscoast -B${pticks} -J${projection} -R${bounds} ${portrait} ${verbose} ${lakes} -D${resolution} -W${coastline} -O -K >> ${psfile}


# deformacion
#slip="slip_1"
#slipfile="fallas/modelos_restringidos/csv_files/${slip}.csv"
#more ${slipfile} | awk -F","  '{printf"%1.7f %1.7f %1.7f\n",  $1, $2, $3}' | gmt triangulate -G${slip}.grd -I0.1m/0.1m -R -V
#gmt makecpt -Csubtle.cpt -T0/50/0.1 -Z > paletaslip.cpt
#gmt grdimage ${slip}.grd -Cpaletaslip.cpt -B${pticks} -J${projection} -N -Q -R${bounds} ${portrait} ${verbose} -O -K >> ${psfile}


# topobatimetria
paleta="/home/rodrigo/Documents/varios/cpt/bath_112.cpt"    #Paleta de colores a usar
topografia="/home/rodrigo/Documents/varios/w100s10.Bathymetry.srtm.grd" #Archivo de topografia


# Cortando la grilla original a los limites establecidos. 
# grdcut archivo_entrada.grd -Garchivo_salida.grd -Roeste/este/sur/norte [-V] 
#gmt grdcut ${topografia} -G${nombre_mapa}.grd -R${limites} -V 

# Iluminando la grilla topografica generada en el grdcut desde un azimut 
# especifico para producir un archivo de intensidad (.int) de iluminacion:
#gmt grdgradient ${nombre_mapa}.grd -G${nombre_mapa}.int -A${illaz} -Nt -M

# Graficando la topografia de la region seleccionada con su iluminacion:
gmt makecpt -C${paleta} -V -T-6000/0/50 -Z  > paletaoceano.cpt
gmt grdimage ${nombre_mapa}.grd -Cpaletaoceano.cpt  -I${nombre_mapa}.int -B${ticks} -J${proyeccion} -R${limites} \
${portrait} ${verbose} -O -K >> ${psfile}

gmt pscoast -B${pticks} -J${projection} -R${bounds} ${portrait} ${verbose} ${lakes} -D${resolution} -W${coastline} -O -K >> ${psfile}
#gmt pscoast -B${pticks} -J${projection} -R${bounds} ${portrait} ${verbose} -D${resolution} -W${coastline} ${land} -O -K >> ${psfile}


# linea de costa 
gmt pscoast -B${pticks} -J${projection} -R${bounds} ${portrait} ${verbose} -D${resolution} -W${coastline} -O -K >> ${psfile}

# fosa 
gmt psxy SAM.txt -R${bounds} -J${projection} -Sf0.2i/0.1irt -G0 -W0.05c,0 -K -O -V >> ${psfile}
#ridge 
cat ridge.txt | awk '{if (NR>1) print $3, $2}' | gmt psxy -R${bounds} -J${projection} -W2p,0 -B${pticks} -A -O -K >> ${psfile}

# leyendas
more ${rests} | awk -F',' '{if ($1==1960) print $2, $3, $4 }' \
| awk  '{if ($3=="-") printf"%1.1f, %1.1f, %1.1f \n", $1, $2, 0; else printf"%1.1f, %1.1f, %1.1f \n", $1, $2, $3}' \
| awk  '{ if ( $3 >= 0 ) print $0}' | gmt psxy -J -R -P -V -St0.2c -W1.0p,red3  -O -K >> ${psfile}

more ${rests} | awk -F',' '{if ($1==1960) print $2, $3, $4 }' \
| awk  '{if ($3=="-") printf"%1.1f, %1.1f, %1.1f \n", $1, $2, 0; else printf"%1.1f, %1.1f, %1.1f \n", $1, $2, $3}' \
| awk  '{ if ( $3 < 0 ) print $0}' | gmt psxy -J -R -P -V -St0.2c -W1.0p,red3  -O -K >> ${psfile}

# ploteo datos tsunami
more ${datatsunami} | awk -F',' '{printf"%1.1f, %1.1f \n", $1, $2}' | gmt psxy -J -R -P -V -Ss0.2c -W1.0p,midnightblue -O -K >> ${psfile}

# recuadro con leyenda
gmt psxy << END -J -R -P -G255 -V -W1.0p -A -O -K >> ${psfile}
-72.7 -46
-72.7 -47.5
-69.2 -47.5
-69.2 -46
-72.7 -46
END
gmt psxy << END -J -R -P -V -Ss -W1.0p,midnightblue -O -K >> ${psfile}
-72.3 -46.75 0.2
END
gmt psxy << END -J -R -P -V -St -W1.0p,red3 -O -K >> ${psfile}
-72.3 -47.25 0.2
END
# leyenda
gmt pstext << END -R -J -P -V -F+f6p,Helvetica,black -O -K >> ${psfile}
-70.92 -46.75 Tsunami Data
-70.7 -47.25 Deformation Data 
END
#titulo
gmt pstext << END -R -J -P -V -F+f9p,Helvetica-bold,black+jMC -N -O -K >> ${psfile}
-71.0 -46.25 Available Data
END

#more ${deffile} | awk -F"," '{if ($3==0) print $1, $2, "NaN"; else print $1, $2, $3}' | gmt xyz2grd -I0.5s -G${deformacion}.grd -R  

#gmt psscale -D3.8c/-1.5c/8c/0.5ch -Cpaletaslip.cpt -Ba10f5:"Slip [m]": -O >> ${psfile}


# mapa indentado

gmt pscoast -Rg -JG280/-36/1.1i -Da -G128 -A5000 -Bg -Wfaint -ECL+gbisque -O -K -X0.5 -Y9  -V >> ${psfile}
echo ${bounds} | sed 's/\// /g' | awk '{printf"%s %s\n %s %s\n %s %s\n %s %s\n %s %s\n", $1, $3, $2, $3, $2, $4, $1, $4, $1, $3}'    | gmt psxy -R -J -A -W0.5p -O -V >> ${psfile}



evince ${psfile} &