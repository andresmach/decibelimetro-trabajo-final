# graficos_hw.gp — figuras del Capítulo 5 (ejecutar desde anteproyecto/hw)
set terminal pngcairo size 1500,720 font "Arial,20" linewidth 2
set datafile separator ","
set output "../figuras/cap5_autonomia.png"
set multiplot layout 1,2
set title "Autonomía según la corriente media (LDO)"
set xlabel "Corriente media del sistema [mA]"; set ylabel "Autonomía [h]"
set grid lc rgb "#dddddd"
set xrange [100:280]; set yrange [0:32]
set arrow 1 from 100,8 to 280,8 nohead dt 2 lw 2 lc rgb "#d62728"
set label 1 "RD-08: 8 h" at 104,9.2 tc rgb "#d62728" font "Arial,16"
set arrow 2 from 173.7,0 to 173.7,32 nohead dt 3 lw 2 lc rgb "#555555"
set label 2 "modo medición" at 176,2 font "Arial,15"
set arrow 3 from 223.7,0 to 223.7,32 nohead dt 3 lw 2 lc rgb "#555555"
set label 3 "peor caso" at 226,2 font "Arial,15"
set key top right font "Arial,15"
plot "resultados/autonomia.csv" u 1:2 w l lw 3 lc rgb "#1f77b4" t "18650 2600 mAh", \
     "" u 1:3 w l lw 2 dt 2 lc rgb "#1f77b4" t "2600 mAh, fin de vida y 10 °C", \
     "" u 1:4 w l lw 3 lc rgb "#2ca02c" t "18650 3000 mAh", \
     "" u 1:5 w l lw 2 dt 2 lc rgb "#2ca02c" t "3000 mAh, fin de vida y 10 °C"
unset arrow; unset label
set title "Tensión de una celda Li-ion y límites de los reguladores"
set xlabel "Estado de carga [%]"; set ylabel "Tensión a circuito abierto [V]"
set xrange [100:0]; set yrange [3.0:4.3]
set arrow 1 from 100,3.54 to 0,3.54 nohead dt 2 lw 2 lc rgb "#d62728"
set label 1 "corte del firmware (VSYS 3,50 V con carga): 94 % utilizable" at 98,3.58 tc rgb "#d62728" font "Arial,14"
set arrow 2 from 100,3.31 to 0,3.31 nohead dt 2 lw 2 lc rgb "#9467bd"
set label 2 "buck-boost (hasta 3,2 V con carga): 98 %" at 98,3.35 tc rgb "#9467bd" font "Arial,14"
unset key
plot "resultados/ocv.csv" u 1:2 w lp pt 7 ps 0.8 lw 3 lc rgb "#333333"
unset multiplot
