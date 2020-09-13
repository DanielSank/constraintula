# constraintula

```python
import attr
import constraintula
import numpy as np

PI = np.pi

area, radius = constraintula.symbols('area radius')


@constraintula.constrain([area - PI * radius**2])
@attr.dataclass(frozen=True)
class Circle:
    radius: float
    area: float

circle_from_radius = Circle(radius=2)
circle_from_area = Circle(area=42)
```

## Installation

### User
```
pip install constraintula
```

### Developer
```
pip install -e .[dev]
```

## Disclaimer

This is not an officially supported Google product.
