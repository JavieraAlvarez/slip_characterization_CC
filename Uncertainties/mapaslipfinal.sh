"""
Slip Pattern final map for Historical Seismic Events (1730, 1906, 1985)
Javiera Álvarez, 2024
GMT 6.5
"""

!/bin/bash
for slip in $(ls /Users/javieraalvarezvargas/Desktop/modelos/milsietetreinta/filtrados72/slip_*.csv | awk -F"/" '{print $NF}' | awk -F"." '{print $1}');
do

region="${slip}"
bounds="-75/-69/-39/-26"
projection="M8.0"
sticks="a2f1SEwn"
portrait="-P"
verbose="-V"
coastline="0.5p,0/0/0"
resolution="f"
land="-Gwhite"
lakes="-C255/255/255 -A0/2/4"
psfile="${region}.ps"
pngfile="${region}.png"
rosa="dg-78/-36+w1c+f+l,,,n"
trench_file="/Users/javieraalvarezvargas/Desktop/modelos/milsietetreinta/trench-chile"  
ridge_file="/Users/javieraalvarezvargas/Desktop/modelos/milsietetreinta/ridge.txt"    

# constrained slips
slipfile="/Users/javieraalvarezvargas/Desktop/modelos/milsietetreinta/filtrados72/${slip}.csv"

# ########################################
#  basemap and titles
# ########################################
gmt psbasemap -Ba1/a1SneW -J${projection} -R${bounds} -X2 -Y6 ${portrait} ${verbose} -K > ${psfile}
gmt pstext -J -R -P -F+f16p,Helvetica-Bold+jTL -N -O -K << END >> ${psfile}
-73 -24.5 1730 Event
END
gmt pstext -J -R -P -F+f12p,Helvetica+jTL -N -O -K << END >> ${psfile}
-72.75 -25 Vertical Slip
END

# coast
gmt pscoast -Ba1/a1neW -J${projection} -R${bounds} ${portrait} ${verbose} -D${resolution} -W${coastline} ${land} -O -K >> ${psfile}
gmt pscoast -Ba1/a1SneW -J${projection} -R${bounds} ${portrait} ${verbose} ${lakes} -D${resolution} -W${coastline} -O -K >> ${psfile}

# ########################################
# vertical displacement
# ########################################

awk -F"," '{printf"%1.7f %1.7f %1.7f\n",  $1, $2, $3}' ${slipfile} | gmt triangulate -G${slip}.grd -I0.1m/0.1m -R${bounds} -V -S50k

# cpt
gmt makecpt -Cblue,cyan,yellow,orange,red -T0/26/1 -Z > paletaslip.cpt

# -----------------------------------------
# from the trench to the coast, cut
# -----------------------------------------
# out of trench -> Nan
gmt grdmask ${trench_file} -R${bounds} -I0.1m/0.1m -Gmask.grd -N1/NaN/NaN -V
gmt grdmath ${slip}.grd mask.grd MUL = ${slip}_masked.grd

gmt grdimage ${slip}_masked.grd -Cpaletaslip.cpt -Bxa2f1 -Bya2f1 -J${projection} -R${bounds} ${portrait} ${verbose} -O -K >> ${psfile}
gmt pscoast -R${bounds} -J${projection} -D${resolution} -W${coastline} -O -K >> ${psfile}

# ########################################
# final contours
# ########################################
gmt grdcontour ${slip}_masked.grd -R${bounds} -J${projection} -C2 -L5/28 -A+a0+f5p,Helvetica-Bold,black -W0.5p,black,- ${portrait} ${verbose} -O -K >> ${psfile}

# ########################################
# color scale
# ########################################
gmt psscale -D3.8c/-1.5c/8c/0.5ch -Cpaletaslip.cpt -Ba5f5+l"Slip [m]" -O -K >> ${psfile}

# ########################################
# text
# ########################################
gmt pstext -R -J -O -K -F+f10p+jCM <<EOF >> ${psfile}
-70.10914 -27.36679 6 0 0 LM Copiapo
-71.04894 -29.78453 6 0 0 LM La Serena
-71.10947 -30.05332 6 0 0 LM Coquimbo
-71.14882 -32.58341 6 0 0 LM Quillota
-71.52963 -33.121 6 0 0 LM Valparaíso
-70.44827 -33.45694 6 0 0 LM Santiago
-70.74407 -34.44214 6 0 0 LM Malloa
-71.73643 -34.60972 6 0 0 LM Alcantara
-70.93943 -34.98279 6 0 0 LM Curicó
-72.2 -35.0867 6 0 0 LM Higuerilla
-71.0 -35.1833 6 0 0 LM La Huerta
-71.90344 -36.60664 6 0 0 LM Chillán
-72.84977 -36.82699 6 0 0 LM Concepción
-68.62717 -32.89084 6 0 0 LM Mendoza
EOF

# afected cities
gmt psxy -R -J -O -K -Sc0.1i -W0.2p,black -Gwhite <<EOF >> ${psfile}
-70.3314 -27.36679 # Copiapo
-71.24894 -29.90453 # La Serena
-71.33947 -30.05332 # Coquimbo
-71.24882 -32.88341 # Quillota
-71.62963 -32.921 # Valparaíso
-70.64827 -33.45694 # Santiago
-70.94407 -34.44214 # Malloa
-71.83643 -34.76972 # Alcantara
-71.23943 -34.98279 # Curicó
-72.1 -34.8667 # Higuerilla
-71.1 -34.9833 # La Huerta
-72.10344 -36.60664 # Chillán
-73.04977 -36.82699 # Concepción
-68.82717 -32.89084 # Mendoza
EOF

# reported deformations
gmt psxy -R -J -O -K -Si0.1i -W0.15p,black -Gblack<<EOF >> ${psfile}
-71.6281 -33.6358 -1000
-71.4145 -33.4448 -1000
-72.0259 -34.4059 1000
-71.6272 -33.0393 1000
-71.2489 -29.9045 1000
-73.0497 -36.8269 -1000
EOF

# reported tsunami
gmt psxy -R -J -O -K -Sc0.07i -W0.1p,black -Gred<<EOF >> ${psfile}
-71.60048 -33.03949
-72.99528 -36.74075
-72.99510 -36.73846
-72.99635 -36.73881
-72.99592 -36.73871
-72.99431 -36.73787
-72.99605 -36.73461
-71.61269 -33.04724
-71.63186 -33.03639
EOF

# ########################################
# trench
# ########################################
gmt psxy ${trench_file} -R${bounds} -J${projection} -Sf0.2i/0.1i+t+l -G0 -W1p,black -O -K >> ${psfile}

# ridge 
awk '{if (NR>1) print $3, $2}' ${ridge_file} | gmt psxy -R${bounds} -J${projection} -W2p,black -O -K >> ${psfile}

# ########################################
# Legend 
# ########################################

gmt pslegend -R -J -Dx3.0i/0.3i+w2.0i+jBR -F+p0.5p+gwhite -C0.1i/0.1i -O <<EOF >> ${psfile}
S 0.07i c 0.08i white 0.3p 0.4i Localities
G 0.05i
S 0.07i c 0.08i red 0.3p 0.4i Tsunami report
G 0.05i
S 0.07i i 0.08i black 0.3p 0.4i Deformation report
EOF


# ########################################
# output
# ########################################
destino="/Users/javieraalvarezvargas/Desktop/modelos/milsietetreinta/figuras_nuevo"
mv ${psfile} ${destino}
for psfile in ${destino}/*.ps; do
    gmt psconvert ${psfile} -Tg -A -P
done

done
