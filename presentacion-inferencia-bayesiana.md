# Inferencia bayesiana — esqueleto

**15 min** (charla + cierre; Q&A después) · **Matias Moran** · Fundamentos matemáticos de la causalidad · 2° cuatrimestre 2026

**Orden:** portada → DAG → ATE en cinco pasos (3-1 a 3-5) → continuará → CEO de NVIDIA → microchips → frecuentismo (dos pasos) → regla de Bayes en tres pasos (9-1 a 9-3) → beta-binomial → posterior → credible/confidence → no cutoff → volvemos al invernadero → modelo y cierre de `F` (15 y 15-2) → marginales → tres respuestas y parámetros reales (17 y 17-2) → small/large → Q&A → libros → takeaways. Los apéndices van después.

**Regla:** una idea por slide. Las citas son textuales; los números son los del notebook reproducible (`seed 1`).

---

## 1 · Portada
**0:20**

# Inferencia bayesiana: pensar con incertidumbre

Matias Moran
Fundamentos matemáticos de la causalidad · 2° cuatrimestre 2026

> Sin subtítulo. El nombre, la materia y el cuatrimestre van en azul para que resalten.

---

## 2 · El problema: el invernadero
**0:45**

Solo el DAG, grande, para explicar el problema sin apurar la respuesta.

**DAG:** `H0 → H1`, `T → F → H1`, `T → H1`.

**Debajo del DAG:** 100 plantas. El tratamiento se asignó al azar; el hongo apareció después.

> `H0` = altura inicial; `T` = tratamiento; `F` = hongo; `H1` = altura final.
>
> `F` es post-tratamiento: está en el camino causal. No resolver todavía el ATE ni las preguntas; esta slide instala el problema.

---

## 3-1 · El problema causal y el ATE
**0:20**

**ATE**

`ATE = E[h1(1) − h1(0)]`

`ATE_hat = media(h1 | T=1) − media(h1 | T=0) = 1.05 cm`

IC 95% bootstrap `[0.13, 1.95] cm`.

Debajo del DAG: 100 plantas. El tratamiento se asignó al azar; el hongo apareció después.

> Base de la secuencia. Sin preguntas todavía y sin el cierre “un número”.

---

## 3-2 · Primera pregunta
**0:15**

Igual que 3-1, más:

**¿Cuál es la probabilidad de que el tratamiento haga crecer, en promedio?**

> Pregunta en lenguaje natural, no en fórmula. La fórmula queda para después de Bayes.

---

## 3-3 · Segunda pregunta
**0:15**

Igual que 3-1, más las dos primeras preguntas:

- ¿Cuál es la probabilidad de que el tratamiento haga crecer, en promedio?
- ¿Cuál es la probabilidad de que ese efecto esté entre 0.5 y 1.5 cm?

---

## 3-4 · Tercera pregunta
**0:15**

Igual que 3-1, más las tres preguntas:

- ¿Cuál es la probabilidad de que el tratamiento haga crecer, en promedio?
- ¿Cuál es la probabilidad de que ese efecto esté entre 0.5 y 1.5 cm?
- ¿Cuál es la probabilidad de que al menos 5 de 10 plantas nuevas tratadas superen los 14 cm?

---

## 3-5 · Un número, todavía no una respuesta
**0:20**

Misma slide que 3-4, más el cierre:

**Un número. Todavía no una respuesta a la decisión.**

> El ATE no responde las tres preguntas. Eso queda instalado antes de pasar a los chips.

---

## 4 · Continuará
**0:10**

Solo la imagen `continue.jpg`.

> “Volvemos a estas preguntas.” No explicar nada más: es una pausa narrativa.

---

## 5 · CEO de NVIDIA
**0:30**

**CEO de NVIDIA** como categoría, sin título central.

Imagen de Jensen a la izquierda; a la derecha, el texto:

# Sos el nuevo CEO

Tu primer tarea es decidir si es rentable fabricar los nuevos chips.

> Tono: juego, no fanatismo. La imagen es alivio cómico, no la protagonista. La decisión es la excusa para hablar de incertidumbre.

---

## 6 · Hook — los microchips
**1:30**

**Fabrico 9 microchips. Anoto si funciona (E) o falla (F):**

`E  F  E  E  E  F  E  F  E`

**¿Qué fracción de los chips sale bien?**

Preguntas, una debajo de otra:

- ¿Más o menos de la mitad funcionan?
- ¿Y más del 60%?
- Si fabrico 20 chips nuevos, ¿cuántos podrían fallar?
- ¿Qué probabilidad hay de que funcionen 4 o menos?

> Pedir 3–4 apuestas antes de mostrar nada. No corregir todavía.
>
> `E` = éxito (funciona); `F` = fallo (defectuoso). La posterior `Beta(7,4)` es para `p = fracción que funciona`.

---

## 7 · Frecuentista: lo que da
**1:00**

**Lo que te da:**
- MLE: `p̂ = 6/9 = 0.667`
- IC 95% exacto: `[0.30, 0.93]`
- Test `H0: p = 0.5` → `p ≈ 0.25` (una cola) / `0.51` (dos colas)
- Conclusión: “no rechazo que la mitad funcione”

**Imágenes de la notebook:**
- Bootstrap: 10.000 remuestreos de 9 chips.
- Bajo `H0: p = 0.5`, observar 6 o más éxitos tiene probabilidad 0.25.

> Dejar la mitad inferior vacía. La próxima slide revela lo que falta.

---

## 8 · Frecuentista: lo que no da
**0:45**

Misma parte superior. Abajo aparece:

**Lo que no te da:**
- `P(p > 0.5 | datos)`
- `P(p > 0.6 | datos)`
- `P(≤4 éxitos en 20 | datos)`

**Punchline:** el test responde `P(datos | H)`, no `P(H | datos)`.

---

## 9-1 · La regla de Bayes, bloque 01
**0:20**

`P(H | D) P(D) = P(D | H) P(H)`

Un solo hint azul debajo:

- **Posterior:** `P(H | D)` — lo que creés después de ver los datos.
- **Likelihood:** `P(D | H)` — qué tan probables son los datos si `H` fuera cierto.
- **Prior:** `P(H)` — lo que creías antes de ver los datos.

> No mostrar los tres bloques juntos. Primero la definición y el vocabulario.

---

## 9-2 · La regla de Bayes, bloque 02
**0:15**

`P(H | D) = P(D | H) P(H) / P(D)`

Hint: dividimos por `P(D)`, la probabilidad de los datos bajo todos los modelos posibles. Ese denominador normaliza la posterior; no cambia qué hipótesis queda mejor rankeada.

---

## 9-3 · La regla de Bayes, bloque 03
**0:20**

`P(H | D) ∝ P(D | H) P(H)`

Hint: `P(D)` es constante una vez observados los datos: normaliza, no cambia el ranking. La posterior es proporcional a likelihood × prior.

> Este bloque va con remarcado más grueso: es la forma final que importa para calcular.

---

## 10 · Prior, likelihood y posterior
**0:45**

**Prior:** `p ~ Beta(1,1)` — plano, todos los valores entre 0 y 1 igual de plausibles. Abajo, el gráfico plano.

**Likelihood:** `y | p ~ Binomial(9,p)`; con `y = 6`, `p^6 (1−p)^3`. Abajo, la curva de verosimilitud.

**Posterior:** `p | y ~ Beta(7,4)` — sumar 6 éxitos y 3 fallos al prior plano. Abajo, la densidad posterior.

`Beta(1,1) + 6E + 3F → Beta(7,4)`

> Es el mismo “contar y comparar” del hook, ahora con nombres y con la forma de cada función.

---

## 11 · Bayes responde
**1:00**

**Posterior:** `p | datos ~ Beta(7,4)`
- Mediana `0.64` · IC 95% `[0.35, 0.88]`
- `P(p > 0.5) = 0.83`
- `P(p > 0.6) = 0.62`
- `P(≤4 éxitos en 20) = 1.2%` · plug-in `Binomial(20, 0.667) = 0.009%`

Cada bloque tiene arriba su gráfico: la posterior Beta con el área sombreada que representa la pregunta.

**La receta:** sampleás de la posterior y contás.

---

## 12 · Credible vs confidence
**1:00**

**Bayes:** `P(p ∈ [0.35, 0.88] | datos) = 0.95`
“Hay 95% de probabilidad posterior de que `p` esté ahí.”

**Frecuentista:** IC 95% exacto `[0.30, 0.93]`. “Si repitieras el experimento muchas veces, 95% de los intervalos así construidos cubrirían el `p` verdadero.”

> Los dos intervalos están graficados. Sin cita decorativa ni footer extra.

---

## 13 · No hay cutoff
**0:30**

`P(p > 0.6 | datos) = 0.62` — hay 62% de probabilidad posterior de que más de 60% funcione. No es “significativo sí/no”.

- La evidencia es continua.
- “Significativo / no significativo” da falsa comodidad.
- Definí “sustancial” **antes** de ver los datos.

> Cita: “This practice provides false comfort. Reality is not so clear-cut.” — *Bayes Rules!*

---

## 14 · Volviendo a nuestro caso original
**0:30**

Título: **Volviendo a nuestro caso original...**

Otra vez el DAG del invernadero. A la derecha, las tres preguntas que el ATE no responde:

- `P(ATE > 0 | datos)`
- `P(0.5 < ATE < 1.5 cm | datos)`
- `P(≥5 de 10 plantas nuevas tratadas > 14 cm | datos)`

> El ATE era `1.05 cm [0.13, 1.95]`. Ninguna de estas tres preguntas era parte de ese número.

---

## 15 · Un modelo lineal en cm
**0:35**

DAG de referencia a la izquierda; modelo más grande a la derecha:

```text
h1_i ~ Normal(mu_i, sigma)
mu_i = a + bT*T_i + bH*(h0_i - mean(h0))
a ~ Normal(mean(h1), 5)
bT ~ Normal(0, 5)
bH ~ Normal(0, 1)
sigma ~ HalfNormal(5)
```

Abajo del modelo: `β_T` es el cambio promedio en altura final para una planta tratada, ajustando por altura inicial. Está en cm, así que es directamente comparable con el ATE.

> Dejar espacio abajo para la conclusión sobre `F`. No decirla todavía.

---

## 15-2 · El modelo y el cierre de `F`
**0:20**

Misma slide, más el texto grande abajo:

**No incluimos `F`:** es post-tratamiento y está en el camino causal.

> El modelo no es “más completo” por meter más variables. El DAG decide.

---

## 16 · Las marginales
**0:40**

Título: **Las marginales**.

Gráfico de marginales de `a`, `β_T`, `β_H` y `σ`, sin las cadenas.

`β_T = 1.20 cm [0.69, 1.71]` al 89%.

> MCMC produce las cadenas; acá mostramos solo la distribución marginal de cada parámetro.

---

## 17 · La posterior responde
**0:50**

Modelo sin `F`: `β_T = 1.20 cm [0.69, 1.71]` (89%).

| Pregunta | Respuesta |
|---|---|
| `P(ATE > 0 \| datos)` | `1.000` |
| `P(0.5 < ATE < 1.5 cm \| datos)` | `0.81` |
| `P(≥5 de 10 plantas nuevas tratadas > 14 cm \| datos)` | `0.78` |

Cada bloque tiene su gráfico: posterior de `β_T` con área sombreada y predictiva posterior del conteo.

**Observación:** el ATE frecuentista era `1.05 cm [0.13, 1.95]`: otro número, otro intervalo, y no respondía estas preguntas.

---

## 17-2 · Los parámetros reales de la simulación
**0:35**

Misma slide, más el panel de verdad:

`h0 ~ Normal(10,2)`, `T` 50/50, `P(F=1 | T=0) = 0.5`, `P(F=1 | T=1) = 0.1`, `h1 = h0 + Normal(5 − 3F, 1)`.

En el modelo sin `F`: `a = 13.5`, `β_T = 1.2`, `β_H = 1`, `σ = 1`.

El ATE verdadero es `1.2 cm`; con `F`, `β_T` verdadero `= 0`.

> Sirve para separar “lo que el modelo estima” de “lo que sabíamos porque simulamos”.

---

## 18 · Small world / large world
**1:00**

**Bayes es óptimo *dado* el modelo.** El modelo es el small world.

- Los dos modelos son igual de bayesianos; uno responde la pregunta causal correcta.
- El posterior no elige el DAG: lo elegís vos.
- El large world se demuestra, no se deduce.

> Cita: “The logical consistency of a model in the small world is no guarantee that it will be optimal in the large world. But it is certainly a warm comfort.” — *Statistical Rethinking*

---

## 19 · Q&A
**abrir el espacio**

> Dejar esta slide en pantalla. Cuando se agoten las preguntas, pasar a libros y cerrar con takeaways.

---

## 20 · Libros y autores
**0:20**

**Bayes Rules!**
*Alicia A. Johnson · Miles Q. Ott · Mine Dogucu*

**Statistical Rethinking**
*Richard McElreath*

> Sin capítulos ni abreviaturas: solo el nombre del libro.

---

## 21 · Key takeaways
**0:45**

1. **Bayes = prior × likelihood → posterior.** Actualizás, no descartás.
2. **El posterior es el producto.** Distribución completa: `P(ATE>0)`, `P(0.5<ATE<1.5)`, predicciones. Sin cutoff.
3. **El prior es una feature, no un bug.** Con pocos datos, es la única forma de usar lo que sabés.
4. **Óptimo en el small world; en el large world, el DAG manda.**

**No llegamos a ver:**
- Actualización secuencial
- Modelos jerárquicos
- Decision theory
- Markov chain Monte Carlo (MCMC)

> El bloque de “no llegamos a ver” va como bullets, con texto más grande y ocupando el espacio inferior.

---

# Apéndices (no cuentan en los 15)

## A · Fairness frecuentista
**0:30**

Un frecuentista sofisticado puede responder varias de estas preguntas con maquinaria extra:

| Pregunta | Frecuentista sofisticado | Bayes |
|---|---|---|
| `P(p > 0.5 \| datos)` | confidence distribution | posterior |
| `P(p > 0.6 \| datos)` | fiducial inference | posterior |
| `P(≤4 éxitos en 20 \| datos)` | bootstrap predictivo | predictiva posterior |
| actualizar secuencialmente | group sequential designs | posterior secuencial |

**Cierre:** no es que no se pueda. Es que no es el default, y la interpretación no es la misma. Bayes lo hace con una sola receta.

> Tono: reconocer, no militar. Fiducial tiene sus caveats; el punto es que existe maquinaria.

## B · El prior cuando el dato es poco: un exoplaneta
**1:30**

- **Tierra (control):** ya sabemos `p ≈ 0.71`. Prior `Beta(71,29)` + 6A/3T → posterior `Beta(77,32)`, media `0.706`, IC 95% `[0.62, 0.79]`. El prior domina, y está bien: ya lo sabíamos.
- **Exoplaneta rocoso en zona habitable:** no sabemos su `p`, pero sabemos algo de la población. Prior `Beta(7,3)` (media `0.7`, “esperamos un planeta océano”) + 9 observaciones (4 agua, 5 tierra) → posterior `Beta(11,8)`, media `0.579`, IC 95% `[0.36, 0.78]`.
- **Con prior débil `Beta(2,2)`:** posterior `Beta(6,7)`, media `0.462`, IC 95% `[0.21, 0.72]`.
- **Moraleja:** con pocos datos, el prior es la única forma de meter el conocimiento de dominio. Con muchos datos, se diluye. No es trampa: es modelar.

> Si preguntan: con datos fuertes, los posteriores convergen. *Bayes Rules!*

## C · Predicción con la posterior (20 chips)
**0:45**

- `P(≤4 éxitos en 20 | datos)`: sampleás `p` de `Beta(7,4)`, simulás 20 chips, contás → `1.2%`.
- Plug-in `Binomial(20, 0.667)` → `0.009%`.
- “El plug-in ignora la incertidumbre en `p`; la predictiva posterior no.”

> Esta es la receta que generaliza al modelo causal: samplear y contar.

## D · Dos modelos, una decisión causal
**1:00**

| Modelo | `β_T` (cm) | Lectura |
|---|---|---|
| Sin `F` | `1.20 [0.69, 1.71]` | el tratamiento funciona |
| Con `F` | `0.03 [-0.28, 0.35]` | “no funciona” |

Forest plot con los dos intervalos al 89%.

**El DAG decide, no el fit.** Controlar `F` bloquea `T → F → H1`; por eso no lo incluimos: es post-tratamiento y sesga el índice.

> Cita: “a correct inference about the treatment still depends upon omitting the post-treatment variable.” — *Statistical Rethinking*

---

# Backup — preguntas probables

- **“¿No es subjetivo el prior?”** Es explícito y auditable; el frecuentismo también elige modelo, estimador y α. Con datos fuertes, los posteriores convergen.
- **“¿Por qué no bootstrap / confidence distribution?”** Se puede; la interpretación no es la misma. Bayes da el posterior directo (Apéndice A).
- **“¿Y la actualización secuencial?”** No la vimos; Bayes actualiza naturalmente. El frecuentismo necesita diseños secuenciales.
- **“¿Qué pasa si el DAG está mal?”** Bayes no arregla un modelo malo. Small world vs large world: el DAG lo elige el experto.
- **“¿Y si necesito decidir?”** Ahí entra decision theory: costo/beneficio, no un cutoff automático.

---

# Si vas justo

- Slide 2 (DAG) → 30 s.
- Slides 3-1 a 3-5 (ATE y preguntas) → 45 s en total.
- Slides 7 y 8 (frecuentista) → contar solo “lo que da” y revelar “lo que no da” en una frase.
- Slides 9-1 a 9-3 (Bayes) → 30 s: definición, despeje, forma final.
- Slide 12 (credible) → 30 s.
- Slide 16 (marginales) → mostrar el gráfico y decir “el DAG ya decidió; acá solo cuantificamos”.
- Apéndices → fuera de los 15; solo si sobra tiempo o si preguntan.

---

# Notebook

`analisis_causal_hongos_bayesiano.ipynb` (raíz del repo) reproduce todos los números y las figuras de `figuras/`.
