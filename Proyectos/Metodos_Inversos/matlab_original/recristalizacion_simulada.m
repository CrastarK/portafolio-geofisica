%programa de inversion por recristalizacion simulada
%es un algoritmo de busqueda global


close all 
clear all 
clc

% domino de los parametros 
dx = 0.1;
dy = 0.1;
x = -3:dx:3;
y = -3:dy:3;
[X , Y] = meshgrid(x,y);
% Se define la superficie de costo
Z1 = 6 * (X/6-X.^3 - Y.^5).*exp(-(X-1/2).^2-Y.^2);
Z2 = 2*exp(-(X+1).^2-Y.^2);
Z3 = 6 * (1-X).^2.*exp(-(2*X.^2)-(Y+1).^2);
Z4 = 1/2*sin(3*X)+cos(5/2*Y);
F=Z1 + Z2 + Z3 + Z4;
figure(1)
surfc(X,Y,F)

%proponemos un modelo inicial 
% conjunto de parámetros iniciales evaluados en la función de costo

mix = 0.7;
miy = -1.8;
% evaluamos los parametros iniciales en la funcion de costo
Z1 = 6 * (mix/6-mix.^3 - miy.^5).*exp(-(mix-1/2).^2-miy.^2);
Z2 = 2*exp(-(mix+1).^2-miy.^2);
Z3 = 6 * (1-mix).^2.*exp(-(2*mix.^2)-(miy+1).^2);
Z4 = 1/2*sin(3*mix)+cos(5/2*miy);
Ei=Z1 + Z2 + Z3 + Z4;
figure(1)
hold on 
plot3(mix,miy,Ei,'*r')

% Definimos los parametros de inversión
% La tolerancia es la distancia minima permitida entre
% los datos observados y los parametros evaluados en el problema 
% directo
