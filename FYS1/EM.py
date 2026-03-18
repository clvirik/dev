import pygame
import math
import collections
import numpy as np

# --- Configuration ---
WIDTH, HEIGHT = 800, 600
FPS = 60
FIELD_SPACING = 20  # Distance between field arrows
PROPAGATION_SPEED = 5.0 # Speed of the "field waves"
HISTORY_LIMIT = 500 # How many past positions to remember

# Colors
BG_COLOR = (10, 10, 20)
PARTICLE_COLOR = (255, 50, 50)
ARROW_COLOR = (100, 150, 255)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Electric Field Propagation Waves")
    clock = pygame.time.Clock()

    # Track particle history: deque of (x, y) coordinates
    history = collections.deque(maxlen=HISTORY_LIMIT)
    
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        history.appendleft(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BG_COLOR)

        # Draw Field Grid
        for x in range(0, WIDTH, FIELD_SPACING):
            for y in range(0, HEIGHT, FIELD_SPACING):
                grid_pos = pygame.Vector2(x, y)
                
                # 1. Find the "Retarded Time" position
                # We look back in history to find where the particle was 
                # when the 'signal' left it to reach this grid point.
                
                delayed_pos = history[0] # Default to current
                for i, past_pos in enumerate(history):
                    dist = grid_pos.distance_to(pygame.Vector2(past_pos))
                    # If the time it took to travel (dist/speed) matches the history index
                    if i >= dist / PROPAGATION_SPEED:
                        delayed_pos = past_pos
                        break
                
                # 2. Calculate direction from the delayed position
                target_vec = grid_pos - pygame.Vector2(delayed_pos)
                dist = target_vec.length()
                
                if dist > 0:
                    target_vec.normalize_ip()
                    # Scale arrow length slightly by distance or keep constant for clarity
                    arrow_end = grid_pos + target_vec * 8*np.exp(-dist/200)
                    
                    # Draw the field line (arrow)
                    pygame.draw.line(screen, ARROW_COLOR, grid_pos, arrow_end, 2)

        # Draw the Particle
        pygame.draw.circle(screen, PARTICLE_COLOR, mouse_pos, 10)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()