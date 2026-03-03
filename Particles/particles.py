import pygame
import numpy as np
import heapq
import math
import random

# ----------------------------
# Constants
# ----------------------------
WIDTH, HEIGHT = 1000, 600
PANEL_WIDTH = 250
WORLD_WIDTH, WORLD_HEIGHT = 10.0, 7.5
SCALE = (WIDTH - PANEL_WIDTH) / WORLD_WIDTH

G = 1#9.81
EPS = 1e-10

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Event-Driven Gravity Collision Simulator")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 22)

# ----------------------------
# Particle
# ----------------------------
class Particle:
    def __init__(self, x, y, vx, vy, r, m, color):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.r = r
        self.m = m
        self.color = color
        self.count = 0

    def advance(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt - 0.5 * G * dt * dt
        self.vy -= G * dt


# ----------------------------
# Event
# ----------------------------
class Event:
    def __init__(self, t, a, b, countA, countB, wall=None):
        self.t = t
        self.a = a
        self.b = b
        self.wall = wall
        self.countA = countA
        self.countB = countB

    def __lt__(self, other):
        return self.t < other.t

    def valid(self):
        if self.a and self.a.count != self.countA:
            return False
        if self.b and self.b.count != self.countB:
            return False
        return True


# ----------------------------
# Collision Timing
# ----------------------------
def time_to_wall(p):
    times = []

    if p.vx > 0:
        t = (WORLD_WIDTH - p.r - p.x) / p.vx
        if t > EPS:
            times.append(("right", t))
    if p.vx < 0:
        t = (p.r - p.x) / p.vx
        if t > EPS:
            times.append(("left", t))

    a = -0.5 * G
    b = p.vy

    # bottom
    c = p.y - p.r
    roots = np.roots([a, b, c])
    for r in roots:
        if np.isreal(r):
            r = np.real(r)
            if r > EPS:
                times.append(("bottom", r))

    # top
    c = p.y - (WORLD_HEIGHT - p.r)
    roots = np.roots([a, b, c])
    for r in roots:
        if np.isreal(r):
            r = np.real(r)
            if r > EPS:
                times.append(("top", r))

    if not times:
        return None
    return min(times, key=lambda x: x[1])


def time_to_hit(p1, p2):
    dx = p1.x - p2.x
    dy = p1.y - p2.y
    dvx = p1.vx - p2.vx
    dvy = p1.vy - p2.vy
    r = p1.r + p2.r

    a = dvx*dvx + dvy*dvy
    b = 2*(dx*dvx + dy*dvy)
    c = dx*dx + dy*dy - r*r

    roots = np.roots([a, b, c])
    real = [np.real(r) for r in roots if np.isreal(r) and np.real(r) > EPS]
    if not real:
        return None
    return min(real)


# ----------------------------
# Collision Resolution
# ----------------------------
def resolve_particle(p1, p2):
    dx = p1.x - p2.x
    dy = p1.y - p2.y
    dist = math.hypot(dx, dy)
    nx, ny = dx/dist, dy/dist

    v1n = p1.vx*nx + p1.vy*ny
    v2n = p2.vx*nx + p2.vy*ny

    m1, m2 = p1.m, p2.m

    v1n_new = (v1n*(m1-m2) + 2*m2*v2n)/(m1+m2)
    v2n_new = (v2n*(m2-m1) + 2*m1*v1n)/(m1+m2)

    p1.vx += (v1n_new - v1n)*nx
    p1.vy += (v1n_new - v1n)*ny
    p2.vx += (v2n_new - v2n)*nx
    p2.vy += (v2n_new - v2n)*ny


def resolve_wall(p, wall):
    if wall in ("left", "right"):
        p.vx *= -1
    else:
        p.vy *= -1


# ----------------------------
# Scheduler
# ----------------------------
particles = []
pq = []
sim_time = 0


def predict(p):
    # Wall
    res = time_to_wall(p)
    if res:
        wall, dt = res
        heapq.heappush(pq, Event(sim_time+dt, p, None, p.count, -1, wall))

    # Particle
    for other in particles:
        if other is not p:
            dt = time_to_hit(p, other)
            if dt:
                heapq.heappush(
                    pq,
                    Event(sim_time+dt, p, other, p.count, other.count)
                )


def add_particle(p):
    particles.append(p)
    predict(p)
    for other in particles:
        if other is not p:
            predict(other)


# ----------------------------
# UI State
# ----------------------------
selected_radius = 0.3
selected_mass = 1.0
drag_start = None


# ----------------------------
# Main Loop
# ----------------------------
running = True
while running:
    dt_real = clock.tick(60)/1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Keyboard controls
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                selected_radius += 0.05
            if event.key == pygame.K_DOWN:
                selected_radius = max(0.05, selected_radius - 0.05)
            if event.key == pygame.K_RIGHT:
                selected_mass += 0.2
            if event.key == pygame.K_LEFT:
                selected_mass = max(0.1, selected_mass - 0.2)

        # Mouse
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            if mx < WIDTH - PANEL_WIDTH:
                drag_start = (mx, my)

        if event.type == pygame.MOUSEBUTTONUP:
            if drag_start:
                mx, my = pygame.mouse.get_pos()
                x = drag_start[0] / SCALE
                y = (HEIGHT - drag_start[1]) / SCALE
                vx = (mx - drag_start[0]) * 0.02
                vy = -(my - drag_start[1]) * 0.02

                p = Particle(
                    x, y, vx, vy,
                    selected_radius,
                    selected_mass,
                    (255,0,0)
                )
                add_particle(p)
                drag_start = None

    # Process events
    while pq and pq[0].t <= sim_time + dt_real:
        event = heapq.heappop(pq)
        if not event.valid():
            continue

        dt = event.t - sim_time
        for p in particles:
            p.advance(dt)
        sim_time = event.t

        if event.b:
            resolve_particle(event.a, event.b)
            event.a.count += 1
            event.b.count += 1
            predict(event.a)
            predict(event.b)
        else:
            resolve_wall(event.a, event.wall)
            event.a.count += 1
            predict(event.a)

    # Advance remainder
    remaining = dt_real
    for p in particles:
        p.advance(remaining)
    sim_time += remaining

    # ---------------- Drawing ----------------
    screen.fill((25,25,30))

    # Draw world boundary
    pygame.draw.rect(screen, (60,60,60),
                     (0,0,WIDTH-PANEL_WIDTH,HEIGHT), 2)

    # Draw particles
    for p in particles:
        px = int(p.x*SCALE)
        py = int(HEIGHT - p.y*SCALE)
        pygame.draw.circle(screen, p.color,
                           (px,py), int(p.r*SCALE))

    # Draw control panel
    panel_x = WIDTH - PANEL_WIDTH
    pygame.draw.rect(screen, (40,40,50),
                     (panel_x,0,PANEL_WIDTH,HEIGHT))

    lines = [
        "Controls:",
        "Drag mouse to add particle",
        "",
        "Arrow Up/Down: Radius",
        "Arrow Left/Right: Mass",
        "",
        f"Radius: {selected_radius:.2f}",
        f"Mass:   {selected_mass:.2f}",
        "",
        f"Particles: {len(particles)}"
    ]

    y_offset = 20
    for line in lines:
        text = font.render(line, True, (220,220,220))
        screen.blit(text, (panel_x+15, y_offset))
        y_offset += 25

    pygame.display.flip()

pygame.quit()