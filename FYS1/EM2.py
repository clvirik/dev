import pygame
import math
import collections

# --- Configuration ---
WIDTH, HEIGHT = 800, 600
FPS = 60
PROPAGATION_SPEED = 5.0  # Speed of the field updates (c)
HISTORY_LIMIT = 600      # Enough to cover the screen corners
NUM_LINES = 40           # Number of radial field lines

# Colors
BG_COLOR = (5, 5, 15)
PARTICLE_COLOR = (255, 80, 80)
FIELD_LINE_COLOR = (70, 130, 230)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Electric Field: Retarded Potential Waves")
    clock = pygame.time.Clock()

    # Track particle history: deque of pygame.Vector2
    history = collections.deque(maxlen=HISTORY_LIMIT)
    
    # Pre-calculate angles for radial lines
    angles = [2 * math.pi * i / NUM_LINES for i in range(NUM_LINES)]

    running = True
    while running:
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        history.appendleft(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BG_COLOR)

        # Draw Radial Field Lines
        # For each radial direction, we sample points at different distances
        for angle in angles:
            points = []
            direction = pygame.Vector2(math.cos(angle), math.sin(angle))
            
            # We step outward from the particle's current position
            for dist in range(0, int(WIDTH * 1.2), 15):
                # Calculate how many frames ago the signal left the particle
                # to reach this distance: time = distance / speed
                delay = int(dist / PROPAGATION_SPEED)
                
                if delay < len(history):
                    # The "Retarded Position": where the particle was
                    origin = history[delay]
                    # The field point is the origin + (direction * distance)
                    point = origin + direction * dist
                    points.append(point)
            
            # Draw the continuous field line if we have enough points
            if len(points) > 1:
                pygame.draw.lines(screen, FIELD_LINE_COLOR, False, points, 1)

        # Draw the Particle (The Charge)
        pygame.draw.circle(screen, (255, 255, 255), mouse_pos, 12, 2) # Outer glow
        pygame.draw.circle(screen, PARTICLE_COLOR, mouse_pos, 8)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()