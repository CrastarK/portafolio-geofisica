close all
clear all
clc

%% Datos sintéticos
x = -10:0.1:10;
G = [x(:).^0 x(:) x(:).^2 x(:).^3];
m_true = [500;50;5;0.5];
d = G * m_true;

figure(1); hold on
plot(x,d,'or'); title('Datos')

%% Modelo inicial
mi = [0 0 0 0]';
di = G*mi;
ei = d - di;
Ei = sqrt(ei'*ei);

%% Parámetros del algoritmo
itermax = 200;
TOL = 1;
NP = 4;
AMP = [10, 1, 0.1, 0.01];

Ti = 1e6;
Tf = 1e-6;
RT = (Tf/Ti)^(1/itermax);
CT = 8;

mopt = mi;
Eopt = Ei;

figure(2); hold on; title('Evolución del error')
figure(3); hold on; title('Distribución de probabilidad DP')

%% Simulated Annealing
k = 0;
while (k < itermax && Ei > TOL)
    k = k + 1;
    
    for c2 = 1:CT
        for c1 = 1:NP
            
            mp = mi;
            perturb = (2*rand - 1) * AMP(c1);
            mp(c1) = mp(c1) + perturb;

            % Acotar parámetros
            mp = max(mp, -3);
            mp = min(mp,  3);

            % Evaluación
            dp = G*mp;
            ep = d - dp;
            Ep = sqrt(ep'*ep);

            if Ep < Ei
                % aceptar siempre
                mi = mp;
                Ei = Ep;

                if Ep < Eopt
                    mopt = mp;
                    Eopt = Ep;
                end
                DP = 1; % aceptación total
            else
                % regla de Metropolis
                DP = exp(-(Ep - Ei)/Ti);
                if rand < DP
                    mi = mp;
                    Ei = Ep;
                end
            end

            figure(3); plot(k,DP,'x');
        end
    end
    
    figure(2); plot(k,Ei,'o')
    Ti = Ti * RT;
end

%% Resultados
disp('Modelo óptimo encontrado:')
mopt
disp('Error final:')
Eopt
