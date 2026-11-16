# Inferencia bayesiana — esqueleto

**15 min** (charla + cierre; Q&A después) · **Matias Moran** · Fundamentos matemáticos de la causalidad · 2° cuatrimestre 2026

**Orden:** problema causal → microchips → frecuentismo y su techo → Bayes → credible/confidence → no cutoff → dos modelos → posterior responde → small/large → Q&A → libros → takeaways. Los apéndices van después.

**Regla:** una idea por slide. Máximo 5 bullets. Las citas son textuales; los números son los del notebook reproducible (`seed 1`).

---

## 1 · Título
**0:30**

# Inferencia bayesiana: pensar con incertidumbre
### De la fábrica al invernadero: qué da Bayes y qué le sigue pidiendo al modelo

Matias Moran
Fundamentos matemáticos de la causalidad · 2° cuatrimestre 2026

---

## 2 · El problema causal — el invernadero
**1:15**

100 plantas. Se mide altura inicial `h0`. Se aleatoriza tratamiento `T`. Al final: altura `h1` y presencia de hongo `F`.

**DAG:** `H0 → H1`, `T → F → H1`, `T → H1`.

**El ATE de la materia:**
`ATE = E[h1(1) − h1(0)]`
`ATE_hat = media(h1 | T=1) − media(h1 | T=0) = 1.05 cm`
IC 95% bootstrap `[0.13, 1.95]`

**Tres preguntas que el ATE no responde:**
- `P(ATE > 0 | datos)`
- `P(0.5 < ATE < 1.5 cm | datos)`
- `P(≥5 de 10 plantas nuevas tratadas > 14 cm | datos)`

> `F` es **post-tratamiento**: está en el camino causal. Volvemos a estas preguntas después de los chips.
>
> No resolver el DAG todavía: la slide instala el problema. La respuesta numérica llega en la slide 9.

---

## 3 · Hook — los microchips
**2:00**

**Fabrico 9 microchips. Anoto si funciona (E) o falla (F):**

`E  F  E  E  E  F  E  F  E`

**¿Qué fracción de los chips sale bien?**

> Pedir 3–4 apuestas antes de mostrar nada. No corregir todavía. La intuición ya está haciendo Bayes.
>
> `E` = éxito (funciona); `F` = fallo (defectuoso). La posterior `Beta(7,4)` es para `p = fracción que funciona`. Si querés la fracción defectuosa, es `1 − p`.

---

## 4 · El approach normal y su techo
**2:00**

**Lo que te da:**
- MLE: `p̂ = 6/9 = 0.667`
- IC 95% exacto: `[0.30, 0.93]`
- Test `H0: p = 0.5` → `p ≈ 0.25` (una cola) / `0.51` (dos colas)
- Conclusión: "no rechazo que la mitad funcione"

**Lo que no te da:**
- `P(p > 0.5 | datos)`
- `P(p > 0.6 | datos)`
- `P(≤4 éxitos en 20 | datos)`

**Punchline:** el test responde `P(datos | H)`, no `P(H | datos)`.

> **Concepto clave:** `p` es fijo en el mundo, incierto en tu cabeza. El frecuentista solo permite probabilidad para lo repetible (los chips); el bayesiano también para tu incertidumbre sobre `p`.
>
> **Inset (20 s):** test positivo en enfermedad rara → `P(enfermo | +) = 25%` vs `P(+ | sano) = 9.4%`. El test no está mal; la pregunta es otra.

---

## 5 · Bayes responde
**2:00**

**Posterior:** `p | datos ~ Beta(7,4)`
- Mediana `0.64` · IC 95% `[0.35, 0.88]`
- `P(p > 0.5) = 0.83`
- `P(p > 0.6) = 0.62`
- `P(≤4 éxitos en 20) = 1.2%` · plug-in `Binomial(20, 0.667) = 0.009%`

**El motor:** `posterior ∝ prior × likelihood`
Prior plano + 6E/3F → `Beta(7,4)`

**La receta:** sampleás de la posterior y contás.

> Cita SR2: "Bayesian inference is really just counting and comparing of possibilities."
>
> Cita SR2: "A Bayesian analysis is a garden of forking data, in which alternative sequences of events are cultivated."

---

## 6 · Credible vs confidence
**1:00**

**Bayes:** `P(p ∈ [0.35, 0.88] | datos) = 0.95`
"Hay 95% de probabilidad posterior de que `p` esté ahí."

**Frecuentista:** IC 95% exacto `[0.30, 0.93]`. "Si repitieras el experimento muchas veces, 95% de los intervalos así construidos cubrirían el `p` verdadero."

> Cita SR3: "The 95% is a *small world* number ... only true in the model's logical world. So it will never apply exactly to the real or *large world*. It is what the golem believes, but you are free to believe something else."
>
> No es "Bayes mejor": es otra pregunta.

---

## 7 · No hay cutoff
**0:45**

`P(p > 0.6 | datos) = 0.62` — más de 60% de los chips funcionan. No es "significativo sí/no".

- La evidencia es continua.
- "Significativo / no significativo" da falsa comodidad.
- Definí "sustancial" **antes** de ver los datos.

> Cita BR8: "This practice provides false comfort. Reality is not so clear-cut."
>
> Cita BR8: "there is no magic, one-size-fits-all cut-off for what Bayes Factor or posterior probability evidence is big enough to filter claims into 'true' or 'false' categories."

---

## 8 · Mismos datos, dos modelos
**1:30**

| Modelo | `β_T` (cm) | Lectura |
|---|---|---|
| Sin `F` | `1.20` `[0.69, 1.71]` | el tratamiento funciona |
| Con `F` | `0.03` `[-0.28, 0.34]` | "no funciona" |

**El DAG decide, no el fit.** Controlar `F` bloquea `T → F → H1`.

> Cita SR6: "a correct inference about the treatment still depends upon omitting the post-treatment variable."
>
> Callback: "la misma familia de errores que `Horas` en el café".
>
> Nota: simulación del libro (100 plantas, `seed 1`). Intervalos de credibilidad 89%.

---

## 9 · La posterior responde
**1:00**

Modelo sin `F`: `β_T = 1.20 cm [0.69, 1.71]` (89% de credibilidad). El ATE frecuentista era `1.05 cm [0.13, 1.95]`.

| Pregunta | Respuesta |
|---|---|
| `P(ATE > 0 \| datos)` | `> 0.99` |
| `P(0.5 < ATE < 1.5 cm \| datos)` | `0.81` |
| `P(≥5 de 10 plantas nuevas tratadas > 14 cm \| datos)` | `0.78` |

> La predictiva integra la incertidumbre en `β` y en la altura inicial. No es el efecto promedio: es una pregunta sobre 10 plantas nuevas.
>
> Números reproducibles en `clases/clase2/analisis_causal_hongos_bayesiano.ipynb`.

---

## 10 · Small world / large world
**1:00**

**Bayes es óptimo *dado* el modelo.** El modelo es el small world.

- Los dos modelos son igual de bayesianos; uno responde la pregunta causal correcta.
- El posterior no elige el DAG: lo elegís vos.
- El large world se demuestra, no se deduce.

> Cita SR2: "No other way of using the available information, beginning with the same state of information, could do better."
>
> Cita SR2: "The logical consistency of a model in the small world is no guarantee that it will be optimal in the large world. But it is certainly a warm comfort."
>
> Cita SR2: "There is no approach to inference that provides universal guarantees."

---

## 11 · Q&A
**abrir el espacio**

> Dejar esta slide en pantalla. Cuando se agoten las preguntas, pasar a libros y cerrar con takeaways.

---

## 12 · Libros y autores
**0:20**

**Bayes Rules!**
Alicia A. Johnson, Miles Q. Ott, Mine Dogucu
Caps. 1, 2, 4, 8

**Statistical Rethinking**
Richard McElreath
Caps. 1, 2, 3, 6

> Las citas textuales de la charla salen de estos dos libros.

---

## 13 · Key takeaways
**1:00**

1. **Bayes = prior × likelihood → posterior.** Actualizás, no descartás.
2. **El posterior es el producto.** Distribución completa: `P(ATE>0)`, `P(0.5<ATE<1.5)`, predicciones. Sin cutoff.
3. **El prior es una feature, no un bug.** Con pocos datos, es la única forma de usar lo que sabés.
4. **Óptimo en el small world; en el large world, el DAG manda.**

> **No llegamos a ver:** actualización secuencial, modelos jerárquicos, decision theory.
>
> Cierre: "Bayes te da la pregunta que querés hacer. El DAG te dice si la pregunta es causal."

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
- **Exoplaneta rocoso en zona habitable:** no sabemos su `p`, pero sabemos algo de la población. Prior `Beta(7,3)` (media `0.7`, "esperamos un planeta océano") + 9 observaciones (4 agua, 5 tierra) → posterior `Beta(11,8)`, media `0.579`, IC 95% `[0.36, 0.78]`.
- **Con prior débil `Beta(2,2)`:** posterior `Beta(6,7)`, media `0.462`, IC 95% `[0.21, 0.72]`.
- **Moraleja:** con pocos datos, el prior es la única forma de meter el conocimiento de dominio. Con muchos datos, se diluye. No es trampa: es modelar.

> Cita BR4 (si preguntan): "no matter the strength of and discrepancies among their prior understanding ... three analysts will come to a common posterior understanding in light of strong data."

## C · Predicción con la posterior (20 chips)
**0:45**

- `P(≤4 éxitos en 20 | datos)`: sampleás `p` de `Beta(7,4)`, simulás 20 chips, contás → `1.2%`.
- Plug-in `Binomial(20, 0.667)` → `0.009%`.
- "El plug-in ignora la incertidumbre en `p`; la predictiva posterior no."

> Esta es la receta que generaliza al modelo causal: samplear y contar.

---

# Backup — preguntas probables

- **"¿No es subjetivo el prior?"** Es explícito y auditable; el frecuentismo también elige modelo, estimador y α. Con datos fuertes, los posteriores convergen (BR4).
- **"¿Por qué no bootstrap / confidence distribution?"** Se puede; la interpretación no es la misma. Bayes da el posterior directo (Apéndice A).
- **"¿Y la actualización secuencial?"** No la vimos; Bayes actualiza naturalmente. El frecuentismo necesita diseños secuenciales.
- **"¿Qué pasa si el DAG está mal?"** Bayes no arregla un modelo malo. Small world vs large world: el DAG lo elige el experto.
- **"¿Y si necesito decidir?"** Ahí entra decision theory: costo/beneficio, no un cutoff automático.

---

# Si vas justo

- Slide 2 (causal) → 1:00.
- Slide 6 (credible) → 45 s.
- Slide 8 (dos modelos) → contar solo el resultado, sin la cita.
- Apéndices → fuera de los 15; solo si sobra tiempo o si preguntan.
