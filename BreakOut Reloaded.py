import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions and setup
screen_width = 800  # Width of the game screen
screen_height = 600  # Height of the game screen
screen = pygame.display.set_mode((screen_width, screen_height))  # Create game window
pygame.display.set_caption("BreakOut Reloaded")  # Set window title

# Colors
BACKGROUND_COLOR = (30, 30, 30)  # Default background color
PADDLE_COLOR = (255, 255, 255)  # Paddle color
BLOCK_COLOR = (255, 255, 255)  # Block color
OBSTACLE_COLOR = (128, 128, 128)  # Obstacle color (green for visibility)
TEXT_COLOR = (255, 255, 255)  # Text color
POWER_UP_COLOR = (0, 0, 255)  # Pink color for power-up block

# Ball properties
ball_radius = 10  # Radius of the ball
ball_speed_x = 5  # Horizontal speed of the ball
ball_speed_y = -5  # Vertical speed of the ball

# Paddle properties
paddle_width = 100  # Width of the paddle
paddle_height = 15  # Height of the paddle
paddle_speed = 8  # Speed of paddle movement

# Block properties
block_width = 50  # Width of each block
block_height = 20  # Height of each block

# Obstacle properties
obstacle_width = 30  # Width of each obstacle
obstacle_height = 30  # Height of each obstacle

# Power-up properties
POWER_UP_WIDTH = 30  # Width of the power-up block
POWER_UP_HEIGHT = 30  # Height of the power-up block

# Game objects
ball = pygame.Rect(0, 0, ball_radius * 2, ball_radius * 2)  # Ball as a rectangle
paddle = pygame.Rect(0, 0, paddle_width, paddle_height)  # Paddle as a rectangle
blocks = []  # List of blocks
obstacles = []  # List of obstacles
power_ups = []  # List of active power-ups
extra_balls = []  # List of extra balls

# Score and font
score = 0  # Player's score
font = pygame.font.SysFont("Arial", 24)  # Font for text

# Clock for frame rate control
clock = pygame.time.Clock()

# Load background images
background_image_easy = pygame.image.load("background_easy.png")
background_image_medium = pygame.image.load("background_medium.png")
background_image_fast = pygame.image.load("background_fast.png")
background_image_start = pygame.image.load("background_start.png")  # Background for start screen
background_image_game_over = pygame.image.load("background_game_over.png")  # Background for game over screen

background_image_easy = pygame.transform.scale(background_image_easy, (screen_width, screen_height))  # Scale to screen size
background_image_medium = pygame.transform.scale(background_image_medium, (screen_width, screen_height))  # Scale to screen size
background_image_fast = pygame.transform.scale(background_image_fast, (screen_width, screen_height))  # Scale to screen size
background_image_start = pygame.transform.scale(background_image_start, (screen_width, screen_height))  # Scale to screen size
background_image_game_over = pygame.transform.scale(background_image_game_over, (screen_width, screen_height))  # Scale to screen size

# Load sounds
collision_sound = pygame.mixer.Sound("collision.wav")  # Sound for ball collisions
elimination_sound = pygame.mixer.Sound("elimination.wav")  # Sound for game over
pygame.mixer.music.load("background_music.mp3")  # Load background music
pygame.mixer.music.set_volume(0.3)  # Set background music volume to 70%

# Load ball image
ball_image = pygame.image.load("ball_image.png")
ball_image = pygame.transform.scale(ball_image, (ball_radius * 2, ball_radius * 2))  # Scale the image

# Play background music in a loop
pygame.mixer.music.play(-1)

# Initialize pause state as False
pause = False  # Pause state

# Difficulty variable (initially set to "easy")
difficulty = "easy"  # Default to Easy mode

# Create blocks in a grid pattern
def create_blocks():
    """Generate blocks in a grid pattern."""
    blocks.clear()  # Clear any existing blocks
    for row in range(5):  # Loop to create 5 rows of blocks
        for col in range(16):  # Loop to create 16 columns of blocks
            block_x = col * (block_width + 5)  # Calculate block's X-coordinate
            block_y = row * (block_height + 5) + 50  # Calculate block's Y-coordinate
            blocks.append(pygame.Rect(block_x, block_y, block_width, block_height))  # Add block to the list

# Randomize the ball direction and speed
def randomize_ball_direction():
    """Randomize the initial direction and speed of the ball."""
    speed_x = random.choice([-1, 1]) * random.randint(4, 6)  # Random speed between 4-6 in a random horizontal direction
    speed_y = random.choice([-1, 1]) * random.randint(4, 6)  # Random speed between 4-6 in a random vertical direction
    return speed_x, speed_y

# Reset the game state
def reset_game():
    """Reset the game state."""
    global ball_speed_x, ball_speed_y, score
    ball.x = screen_width // 2 - ball.width // 2  # Center the ball horizontally
    ball.y = screen_height // 2 - ball.height // 2  # Center the ball vertically
    ball_speed_x, ball_speed_y = randomize_ball_direction()  # Randomize ball direction and speed
    paddle.x = screen_width // 2 - paddle.width // 2  # Center the paddle
    paddle.y = screen_height - 30  # Position the paddle near the bottom
    score = 0  # Reset score
    create_blocks()  # Generate a new grid of blocks
    obstacles.clear()  # Clear existing obstacles
    power_ups.clear()  # Clear existing power-ups
    extra_balls.clear()  # Clear extra balls

# Handle collisions with paddle, blocks, and obstacles
def handle_collision():
    """Handle collisions of the ball with the paddle, blocks, and obstacles."""
    global ball_speed_x, ball_speed_y, score
    if ball.colliderect(paddle):  # Check collision with paddle
        ball_speed_y = -abs(ball_speed_y)  # Ensure ball bounces upwards
        ball_speed_x += (ball.centerx - paddle.centerx) / (paddle.width / 2) * 2  # Horizontal reflection based on paddle hit
        collision_sound.play()

    for block in blocks[:]:  # Check collision with blocks
        if ball.colliderect(block):
            blocks.remove(block)  # Remove the block
            obstacles.append(create_new_obstacle())  # Add a new obstacle
            score += 10  # Increase score
            ball_speed_x *= -1  # Reverse horizontal direction
            ball_speed_y *= -1  # Reverse vertical direction
            collision_sound.play()  # Play collision sound
            if random.random() < 0.1:  # 10% chance to spawn a power-up
                power_ups.append(create_power_up())
            break

    for obstacle in obstacles[:]:  # Check collision with obstacles
        if ball.colliderect(obstacle):
            obstacles.remove(obstacle)  # Remove the obstacle
            obstacles.append(create_new_obstacle())  # Add a new obstacle
            score += 5  # Increase score
            ball_speed_x *= -1  # Reverse horizontal direction
            ball_speed_y *= -1  # Reverse vertical direction
            collision_sound.play()  # Play collision sound
            break

# Generate a new obstacle at a random position
def create_new_obstacle():
    """Generate a new obstacle at a random position."""
    while True:
        obstacle_x = random.randint(0, screen_width - obstacle_width)  # Random X-coordinate
        obstacle_y = random.randint(50, screen_height - 200)  # Random Y-coordinate
        obstacle_rect = pygame.Rect(obstacle_x, obstacle_y, obstacle_width, obstacle_height)  # Create obstacle
        # Ensure obstacle does not overlap any block
        if not any(obstacle_rect.colliderect(block) for block in blocks):
            return obstacle_rect  # Return the new obstacle

# Create a new power-up at a random position (colored block instead of image)
def create_power_up():
    """Generate a new power-up block at a random position."""
    while True:
        power_up_x = random.randint(0, screen_width - POWER_UP_WIDTH)  # Random X-coordinate
        power_up_y = random.randint(50, screen_height - 200)  # Random Y-coordinate
        power_up_rect = pygame.Rect(power_up_x, power_up_y, POWER_UP_WIDTH, POWER_UP_HEIGHT)  # Create power-up
        return power_up_rect  # Return the new power-up

# Handle power-up collision
def handle_power_up_collision():
    """Check if the ball collides with a power-up and spawn an extra ball."""
    global ball_speed_x, ball_speed_y
    for power_up in power_ups[:]:
        if ball.colliderect(power_up):  # Check collision with main ball
            power_ups.remove(power_up)  # Remove the power-up
            # Make the ball 3x faster
            ball_speed_x *= 3
            ball_speed_y *= 3

# Show the start screen and allow the user to pick a mode
def show_start_screen():
    """Display the start screen with mode selection."""
    global ball_speed_x, ball_speed_y, difficulty
    while True:
        screen.fill(BACKGROUND_COLOR)  # Fill background
        screen.blit(background_image_start, (0, 0))  # Show start screen background
        title_text = font.render("BreakOut Reloaded", True, TEXT_COLOR)  # Game title text
        easy_text = font.render("Press 1 for Easy", True, TEXT_COLOR)
        medium_text = font.render("Press 2 for Medium", True, TEXT_COLOR)
        fast_text = font.render("Press 3 for Fast", True, TEXT_COLOR)

        screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, screen_height // 2 - 100))
        screen.blit(easy_text, (screen_width // 2 - easy_text.get_width() // 2, screen_height // 2 - 50))
        screen.blit(medium_text, (screen_width // 2 - medium_text.get_width() // 2, screen_height // 2))
        screen.blit(fast_text, (screen_width // 2 - fast_text.get_width() // 2, screen_height // 2 + 50))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    difficulty = "easy"
                    ball_speed_x = 3
                    ball_speed_y = -3
                    return
                elif event.key == pygame.K_2:
                    difficulty = "medium"
                    ball_speed_x = 5
                    ball_speed_y = -5
                    return
                elif event.key == pygame.K_3:
                    difficulty = "fast"
                    ball_speed_x = 7
                    ball_speed_y = -7
                    return

# Show the game over screen
def show_game_over_screen():
    """Display the game over screen."""
    elimination_sound.play()  # Play game over sound
    while True:
        screen.fill(BACKGROUND_COLOR)  # Fill background
        screen.blit(background_image_game_over, (0, 0))  # Show game over background
        game_over_text = font.render("Game Over", True, TEXT_COLOR)  # Game over text
        score_text = font.render(f"Final Score: {score}", True, TEXT_COLOR)  # Final score text
        replay_text = font.render("Press R to Replay or Q to Quit", True, TEXT_COLOR)  # Replay instructions
        screen.blit(game_over_text, (screen_width // 2 - game_over_text.get_width() // 2, screen_height // 2 - 50))
        screen.blit(score_text, (screen_width // 2 - score_text.get_width() // 2, screen_height // 2 + 10))
        screen.blit(replay_text, (screen_width // 2 - replay_text.get_width() // 2, screen_height // 2 + 70))
        pygame.display.flip()  # Update display
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Quit game
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Replay game
                    return True
                if event.key == pygame.K_q:  # Quit game
                    return False

# Main game loop
def main():
    """Main game loop."""
    global ball_speed_x, ball_speed_y, pause, score, difficulty
    reset_game()
    running = True
    while running:
        clock.tick(60)
        if difficulty == "easy":
            screen.blit(background_image_easy, (0, 0))  # Draw the background first
        elif difficulty == "medium":
            screen.blit(background_image_medium, (0, 0))  # Draw the background first
        elif difficulty == "fast":
            screen.blit(background_image_fast, (0, 0))  # Draw the background first

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:  # Pause when 'P' is pressed
                    pause = not pause

        if pause:
            # Display Pause Text
            pause_text = font.render("PAUSED", True, TEXT_COLOR)
            screen.blit(pause_text, (screen_width // 2 - pause_text.get_width() // 2, screen_height // 2))
            pygame.display.flip()
            continue  # Skip the rest of the game loop to maintain the pause screen

        # Handle paddle movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and paddle.x > 0:
            paddle.x -= 8
        if keys[pygame.K_RIGHT] and paddle.x < screen_width - paddle.width:
            paddle.x += 8

        # Move ball
        ball.x += ball_speed_x
        ball.y += ball_speed_y

        # Ball collision with walls
        if ball.x <= 0 or ball.x >= screen_width - ball.width:
            ball_speed_x *= -1
        if ball.y <= 0:
            ball_speed_y *= -1
        if ball.y >= screen_height:  # Game Over when ball falls below the screen
            if not show_game_over_screen():
                running = False
            else:
                reset_game()

        handle_collision()
        handle_power_up_collision()

        # Draw ball and paddle
        screen.blit(ball_image, (ball.x, ball.y))  # Ball
        pygame.draw.rect(screen, PADDLE_COLOR, paddle)  # Paddle

        # Draw blocks
        for block in blocks:
            pygame.draw.rect(screen, BLOCK_COLOR, block)

        # Draw obstacles (this is the key fix)
        for obstacle in obstacles:
            pygame.draw.rect(screen, OBSTACLE_COLOR, obstacle)

        # Draw power-ups as colored blocks
        for power_up in power_ups:
            pygame.draw.rect(screen, POWER_UP_COLOR, power_up)

        # Draw score
        score_text = font.render(f"Score: {score}", True, TEXT_COLOR)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()

    pygame.quit()

# Start the game
show_start_screen()  # Show the start screen and mode selection
reset_game()  # Initialize game state
main()
