import pygame
import sys
import random
import time
import math
<<<<<<< HEAD
import json
=======
import socket
import threading
import json
import select
>>>>>>> 19cd523d330dac0de51f22d99ce50ac914e0fe58

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
STORY_DISPLAY_TIME = 3  # seconds to display each story line
FADE_DURATION = 1.0  # seconds for fade animation
POWERUP_DURATION = 5.0  # seconds
PORT = 5000
BUFFER_SIZE = 1024

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
PINK = (255, 192, 203)

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

class PowerUp:
    def __init__(self):
        self.width = 20
        self.height = 20
        self.x = random.randint(0, WINDOW_WIDTH - self.width)
        self.y = -self.height
        self.speed = 3
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.type = random.choice(['speed', 'shield', 'time_slow'])
        self.colors = {
            'speed': GREEN,
            'shield': CYAN,
            'time_slow': ORANGE
        }
        self.rotation = 0

    def move(self):
        self.rect.y += self.speed
        self.rotation += 2

    def draw(self):
        color = self.colors[self.type]
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

class EnhancedObstacle(Obstacle):
    def __init__(self):
        super().__init__()
        self.ability = random.choice(['teleport', 'homing', 'shield'])
        self.teleport_timer = 0
        self.homing_speed = 2
        self.shield_active = False
        self.shield_timer = 0

    def move(self):
        if self.ability == 'teleport':
            self.teleport_timer += 1
            if self.teleport_timer >= 60:  # Teleport every second
                self.rect.x = random.randint(0, WINDOW_WIDTH - self.width)
                self.teleport_timer = 0
        elif self.ability == 'homing':
            # Move towards player
            if self.rect.centerx < self.player.rect.centerx:
                self.rect.x += self.homing_speed
            else:
                self.rect.x -= self.homing_speed
        elif self.ability == 'shield':
            self.shield_timer += 1
            if self.shield_timer >= 120:  # Toggle shield every 2 seconds
                self.shield_active = not self.shield_active
                self.shield_timer = 0

        super().move()

    def draw(self):
        super().draw()
        if self.ability == 'shield' and self.shield_active:
            pygame.draw.circle(screen, CYAN, self.rect.center, self.width + 5, 2)

class NetworkManager:
    def __init__(self, is_host=False):
        self.is_host = is_host
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self.other_players = {}
        self.receive_thread = None

    def host_game(self):
        self.socket.bind(('0.0.0.0', PORT))
        self.socket.listen(1)
        print(f"Waiting for connection on port {PORT}...")
        client_socket, address = self.socket.accept()
        self.socket = client_socket
        self.connected = True
        self.start_receive_thread()

    def join_game(self, host_ip):
        self.socket.connect((host_ip, PORT))
        self.connected = True
        self.start_receive_thread()

    def start_receive_thread(self):
        self.receive_thread = threading.Thread(target=self.receive_data)
        self.receive_thread.daemon = True
        self.receive_thread.start()

    def receive_data(self):
        while self.connected:
            try:
                data = self.socket.recv(BUFFER_SIZE)
                if not data:
                    break
                player_data = json.loads(data.decode())
                self.other_players[player_data['id']] = player_data
            except:
                break
        self.connected = False

    def send_data(self, player_data):
        if self.connected:
            try:
                self.socket.send(json.dumps(player_data).encode())
            except:
                self.connected = False

    def close(self):
        self.connected = False
        if self.receive_thread:
            self.receive_thread.join()
        self.socket.close()

class Player:
    def __init__(self, x, controls, color, name, player_id):
        self.width = 50
        self.height = 50
        self.x = x
        self.y = WINDOW_HEIGHT - 100
        self.base_speed = 5
        self.speed = self.base_speed
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.lives = 3
        self.score = 0
        self.invincible = False
        self.invincible_timer = 0
        self.engine_particles = []
        self.active_powerups = {}
        self.time_slow_factor = 1.0
        self.controls = controls
        self.color = color
        self.name = name
        self.id = player_id
        self.last_update = time.time()

    def get_state(self):
        return {
            'id': self.id,
            'x': self.rect.x,
            'y': self.rect.y,
            'score': self.score,
            'lives': self.lives,
            'active_powerups': self.active_powerups,
            'invincible': self.invincible
        }

    def update_from_state(self, state):
        self.rect.x = state['x']
        self.rect.y = state['y']
        self.score = state['score']
        self.lives = state['lives']
        self.active_powerups = state['active_powerups']
        self.invincible = state['invincible']

    def activate_powerup(self, powerup_type):
        self.active_powerups[powerup_type] = time.time()
        if powerup_type == 'speed':
            self.speed = self.base_speed * 2
        elif powerup_type == 'shield':
            self.invincible = True
        elif powerup_type == 'time_slow':
            self.time_slow_factor = 0.5

    def update_powerups(self):
        current_time = time.time()
        for powerup_type in list(self.active_powerups.keys()):
            if current_time - self.active_powerups[powerup_type] > POWERUP_DURATION:
                if powerup_type == 'speed':
                    self.speed = self.base_speed
                elif powerup_type == 'shield':
                    self.invincible = False
                elif powerup_type == 'time_slow':
                    self.time_slow_factor = 1.0
                del self.active_powerups[powerup_type]

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[self.controls['left']] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[self.controls['right']] and self.rect.right < WINDOW_WIDTH:
            self.rect.x += self.speed
        if keys[self.controls['powerup']] and not self.active_powerups:
            self.activate_powerup(random.choice(['speed', 'shield', 'time_slow']))

        self.update_powerups()

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
        color = PURPLE if self.invincible else self.color
        pygame.draw.polygon(screen, color, points)

        # Draw player name
        name_text = game.small_font.render(self.name, True, WHITE)
        screen.blit(name_text, (self.rect.centerx - 20, self.rect.top - 20))

class Game:
    def __init__(self):
        self.network = None
        self.player = None
        self.other_players = {}
        self.obstacles = []
        self.powerups = []
        self.stars = [Star() for _ in range(100)]
        self.story_phase = 0
        self.story_text = [
            "You were once a famous space racer, living a peaceful life with your family...",
            "Until a wealthy crime lord, Mr. X, approached you with an offer...",
            "He wanted you to throw the race for his gambling ring. You refused.",
            "Now he's taken your family hostage!",
            "You must win this deadly race to save them...",
            "But beware! Other racers will cheat and sabotage you!",
            "Use LEFT and RIGHT arrow keys to move.",
            "Press P for power-ups.",
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
        self.menu_active = True
        self.menu_options = ["Host Game", "Join Game", "Exit"]
        self.selected_option = 0
        self.host_ip = ""
        self.player_name = "Player"
        self.inputting_name = False
        self.inputting_ip = False
        self.last_menu_update = 0
        self.menu_update_interval = 100  # milliseconds
        self.paused = False
        self.pause_options = ["Resume", "Restart", "Exit to Menu"]
        self.selected_pause_option = 0
        self.last_pause_update = 0
        self.pause_update_interval = 100  # milliseconds

    def show_pause_menu(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_pause_update < self.pause_update_interval:
            return
        
        self.last_pause_update = current_time
        
        # Create semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Semi-transparent black
        screen.blit(overlay, (0, 0))

        # Draw pause title
        title = self.font.render("PAUSED", True, WHITE)
        screen.blit(title, (WINDOW_WIDTH/2 - 50, 200))

        # Draw options
        for i, option in enumerate(self.pause_options):
            color = GREEN if i == self.selected_pause_option else WHITE
            text = self.font.render(option, True, color)
            screen.blit(text, (WINDOW_WIDTH/2 - 100, 300 + i * 50))

        pygame.display.flip()

    def handle_pause_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.paused = False
                elif event.key == pygame.K_UP:
                    self.selected_pause_option = (self.selected_pause_option - 1) % len(self.pause_options)
                elif event.key == pygame.K_DOWN:
                    self.selected_pause_option = (self.selected_pause_option + 1) % len(self.pause_options)
                elif event.key == pygame.K_RETURN:
                    if self.selected_pause_option == 0:  # Resume
                        self.paused = False
                    elif self.selected_pause_option == 1:  # Restart
                        self.__init__()
                    elif self.selected_pause_option == 2:  # Exit to Menu
                        self.menu_active = True
                        self.paused = False
                        self.network = None
                        self.player = None
                        self.other_players = {}
        return True

    def show_menu(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_menu_update < self.menu_update_interval:
            return
        
        self.last_menu_update = current_time
        screen.fill(BLACK)
        
        # Draw animated stars in background
        for star in self.stars:
            star.move()
            star.draw()

        # Draw game title with animation
        title = self.font.render("SPACE RUN", True, WHITE)
        subtitle = self.small_font.render("Multiplayer Space Racing", True, WHITE)
        screen.blit(title, (WINDOW_WIDTH/2 - 100, 100))
        screen.blit(subtitle, (WINDOW_WIDTH/2 - 150, 150))

        # Draw player name input with better styling
        name_label = self.small_font.render("YOUR NAME:", True, WHITE)
        name_box = pygame.Rect(WINDOW_WIDTH/2 - 100, 200, 200, 40)
        pygame.draw.rect(screen, GREEN if self.inputting_name else WHITE, name_box, 2)
        name_text = self.font.render(self.player_name, True, GREEN if self.inputting_name else WHITE)
        screen.blit(name_label, (WINDOW_WIDTH/2 - 200, 210))
        screen.blit(name_text, (WINDOW_WIDTH/2 - 90, 210))

        # Draw menu options with better spacing
        for i, option in enumerate(self.menu_options):
            color = GREEN if i == self.selected_option else WHITE
            text = self.font.render(option, True, color)
            screen.blit(text, (WINDOW_WIDTH/2 - 100, 300 + i * 50))

        # Draw IP input with better styling
        if self.selected_option == 1:  # Join Game
            ip_label = self.small_font.render("HOST IP:", True, WHITE)
            ip_box = pygame.Rect(WINDOW_WIDTH/2 - 100, 450, 200, 40)
            pygame.draw.rect(screen, GREEN if self.inputting_ip else WHITE, ip_box, 2)
            ip_text = self.font.render(self.host_ip, True, GREEN if self.inputting_ip else WHITE)
            screen.blit(ip_label, (WINDOW_WIDTH/2 - 200, 460))
            screen.blit(ip_text, (WINDOW_WIDTH/2 - 90, 460))

        # Draw controls help
        controls_text = [
            "N - Edit Name",
            "I - Edit IP",
            "↑↓ - Navigate",
            "ENTER - Select"
        ]
        for i, text in enumerate(controls_text):
            help_text = self.small_font.render(text, True, WHITE)
            screen.blit(help_text, (WINDOW_WIDTH - 200, 500 + i * 25))

        pygame.display.flip()

    def handle_menu_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if self.inputting_name:
                    if event.key == pygame.K_RETURN:
                        self.inputting_name = False
                    elif event.key == pygame.K_BACKSPACE:
                        self.player_name = self.player_name[:-1]
                    elif len(self.player_name) < 12 and event.unicode.isalnum():
                        self.player_name += event.unicode
                elif self.inputting_ip:
                    if event.key == pygame.K_RETURN:
                        self.inputting_ip = False
                    elif event.key == pygame.K_BACKSPACE:
                        self.host_ip = self.host_ip[:-1]
                    elif event.unicode.isdigit() or event.unicode == '.':
                        self.host_ip += event.unicode
                else:
                    if event.key == pygame.K_UP:
                        self.selected_option = (self.selected_option - 1) % len(self.menu_options)
                    elif event.key == pygame.K_DOWN:
                        self.selected_option = (self.selected_option + 1) % len(self.menu_options)
                    elif event.key == pygame.K_RETURN:
                        if self.selected_option == 0:  # Host Game
                            self.network = NetworkManager(is_host=True)
                            self.player = Player(
                                WINDOW_WIDTH // 2,
                                {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'powerup': pygame.K_p},
                                BLUE,
                                self.player_name,
                                "1"
                            )
                            threading.Thread(target=self.network.host_game).start()
                            self.menu_active = False
                        elif self.selected_option == 1:  # Join Game
                            if self.host_ip:
                                self.network = NetworkManager(is_host=False)
                                self.player = Player(
                                    WINDOW_WIDTH // 2,
                                    {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'powerup': pygame.K_p},
                                    RED,
                                    self.player_name,
                                    "2"
                                )
                                self.network.join_game(self.host_ip)
                                self.menu_active = False
                        elif event.key == pygame.K_n and not self.inputting_ip:
                            self.inputting_name = True
                        elif event.key == pygame.K_i and not self.inputting_name:
                            self.inputting_ip = True
        return True

    def update_story_setting(self):
        global game_data
        game_data = {"show_story": "false"}
        with open("game_data.json", "w") as json_data:
            json.dump(game_data, json_data)

    def spawn_obstacle(self):
        if random.random() < 0.02:
            if random.random() < 0.3:  # 30% chance for enhanced obstacle
                obstacle = EnhancedObstacle()
                obstacle.player = self.player  # Pass player reference for homing
                self.obstacles.append(obstacle)
            else:
                self.obstacles.append(Obstacle())

    def spawn_powerup(self):
        if random.random() < 0.005:  # 0.5% chance each frame
            self.powerups.append(PowerUp())

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

    def draw_lives(self, player, x_offset):
        for i in range(player.lives):
            x = x_offset + i * 30
            y = 10
            points = [
                (x + 10, y),
                (x + 20, y + 10),
                (x + 10, y + 20),
                (x, y + 10)
            ]
            pygame.draw.polygon(screen, player.color, points)

    def draw_score(self, player, x_offset):
        score_text = self.small_font.render(f"{player.name}: {player.score}", True, WHITE)
        screen.blit(score_text, (x_offset, 40))

    def draw_powerups(self, player, y_pos):
        for powerup_type in player.active_powerups:
            remaining_time = POWERUP_DURATION - (time.time() - player.active_powerups[powerup_type])
            powerup_text = self.small_font.render(f"{powerup_type}: {remaining_time:.1f}s", True, WHITE)
            screen.blit(powerup_text, (10, y_pos))
            y_pos += 20

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
            if self.menu_active:
                running = self.handle_menu_input()
                self.show_menu()
            elif self.paused:
                # Handle pause menu
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.paused = False
                        elif event.key == pygame.K_UP:
                            self.selected_pause_option = (self.selected_pause_option - 1) % len(self.pause_options)
                        elif event.key == pygame.K_DOWN:
                            self.selected_pause_option = (self.selected_pause_option + 1) % len(self.pause_options)
                        elif event.key == pygame.K_RETURN:
                            if self.selected_pause_option == 0:  # Resume
                                self.paused = False
                            elif self.selected_pause_option == 1:  # Restart
                                self.__init__()
                            elif self.selected_pause_option == 2:  # Exit to Menu
                                self.menu_active = True
                                self.paused = False
                                self.network = None
                                self.player = None
                                self.other_players = {}
                
                # Draw pause menu
                overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 128))
                screen.blit(overlay, (0, 0))
                
                title = self.font.render("PAUSED", True, WHITE)
                screen.blit(title, (WINDOW_WIDTH/2 - 50, 200))
                
                for i, option in enumerate(self.pause_options):
                    color = GREEN if i == self.selected_pause_option else WHITE
                    text = self.font.render(option, True, color)
                    screen.blit(text, (WINDOW_WIDTH/2 - 100, 300 + i * 50))
                
                pygame.display.flip()
            else:
                # Gameplay loop
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.paused = True
                        elif event.key == pygame.K_SPACE:
                            if self.game_over:
                                self.__init__()
                            elif self.showing_story:
                                self.story_phase += 1
                                self.story_start_time = time.time()
                                if self.story_phase >= len(self.story_text):
                                    self.showing_story = False

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
                    if self.player:
                        self.player.move()
                        if self.network and self.network.connected:
                            self.network.send_data(self.player.get_state())
                            for player_id, player_data in self.network.other_players.items():
                                if player_id not in self.other_players:
                                    self.other_players[player_id] = Player(
                                        player_data['x'],
                                        None,
                                        RED if player_id == "2" else BLUE,
                                        f"Player {player_id}",
                                        player_id
                                    )
                                self.other_players[player_id].update_from_state(player_data)

                    self.spawn_obstacle()
                    self.spawn_powerup()

                    # Update and draw powerups
                    for powerup in self.powerups[:]:
                        powerup.move()
                        powerup.draw()
                        if powerup.rect.top > WINDOW_HEIGHT:
                            self.powerups.remove(powerup)
                        elif self.player and powerup.rect.colliderect(self.player.rect):
                            self.player.activate_powerup(powerup.type)
                            self.powerups.remove(powerup)

                    # Update and draw obstacles
                    for obstacle in self.obstacles[:]:
                        obstacle.move()
                        obstacle.draw()
                        if obstacle.rect.top > WINDOW_HEIGHT:
                            self.obstacles.remove(obstacle)
                            if self.player:
                                self.player.score += 10
                        elif self.player and obstacle.rect.colliderect(self.player.rect) and not self.player.invincible:
                            self.obstacles.remove(obstacle)
                            self.player.lives -= 1
                            self.player.invincible = True
                            self.player.invincible_timer = time.time()
                            if self.player.lives <= 0:
                                self.game_over = True

                    # Draw players
                    if self.player:
                        self.player.draw()
                        self.draw_lives(self.player, 10)
                        self.draw_score(self.player, 10)
                        self.draw_powerups(self.player, 70)

                    for other_player in self.other_players.values():
                        other_player.draw()
                        self.draw_lives(other_player, 10 + 300)
                        self.draw_score(other_player, 10 + 300)

                pygame.display.flip()
                clock.tick(FPS)

        if self.network:
            self.network.close()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run() 