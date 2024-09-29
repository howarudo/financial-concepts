## Statistical Analysis

### Constant Mean Return Model
For abnormal return calculation, we use the **Constant Mean Return Model**. The model assumes that the stock price has a constant mean return over the event window.

$$
R_{t} = \mu + \epsilon_{t}
$$
$$
E[\epsilon_{t}] = 0, Var[\epsilon_{t}] = \sigma_{\epsilon}^2
$$

where $R_{t}$ is the return of stock at time $t$, $\mu$ is the stock-specific constant, and $\epsilon_{t}$ is the error term.


### Statistical Test
For a given time window of $[t_i - 2, t_i + 3]$, we calculate the mean return during this window. Then we calculate the **abnormal return** by subtracting the mean return from the actual return at time $t_i$.

$$
R_{MVA, t} = \frac{1}{5} \sum_{j = -2}^{3} R_{t + j}
$$

Hence, the statistical test for this model is:

$$
H_0: R_{MVA, t} = \mu
$$
$$
H_1: R_{MVA, t} \neq \mu
$$

where $H_0$ is the null hypothesis, and $H_1$ is the alternative hypothesis.
