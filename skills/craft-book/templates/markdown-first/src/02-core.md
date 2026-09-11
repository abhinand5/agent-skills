# The reusable core

For the sup norm $\|v\|_\infty = \max_s |v(s)|$ the operator is a $\gamma$-contraction:

$$
\|\mathcal{T}^{\pi} v - \mathcal{T}^{\pi} w\|_\infty \leq \gamma \|v - w\|_\infty .
$$

## A table with maths in it

| Symbol        | Meaning                                  |
|:--------------|:-----------------------------------------|
| $G_t$         | discounted return from time $t$          |
| $v_\pi, q_\pi$ | state and action values under $\pi$     |
| $\mathcal{T}^{\pi}$ | Bellman expectation operator       |

::: printonly
This paragraph appears only in the PDF edition.
:::

::: epubonly
This paragraph appears only in the EPUB edition.
:::

::: mdonly
This paragraph appears only in the Markdown edition.
:::

::: checkpoint
**2.1** Prove $|\max_a x_a - \max_a y_a| \leq \max_a |x_a - y_a|$.
:::
