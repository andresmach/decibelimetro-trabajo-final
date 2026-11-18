# graficos.gp — figuras del Capítulo 3 (ejecutar desde anteproyecto/dsp)
set terminal pngcairo size 1500,820 font "Arial,20" linewidth 2
set datafile separator ","
set logscale x
set grid xtics ytics mxtics lc rgb "#dddddd"
set key outside right top
set xlabel "Frecuencia [Hz]"
set ylabel "Ganancia [dB]"
nomb = "125 250 500 1k 2k 4k 8k"
colr = "#1f77b4 #ff7f0e #2ca02c #d62728 #9467bd #8c564b #e377c2"

set output "../figuras/cap3_prototipo_previo.png"
set title "Prototipo previo: un biquad por banda (fs = 51,2 kHz)"
set xrange [10:25600]; set yrange [-40:3]
plot for [i=1:7] "resultados/previo.csv" u 1:(column(i+1)) w l lw 2.5 lc rgb word(colr,i) t word(nomb,i)

set output "../figuras/cap3_banco_n4.png"
set title "Banco propuesto: Butterworth pasabanda de orden 8, multitasa"
set xrange [20:24000]; set yrange [-100:5]
plot for [i=1:7] "resultados/resp_4.csv" u 1:(column(i+1)) w l lw 2.5 lc rgb word(colr,i) t word(nomb,i)

set output "../figuras/cap3_mascara_1k.png"
set title "Banda de 1 kHz frente a la máscara de trabajo IEC 61260-1 clase 1"
set xlabel "Frecuencia normalizada f / f_m"
set ylabel "Ganancia relativa [dB]"
set xrange [1.0/18:18]; set yrange [-90:3]
set xtics ("1/16" 0.0625, "1/8" 0.125, "1/4" 0.25, "1/2" 0.5, "1" 1, "2" 2, "4" 4, "8" 8, "16" 16)
set datafile separator whitespace
plot "resultados/mascara_plot.dat" u 1:2 w lp lw 2 dt 2 pt 5 ps 1 lc rgb "#000000" t "límite superior (atenuación mínima)", \
     "resultados/mascara_plot.dat" u 1:($3 > -150 ? $3 : 1/0) w lp lw 2 dt 3 pt 4 ps 1 lc rgb "#666666" t "límite inferior (atenuación máxima)", \
     "< tr ',' ' ' < resultados/resp_3.csv" u ($1/1000):5 w l lw 2.5 lc rgb "#ff7f0e" t "N = 3 (orden 6)", \
     "< tr ',' ' ' < resultados/resp_4.csv" u ($1/1000):5 w l lw 3 lc rgb "#1f77b4" t "N = 4 (orden 8)"

set output "../figuras/cap3_mascara_1k_detalle.png"
set title "Detalle de la banda de paso (1 kHz)"
set xrange [0.6:1.7]; set yrange [-7:1]
set xtics ("0,7" 0.7, "G^{-1/2}" 0.7079, "0,8" 0.8, "1" 1, "1,2" 1.2, "G^{1/2}" 1.4125, "1,6" 1.6)
set xtics (0.6, 0.7, 0.8, 0.9, 1, 1.2, 1.4, 1.6)
replot

set output "../figuras/cap3_piso_ruido.png"
reset
set terminal pngcairo size 1500,760 font "Arial,20" linewidth 2
set datafile separator whitespace
set title "Piso de ruido estimado por banda frente al límite ISO 8253-1 (valores a verificar)"
set style data histograms
set style histogram clustered gap 1.5
set style fill solid 0.85 border -1
set boxwidth 0.9
set yrange [0:50]
set ylabel "Nivel por banda [dB SPL]"
set xlabel "Banda de octava [Hz]"
set grid ytics lc rgb "#dddddd"
set key top left
plot "resultados/piso_ruido.dat" u 2:xtic(1) t "Límite ISO 8253-1 (tabla del prototipo)" lc rgb "#9e9e9e", \
     "" u 3 t "INMP441 (EIN 33 dBA)" lc rgb "#d62728", \
     "" u 4 t "ICS-43434 (EIN 29 dBA)" lc rgb "#1f77b4"

reset
set terminal pngcairo size 1500,820 font "Arial,20" linewidth 2
set output "../figuras/cap3_e2e_relativa.png"
set multiplot layout 1,2 title "Atenuación relativa extremo a extremo de las 7 bandas (289 tonos por banda) frente a la máscara de trabajo clase 1"
set logscale x
set grid xtics ytics lc rgb "#dddddd"
set xlabel "f / f_m"
set ylabel "Ganancia relativa [dB]"
colr = "#1f77b4 #ff7f0e #2ca02c #d62728 #9467bd #8c564b #e377c2"
nomb = "125 250 500 1k 2k 4k 8k"
G = 10**0.3
set key top left font "Arial,15" maxrows 4 width -2
set xrange [1.0/20:20]; set yrange [-100:3]
set xtics ("1/16" 0.0625, "1/4" 0.25, "1" 1, "4" 4, "16" 16)
set datafile separator ","
plot for [i=1:7] "resultados/e2e_relativa.csv" u (G**$1):(-column(i+1)) w l lw 2 lc rgb word(colr,i) t word(nomb,i), \
     "< tr ' ' ',' < resultados/mascara_plot.dat | grep -v '#'" u 1:2 w l dt 2 lw 2.5 lc rgb "#000000" t "límite"
unset key
set title "Detalle de la banda de paso"
set xrange [0.65:1.55]; set yrange [-6.5:1]
set xtics (0.7, 0.8, 0.9, 1, 1.2, 1.4)
plot for [i=1:7] "resultados/e2e_relativa.csv" u (G**$1):(-column(i+1)) w l lw 2 lc rgb word(colr,i), \
     "< tr ' ' ',' < resultados/mascara_plot.dat | grep -v '#'" u 1:2 w lp dt 2 pt 5 lw 2 lc rgb "#000000", \
     "< tr ' ' ',' < resultados/mascara_plot.dat | grep -v '#'" u 1:($3 > -150 ? $3 : 1/0) w lp dt 3 pt 4 lw 2 lc rgb "#666666"
unset multiplot

reset
set terminal pngcairo size 1500,760 font "Arial,20" linewidth 2
set output "../figuras/cap3_polos_ceros.png"
set multiplot layout 1,2 title "Diagramas de polos (×) y ceros (o) de la banda de 1 kHz"
set size ratio -1
set grid lc rgb "#dddddd"
set xrange [-1.25:1.25]; set yrange [-1.25:1.25]
set xlabel "Re(z)"; set ylabel "Im(z)"
set parametric; set trange [0:2*pi]; set samples 400
set key off
set title "Prototipo previo (1 biquad, f_s = 51,2 kHz)"
plot cos(t), sin(t) w l lc rgb "#888888", \
     "resultados/pz_1k.dat" index 2 u 1:2 w p pt 2 ps 3 lw 3 lc rgb "#d62728", \
     "resultados/pz_1k.dat" index 3 u 1:2 w p pt 6 ps 3 lw 3 lc rgb "#1f77b4"
set title "Propuesto (Butterworth orden 8, f_s = 6 kHz)"
set label 1 "×4" at 1.05,0.18 font "Arial,16"
set label 2 "×4" at -1.18,0.18 font "Arial,16"
plot cos(t), sin(t) w l lc rgb "#888888", \
     "resultados/pz_1k.dat" index 0 u 1:2 w p pt 2 ps 3 lw 3 lc rgb "#d62728", \
     "resultados/pz_1k.dat" index 1 u 1:2 w p pt 6 ps 3 lw 3 lc rgb "#1f77b4"
unset multiplot
