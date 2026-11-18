# graficos_rt.gp — figuras del Capítulo 4 (ejecutar desde anteproyecto/rtos)
set terminal pngcairo size 1500,700 font "Arial,20" linewidth 2
set datafile separator ","
set output "../figuras/cap4_ocupacion_dma.png"
set title "Ocupación del anillo DMA ante una detención de 100 ms del núcleo DSP (C pesimista = 6,2 ms)"
set xlabel "Tiempo [ms]"; set ylabel "Ocupación del anillo [%]"
set grid lc rgb "#dddddd"
set yrange [0:110]; set xrange [0:400]
set object 1 rect from 100,0 to 200,110 fc rgb "#f3e8f7" fs solid 0.6 noborder behind
set label 1 "núcleo 1 detenido" at 104,30 font "Arial,17" tc rgb "#6a1b9a"
set arrow 1 from 0,100 to 400,100 nohead dt 2 lc rgb "#d62728"
set label 2 "anillo lleno: se pierden muestras" at 215,95 font "Arial,16" tc rgb "#d62728"
set key top left
plot "resultados/ocupacion_8.csv" u 1:2 w l lw 3 lc rgb "#d62728" t "8 descriptores (75 ms útiles)", \
     "resultados/ocupacion_16.csv" u 1:2 w l lw 3 lc rgb "#1f77b4" t "16 descriptores (160 ms útiles)"
