x0 = 1
v0 = 0
alpha = 0
beta = 1

t0 = 0
t_slutt = 40
dt = 0.001
antall_steg = int((t_slutt - t0)/dt)

def f(x, v):
    return -alpha*v - beta*x

import matplotlib.pyplot as plt

x_values = [x0]
v_values = [v0]
t_values = [t0]

x = x0
v = v0
t = t0

for i in range(antall_steg):
    x = x + v * dt
    v = v + f(x, v) * dt
    t = t + dt
    
    x_values.append(x)
    v_values.append(v)
    t_values.append(t)

import numpy as np

def X(t):
    D = alpha**2 - 4*beta

    # Underdempet (komplekse røtter)
    if D < 0:
        omega = np.sqrt(4*beta - alpha**2) / 2
        C1 = x0
        C2 = (v0 + (alpha/2)*x0) / omega
        return np.exp(-alpha*t/2) * (
            C1*np.cos(omega*t) + C2*np.sin(omega*t)
        )

    # Kritisk dempet (dobbel rot)
    elif D == 0:
        r = -alpha/2
        C1 = x0
        C2 = v0 - r*x0
        return (C1 + C2*t) * np.exp(r*t)

    # Overdempet (to reelle røtter)
    else:
        r1 = (-alpha + np.sqrt(D)) / 2
        r2 = (-alpha - np.sqrt(D)) / 2
        
        C2 = (v0 - r1*x0) / (r2 - r1)
        C1 = x0 - C2
        
        return C1*np.exp(r1*t) + C2*np.exp(r2*t)

T = np.linspace(t0, t_slutt, 10000)

plt.plot(T, X(T), "--")
plt.plot(t_values, x_values)
x_values = [x0]
v_values = [v0]
t_values = [t0]

x = x0
v = v0
t = t0

for i in range(antall_steg):
    b = x
    
    x = x + v * dt
    v = v + f(b, v) * dt
    t = t + dt
    
    x_values.append(x)
    v_values.append(v)
    t_values.append(t)
plt.plot(t_values, x_values)
x_values = [x0]
v_values = [v0]
t_values = [t0]

x = x0
v = v0
t = t0

for i in range(antall_steg):
    v = v + f(x, v) * dt
    x = x + v * dt
    t = t + dt
    
    x_values.append(x)
    v_values.append(v)
    t_values.append(t)
#plt.plot(t_values, x_values, label="EC")
plt.legend()
plt.xlabel("Tid")
plt.ylabel("Posisjon")
plt.title("Dempede svingninger med Eulers metode")
plt.grid()
plt.show()