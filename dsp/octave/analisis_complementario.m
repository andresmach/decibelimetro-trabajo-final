% analisis_complementario.m — Análisis adicionales del Capítulo 3 (v0.2)
% Uso (desde anteproyecto/dsp):  octave --no-gui octave/analisis_complementario.m
%   1) transitorio de establecimiento por banda (justifica el descarte inicial)
%   2) ruido de redondeo en aritmética float32 (DF2T simulada en single)
%   3) contra-caso: banda de 125 Hz diseñada directamente a 48 kHz
%   4) polos y ceros (banda de 1 kHz propuesta y biquad previo)
%   5) efecto de la ondulación del antialias (0,05 dB vs 0,01 dB)
%   6) incertidumbre estadística del Leq con ruido aleatorio

pkg load signal
addpath(fileparts(mfilename('fullpath')));
more off
outdir = 'resultados';
fid = fopen(fullfile(outdir, 'complementario.txt'), 'w');
out = @(varargin) fprintf(fid, varargin{:});

FS = 48000; G = 10^0.3; k = -3:3; fm = 1000*G.^k; nb = 7;
fnom = [125 250 500 1000 2000 4000 8000];
fsb = FS ./ 2.^(3 - k); N = 4;
for b = 1:nb
  [z, p, g] = butter(N, [fm(b)/sqrt(G) fm(b)*sqrt(G)]/(fsb(b)/2));
  sos{b} = zp2sos(z, p, g); Z{b} = z; Pp{b} = p;
end
mk_dec = @(rp) zp2sos(nthargout(1:3, @ellip, 6, rp, 80, 0.236){:});
sosd = mk_dec(0.01);

function y = chain_to(x, b, sosb, sosd, nb)
  for bb = nb:-1:b+1, x = sosfilt(sosd, x); x = x(1:2:end); end
  y = sosfilt(sosb, x);
end

function y = df2t_single(sos, x)
  % Forma directa II transpuesta en precisión simple (como dsps_biquad_f32)
  y = single(x(:));
  for r = 1:rows(sos)
    c = single(sos(r,:) / sos(r,4));
    b0 = c(1); b1 = c(2); b2 = c(3); a1 = c(5); a2 = c(6);
    w1 = single(0); w2 = single(0);
    v = y;
    for n = 1:numel(v)
      xn = v(n);
      yn = b0*xn + w1;
      w1 = b1*xn - a1*yn + w2;
      w2 = b2*xn - a2*yn;
      v(n) = yn;
    end
    y = v;
  end
end

%% 1) Transitorio de establecimiento
out('== 1) Transitorio: tono en f_m encendido en t = 0, cadena completa ==\n');
out('banda  t_establecimiento(±0,1 dB)[ms]  retardo_de_grupo_en_fm[ms]\n');
T = 1.5; t = (0:round(T*FS)-1)'/FS;
for b = 1:nb
  y = chain_to(sin(2*pi*fm(b)*t), b, sos{b}, sosd, nb);
  tb = (0:numel(y)-1)'/fsb(b);
  L = max(4, round(4*fsb(b)/fm(b)));                 % ventana de 4 períodos
  e = filter(ones(L,1)/L, 1, y.^2);
  ss = mean(y(round(end/2):end).^2);
  dev = abs(10*log10(e./ss + 1e-30));
  i = find(dev > 0.1, 1, 'last');
  ts = tb(min(i+1, end)) * 1000;
  % retardo de grupo de la banda (a su tasa)
  [gd, w] = grpdelay(sos2tf(sos{b}), 1, [fm(b) fm(b)*1.0001], fsb(b));
  out('%5d   %8.1f                       %6.1f\n', fnom(b), ts, gd(1)/fsb(b)*1000);
end

%% 2) Ruido de redondeo en float32
out('\n== 2) Redondeo float32 (DF2T simple) vs referencia en doble precisión ==\n');
T2 = 4; t2 = (0:round(T2*FS)-1)'/FS;
randn('seed', 1);
x = 0.3*sin(2*pi*7943*t2) + 1e-5*randn(size(t2));    % tono fuerte fuera de banda + ruido a -100 dBFS
for b = [1 4]
  xd = x; xs = single(x);
  for bb = nb:-1:b+1
    xd = sosfilt(sosd, xd); xd = xd(1:2:end);
    xs = df2t_single(sosd, xs); xs = xs(1:2:end);
  end
  yd = sosfilt(sos{b}, xd); ys = df2t_single(sos{b}, xs);
  n0 = round(numel(yd)/4);
  Ld = 10*log10(mean(yd(n0:end).^2)); Ls = 10*log10(mean(double(ys(n0:end)).^2));
  Le = 10*log10(mean((double(ys(n0:end)) - yd(n0:end)).^2) + 1e-300);
  out('banda %5d: nivel doble %.2f dBFS, simple %.2f dBFS, diferencia %.4f dB, error de redondeo %.1f dBFS\n', ...
      fnom(b), Ld, Ls, Ls - Ld, Le);
end

%% 3) Contra-caso: 125 Hz diseñado a 48 kHz
out('\n== 3) Contra-caso: banda de 125 Hz diseñada directamente a 48 kHz (N = 4) ==\n');
[z, p, g] = butter(N, [fm(1)/sqrt(G) fm(1)*sqrt(G)]/(FS/2));
s48 = zp2sos(z, p, g);
out('Radio máximo de polos: %.6f (1 - %.1e)\n', max(abs(p)), 1 - max(abs(p)));
fe = logspace(log10(fm(1)/G), log10(fm(1)*G), 400);
H64 = 20*log10(abs(sosresp(s48, fe, FS)));
H32 = 20*log10(abs(sosresp(double(single(s48)), fe, FS)));
out('Máx. diferencia por cuantización float32 de coeficientes (f_m/G a f_m·G): %.3f dB\n', max(abs(H64 - H32)));
tt = (0:round(3*FS)-1)'/FS; xx = sin(2*pi*fm(1)*tt);
yd = sosfilt(s48, xx); ys = df2t_single(s48, single(xx));
n0 = round(numel(yd)/2);
out('Tono en f_m: nivel doble %.3f dB, simple %.3f dB\n', 10*log10(mean(yd(n0:end).^2)/0.5), ...
    10*log10(mean(double(ys(n0:end)).^2)/0.5));
yd = sosfilt(s48, x); ys = df2t_single(s48, single(x));
n0 = round(numel(yd)/4);
out('Misma señal que en 2) (tono fuerte + ruido a -100 dBFS): nivel doble %.2f dBFS, simple %.2f dBFS, error de redondeo %.1f dBFS\n', ...
    10*log10(mean(yd(n0:end).^2)), 10*log10(mean(double(ys(n0:end)).^2)), ...
    10*log10(mean((double(ys(n0:end)) - yd(n0:end)).^2)));
out('Costo de 7 bandas a 48 kHz sin multitasa (4 SOS c/u): %.2f M mult/s\n', 7*4*5*FS/1e6);

%% 4) Polos y ceros
b = 4;
fz = fopen(fullfile(outdir, 'pz_1k.dat'), 'w');
fprintf(fz, '# re im  (polos banda 1 kHz propuesta @6 kHz)\n');
fprintf(fz, '%.6f %.6f\n', [real(Pp{b}(:)) imag(Pp{b}(:))]');
fprintf(fz, '\n\n# ceros banda propuesta (multiplicidad 4 en +1 y -1)\n1 0\n-1 0\n');
fprintf(fz, '\n\n# polos biquad previo 1 kHz @51,2 kHz\n');
pr = roots([1 -1.871 0.871]);
fprintf(fz, '%.6f %.6f\n', [real(pr) imag(pr)]');
fprintf(fz, '\n\n# ceros biquad previo\n1 0\n-1 0\n');
fclose(fz);
out('\n== 4) Polos banda 1 kHz (|p|, ángulo -> Hz a 6 kHz) ==\n');
for i = 1:numel(Pp{b})
  if imag(Pp{b}(i)) >= 0
    out('  |p| = %.4f  f = %.1f Hz\n', abs(Pp{b}(i)), angle(Pp{b}(i))*fsb(b)/2/pi);
  end
end

%% 5) Ondulación del antialias
out('\n== 5) Error de ganancia entre bandas (dA en f_m respecto de 1 kHz) según ondulación ==\n');
T5 = 4; t5 = (0:round(T5*FS)-1)'/FS;
for rp = [0.05 0.01]
  sd = mk_dec(rp);
  A = zeros(1, nb);
  for b = 1:nb
    y = chain_to(sin(2*pi*fm(b)*t5), b, sos{b}, sd, nb);
    A(b) = -10*log10(mean(y(round(end/2):end).^2)/0.5);
  end
  out('Rp = %.2f dB: ', rp); out('%+.3f ', A - A(4)); out(' (125 ... 8000 Hz)\n');
end

%% 6) Incertidumbre estadística del Leq (ruido gaussiano, banda B, tiempo T)
out('\n== 6) Desvío estándar del Leq: sigma = 4,34 / sqrt(B*T) [dB] ==\n');
B = fm*(sqrt(G) - 1/sqrt(G));
out('T[s] '); out('%7d ', fnom); out('\n');
for Tm = [5 10 30]
  out('%4d ', Tm); out('%7.3f ', 4.34./sqrt(B*Tm)); out('\n');
end
fclose(fid);
type(fullfile(outdir, 'complementario.txt'));
