import pygame
import random
import os
import time

# Constants
small_screen_size = (800, 600)
large_screen_size = (1920, 1080)
screen_size = large_screen_size  # Adjust as needed

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

# Maze layout
maze = [
    "####################",
    "#..................#",
    "#.###.###..###.###.#",
    "#.#...#......#...#.#",
    "#.#.###.####.###.#.#",
    "#.#..............#.#",
    "#.###.#.#.##.#.#.#.#",
    "#.....#.#........#.#",
    "#####.#.#####.#.#.#.",
    "#.....#...#...#.#.#.",
    "#.###.###.#.###.#.#.",
    "#.#..............#.#",
    "#.###.#.#.##.#.#.#.#",
    "#.....#.#........#.#",
    "#####.#.#####.#.#.#.",
    "#...............#.#.",
    "###################"
]

# Game variables
player_pos = (1, 1)  # Player starting position
ghosts = [(14, 7), (14, 13)]  # Initial ghost positions
direction = None  # Player's current direction
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
            top_scores = [int(score.strip()) for score in f.readlines()]


# Save top scores to file
def save_top_scores():
    global top_scores
    with open(top_scores_file, 'w') as f:
        for score in top_scores:
            f.write(f"{score}\n")


# Initialize game
def initialize_game():
    global player_pos, ghosts, direction, lives, game_over, start_time, elapsed_time
    player_pos = (1, 1)
    ghosts = [(14, 7), (14, 13)]
    direction = None
    lives = 3
    game_over = False
    start_time = time.time()
    elapsed_time = 0


# Check if position is a valid move (within maze and not wall)
def is_valid_move(pos):
    x, y = pos
    if 0 <= x < len(maze[0]) and 0 <= y < len(maze):
        return maze[y][x] != '#'
    return False


# Main game loop
def main_game_loop():
    global player_pos, direction, lives, game_over, start_time, elapsed_time

    running = True
    while running:
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    direction = 'UP'
                elif event.key == pygame.K_DOWN:
                    direction = 'DOWN'
                elif event.key == pygame.K_LEFT:
                    direction = 'LEFT'
                elif event.key == pygame.K_RIGHT:
                    direction = 'RIGHT'

        if not game_over:
            # Update player position
            if direction == 'UP':
                new_pos = (player_pos[0], player_pos[1] - 1)
            elif direction == 'DOWN':
                new_pos = (player_pos[0], player_pos[1] + 1)
            elif direction == 'LEFT':
                new_pos = (player_pos[0] - 1, player_pos[1])
            elif direction == 'RIGHT':
                new_pos = (player_pos[0] + 1, player_pos[1])
            else:
                new_pos = player_pos

            if is_valid_move(new_pos):
                player_pos = new_pos

            # Update ghosts (basic random movement)
            for i, ghost in enumerate(ghosts):
                x, y = ghost
                dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
                if is_valid_move((x + dx, y + dy)):
                    ghosts[i] = (x + dx, y + dy)

            # Render maze
            for y, line in enumerate(maze):
                for x, char in enumerate(line):
                    color = WHITE if char == '.' else BLUE if char == '#' else BLACK
                    pygame.draw.rect(screen, color, (x * 40, y * 40, 40, 40))

            # Render player
            pygame.draw.circle(screen, YELLOW, (player_pos[0] * 40 + 20, player_pos[1] * 40 + 20), 15)

            # Render ghosts
            for ghost in ghosts:
                pygame.draw.circle(screen, BLUE, (ghost[0] * 40 + 20, ghost[1] * 40 + 20), 15)

            # Update timer and display elapsed time
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
                top_scores.sort()
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

            # Wait for key press to restart
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        initialize_game()

        pygame.display.flip()
        clock.tick(10)


# Load top scores at the beginning of the game
load_top_scores()

# Start the game loop
initialize_game()
main_game_loop()

pygame.quit()
