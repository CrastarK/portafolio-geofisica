close all
clear all
clc
%algoritmo de buúsqueda global
%DEFINIMOS EL DOMINIO DE LOS PARÁMETROS
dm1=0.1;
dm2=0.1;
m1=[-3:dm1:3];
m2=[-3:dm2:3];
[M1 M2]=meshgrid(m1,m2);
%DEFINIMOS LA SUPERFICIE DE COSTO (DOMINIO DE LOS PARÁMETROS)
Z1=6*(M1/6-M1.^3-M2.^5).*exp(-(M1-1/2).^2-M2.^2);
Z2=2*exp(-(M1+1).^2-M2.^2);
Z3=-6*(1-M1).^2.*exp(-(2*M1.^2)-(M2+1).^2);
Z4=1/2*sin(3*M1)+cos(5/2*M2);
E=Z1+Z2+Z3+Z4+10;
figure(1)
surfc(M1,M2,E)
%PROPONEMOS UN MODELO INICIAL
mi=[-1.6;0.6];
%evalueamos en el PD y calculamos el error
Z1=6*(mi(1)/6-mi(1).^3-mi(2).^5).*exp(-(mi(1)-1/2).^2-mi(2).^2);
Z2=2*exp(-(mi(1)+1).^2-mi(2).^2);
Z3=-6*(1-mi(1)).^2.*exp(-(2*mi(1).^2)-(mi(2)+1).^2);
Z4=1/2*sin(3*mi(1))+cos(5/2*mi(2));
Ei=Z1+Z2+Z3+Z4+10;
hold on
plot3(mi(1),mi(2),Ei,'*k')
%PARAMETROS DEL ALGORITMO DE INVERSIÓN
itermax=500;
TOL=2;
NP=2;
AMP=[0.5,0.5];
k=0;
mp=mi;
Ep=Ei;
%ciclos termodinamos
Ti = 1000000;
Tf = 0.0000001;
% reduccion de temperatura
RT=(Tf/Ti)^(1/itermax);
CT=8;
mopt=mi;
Eopt=Ei;
while(k<itermax && TOL<Ei)%ciclo externo
k=k+1
for c2=1:CT%ciclo intermedio que evalua la calidad de a sol
for c1=1:NP%ciclo interno en función del número de prámetros
a=(rand*2-1)*AMP(c1);
mp(c1)=mi(c1)+a;
% acotamos el espacio de los parametros o de las soluciones
if mp(c1)<-3
    mp(c1)=3;
end
if mp(c1)>3
    mp(c1)=3;
end

%evaluamos el error del modelo
Z1=6*(mp(1)/6-mp(1).^3-mp(2).^5).*exp(-(mp(1)-1/2).^2-mp(2).^2);
Z2=2*exp(-(mp(1)+1).^2-mp(2).^2);
Z3=-6*(1-mp(1)).^2.*exp(-(2*mp(1).^2)-(mp(2)+1).^2);
Z4=1/2*sin(3*mp(1))+cos(5/2*mp(2));
Ep=Z1+Z2+Z3+Z4+10;
if Ep < Ei%aceptamos incondicionalmente el modelo
mi(c1)=mp(c1);
Ei=Ep;
if Ep<Eopt
mopt=mp;
Eopt=Ep;
end
else%le damos una oportunidad al modelo condicional
DP=exp(-(Ep-Ei)/Ti);
a=rand;
if a<DP
mi(c1)=mp(c1);
Ei=Ep;
else

mp(c1)=mi(c1);
end
end
end%fin del ciclo interno
end%cilo itermedio
figure(1)
plot3(mi(1),mi(2),Ei,'*')
figure(2)
hold on
plot(k,Ei,'o')
Ti = Ti*RT
% curva de distribucion de probabilidad
figure(3) 
hold on 
plot(k,DP,'x')
end%fin del ciclo externo



% cuadros de exploracion y de optimizacion, si no se encuentra la mejor
% configuracion en la tercera parte es muy poco probable que la encuentes
% despues entonces con eso se debe de converger en las iteraciones.


% p = 500 + 50x + 5x^2 + 0.5x^3