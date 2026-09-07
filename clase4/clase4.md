Parametro de interes

ATE = E(Y|t=1) - E(Y|t=0)
ATE_hat = sum(Y_i It=1)/sum(I=1) - sum(Y_i It=0)/sum(I=0)

1)


t\Y^0, Y^1 |  00 | 01 | 10 | 11
t          | x1  | x2 | x3 | x4
c          | x5  | x6 | x7 | x8


T/y |  0  |  1
t   |  q1 |  q2
c   |  q3 |  q4

donde 
q1= x1 + x2
q2 = x3 + x4
q3 = x5 + x7
q4 = x6 + x8




2)
ATE = E(y=1) - E(y=0)
= P(y^0=1) - P(y^0=1)
= x3 + x4 + x7 +x8  - (x2 +x6 + x4 + x8)
= x3 + x7 - x2 -x6


3)
para los numeritos del punto 3 y por restricciones del simplex podemos
calcular el minimo y maximo del ATE usando simplex para calcular el maximo y minimo dada las restricciones
tenemos que ATE = [ - 14/20, 6/20 ]


4)

ATE Generico para caso general:
ATE = [-q1 -q4, q2 + q3]




Clase4.pdf

N = N_t1 + N_t0

si tengo excheangebaility para el experimento podemos  predecir cuantos de tratamiento nt0 con el nt1


P(Yt1=1) = nt1 + nt1 * Nt0 / Nt1 / (Nt1 + Nt0) = nt1/Nt1

si hacemos lo mismo para cada nivel de L se puede hacer lo mismo con independencia incondicional

