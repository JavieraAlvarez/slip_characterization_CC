#!/bin/bash

for deformacion in $(ls /home/ignacia/Documentos/Javiera2/1906/bundle/fallas/defiles/deformacion_*.csv | awk -F"/" '{print $10}' | awk -F"." '{print $1}');
do



#script written to plot the station delays in GMT5
region="${deformacion}"
bounds="-75/-69/-39/-30"
projection="M8.0"
pticks="a2f1SeWn"
sticks="a2f1SEwn"
portrait="-P"	
verbose="-V"
coastline="0.5p,0/0/0"
resolution="f"	
land="-G175/175/175"
lakes="-C255/255/255 -A0/2/4"
psfile="${region}.ps"
#rests="input/restricciones.csv"
rosa="dg-78/-36+w1c+f+l,,,n"
########################################
#p delays
####################
#basemap and coast
gmt psbasemap -B${pticks} -J${projection} -R${bounds}  -X2 -Y6 ${portrait} ${verbose} -K > ${psfile}
gmt pscoast -B${pticks} -J${projection} -R${bounds} ${portrait} ${verbose} -D${resolution} -W${coastline} ${land} -O -K >> ${psfile}
gmt pscoast -B${pticks} -J${projection} -R${bounds} ${portrait} ${verbose} ${lakes} -D${resolution} -W${coastline} -O -K >> ${psfile}


# deformacion
paleta="/home/ignacia/Documentos/Javiera2/1906/bundle/paletas/French_flag_smooth.cpt"
def="/home/ignacia/Documentos/Javiera2/1906/bundle/paletas/paletadeformacion.cpt"
deffile="/home/ignacia/Documentos/Javiera2/1906/bundle/fallas/defiles/${deformacion}.csv"
more ${deffile} | awk -F","  '{printf"%1.7f %1.7f %1.7f\n",  $1, $2, $3}' | awk  '{if (($3)<0.01 && ($3)>-0.01 ) print $1, $2, "NaN"; else print $1, $2, $3}' | gmt triangulate -G${deformacion}.grd -I0.1m/0.1m -R -V
gmt makecpt -C${paleta} -T-0.05/0.05/0.001 -Z > paletadeformacion.cpt
gmt grdimage ${deformacion}.grd -Cpaletadeformacion.cpt -B${pticks} -J${projection} -N -Q -R${bounds} ${portrait} ${verbose} -O -K >> ${psfile}
gmt pscoast -B${pticks} -J${projection} -R${bounds} ${portrait} ${verbose} -D${resolution} -W${coastline} -O -K >> ${psfile}

# fosa 
gmt psxy SAM.txt -R${bounds} -J${projection} -Sf0.2i/0.1irt -G0 -W0.05c,0 -K -O -V >> ${psfile}
#ridge 
cat ridge.txt | awk '{if (NR>1) print $3, $2}' | gmt psxy -R${bounds} -J${projection} -W2p,0 -B${pticks} -A -O -K >> ${psfile}

# leyendas
more ${rests} | awk -F',' '{if ($1==1906) print $2, $3, $4 }' \
| awk  '{if ($3=="-") printf"%1.1f, %1.1f, %1.1f \n", $1, $2, 0; else printf"%1.1f, %1.1f, %1.1f \n", $1, $2, $3}' \
| awk  '{ if ( $3 >= 0 ) print $0}' | gmt psxy -J -R -P -V -S-0.15c -W1.0p,red3 -O -K >> ${psfile}

more ${rests} | awk -F',' '{if ($1==1906) print $2, $3, $4 }' \
| awk  '{if ($3=="-") printf"%1.1f, %1.1f, %1.1f \n", $1, $2, 0; else printf"%1.1f, %1.1f, %1.1f \n", $1, $2, $3}' \
| awk  '{ if ( $3 < 0 ) print $0}' | gmt psxy -J -R -P -V -Sc0.15c -W1.0p,blue -O -K >> ${psfile}

# recuadro con leyenda
gmt psxy << END -J -R -P -G255 -V -W1.0p -O -K >> ${psfile}
-72 -37.5
-72 -38.5
-70 -38.5
-70 -37.5
-72 -37.5
END
gmt psxy << END -J -R -P -V -Sc- -W1.0p,blue -O -K >> ${psfile}
-71.7 -38 .15
-71.518 -31.912 0.15
-71.532 -32.136 0.15
-71.446 -32.507 0.15
-71.455 -32.556 0.15
-71.515 -32.921 0.15
-71.550 -33.921 0.15
-71.675 -33.364 0.15
-71.604 -33.548 0.15
-71.875 -33.963 0.15
-72.001 -34.386 0.15
-72.011 -34.496 0.15
-72.061 -34.775 0.15
-72.183 -34.941 0.15
-72.411 -35.331 0.15
END
# leyenda
gmt pstext << END -R -J -P -V -F+f10p,Helvetica,black -O -K >> ${psfile}
-71.3 -38 Uplift
END
#titulo
gmt pstext << END -R -J -P -V -F+f12p,Helvetica-bold,black+jMC -N -O -K >> ${psfile}
-71 -37.7 Vertical Disp.
END

#more ${deffile} | awk -F"," '{if ($3==0) print $1, $2, "NaN"; else print $1, $2, $3}' | gmt xyz2grd -I0.5s -G${deformacion}.grd -R  

gmt psscale -D3.8c/-1.5c/8c/0.5ch -Cpaletadeformacion.cpt -Ba0.05f0.05:"Deformation [m]": -O >> ${psfile}


destino="/home/ignacia/Documentos/Javiera2/1906/bundle/figurasdef"

mv ${psfile} ${destino}
echo "copiado ${psfile} a ${destino}"
done

evince ${psfile} &
