import pygame
import math
import random

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GLIDER_SPEED = 3
MAX_BANK_ANGLE = 45
BANK_RATE = 2
TURN_RATE_SCALAR = 0.1 # How much bank affects turn rate
CONTRAIL_LENGTH = 60
CONTRAIL_POINT_DELAY = 2 # Add a point every N frames
THERMAL_SPAWN_BASE_RATE = 90 # Base chance to try spawning a thermal
THERMAL_LIFESPAN = 700 # Frames
THERMAL_RADIUS = 25
THERMAL_STRENGTH = 50

TILE_SIZE = 40 # Pixel size of each map tile
MAP_GRID_WIDTH = SCREEN_WIDTH // TILE_SIZE
MAP_GRID_HEIGHT = SCREEN_HEIGHT // TILE_SIZE

# --- Game States ---
STATE_START_SCREEN = 0
STATE_PLAYING = 1
STATE_GAME_OVER = 2 # Placeholder for future

# --- Colors ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_GRAY = (50, 50, 50)
GRAY = (150, 150, 150) # Contrail
LIGHT_GRAY = (200, 200, 200)

# Pastel Land Type Colors
COLOR_WATER = (173, 216, 230)  # Light Blue
COLOR_PLAINS = (170, 238, 170) # Pale Green (was 152, 251, 152)
COLOR_FOREST = (144, 200, 144) # Light Green (darker than plains)
COLOR_MOUNTAIN_BASE = (200, 200, 180) # Light Gray-Brownish (was 211,211,211)
COLOR_SAND = (245, 222, 179)    # Pale Yellow/Wheat (was 240,230,140)

# Glider Colors
GLIDER_BODY_COLOR = (80, 80, 220)
GLIDER_WING_COLOR = (120, 120, 255)

THERMAL_COLOR_PRIMARY = (255, 150, 150, 100) # Semi-transparent Red
THERMAL_COLOR_ACCENT = (255, 255, 255, 120) # Semi-transparent White

# --- Land Types ---
class LandType:
    WATER = 0
    PLAINS = 1
    FOREST = 2
    MOUNTAIN_BASE = 3
    SAND = 4

LAND_TYPE_COLORS = {
    LandType.WATER: COLOR_WATER,
    LandType.PLAINS: COLOR_PLAINS,
    LandType.FOREST: COLOR_FOREST,
    LandType.MOUNTAIN_BASE: COLOR_MOUNTAIN_BASE,
    LandType.SAND: COLOR_SAND,
}

# Probability of thermals spawning over this land type (0.0 to 1.0)
LAND_TYPE_THERMAL_PROBABILITY = {
    LandType.WATER: 0.01, # Very rare over water
    LandType.PLAINS: 0.7,
    LandType.FOREST: 0.4,
    LandType.MOUNTAIN_BASE: 0.6,
    LandType.SAND: 0.9,
}

# --- Glider Class ---
class Glider(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = pygame.Surface([50, 40], pygame.SRCALPHA) # Length 50, Wingspan 40
        # Fuselage (length 50, thickness 6, centered vertically)
        pygame.draw.rect(self.original_image, GLIDER_BODY_COLOR, (0, 17, 50, 6))
        # Main Wing (wingspan 40, chord 10, positioned mid-fuselage)
        pygame.draw.rect(self.original_image, GLIDER_WING_COLOR, (15, 0, 10, 40))
        # Tail Plane (Horizontal Stabilizer - span 20, chord 8, at rear)
        pygame.draw.rect(self.original_image, GLIDER_WING_COLOR, (0, 10, 8, 20))
        # Tail Fin (Vertical Stabilizer - height 10, on top rear fuselage)
        pygame.draw.polygon(self.original_image, GLIDER_BODY_COLOR, [(2, 17), (10, 17), (6, 7)])

        self.image = self.original_image
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

        self.x = float(self.rect.centerx)
        self.y = float(self.rect.centery)
        self.heading = 0
        self.bank_angle = 0
        self.height = 0
        self.trail_points = []
        self.contrail_frame_counter = 0
        self.glider_length = self.original_image.get_width() # Used for tail calculation

    def reset(self):
        self.x = float(SCREEN_WIDTH // 2)
        self.y = float(SCREEN_HEIGHT // 2)
        self.rect.center = (self.x, self.y)
        self.heading = 0
        self.bank_angle = 0
        self.height = 0
        self.trail_points = []
        self.contrail_frame_counter = 0
        self.image = pygame.transform.rotate(self.original_image, -self.heading) # Reset rotation

    def update(self, keys):
        if keys[pygame.K_LEFT]:
            self.bank_angle -= BANK_RATE
            self.bank_angle = max(self.bank_angle, -MAX_BANK_ANGLE)
        elif keys[pygame.K_RIGHT]:
            self.bank_angle += BANK_RATE
            self.bank_angle = min(self.bank_angle, MAX_BANK_ANGLE)
        else: # Auto-level
            self.bank_angle *= 0.95 # More gradual auto-leveling
            if abs(self.bank_angle) < 0.1 : self.bank_angle = 0


        turn_rate_degrees = self.bank_angle * TURN_RATE_SCALAR
        self.heading += turn_rate_degrees
        self.heading %= 360

        heading_rad = math.radians(self.heading)
        self.x += GLIDER_SPEED * math.cos(heading_rad)
        self.y += GLIDER_SPEED * math.sin(heading_rad)

        self.image = pygame.transform.rotate(self.original_image, -self.heading)
        self.rect = self.image.get_rect(center=(round(self.x), round(self.y)))

        # Contrail from tail
        self.contrail_frame_counter +=1
        if self.contrail_frame_counter >= CONTRAIL_POINT_DELAY:
            self.contrail_frame_counter = 0
            # Calculate tail position: center of glider minus half its length along its heading
            tail_offset_x = - (self.glider_length / 2 - 5) * math.cos(heading_rad) # Move it slightly forward from absolute tail
            tail_offset_y = - (self.glider_length / 2 - 5) * math.sin(heading_rad)
            self.trail_points.append((self.rect.centerx + tail_offset_x, self.rect.centery + tail_offset_y))
            if len(self.trail_points) > CONTRAIL_LENGTH:
                self.trail_points.pop(0)

        # Screen Wrap
        if self.x - self.rect.width/2 > SCREEN_WIDTH: self.x = -self.rect.width/2
        if self.x + self.rect.width/2 < 0: self.x = SCREEN_WIDTH + self.rect.width/2
        if self.y - self.rect.height/2 > SCREEN_HEIGHT: self.y = -self.rect.height/2
        if self.y + self.rect.height/2 < 0: self.y = SCREEN_HEIGHT + self.rect.height/2


    def draw_contrail(self, surface):
        if len(self.trail_points) > 1:
            for i, point in enumerate(self.trail_points):
                alpha = int(200 * (i / CONTRAIL_LENGTH)) # Max alpha 200 for softer trail
                temp_surface = pygame.Surface((4,4), pygame.SRCALPHA)
                pygame.draw.circle(temp_surface, (GRAY[0], GRAY[1], GRAY[2], alpha), (2,2), 2)
                surface.blit(temp_surface, (point[0]-2, point[1]-2))

# --- Thermal Class ---
class Thermal(pygame.sprite.Sprite):
    def __init__(self, center_pos):
        super().__init__()
        self.radius = THERMAL_RADIUS
        self.image = pygame.Surface([self.radius * 2, self.radius * 2], pygame.SRCALPHA)
        pygame.draw.circle(self.image, THERMAL_COLOR_PRIMARY, (self.radius, self.radius), self.radius)
        pygame.draw.circle(self.image, THERMAL_COLOR_ACCENT, (self.radius, self.radius), int(self.radius * 0.7), 2)
        self.rect = self.image.get_rect(center=center_pos)
        self.lifespan = THERMAL_LIFESPAN
        self.creation_time = pygame.time.get_ticks()

    def update(self):
        self.lifespan -= 1
        if self.lifespan <= 0:
            self.kill()

        # Pulsing animation
        pulse_alpha = (math.sin(pygame.time.get_ticks() * 0.005 + self.creation_time * 0.01) * 0.3 + 0.7) # Varies between 0.4 and 1.0
        alpha = int(100 * pulse_alpha * (self.lifespan / THERMAL_LIFESPAN)) # Fade out over lifespan
        
        current_radius_factor = math.sin(pygame.time.get_ticks() * 0.002 + self.creation_time * 0.005) * 0.1 + 0.95 # Scale factor 0.85 to 1.05
        current_radius = int(self.radius * current_radius_factor)

        self.image.fill((0,0,0,0))
        pygame.draw.circle(self.image, (*THERMAL_COLOR_PRIMARY[:3], alpha), (self.radius, self.radius), current_radius)
        pygame.draw.circle(self.image, (*THERMAL_COLOR_ACCENT[:3], int(alpha*1.2)), (self.radius, self.radius), int(current_radius * 0.7), 2)
        # Ensure rect is updated if size changes, though here radius of surface is fixed.
        # self.rect = self.image.get_rect(center=self.rect.center)


# --- Map Data & Functions ---
map_data = []

def generate_map():
    global map_data
    map_data = []
    # Define weights for land types to make some more common
    land_types = [LandType.WATER, LandType.PLAINS, LandType.FOREST, LandType.MOUNTAIN_BASE, LandType.SAND]
    weights =    [0.15,         0.35,         0.20,         0.15,              0.15] # Sum to 1.0

    for _ in range(MAP_GRID_HEIGHT):
        row = random.choices(land_types, weights=weights, k=MAP_GRID_WIDTH)
        map_data.append(row)

def get_land_type_at_pos(world_x, world_y):
    grid_x = int(world_x // TILE_SIZE)
    grid_y = int(world_y // TILE_SIZE)
    # Handle cases where glider might be slightly off-map due to screen wrap
    grid_x = max(0, min(grid_x, MAP_GRID_WIDTH - 1))
    grid_y = max(0, min(grid_y, MAP_GRID_HEIGHT - 1))
    return map_data[grid_y][grid_x]

def draw_map(surface):
    for r_idx, row in enumerate(map_data):
        for c_idx, tile_type in enumerate(row):
            color = LAND_TYPE_COLORS.get(tile_type, BLACK) # Default to black if type unknown
            rect = pygame.Rect(c_idx * TILE_SIZE, r_idx * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(surface, color, rect)

# --- Text Rendering Helper ---
def draw_text(surface, text, size, x, y, color=WHITE, font_name=None, center=False):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)

# --- Pygame Setup ---
pygame.init()
pygame.mixer.init() # For potential future sounds
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pastel Glider")
clock = pygame.time.Clock()

# --- Game Objects ---
player = Glider()
all_sprites = pygame.sprite.Group() # For drawing all sprites (player, thermals)
thermals_group = pygame.sprite.Group() # For thermal-specific logic and collisions
# Player is added to all_sprites when game starts/resets

# --- Game Variables ---
game_state = STATE_START_SCREEN
thermal_spawn_timer = 0
generate_map() # Generate initial map

# Function to reset game for retry
def reset_game_state():
    global thermal_spawn_timer
    player.reset()
    thermals_group.empty() # Clear existing thermals
    all_sprites.empty()    # Clear all sprites
    all_sprites.add(player)# Re-add player
    thermal_spawn_timer = 0
    # generate_map() # Optionally regenerate map on each retry

# --- Start Screen Function ---
def draw_start_screen_content(surface):
    surface.fill(DARK_GRAY)
    draw_text(surface, "Pastel Glider", 64, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4, COLOR_PLAINS, center=True)
    draw_text(surface, "Use LEFT and RIGHT arrow keys to bank and turn.", 28, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30, WHITE, center=True)
    draw_text(surface, "Fly through red thermals to gain height.", 28, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10, WHITE, center=True)
    draw_text(surface, "Press ENTER to Start", 36, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4, LIGHT_GRAY, center=True)
    draw_text(surface, "Press ESC during game to return to this screen.", 22, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4 + 50, GRAY, center=True)


# --- Game Loop ---
running = True
while running:
    dt = clock.tick(60) / 1000.0 # Delta time in seconds, not used yet but good practice

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if game_state == STATE_START_SCREEN:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    reset_game_state() # Prepare for new game
                    game_state = STATE_PLAYING
        elif game_state == STATE_PLAYING:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_state = STATE_START_SCREEN


    # --- Game State Logic ---
    if game_state == STATE_START_SCREEN:
        draw_start_screen_content(screen)

    elif game_state == STATE_PLAYING:
        keys = pygame.key.get_pressed()
        player.update(keys)
        thermals_group.update() # Thermals update themselves (lifespan, animation)

        # Spawn Thermals based on land type
        thermal_spawn_timer += 1
        if thermal_spawn_timer >= THERMAL_SPAWN_BASE_RATE:
            thermal_spawn_timer = 0
            # Try to spawn a thermal
            try_x = random.randint(0, SCREEN_WIDTH - 1)
            try_y = random.randint(0, SCREEN_HEIGHT - 1)
            land_type = get_land_type_at_pos(try_x, try_y)
            
            if random.random() < LAND_TYPE_THERMAL_PROBABILITY.get(land_type, 0.0):
                new_thermal = Thermal((try_x, try_y))
                all_sprites.add(new_thermal)
                thermals_group.add(new_thermal)

        # Glider-Thermal Collision
        hit_thermals = pygame.sprite.spritecollide(player, thermals_group, True) # True to kill thermal
        for thermal_hit in hit_thermals:
            player.height += THERMAL_STRENGTH
            # todo: Add sound effect for thermal

        # --- Draw ---
        draw_map(screen) # Draw background map
        player.draw_contrail(screen) # Draw contrail under the player
        all_sprites.draw(screen) # Draws player and thermals

        # Display Info
        draw_text(screen, f"Bank: {int(player.bank_angle)}°", 24, 10, 10, BLACK)
        draw_text(screen, f"Heading: {int(player.heading)}°", 24, 10, 35, BLACK)
        draw_text(screen, f"Height: {player.height} m", 24, 10, 60, BLACK)
        draw_text(screen, "ESC for Menu", 18, SCREEN_WIDTH - 100, 10, BLACK)


    pygame.display.flip()

pygame.quit()
