clear all
close all
clc
%algoritmo de busqueda local
da=0.1;
db=0.1;
%profundidad (>0 <3000km)
%densidad (>0 <2.8 kg/m3)
m1=[-3:da:3];
m2=[-3:db:3];
[M1,M2]=meshgrid(m1,m2);      
%LA SUPERFICIE DE COSTO LAPODEMOS INTERPRATAR COMO LA DISTRIBUCIÓN DE
%ERRORES ASOCIADOS A UNA NORMA
Z1=6*(M1/6-M1.^3-M2.^5).*exp(-(M1-1/2).^2-M2.^2);
Z2=2*exp(-(M1+1).^2-M2.^2);
Z3=-6*(1-M1).^2.*exp(-(2*M1.^2)-(M2+1).^2);
Z4=1/2*sin(3*M1)+cos(5/2*M2);
E=Z1+Z2+Z3+Z4+10;
figure(1)
surfc(M1,M2,E)
%PROPONEMOS UN MODELO INICIAL
mi=[-1.6;0.6];
%Evaluemos en el PD y calculamos el error
Z1=6*(mi(1)/6-mi(1).^3-mi(2).^5).*exp(-(mi(1)-1/2).^2-mi(2).^2);
Z2=2*exp(-(mi(1)+1).^2-mi(2).^2);
Z3=-6*(1-mi(1)).^2.*exp(-(2*mi(1).^2)-(mi(2)+1).^2);
Z4=1/2*sin(3*mi(1))+cos(5/2*mi(2));
Ei=Z1+Z2+Z3+Z4+10;
hold on
plot3(mi(1),mi(2),Ei,'*k')
% parametros del algoritmo de inversión
itermax = 500;
TOL = 1.9;
NP = 2;
AMP=[0.1;0.1];
k = 0;
mp = mi;
Ep = Ei;
while (k < itermax && TOL < Ei)   %%% ciclo externo

    k= k+1
    for c1 = 1:NP %ciclo interno en funcion del numero de parametrosf
        a = (2*rand - 1) * AMP(c1);
        mp(c1)=mi(c1)+a;
        % evaluamos el error del modelo
        Z1=6*(mp(1)/6-mp(1).^3-mp(2).^5).*exp(-(mp(1)-1/2).^2-mp(2).^2);
        Z2=2*exp(-(mp(1)+1).^2-mp(2).^2);
        Z3=-6*(1-mp(1)).^2.*exp(-(2*mp(1).^2)-(mp(2)+1).^2);
        Z4=1/2*sin(3*mp(1))+cos(5/2*mp(2));
        Ep=Z1+Z2+Z3+Z4+10;
        if Ep < Ei %aceptamos la pertubacion
            mi(c1)=mp(c1)
            Ei = Ep; % Update the error with the new model
        else
            mp(c1)=mi(c1) %desechamos si es que la perturbacion no es menor

        end
       
        

    end
    figure(1)
    plot3(mi(1),mi(2),Ei,'*')
    figure(2)
    hold on
    plot(k,Ei,'o')
end
