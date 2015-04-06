Matplotlib
==========

We save matplotlib figures in a local `images/` directory and then link to them
from the markdown file.

```python
>>> import matplotlib.pyplot as plt

>>> fig = plt.figure()
>>> plt.plot([1, 2, 3, 4, 5], [6, 7, 2, 4, 5])
>>> fig
```
