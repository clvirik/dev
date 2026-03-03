import numpy as np

def f(x,y):
    return np.arctan(np.exp(x*y)/(x**2+y**2))

x0 = 0
y0 = 0.1
x_slutt = 10
h = 0.0001

x = x0
y = y0

x_values = [x0]
y_values = [y0]

while x <= x_slutt:
    y = y + h * f(x, y)
    x = x + h
    #print(x, y)
    x_values.append(x)
    y_values.append(y)


import matplotlib.pyplot as plt
import numpy as np
def y(x):
    return 2*np.exp(x) - x - 1

X = np.linspace(0,2,100)
#plt.plot(X, y(X), "--")
plt.plot(x_values , y_values)
plt.xlabel("x")
plt.ylabel("y")
plt.title("Eulers metode")
plt.show()