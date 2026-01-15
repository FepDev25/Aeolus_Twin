% ==========================================================
% PARÁMETROS DEL SISTEMA DE TURBINA EÓLICA (Script: parametros_aerogenerador.m)
% ==========================================================

% -- Parámetros de la Turbina (Basado en 2 MW de 07395143.pdf) --
rho = 1.225;            % Densidad del aire (kg/m^3)
R = 42;                 % Radio de la turbina (m) - Estimado para 2MW
A = pi*R^2;             % Área barrida por las palas (m^2)

% Coeficientes de la curva Cp(lambda, beta) 
c1 = 0.5176;
c2 = 116;
c3 = 0.4;
c4 = 5;
c5 = 21;
c6 = 0.0068;

disp('Parámetros de la turbina cargados.');

% -- Parámetros del Generador (Basado en 2 MW de 07395143.pdf) -- [cite: 2306]
Pn = 2e6;               % Potencia Nominal (W)
Rs = 0.008;             % Resistencia Estator (Ohm)
Ld = 0.0003;            % Inductancia eje d (H)
Lq = 0.0003;            % Inductancia eje q (H) -> Ld=Lq asumido
lambda_pm = 3.86;       % Flujo Imanes Permanentes (Wb)
p = 60;                 % Pares de Polos (Npp en otros papers) - Corregido (120 polos = 60 pares)
J = 8000;               % Inercia (kg.m^2)
Bm = 0.00001349;        % Fricción Viscosa (N.m.s/rad) - Muy bajo, casi cero

disp('Parámetros del generador cargados.');