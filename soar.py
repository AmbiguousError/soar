import pygame
import math
import random

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
HUD_HEIGHT = 100 # Height of the top HUD panel

# Glider Physics & Control
INITIAL_HEIGHT = 500 # This is altitude (z-axis), not affected by map scrolling
INITIAL_SPEED = 3
MIN_SPEED = 1.0
MAX_SPEED = 7
ACCELERATION = 0.12

STALL_SPEED = 1.8
STALL_SINK_PENALTY = 0.08

# Gravity and Lift
GRAVITY_BASE_PULL = 0.22
LIFT_PER_SPEED_UNIT = 0.03
MINIMUM_SINK_RATE = 0.04

# Energy Exchange Physics
DIVE_TO_SPEED_FACTOR = 0.08
ZOOM_CLIMB_FACTOR = 1.8

MAX_BANK_ANGLE = 45
BANK_RATE = 2
TURN_RATE_SCALAR = 0.1

# Contrail
CONTRAIL_LENGTH = 60
CONTRAIL_POINT_DELAY = 2

# Thermals
BASE_THERMAL_SPAWN_RATE = 90 # Frames per potential spawn
THERMAL_SPAWN_RATE_INCREASE_PER_LEVEL = 15
MIN_THERMAL_RADIUS = 20
MAX_THERMAL_RADIUS = 50
MIN_THERMAL_LIFESPAN = 400 # Frames
MAX_THERMAL_LIFESPAN = 1200 # Frames
MIN_THERMAL_LIFT_POWER = 0.20
MAX_THERMAL_LIFT_POWER = 0.55
THERMAL_SPAWN_AREA_WIDTH = SCREEN_WIDTH + 200 # Spawn thermals a bit outside view
THERMAL_SPAWN_AREA_HEIGHT = SCREEN_HEIGHT + 200


# Map
TILE_SIZE = 40
# GAME_WORLD_Y_OFFSET = 0 # No longer needed like this
# MAP_GRID_WIDTH = SCREEN_WIDTH // TILE_SIZE # Not for fixed map anymore
# MAP_GRID_HEIGHT = SCREEN_HEIGHT // TILE_SIZE # Not for fixed map anymore

# Wind (will be global variables, initialized here)
MAX_WIND_STRENGTH = 1.0 # Max speed of wind in pixels/frame
current_wind_speed_x = 0.0
current_wind_speed_y = 0.0

# Clouds (Remain screen-space effects)
NUM_FOREGROUND_CLOUDS = 12
MIN_CLOUD_SPEED_FACTOR = 1.5
MAX_CLOUD_SPEED_FACTOR = 2.5
CLOUD_MIN_ALPHA = 40
CLOUD_MAX_ALPHA = 100

# Game Mechanics
TARGET_HEIGHT_PER_LEVEL = 1000
START_HEIGHT_NEW_LEVEL = 250 # Altitude

# Height Indicator (HUD element, screen space)
INDICATOR_WIDTH = 20
INDICATOR_X_MARGIN = 20
INDICATOR_Y_MARGIN_FROM_HUD = 20
INDICATOR_COLOR = (50, 50, 80)

# --- Game States ---
STATE_START_SCREEN = 0
STATE_PLAYING = 1
STATE_GAME_OVER = 2
STATE_LEVEL_COMPLETE = 3

# --- Colors ---
BLACK = (0, 0, 0); WHITE = (255, 255, 255); DARK_GRAY = (64, 64, 64)
GRAY = (150, 150, 150); LIGHT_GRAY = (200, 200, 200); RED = (255, 0, 0)
GREEN = (0, 200, 0); GOLD = (255, 215, 0)
CLOUD_COLOR = (220, 220, 240)
HUD_PANEL_COLOR = (30, 30, 50, 200) # Semi-transparent for HUD

COLOR_WATER = (173, 216, 230); COLOR_PLAINS = (170, 238, 170)
COLOR_FOREST = (144, 200, 144); COLOR_MOUNTAIN_BASE = (200, 200, 180)
COLOR_SAND = (245, 222, 179)

GLIDER_BODY_COLOR = (100, 100, 230); GLIDER_WING_COLOR = (150, 150, 255)

THERMAL_COLOR_PRIMARY_TUPLE = (255, 150, 150); THERMAL_COLOR_ACCENT_TUPLE = (255, 255, 255)
THERMAL_BASE_ALPHA = 100; THERMAL_ACCENT_ALPHA = 120

INDICATOR_PLAYER_COLOR = GOLD
INDICATOR_TARGET_COLOR = GREEN
INDICATOR_GROUND_COLOR = (100, 80, 60)


# --- Land Types ---
class LandType:
    WATER = 0; PLAINS = 1; FOREST = 2; MOUNTAIN_BASE = 3; SAND = 4

LAND_TYPE_COLORS = {
    LandType.WATER: COLOR_WATER, LandType.PLAINS: COLOR_PLAINS,
    LandType.FOREST: COLOR_FOREST, LandType.MOUNTAIN_BASE: COLOR_MOUNTAIN_BASE,
    LandType.SAND: COLOR_SAND,
}
LAND_TYPE_THERMAL_PROBABILITY = { # Probabilities for thermal generation over land types
    LandType.WATER: 0.01, LandType.PLAINS: 0.7, LandType.FOREST: 0.4,
    LandType.MOUNTAIN_BASE: 0.6, LandType.SAND: 0.9,
}

# --- Camera ---
camera_x = 0.0
camera_y = 0.0

# --- Glider Class ---
class Glider(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.fuselage_length = 45; fuselage_thickness = 4
        wing_span = 70; wing_chord = 5
        tail_plane_span = 18; tail_plane_chord = 4; tail_fin_height = 8

        canvas_width = self.fuselage_length; canvas_height = wing_span # Sprite canvas size
        self.original_image = pygame.Surface([canvas_width, canvas_height], pygame.SRCALPHA)

        # Draw glider components onto original_image (centered on its own canvas)
        fuselage_y_top = (canvas_height - fuselage_thickness) / 2
        pygame.draw.rect(self.original_image, GLIDER_BODY_COLOR, (0, fuselage_y_top, self.fuselage_length, fuselage_thickness))
        wing_leading_edge_x_from_tail = self.fuselage_length * 0.65 # Position of wing on fuselage
        pygame.draw.rect(self.original_image, GLIDER_WING_COLOR, (wing_leading_edge_x_from_tail, 0, wing_chord, wing_span))
        tail_plane_y_top = (canvas_height - tail_plane_span) / 2
        pygame.draw.rect(self.original_image, GLIDER_WING_COLOR, (0, tail_plane_y_top, tail_plane_chord, tail_plane_span))
        fin_base_y = fuselage_y_top; fin_tip_y = fin_base_y - tail_fin_height
        fin_base_start_x = 0; fin_base_end_x = tail_plane_chord
        fin_tip_x = (fin_base_start_x + fin_base_end_x) / 2
        pygame.draw.polygon(self.original_image, GLIDER_BODY_COLOR, [(fin_base_start_x, fin_base_y), (fin_base_end_x, fin_base_y), (fin_tip_x, fin_tip_y)])


        self.image = self.original_image
        # Player is always drawn at the screen center
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.radius = min(self.rect.width, self.rect.height) / 3 # For collision with thermals

        # World coordinates
        self.world_x = 0.0
        self.world_y = 0.0

        self.heading = 0 # Degrees, 0 is East/Right
        self.bank_angle = 0 # Degrees
        self.height = INITIAL_HEIGHT # Altitude
        self.speed = INITIAL_SPEED # Airspeed

        self.trail_points = [] # Stores world coordinates for contrail
        self.contrail_frame_counter = 0

    def reset(self, start_height=INITIAL_HEIGHT):
        self.world_x = 0.0 # Start at world origin
        self.world_y = 0.0
        # Screen position is fixed
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        self.heading = 0; self.bank_angle = 0
        self.height = start_height
        self.speed = INITIAL_SPEED
        self.trail_points = []; self.contrail_frame_counter = 0
        self.image = pygame.transform.rotate(self.original_image, -self.heading)


    def update(self, keys):
        global current_wind_speed_x, current_wind_speed_y # Access global wind

        # Speed control
        if keys[pygame.K_UP]: self.speed += ACCELERATION
        elif keys[pygame.K_DOWN]: # Exchange speed for height (zoom climb) or vice-versa
            potential_new_speed = self.speed - ACCELERATION
            if potential_new_speed >= MIN_SPEED:
                self.speed = potential_new_speed
                self.height += ACCELERATION * ZOOM_CLIMB_FACTOR # Gain height by reducing speed
            else: self.speed = MIN_SPEED
        self.speed = max(MIN_SPEED, min(self.speed, MAX_SPEED))

        # Banking and Turning
        if keys[pygame.K_LEFT]: self.bank_angle -= BANK_RATE
        elif keys[pygame.K_RIGHT]: self.bank_angle += BANK_RATE
        else: # Auto-level bank
            self.bank_angle *= 0.95
        if abs(self.bank_angle) < 0.1: self.bank_angle = 0 # Snap to zero if close
        self.bank_angle = max(-MAX_BANK_ANGLE, min(self.bank_angle, MAX_BANK_ANGLE))

        turn_rate_degrees = self.bank_angle * TURN_RATE_SCALAR * (self.speed / INITIAL_SPEED) # Turn rate affected by speed
        self.heading = (self.heading + turn_rate_degrees) % 360

        # Movement in world coordinates
        heading_rad = math.radians(self.heading)
        self.world_x += self.speed * math.cos(heading_rad)
        self.world_y += self.speed * math.sin(heading_rad)

        # Apply wind effect to world position
        self.world_x += current_wind_speed_x
        self.world_y += current_wind_speed_y

        # Update image rotation and fixed screen rect
        self.image = pygame.transform.rotate(self.original_image, -self.heading)
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))


        # Physics: Lift, Gravity, Stall
        height_change_due_to_physics = 0
        if self.speed < STALL_SPEED: # Stall condition
            height_change_due_to_physics = -GRAVITY_BASE_PULL - STALL_SINK_PENALTY
        else:
            lift_from_airspeed = self.speed * LIFT_PER_SPEED_UNIT
            net_vertical_force = lift_from_airspeed - GRAVITY_BASE_PULL
            # Sink rate if not enough lift, or climb rate if positive lift
            height_change_due_to_physics = max(net_vertical_force, -MINIMUM_SINK_RATE) if net_vertical_force < 0 else net_vertical_force
        self.height += height_change_due_to_physics

        # Energy exchange: Diving converts height to speed
        if height_change_due_to_physics < 0: # If sinking/diving
            self.speed = min(self.speed + abs(height_change_due_to_physics) * DIVE_TO_SPEED_FACTOR, MAX_SPEED)

        # Contrail
        self.contrail_frame_counter +=1
        if self.contrail_frame_counter >= CONTRAIL_POINT_DELAY:
            self.contrail_frame_counter = 0
            # Calculate tail position in world coordinates for contrail
            effective_tail_offset = (self.fuselage_length / 2) - 2 # Offset from glider center to tail
            tail_offset_x_world = -effective_tail_offset * math.cos(heading_rad)
            tail_offset_y_world = -effective_tail_offset * math.sin(heading_rad)
            # Base contrail point on glider's world center, then offset
            contrail_world_x = self.world_x + tail_offset_x_world
            contrail_world_y = self.world_y + tail_offset_y_world
            self.trail_points.append((contrail_world_x, contrail_world_y))
            if len(self.trail_points) > CONTRAIL_LENGTH: self.trail_points.pop(0)

        # Screen wrapping is removed as world is endless and camera follows player


    def apply_lift_from_thermal(self, thermal_lift_power_at_nominal_speed):
        if self.speed < STALL_SPEED: # No thermal lift if stalled
            return
        # Lift is stronger at lower speeds (easier to stay in thermal)
        lift_this_frame = thermal_lift_power_at_nominal_speed * (INITIAL_SPEED / max(self.speed, MIN_SPEED * 0.5))
        # Ensure some minimum lift even at high speed if in thermal
        self.height += max(lift_this_frame, thermal_lift_power_at_nominal_speed * 0.2)

    def draw_contrail(self, surface, cam_x, cam_y):
        if len(self.trail_points) > 1:
            for i, world_point in enumerate(self.trail_points):
                alpha = int(200 * (i / CONTRAIL_LENGTH)) # Fade out older points
                temp_surface = pygame.Surface((4,4), pygame.SRCALPHA) # Small surface for each dot
                pygame.draw.circle(temp_surface, (*GRAY, alpha), (2,2), 2)
                # Convert world point to screen point
                screen_px = world_point[0] - cam_x
                screen_py = world_point[1] - cam_y
                surface.blit(temp_surface, (screen_px - 2, screen_py - 2)) # Adjust for circle center

# --- Thermal Class ---
class Thermal(pygame.sprite.Sprite):
    def __init__(self, world_center_pos): # Takes world coordinates
        super().__init__()
        self.world_pos = pygame.math.Vector2(world_center_pos) # Store world position
        self.radius = random.randint(MIN_THERMAL_RADIUS, MAX_THERMAL_RADIUS)

        # Determine properties based on radius (smaller = stronger/shorter, larger = gentler/longer)
        if MAX_THERMAL_RADIUS == MIN_THERMAL_RADIUS: normalized_radius = 0.5
        else: normalized_radius = (self.radius - MIN_THERMAL_RADIUS) / (MAX_THERMAL_RADIUS - MIN_THERMAL_RADIUS)

        self.lifespan = MIN_THERMAL_LIFESPAN + (MAX_THERMAL_LIFESPAN - MIN_THERMAL_LIFESPAN) * normalized_radius
        self.initial_lifespan = self.lifespan
        self.lift_power = MAX_THERMAL_LIFT_POWER - (MAX_THERMAL_LIFT_POWER - MIN_THERMAL_LIFT_POWER) * normalized_radius

        self.image = pygame.Surface([self.radius * 2, self.radius * 2], pygame.SRCALPHA) # Image for visuals
        self.rect = self.image.get_rect() # Screen rect, updated each frame
        self.creation_time = pygame.time.get_ticks() # For visual pulsing
        self.update_visuals() # Initial draw of thermal visuals

    def update_visuals(self): # Update appearance based on age and pulse
        pulse_alpha_factor = (math.sin(pygame.time.get_ticks()*0.005 + self.creation_time*0.01)*0.3 + 0.7)
        age_factor = max(0, self.lifespan / self.initial_lifespan if self.initial_lifespan > 0 else 0) # Fades out
        alpha = int(THERMAL_BASE_ALPHA * pulse_alpha_factor * age_factor)
        accent_alpha = int(THERMAL_ACCENT_ALPHA * pulse_alpha_factor * age_factor)
        visual_radius_factor = math.sin(pygame.time.get_ticks()*0.002 + self.creation_time*0.005)*0.1 + 0.95 # Pulsing size
        current_visual_radius = int(self.radius * visual_radius_factor)

        self.image.fill((0,0,0,0)) # Clear previous frame
        pygame.draw.circle(self.image, (*THERMAL_COLOR_PRIMARY_TUPLE, alpha), (self.radius, self.radius), current_visual_radius)
        pygame.draw.circle(self.image, (*THERMAL_COLOR_ACCENT_TUPLE, accent_alpha), (self.radius, self.radius), int(current_visual_radius*0.7), 2) # Accent ring


    def update(self, cam_x, cam_y): # Needs camera coords to update screen rect
        self.lifespan -= 1
        if self.lifespan <= 0:
            self.kill() # Remove from sprite groups
        else:
            self.update_visuals()

        # Update screen position based on world position and camera
        self.rect.centerx = self.world_pos.x - cam_x
        self.rect.centery = self.world_pos.y - cam_y


# --- ForegroundCloud Class (Remains Screen-Space) ---
class ForegroundCloud(pygame.sprite.Sprite):
    def __init__(self, initial_distribution=False, index=0, total_clouds=1):
        super().__init__()
        global current_wind_speed_x, current_wind_speed_y

        self.width = random.randint(100, 250); self.height = random.randint(40, 80)
        self.image = pygame.Surface([self.width, self.height], pygame.SRCALPHA)
        num_puffs = random.randint(4, 7)
        for _ in range(num_puffs):
            puff_w=random.randint(int(self.width*0.4),int(self.width*0.8)); puff_h=random.randint(int(self.height*0.5),int(self.height*0.9))
            puff_x=random.randint(0,self.width-puff_w); puff_y=random.randint(0,self.height-puff_h)
            alpha = random.randint(CLOUD_MIN_ALPHA, CLOUD_MAX_ALPHA)
            pygame.draw.ellipse(self.image, (*CLOUD_COLOR, alpha), (puff_x, puff_y, puff_w, puff_h))

        self.speed_factor = random.uniform(MIN_CLOUD_SPEED_FACTOR, MAX_CLOUD_SPEED_FACTOR)
        self.dx = current_wind_speed_x * self.speed_factor
        self.dy = current_wind_speed_y * self.speed_factor

        # Initial positioning (screen space)
        if initial_distribution:
            self.x = (index/total_clouds)*SCREEN_WIDTH - self.width/2 + random.uniform(-SCREEN_WIDTH/(total_clouds*2), SCREEN_WIDTH/(total_clouds*2))
            self.y = random.randint(-self.height//2, SCREEN_HEIGHT - self.height//2)
        else: # Spawn off-screen based on their calculated dx, dy
            if self.dx == 0 and self.dy == 0:
                if random.choice([True, False]):
                    start_x = random.choice([-self.width - 20, SCREEN_WIDTH + 20])
                    start_y = random.randint(-self.height, SCREEN_HEIGHT)
                else:
                    start_x = random.randint(-self.width, SCREEN_WIDTH)
                    start_y = random.choice([-self.height - 20, SCREEN_HEIGHT + 20])
            else:
                if abs(self.dx) > abs(self.dy):
                    start_x = SCREEN_WIDTH + random.randint(0,100) + self.width/2 if self.dx < 0 else -random.randint(0,100) - self.width/2
                    start_y = random.randint(-self.height//2, SCREEN_HEIGHT - self.height//2)
                else:
                    start_y = SCREEN_HEIGHT + random.randint(0,50) + self.height/2 if self.dy < 0 else -random.randint(0,50) - self.height/2
                    start_x = random.randint(-self.width//2, SCREEN_WIDTH - self.width//2)
        self.rect = self.image.get_rect(topleft=(self.x if initial_distribution else start_x, self.y if initial_distribution else start_y))
        self.x = float(self.rect.x); self.y = float(self.rect.y)


    def update(self): # Clouds update in screen space
        self.dx = current_wind_speed_x * self.speed_factor
        self.dy = current_wind_speed_y * self.speed_factor
        self.x += self.dx; self.y += self.dy
        self.rect.topleft = (round(self.x), round(self.y))

        off_screen_margin_x = self.width*1.5 + abs(self.dx * 10) # Dynamic margin based on speed
        off_screen_margin_y = self.height*1.5 + abs(self.dy * 10)
        despawn = False
        if self.dx < 0 and self.rect.right < -off_screen_margin_x : despawn = True
        elif self.dx > 0 and self.rect.left > SCREEN_WIDTH + off_screen_margin_x : despawn = True
        if not despawn:
            if self.dy < 0 and self.rect.bottom < -off_screen_margin_y : despawn = True
            elif self.dy > 0 and self.rect.top > SCREEN_HEIGHT + off_screen_margin_y : despawn = True
        if self.dx == 0 and self.dy == 0: # For static clouds
            if not (-off_screen_margin_x < self.rect.centerx < SCREEN_WIDTH + off_screen_margin_x and \
                    -off_screen_margin_y < self.rect.centery < SCREEN_HEIGHT + off_screen_margin_y):
                despawn = True
        if despawn: self.kill()


# --- Endless Map Data & Functions ---
map_tile_random_generator = random.Random() # Dedicated Random instance for deterministic map generation

def get_land_type_at_world_pos(world_x, world_y):
    tile_grid_x = math.floor(world_x / TILE_SIZE)
    tile_grid_y = math.floor(world_y / TILE_SIZE)

    # Create a unique, deterministic seed for each tile coordinate
    # Primes help in distributing seeds better
    seed_val = (tile_grid_x * 73856093) ^ (tile_grid_y * 19349663) ^ ((tile_grid_x + tile_grid_y) * 47834583)
    map_tile_random_generator.seed(seed_val)

    land_types = [LandType.WATER, LandType.PLAINS, LandType.FOREST, LandType.MOUNTAIN_BASE, LandType.SAND]
    weights = [0.15, 0.35, 0.20, 0.15, 0.15] # Define probabilities for each land type
    return map_tile_random_generator.choices(land_types, weights=weights, k=1)[0]

def draw_endless_map(surface, cam_x, cam_y):
    # Calculate the world coordinates of the top-left tile visible on screen
    start_world_tile_x_coord = math.floor(cam_x / TILE_SIZE) * TILE_SIZE
    start_world_tile_y_coord = math.floor(cam_y / TILE_SIZE) * TILE_SIZE

    # Determine how many tiles to draw to cover the screen plus one extra for smooth scrolling
    num_tiles_x = SCREEN_WIDTH // TILE_SIZE + 2
    num_tiles_y = SCREEN_HEIGHT // TILE_SIZE + 2

    for i in range(num_tiles_y): # Iterate over tile rows
        for j in range(num_tiles_x): # Iterate over tile columns
            # Calculate world coordinates of the current tile
            current_tile_world_x = start_world_tile_x_coord + j * TILE_SIZE
            current_tile_world_y = start_world_tile_y_coord + i * TILE_SIZE

            # Calculate screen position to draw this tile
            tile_screen_x = current_tile_world_x - cam_x
            tile_screen_y = current_tile_world_y - cam_y

            tile_type = get_land_type_at_world_pos(current_tile_world_x, current_tile_world_y)
            color = LAND_TYPE_COLORS.get(tile_type, BLACK) # Default to black if type unknown
            pygame.draw.rect(surface, color, (tile_screen_x, tile_screen_y, TILE_SIZE, TILE_SIZE))

# --- Text Rendering Helper ---
def draw_text(surface, text, size, x, y, color=WHITE, font_name=None, center=False, antialias=True):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, antialias, color)
    text_rect = text_surface.get_rect()
    if center: text_rect.center = (x, y)
    else: text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)

# --- Pygame Setup ---
pygame.init(); pygame.mixer.init() # Initialize Pygame modules
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pastel Glider - Endless World")
clock = pygame.time.Clock()

# --- Game Objects & Variables ---
player = Glider()
# Sprite groups for managing and drawing game objects
all_world_sprites = pygame.sprite.Group() # Sprites that exist in world space (thermals)
# player_sprite_group = pygame.sprite.GroupSingle(player) # Player is drawn separately, always centered
thermals_group = pygame.sprite.Group() # For thermals
foreground_clouds_group = pygame.sprite.Group() # Screen-space clouds

game_state = STATE_START_SCREEN
current_level = 1; level_timer_start_ticks = 0; time_taken_for_level = 0
current_thermal_spawn_rate = BASE_THERMAL_SPAWN_RATE
thermal_spawn_timer = 0; final_score = 0
# generate_map() # No longer used for fixed map

def generate_new_wind():
    global current_wind_speed_x, current_wind_speed_y
    wind_angle_rad = random.uniform(0, 2 * math.pi)
    wind_strength = random.uniform(0.1, MAX_WIND_STRENGTH) # Ensure some wind always
    current_wind_speed_x = wind_strength * math.cos(wind_angle_rad)
    current_wind_speed_y = wind_strength * math.sin(wind_angle_rad)

def start_new_level(level_num):
    global current_level,level_timer_start_ticks,current_thermal_spawn_rate,thermal_spawn_timer, camera_x, camera_y
    current_level=level_num; level_timer_start_ticks=pygame.time.get_ticks()
    current_thermal_spawn_rate = BASE_THERMAL_SPAWN_RATE + (THERMAL_SPAWN_RATE_INCREASE_PER_LEVEL * (current_level -1))
    thermal_spawn_timer=0
    # generate_map() # No longer used
    generate_new_wind()
    thermals_group.empty()
    all_world_sprites.empty()


    foreground_clouds_group.empty()
    for i in range(NUM_FOREGROUND_CLOUDS):
        foreground_clouds_group.add(ForegroundCloud(initial_distribution=True,index=i,total_clouds=NUM_FOREGROUND_CLOUDS))

    start_h = START_HEIGHT_NEW_LEVEL if current_level > 1 else INITIAL_HEIGHT
    player.reset(start_height=start_h) # Resets player world_x, world_y to 0,0
    # Camera will be updated based on player's new world position in main loop

def reset_to_main_menu():
    global game_state,current_level,final_score, current_wind_speed_x, current_wind_speed_y, camera_x, camera_y
    player.reset(); thermals_group.empty(); all_world_sprites.empty()
    foreground_clouds_group.empty()
    current_wind_speed_x = -0.2 # Gentle default for menu clouds
    current_wind_speed_y = 0.05
    for i in range(NUM_FOREGROUND_CLOUDS): foreground_clouds_group.add(ForegroundCloud(initial_distribution=True,index=i,total_clouds=NUM_FOREGROUND_CLOUDS))
    current_level=1; final_score=0; game_state = STATE_START_SCREEN
    # Reset camera based on player's reset position
    camera_x = player.world_x - SCREEN_WIDTH // 2
    camera_y = player.world_y - SCREEN_HEIGHT // 2


# --- Screen Drawing Functions (HUD elements are screen-space) ---
def draw_start_screen_content(surface): # Draws on main screen or a dedicated surface
    surface.fill(DARK_GRAY) # Background for start screen
    draw_text(surface, "Pastel Glider", 64, SCREEN_WIDTH//2, SCREEN_HEIGHT//4 - 40, COLOR_PLAINS, center=True)
    draw_text(surface, "Reach 1000m to advance!", 26, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 120, WHITE, center=True)
    draw_text(surface, "UP/DOWN: Speed | L/R: Bank", 22, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80, WHITE, center=True)
    draw_text(surface, f"Stall < {STALL_SPEED:.1f} speed (no thermal lift!)", 22, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50, WHITE, center=True)
    draw_text(surface, "K_DOWN: Speed for Height | Diving: Height for Speed", 22, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20, WHITE, center=True)
    draw_text(surface, "Small thermals: strong/short. Large: gentle/long.", 22, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 10, WHITE, center=True)
    draw_text(surface, "Thermals rarer & Wind changes each level!", 22, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40, WHITE, center=True)
    draw_text(surface, "ENTER to Start", 30, SCREEN_WIDTH//2, SCREEN_HEIGHT*3//4 + 20, LIGHT_GRAY, center=True)
    draw_text(surface, "ESC for Menu", 20, SCREEN_WIDTH//2, SCREEN_HEIGHT*3//4 + 60, GRAY, center=True)

def draw_level_complete_screen(surface, level, time_taken_seconds_val):
    surface.fill(DARK_GRAY)
    draw_text(surface, f"Level {level} Complete!", 60, SCREEN_WIDTH//2, SCREEN_HEIGHT//3, GOLD, center=True)
    draw_text(surface, f"Time: {time_taken_seconds_val:.1f}s", 36, SCREEN_WIDTH//2, SCREEN_HEIGHT//2, WHITE, center=True)
    draw_text(surface, "Press ENTER for Next Level", 36, SCREEN_WIDTH//2, SCREEN_HEIGHT*2//3, LIGHT_GRAY, center=True)

def draw_game_over_screen_content(surface, score, level):
    surface.fill(DARK_GRAY)
    draw_text(surface, "GAME OVER", 72, SCREEN_WIDTH//2, SCREEN_HEIGHT//3, RED, center=True)
    draw_text(surface, f"Reached Level: {level}", 36, SCREEN_WIDTH//2, SCREEN_HEIGHT//2-30, WHITE, center=True)
    draw_text(surface, f"Final Height: {int(score)}m", 36, SCREEN_WIDTH//2, SCREEN_HEIGHT//2+10, WHITE, center=True)
    draw_text(surface, "ENTER for Menu", 32, SCREEN_WIDTH//2, SCREEN_HEIGHT*2//3, LIGHT_GRAY, center=True)

def draw_height_indicator_hud(surface, current_player_height, target_h): # Screen space
    indicator_bar_height = SCREEN_HEIGHT - HUD_HEIGHT - (2 * INDICATOR_Y_MARGIN_FROM_HUD)
    indicator_x_pos = SCREEN_WIDTH - INDICATOR_WIDTH - INDICATOR_X_MARGIN
    indicator_y_pos = HUD_HEIGHT + INDICATOR_Y_MARGIN_FROM_HUD
    pygame.draw.rect(surface, INDICATOR_COLOR, (indicator_x_pos, indicator_y_pos, INDICATOR_WIDTH, indicator_bar_height))
    max_indicator_height_value = target_h * 1.1
    if max_indicator_height_value <=0: max_indicator_height_value = 1

    pygame.draw.line(surface, INDICATOR_GROUND_COLOR, (indicator_x_pos-5, indicator_y_pos+indicator_bar_height), (indicator_x_pos+INDICATOR_WIDTH+5, indicator_y_pos+indicator_bar_height), 3)
    draw_text(surface, "0m", 14, indicator_x_pos+INDICATOR_WIDTH+8, indicator_y_pos+indicator_bar_height-7, WHITE)

    target_marker_y_on_bar = indicator_y_pos
    if target_h > 0 :
        target_ratio = min(target_h / max_indicator_height_value, 1.0)
        target_marker_y_on_bar = indicator_y_pos + indicator_bar_height * (1 - target_ratio)
        pygame.draw.line(surface, INDICATOR_TARGET_COLOR, (indicator_x_pos-5, target_marker_y_on_bar), (indicator_x_pos+INDICATOR_WIDTH+5, target_marker_y_on_bar), 3)
        draw_text(surface, f"{target_h}m", 14, indicator_x_pos+INDICATOR_WIDTH+8, target_marker_y_on_bar-7, INDICATOR_TARGET_COLOR)

    if current_player_height > 0:
        player_height_ratio = min(current_player_height / max_indicator_height_value, 1.0)
        player_marker_y_on_bar = indicator_y_pos + indicator_bar_height * (1 - player_height_ratio)
        pygame.draw.line(surface, INDICATOR_PLAYER_COLOR, (indicator_x_pos, player_marker_y_on_bar), (indicator_x_pos+INDICATOR_WIDTH, player_marker_y_on_bar), 5)
        text_y = player_marker_y_on_bar - 7
        ground_text_y = indicator_y_pos + indicator_bar_height - 7
        target_text_y = target_marker_y_on_bar - 7
        if abs(text_y - ground_text_y) < 15 : text_y = ground_text_y - 15
        if target_h > 0 and abs(text_y - target_text_y) < 15 :
            if player_marker_y_on_bar > target_marker_y_on_bar: text_y = target_text_y + 15
            else: text_y = target_text_y - 15
        draw_text(surface, f"{int(current_player_height)}m", 14, indicator_x_pos-35, text_y, INDICATOR_PLAYER_COLOR)


def draw_weather_vane(surface, wind_x, wind_y, center_x, center_y, max_strength_for_scaling=MAX_WIND_STRENGTH): # Screen space
    wind_angle_rad = math.atan2(wind_y, wind_x)
    wind_magnitude = math.hypot(wind_x, wind_y)
    arrow_base_length = 15; arrow_max_additional_length = 20; arrow_color = WHITE; arrow_thickness = 2
    vane_circle_radius = 3; vane_circle_color = GRAY
    strength_ratio = 0.0
    if max_strength_for_scaling > 0: strength_ratio = min(wind_magnitude / max_strength_for_scaling, 1.0)
    current_arrow_length = arrow_base_length + arrow_max_additional_length * strength_ratio
    tip_x = center_x + current_arrow_length * math.cos(wind_angle_rad)
    tip_y = center_y + current_arrow_length * math.sin(wind_angle_rad)
    tail_length_factor = 0.3
    tail_x = center_x - (arrow_base_length * tail_length_factor) * math.cos(wind_angle_rad)
    tail_y = center_y - (arrow_base_length * tail_length_factor) * math.sin(wind_angle_rad)
    arrowhead_angle_offset = math.radians(150); arrowhead_length = 8
    barb1_angle = wind_angle_rad + arrowhead_angle_offset; barb1_x = tip_x + arrowhead_length * math.cos(barb1_angle); barb1_y = tip_y + arrowhead_length * math.sin(barb1_angle)
    barb2_angle = wind_angle_rad - arrowhead_angle_offset; barb2_x = tip_x + arrowhead_length * math.cos(barb2_angle); barb2_y = tip_y + arrowhead_length * math.sin(barb2_angle)
    pygame.draw.line(surface, arrow_color, (tail_x, tail_y), (tip_x, tip_y), arrow_thickness)
    pygame.draw.line(surface, arrow_color, (tip_x, tip_y), (barb1_x, barb1_y), arrow_thickness)
    pygame.draw.line(surface, arrow_color, (tip_x, tip_y), (barb2_x, barb2_y), arrow_thickness)
    pygame.draw.circle(surface, vane_circle_color, (center_x, center_y), vane_circle_radius)
    pygame.draw.circle(surface, arrow_color, (center_x, center_y), vane_circle_radius, 1)

# --- Game Loop ---
running = True
while running:
    dt = clock.tick(60) / 1000.0 # Delta time, not heavily used yet but good practice
    current_ticks = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if game_state == STATE_START_SCREEN and event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            start_new_level(1); game_state = STATE_PLAYING
        elif game_state == STATE_PLAYING and event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            reset_to_main_menu()
        elif game_state == STATE_LEVEL_COMPLETE and event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            start_new_level(current_level + 1); game_state = STATE_PLAYING
        elif game_state == STATE_GAME_OVER and event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            reset_to_main_menu()

    # --- Updates ---
    if game_state == STATE_PLAYING:
        keys = pygame.key.get_pressed()
        player.update(keys)

        # Update camera to follow player's world position
        camera_x = player.world_x - SCREEN_WIDTH // 2
        camera_y = player.world_y - SCREEN_HEIGHT // 2

        # Update world sprites (thermals) with camera info for their screen rects
        for thermal_sprite in thermals_group: # Using specific group for type hinting if needed
            thermal_sprite.update(camera_x, camera_y)

        foreground_clouds_group.update() # Screen-space clouds update normally

        if len(foreground_clouds_group) < NUM_FOREGROUND_CLOUDS:
            foreground_clouds_group.add(ForegroundCloud()) # Respawn clouds

        # Thermal Spawning (relative to camera view, but positions stored in world coords)
        thermal_spawn_timer += 1
        if thermal_spawn_timer >= current_thermal_spawn_rate:
            thermal_spawn_timer = 0
            # Spawn thermals in an area around the camera's current view
            spawn_world_x = camera_x + random.randint(-THERMAL_SPAWN_AREA_WIDTH // 2, THERMAL_SPAWN_AREA_WIDTH // 2)
            spawn_world_y = camera_y + random.randint(-THERMAL_SPAWN_AREA_HEIGHT // 2, THERMAL_SPAWN_AREA_HEIGHT // 2)

            land_type = get_land_type_at_world_pos(spawn_world_x, spawn_world_y)
            if random.random() < LAND_TYPE_THERMAL_PROBABILITY.get(land_type, 0.0):
                new_thermal = Thermal((spawn_world_x, spawn_world_y))
                all_world_sprites.add(new_thermal); thermals_group.add(new_thermal)

        # Player-Thermal Collision (using world coordinates)
        player_world_pos_vec = pygame.math.Vector2(player.world_x, player.world_y)
        for thermal in thermals_group:
            distance_to_thermal_center = player_world_pos_vec.distance_to(thermal.world_pos)
            # Approximate player as a circle for collision
            if distance_to_thermal_center < thermal.radius + player.radius * 0.7: # Player radius reduced for leniency
                player.apply_lift_from_thermal(thermal.lift_power)

        # Game State Transitions based on height
        if player.height >= TARGET_HEIGHT_PER_LEVEL:
            game_state = STATE_LEVEL_COMPLETE
            level_end_ticks = pygame.time.get_ticks()
            time_taken_for_level = (level_end_ticks - level_timer_start_ticks) / 1000.0
        if player.height <= 0: # Crashed
            final_score = player.height; player.height = 0 # Record score, then set height to 0 for display
            game_state = STATE_GAME_OVER

    # --- Drawing ---
    screen.fill(BLACK) # Default background, map will draw over this

    if game_state == STATE_START_SCREEN:
        draw_start_screen_content(screen)
        foreground_clouds_group.draw(screen) # Screen-space clouds
    elif game_state == STATE_LEVEL_COMPLETE:
        draw_level_complete_screen(screen, current_level, time_taken_for_level)
        foreground_clouds_group.draw(screen)
    elif game_state == STATE_PLAYING:
        # Draw world elements (affected by camera)
        draw_endless_map(screen, camera_x, camera_y)
        player.draw_contrail(screen, camera_x, camera_y)
        all_world_sprites.draw(screen) # Draws thermals at their screen rects

        # Draw player (always centered on screen)
        screen.blit(player.image, player.rect)

        # Draw screen-space elements (NOT affected by camera)
        foreground_clouds_group.draw(screen)

        # HUD (drawn on top, screen space)
        hud_surface = pygame.Surface((SCREEN_WIDTH, HUD_HEIGHT), pygame.SRCALPHA)
        hud_surface.fill(HUD_PANEL_COLOR)
        screen.blit(hud_surface, (0,0)) # Blit HUD panel at top of screen

        text_color_on_hud = WHITE; hud_margin = 10; line_spacing = 22; current_y_hud = hud_margin
        draw_text(screen, f"Level: {current_level}", 20, hud_margin, current_y_hud, text_color_on_hud)
        draw_text(screen, f"Target: {TARGET_HEIGHT_PER_LEVEL}m", 20, hud_margin + 120, current_y_hud, text_color_on_hud)
        current_y_hud += line_spacing
        timer_seconds = (current_ticks - level_timer_start_ticks) / 1000.0
        draw_text(screen, f"Time: {timer_seconds:.1f}s", 20, hud_margin, current_y_hud, text_color_on_hud)
        current_y_hud += line_spacing
        draw_text(screen, f"Height: {int(player.height)}m", 20, hud_margin, current_y_hud, text_color_on_hud)
        draw_text(screen, f"Speed: {player.speed:.1f}", 20, hud_margin + 120, current_y_hud, text_color_on_hud)

        if player.speed < STALL_SPEED: draw_text(screen, "STALL!", 24, SCREEN_WIDTH//2, hud_margin + line_spacing//2, RED, center=True)

        wind_display_text = f"Wind: <{current_wind_speed_x*10:.0f}, {current_wind_speed_y*10:.0f}>"
        wind_text_x_pos = SCREEN_WIDTH - 220
        draw_text(screen, wind_display_text, 18, wind_text_x_pos, hud_margin + 5, text_color_on_hud)
        draw_text(screen, "ESC for Menu", 18, wind_text_x_pos, hud_margin + 5 + line_spacing, text_color_on_hud)
        draw_weather_vane(screen, current_wind_speed_x, current_wind_speed_y, wind_text_x_pos + 150, hud_margin + 25)
        draw_height_indicator_hud(screen, player.height, TARGET_HEIGHT_PER_LEVEL)

    elif game_state == STATE_GAME_OVER:
        draw_game_over_screen_content(screen, final_score, current_level)
        foreground_clouds_group.draw(screen)

    pygame.display.flip() # Update the full display

pygame.quit()