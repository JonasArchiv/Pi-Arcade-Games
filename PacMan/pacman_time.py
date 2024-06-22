import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
small_screen_size = (800, 600)  # 8.5x15.5 cm screen
large_screen_size = (1920, 1080)  # 43 inch screen

# Set the size based on your choice
screen_size = large_screen_size  # Change to small_screen_size for the smaller screen

screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("Pac-Man")

# Colors
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)

# Pac-Man settings
pacman_size = 50
pacman_x = screen_size[0] // 2
pacman_y = screen_size[1] // 2
pacman_speed = 5

# Ghost settings
ghost_size = 50
ghost_speed = 2

# Initialize ghost positions
ghosts = [
    {"x": random.randint(0, screen_size[0] - ghost_size), "y": random.randint(0, screen_size[1] - ghost_size)}
    for _ in range(4)
]

# Joystick setup
pygame.joystick.init()
joystick = None
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Movement
    keys = pygame.key.get_pressed()
    if joystick:
        x_axis = joystick.get_axis(0)
        y_axis = joystick.get_axis(1)
        if x_axis < -0.1:
            pacman_x -= pacman_speed
        if x_axis > 0.1:
            pacman_x += pacman_speed
        if y_axis < -0.1:
            pacman_y -= pacman_speed
        if y_axis > 0.1:
            pacman_y += pacman_speed
    else:
        if keys[pygame.K_LEFT]:
            pacman_x -= pacman_speed
        if keys[pygame.K_RIGHT]:
            pacman_x += pacman_speed
        if keys[pygame.K_UP]:
            pacman_y -= pacman_speed
        if keys[pygame.K_DOWN]:
            pacman_y += pacman_speed

    # Screen wrapping
    if pacman_x < 0:
        pacman_x = screen_size[0]
    if pacman_x > screen_size[0]:
        pacman_x = 0
    if pacman_y < 0:
        pacman_y = screen_size[1]
    if pacman_y > screen_size[1]:
        pacman_y = 0

    # Ghost movement
    for ghost in ghosts:
        if ghost["x"] < pacman_x:
            ghost["x"] += ghost_speed
        elif ghost["x"] > pacman_x:
            ghost["x"] -= ghost_speed
        if ghost["y"] < pacman_y:
            ghost["y"] += ghost_speed
        elif ghost["y"] > pacman_y:
            ghost["y"] -= ghost_speed

    # Drawing
    screen.fill(BLACK)
    pygame.draw.circle(screen, YELLOW, (pacman_x, pacman_y), pacman_size // 2)
    for ghost in ghosts:
        pygame.draw.rect(screen, WHITE, (ghost["x"], ghost["y"], ghost_size, ghost_size))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
