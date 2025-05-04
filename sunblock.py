import pygame
import sys
import math
import random

# Initialize Pygame
pygame.init()

# Game constants (reduced by 25%)
WINDOW_WIDTH = 600  # Was 800
WINDOW_HEIGHT = 750  # Was 1000
TITLE = "Sunblock"
FPS = 60

# Enhanced color definitions
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (150, 150, 150)
NEON_PINK = (255, 20, 147)
NEON_BLUE = (0, 191, 255)
NEON_YELLOW = (255, 255, 0)
NEON_CYAN = (0, 255, 255)
NEON_GREEN = (57, 255, 20)  # New color for selected items
NEON_RED = (255, 0, 60)     # Add this new color for game over screen

# Add new constants for the game
# Ship dimensions (reduced by 25%)
SHIP_WIDTH = 45  # Was 60
SHIP_HEIGHT = 60  # Was 80

# Add new colors for the ship
SHIP_BLUE = (30, 144, 255)
SHIP_GRAY = (169, 169, 169)
SHIP_DETAIL = (100, 100, 100)

# Ship movement constants (adjusted for new scale)
SHIP_SPEED = 6.0  # Was 8.0
SHIP_ACCELERATION = 0.375  # Was 0.5
SHIP_FRICTION = 0.92  # Slows ship when not accelerating (0-1)
SHIP_MIN_SPEED = 0.075  # Was 0.1

# Bullet constants (reduced by 25%)
BULLET_WIDTH = 3  # Was 4
BULLET_HEIGHT = 9  # Was 12
BULLET_SPEED = 11  # Was 15
BULLET_COLOR = NEON_CYAN

# Add these constants after the bullet constants
INITIAL_AMMO = 500
MAX_FIRE_RATE = 0.05  # Minimum time between shots (fastest)
MIN_FIRE_RATE = 0.25  # Maximum time between shots (slowest)
FIRE_RATE_DECAY = 1.1  # How quickly fire rate slows down
FIRE_RATE_RECOVERY = 0.95  # How quickly fire rate recovers

# Add new constants after existing ones
ENEMY_WIDTH = 50
ENEMY_HEIGHT = 30
ENEMY_SPEED = 3
ENEMY_SPAWN_RATE = 2.0  # Increased slightly to space out spawns
SCORE_PER_KILL = 10
PLAYER_LIVES = 3
POWERUP_DURATION = 5.0  # Seconds
SPRAY_BULLET_COUNT = 3
SPRAY_ANGLE = 15  # Degrees between spray bullets

# Add new constants for enemy behavior and ammo crates
ENEMY_HORIZONTAL_SPEED = 2.0
ENEMY_DIRECTION_CHANGE_TIME = 1.5  # Seconds between direction changes
MAX_ENEMIES = 8  # Reduced to ensure screen doesn't get too crowded
AMMO_CRATE_SIZE = 20
AMMO_CRATE_SPEED = 2
AMMO_CRATE_SPAWN_RATE = 15.0  # Seconds between crate spawns

# Add after existing enemy constants
LARGE_ENEMY_WIDTH = 90  # Increased from 80
LARGE_ENEMY_HEIGHT = 60  # Increased from 50
LARGE_ENEMY_SPEED = 1.2  # Slightly slower
LARGE_ENEMY_HEALTH = 3
LARGE_ENEMY_SCORE = 50  # Increased score reward from 30
SCORE_PENALTY = 100
ENEMY_TYPE_THRESHOLD = 0.7  # Reduced from 0.87 - now 70% normal enemies, 30% large enemies
HIGHSCORE_FILE = "highscores.txt"
MULTI_SPAWN_CHANCE = 0.3  # 30% chance to spawn multiple enemies

# Menu constants
MENU_OPTIONS = ["Start Game", "Quit"]
selected_option = 0
SELECTION_ARROW = "→"  # Arrow indicator for selected item

# Add these constants at the top with other menu constants
GAME_OVER_OPTIONS = ["Play Again", "Quit to Menu"]
game_over_selected = 0

# Add new constants for background
STAR_COUNT = 100
PLANET_COUNT = 3
BG_COLORS = [
    (30, 30, 40),    # Dark blue-gray
    (40, 25, 35),    # Dark purple
    (35, 35, 45)     # Dark slate
]

def create_background():
    """Create a static background surface with stars and planets"""
    background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    background.fill(BLACK)
    
    # Draw stars
    for _ in range(STAR_COUNT):
        x = random.randint(0, WINDOW_WIDTH)
        y = random.randint(0, WINDOW_HEIGHT)
        radius = random.randint(1, 2)
        alpha = random.randint(30, 128)
        
        star_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(star_surface, (*GRAY, alpha), (radius, radius), radius)
        background.blit(star_surface, (x, y))
    
    # Draw planets
    for _ in range(PLANET_COUNT):
        x = random.randint(0, WINDOW_WIDTH)
        y = random.randint(0, WINDOW_HEIGHT)
        radius = random.randint(20, 50)
        color = random.choice(BG_COLORS)
        
        # Draw planet with gradient effect
        for r in range(radius, 0, -1):
            alpha = 128 if r == radius else max(30, 128 - (radius - r) * 3)
            planet_surface = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(planet_surface, (*color, alpha), (r, r), r)
            background.blit(planet_surface, (x + radius - r, y + radius - r))
    
    return background

# Set up the game window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption(TITLE)

# Initialize fonts for text rendering
try:
    # Try to load a more cyberpunk-style font if available
    title_font = pygame.font.Font("arial", 60)  # Was 80
except:
    title_font = pygame.font.Font(None, 60)  # Was 80
menu_font = pygame.font.Font(None, 38)  # Was 50

def create_glowing_text(text, font, glow_color, main_color, glow_size=6, offset_3d=4):
    """
    Creates text with an intense glowing effect and 3D depth
    """
    glow_surfaces = []
    # Create more layers for intense glow
    for i in range(glow_size, 0, -1):
        size = i * 3  # Increased size multiplier
        glow_surface = font.render(text, True, glow_color)
        glow_surface = pygame.transform.scale(
            glow_surface,
            (glow_surface.get_width() + size, glow_surface.get_height() + size)
        )
        glow_surfaces.append(glow_surface)
    
    # Create 3D effect layers
    shadow_layers = []
    for i in range(offset_3d):
        shadow = font.render(text, True, (50, 50, 50))
        shadow_layers.append(shadow)
    
    main_surface = font.render(text, True, main_color)
    return glow_surfaces, shadow_layers, main_surface

def draw_menu_option(text, position, selected):
    """
    Draws a menu option with clear visual feedback for selection
    """
    # Define colors based on selection state
    text_color = NEON_GREEN if selected else NEON_YELLOW
    glow_size = 4 if selected else 2
    
    # Create the text surfaces
    glow_surfaces, _, text_surface = create_glowing_text(
        text,
        menu_font,
        text_color,
        WHITE,
        glow_size=glow_size
    )
    
    # Draw static glow effect
    for surface in glow_surfaces:
        surface.set_alpha(255 if selected else 128)  # Full opacity when selected
        rect = surface.get_rect(center=position)
        screen.blit(surface, rect)
    
    # Draw main text
    text_rect = text_surface.get_rect(center=position)
    screen.blit(text_surface, text_rect)
    
    # Draw selection arrow if selected
    if selected:
        arrow_surface = menu_font.render(SELECTION_ARROW, True, NEON_GREEN)
        arrow_rect = arrow_surface.get_rect(
            midright=(text_rect.left - 20, text_rect.centery)
        )
        screen.blit(arrow_surface, arrow_rect)
    
    return text_rect

def draw_menu():
    """
    Draws the cyberpunk-styled menu interface
    """
    current_time = pygame.time.get_ticks()
    glow_intensity = (math.sin(current_time * 0.003) + 1) * 0.5
    
    # Create enhanced glowing title with pulsing effect
    glow_surfaces, shadow_layers, main_surface = create_glowing_text(
        TITLE,
        title_font,
        NEON_BLUE,
        NEON_PINK,
        glow_size=8,
        offset_3d=6
    )
    
    # Calculate positions
    title_x = WINDOW_WIDTH // 2
    title_y = WINDOW_HEIGHT // 4
    
    # Draw 3D shadow layers for title
    for i, shadow in enumerate(shadow_layers):
        offset = i * 2
        rect = shadow.get_rect(center=(title_x + offset, title_y + offset))
        screen.blit(shadow, rect)
    
    # Draw pulsing glow layers for title only
    for i, surface in enumerate(glow_surfaces):
        alpha = int(255 * glow_intensity * (i / len(glow_surfaces)))
        surface.set_alpha(alpha)
        rect = surface.get_rect(center=(title_x, title_y))
        screen.blit(surface, rect)
    
    # Draw main title
    main_rect = main_surface.get_rect(center=(title_x, title_y))
    screen.blit(main_surface, main_rect)
    
    # Draw menu options
    menu_rects = []
    for i, option in enumerate(MENU_OPTIONS):
        pos = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + i * 100)
        rect = draw_menu_option(option, pos, i == selected_option)
        menu_rects.append(rect)
    
    return menu_rects

class Bullet:
    def __init__(self, x, y, angle=0):
        self.x = x
        self.y = y
        self.width = BULLET_WIDTH
        self.height = BULLET_HEIGHT
        self.speed = BULLET_SPEED
        self.angle = angle
    
    def move(self):
        """Move bullet upward"""
        self.y -= self.speed * math.cos(math.radians(self.angle))
        self.x += self.speed * math.sin(math.radians(self.angle))
    
    def draw(self, screen):
        """Draw bullet on screen"""
        # Enhanced bullet design
        # Main bullet body
        pygame.draw.rect(screen, BULLET_COLOR,
                        (self.x - self.width//2, 
                         self.y - self.height//2,
                         self.width, 
                         self.height))
        
        # Glowing trail
        trail_length = 3
        for i in range(trail_length):
            alpha = 255 - (i * 85)
            trail_surface = pygame.Surface((self.width, self.height))
            trail_surface.fill(BULLET_COLOR)
            trail_surface.set_alpha(alpha)
            screen.blit(trail_surface,
                       (self.x - self.width//2,
                        self.y - self.height//2 + (i * 4)))
    
    def is_off_screen(self):
        """Check if bullet has moved off screen"""
        return self.y < -self.height or self.x < -self.width or self.x > WINDOW_WIDTH

    def get_rect(self):
        return pygame.Rect(self.x - self.width//2, self.y - self.height//2, self.width, self.height)

class Enemy:
    def __init__(self):
        self.x = random.randint(ENEMY_WIDTH, WINDOW_WIDTH - ENEMY_WIDTH)
        self.y = -ENEMY_HEIGHT
        self.width = ENEMY_WIDTH
        self.height = ENEMY_HEIGHT
        self.speed = ENEMY_SPEED
        self.exploding = False
        self.explosion_frame = 0
        self.explosion_max_frames = 8
        self.direction = random.choice([-1, 1])
        self.direction_change_time = random.uniform(0, ENEMY_DIRECTION_CHANGE_TIME)
        self.last_direction_change = 0
    
    def move(self):
        self.y += self.speed
        self.x += ENEMY_HORIZONTAL_SPEED * self.direction
        
        # Keep within screen bounds
        if self.x < ENEMY_WIDTH//2:
            self.x = ENEMY_WIDTH//2
            self.direction = 1
        elif self.x > WINDOW_WIDTH - ENEMY_WIDTH//2:
            self.x = WINDOW_WIDTH - ENEMY_WIDTH//2
            self.direction = -1
        
        # Random direction changes
        current_time = pygame.time.get_ticks() / 1000.0
        if current_time - self.last_direction_change > self.direction_change_time:
            self.direction *= -1 if random.random() < 0.7 else 1
            self.last_direction_change = current_time
            self.direction_change_time = random.uniform(0.5, ENEMY_DIRECTION_CHANGE_TIME)
    
    def draw(self, screen):
        if self.exploding:
            # Enhanced explosion animation
            radius = (self.explosion_frame / self.explosion_max_frames) * ENEMY_WIDTH
            for i in range(3):  # Multiple circles for better effect
                color = (NEON_PINK[0], 
                        max(0, NEON_PINK[1] - self.explosion_frame * 20),
                        max(0, NEON_PINK[2] - self.explosion_frame * 20))
                pygame.draw.circle(screen, color, 
                                 (int(self.x), int(self.y)), 
                                 int(radius - i * 5))
            self.explosion_frame += 1
        else:
            # Enhanced enemy ship design
            # Main body
            pygame.draw.ellipse(screen, NEON_PINK, 
                              (self.x - ENEMY_WIDTH//2, self.y - ENEMY_HEIGHT//2,
                               ENEMY_WIDTH, ENEMY_HEIGHT))
            
            # Cockpit
            pygame.draw.ellipse(screen, NEON_BLUE,
                              (self.x - ENEMY_WIDTH//4, self.y - ENEMY_HEIGHT//4,
                               ENEMY_WIDTH//2, ENEMY_HEIGHT//2))
            
            # Engine glow
            glow_radius = abs(math.sin(pygame.time.get_ticks() * 0.01)) * 5 + 5
            pygame.draw.circle(screen, NEON_CYAN,
                             (int(self.x), int(self.y + ENEMY_HEIGHT//3)),
                             int(glow_radius))
            
            # Detail lines
            pygame.draw.line(screen, NEON_PINK,
                           (self.x - ENEMY_WIDTH//2, self.y),
                           (self.x + ENEMY_WIDTH//2, self.y), 2)
    
    def collides_with(self, rect):
        return (abs(self.x - rect.centerx) < (ENEMY_WIDTH + rect.width)//2 and
                abs(self.y - rect.centery) < (ENEMY_HEIGHT + rect.height)//2)
    
    def is_finished_exploding(self):
        return self.exploding and self.explosion_frame >= self.explosion_max_frames

class LargeEnemy(Enemy):
    def __init__(self):
        super().__init__()
        self.width = LARGE_ENEMY_WIDTH
        self.height = LARGE_ENEMY_HEIGHT
        self.speed = LARGE_ENEMY_SPEED
        self.health = LARGE_ENEMY_HEALTH
        self.x = random.randint(LARGE_ENEMY_WIDTH, WINDOW_WIDTH - LARGE_ENEMY_WIDTH)
    
    def draw(self, screen):
        if self.exploding:
            # Enhanced explosion animation for large enemy
            radius = (self.explosion_frame / self.explosion_max_frames) * LARGE_ENEMY_WIDTH
            for i in range(4):  # More circles for bigger explosion
                color = (NEON_RED[0], 
                        max(0, NEON_RED[1] - self.explosion_frame * 20),
                        max(0, NEON_RED[2] - self.explosion_frame * 20))
                pygame.draw.circle(screen, color, 
                                 (int(self.x), int(self.y)), 
                                 int(radius - i * 8))
            self.explosion_frame += 1
        else:
            # Enhanced large enemy design
            # Main body
            pygame.draw.ellipse(screen, NEON_RED, 
                              (self.x - self.width//2, self.y - self.height//2,
                               self.width, self.height))
            
            # Multiple cockpits
            for i in range(3):
                offset = (i - 1) * (self.width//4)
                pygame.draw.ellipse(screen, NEON_BLUE,
                                  (self.x - self.width//6 + offset, 
                                   self.y - self.height//4,
                                   self.width//3, self.height//2))
            
            # Health bar
            health_width = (self.width * 0.8) * (self.health / LARGE_ENEMY_HEALTH)
            pygame.draw.rect(screen, NEON_GREEN,
                           (self.x - health_width//2, 
                            self.y - self.height//2 - 10,
                            health_width, 5))

class AmmoCrate:
    def __init__(self):
        self.width = AMMO_CRATE_SIZE
        self.height = AMMO_CRATE_SIZE
        self.x = random.randint(self.width, WINDOW_WIDTH - self.width)
        self.y = -self.height
        self.speed = AMMO_CRATE_SPEED
        self.rotation = 0
        self.rotation_speed = 2
    
    def move(self):
        self.y += self.speed
        self.rotation = (self.rotation + self.rotation_speed) % 360
    
    def draw(self, screen):
        # Draw base crate
        crate_rect = pygame.Rect(
            self.x - self.width//2,
            self.y - self.height//2,
            self.width,
            self.height
        )
        pygame.draw.rect(screen, NEON_YELLOW, crate_rect, 2)
        
        # Draw diagonal cross
        pygame.draw.line(screen, NEON_YELLOW,
                        (self.x - self.width//2, self.y - self.height//2),
                        (self.x + self.width//2, self.y + self.height//2), 2)
        pygame.draw.line(screen, NEON_YELLOW,
                        (self.x - self.width//2, self.y + self.height//2),
                        (self.x + self.width//2, self.y - self.height//2), 2)
        
        # Draw ammo symbol
        pygame.draw.rect(screen, NEON_CYAN,
                        (self.x - 4, self.y - 6, 8, 12))
        
    def is_off_screen(self):
        return self.y > WINDOW_HEIGHT
    
    def get_rect(self):
        return pygame.Rect(self.x - self.width//2, self.y - self.height//2,
                         self.width, self.height)

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.ship_x = WINDOW_WIDTH // 2
        self.ship_y = WINDOW_HEIGHT - 75  # Was 100
        self.bullets = []
        # Add velocity for smooth movement
        self.ship_vel_x = 0.0
        
        # Add new attributes for bullet firing system
        self.ammo = INITIAL_AMMO
        self.last_shot_time = 0
        self.current_fire_rate = MAX_FIRE_RATE
        self.can_shoot = True

        self.enemies = []
        self.last_enemy_spawn = 0
        self.lives = PLAYER_LIVES
        self.score = 0
        self.powerup_active = False
        self.powerup_end_time = 0
        self.ammo_crates = []
        self.last_crate_spawn = 0
        self.score_penalty_flash = 0  # Timer for penalty flash
        self.penalty_message = ""
        self.background = create_background()

    def draw_spaceship(self):
        """Draw a detailed spaceship with multiple components"""
        # Main body
        points = [
            (self.ship_x, self.ship_y - SHIP_HEIGHT),  # Top
            (self.ship_x - SHIP_WIDTH//2, self.ship_y),  # Bottom left
            (self.ship_x + SHIP_WIDTH//2, self.ship_y)   # Bottom right
        ]
        pygame.draw.polygon(self.screen, SHIP_BLUE, points)
        
        # Engine glow
        engine_rect = pygame.Rect(
            self.ship_x - 11,  # Was 15
            self.ship_y - 4,   # Was 5
            22,                # Was 30
            7                  # Was 10
        )
        pygame.draw.rect(self.screen, NEON_CYAN, engine_rect)
        
        # Cockpit
        cockpit_points = [
            (self.ship_x, self.ship_y - SHIP_HEIGHT + 15),      # Was 20
            (self.ship_x - 7, self.ship_y - SHIP_HEIGHT + 30),  # Was 10, 40
            (self.ship_x + 7, self.ship_y - SHIP_HEIGHT + 30)   # Was 10, 40
        ]
        pygame.draw.polygon(self.screen, NEON_BLUE, cockpit_points)
        
        # Wing details
        pygame.draw.line(self.screen, SHIP_DETAIL,
                        (self.ship_x - SHIP_WIDTH//3, self.ship_y - SHIP_HEIGHT//3),
                        (self.ship_x - SHIP_WIDTH//2, self.ship_y),
                        3)
        pygame.draw.line(self.screen, SHIP_DETAIL,
                        (self.ship_x + SHIP_WIDTH//3, self.ship_y - SHIP_HEIGHT//3),
                        (self.ship_x + SHIP_WIDTH//2, self.ship_y),
                        3)
        
        # Armor plates
        pygame.draw.line(self.screen, SHIP_GRAY,
                        (self.ship_x - 15, self.ship_y - SHIP_HEIGHT//2),  # Was 20
                        (self.ship_x + 15, self.ship_y - SHIP_HEIGHT//2),  # Was 20
                        3)  # Was 4

    def spawn_enemy(self):
        current_time = pygame.time.get_ticks() / 1000.0
        if current_time - self.last_enemy_spawn >= ENEMY_SPAWN_RATE:
            if len(self.enemies) < MAX_ENEMIES:
                # Determine number of enemies to spawn
                spawn_count = 1
                if random.random() < MULTI_SPAWN_CHANCE:
                    spawn_count = random.randint(2, 3)
                
                # Spawn enemies
                for _ in range(spawn_count):
                    if len(self.enemies) < MAX_ENEMIES:
                        if random.random() < ENEMY_TYPE_THRESHOLD:
                            self.enemies.append(Enemy())
                        else:
                            self.enemies.append(LargeEnemy())
                
                self.last_enemy_spawn = current_time

    def spawn_ammo_crate(self):
        current_time = pygame.time.get_ticks() / 1000.0
        if current_time - self.last_crate_spawn >= AMMO_CRATE_SPAWN_RATE:
            self.ammo_crates.append(AmmoCrate())
            self.last_crate_spawn = current_time

    def shoot(self):
        if self.ammo > 0:
            if self.powerup_active:
                # Spray shot
                for angle in range(-SPRAY_ANGLE, SPRAY_ANGLE + 1, SPRAY_ANGLE):
                    bullet = Bullet(self.ship_x, self.ship_y - SHIP_HEIGHT, angle)
                    self.bullets.append(bullet)
                self.ammo -= SPRAY_BULLET_COUNT
            else:
                # Normal shot
                bullet = Bullet(self.ship_x, self.ship_y - SHIP_HEIGHT)
                self.bullets.append(bullet)
                self.ammo -= 1

    def check_powerup(self):
        if self.score > 0 and self.score % 100 == 0:
            self.powerup_active = True
            self.powerup_end_time = pygame.time.get_ticks() / 1000.0 + POWERUP_DURATION

    def update(self):
        """Update game state"""
        current_time = pygame.time.get_ticks() / 1000.0  # Convert to seconds
        keys = pygame.key.get_pressed()
        
        # Handle shooting mechanics
        if keys[pygame.K_SPACE] and self.can_shoot and self.ammo > 0:
            if current_time - self.last_shot_time >= self.current_fire_rate:
                self.shoot()
                self.last_shot_time = current_time
                # Increase time between shots (slow down fire rate)
                self.current_fire_rate *= FIRE_RATE_DECAY
                # Cap the fire rate at the minimum speed
                self.current_fire_rate = min(self.current_fire_rate, MIN_FIRE_RATE)
        elif not keys[pygame.K_SPACE]:
            # Recover fire rate when not shooting
            self.current_fire_rate *= FIRE_RATE_RECOVERY
            # Cap the recovery at the maximum speed
            self.current_fire_rate = max(self.current_fire_rate, MAX_FIRE_RATE)
        
        # Handle ship movement
        # Apply acceleration based on input
        if keys[pygame.K_LEFT]:
            self.ship_vel_x -= SHIP_ACCELERATION
        if keys[pygame.K_RIGHT]:
            self.ship_vel_x += SHIP_ACCELERATION
        
        # Apply friction to slow down when no input
        if not (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]):
            self.ship_vel_x *= SHIP_FRICTION
        
        # Clamp velocity to maximum speed
        self.ship_vel_x = max(-SHIP_SPEED, min(SHIP_SPEED, self.ship_vel_x))
        
        # Stop ship if moving very slowly
        if abs(self.ship_vel_x) < SHIP_MIN_SPEED:
            self.ship_vel_x = 0
        
        # Update ship position
        self.ship_x += self.ship_vel_x
        
        # Keep ship within screen bounds
        self.ship_x = max(SHIP_WIDTH//2, min(WINDOW_WIDTH - SHIP_WIDTH//2, self.ship_x))
        
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.move()
            if bullet.is_off_screen():
                self.bullets.remove(bullet)

        # Update powerup status
        current_time = pygame.time.get_ticks() / 1000.0
        if self.powerup_active and current_time > self.powerup_end_time:
            self.powerup_active = False
        
        # Spawn and update enemies
        self.spawn_enemy()
        for enemy in self.enemies[:]:
            enemy.move()
            
            # Check if enemy passed player
            if enemy.y > WINDOW_HEIGHT:
                self.score = max(0, self.score - SCORE_PENALTY)
                self.score_penalty_flash = 60  # Show penalty for 60 frames
                self.penalty_message = f"-{SCORE_PENALTY} points!"
                self.enemies.remove(enemy)
                continue
            
            # Check bullet collisions
            for bullet in self.bullets[:]:
                if enemy.collides_with(bullet.get_rect()):
                    self.bullets.remove(bullet)
                    if isinstance(enemy, LargeEnemy):
                        enemy.health -= 1
                        if enemy.health <= 0:
                            enemy.exploding = True
                            self.score += LARGE_ENEMY_SCORE
                    else:
                        enemy.exploding = True
                        self.score += SCORE_PER_KILL
                    self.check_powerup()
                    break
            
            # Check player collision
            if not enemy.exploding and enemy.collides_with(self.get_ship_rect()):
                enemy.exploding = True
                self.lives -= 1
                if self.lives <= 0:
                    self.running = False
            
            # Remove finished explosions and off-screen enemies
            if enemy.is_finished_exploding() or enemy.y > WINDOW_HEIGHT:
                self.enemies.remove(enemy)
        
        # Update ammo crates
        self.spawn_ammo_crate()
        for crate in self.ammo_crates[:]:
            crate.move()
            if crate.get_rect().colliderect(self.get_ship_rect()):
                self.ammo = INITIAL_AMMO
                self.ammo_crates.remove(crate)
            elif crate.is_off_screen():
                self.ammo_crates.remove(crate)
        
        # Update penalty flash
        if self.score_penalty_flash > 0:
            self.score_penalty_flash -= 1
    
    def draw_hud(self):
        # Draw score
        score_text = f"Score: {self.score}"
        self.draw_glowing_text(score_text, (20, 20), NEON_GREEN)
        
        # Draw lives
        for i in range(self.lives):
            mini_ship_points = [
                (WINDOW_WIDTH - 20 - (i * 25), 30),
                (WINDOW_WIDTH - 30 - (i * 25), 40),
                (WINDOW_WIDTH - 10 - (i * 25), 40)
            ]
            pygame.draw.polygon(self.screen, SHIP_BLUE, mini_ship_points)
        
        # Draw ammo counter
        self.draw_ammo_counter()
        
        # Draw powerup indicator
        if self.powerup_active:
            self.draw_glowing_text("POWER UP!", 
                                 (WINDOW_WIDTH//2, 50), 
                                 NEON_YELLOW)
        
        # Draw penalty message
        if self.score_penalty_flash > 0:
            alpha = min(255, self.score_penalty_flash * 4)
            font = pygame.font.Font(None, 48)
            penalty_surface = font.render(self.penalty_message, True, NEON_RED)
            penalty_surface.set_alpha(alpha)
            penalty_rect = penalty_surface.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            self.screen.blit(penalty_surface, penalty_rect)

    def draw_glowing_text(self, text, position, color):
        font = pygame.font.Font(None, 36)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(topleft=position)
        self.screen.blit(text_surface, text_rect)

    def draw_ammo_counter(self):
        """Draw ammo count in bottom right corner with glow effect"""
        font = pygame.font.Font(None, 36)
        ammo_text = f"Ammo: {self.ammo}"
        
        # Create glowing text effect
        glow_surfaces, _, main_surface = create_glowing_text(
            ammo_text,
            font,
            NEON_CYAN,
            WHITE,
            glow_size=3
        )
        
        # Position in bottom right
        pos = (WINDOW_WIDTH - 20, WINDOW_HEIGHT - 20)
        
        # Draw glow layers
        for surface in glow_surfaces:
            rect = surface.get_rect(bottomright=pos)
            self.screen.blit(surface, rect)
        
        # Draw main text
        rect = main_surface.get_rect(bottomright=pos)
        self.screen.blit(main_surface, rect)

    def draw(self):
        """Draw game state"""
        self.screen.blit(self.background, (0, 0))  # Draw background first
        self.draw_spaceship()
        
        for enemy in self.enemies:
            enemy.draw(self.screen)
        
        for bullet in self.bullets:
            bullet.draw(self.screen)
        
        for crate in self.ammo_crates:
            crate.draw(self.screen)
        
        self.draw_hud()
        pygame.display.flip()
    
    def get_ship_rect(self):
        return pygame.Rect(self.ship_x - SHIP_WIDTH//2, self.ship_y - SHIP_HEIGHT, SHIP_WIDTH, SHIP_HEIGHT)
    
    def run(self):
        """Main game loop"""
        clock = pygame.time.Clock()
        
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_SPACE:
                        self.shoot()
            
            self.update()
            self.draw()
            clock.tick(FPS)

def save_highscore(name, score):
    scores = []
    try:
        with open(HIGHSCORE_FILE, 'r') as f:
            for line in f:
                n, s = line.strip().split(',')
                scores.append((n, int(s)))
    except FileNotFoundError:
        pass
    
    scores.append((name, score))
    scores.sort(key=lambda x: x[1], reverse=True)
    scores = scores[:10]  # Keep top 10
    
    with open(HIGHSCORE_FILE, 'w') as f:
        for n, s in scores:
            f.write(f"{n},{s}\n")

def get_top_scores():
    """Get the top 3 high scores from the file"""
    scores = []
    try:
        with open(HIGHSCORE_FILE, 'r') as f:
            for line in f:
                n, s = line.strip().split(',')
                scores.append((n, int(s)))
    except FileNotFoundError:
        return []
    
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:3]

def draw_high_scores(screen, center_x, start_y):
    """Draw the top 3 high scores with better spacing"""
    scores = get_top_scores()
    if not scores:
        return
    
    # Draw header
    header_surfaces, _, header_main = create_glowing_text(
        "HIGH SCORES",
        menu_font,
        NEON_BLUE,
        WHITE,
        glow_size=3
    )
    
    # Header position (moved up)
    header_y = start_y - 100
    for surface in header_surfaces:
        rect = surface.get_rect(center=(center_x, header_y))
        screen.blit(surface, rect)
    
    # Draw scores with more spacing
    for i, (name, score) in enumerate(scores):
        score_text = f"#{i+1} {name}: {score}"
        color = NEON_PINK if i == 0 else (NEON_CYAN if i == 1 else NEON_YELLOW)
        
        score_surfaces, _, score_main = create_glowing_text(
            score_text,
            menu_font,
            color,
            WHITE,
            glow_size=2
        )
        
        # Increased vertical spacing between scores
        score_y = start_y - 40 + (i * 45)
        for surface in score_surfaces:
            rect = surface.get_rect(center=(center_x, score_y))
            screen.blit(surface, rect)

# Update the draw_game_over function to show high scores
def draw_game_over(screen, score):
    global game_over_selected
    running = True
    clock = pygame.time.Clock()
    name = ""
    entering_name = True
    
    while entering_name:
        screen.fill(BLACK)
        prompt_text = "Enter your name:"
        name_text = name + "_"
        
        # Draw prompt
        prompt_surfaces, _, prompt_main = create_glowing_text(
            prompt_text,
            menu_font,
            NEON_BLUE,
            WHITE,
            glow_size=3
        )
        
        # Draw current name
        name_surfaces, _, name_main = create_glowing_text(
            name_text,
            menu_font,
            NEON_GREEN,
            WHITE,
            glow_size=3
        )
        
        # Position text
        center_x = WINDOW_WIDTH // 2
        prompt_y = WINDOW_HEIGHT // 2 - 40
        name_y = WINDOW_HEIGHT // 2 + 20
        
        # Draw all text
        for surface in prompt_surfaces:
            rect = surface.get_rect(center=(center_x, prompt_y))
            screen.blit(surface, rect)
        
        for surface in name_surfaces:
            rect = surface.get_rect(center=(center_x, name_y))
            screen.blit(surface, rect)
        
        pygame.display.flip()
        
        # Handle input
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name:
                    entering_name = False
                    save_highscore(name, score)
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 15 and event.unicode.isalnum():
                    name += event.unicode
        
        clock.tick(FPS)
    
    while running:
        screen.fill(BLACK)
        
        # Create game over text
        game_over_text = "GAME OVER"
        score_text = f"Final Score: {score}"
        
        # Draw main "GAME OVER" text
        glow_surfaces, shadow_layers, main_surface = create_glowing_text(
            game_over_text,
            title_font,
            NEON_RED,
            NEON_PINK,
            glow_size=8,
            offset_3d=6
        )
        
        # Calculate positions
        center_x = WINDOW_WIDTH // 2
        center_y = WINDOW_HEIGHT // 4  # Moved up higher
        
        # Draw all layers for main text
        for shadow in shadow_layers:
            rect = shadow.get_rect(center=(center_x, center_y))
            screen.blit(shadow, rect)
        
        for surface in glow_surfaces:
            rect = surface.get_rect(center=(center_x, center_y))
            screen.blit(surface, rect)
        
        rect = main_surface.get_rect(center=(center_x, center_y))
        screen.blit(main_surface, rect)
        
        # Draw score
        score_surfaces, _, score_main = create_glowing_text(
            score_text,
            menu_font,
            NEON_GREEN,
            WHITE,
            glow_size=4
        )
        
        score_y = center_y + 100  # Increased spacing
        for surface in score_surfaces:
            rect = surface.get_rect(center=(center_x, score_y))
            screen.blit(surface, rect)
        
        rect = score_main.get_rect(center=(center_x, score_y))
        screen.blit(score_main, rect)
        
        # Draw high scores with more room
        draw_high_scores(screen, center_x, score_y + 80)
        
        # Move menu options down further
        menu_y = score_y + 250  # Increased spacing
        menu_rects = []
        for i, option in enumerate(GAME_OVER_OPTIONS):
            pos = (center_x, menu_y + i * 70)  # Increased menu option spacing
            rect = draw_menu_option(option, pos, i == game_over_selected)
            menu_rects.append(rect)
        
        pygame.display.flip()
        
        # Handle input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    game_over_selected = (game_over_selected - 1) % len(GAME_OVER_OPTIONS)
                elif event.key == pygame.K_DOWN:
                    game_over_selected = (game_over_selected + 1) % len(GAME_OVER_OPTIONS)
                elif event.key == pygame.K_RETURN:
                    return game_over_selected == 0  # Return True for restart, False for quit
            
            if event.type == pygame.MOUSEMOTION:
                for i, rect in enumerate(menu_rects):
                    if rect.collidepoint(event.pos):
                        game_over_selected = i
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if menu_rects[game_over_selected].collidepoint(event.pos):
                    return game_over_selected == 0  # Return True for restart, False for quit
        
        clock.tick(FPS)

# Update the main function's game state handling
def main():
    """Main program"""
    global selected_option
    clock = pygame.time.Clock()
    running = True
    game_state = "MENU"
    
    while running:
        if game_state == "MENU":
            screen.fill(BLACK)
            menu_rects = draw_menu()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_option = (selected_option - 1) % len(MENU_OPTIONS)
                    elif event.key == pygame.K_DOWN:
                        selected_option = (selected_option + 1) % len(MENU_OPTIONS)
                    elif event.key == pygame.K_RETURN:
                        if selected_option == 0:  # Start Game
                            game_state = "GAME"
                        elif selected_option == 1:  # Quit
                            running = False
                
                if event.type == pygame.MOUSEMOTION:
                    for i, rect in enumerate(menu_rects):
                        if rect.collidepoint(event.pos):
                            selected_option = i
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if menu_rects[selected_option].collidepoint(event.pos):
                        if selected_option == 0:  # Start Game
                            game_state = "GAME"
                        elif selected_option == 1:  # Quit
                            running = False
        
        elif game_state == "GAME":
            game = Game(screen)
            game.run()
            if draw_game_over(screen, game.score):
                game_state = "GAME"  # Restart game
            else:
                game_state = "MENU"  # Return to main menu
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()