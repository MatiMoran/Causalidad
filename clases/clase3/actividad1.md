# Actividad 1 — COVID y paradoja de Simpson

Sean las variables binarias:

- $X$: grupo etario, con $X=0$ para adultos jóvenes y $X=1$ para adultos mayores.
- $T$: lugar de residencia, con $T=0$ para AMBA y $T=1$ para CABA.
- $Y$: desenlace, con $Y=1$ si la persona muere y $Y=0$ en caso contrario.

La tasa de letalidad de un grupo se expresa como una probabilidad condicional de muerte.

## 1. Comparación dentro de cada grupo etario

La afirmación «la tasa de letalidad, tanto en adultos jóvenes como en adultos mayores, es más baja en AMBA que en CABA» se escribe como:

$$
P(Y=1\mid T=0, X=x) < P(Y=1\mid T=1, X=x),
\qquad \text{para todo } x\in\{0,1\}.
$$

Equivalentemente, de forma explícita:

$$
P(Y=1\mid T=0, X=0) < P(Y=1\mid T=1, X=0)
$$

y

$$
P(Y=1\mid T=0, X=1) < P(Y=1\mid T=1, X=1).
$$

## 2. Comparación sin condicionar por edad

La afirmación «la tasa de letalidad es más baja en AMBA que en CABA» se escribe como:

$$
P(Y=1\mid T=0) < P(Y=1\mid T=1).
$$

Esta comparación mezcla las edades dentro de cada zona.

## 3. Valores numéricos compatibles con las dos afirmaciones

Supongamos las siguientes tasas de letalidad:

| Grupo etario | AMBA ($T=0$) | CABA ($T=1$) |
|---|---:|---:|
| Jóvenes ($X=0$) | $0.1\%$ | $0.2\%$ |
| Mayores ($X=1$) | $10\%$ | $12\%$ |

AMBA tiene una población relativamente más joven, mientras que CABA tiene una población relativamente más mayor:

| Zona | Jóvenes | Mayores | Muertes esperadas | Total | Letalidad total |
|---|---:|---:|---:|---:|---:|
| AMBA | 9 000 | 1 000 | $9 + 100 = 109$ | 10 000 | $1.09\%$ |
| CABA | 1 000 | 9 000 | $2 + 1\,080 = 1\,082$ | 10 000 | $10.82\%$ |

Por lo tanto, dentro de cada edad AMBA tiene menor letalidad, y también la letalidad agregada es menor en AMBA:

$$
1.09\% < 10.82\%.
$$

## 4. ¿Dónde aparece la paradoja de Simpson?

Tal como está escrita la actividad, las afirmaciones de los puntos 1 y 2 tienen la **misma dirección**, por lo que son compatibles y no constituyen una paradoja de Simpson.

La paradoja aparece si, a pesar de que AMBA tiene menor letalidad dentro de cada grupo etario, la comparación agregada concluye lo contrario:

$$
P(Y=1\mid T=0) > P(Y=1\mid T=1).
$$

Por ejemplo, si se mantienen las tasas por edad de la tabla anterior, pero se invierte la composición etaria de las zonas:

| Zona | Jóvenes | Mayores | Muertes esperadas | Total | Letalidad total |
|---|---:|---:|---:|---:|---:|
| AMBA | 1 000 | 9 000 | $1 + 900 = 901$ | 10 000 | $9.01\%$ |
| CABA | 9 000 | 1 000 | $18 + 120 = 138$ | 10 000 | $1.38\%$ |

Ahora AMBA sigue teniendo una tasa menor para jóvenes y para mayores, pero su tasa total es mayor:

$$
9.01\% > 1.38\%.
$$

La aparente contradicción se debe a que $X$, la edad, afecta fuertemente la probabilidad de muerte y está distribuida de manera distinta entre AMBA y CABA. Al no condicionar por $X$, la tasa agregada combina dos poblaciones con composiciones etarias diferentes. La edad funciona entonces como una variable de confusión para la comparación marginal entre zonas.

## Descomposición de la letalidad en AMBA por grupo etario

Partimos de la probabilidad de muerte en AMBA. Por definición de probabilidad condicional:

$$
P(Y=1\mid T=0) = \frac{P(Y=1, T=0)}{P(T=0)}.
$$

Como $X$ es binaria, los eventos $X=0$ y $X=1$ dividen el numerador en dos casos mutuamente excluyentes y exhaustivos:

$$
P(Y=1, T=0)
= P(Y=1, T=0, X=0) + P(Y=1, T=0, X=1).
$$

Entonces:

$$
P(Y=1\mid T=0)
= \frac{P(Y=1, T=0, X=0) + P(Y=1, T=0, X=1)}{P(T=0)}.
$$

Para cada término del numerador, usamos la regla del producto:

$$
P(Y=1, T=0, X=x)
= P(Y=1\mid T=0, X=x)\, P(X=x\mid T=0)\, P(T=0).
$$

Al reemplazar y cancelar $P(T=0)$, obtenemos:

$$
\begin{aligned}
P(Y=1\mid T=0)
= {} & P(Y=1\mid T=0, X=0)\,P(X=0\mid T=0) \\
&+ P(Y=1\mid T=0, X=1)\,P(X=1\mid T=0).
\end{aligned}
$$

Es decir: la letalidad total en AMBA es un promedio ponderado de las letalidades de jóvenes y mayores. Los pesos son las proporciones de cada grupo etario dentro de AMBA. La misma descomposición vale para CABA reemplazando $T=0$ por $T=1$.
