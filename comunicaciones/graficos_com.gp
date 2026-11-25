# graficos_com.gp — figuras del Capítulo 6 (ejecutar desde anteproyecto/comunicaciones)
set terminal pngcairo size 1100,700 font "Arial,22" linewidth 2
set decimalsign ","
set datafile separator ","
set output "../figuras/cap6_enlace.png"
set title "Margen del enlace equipo → celular"
set xlabel "Atenuación de la cabina [dB]"; set ylabel "Margen sobre la sensibilidad [dB]"
set grid lc rgb "#dddddd"
set xrange [0:60]; set yrange [-20:60]
set arrow 1 from 0,10 to 60,10 nohead dt 2 lw 2 lc rgb "#d62728"
set label 1 "margen exigido: 10 dB" at 2,13 tc rgb "#d62728" font "Arial,18"
set arrow 2 from 0,0 to 60,0 nohead lw 1 lc rgb "#888888"
set key top right font "Arial,18"
plot "resultados/margen_enlace.csv" u 1:2 w l lw 3 lc rgb "#9ecae1" t "3 m, 8,5 dBm", \
     "" u 1:3 w l lw 3 lc rgb "#1f77b4" t "3 m, 13 dBm (propuesto)", \
     "" u 1:4 w l lw 3 lc rgb "#08306b" t "3 m, 19,5 dBm", \
     "" u 1:5 w l lw 3 dt 2 lc rgb "#1f77b4" t "10 m, 13 dBm"
unset arrow; unset label
set output "../figuras/cap6_sesgo.png"
set title "Promediar niveles en dB subestima el L_{eq}"
set xlabel "Desvío estándar de la fluctuación del nivel [dB]"; set ylabel "L_{eq} − promedio de niveles [dB]"
set xrange [0:6]; set yrange [0:4.5]
set key top left font "Arial,18"
plot "resultados/sesgo_db.csv" u 1:2 w p pt 7 ps 1.4 lc rgb "#d62728" t "simulación (20 000 valores)", \
     "" u 1:3 w l lw 3 lc rgb "#333333" t "0,115·σ² (ruido log-normal)"
