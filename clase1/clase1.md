Y = Respuesta de interes - Productividad

T = Tratamiento "Tomar o no cafe"

x1 = Turno
x2 = Horas de trabajo

## Datos
https://reda-ar.shinyapps.io/causalidad/


## Hipotesis mala
Hipotesis H1:
b0 = E(Y|t=cafe) != E(Y|T=no cafe)

t.test(Y[T==cafe], Y[T==no cafe])

Hay que ver si b0 es cercano a cero o no para que el modelo lineal nos diga si hay diferencias estadisticas entre las medias de los dos grupos

Y = bo + b1 * I_t + error. donde I_t es el indice del grupo si toma o no cafe

Si hacemos esto vemos estadisticamente significativamente que el b_0 indica que el cafe es malo.


Nota: Hay que saber el data generated process y conocimiento de dominio
Nota 2: El imacpo causal y la intervencion no puede estar basada en asociasion y sacar el cafe no garantiza que va a mejorar la productividad


## Explicacion

Y = Respuesta de interes - Productividad

T = Tratamiento "Tomar o no cafe"

La causalidad mas que ver la diferencia quiere ver el Potential Outcome
Potential Outcome: Consiste en imaginar un mundi paralelo donde todos los individuios reciben el tratamiento y otro donde no reciben y quiere medir la productividad en cada mundo.
Y_0 e Y_1 son respuestas en escenarios hipoteticos donde toda la poblacion recibe el tratamiento o no

Esto necesita varios supuestos, uno es que el tratamiento solo afecta al individio por ejemplo otro caso donde esto no pasa es en la vacunacion, se llama SUTVA
Hay que explicar que es, en pocas palabras es que la variable respuesta depende exlusivamente de su tratamiento y no de otros

No vamosa ver efectos particulares sino efectos poblacionales (media), la primera pregunta que responde la causalidad es el average treatment effect

ATE = E(Ysupra1) - E(Ysupra0) (mundo teorico)
Tambien pueden ser las diferencias de las medianas o la distribucion inclusive
F_Yo(t) = F_Y1(t)

### Variables obseravadas
(T, Y) Como se relacciona Y Y y las potencial outcomes o contrafactuales. (Si yo te doy cafe rendis lo mismo que si no) mundo contrafactico

Consistencia (Incluido Sutva), si no tengo sutva no tiene sentido hablar de contrafactuales
Definicion: La variable que ves coincide con Y_0 dado T=0 y coincide con Y_1 dado T=1
En otras palabras es que la realidad condice con el modelo teorico hipotetico

Por naturaleza el modelo va a tener missing data dado que de un individuo solamente podemos saber su valor real con T=0 o T=1 y nunca por los dos
inherente al problema vamos a tener missing data

En la practica podemos ver E(Y|T=0) y E(Y|T=1) pero esto no es exactamente lo que queremos
E(Ysupra1) es el hipotetico de multiversos.

E(Y|T=0) = E(Ysupra0 | T=0) (consistencia)
E(Y|T=1) = E(Ysupra0 | T=1)

Cuando la media de la respuesta coinciden? para t=0 y t=1??
E(Y|T=t) = E(ysuprat)

por consistencia sabemos que E(Y|T=t) = E(Ysuprat | T=t), Cuando podemos decir que estoes E(ysuprat)
la respuesta es que la aleatoridad te da eso, la aleatorizacion nos dice que los potencial outcomes son independientes del tratamiento matematicamente hablando

LEMA: Ysuptrat independiente de T para t=0,1 => E(Y|T=t) = E(Ysuprat)

Si el tratamiento es aleatorio entonces estamos todo bien

Estamos diciendo que el mecanismo de conformacion de grupos hace que los grupos sean intercambiables y a priori la aleatorizacion comparte las mismas propiedades iguales y son comaprables.
Eso hace que la Y0 es la misma distribucion en los dos y se peude medir y trabajar.
Necesitamos independencia entre contrafatual y los grupos.
El criterio de seleccion no miro nada y tiene que ser bueno (aleatorio), hay que asignar grupos con un mecanismo externo para hacer los grupos comaprables

Aleatorizacion === exchangeability

No hay sesgo de seleccion y los grupos de tratamiento y control son intercambiables y tienen las mismas propiedades y distribuciones

Con toda esta cosa podemos decir que 
E(Y|T=t) = E(ysuprat)

y que todo se comporta igual en todos los casos

#### Identificabilidada
Para ATE (Parametro causal de interes), ATE queda determinado por la distribucion de las variables observadas
A veces no podes obtenerlo entonces ya estas sesgado y es malo, tenes q tener bien le modelo

Si las varaible observadas son (T, Y) el supuesto de independencia condicional
Ysupat independiente T para todo t garantiza identificabilidad

Ejercicio
Armemos (Ysupra0, Ysupra1, T) tal que (Y_j, T_j) sea siempre la misma
Es decir como podemos armar un sesgo en la selecccion para que todo el analisis este mal.

las distribuciones marginales no determinan la distribucion conjunta
podemos armar muchas tablas con las mismas distribuciones marginales pero diferentes conjuntas entonces
con saber las distribuciones marginales no nos alcanza para saber la distribucion conjunta

### Ejemplo: Diabetes y Colesterol Alto

Las tres tablas comparten las mismas marginales:
- P(Diabetes = Sí) = 0.30, P(Diabetes = No) = 0.70
- P(Colesterol Alto = Sí) = 0.40, P(Colesterol Alto = No) = 0.60

pero tienen distribuciones conjuntas completamente distintas.

**Tabla 1 — Independencia** (caso base: las variables no están relacionadas)

|                     | Colesterol Alto = Sí | Colesterol Alto = No | **Marginal** |
|---------------------|---------------------:|---------------------:|-------------:|
| **Diabetes = Sí**   | 0.12                 | 0.18                 | **0.30**     |
| **Diabetes = No**   | 0.28                 | 0.42                 | **0.70**     |
| **Marginal**        | **0.40**             | **0.60**             | **1.00**     |

P(D=Sí, C=Sí) = P(D=Sí) × P(C=Sí) = 0.30 × 0.40 = 0.12. Las variables son independientes: saber si alguien tiene diabetes no dice nada sobre su colesterol.

---

**Tabla 2 — Asociación positiva** (comorbilidad: las enfermedades tienden a aparecer juntas)

|                     | Colesterol Alto = Sí | Colesterol Alto = No | **Marginal** |
|---------------------|---------------------:|---------------------:|-------------:|
| **Diabetes = Sí**   | 0.20                 | 0.10                 | **0.30**     |
| **Diabetes = No**   | 0.20                 | 0.50                 | **0.70**     |
| **Marginal**        | **0.40**             | **0.60**             | **1.00**     |

P(D=Sí | C=Sí) = 0.20/0.40 = 0.50, mucho mayor que la marginal 0.30. Quien tiene colesterol alto tiene más del doble de probabilidad de tener diabetes que la población general. Las marginales son idénticas a la Tabla 1 pero la relación entre variables es completamente diferente.

---

**Tabla 3 — Asociación negativa** (las enfermedades tienden a no aparecer juntas)

|                     | Colesterol Alto = Sí | Colesterol Alto = No | **Marginal** |
|---------------------|---------------------:|---------------------:|-------------:|
| **Diabetes = Sí**   | 0.05                 | 0.25                 | **0.30**     |
| **Diabetes = No**   | 0.35                 | 0.35                 | **0.70**     |
| **Marginal**        | **0.40**             | **0.60**             | **1.00**     |

P(D=Sí | C=Sí) = 0.05/0.40 = 0.125, mucho menor que la marginal 0.30. Quien tiene colesterol alto tiene menos probabilidad de tener diabetes. Nuevamente las marginales son exactamente iguales a las tablas anteriores.

**Conclusión:** conocer P(Diabetes) y P(Colesterol Alto) por separado no alcanza para saber si existe una relación entre ellas ni en qué dirección va. Esto es exactamente por qué las distribuciones marginales de (Y_0, Y_1) y T no determinan la distribución conjunta (Y_0, Y_1, T), y por qué no podemos leer el efecto causal solo de los datos observados sin supuestos adicionales.

TAREA
Volvienod a lo del cafe hay que tratar de conseguir 2 mundos donde lo que veo la distribucion de variables observadas esl amisma
SIn embargo el ATE en uno y el otro dan distinto, sin supuestos la distribucion del as variables observadas no alcanza para determinar el ATE
Neceitamos supuestos para identificabilidad

| T/YSupra0 | 0   | 1   |P Margnial |
|-----------| --- | --- | --------- |
| 0         | a11 | a12 | a11 + a12 |
| 1         | a21 | a22 | a21 + a22 |

| T/YSupra0 | 0   | 1   |P Margnial |
|-----------| --- | --- | --------- |
| 0         | b11 | b12 | b11 + b12 |
| 1         | b21 | b22 | b21 + b22 |

Esta es final
| T/Y | 0   | 1   |
|-----| --- | --- |
| 0   | a12 | a12 |
| 1   | b12 | b22 |

LOS supuestos de la causalidad son de las contrafactuales y solo tenes las observadas, con las observadas no podes indentificar las contrafactuales
Si me vienen con estos datos puedo decir algo sobre el cafe?, hay que suponer el conociemiento del experto para saber si fue aleatorio
En el caso aleatorizado (independenia entre grupos y lo otro) donde las contrafactuales estan buenas ahi esta todo bien.
El protocolo que garantiza exchangeability 

Hay un problema cuando no pasa esto de la aleatorizacion, entonces hay que saber si podemos hacer algo en estos casos reales observables.
Como podemos a partir del DAG causal poder estimar las esperanzas reales y identificabilidad incluso cuando no haya aleatorizacion.
Missin at random

TAREA
CAPITULO 1 y 2 de 
A fist course in causal inference - Peng Ding
Introduction to Causal Inference from a Machine Learning perspective - Brady Neal
