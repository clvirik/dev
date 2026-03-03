import pygame
import random
import math

# --- Constants ---
WIDTH, HEIGHT = 1000, 650
FPS = 100

K = 1.71
ALPHA_CHARGE = 2
NUCLEUS_CHARGE = 79
ALPHA_MASS = 1

# Adjustable parameters
MIN_ENERGY, MAX_ENERGY = 1, 30
MIN_CORE, MAX_CORE = 2, 50
MIN_INF, MAX_INF = 20, 50

current_energy = 6
core_radius = 8
influence_radius = 50

# Slider layout
SLIDER_WIDTH = 600
SLIDER_HEIGHT = 8
HANDLE_RADIUS = 10
SLIDER_X = 200

ENERGY_Y = 560
CORE_Y = 600
INF_Y = 600

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rutherford")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 20)

# --- Nucleus grid (3 deep) ---
NUCLEI = []
GRID_ROWS = 6
GRID_COLUMNS = 4
SPACING_Y = 100
SPACING_X = 100

start_x = WIDTH // 2 - (GRID_COLUMNS // 2) * SPACING_X
start_y = HEIGHT // 2 - (GRID_ROWS // 2) * SPACING_Y

for col in range(GRID_COLUMNS):
    for row in range(GRID_ROWS):
        x = start_x + col * SPACING_X
        y = start_y + row * SPACING_Y
        NUCLEI.append((x, y))


class AlphaParticle:
    def __init__(self, energy):
        self.x = 0
        self.y = random.randint(100, HEIGHT - 150)
        self.speed = math.sqrt(2 * energy / ALPHA_MASS)
        self.vx = self.speed
        self.vy = 0
        self.alive = True

    def update(self):
        total_fx = 0
        total_fy = 0

        for nucleus in NUCLEI:
            dx = self.x - nucleus[0]
            dy = self.y - nucleus[1]
            r = math.sqrt(dx**2 + dy**2)

            if r < core_radius:
                continue

            if r > influence_radius:
                continue

            force = K * ALPHA_CHARGE * NUCLEUS_CHARGE / (r**2)
            total_fx += force * (dx / r)
            total_fy += force * (dy / r)

        ax = total_fx / ALPHA_MASS
        ay = total_fy / ALPHA_MASS

        self.vx += ax
        self.vy += ay
        self.x += self.vx
        self.y += self.vy

        if self.x > WIDTH or self.x < 0 or self.y < 0 or self.y > HEIGHT:
            self.alive = False

    def draw(self, surface):
        pygame.draw.circle(surface, (255, 255, 0),
                           (int(self.x), int(self.y)), 3)


def draw_slider(label, display_value, value, min_val, max_val, y):
    pygame.draw.rect(screen, (180, 180, 180),
                     (SLIDER_X, y, SLIDER_WIDTH, SLIDER_HEIGHT))

    ratio = (value - min_val) / (max_val - min_val)
    handle_x = SLIDER_X + ratio * SLIDER_WIDTH

    pygame.draw.circle(screen, (0, 200, 255),
                       (int(handle_x), y + SLIDER_HEIGHT // 2),
                       HANDLE_RADIUS)

    text = font.render(f"{label}: {display_value:.2f}", True, (255, 255, 255))
    screen.blit(text, (SLIDER_X, y - 25))

    return handle_x


particles = []
spawn_timer = 0
dragging = None
paused = False

running = True
while running:
    clock.tick(FPS)
    screen.fill((0, 0, 0))

    # Draw nuclei
    for nucleus in NUCLEI:
        pygame.draw.circle(screen, (255, 0, 0), nucleus, int(core_radius))
        #pygame.draw.circle(screen, (0, 255, 0), nucleus, int(influence_radius), 1)

    if not paused:
        spawn_timer += 1
        if spawn_timer > 5:
            particles.append(AlphaParticle(current_energy))
            spawn_timer = 0

        for p in particles[:]:
            p.update()
            p.draw(screen)
            if not p.alive:
                particles.remove(p)
    else:
        for p in particles:
            p.draw(screen)

    # Draw sliders
    energy_handle = draw_slider("Energi [eV]", current_energy,current_energy,
                                 MIN_ENERGY, MAX_ENERGY, ENERGY_Y)
    core_handle = draw_slider("Kjerneradius [pm]", core_radius*2.90, core_radius,
                               MIN_CORE, MAX_CORE, CORE_Y)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
            if event.key == pygame.K_r:
                particles.clear()

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            if abs(mx - energy_handle) < HANDLE_RADIUS and abs(my - ENERGY_Y) < 20:
                dragging = "energy"
            elif abs(mx - core_handle) < HANDLE_RADIUS and abs(my - CORE_Y) < 20:
                dragging = "core"

        if event.type == pygame.MOUSEBUTTONUP:
            dragging = None

        if event.type == pygame.MOUSEMOTION and dragging:
            mx, _ = pygame.mouse.get_pos()
            mx = max(SLIDER_X, min(mx, SLIDER_X + SLIDER_WIDTH))
            ratio = (mx - SLIDER_X) / SLIDER_WIDTH

            if dragging == "energy":
                current_energy = MIN_ENERGY + ratio * (MAX_ENERGY - MIN_ENERGY)
            elif dragging == "core":
                core_radius = MIN_CORE + ratio * (MAX_CORE - MIN_CORE)
            elif dragging == "inf":
                influence_radius = MIN_INF + ratio * (MAX_INF - MIN_INF)

    pygame.display.flip()

pygame.quit()