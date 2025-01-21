#!/bin/bash
#script written to plot the station delays in GMT5
for slip in $(ls /media/ignacia/Elements/Matias/Mati1730/bundle/fallas/modelos_restringidos_coincidencia_final/slip_*.csv | awk -F"/" '{print $NF}' | awk -F"." '{print $1}');
do

region="${slip}"
bounds="-75/-69/-39/-26"
projection="M8.0"
#pticks="a1f1WesN"
sticks="a2f1SEwn"
portrait="-P"
verbose="-V"
coastline="0.5p,0/0/0"
resolution="f"	
land="-Gwhite"
lakes="-C255/255/255 -A0/2/4"
psfile="${region}.ps"
pngfile="${region}.png"
#rests="input/restricciones.csv"
rosa="dg-78/-36+w1c+f+l,,,n"
########################################
#p delays
####################
#basemap and coast
gmt psbasemap -Ba1/a1SneW -J${projection} -R${bounds}  -X2 -Y6 ${portrait} ${verbose} -K > ${psfile}

# Agrega el título principal
gmt pstext -J -R -P -F+f16p,Helvetica-Bold+jTL -N -O -K << END >> ${psfile}
-73 -25 1730 Event
END

# Agrega el subtítulo
gmt pstext -J -R -P -F+f12p,Helvetica+jTL -N -O -K << END >> ${psfile}
-72.75 -25.5 Vertical Slip
END

gmt pscoast -Ba1/a1neW -J${projection} -R${bounds} ${portrait} ${verbose} -D${resolution} -W${coastline} ${land} -O -K >> ${psfile}
gmt pscoast -Ba1/a1SneW -J${projection} -R${bounds} ${portrait} ${verbose} ${lakes} -D${resolution} -W${coastline} -O -K >> ${psfile}


# deformacion
#slip="slip_1"
slipfile="/media/ignacia/Elements/Matias/Mati1730/bundle/fallas/modelos_restringidos_coincidencia_final/${slip}.csv"
more ${slipfile} | awk -F","  '{printf"%1.7f %1.7f %1.7f\n",  $1, $2, $3}' | gmt triangulate -G${slip}.grd -I0.1m/0.1m -R -V -S50k
cptfile="/media/ignacia/Elements/Matias/Mati1730/bundle/paletas/subtle.cpt"
#cptfile2="/home/ignacia/Documentos/Javiera2/bundle/paletas/paletaslip.cpt"
#gmt makecpt -C${cptfile} -T0/50/0.1 -Z > ${cptfile2}
#gmt makecpt -Cjet -T0/20/0.1 -Z -D > paletaslip.cpt


gmt makecpt -Cblue,cyan,yellow,orange,red -T0/20/0.1 > paletaslip.cpt

gmt grdimage ${slip}.grd -Cpaletaslip.cpt -Bn${pticks} -J${projection} -N -Q -R${bounds} ${portrait} ${verbose} -O -K >> ${psfile}
gmt pscoast -B${pticks} -J${projection} -R${bounds} ${portrait} ${verbose} -D${resolution} -W${coastline} -O -K >> ${psfile}

#contornos
gmt grdcontour ${slip}.grd -J${projection} -B${pticks} -C1 -L0/15 -A10+f5p -W0.01c,black,- ${portrait} ${verbose} -O -K >> ${psfile}


# fosa 
gmt psxy SAM.txt -R${bounds} -J${projection} -Sf0.2i/0.1irt -G0 -W0.05c,0 -K -O -V >> ${psfile}
#ridge 
cat ridge.txt | awk '{if (NR>1) print $3, $2}' | gmt psxy -R${bounds} -J${projection} -W2p,0 -B${pticks} -A -O -K >> ${psfile}

# leyendas
more ${rests} | awk -F',' '{if ($1==1730) print $2, $3, $4 }' \
| awk  '{if ($3=="-") printf"%1.1f, %1.1f, %1.1f \n", $1, $2, 0; else printf"%1.1f, %1.1f, %1.1f \n", $1, $2, $3}' \
| awk  '{ if ( $3 >= 0 ) print $0}' | gmt psxy -J -R -P -V -Si-0.15c -W1.0p,red3 -O -K >> ${psfile}

more ${rests} | awk -F',' '{if ($1==1730) print $2, $3, $4 }' \
| awk  '{if ($3=="-") printf"%1.1f, %1.1f, %1.1f \n", $1, $2, 0; else printf"%1.1f, %1.1f, %1.1f \n", $1, $2, $3}' \
| awk  '{ if ( $3 < 0 ) print $0}' | gmt psxy -J -R -P -V -Sc0.15c -W1.0p,blue -O -K >> ${psfile}

# recuadro con leyenda
gmt psxy << END -J -R -P -G255 -V -W2.0p -O -K >> ${psfile}
-72 -37
-72 -38
-69.5 -38
-69.5 -37
-72 -37
END
gmt psxy << END -J -R -P -V -Sc -W2.0p,blue -O -K >> ${psfile}
-71.7 -37.25 0.2
-71.6272 -33.0393 0.2
-73.0497 -36.8269 0.2
-71.2489 -29.9045 0.2
END
gmt psxy << END -J -R -P -V -Si -W2.0p,red3 -O -K >> ${psfile}
-71.7 -37.75 .2
-71.2 -33.6358 0.2
-71 -33.4448 0.2
-71.9 -34.4059 0.2
END
# leyenda
gmt pstext << END -R -J -P -V -F+10p,Helvetica-bold,black+jMC -N -O -K >> ${psfile}
-70.5 -37.25 Relevant point 
#END
#leyenda
gmt pstext << END -R -J -P -V -F+f10p,Helvetica-bold,black+jMC -N -O -K >> ${psfile}
-70.5 -37.75 Uplift
END


#more ${deffile} | awk -F"," '{if ($3==0) print $1, $2, "NaN"; else print $1, $2, $3}' | gmt xyz2grd -I0.5s -G${deformacion}.grd -R  
gmt psscale -D3.8c/-1.5c/8c/0.5ch -Cpaletaslip.cpt -Ba5f5:"Slip [m]": -O >> ${psfile}


destino="/media/ignacia/Elements/Matias/Mati1730/bundle/figuras2"

mv ${psfile} ${destino}
for psfile in ${destino}/*.ps; do
gmt psconvert ${psfile} -Tg -A -P
done
#mv ${pngfile} ${destino}
#echo "copiado ${pngfile} a ${destino}"

done
#evince ${psfile} & 
