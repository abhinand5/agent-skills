# The language of consequences

The central object is a *trajectory* $S_0, A_0, R_1, S_1, A_1, R_2, \ldots$ and
everything else is an answer to one of three questions [@suttonbarto2018].

::: mentalmodel
An algorithm sits inside a causal loop. Its policy changes the data distribution;
the new data changes its estimates; the estimates change the policy.
:::

## Return and objective

For an infinite discounted task, define the return

$$
G_t = R_{t+1} + \gamma R_{t+2} + \gamma^2 R_{t+3} + \cdots = R_{t+1} + \gamma G_{t+1},
\qquad 0 \leq \gamma < 1.
$$

If rewards satisfy $|R_t| \leq R_{\max}$ then $|G_t| \leq R_{\max}/(1-\gamma)$.

::: {.example title="Constant reward"}
A task pays reward $1$ forever. With $\gamma = 0.9$,
$v = \sum_{t \geq 0} \gamma^t = 1/(1-\gamma) = 10$.
:::

::: failuremode
A single camera frame in a control task may omit velocity. No learning algorithm
can repair information the observation discarded.
:::

![The projection keeps the expressible component and discards an orthogonal residual.](assets/projection.svg)

::: {.algorithm title="Value iteration"}
Initialise $v(s)$ arbitrarily. Repeat sweeps over states:
$v(s) \leftarrow \max_a \sum_{s'} P(s' \mid s, a)\,[r(s,a) + \gamma v(s')]$.
Stop when the Bellman residual is small enough.
:::

::: checkpoint
**1.1** Show that $\sum_a \pi(a \mid s) A_\pi(s,a) = 0$.

**1.2** Compute $v$ for $\gamma = 0.99$ in the constant-reward example.
:::

::: takeaway
Value is a conditional forecast under a named policy.
:::

*Read deeper:* Sutton and Barto, Chapters 3–4 [@suttonbarto2018]; Watkins and Dayan [@watkins1992].
