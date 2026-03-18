import numpy as np
import pygame

# constants
hbar = 1.0
m = 1.0

# grid
N = 1024
L = 200
dx = L / N
x = np.linspace(-L/2, L/2, N)

# time step
dt = 0.05

# momentum grid
k = 2*np.pi*np.fft.fftfreq(N, d=dx)

# ----- Potential (two finite square barriers) -----

V = np.zeros(N)

barrier_width = 1
barrier_height = 30
B1 = -40
B2 = 30

V[(x > B1) & (x < B1 + barrier_width)] = barrier_height
V[(x > B2) & (x < B2 + barrier_width)] = barrier_height

# ----- Initial Gaussian wave packet -----

x0 = 0
sigma = 5
p0 = 7

psi = np.exp(-(x-x0)**2/(2*sigma**2)) * np.exp(1j*p0*x)

# normalize
psi /= np.sqrt(np.sum(np.abs(psi)**2)*dx)

# precompute operators
kinetic = np.exp(-1j*(hbar*k**2/(2*m))*dt)
potential_half = np.exp(-1j*V*dt/(2*hbar))

# ----- pygame setup -----
mask = np.ones(N)

edge = 10
for i in range(edge):
    damping = np.exp(-(edge-i)**2/100)
    mask[i] *= damping
    mask[-i-1] *= damping


pygame.init()
width = 1024
height = 400

screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

running = True

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # ----- Split-step evolution -----

    psi *= potential_half
    psi_k = np.fft.fft(psi)

    psi_k *= kinetic

    psi = np.fft.ifft(psi_k)
    psi *= potential_half
    
    
    prob = np.abs(psi)**2
    
    psi *= mask
    # ----- drawing -----

    screen.fill((20,20,30))

    scale_x = width / N
    scale_y = 3E3

    # draw probability density
    for i in range(N-1):

        y1 = height - prob[i]*scale_y
        y2 = height - prob[i+1]*scale_y
        if (x[i] < -40) or (x[i] > 30 + barrier_width):
            y1 = height - prob[i]*scale_y*20
        else:
            y1 = height - prob[i]*scale_y
        if (x[i+1] < -40) or (x[i+1] > 30 + barrier_width):    
            y2 = height - prob[i+1]*scale_y*20
        else:
            y2 = height - prob[i+1]*scale_y
        pygame.draw.line(
            screen,
            (0,200,255),
            (i*scale_x, y1),
            ((i+1)*scale_x, y2),
            2
        )

    # draw potential
    scale_x = width / L

    def sx(xval):
        return (xval + L/2) * scale_x

    base = height
    top  = height - barrier_height*5

    # x positions
    x0 = sx(-L/2)
    x1 = sx(B1)
    x2 = sx(B1 + barrier_width)
    x3 = sx(B2)
    x4 = sx(B2 + barrier_width)
    x5 = sx(L/2)

    c = (255,120,120)

    # 1 baseline
    pygame.draw.line(screen,c,(x0,base),(x1,base),2)

    # 2 up
    pygame.draw.line(screen,c,(x1,base),(x1,top),2)

    # 3 barrier top
    pygame.draw.line(screen,c,(x1,top),(x2,top),2)

    # 4 down
    pygame.draw.line(screen,c,(x2,top),(x2,base),2)

    # 5 middle baseline
    pygame.draw.line(screen,c,(x2,base),(x3,base),2)

    # 6 up
    pygame.draw.line(screen,c,(x3,base),(x3,top),2)

    # 7 barrier top
    pygame.draw.line(screen,c,(x3,top),(x4,top),2)

    # 8 down
    pygame.draw.line(screen,c,(x4,top),(x4,base),2)

    # 9 final baseline
    pygame.draw.line(screen,c,(x4,base),(x5,base),2)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()