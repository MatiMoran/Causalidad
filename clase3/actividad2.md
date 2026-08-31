# Actividad 2 — Paradoja de Simpson y causalidad

Sean $X$, $T$ e $Y$ variables binarias:

- $X$: tamaño de la piedra; $X=1$ si la piedra es grande y $X=0$ si es pequeña.
- $T$: tratamiento; $T=1$ para cirugía convencional y $T=0$ para cirugía laparoscópica.
- $Y$: resultado; $Y=1$ si la intervención es exitosa y $Y=0$ si no lo es.

Además, $Y^{(1)}$ e $Y^{(0)}$ denotan los outcomes potenciales: el resultado que tendría una persona bajo cirugía convencional o laparoscópica, respectivamente.

## 1. Expresión ingenua u observacional

Decir que el tratamiento 1 es mejor para pacientes con piedras pequeñas y grandes significa observar:

$$
P(Y=1\mid T=1, X=x) > P(Y=1\mid T=0, X=x),
\qquad \text{para todo } x\in\{0,1\}.
$$

Es decir:

$$
P(Y=1\mid T=1, X=0) > P(Y=1\mid T=0, X=0)
$$

y

$$
P(Y=1\mid T=1, X=1) > P(Y=1\mid T=0, X=1).
$$

Pero afirmar ingenuamente que el tratamiento 1 es peor para la población total significa:

$$
P(Y=1\mid T=1) < P(Y=1\mid T=0).
$$

Estas tres desigualdades pueden ocurrir simultáneamente. La razón es que los grupos que reciben cada tratamiento pueden tener proporciones distintas de piedras grandes y pequeñas. Por ejemplo, si la cirugía convencional se usa más frecuentemente en piedras grandes —que tienen menor probabilidad de éxito— su tasa agregada puede ser inferior aun cuando sea mejor dentro de cada tamaño de piedra. Esta es la paradoja de Simpson.

## 2. Expresión causal y demostración para toda la población

La afirmación causal «el tratamiento 1 es mejor para pacientes con piedras pequeñas y grandes» se expresa como:

$$
P(Y^{(1)}=1\mid X=x) > P(Y^{(0)}=1\mid X=x),
\qquad \text{para todo } x\in\{0,1\}.
$$

Queremos demostrar que entonces el tratamiento 1 también es mejor para toda la población:

$$
P(Y^{(1)}=1) > P(Y^{(0)}=1).
$$

Por la ley de la probabilidad total:

$$
P(Y^{(t)}=1)
= \sum_{x\in\{0,1\}} P(Y^{(t)}=1\mid X=x)P(X=x),
\qquad t\in\{0,1\}.
$$

Por lo tanto, la diferencia causal total puede escribirse como:

$$
\begin{aligned}
& P(Y^{(1)}=1) - P(Y^{(0)}=1) \\
= {} & \sum_{x\in\{0,1\}}
\left[
P(Y^{(1)}=1\mid X=x) - P(Y^{(0)}=1\mid X=x)
\right]P(X=x).
\end{aligned}
$$

Cada diferencia entre corchetes es estrictamente positiva por la hipótesis causal. Además, cada peso $P(X=x)$ es no negativo. En consecuencia, la suma es positiva y se concluye que:

$$
P(Y^{(1)}=1) > P(Y^{(0)}=1).
$$

No hay paradoja en la comparación causal: ambos tratamientos se evalúan sobre la misma distribución de tamaños de piedra, $P(X=x)$.

## 3. Aleatorización condicional

Ahora supongamos que se observa que el tratamiento 1 es mejor dentro de cada estrato de tamaño:

$$
P(Y=1\mid T=1, X=x) > P(Y=1\mid T=0, X=x),
\qquad \text{para todo } x\in\{0,1\}.
$$

Supongamos también aleatorización condicional:

$$
Y^{(t)} \perp T \mid X,
\qquad t\in\{0,1\},
$$

junto con consistencia, es decir, $Y=Y^{(t)}$ cuando $T=t$. Se requiere además positividad:

$$
P(T=t\mid X=x)>0,
\qquad \text{para todo } t,x\in\{0,1\}.
$$

Para cada tamaño de piedra y cada tratamiento, la aleatorización condicional permite reemplazar el outcome potencial por la información observada:

$$
\begin{aligned}
P(Y^{(t)}=1\mid X=x)
= {} & P(Y^{(t)}=1\mid T=t, X=x) \\
= {} & P(Y=1\mid T=t, X=x).
\end{aligned}
$$

La primera igualdad usa $Y^{(t)} \perp T\mid X$ y la segunda usa consistencia. Así, la desigualdad observacional dentro de cada estrato implica la desigualdad causal dentro de cada estrato:

$$
P(Y^{(1)}=1\mid X=x) > P(Y^{(0)}=1\mid X=x).
$$

Aplicando el resultado del punto 2:

$$
P(Y^{(1)}=1) > P(Y^{(0)}=1).
$$

En conclusión, si el tratamiento se asigna aleatoriamente una vez fijado el tamaño de la piedra, la evidencia observacional estratificada identifica el efecto causal. Por eso se puede concluir que la cirugía convencional es mejor para la población total.
