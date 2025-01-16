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
BACKGROUND_COLOR = (30, 30, 30)  # Background color
PADDLE_COLOR = (0, 122, 255)  # Paddle color
BALL_COLOR = (255, 50, 50)  # Ball color
BLOCK_COLOR = (0, 255, 0)  # Block color
OBSTACLE_COLOR = (255, 165, 0)  # Obstacle color
TEXT_COLOR = (255, 255, 255)  # Text color

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
POWER_UP_COLOR = (0, 0, 255)  # Blue for visibility
POWER_UP_WIDTH = 30  # Width of the power-up
POWER_UP_HEIGHT = 30  # Height of the power-up

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

# Load sounds
collision_sound = pygame.mixer.Sound("collision.wav")  # Sound for ball collisions
elimination_sound = pygame.mixer.Sound("elimination.wav")  # Sound for game over


def create_blocks():
    """Generate blocks in a grid pattern."""
    blocks.clear()  # Clear any existing blocks
    for row in range(5):  # Loop to create 5 rows of blocks
        for col in range(16):  # Loop to create 16 columns of blocks
            block_x = col * (block_width + 5)  # Calculate block's X-coordinate
            block_y = row * (block_height + 5) + 50  # Calculate block's Y-coordinate
            blocks.append(pygame.Rect(block_x, block_y, block_width, block_height))  # Add block to the list


def create_power_up():
    """Generate a new power-up block at a random position."""
    while True:
        power_up_x = random.randint(0, screen_width - POWER_UP_WIDTH)  # Random X-coordinate
        power_up_y = random.randint(50, screen_height - 200)  # Random Y-coordinate
        power_up_rect = pygame.Rect(power_up_x, power_up_y, POWER_UP_WIDTH, POWER_UP_HEIGHT)  # Create power-up
        # Ensure power-up does not overlap any block or obstacle
        if not any(power_up_rect.colliderect(block) for block in blocks) and \
           not any(power_up_rect.colliderect(obstacle) for obstacle in obstacles):
            return power_up_rect  # Return the new power-up


def create_new_obstacle():
    """Generate a new obstacle at a random position."""
    while True:
        obstacle_x = random.randint(0, screen_width - obstacle_width)  # Random X-coordinate
        obstacle_y = random.randint(50, screen_height - 200)  # Random Y-coordinate
        obstacle_rect = pygame.Rect(obstacle_x, obstacle_y, obstacle_width, obstacle_height)  # Create obstacle
        # Ensure obstacle does not overlap any block
        if not any(obstacle_rect.colliderect(block) for block in blocks):
            return obstacle_rect  # Return the new obstacle


def randomize_ball_direction():
    """Randomize the initial direction and speed of the ball."""
    speed_x = random.choice([-1, 1]) * random.randint(4, 6)  # Random speed between 4-6 in a random horizontal direction
    speed_y = random.choice([-1, 1]) * random.randint(4, 6)  # Random speed between 4-6 in a random vertical direction
    return speed_x, speed_y


def reset_game():
    """Reset the game state."""
    global ball_speed_x, ball_speed_y, score
    ball.x = screen_width // 2 - ball_radius  # Center the ball horizontally
    ball.y = screen_height // 2 - ball_radius + 50  # Center the ball vertically but under blocks
    ball_speed_x, ball_speed_y = randomize_ball_direction()  # Randomize ball direction and speed
    paddle.x = screen_width // 2 - paddle_width // 2  # Center the paddle
    paddle.y = screen_height - 30  # Position the paddle near the bottom
    score = 0  # Reset score
    create_blocks()  # Generate a new grid of blocks
    obstacles.clear()  # Clear existing obstacles
    power_ups.clear()  # Clear existing power-ups
    extra_balls.clear()  # Clear extra balls


def handle_collision():
    """Handle collisions of the ball with the paddle, blocks, and obstacles."""
    global ball_speed_x, ball_speed_y, score
    if ball.colliderect(paddle):  # Check collision with paddle
        ball_speed_y = -abs(ball_speed_y)  # Ensure ball bounces upwards
        ball_speed_x += (ball.centerx - paddle.centerx) / (paddle_width / 2) * 2  # Horizontal reflection based on paddle hit
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


def handle_power_up_collision():
    """Check if the ball collides with a power-up and spawn an extra ball."""
    global ball_speed_x, ball_speed_y
    for power_up in power_ups[:]:
        if ball.colliderect(power_up):  # Check collision with main ball
            power_ups.remove(power_up)  # Remove the power-up
            # Create a new ball with randomized direction
            speed_x, speed_y = randomize_ball_direction()
            extra_ball = pygame.Rect(ball.x, ball.y, ball_radius * 2, ball_radius * 2)
            extra_balls.append({"rect": extra_ball, "speed_x": speed_x, "speed_y": speed_y})


def update_extra_balls():
    """Update positions of extra balls and handle their collisions."""
    for extra_ball in extra_balls[:]:
        ball_rect = extra_ball["rect"]
        ball_rect.x += extra_ball["speed_x"]
        ball_rect.y += extra_ball["speed_y"]

        # Bounce off walls
        if ball_rect.x <= 0 or ball_rect.x >= screen_width - ball_radius * 2:
            extra_ball["speed_x"] *= -1
        if ball_rect.y <= 0:
            extra_ball["speed_y"] *= -1
        if ball_rect.y >= screen_height:  # Remove ball if it falls below the screen
            extra_balls.remove(extra_ball)

        # Handle collisions for extra balls
        if ball_rect.colliderect(paddle):
            extra_ball["speed_y"] = -abs(extra_ball["speed_y"])
        for block in blocks[:]:
            if ball_rect.colliderect(block):
                blocks.remove(block)
                score += 10
                extra_ball["speed_x"] *= -1
                extra_ball["speed_y"] *= -1
                break
        for obstacle in obstacles[:]:
            if ball_rect.colliderect(obstacle):
                obstacles.remove(obstacle)
                obstacles.append(create_new_obstacle())
                score += 5
                extra_ball["speed_x"] *= -1
                extra_ball["speed_y"] *= -1
                break


def draw():
    """Draw all game elements on the screen."""
    screen.fill(BACKGROUND_COLOR)
    pygame.draw.rect(screen, PADDLE_COLOR, paddle)
    pygame.draw.ellipse(screen, BALL_COLOR, ball)
    for extra_ball in extra_balls:
        pygame.draw.ellipse(screen, BALL_COLOR, extra_ball["rect"])
    for block in blocks:
        pygame.draw.rect(screen, BLOCK_COLOR, block)
    for obstacle in obstacles:
        pygame.draw.rect(screen, OBSTACLE_COLOR, obstacle)
    for power_up in power_ups:
        pygame.draw.rect(screen, POWER_UP_COLOR, power_up)
    score_text = font.render(f"Score: {score}", True, TEXT_COLOR)
    screen.blit(score_text, (10, 10))
    pygame.display.flip()


def show_start_screen():
    """Display the start screen."""
    while True:
        screen.fill(BACKGROUND_COLOR)  # Fill background
        title_text = font.render("Ball Breaker Game", True, TEXT_COLOR)  # Game title text
        play_text = font.render("Press SPACE to Play", True, TEXT_COLOR)  # Instruction text
        screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, screen_height // 2 - 50))
        screen.blit(play_text, (screen_width // 2 - play_text.get_width() // 2, screen_height // 2 + 10))
        pygame.display.flip()  # Update display
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Quit game
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:  # Start game
                return


def show_game_over_screen():
    """Display the game over screen."""
    elimination_sound.play()  # Play game over sound
    while True:
        screen.fill(BACKGROUND_COLOR)  # Fill background
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


def main():
    """Main game loop."""
    global ball_speed_x, ball_speed_y
    reset_game()
    running = True
    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and paddle.x > 0:
            paddle.x -= paddle_speed
        if keys[pygame.K_RIGHT] and paddle.x < screen_width - paddle_width:
            paddle.x += paddle_speed
        ball.x += ball_speed_x
        ball.y += ball_speed_y
        if ball.x <= 0 or ball.x >= screen_width - ball_radius * 2:
            ball_speed_x *= -1
        if ball.y <= 0:
            ball_speed_y *= -1
        if ball.y >= screen_height:
            if not show_game_over_screen():
                running = False
            else:
                reset_game()
        handle_collision()
        handle_power_up_collision()
        update_extra_balls()
        draw()
    pygame.quit()

# Start the game
show_start_screen()
main()
