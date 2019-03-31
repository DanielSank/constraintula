# constraintula

```python
from constraintula import Symbol, System

a = Symbol('a')
b = Symbol('b')
ratio = Symbol('r')
product = Symbol('p')

equations = set([product - (a * b), ratio - (a / b)])

system = System(equations)

system.constrain_symbol(ratio)
system.constrain_symbol(product)
system.solutions
```
