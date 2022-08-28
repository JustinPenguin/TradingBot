import matplotlib.pyplot as plt
from scipy.interpolate import InterpolatedUnivariateSpline
import numpy as np


rng = np.random.default_rng()
x = (3,4,5,6)
y = (3,-2,3,5)
# y = np.exp(-x**2) + 0.1 * rng.standard_normal(7)
spl = InterpolatedUnivariateSpline(x, y)
plt.plot(x, y, 'ro', ms=5)
xs = np.linspace(3, 6, 1000)

print(spl.derivatives(3))

plt.plot(xs, spl(xs), 'g', lw=3, alpha=0.7)
plt.show()