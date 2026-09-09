Siempre vas a tener misising data en inferencia causal dado que para cada universo solo tenes un factual sabido no podes tener el factual y contrafactual por diseño de la inferencia causal.

Hay que resolver la esperanza donde una es missing y otra obserbada y por eso causal inference y missing data tienen muchos puntos en comun aunque sean areas diferentes

La consistencia era que lo que te dio a vos coincide con la potencial outcome de tratamiento, T=t -> Y=Y^(t)
y vale Y^1 si T=1 y sino Y^0 si T=0

el Average treatment effect es E(Y^1) - E(Y^0)

este ATE queda determinado por la distribucion conjunta de (T,Y)? -> NO Explicacion tarea

es analogo a "La distribucion conjunta da mas informacionq ue las marginales porque muchas marginales puede tener la misma conjunta"

Hay varias distribuciones contrafactuales que dan lo mismo en el mundo observado y el ATE en cada caso contrafactual puede ser diferente.

para un caso donde Y puede ser 0 o 1. => 
=> ATE = E(Y^1) - E(Y^0) 
= P(Y^1 = 1) - P(Y^0 = 1)
= (P(Y^0 = 0, Y^1 = 1) + P(Y^0 = 1, Y^1 = 1)) - (P(Y^0 = 1, Y^1 = 0) + P(Y^0 = 1, Y^1 = 1))
= P(Y^0 = 0, Y^1 = 1) - P(Y^0 = 1, Y^1 = 0)

ATE = P(Y^0 = 0, Y^1 = 1) - P(Y^0 = 1, Y^1 = 0) y puede tener infinitos valores dependiendo de los mundos contrafactuales compatibles con las variables contrafactuales (Y, T) y con diferentes ATEs.

A priori sin supuestos adicionales salvo los de consistencia y no inferencia (no vacunacion) no podemos identificar el ATE

Es imposible verificar estos supuestos extra porque requiere saber los contrafactuales pero es imposible entonces necesitamos conociniemto de dominio para validar que los supuestos tienen sentido sobre la data que no vemos

Solamente podemos definir ATE por consistencia y no interferencia.

Como hacemos para tener identificabilidad???

Supuesto de aleatoriedad: Es el de exchaengability entre los grupos de tratamiento y son comparables (Ultimo digito del DNI) Hay que armar bien los grupos para el analisis, Y^a Independiente A for all values a. el tratamiento tiene que se exogeno.

si sumamos aleatorizacion entonces el ATE queda definido

ATE = E(Y^1) - E(Y^0) = E(Y|T=1) - E(Y|T=0)

En un analisis donde no podemos garantizar la aleatorizacion y la exchangeability, podemos safar usando la estratificacion o hacer lo mismo por grupos.

el supuesto se llama conditional excheangability, Volviendo al ejemplo del cafe tenemos Turno, Cafe, Productividad y Horas.
Definicion: Existe X Nueva variable aleatoria de forma tal que la contrafactual es independiente del tratamiento condicional a X
Y^(a) independiente T | X.

Repaso de probar, (x,y), si miro Y|x=x es como un filtro ~ Fy/x=x. si (x,y) independiente => F_y/x=x = F_y (Saber x no te dio informacion)

Sean (A_1, A_2, A_3) vector aleatorio. A_1 Independiente A_2 | A_3 que es independencia condicional
P_(A_1 A_2)(a_1, a_2) | A_3 = a_3 = PA_1(a_1)| A_3 = a_3 * PA_2(a_2)| A_3 = a_3.

LEMA - Supuesto nuevo
Y^a independiente T | X => todo joya

Repaso Proba:
A_1 independiente A_2 | A_3. Otra manera de decir esto es A_1|A_3 A_2 = A_1 | A_3

Quiero llegar a que ATE = E(Y^1) - E(Y^0) se puede escribir en base a las variables observadas.

E(Y^1) = E(E(Y^1 | x) for all x) "Promedio de promedios por cada x"
= E(E(Y^1 | x, T) for all x) dado que tenemos conditional excheangability
= E(E(Y^1 | x, T=1) for all x) dado un T particular porque son independientes
= E(E(Y | x, T) for all x) por consistencia
Analogo para Y^0 => ATE queda identificado

el DAG causal del cafe seria
Turno -> Productividad
Turno -> Cafe
Cafe -> Productividad
Cafe -> Horas
Productividad -> Horas

Otra manera de indentificar con el mismo supuesto (Conditional exchengeability) (Y^a independiente T | X)
E(Y^1) = E(Y,I_T=1 / P(T=1|X))

donde P(T=1|X) es el propensity score (Cual es la probabilidad de que tomes cafe dado que sos del turno noche)

= E(Y, I_T=1 / PI(X)) 
= E( E( Y, I_T=1 / PI(X) ) | X ) 
= E(1/PI(X)) * E( Y, I_T=1 |X)
= E( 1/pi(x) * E(Y^1 | X) * E(I_T=1 | X) ) 
= E( 1/pi(x) * E(Y^1 | X) * pi(x) ) 
= E(E(Y^1 | X))

Este proceso es diferente dado que en el proceso de estimacion va a ser diferente, va a ser como un proceso logistico
Ahi se habre en dos mundos (Estimadores de propensity score vs el otro)
