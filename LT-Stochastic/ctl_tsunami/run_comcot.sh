#!/bin/bash 
archivo_def=$(ls deformacion_*.xyz)
more ${archivo_def} |  awk '{printf"%3.8f %2.8f %2.8f \n", $1+360, $2, $3}' > ${archivo_def}.bu && rm ${archivo_def} && mv ${archivo_def}.bu ${archivo_def}
wine comcot.exe 