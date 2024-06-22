import pygame
import random
import time

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
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Pac-Man settings
pacman_size = 50
pacman_speed = 5

# Ghost settings
ghost_size = 50
ghost_speed = 2

# Lives settings
initial_lives = 3
lives = initial_lives

# Font settings
font = pygame.font.Font(None, 36)

# Time tracking
start_time = time.time()
times = []
attempts = []

# File for saving times
times_file = "times.txt"

def reset_positions():
    global pacman_x, pacman_y, ghosts, start_time
    pacman_x = screen_size[0] // 2
    pacman_y = screen_size[1] // 2
    ghosts = [
        {"x": random.randint(0, screen_size[0] - ghost_size), "y": random.randint(0, screen_size[1] - ghost_size)}
        for _ in range(4)
    ]
    start_time = time.time()

def load_times():
    try:
        with open(times_file, "r") as file:
            times = [float(line.strip()) for line in file.readlines()]
            times.sort()
            return times
    except FileNotFoundError:
        return []

def save_time(new_time):
    times.append(new_time)
    times.sort()
    with open(times_file, "w") as file:
        for t in times[:3]:
            file.write(f"{t}\n")

def draw_button(text, position, size, color, hover_color, click):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if position[0] < mouse[0] < position[0] + size[0] and position[1] < mouse[1] < position[1] + size[1]:
        pygame.draw.rect(screen, hover_color, (*position, *size))
        if click[0] == 1:
            return True
    else:
        pygame.draw.rect(screen, color, (*position, *size))

    text_surface = font.render(text, True, BLACK)
    text_rect = text_surface.get_rect(center=(position[0] + size[0] // 2, position[1] + size[1] // 2))
    screen.blit(text_surface, text_rect)
    return False

reset_positions()
times = load_times()

# Joystick setup
pygame.joystick.init()
joystick = None
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

# Function to check for collisions between ghosts
def is_collision(x1, y1, x2, y2, size):
    return abs(x1 - x2) < size and abs(y1 - y2) < size

# Main game loop
running = True
game_over = False
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not game_over:
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

        # Prevent Pac-Man from going off-screen
        pacman_x = max(0, min(pacman_x, screen_size[0] - pacman_size))
        pacman_y = max(0, min(pacman_y, screen_size[1] - pacman_size))

        # Ghost movement with collision avoidance
        for ghost in ghosts:
            potential_positions = [
                (ghost["x"] + ghost_speed, ghost["y"]),  # Right
                (ghost["x"] - ghost_speed, ghost["y"]),  # Left
                (ghost["x"], ghost["y"] + ghost_speed),  # Down
                (ghost["x"], ghost["y"] - ghost_speed)   # Up
            ]

            # Prioritize moving towards Pac-Man
            potential_positions.sort(key=lambda pos: (abs(pos[0] - pacman_x) + abs(pos[1] - pacman_y)))

            moved = False
            for pos in potential_positions:
                collision = False
                for other_ghost in ghosts:
                    if other_ghost != ghost and is_collision(pos[0], pos[1], other_ghost["x"], other_ghost["y"], ghost_size):
                        collision = True
                        break
                if not collision:
                    ghost["x"], ghost["y"] = pos
                    moved = True
                    break

            if not moved:
                # Attempt to move to random position if stuck
                for _ in range(10):  # try up to 10 random moves
                    random_pos = (ghost["x"] + random.choice([-ghost_speed, ghost_speed]),
                                  ghost["y"] + random.choice([-ghost_speed, ghost_speed]))
                    collision = False
                    for other_ghost in ghosts:
                        if other_ghost != ghost and is_collision(random_pos[0], random_pos[1], other_ghost["x"], other_ghost["y"], ghost_size):
                            collision = True
                            break
                    if not collision:
                        ghost["x"], ghost["y"] = random_pos
                        break

        # Prevent ghosts from going off-screen
        for ghost in ghosts:
            ghost["x"] = max(0, min(ghost["x"], screen_size[0] - ghost_size))
            ghost["y"] = max(0, min(ghost["y"], screen_size[1] - ghost_size))

        # Check for collisions between Pac-Man and ghosts
        for ghost in ghosts:
            if is_collision(pacman_x, pacman_y, ghost["x"], ghost["y"], pacman_size):
                lives -= 1
                end_time = time.time()
                survival_time = round(end_time - start_time, 2)
                attempts.append(survival_time)
                if lives > 0:
                    reset_positions()
                else:
                    save_time(survival_time)
                    game_over = True
                break

        # Drawing
        screen.fill(BLACK)
        pygame.draw.circle(screen, YELLOW, (pacman_x, pacman_y), pacman_size // 2)
        for ghost in ghosts:
            pygame.draw.rect(screen, WHITE, (ghost["x"], ghost["y"], ghost_size, ghost_size))

        # Draw lives
        lives_text = font.render(f"Lives: {lives}", True, RED)
        screen.blit(lives_text, (screen_size[0] - 150, 10))

        # Draw survival time
        current_time = round(time.time() - start_time, 2)
        time_text = font.render(f"Time: {current_time}", True, RED)
        screen.blit(time_text, (10, 10))
    else:
        # Game Over screen
        screen.fill(BLACK)
        game_over_text = font.render("Game Over", True, RED)
        screen.blit(game_over_text, (screen_size[0] // 2 - 100, screen_size[1] // 2 - 100))

        # Displaying attempts and global times
        for i, t in enumerate(attempts):
            attempt_time_text = font.render(f"Your {i + 1} Time: {t}", True, WHITE)
            screen.blit(attempt_time_text, (screen_size[0] // 4 - 100, screen_size[1] // 2 + i * 30))

        best_times = load_times()[:3]
        for i, t in enumerate(best_times):
            best_time_text = font.render(f"Global Place {i + 1}: {t}", True, WHITE)
            screen.blit(best_time_text, (3 * screen_size[0] // 4 - 100, screen_size[1] // 2 + i * 30))

        # Draw Restart button
        if draw_button("Restart", (screen_size[0] // 2 - 75, screen_size[1] // 2 + 150), (150, 50), GREEN, WHITE, pygame.mouse.get_pressed()):
            game_over = False
            lives = initial_lives
            attempts = []
            reset_positions()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
