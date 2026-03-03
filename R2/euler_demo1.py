import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# Differential equation
def f(x, y):
    return -y

# Exact solution
def exact(x):
    return np.exp(-x)

# Initial conditions
x0 = 0
y0 = 1
x_end = 5

# Create figure
fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.25)

# Initial step length
h0 = 0.5

def euler(h):
    n = int((x_end - x0) / h)
    x = x0
    y = y0
    x_values = [x]
    y_values = [y]
    
    for _ in range(n):
        y = y + h * f(x, y)
        x = x + h
        x_values.append(x)
        y_values.append(y)
        
    return np.array(x_values), np.array(y_values)

# Initial plot
x_euler, y_euler = euler(h0)
x_exact = np.linspace(x0, x_end, 400)

line_euler, = ax.plot(x_euler, y_euler, 'o-', label="Eulers meetode")
line_exact, = ax.plot(x_exact, exact(x_exact), '--', label="Eksakt løsning")

ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_title("Eulers metode")
ax.legend()
ax.grid(True)

# Slider setup
ax_slider = plt.axes([0.2, 0.1, 0.65, 0.03])
slider = Slider(ax_slider, "dx", 0.01, 1.0, valinit=h0)

# Update function
def update(val):
    h = slider.val
    x_euler, y_euler = euler(h)
    line_euler.set_xdata(x_euler)
    line_euler.set_ydata(y_euler)
    fig.canvas.draw_idle()

slider.on_changed(update)

plt.show()
