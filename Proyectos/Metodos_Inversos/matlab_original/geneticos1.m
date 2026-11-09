% programa que encuentra el minimo global, mediante algoritmos geneticos
close all
clear all
clc
% definimos el dominio de los parámetros
dm1 = 0.1;
dm2 = 0.1;
m1 = -3:dm1:3;
m2 = -3:dm2:3;
[M1, M2] = meshgrid(m1, m2);
% definimos la superficie de costo
Z1=6*(M1/6-M1.^3-M2.^5).*exp(-(M1-1/2).^2-M2.^2);
Z2=2*exp(-(M1+1).^2-M2.^2);
Z3=-6*(1-M1).^2.*exp(-(2*M1.^2)-(M2+1).^2);
Z4=1/2*sin(3*M1)+cos(5/2*M2);
FA=Z1+Z2+Z3+Z4+10;
figure(1)
surfc(M1,M2,FA)
% Convertimos el dominio de los parametros a un dominio 
% de enteros, donde cada coordenada es  expresada como una
% combinación de números enteros.
np1 = length(m1);
np2 = length(m2);
% dominio de enteros que es un vector de enteros ordenados
dep1 = 1:np1;
dep2 = 1:np2;
% Definímos el número de parámetros a invertir.
np= 2;
% Definimos la longitud del cromosoma
% un cromosoma es la expresión en formato binario de un parámetro
% un crommosoma también es la expresion en formato binario de cada
% elemento del vector de enteros.
% ¨La extención del cromosoma es el número de posiciones fijas para
%  el formato binario"
LCR = 10;
% definimos la longitud del padre
% el padre esta conformado por la concatenación de los parámetros
% en formato binario 
% ejemplo
% para la línea recta se tiene 2 parámetros por lo tanto el padre
% estará conformado por 2 parametros en formato binario
% y = m1 + m2*x
% padre = (m1,m2)
% m1 = [aaaaaaaaaa] m2 = [bbbbbbbbbb] padre = [aaaaaaaaaa bbbbbbbbbb];
%  y = m1 + m2*x + m3x^2
% padre = [m1,m2,m3]
% m1 = [aaaaaaaaaa] m2 = [bbbbbbbbbbb] m3=[cccccccccc]
% padre para el caso parabola = [aaaaaaaaaaa bbbbbbbbbb cccccccccc]
% por lo tanto la longitud del padre es de la longitud del cromosoma LCR 
% por el numero de parámetros
LP = LCR * np;

% concepto de generaciones
% es el numero de iteraciones que controla el ciclo externo o ciclo
% principal

generaciones = 120; % con cuantas generaciones seconsigue 
mutacion = 0.5; % el indice de probabilidad con el que puede "mutar"
% pareja 
% el concepto de pareja se refiere a cada individuo de la población
% inicial al cual se le asignará otro individuo para formar un par
% podemos describir el numero de parejas como el número de individuos
parejas = 10;

% módulo 1
% seleccionamos un conjunto de parejas de manera aleatoria para 
% tomarlas como modelo inicial


for c1 = 1:parejas
    mi1(c1,1)=fix(rand*np1)+1;
    mi2(c1,1)=fix(rand*np2)+1;
end

% evaluamos los parámetros iniciales en la superficie de costo
MI1 = m1(mi1);
MI2 = m2(mi2);


Z1=6*(MI1/6-MI1.^3-MI2.^5).*exp(-(MI1-1/2).^2-MI2.^2);
Z2=2*exp(-(MI1+1).^2-MI2.^2);
Z3=-6*(1-MI1).^2.*exp(-(2*MI1.^2)-(MI2+1).^2);
Z4=1/2*sin(3*MI1)+cos(5/2*MI2);
FIA=Z1+Z2+Z3+Z4+10;
figure(1)
hold on
plot3(MI1,MI2,FIA,'*r')
% modulo 2
% convertimos de decimal a binario y utilizamos el concepto de 
% cromosoma cada parámmetro está asociado a un cromosoma
% m1 ---> cromosoma1
% m2 ---> cromosoma2
% m3 ---> cromosoma3
% Convertimos los parámetros iniciales a formato binario
crom1 = dec2bin(mi1, LCR);
crom2 = dec2bin(mi2, LCR);

% modulo 3
% formamos los padres 
% el padre es la concatenación de los parámetros que define
% un problema directo
% padre = [m1,m2] ---> formato binario padre = [crom1,crom2]

for c1 = 1:parejas
    padres(c1,:)=[crom1(c1,:),crom2(c1,:)];
end


% modulo 4
% pasamos de un vector ordenado a un vector aleatorio 
% en este momento tenemos 10 parejas compuestas por crom1 y crom2
% (no 10 pares)

p_comb = vale(parejas);
% modulo 5
% separamos en padre y madre para formar los pares
% la asignacion de sexo es completamente aleatoria
for c1= 1:parejas/2
    padre(c1,:)= padres(p_comb(c1*2-1),:);
    madre(c1,:)= padres(p_comb(c1*2),:);
end

% modulo 6 
% cruza de parejas
% seleccionamos un gen de manera aleatoria y realizamos la cruza
% la combinacion genética (cruza)
% cada elemento del vector de cromosomas lo denominamos gen
% los cromosomas estan compuestos por genes
% los elementos binario ( 0 o 1) que conforman al cromosoma lo
% denominamos gen
% parametros    cromosoma       gen
% m1 --->     [110101011001]  -->1
% m2 --->     [010101010001]  -->0
% padre--->   [110101011001 010101010001]
% cuando asignamos un sexo entonces podemos hablar de padre o madre
% padre --> [110101011001 010101010001]
% madr ---> [110101011001 010101010001]
% dependiendo el vector aleatorio se le asigna un sexo 
% realizamos la cruza a partir de padre y madre para generar 2
% hijos 
% la cruza siempre generara 2 hijos 
% el hijo 1 [1 10101011001 010101010001]
% el hijo 2 [1 10101011001 010101010001]
for c1 = 1:parejas/2
    a = fix(rand*(LP-1))+1;
    hijo1(c1,:) = [padre(c1,1:a),madre(c1,a+1:LP)];
    hijo2(c1,:) = [madre(c1,1:a),padre(c1,a+1:LP)];
end

% modulo 7
% separamos los hijos en cromosomas
% los hijos tienen el mínimo número de cromosomas que los padres
% y el mismo numero de génes
for c1 = 1:parejas/2
    crom1(c1*2-1,:)=hijo1(c1,1:LCR);
    crom1(c1*2,:)=hijo2(c1,1:LCR);
    crom2(c1*2-1,:)=hijo1(c1,LCR+1:LCR*2);
    crom2(c1*2,:)=hijo2(c1,LCR+1:LCR*2);
end

% modulo 8 
% realizamos la mutación en función de un número aleatorios 
% y el parámetro de mutación
% para el parámetro m1(cromosoma1)
for c1 =1:parejas
    a = rand;
    if a< mutacion
        gen = fix(rand*LCR)+1;
        n = crom1(c1,gen);
        switch n
            case '1'
                crom1(c1,gen)='0';
            case '0'
                crom1(c1,gen)='0';
        end
    end
    

    % if rand < mutacion
    %     crom1(c1,:) = ~crom1(c1,:); % Mutate the chromosome by flipping bits
    % end

end

% para el parametro 2 m2
for c1 =1:parejas
    a = rand;
    if a< mutacion
        gen = fix(rand*LCR)+1;
        n = crom2(c1,gen);
        switch n
            case '1'
                crom2(c1,gen)='0';
            case '0'
                crom2(c1,gen)='0';
        end
    end
    
end
% modulo 9

% mutacion es el cambio de paridad de un gen elegido de manera aleatoria
% dentro de un cromosoma que cumple una condicion de probabilidad 
% que el numero aleatorio a<mutacion
m1h = bin2dec(crom1);
m2h = bin2dec(crom2);

% verificamos que el dominio de enteros se encuentre dentro del rango
% del estudio
% para el parametro 1  m1
for c1=1:parejas
    if (m1h(c1)>np1 || m1h(c1)==0)
        m1h(c1)=fix(rand*np1)+1;
    end
end

% para el parametro 2 m2
for c1=1:parejas
    if (m2h(c1)>np1 || m2h(c1)==0)
        m2h(c1)=fix(rand*np2)+1;
    end
end

% la poblacion final es el conjunto de padres e hijos en un mismo
% vector
m1total=[mil;m1h];
% la población total se compone de los padres y los hijos
m2total = [mi2; m2h];
% evaluamos los parametros en la superficie de costo
mi1 = m1(m1total);
mi2 = m2(m2total);

