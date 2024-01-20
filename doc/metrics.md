# Metric Solver API

## Signal-to-Noise Ratio 
The signal-to-noise ratio of a signal is defined as the ratio of a signal's data component to the signal's noise 
component. For side-channel analysis, the SNR of a power trace relates to the ability for an attacker to obtain 
information from a power trace during an attack. The effectiveness of side channel attack increases for larger SNR 
values since the signal leakage is more prominent relative to the noise of the signal. Typically recorded power traces 
need to be partitioned into different sets called labels.
```{math}
SNR = \frac{VAR(L_d)}{VAR(L_n)} = \frac{\sum_{v=0}^{V} (\hat{\mu_v}^2 - \hat{\mu})^2}{\hat{\sigma}^2}
```
The resulting array is the value of the SNR at a given discrete time sample. Windows of the resulting trace where the 
magnitude of the SNR is high may also indicate an area of interest since it implies that there exists a significant 
amount of leakage at that sample. 
signal_to_noise_ratio(labels)



## Table

| No.  |  Prime |
| ---- | ------ |
| 1    |  No    |
| 2    |  Yes   |
| 3    |  Yes   |
| 4    |  No    |



## Code blocks

The following is a Python code block:
```python
  def hello():
      print("Hello world")
```

And this is a C code block:
```c
#include <stdio.h>
int main()
{
    printf("Hello, World!");
    return 0;
}
```


## Math

This creates an equation:
```{math}
a^2 + b^2 = c^2
```

This is an in-line equation, {math}`a^2 + b^2 = c^2`, embedded in text.
