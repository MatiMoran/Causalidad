# Bounds para el ATE sin identificación

Esta nota desarrolla los cuatro incisos trabajados en clase. La idea central es importante: que el ATE no esté **identificado** no significa que no podamos decir nada sobre él. Significa que los datos observados son compatibles con varios valores del ATE; los *bounds* describen el intervalo de todos esos valores posibles.

## 0. Qué queremos estimar y qué falta observar

Sea $T\in\{0,1\}$ el tratamiento y sea $Y\in\{0,1\}$ un outcome binario. Para cada persona existen dos outcomes potenciales:

- $Y^{(1)}$: outcome si recibiera tratamiento.
- $Y^{(0)}$: outcome si no lo recibiera.

El parámetro causal de interés es

$$
\operatorname{ATE}=\mathbb{E}[Y^{(1)}-Y^{(0)}].
$$

Para cada persona solo observamos uno de los dos outcomes potenciales:

$$
Y = T Y^{(1)}+(1-T)Y^{(0)}.
$$

Esta es la hipótesis de consistencia: si una persona fue tratada, su $Y$ observado es $Y^{(1)}$; si no fue tratada, es $Y^{(0)}$. No estamos suponiendo aleatorización ni ausencia de confusión.

Por eso, comparar $\mathbb{E}[Y\mid T=1]$ con $\mathbb{E}[Y\mid T=0]$ no identifica el ATE: los dos grupos pueden ser distintos antes del tratamiento y, además, para cada persona queda un contrafactual sin observar.

## 1. El cuadro de tipos potenciales

Cada persona pertenece a uno de cuatro tipos según $(Y^{(1)},Y^{(0)})$:

| Tipo | $(Y^{(1)},Y^{(0)})$ | Efecto individual $Y^{(1)}-Y^{(0)}$ |
|---|---:|---:|
| Nunca tiene el outcome | $(0,0)$ | $0$ |
| Se beneficia del tratamiento | $(1,0)$ | $+1$ |
| Se perjudica con el tratamiento | $(0,1)$ | $-1$ |
| Siempre tiene el outcome | $(1,1)$ | $0$ |

Si llamamos $x_1,\ldots,x_4$ a las proporciones de esos cuatro tipos entre tratados y $x_5,\ldots,x_8$ a las mismas proporciones entre controles, respectivamente, entonces

$$
\operatorname{ATE}=x_2+x_6-x_3-x_7.
$$

Es decir: el ATE es la fracción que se beneficia menos la fracción que se perjudica. Los $x_i$ no se conocen por completo porque cada grupo revela solamente una de las dos coordenadas de cada tipo.

> En el apunte breve de clase, la expresión del punto 2 aparece con el signo invertido. Con la definición usual $\mathbb{E}[Y^{(1)}-Y^{(0)}]$ y el orden $(Y^{(1)},Y^{(0)})$, la expresión correcta es la de arriba.

## 2. Qué sí revelan los datos observados

Definimos las cuatro probabilidades observables:

| | $Y=0$ | $Y=1$ |
|---|---:|---:|
| $T=1$ | $q_1=P(T=1,Y=0)$ | $q_2=P(T=1,Y=1)$ |
| $T=0$ | $q_3=P(T=0,Y=0)$ | $q_4=P(T=0,Y=1)$ |

Por consistencia:

- Las personas en $q_1$ tienen $Y^{(1)}=0$, pero no sabemos su $Y^{(0)}$.
- Las personas en $q_2$ tienen $Y^{(1)}=1$, pero no sabemos su $Y^{(0)}$.
- Las personas en $q_3$ tienen $Y^{(0)}=0$, pero no sabemos su $Y^{(1)}$.
- Las personas en $q_4$ tienen $Y^{(0)}=1$, pero no sabemos su $Y^{(1)}$.

Esto es exactamente “no hay identificación”: los mismos $q_1,\ldots,q_4$ admiten varios cuadros de outcomes potenciales y, por lo tanto, varios ATE.

## 3. Bounds de Manski para el ATE

Para hacer el ATE lo más pequeño posible, asignamos el peor contrafactual compatible con lo observado:

- Quienes están en $q_1$ pueden tener efecto $-1$.
- Quienes están en $q_4$ pueden tener efecto $-1$.
- Los otros dos grupos no necesitan aportar un efecto negativo.

Por lo tanto,

$$
\operatorname{ATE}_{\min}=-q_1-q_4.
$$

Para hacer el ATE lo más grande posible, asignamos el mejor contrafactual compatible:

- Quienes están en $q_2$ pueden tener efecto $+1$.
- Quienes están en $q_3$ pueden tener efecto $+1$.
- Los otros dos grupos no necesitan aportar un efecto positivo.

Así obtenemos

$$
\boxed{-q_1-q_4\ \leq\ \operatorname{ATE}\ \leq\ q_2+q_3.}
$$

Son bounds “honestos”: no inventan aleatorización. Solo usan que $Y$ es binaria y que el outcome observado coincide con el potencial correspondiente al tratamiento efectivamente recibido. Si tampoco aceptáramos consistencia, ni siquiera los $q_i$ informarían sobre los outcomes potenciales y el bound trivial sería $[-1,1]$.

## 4. Ejemplo 0: dos personas y el mismo dato observado

Observamos dos personas:

| Persona | Tratamiento observado | Outcome observado |
|---|---:|---:|
| Ana | $T=1$ | $Y=1$ |
| Beto | $T=0$ | $Y=0$ |

Entonces $q_2=q_3=1/2$ y $q_1=q_4=0$. El bound es

$$
0\leq \operatorname{ATE}\leq 1.
$$

Los datos observados son iguales en estos dos mundos:

| Mundo | Ana $(Y^{(1)},Y^{(0)})$ | Beto $(Y^{(1)},Y^{(0)})$ | ATE |
|---|---:|---:|---:|
| A: tratamiento no cambia nada | $(1,1)$ | $(0,0)$ | $0$ |
| B: tratamiento ayuda a ambos | $(1,0)$ | $(1,0)$ | $1$ |

No podemos decidir entre ambos mundos mirando solo esos dos datos. Por eso no hay identificación. Pero sí sabemos que, dadas esas observaciones, el ATE no puede ser negativo ni mayor que uno.

## 5. Ejemplo de juguete: cuatro personas

Supongamos que en una muestra de cuatro personas observamos una en cada celda: una tratada con $Y=0$, una tratada con $Y=1$, una control con $Y=0$ y una control con $Y=1$. Entonces

$$
q_1=q_2=q_3=q_4=1/4.
$$

La diferencia observacional entre tratados y controles es cero, pero el ATE causal satisface

$$
-1/2\leq \operatorname{ATE}\leq 1/2.
$$

El cero observado no prueba que el efecto causal sea cero: puede haber selección al tratamiento que oculte un efecto positivo o negativo. La información disponible solo permite descartar efectos fuera de ese intervalo.

## Idea para recordar

La identificación transforma datos observados en un único valor causal añadiendo supuestos, por ejemplo aleatorización o intercambio condicional. Los bounds hacen otra cosa: conservan únicamente supuestos mínimos y devuelven todos los valores causales que siguen siendo compatibles con los datos. Si el intervalo es ancho, no es un error del método; es una medida explícita de cuánta información causal falta.
