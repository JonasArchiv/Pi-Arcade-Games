import pygame
import random
import os
import time

# Constants
small_screen_size = (800, 600)
large_screen_size = (1920, 1080)
screen_size = large_screen_size

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("Pac-Man")

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

# Game variables
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# Maze layout (larger map)
maze = [
    "#########################################",
    "#.......................................#",
    "#.###.###..###.###..###.###..###.###.###.#",
    "#.#...#......#...#......#...#......#...#.#",
    "#.#.###.####.###.#.####.###.####.###.#.#.#",
    "#.#.............................#......#.#",
    "#.###.#.#.##.#.#.###.#.#.##.#.#.##.#.#.#.#",
    "#.....#.#......#.....#.#......#.....#.#.#.#",
    "#####.#.#####.#.#####.#.#####.#.#####.#.#.",
    "#.....#...#...#...#...#...#...#...#...#.#.",
    "#.###.###.#.###.#.###.#.###.#.###.#.###.#.",
    "#.#...................................#.#",
    "#.###.#.#.##.#.#.###.#.#.##.#.#.##.#.#.#.#",
    "#.....#.#......#.....#.#......#.....#.#.#.#",
    "#####.#.#####.#.#####.#.#####.#.#####.#.#.",
    "#...............#...............#........#",
    "#########################################"
]

# Game variables
player_pos = (1, 1)  # Player starting position
ghosts = [(14, 7), (14, 13)]  # Initial ghost positions
ghost_directions = [None, None]  # Directions for each ghost
joystick_enabled = False  # Flag to check if joystick is enabled
lives = 3
game_over = False
start_time = 0
elapsed_time = 0
top_scores_file = "top_scores.txt"
top_scores = []


# Load top scores from file
def load_top_scores():
    global top_scores
    if os.path.exists(top_scores_file):
        with open(top_scores_file, 'r') as f:
            top_scores = [float(score.strip()) for score in f.readlines()]


# Save top scores to file
def save_top_scores():
    global top_scores
    with open(top_scores_file, 'w') as f:
        for score in top_scores:
            f.write(f"{score}\n")


# Initialize game
def initialize_game():
    global player_pos, ghosts, ghost_directions, lives, game_over, start_time, elapsed_time
    player_pos = (1, 1)
    ghosts = [(14, 7), (14, 13)]
    ghost_directions = [None, None]
    lives = 3
    game_over = False
    start_time = 0
    elapsed_time = 0


# Check if position is a valid move (within maze and not wall)
def is_valid_move(pos):
    x, y = pos
    if 0 <= x < len(maze[0]) and 0 <= y < len(maze):
        return maze[y][x] != '#'
    return False


# Calculate distance between two points (Manhattan distance)
def distance(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


# Find shortest path for ghost to player using BFS algorithm
def find_shortest_path(ghost_pos, player_pos):
    queue = [(ghost_pos, [])]
    visited = set()
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    while queue:
        current, path = queue.pop(0)
        if current == player_pos:
            return path
        if current in visited:
            continue
        visited.add(current)
        for direction in directions:
            next_pos = (current[0] + direction[0], current[1] + direction[1])
            if is_valid_move(next_pos) and next_pos not in visited:
                queue.append((next_pos, path + [direction]))

    return []  # No path found


# Move player function
def move_player(direction):
    global player_pos
    x, y = player_pos
    if direction == 'UP' and is_valid_move((x, y - 1)):
        player_pos = (x, y - 1)
    elif direction == 'DOWN' and is_valid_move((x, y + 1)):
        player_pos = (x, y + 1)
    elif direction == 'LEFT' and is_valid_move((x - 1, y)):
        player_pos = (x - 1, y)
    elif direction == 'RIGHT' and is_valid_move((x + 1, y)):
        player_pos = (x + 1, y)


# Main game loop
def main_game_loop():
    global player_pos, lives, game_over, start_time, elapsed_time, top_scores, ghost_directions, joystick_enabled

    restart_button_rect = pygame.Rect(screen_size[0] // 2 - 75, screen_size[1] - 150, 150, 50)
    restart_text = font.render("Restart", True, WHITE)

    exit_button_rect = pygame.Rect(screen_size[0] // 2 - 75, screen_size[1] - 80, 150, 50)
    exit_text = font.render("Exit", True, WHITE)

    running = True
    while running:
        screen.fill(BLACK)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if restart_button_rect.collidepoint(mouse_pos):
                    initialize_game()
                elif exit_button_rect.collidepoint(mouse_pos):
                    running = False

        # Handle player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            move_player('UP')
        elif keys[pygame.K_DOWN]:
            move_player('DOWN')
        elif keys[pygame.K_LEFT]:
            move_player('LEFT')
        elif keys[pygame.K_RIGHT]:
            move_player('RIGHT')

        # Handle joystick movement
        if joystick_enabled:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
            axis_horizontal = joystick.get_axis(0)
            axis_vertical = joystick.get_axis(1)
            if axis_horizontal > 0.5:
                move_player('RIGHT')
            elif axis_horizontal < -0.5:
                move_player('LEFT')
            if axis_vertical > 0.5:
                move_player('DOWN')
            elif axis_vertical < -0.5:
                move_player('UP')

        if not game_over:
            # Update ghosts (move towards player using shortest path or random movement)
            for i, ghost in enumerate(ghosts):
                if random.randint(1, 10) <= 8:  # 80% chance to move towards player
                    path = find_shortest_path(ghost, player_pos)
                    if path:
                        dx, dy = path[0]
                        if is_valid_move((ghost[0] + dx, ghost[1] + dy)):
                            ghosts[i] = (ghost[0] + dx, ghost[1] + dy)
                            ghost_directions[i] = (dx, dy)
                else:
                    dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
                    if is_valid_move((ghost[0] + dx, ghost[1] + dy)):
                        ghosts[i] = (ghost[0] + dx, ghost[1] + dy)
                        ghost_directions[i] = (dx, dy)

            # Check if player collides with ghosts
            for ghost in ghosts:
                if player_pos == ghost:
                    lives -= 1
                    # If the player collides with a ghost, move player to a valid starting position
                    possible_start_positions = [(1, 1), (1, 16), (15, 1), (15, 16)]
                    new_player_pos = random.choice(possible_start_positions)
                    while not is_valid_move(new_player_pos):
                        new_player_pos = random.choice(possible_start_positions)
                    player_pos = new_player_pos
                    break  # Stop checking further collisions

            # Render maze
            for y, line in enumerate(maze):
                for x, char in enumerate(line):
                    color = WHITE if char == '.' else BLUE if char == '#' else BLACK
                    pygame.draw.rect(screen, color, (x * 40 + 100, y * 40 + 100, 40, 40))

            # Render player
            pygame.draw.circle(screen, YELLOW, (player_pos[0] * 40 + 120, player_pos[1] * 40 + 120), 15)

            # Render ghosts
            for i, ghost in enumerate(ghosts):
                pygame.draw.circle(screen, BLUE, (ghost[0] * 40 + 120, ghost[1] * 40 + 120), 15)

            # Render restart button
            pygame.draw.rect(screen, BLUE, restart_button_rect)
            screen.blit(restart_text, (restart_button_rect.centerx - restart_text.get_width() // 2,
                                       restart_button_rect.centery - restart_text.get_height() // 2))

            # Render exit button
            pygame.draw.rect(screen, BLUE, exit_button_rect)
            screen.blit(exit_text, (exit_button_rect.centerx - exit_text.get_width() // 2,
                                    exit_button_rect.centery - exit_text.get_height() // 2))

            # Update timer and display elapsed time
            if start_time == 0:
                start_time = time.time()
            current_time = time.time()
            elapsed_time = current_time - start_time
            time_text = font.render(f"Time: {int(elapsed_time)}", True, WHITE)
            screen.blit(time_text, (10, 10))

            # Display lives remaining
            lives_text = font.render(f"Lives: {lives}", True, WHITE)
            screen.blit(lives_text, (10, 50))

            # Check game over condition
            if lives <= 0:
                game_over = True
                # Add current score to top scores
                top_scores.append(elapsed_time)
                # Sort scores and keep top 5
                top_scores.sort(reverse=True)
                top_scores = top_scores[:5]
                # Save scores to file
                save_top_scores()

        else:
            # Game over screen
            screen.fill(BLACK)
            game_over_text = font.render("GAME OVER", True, WHITE)
            screen.blit(game_over_text, (screen_size[0] // 2 - 100, screen_size[1] // 2 - 50))
            time_text = font.render(f"Time: {int(elapsed_time)} seconds", True, WHITE)
            screen.blit(time_text, (screen_size[0] // 2 - 100, screen_size[1] // 2))
            scores_text = font.render("Top 5 Scores:", True, WHITE)
            screen.blit(scores_text, (screen_size[0] // 2 - 100, screen_size[1] // 2 + 50))
            for i, score in enumerate(top_scores):
                score_text = font.render(f"{i + 1}. {int(score)} seconds", True, WHITE)
                screen.blit(score_text, (screen_size[0] // 2 - 100, screen_size[1] // 2 + 100 + i * 40))

            # Render restart button
            pygame.draw.rect(screen, BLUE, restart_button_rect)
            screen.blit(restart_text, (restart_button_rect.centerx - restart_text.get_width() // 2,
                                       restart_button_rect.centery - restart_text.get_height() // 2))

            # Render exit button
            pygame.draw.rect(screen, BLUE, exit_button_rect)
            screen.blit(exit_text, (exit_button_rect.centerx - exit_text.get_width() // 2,
                                    exit_button_rect.centery - exit_text.get_height() // 2))

        pygame.display.flip()
        clock.tick(10)


# Load top scores at the beginning of the game
load_top_scores()

# Start the game loop
initialize_game()
main_game_loop()

pygame.quit()
