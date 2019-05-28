# constraintula

```python
import attr
import constraintula
import numpy as np

PI = np.pi

area, radius = constraintula.symbols('area radius')


@constraintula.contrain([area - PI * radius**2])
@attr.attrs(auto_attrib=True, frozen=True)
class Circle:
    radius: float
    area: float

circle_from_radius = Circle(radius=2)
circle_from_area = Circle(area=42)
```
