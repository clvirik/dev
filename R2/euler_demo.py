import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# Interval
x0 = 0
x_end = 20

# Differential equations
def f1(x, y):
    return -y

def f2(x, y):
    return np.sin(x)

# Exact solutions
def exact1(x):
    return np.exp(-x)

def exact2(x):
    return 1 - np.cos(x)

# Euler method
def euler(f, y0, h):
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

# Create figure with two subplots
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))
plt.subplots_adjust(bottom=0.25)

# Initial step size
h0 = 0.5

# Initial data
x1, y1 = euler(f1, 1, h0)
x2, y2 = euler(f2, 0, h0)

x_exact = np.linspace(x0, x_end, 400)

# Plot first equation
line1_euler, = ax1.plot(x1, y1, 'o-', label="Euler")
line1_exact, = ax1.plot(x_exact, exact1(x_exact), '--', label="Exact")
ax1.set_title("y' = -y ,  y(0)=1")
ax1.legend()
ax1.grid(True)

# Plot second equation
line2_euler, = ax2.plot(x2, y2, 'o-', label="Euler")
line2_exact, = ax2.plot(x_exact, exact2(x_exact), '--', label="Exact")
ax2.set_title("y' = sin(x) ,  y(0)=0")
ax2.legend()
ax2.grid(True)

# Slider
ax_slider = plt.axes([0.2, 0.1, 0.65, 0.03])
slider = Slider(ax_slider, "Step length h", 0.05, 1.0, valinit=h0)

# Update function
def update(val):
    h = slider.val
    
    x1, y1 = euler(f1, 1, h)
    x2, y2 = euler(f2, 0, h)
    
    line1_euler.set_xdata(x1)
    line1_euler.set_ydata(y1)
    
    line2_euler.set_xdata(x2)
    line2_euler.set_ydata(y2)
    
    fig.canvas.draw_idle()

slider.on_changed(update)

plt.show()
