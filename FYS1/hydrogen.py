import pygame
import math

# Initialization
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Electron Orbit with Radiation Damping")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PROTON_COLOR = (255, 50, 50)
ELECTRON_COLOR = (50, 150, 255)
TRAIL_COLOR = (100, 100, 100)

# Constants & Physics Variables
K = 5000  # Electrostatic constant (scaled for visual)
damping_factor = 1
damping_active = False

class Particle:
    def __init__(self, x, y, mass, color):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, 0)
        self.mass = mass
        self.color = color
        self.trail = []

    def draw(self):
        if len(self.trail) > 2:
            pygame.draw.lines(screen, TRAIL_COLOR, False, self.trail, 1)
        pygame.draw.circle(screen, self.color, (int(self.pos.x), int(self.pos.y)), 6)

# Setup objects
proton = Particle(WIDTH // 2, HEIGHT // 2, 100, PROTON_COLOR)
electron = Particle(WIDTH // 2 + 150, HEIGHT // 2, 1, ELECTRON_COLOR)
electron.vel = pygame.Vector2(0, -5.8) # Initial orbital velocity

running = True
while running:
    screen.fill(BLACK)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                damping_active = not damping_active
            if event.key == pygame.K_r: # Reset simulation
                electron.pos = pygame.Vector2(WIDTH // 2 + 150, HEIGHT // 2)
                electron.vel = pygame.Vector2(0, -5.8)
                electron.trail = []

    # Calculate Force (Coulomb's Law)
    direction = proton.pos - electron.pos
    distance = direction.length()
    
    if distance > 5: # Prevent division by zero/extreme forces
        force_mag = K / (distance**2)
        acceleration = direction.normalize() * force_mag
        
        # Apply Acceleration
        electron.vel += acceleration
        
        # Radiation Damping (Larmor-inspired)
        if damping_active:
            # In a real atom, the electron would spiral in almost instantly.
            # We scale the damping to the square of acceleration.
            loss = acceleration.length()**2 * damping_factor
            electron.vel *= (1 - (loss / 100))

    # Update Position
    electron.pos += electron.vel
    
    # Update Trail
    electron.trail.append((electron.pos.x, electron.pos.y))
    if len(electron.trail) > 500:
        electron.trail.pop(0)

    # Draw everything
    proton.draw()
    electron.draw()

    # UI Instructions
    font = pygame.font.SysFont(None, 24)
    status = "ON" if damping_active else "OFF"
    img = font.render(f"Damping (D): {status} | Reset (R)", True, WHITE)
    screen.blit(img, (20, 20))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()