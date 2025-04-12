import pygame
import sys
import random
import time
import math
import json

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
STORY_DISPLAY_TIME = 3  # seconds to display each story line
FADE_DURATION = 1.0  # seconds for fade animation

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)

# Game setup
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Space Run - Race for Family")
clock = pygame.time.Clock()
game_data = {}

class Star:
    def __init__(self):
        self.x = random.randint(0, WINDOW_WIDTH)
        self.y = random.randint(0, WINDOW_HEIGHT)
        self.size = random.randint(1, 3)
        self.speed = random.uniform(0.5, 2.0)
        self.brightness = random.randint(100, 255)

    def move(self):
        self.y += self.speed
        if self.y > WINDOW_HEIGHT:
            self.y = 0
            self.x = random.randint(0, WINDOW_WIDTH)

    def draw(self):
        pygame.draw.circle(screen, (self.brightness, self.brightness, self.brightness), (int(self.x), int(self.y)), self.size)

class Obstacle:
    def __init__(self):
        self.width = random.randint(20, 50)
        self.height = random.randint(20, 50)
        self.x = random.randint(0, WINDOW_WIDTH - self.width)
        self.y = -self.height
        self.speed = random.randint(3, 7)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.is_cheating = random.random() < 0.3
        self.rotation = 0
        self.rotation_speed = random.uniform(-2, 2)

    def move(self):
        self.rect.y += self.speed
        if self.is_cheating:
            self.rect.x += random.randint(-2, 2)
        self.rotation += self.rotation_speed

    def draw(self):
        color = YELLOW if self.is_cheating else RED
        points = [
            (self.rect.centerx, self.rect.top),
            (self.rect.right, self.rect.bottom),
            (self.rect.left, self.rect.bottom)
        ]
        rotated_points = []
        for point in points:
            x = point[0] - self.rect.centerx
            y = point[1] - self.rect.centery
            rotated_x = x * math.cos(math.radians(self.rotation)) - y * math.sin(math.radians(self.rotation))
            rotated_y = x * math.sin(math.radians(self.rotation)) + y * math.cos(math.radians(self.rotation))
            rotated_points.append((rotated_x + self.rect.centerx, rotated_y + self.rect.centery))
        pygame.draw.polygon(screen, color, rotated_points)

class Player:
    def __init__(self):
        self.width = 50
        self.height = 50
        self.x = WINDOW_WIDTH // 2 - self.width // 2
        self.y = WINDOW_HEIGHT - 100
        self.speed = 5
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.lives = 3
        self.score = 0
        self.invincible = False
        self.invincible_timer = 0
        self.engine_particles = []

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WINDOW_WIDTH:
            self.rect.x += self.speed

    def draw(self):
        # Draw engine particles
        for particle in self.engine_particles[:]:
            particle[1] += 2
            particle[2] -= 1
            if particle[2] <= 0:
                self.engine_particles.remove(particle)
            else:
                pygame.draw.circle(screen, (255, 165, 0), (particle[0], particle[1]), particle[2])

        # Add new particles
        if random.random() < 0.3:
            self.engine_particles.append([self.rect.centerx, self.rect.bottom, random.randint(2, 4)])

        # Draw spaceship
        points = [
            (self.rect.centerx, self.rect.top),
            (self.rect.right, self.rect.bottom),
            (self.rect.left, self.rect.bottom)
        ]
        color = PURPLE if self.invincible else BLUE
        pygame.draw.polygon(screen, color, points)

class Game:
    def __init__(self):
        self.player = Player()
        self.obstacles = []
        self.stars = [Star() for _ in range(100)]
        self.story_phase = 0
        self.story_text = [
            "You were once a famous space racer, living a peaceful life with your family...",
            "Until a wealthy crime lord, Mr. X, approached you with an offer...",
            "He wanted you to throw the race for his gambling ring. You refused.",
            "Now he's taken your family hostage!",
            "You must win this deadly race to save them...",
            "But beware! Other racers will cheat and sabotage you!",
            "Use LEFT and RIGHT arrow keys to dodge obstacles.",
            "Yellow obstacles are cheating racers - they move unpredictably!",
            "Press SPACE to continue..."
        ]
        self.font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 24)
        self.showing_story = True
        self.game_over = False
        self.story_start_time = time.time()
        self.fade_alpha = 0
        self.fade_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.fade_surface.fill(BLACK)

    def update_story_setting(self):
        global game_data
        game_data = {"show_story": "false"}
        with open("game_data.json", "w") as json_data:
            json.dump(game_data, json_data)

    def spawn_obstacle(self):
        if random.random() < 0.02:
            self.obstacles.append(Obstacle())

    def handle_story(self):
        if self.story_phase < len(self.story_text):
            current_time = time.time()
            elapsed_time = current_time - self.story_start_time
            
            # Calculate fade alpha
            if elapsed_time < FADE_DURATION:
                self.fade_alpha = int(255 * (1 - elapsed_time / FADE_DURATION))
            elif elapsed_time > STORY_DISPLAY_TIME - FADE_DURATION:
                self.fade_alpha = int(255 * ((elapsed_time - (STORY_DISPLAY_TIME - FADE_DURATION)) / FADE_DURATION))
            else:
                self.fade_alpha = 0

            if elapsed_time >= STORY_DISPLAY_TIME:
                self.story_phase += 1
                self.story_start_time = current_time
                if self.story_phase >= len(self.story_text):
                    self.showing_story = False
                    self.update_story_setting()
                    return

            text = self.story_text[self.story_phase]
            text_surface = self.font.render(text, True, WHITE)
            text_rect = text_surface.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
            screen.blit(text_surface, text_rect)

            # Draw fade effect
            self.fade_surface.set_alpha(self.fade_alpha)
            screen.blit(self.fade_surface, (0, 0))

    def draw_lives(self):
        for i in range(self.player.lives):
            x = 10 + i * 30
            y = 10
            points = [
                (x + 10, y),
                (x + 20, y + 10),
                (x + 10, y + 20),
                (x, y + 10)
            ]
            pygame.draw.polygon(screen, BLUE, points)

    def draw_score(self):
        score_text = self.small_font.render(f"Score: {self.player.score}", True, WHITE)
        screen.blit(score_text, (WINDOW_WIDTH - 150, 10))

    def run(self):
        global game_data
        try:
            with open("game_data.json") as json_data:
                game_data = json.load(json_data)
        except (FileNotFoundError, json.JSONDecodeError):
            game_data = {"show_story": "true"}
            with open("game_data.json", "w") as json_data:
                json.dump(game_data, json_data)

        if game_data == {}:
            game_data = {"show_story": "true"}
        else:
            if game_data.get("show_story") == "true":
                self.showing_story = True
            else:
                self.showing_story = False

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if self.game_over:
                            self.__init__()
                        elif self.showing_story:
                            self.story_phase += 1
                            self.story_start_time = time.time()
                            if self.story_phase >= len(self.story_text):
                                self.showing_story = False
                                self.update_story_setting()

            screen.fill(BLACK)

            # Draw stars
            for star in self.stars:
                star.move()
                star.draw()

            if self.showing_story:
                self.handle_story()
            elif self.game_over:
                game_over_text = self.font.render("GAME OVER - Press SPACE to restart", True, WHITE)
                screen.blit(game_over_text, (WINDOW_WIDTH/2 - 200, WINDOW_HEIGHT/2))
            else:
                # Gameplay
                self.player.move()
                self.spawn_obstacle()

                # Update and draw obstacles
                for obstacle in self.obstacles[:]:
                    obstacle.move()
                    obstacle.draw()
                    if obstacle.rect.top > WINDOW_HEIGHT:
                        self.obstacles.remove(obstacle)
                        self.player.score += 10
                    elif obstacle.rect.colliderect(self.player.rect) and not self.player.invincible:
                        self.obstacles.remove(obstacle)
                        self.player.lives -= 1
                        self.player.invincible = True
                        self.player.invincible_timer = time.time()
                        if self.player.lives <= 0:
                            self.game_over = True

                # Handle invincibility
                if self.player.invincible and time.time() - self.player.invincible_timer > 2:
                    self.player.invincible = False

                self.player.draw()
                self.draw_lives()
                self.draw_score()

            pygame.display.flip()
            clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run() 