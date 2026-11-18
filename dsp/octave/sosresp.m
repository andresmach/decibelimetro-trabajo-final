function H = sosresp(sos, f, fs)
  % Respuesta en frecuencia compleja de una cascada SOS en las frecuencias f (Hz).
  % Si fs se omite, f se interpreta como número de puntos (0..pi), como freqz.
  if nargin < 3
    n = f; w = pi*(0:n-1)'/n;
  else
    w = 2*pi*f(:)/fs;
  end
  z = exp(-1j*w);
  H = ones(size(w));
  for r = 1:rows(sos)
    H = H .* (sos(r,1) + sos(r,2)*z + sos(r,3)*z.^2) ./ (sos(r,4) + sos(r,5)*z + sos(r,6)*z.^2);
  end
  if nargin < 3, H = [H w]; end
end
