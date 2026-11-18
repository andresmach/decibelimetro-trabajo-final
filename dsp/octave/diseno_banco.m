% diseno_banco.m — Diseño y verificación del banco de filtros de octava
% Analizador de ruido ambiente ISO 8253-1 (Capítulo 3, DSP)
%
% Uso (desde anteproyecto/dsp):  octave --no-gui octave/diseno_banco.m
%
% Genera en resultados/:
%   resumen.txt            tablas de verificación (máscara, ancho de banda, polos)
%   resp_<N>.csv           respuesta analítica de cada banda (orden de prototipo N)
%   e2e.csv                respuesta extremo a extremo simulada (cadena multitasa)
%   mascara.csv            máscara de trabajo IEC 61260-1 clase 1 / clase 2
%   octave_coeffs.h        coeficientes SOS en float32 para ESP-DSP
%
% NOTA: los límites de la máscara son VALORES DE TRABAJO a verificar contra la
% Tabla 1 de IEC 61260-1:2014 (texto con acceso restringido).

pkg load signal
addpath(fileparts(mfilename("fullpath")));
more off
outdir = 'resultados';
if ~exist(outdir, 'dir'), mkdir(outdir); end
fid = fopen(fullfile(outdir, 'resumen.txt'), 'w');
out = @(varargin) fprintf(fid, varargin{:});

%% Parámetros
FS   = 48000;                 % frecuencia de muestreo del I2S
G    = 10^(3/10);             % razón de octava en base 10 (IEC 61260-1)
k    = -3:3;                  % índices de banda: 125 Hz ... 8 kHz
fm   = 1000 * G.^k;           % frecuencias medias exactas
fnom = [125 250 500 1000 2000 4000 8000];
f1   = fm * G^(-1/2);         % borde inferior
f2   = fm * G^(1/2);          % borde superior
nb   = numel(fm);
fsb  = FS ./ 2.^(3 - k);      % tasa de cada banda: 750 Hz ... 48 kHz

% Máscara de trabajo (atenuación relativa en dB; exponente de G)
%   x       min_c1  max_c1  min_c2  max_c2
M = [0      -0.4    0.4    -0.6    0.6
     1/8    -0.4    0.6    -0.6    0.8
     1/4    -0.4    0.8    -0.6    1.1
     3/8    -0.4    1.4    -0.6    1.9
     1/2     1.2    5.3     0.4    5.8
     1       17.5   Inf     16.5   Inf
     2       42.5   Inf     41.5   Inf
     3       62.0   Inf     55.0   Inf
     4       75.0   Inf     60.0   Inf];
csvwrite(fullfile(outdir, 'mascara.csv'), M);

%% Filtro diezmador (común a todas las etapas, normalizado a la tasa de entrada)
% Banda de paso hasta el borde superior de la banda siguiente (f2/fs_in = 0.1177)
% Banda de rechazo desde 0.382*fs_in (lo que se plegaría sobre las bandas útiles)
wp = 0.1180 * 2;              % normalizado a Nyquist
[zd, pd, kd] = ellip(6, 0.01, 80, wp);
sosd = zp2sos(zd, pd, kd);
HW = sosresp(sosd, 4096); Hd = HW(:,1); wd = real(HW(:,2));
Hd_db = 20*log10(abs(Hd) + eps);
fd = wd / pi / 2;             % en fracción de fs_in
idx_stop = find(fd >= 0.382, 1);
out('== Filtro diezmador (elíptico, orden 6, 3 SOS) ==\n');
out('Ondulación en banda de paso (0 a 0.118 fs): %.3f dB\n', ...
    max(Hd_db(fd <= 0.118)) - min(Hd_db(fd <= 0.118)));
out('Atenuación mínima desde 0.382 fs: %.1f dB\n', -max(Hd_db(idx_stop:end)));
out('Radio máximo de polos: %.4f\n\n', max(abs(pd)));

%% Diseño de bandas para dos órdenes de prototipo
f_eval = logspace(log10(10), log10(23999), 4000);
res = struct();
for N = [3 4]
  out('== Prototipo Butterworth N = %d (pasabanda de orden %d, %d SOS) ==\n', N, 2*N, N);
  out('banda  fm[Hz]   fs[Hz]  |p|max   margen_min_c1[dB]  dB_en_fm  dB_bordes      dB_err_ancho\n');
  R = zeros(numel(f_eval), nb);
  for b = 1:nb
    Wn = [f1(b) f2(b)] / (fsb(b)/2);
    [z, p, g] = butter(N, Wn);        % bilineal con predistorsión de los bordes
    sos = zp2sos(z, p, g);
    res(N).sos{b} = sos;
    % respuesta analítica a la tasa propia (solo f < fs_b/2)
    fe = f_eval(f_eval < fsb(b)/2);
    H = sosresp(sos, fe, fsb(b));
    A = -20*log10(abs(H) + eps);      % atenuación relativa (dB)
    R(1:numel(fe), b) = -A;
    R(numel(fe)+1:end, b) = NaN;
    % margen contra la máscara clase 1 (ambos lados)
    marg = Inf;
    for r = 1:rows(M)
      for s = [-1 1]
        fx = fm(b) * G^(s*M(r,1));
        if fx >= fsb(b)/2, continue; end
        a = -20*log10(abs(sosresp(sos, fx, fsb(b)))(1));
        marg = min([marg, a - M(r,2), M(r,3) - a]);
      end
    end
    a_fm = -20*log10(abs(sosresp(sos, fm(b), fsb(b)))(1));
    a_e  = -20*log10(abs(sosresp(sos, [f1(b) f2(b)], fsb(b))));
    % desviación del ancho de banda efectivo (escala logarítmica)
    fl = logspace(log10(fm(b)/G^5), log10(min(fm(b)*G^5, 0.499*fsb(b))), 20000);
    Hl = abs(sosresp(sos, fl, fsb(b))).^2;
    Be = trapz(log10(fl(:)), Hl) / abs(sosresp(sos, fm(b), fsb(b)))(1)^2;
    dB_bw = 10*log10(Be / log10(G));
    res(N).marg(b) = marg; res(N).dbw(b) = dB_bw;
    out('%5d %8.2f %7d  %.4f   %8.2f         %6.3f   %5.2f / %5.2f   %+6.3f\n', ...
        fnom(b), fm(b), fsb(b), max(abs(p)), marg, a_fm, a_e(1), a_e(2), dB_bw);
  end
  dlmwrite(fullfile(outdir, sprintf('resp_%d.csv', N)), [f_eval(:) R], 'precision', '%.6g');
  % Sensibilidad a la cuantización float32 de los coeficientes
  dmax = 0;
  for b = 1:nb
    sos = res(N).sos{b};
    fe = logspace(log10(f1(b)/G^2), log10(min(f2(b)*G^2, 0.49*fsb(b))), 800);
    H64 = 20*log10(abs(sosresp(sos, fe, fsb(b))));
    H32 = 20*log10(abs(sosresp(double(single(sos)), fe, fsb(b))));
    sel = H64 > -40;
    dmax = max(dmax, max(abs(H64(sel) - H32(sel))));
  end
  out('Máx. diferencia float32 vs float64 (zona > -40 dB): %.2e dB\n\n', dmax);
end

%% Cadena multitasa completa: simulación temporal con tonos (orden elegido)
NSEL = 4;
out('== Verificación extremo a extremo (simulación temporal, N = %d) ==\n', NSEL);
ftest = logspace(log10(20), log10(23000), 260);
T = 2.0;                               % s de señal por tono
nT = round(T*FS); t = (0:nT-1)'/FS;
E = zeros(numel(ftest), nb);
for it = 1:numel(ftest)
  x = sin(2*pi*ftest(it)*t);
  ref = 0.5;                           % potencia del seno de amplitud 1
  xs = x;
  for b = nb:-1:1                      % de 8 kHz hacia 125 Hz
    y = sosfilt(res(NSEL).sos{b}, xs);
    y = y(round(end/2):end);           % descarta el transitorio
    E(it, b) = 10*log10(mean(y.^2)/ref + 1e-20);
    if b > 1
      xs = sosfilt(sosd, xs);          % antialias
      xs = xs(1:2:end);                % diezmado por 2
    end
  end
end
dlmwrite(fullfile(outdir, 'e2e.csv'), [ftest(:) E], 'precision', '%.6g');

% Verificación densa contra la máscara (atenuación RELATIVA, IEC 61260-1):
% dA_b(f) = A_b(f) - A_ref, con A_ref = atenuación de la banda de 1 kHz a 1 kHz.
% La máscara se interpola linealmente en el exponente de G entre puntos de quiebre.
function A = e2e_aten(f, b, sosb, sosd, FS, nb, T)
  t = (0:round(T*FS)-1)'/FS; xs = sin(2*pi*f*t);
  for bb = nb:-1:b+1, xs = sosfilt(sosd, xs); xs = xs(1:2:end); end
  y = sosfilt(sosb, xs); y = y(round(end/2):end);
  A = -10*log10(mean(y.^2)/0.5 + 1e-30);
end
function [lo, hi] = mask_at(x, M, cmin, cmax)
  ax = abs(x); xs = M(:,1);
  if ax >= xs(end), lo = M(end,cmin); else, lo = interp1(xs, M(:,cmin), ax); end
  mx = M(:,cmax); i = find(isfinite(mx), 1, 'last');
  if ax <= xs(i), hi = interp1(xs(1:i), mx(1:i), ax); else, hi = Inf; end
end
Tv = 4.0;
Aref = e2e_aten(1000, 4, res(NSEL).sos{4}, sosd, FS, nb, Tv);
xg = -4.5:1/32:4.5;
DA = nan(numel(xg), nb);
out('\n== Verificación densa (%d tonos por banda, x de -4,5 a 4,5 en pasos de 1/32) ==\n', numel(xg));
out('A_ref (1 kHz en 1 kHz) = %.4f dB\n', Aref);
out('banda  dA(fm)[dB]  margen_paso_c1  margen_rechazo_c1  margen_paso_c2  margen_rechazo_c2  peor_x_rechazo\n');
for b = 1:nb
  mp1 = Inf; mr1 = Inf; mp2 = Inf; mr2 = Inf; px = NaN;
  for ix = 1:numel(xg)
    f = fm(b) * G^xg(ix);
    if f >= FS/2 || f < 2, continue; end
    a = e2e_aten(f, b, res(NSEL).sos{b}, sosd, FS, nb, Tv) - Aref;
    DA(ix, b) = a;
    [l1, h1] = mask_at(xg(ix), M, 2, 3); [l2, h2] = mask_at(xg(ix), M, 4, 5);
    m1 = min(a - l1, h1 - a); m2 = min(a - l2, h2 - a);
    if abs(xg(ix)) <= 0.5
      mp1 = min(mp1, m1); mp2 = min(mp2, m2);
    else
      if m1 < mr1, mr1 = m1; px = xg(ix); end
      mr2 = min(mr2, m2);
    end
  end
  dfm = e2e_aten(fm(b), b, res(NSEL).sos{b}, sosd, FS, nb, Tv) - Aref;
  out('%5d   %+7.3f     %7.2f          %7.2f            %7.2f          %7.2f         %+.3f\n', ...
      fnom(b), dfm, mp1, mr1, mp2, mr2, px);
end
dlmwrite(fullfile(outdir, 'e2e_relativa.csv'), [xg(:) DA], 'precision', '%.6g');

%% Costo computacional estimado
nsos = NSEL*nb + 3*(nb-1);
mult = 0;
for b = 1:nb
  mult += 5*NSEL*fsb(b);               % 5 multiplicaciones por SOS y muestra
  if b < nb, mult += 5*3*fsb(b)*2; end % antialias que alimenta la banda b, a su tasa de entrada 2*fsb(b)
end
out('\n== Costo ==\nSOS totales: %d   Multiplicaciones/s: %.2f M\n', nsos, mult/1e6);
for Nc = [3 4]
  mc = sum(5*Nc*fsb) + sum(5*3*2*fsb(1:nb-1));
  out('N = %d: %d SOS, %.2f M mult/s (antialias: %.2f M)\n', Nc, Nc*nb + 3*(nb-1), mc/1e6, sum(5*3*2*fsb(1:nb-1))/1e6);
end

%% Exportación de coeficientes para el firmware (float32, formato ESP-DSP)
% ESP-DSP dsps_biquad_f32: coef = {b0, b1, b2, a1, a2}, a0 = 1
h = fopen(fullfile(outdir, 'octave_coeffs.h'), 'w');
fprintf(h, '/* octave_coeffs.h — generado por dsp/octave/diseno_banco.m. NO EDITAR.\n');
fprintf(h, ' * Butterworth N=%d (pasabanda orden %d), bilineal con predistorsión,\n', NSEL, 2*NSEL);
fprintf(h, ' * arquitectura multitasa: banda b se procesa a FS/2^(6-b). */\n');
fprintf(h, '#pragma once\n#define OCT_N_BANDS %d\n#define OCT_N_SOS %d\n#define DEC_N_SOS 3\n', nb, NSEL);
fprintf(h, 'static const float OCT_FM_HZ[OCT_N_BANDS] = {');
fprintf(h, '%.4ff, ', fm(1:end-1)); fprintf(h, '%.4ff};\n', fm(end));
fprintf(h, 'static const float OCT_SOS[OCT_N_BANDS][OCT_N_SOS][5] = {\n');
for b = 1:nb
  s = res(NSEL).sos{b};
  fprintf(h, '  /* %5d Hz @ %5d Hz */ {', fnom(b), fsb(b));
  for r = 1:rows(s)
    fprintf(h, '{%.9ef, %.9ef, %.9ef, %.9ef, %.9ef}', s(r,1:3), s(r,5:6));
    if r < rows(s), fprintf(h, ', '); end
  end
  fprintf(h, '},\n');
end
fprintf(h, '};\nstatic const float DEC_SOS[DEC_N_SOS][5] = {\n');
for r = 1:rows(sosd)
  fprintf(h, '  {%.9ef, %.9ef, %.9ef, %.9ef, %.9ef},\n', sosd(r,1:3), sosd(r,5:6));
end
fprintf(h, '};\n');
fclose(h);

%% Datos del diezmador para graficar
dlmwrite(fullfile(outdir, 'diezmador.csv'), [fd Hd_db], 'precision', '%.6g');

%% Filtros del prototipo previo (para comparación)
C = [0.008700 0 -0.008700 -1.982300 0.982600
     0.017400 0 -0.017400 -1.965100 0.965200
     0.034000 0 -0.034000 -1.931900 0.932000
     0.064500 0 -0.064500 -1.871000 0.871000
     0.115400 0 -0.115400 -1.769300 0.769300
     0.187300 0 -0.187300 -1.625400 0.625400
     0.274300 0 -0.274300 -1.451400 0.451400];
fe = logspace(log10(10), log10(25599), 3000);
P = zeros(numel(fe), nb);
out('\n== Prototipo previo (fs = 51200 Hz, 1 biquad) ==\n');
out('banda  polos (módulo, ángulo->Hz)        dB_en_fc   -3dB_inf[Hz] -3dB_sup[Hz]  1+a1+a2(float32)  |p|max(float32)  1-a2-2b0\n');
for b = 1:nb
  bq = C(b,1:3); aq = [1 C(b,4:5)];
  H = freqz(bq, aq, fe, 51200);
  Hn = 20*log10(abs(H)); P(:, b) = Hn;
  pk = max(Hn);
  in3 = find(Hn >= pk - 3);
  pz = roots(aq);
  a32 = single(aq); s32 = double(a32(1) + a32(2) + a32(3));
  p32 = max(abs(roots(double(a32))));
  out('%5d  %.4f@%6.1f  %.4f@%6.1f   %6.2f     %8.1f     %8.1f     %+.2e        1%+.1e       %+.1e\n', fnom(b), ...
      abs(pz(1)), abs(angle(pz(1)))*51200/2/pi, abs(pz(2)), abs(angle(pz(2)))*51200/2/pi, ...
      20*log10(abs(freqz(bq, aq, [fnom(b) fnom(b)], 51200))(1)), fe(in3(1)), fe(in3(end)), s32, p32-1, 1-aq(3)-2*bq(1));
end
dlmwrite(fullfile(outdir, 'previo.csv'), [fe(:) P], 'precision', '%.6g');

fclose(fid);
type(fullfile(outdir, 'resumen.txt'));
