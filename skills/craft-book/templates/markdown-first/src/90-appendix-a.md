\appendix

# Probability refresher

Conditioning zooms into the slice compatible with observed information and renormalises:

$$
p(x \mid y) = \frac{p(x,y)}{p_Y(y)}, \qquad p_Y(y) > 0.
$$

## A complete Bayes example

Terrain is slippery with probability $0.30$; a sensor fires with probability $0.80$
on slippery terrain and $0.10$ otherwise. After a warning,
$\Pr(\text{slippery} \mid \text{warning}) = 0.24 / 0.31 \approx 0.774$.

::: checkpoint
**A.1** Recompute the posterior with prior $0.05$.
:::
