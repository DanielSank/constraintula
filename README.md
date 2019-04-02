# constraintula

```python
>>> from constraintula import Symbol, System
>>> a = Symbol('a')
>>> b = Symbol('b')
>>> ratio = Symbol('r')
>>> product = Symbol('p')
>>> equations = set([product - (a * b), ratio - (a / b)])
>>> system = System(equations)
>>> system.constrain_symbol(ratio)
False
>>> system.constrain_symbol(product)
Solved for a
Solved for b
True
>>> system.solutions
{r: r, p: p, a: r*sqrt(p/r), b: sqrt(p/r)}
>>>
```
