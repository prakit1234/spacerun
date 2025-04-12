import pygame
import sys
import random
import time
import math
import json
import socket
import threading
import json
import select

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
        self.pulse_scale = 1.0
        self.pulse_growing = True

    def move(self):
        self.rect.y += self.speed
        if self.is_cheating:
            self.rect.x += random.randint(-2, 2)
        self.rotation += self.rotation_speed

    def draw(self):
        # Create obstacle surface
        obstacle_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Draw main body with pulse effect
        if self.pulse_growing:
            self.pulse_scale += 0.02
            if self.pulse_scale >= 1.2:
                self.pulse_growing = False
        else:
            self.pulse_scale -= 0.02
            if self.pulse_scale <= 0.8:
                self.pulse_growing = True

        # Draw obstacle with rotation and pulse
        color = YELLOW if self.is_cheating else RED
        points = [
            (self.width//2, 0),
            (self.width, self.height),
            (self.width//2, self.height - 10),
            (0, self.height)
        ]
        
        # Apply rotation
        rotated_points = []
        for point in points:
            x = point[0] - self.width//2
            y = point[1] - self.height//2
            rotated_x = x * math.cos(math.radians(self.rotation)) - y * math.sin(math.radians(self.rotation))
            rotated_y = x * math.sin(math.radians(self.rotation)) + y * math.cos(math.radians(self.rotation))
            rotated_points.append((
                rotated_x * self.pulse_scale + self.width//2,
                rotated_y * self.pulse_scale + self.height//2
            ))
        
        pygame.draw.polygon(obstacle_surface, color, rotated_points)
        
        # Add details
        if self.is_cheating:
            # Draw warning symbol
            pygame.draw.line(obstacle_surface, WHITE, 
                           (self.width//2, 5), (self.width//2, self.height - 5), 2)
            pygame.draw.line(obstacle_surface, WHITE, 
                           (5, self.height//2), (self.width - 5, self.height//2), 2)
        
        screen.blit(obstacle_surface, self.rect)

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
        self.pulse_scale = 1.0
        self.pulse_growing = True
        self.glow_radius = 0
        self.glow_growing = True

    def move(self):
        self.rect.y += self.speed
        self.rotation += 2

    def draw(self):
        # Create powerup surface
        powerup_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Update pulse effect
        if self.pulse_growing:
            self.pulse_scale += 0.02
            if self.pulse_scale >= 1.2:
                self.pulse_growing = False
        else:
            self.pulse_scale -= 0.02
            if self.pulse_scale <= 0.8:
                self.pulse_growing = True

        # Update glow effect
        if self.glow_growing:
            self.glow_radius += 0.5
            if self.glow_radius >= 15:
                self.glow_growing = False
        else:
            self.glow_radius -= 0.5
            if self.glow_radius <= 10:
                self.glow_growing = True

        # Draw glow
        glow_surface = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*self.colors[self.type], 128), 
                         (15, 15), self.glow_radius)
        powerup_surface.blit(glow_surface, (-5, -5))

        # Draw powerup icon
        points = [
            (self.width//2, 0),
            (self.width, self.height),
            (self.width//2, self.height - 10),
            (0, self.height)
        ]
        
        # Apply rotation and pulse
        rotated_points = []
        for point in points:
            x = point[0] - self.width//2
            y = point[1] - self.height//2
            rotated_x = x * math.cos(math.radians(self.rotation)) - y * math.sin(math.radians(self.rotation))
            rotated_y = x * math.sin(math.radians(self.rotation)) + y * math.cos(math.radians(self.rotation))
            rotated_points.append((
                rotated_x * self.pulse_scale + self.width//2,
                rotated_y * self.pulse_scale + self.height//2
            ))
        
        pygame.draw.polygon(powerup_surface, self.colors[self.type], rotated_points)
        
        # Add type-specific details
        if self.type == 'speed':
            pygame.draw.line(powerup_surface, WHITE, 
                           (5, 5), (self.width - 5, self.height - 5), 2)
            pygame.draw.line(powerup_surface, WHITE, 
                           (5, self.height - 5), (self.width - 5, 5), 2)
        elif self.type == 'shield':
            pygame.draw.circle(powerup_surface, WHITE, 
                             (self.width//2, self.height//2), 5, 2)
        elif self.type == 'time_slow':
            pygame.draw.arc(powerup_surface, WHITE, 
                          (5, 5, self.width - 10, self.height - 10), 
                          math.pi/4, 3*math.pi/4, 2)
        
        screen.blit(powerup_surface, self.rect)

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
    def __init__(self, is_server=False, server_ip=None):
        self.is_server = is_server
        self.server_ip = server_ip
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}  # Only used by server
        self.client_id = None  # Only used by client
        self.running = True

    def start_server(self):
        """Start the game server"""
        try:
            self.socket.bind(('0.0.0.0', 5000))
            self.socket.listen(5)
            print(f"Server started on port 5000")
            threading.Thread(target=self.accept_connections).start()
            return True
        except Exception as e:
            print(f"Failed to start server: {e}")
            return False

    def accept_connections(self):
        """Accept new client connections"""
        while self.running:
            try:
                client_socket, address = self.socket.accept()
                client_id = str(len(self.clients) + 1)
                self.clients[client_id] = {
                    'socket': client_socket,
                    'address': address,
                    'player': None
                }
                print(f"New connection from {address} as client {client_id}")
                threading.Thread(target=self.handle_client, args=(client_id,)).start()
            except:
                break

    def handle_client(self, client_id):
        """Handle communication with a specific client"""
        client = self.clients[client_id]
        while self.running:
            try:
                data = client['socket'].recv(1024)
                if not data:
                    break
                message = json.loads(data.decode())
                self.broadcast(message, exclude=client_id)
            except:
                break
        self.remove_client(client_id)

    def broadcast(self, message, exclude=None):
        """Send message to all clients except the excluded one"""
        for cid, client in self.clients.items():
            if cid != exclude:
                try:
                    client['socket'].send(json.dumps(message).encode())
                except:
                    self.remove_client(cid)

    def remove_client(self, client_id):
        """Remove a disconnected client"""
        if client_id in self.clients:
            try:
                self.clients[client_id]['socket'].close()
            except:
                pass
            del self.clients[client_id]
            print(f"Client {client_id} disconnected")

    def connect_to_server(self):
        """Connect to the game server"""
        try:
            self.socket.connect((self.server_ip, 5000))
            self.client_id = str(uuid.uuid4())[:8]
            threading.Thread(target=self.receive_messages).start()
            return True
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            return False

    def receive_messages(self):
        """Receive messages from the server"""
        while self.running:
            try:
                data = self.socket.recv(1024)
                if not data:
                    break
                message = json.loads(data.decode())
                self.handle_server_message(message)
            except:
                break
        self.disconnect()

    def handle_server_message(self, message):
        """Handle incoming server messages"""
        if 'type' in message:
            if message['type'] == 'player_join':
                self.game.add_remote_player(message['player_id'], message['player_data'])
            elif message['type'] == 'player_update':
                self.game.update_remote_player(message['player_id'], message['player_data'])
            elif message['type'] == 'player_leave':
                self.game.remove_remote_player(message['player_id'])

    def send_message(self, message_type, data):
        """Send a message to the server"""
        if not self.is_server and self.socket:
            try:
                message = {
                    'type': message_type,
                    'client_id': self.client_id,
                    'data': data
                }
                self.socket.send(json.dumps(message).encode())
            except:
                self.disconnect()

    def disconnect(self):
        """Disconnect from the server"""
        self.running = False
        try:
            self.socket.close()
        except:
            pass

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
        self.invincible_duration = 2.0  # 2 seconds of invincibility after hit
        self.blink_timer = 0
        self.blink_interval = 0.1  # Blink every 0.1 seconds
        self.visible = True
        self.engine_particles = []
        self.active_powerups = {}
        self.time_slow_factor = 1.0
        self.controls = controls
        self.color = color
        self.name = name
        self.id = player_id
        self.last_update = time.time()
        self.shield_radius = 0
        self.shield_growing = True
        self.trail_particles = []
        self.last_trail_time = 0
        self.trail_interval = 0.1  # seconds between trail particles
        self.powerups_remaining = 3  # Limit of 3 powerups per player

    def get_state(self):
        return {
            'id': self.id,
            'x': self.rect.x,
            'y': self.rect.y,
            'score': self.score,
            'lives': self.lives,
            'active_powerups': self.active_powerups,
            'invincible': self.invincible,
            'powerups_remaining': self.powerups_remaining
        }

    def update_from_state(self, state):
        self.rect.x = state['x']
        self.rect.y = state['y']
        self.score = state['score']
        self.lives = state['lives']
        self.active_powerups = state['active_powerups']
        self.invincible = state['invincible']
        if 'powerups_remaining' in state:
            self.powerups_remaining = state['powerups_remaining']

    def activate_powerup(self, powerup_type):
        # Check if player has powerups remaining
        if self.powerups_remaining <= 0:
            return False  # Cannot activate powerup
            
        self.active_powerups[powerup_type] = time.time()
        self.powerups_remaining -= 1  # Decrement remaining powerups
        
        if powerup_type == 'speed':
            self.speed = self.base_speed * 2
        elif powerup_type == 'shield':
            self.invincible = True
        elif powerup_type == 'time_slow':
            self.time_slow_factor = 0.5
            
        return True  # Successfully activated powerup

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
            if self.powerups_remaining > 0:  # Only activate if powerups remaining
                self.activate_powerup(random.choice(['speed', 'shield', 'time_slow']))

        self.update_powerups()

    def update(self):
        # Update invincibility
        if self.invincible:
            current_time = time.time()
            if current_time - self.invincible_timer >= self.invincible_duration:
                self.invincible = False
            else:
                # Blink effect
                self.blink_timer += 1
                if self.blink_timer >= self.blink_interval * FPS:
                    self.visible = not self.visible
                    self.blink_timer = 0

    def draw(self):
        if not self.visible and self.invincible:
            return  # Skip drawing during blink when invincible
        # Draw engine trail
        current_time = time.time()
        if current_time - self.last_trail_time >= self.trail_interval:
            self.trail_particles.append([self.rect.centerx, self.rect.bottom, 5])
            self.last_trail_time = current_time

        # Update and draw trail particles
        for particle in self.trail_particles[:]:
            particle[1] += 2
            particle[2] -= 0.2
            if particle[2] <= 0:
                self.trail_particles.remove(particle)
            else:
                alpha = int(255 * (particle[2] / 5))
                trail_surface = pygame.Surface((4, 4), pygame.SRCALPHA)
                pygame.draw.circle(trail_surface, (*self.color, alpha), (2, 2), particle[2])
                screen.blit(trail_surface, (particle[0] - 2, particle[1] - 2))

        # Draw shield effect
        if self.invincible:
            if self.shield_growing:
                self.shield_radius += 1
                if self.shield_radius >= 30:
                    self.shield_growing = False
            else:
                self.shield_radius -= 1
                if self.shield_radius <= 20:
                    self.shield_growing = True

            shield_surface = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.circle(shield_surface, (*CYAN, 128), (30, 30), self.shield_radius, 2)
            screen.blit(shield_surface, (self.rect.centerx - 30, self.rect.centery - 30))

        # Draw spaceship with better visuals
        ship_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Draw main body
        points = [
            (self.width//2, 0),  # Nose
            (self.width, self.height),  # Bottom right
            (self.width//2, self.height - 10),  # Bottom center
            (0, self.height)  # Bottom left
        ]
        pygame.draw.polygon(ship_surface, self.color, points)
        
        # Draw cockpit
        pygame.draw.ellipse(ship_surface, (200, 200, 255), 
                          (self.width//2 - 10, 5, 20, 15))
        
        # Draw engine glow
        if random.random() < 0.3:
            glow_points = [
                (self.width//2 - 5, self.height - 5),
                (self.width//2 + 5, self.height - 5),
                (self.width//2, self.height + 10)
            ]
            pygame.draw.polygon(ship_surface, (255, 165, 0), glow_points)
        
        # Draw details
        pygame.draw.line(ship_surface, (255, 255, 255), 
                        (self.width//2 - 5, 5), (self.width//2 - 5, 15), 2)
        pygame.draw.line(ship_surface, (255, 255, 255), 
                        (self.width//2 + 5, 5), (self.width//2 + 5, 15), 2)
        
        screen.blit(ship_surface, self.rect)

        # Draw player name with better styling
        name_surface = pygame.Surface((100, 30), pygame.SRCALPHA)
        pygame.draw.rect(name_surface, (*BLACK, 128), (0, 0, 100, 30), border_radius=5)
        name_text = game.small_font.render(self.name, True, WHITE)
        name_surface.blit(name_text, (5, 5))
        screen.blit(name_surface, (self.rect.centerx - 50, self.rect.top - 35))

class Game:
    def __init__(self):
        self.reset_game()
    
    def reset_game(self):
        """Reset the game to initial state with menu active"""
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
        self.menu_active = True  # Ensure menu is active at start
        self.menu_options = ["Start Server", "Join Server", "Exit"]
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
        self.server = None
        self.is_hosting = False
        self.max_lives = 3
        self.life_icons = []  # Store life icon positions and states
        self.last_obstacle_spawn = 0
        self.obstacle_spawn_interval = 1.0  # seconds between obstacle spawns
        self.last_powerup_spawn = 0
        self.powerup_spawn_interval = 5.0  # seconds between powerup spawns
        self.running = True
        self.clock = pygame.time.Clock()
        self.level = 1
        self.score_for_next_level = 1000  # Score needed to advance to next level

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
                        self.reset_game()  # Use reset_game instead of __init__
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
        
        # Draw stars in background
        for star in self.stars:
            star.move()
            star.draw()

        title = self.font.render("SPACE RUN", True, WHITE)
        subtitle = self.small_font.render("Multiplayer Space Racing", True, WHITE)
        screen.blit(title, (WINDOW_WIDTH/2 - 100, 100))
        screen.blit(subtitle, (WINDOW_WIDTH/2 - 150, 150))

        # Draw player name input
        name_label = self.small_font.render("YOUR NAME:", True, WHITE)
        name_box = pygame.Rect(WINDOW_WIDTH/2 - 100, 200, 200, 40)
        pygame.draw.rect(screen, GREEN if self.inputting_name else WHITE, name_box, 2)
        name_text = self.font.render(self.player_name, True, GREEN if self.inputting_name else WHITE)
        screen.blit(name_label, (WINDOW_WIDTH/2 - 200, 210))
        screen.blit(name_text, (WINDOW_WIDTH/2 - 90, 210))

        # Draw menu options
        menu_options = ["Start Server", "Join Server", "Exit"]
        for i, option in enumerate(menu_options):
            color = GREEN if i == self.selected_option else WHITE
            text = self.font.render(option, True, color)
            screen.blit(text, (WINDOW_WIDTH/2 - 100, 300 + i * 50))

        # Draw server IP input
        if self.selected_option == 1:  # Join Server
            ip_label = self.small_font.render("SERVER IP:", True, WHITE)
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
                        self.selected_option = (self.selected_option - 1) % 3
                    elif event.key == pygame.K_DOWN:
                        self.selected_option = (self.selected_option + 1) % 3
                    elif event.key == pygame.K_RETURN:
                        if self.selected_option == 0:  # Start Server
                            self.server = NetworkManager(is_server=True)
                            if self.server.start_server():
                                self.is_hosting = True
                                self.player = Player(
                                    WINDOW_WIDTH // 2,
                                    {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'powerup': pygame.K_p},
                                    BLUE,
                                    self.player_name,
                                    "host"
                                )
                                self.menu_active = False
                        elif self.selected_option == 1:  # Join Server
                            if self.host_ip:
                                self.network = NetworkManager(is_server=False, server_ip=self.host_ip)
                                if self.network.connect_to_server():
                                    self.player = Player(
                                        WINDOW_WIDTH // 2,
                                        {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'powerup': pygame.K_p},
                                        RED,
                                        self.player_name,
                                        "client"
                                    )
                                    self.menu_active = False
                        elif self.selected_option == 2:  # Exit
                            return False
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
            powerup = PowerUp()
            # 20% chance for a refill powerup at higher levels
            if random.random() < 0.2 and self.level > 1:
                powerup.type = 'refill'
                powerup.colors['refill'] = PURPLE
            self.powerups.append(powerup)

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
        """Draw life icons with better visuals"""
        for i in range(3):  # Always show 3 life slots
            x = x_offset + i * 30
            y = 10
            # Draw life icon background
            pygame.draw.circle(screen, (50, 50, 50), (x + 15, y + 15), 12)
            # Draw life icon
            if i < player.lives:
                # Draw filled heart for active lives
                points = [
                    (x + 15, y + 5),  # Top point
                    (x + 5, y + 15),  # Left point
                    (x + 15, y + 25),  # Bottom point
                    (x + 25, y + 15)   # Right point
                ]
                pygame.draw.polygon(screen, player.color, points)
                # Add shine effect
                pygame.draw.circle(screen, (255, 255, 255, 128), (x + 18, y + 8), 3)
            else:
                # Draw empty heart for lost lives
                points = [
                    (x + 15, y + 5),
                    (x + 5, y + 15),
                    (x + 15, y + 25),
                    (x + 25, y + 15)
                ]
                pygame.draw.polygon(screen, (100, 100, 100), points, 2)

    def draw_score(self, player, x_offset):
        """Draw score with better visuals"""
        # Draw score background
        score_bg = pygame.Rect(x_offset, 40, 150, 30)
        pygame.draw.rect(screen, (50, 50, 50), score_bg, border_radius=5)
        # Draw score text
        score_text = self.small_font.render(f"{player.name}: {player.score}", True, WHITE)
        screen.blit(score_text, (x_offset + 10, 45))

    def draw_powerups(self, player, y_pos):
        """Draw powerups with better visuals"""
        # First draw the powerups remaining indicator
        powerup_count_bg = pygame.Rect(10, y_pos - 30, 150, 25)
        pygame.draw.rect(screen, (50, 50, 50), powerup_count_bg, border_radius=5)
        
        # Create a visual indicator for powerups remaining
        for i in range(3):  # Total slots
            x_pos = 25 + i * 25
            if i < player.powerups_remaining:
                # Draw filled circle for available powerups
                pygame.draw.circle(screen, GREEN, (x_pos, y_pos - 18), 8)
            else:
                # Draw empty circle for used powerups
                pygame.draw.circle(screen, (100, 100, 100), (x_pos, y_pos - 18), 8, 2)
        
        # Draw "POWER-UPS:" text
        count_text = self.small_font.render("POWER-UPS:", True, WHITE)
        screen.blit(count_text, (85, y_pos - 25))
        
        # Draw active powerups
        for i, powerup_type in enumerate(player.active_powerups):
            remaining_time = POWERUP_DURATION - (time.time() - player.active_powerups[powerup_type])
            # Draw powerup background
            powerup_bg = pygame.Rect(10, y_pos + i * 30, 150, 25)
            pygame.draw.rect(screen, (50, 50, 50), powerup_bg, border_radius=5)
            # Draw powerup icon
            icon_color = {
                'speed': GREEN,
                'shield': CYAN,
                'time_slow': ORANGE
            }[powerup_type]
            pygame.draw.circle(screen, icon_color, (25, y_pos + i * 30 + 12), 8)
            # Draw powerup text
            powerup_text = self.small_font.render(f"{powerup_type}: {remaining_time:.1f}s", True, WHITE)
            screen.blit(powerup_text, (40, y_pos + i * 30 + 5))

    def run(self):
        running = True
        while running:
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

            # Update game state
            if not self.showing_story and not self.game_over:
                current_time = time.time()

                # Update local player
                if self.player:
                    self.player.move()
                    self.player.update_powerups()
                    self.player.update()
                    if self.network and not self.is_hosting:
                        self.network.send_message('player_update', self.player.get_state())

                # Update other players
                for player_id, player in self.other_players.items():
                    player.move()
                    player.update_powerups()
                    player.update()

                # Spawn obstacles with proper timing
                if current_time - self.last_obstacle_spawn >= self.obstacle_spawn_interval:
                    self.spawn_obstacle()
                    self.last_obstacle_spawn = current_time

                # Spawn powerups with proper timing
                if current_time - self.last_powerup_spawn >= self.powerup_spawn_interval:
                    self.spawn_powerup()
                    self.last_powerup_spawn = current_time

                # Update obstacles and powerups
                for obstacle in self.obstacles[:]:
                    obstacle.move()
                    if self.player and obstacle.rect.colliderect(self.player.rect):
                        if not self.player.invincible:
                            self.player.lives -= 1
                            self.player.invincible = True
                            self.player.invincible_timer = time.time()
                            if self.player.lives <= 0:
                                self.game_over = True
                        self.obstacles.remove(obstacle)
                    else:
                        for player_id, player in self.other_players.items():
                            if obstacle.rect.colliderect(player.rect):
                                if not player.invincible:
                                    player.lives -= 1
                                    player.invincible = True
                                    player.invincible_timer = time.time()
                                self.obstacles.remove(obstacle)
                                break

                for powerup in self.powerups[:]:
                    powerup.move()
                    if self.player and powerup.rect.colliderect(self.player.rect):
                        self.player.activate_powerup(powerup.type)
                        self.powerups.remove(powerup)
                    else:
                        for player_id, player in self.other_players.items():
                            if powerup.rect.colliderect(player.rect):
                                player.activate_powerup(powerup.type)
                                self.powerups.remove(powerup)
                                break

            # Check score for level up and power-up refresh
            if self.player and self.player.score >= self.score_for_next_level:
                self.level += 1
                self.score_for_next_level += 1000 * self.level  # Increase score needed for next level
                self.player.powerups_remaining = 3  # Refresh powerups when leveling up
                
                # Create level up message
                level_up_text = self.font.render(f"LEVEL UP! POWER-UPS REFRESHED!", True, GREEN)
                screen.blit(level_up_text, (WINDOW_WIDTH//2 - 200, 100))
                pygame.display.flip()
                pygame.time.delay(1000)  # Show message for 1 second

            # Draw everything
            screen.fill(BLACK)
            
            # Draw stars
            for star in self.stars:
                star.move()
                star.draw()

            if self.showing_story:
                self.handle_story()
            elif self.game_over:
                self.show_game_over()
            elif self.paused:
                self.show_pause_menu()
            else:
                # Draw game elements
                for obstacle in self.obstacles:
                    obstacle.draw()
                for powerup in self.powerups:
                    powerup.draw()
                if self.player:
                    self.player.draw()
                    self.draw_lives(self.player, 10)
                    self.draw_score(self.player, 10)
                    self.draw_powerups(self.player, 70)
                for player_id, player in self.other_players.items():
                    player.draw()
                    self.draw_lives(player, 10 + 300)
                    self.draw_score(player, 10 + 300)
                    self.draw_powerups(player, 70 + 300)

            pygame.display.flip()
            self.clock.tick(FPS)  # Maintain consistent frame rate

    def show_game_over(self):
        """Display the game over screen"""
        game_over_text = self.font.render("GAME OVER", True, RED)
        score_text = self.font.render(f"Final Score: {self.player.score}", True, WHITE)
        restart_text = self.font.render("Press SPACE to restart", True, WHITE)
        
        screen.blit(game_over_text, (WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 - 50))
        screen.blit(score_text, (WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2))
        screen.blit(restart_text, (WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2 + 50))

if __name__ == "__main__":
    game = Game()
    game.run()