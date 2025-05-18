import pygame
import math
import random

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
HUD_HEIGHT = 100 # Height of the top HUD panel

# Glider Physics & Control
INITIAL_HEIGHT = 500
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
BASE_THERMAL_SPAWN_RATE = 90
THERMAL_SPAWN_RATE_INCREASE_PER_LEVEL = 15
MIN_THERMAL_RADIUS = 20
MAX_THERMAL_RADIUS = 50
MIN_THERMAL_LIFESPAN = 400
MAX_THERMAL_LIFESPAN = 1200
MIN_THERMAL_LIFT_POWER = 0.20
MAX_THERMAL_LIFT_POWER = 0.55

# Map
TILE_SIZE = 40
GAME_WORLD_Y_OFFSET = 0
MAP_GRID_WIDTH = SCREEN_WIDTH // TILE_SIZE
MAP_GRID_HEIGHT = SCREEN_HEIGHT // TILE_SIZE

# Wind (will be global variables, initialized here)
MAX_WIND_STRENGTH = 1.0 # Max speed of wind in pixels/frame
current_wind_speed_x = 0.0
current_wind_speed_y = 0.0

# Clouds
NUM_FOREGROUND_CLOUDS = 12 # Slightly increased for better full-screen feel
MIN_CLOUD_SPEED_FACTOR = 1.5
MAX_CLOUD_SPEED_FACTOR = 2.5
CLOUD_MIN_ALPHA = 40
CLOUD_MAX_ALPHA = 100

# Game Mechanics
TARGET_HEIGHT_PER_LEVEL = 1000
START_HEIGHT_NEW_LEVEL = 250

# Height Indicator
INDICATOR_WIDTH = 20
INDICATOR_X_MARGIN = 20
INDICATOR_Y_MARGIN_FROM_HUD = 20
INDICATOR_COLOR = (50, 50, 80)
# Colors for indicator defined after main color block

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
HUD_PANEL_COLOR = (30, 30, 50, 200)

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
LAND_TYPE_THERMAL_PROBABILITY = {
    LandType.WATER: 0.01, LandType.PLAINS: 0.7, LandType.FOREST: 0.4,
    LandType.MOUNTAIN_BASE: 0.6, LandType.SAND: 0.9,
}

# --- Glider Class ---
class Glider(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.fuselage_length = 45; fuselage_thickness = 4
        wing_span = 70; wing_chord = 5
        tail_plane_span = 18; tail_plane_chord = 4; tail_fin_height = 8

        canvas_width = self.fuselage_length; canvas_height = wing_span
        self.original_image = pygame.Surface([canvas_width, canvas_height], pygame.SRCALPHA)

        fuselage_y_top = (canvas_height - fuselage_thickness) / 2
        pygame.draw.rect(self.original_image, GLIDER_BODY_COLOR, (0, fuselage_y_top, self.fuselage_length, fuselage_thickness))
        wing_leading_edge_x_from_tail = self.fuselage_length * 0.65
        pygame.draw.rect(self.original_image, GLIDER_WING_COLOR, (wing_leading_edge_x_from_tail, 0, wing_chord, wing_span))
        tail_plane_y_top = (canvas_height - tail_plane_span) / 2
        pygame.draw.rect(self.original_image, GLIDER_WING_COLOR, (0, tail_plane_y_top, tail_plane_chord, tail_plane_span))
        fin_base_y = fuselage_y_top; fin_tip_y = fin_base_y - tail_fin_height
        fin_base_start_x = 0; fin_base_end_x = tail_plane_chord
        fin_tip_x = (fin_base_start_x + fin_base_end_x) / 2
        pygame.draw.polygon(self.original_image, GLIDER_BODY_COLOR, [(fin_base_start_x, fin_base_y), (fin_base_end_x, fin_base_y), (fin_tip_x, fin_tip_y)])

        self.image = self.original_image
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.radius = min(self.rect.width, self.rect.height) / 3

        self.x = float(self.rect.centerx); self.y = float(self.rect.centery)
        self.heading = 0; self.bank_angle = 0
        self.height = INITIAL_HEIGHT; self.speed = INITIAL_SPEED
        self.trail_points = []; self.contrail_frame_counter = 0

    def reset(self, start_height=INITIAL_HEIGHT):
        self.x = float(SCREEN_WIDTH // 2); self.y = float(SCREEN_HEIGHT // 2)
        self.rect.center = (round(self.x), round(self.y))
        self.heading = 0; self.bank_angle = 0
        self.height = start_height
        self.speed = INITIAL_SPEED
        self.trail_points = []; self.contrail_frame_counter = 0
        self.image = pygame.transform.rotate(self.original_image, -self.heading)

    def update(self, keys):
        global current_wind_speed_x, current_wind_speed_y # Access global wind

        if keys[pygame.K_UP]: self.speed += ACCELERATION
        elif keys[pygame.K_DOWN]:
            potential_new_speed = self.speed - ACCELERATION
            if potential_new_speed >= MIN_SPEED:
                self.speed = potential_new_speed
                self.height += ACCELERATION * ZOOM_CLIMB_FACTOR
            else: self.speed = MIN_SPEED
        self.speed = max(MIN_SPEED, min(self.speed, MAX_SPEED))

        if keys[pygame.K_LEFT]: self.bank_angle -= BANK_RATE
        elif keys[pygame.K_RIGHT]: self.bank_angle += BANK_RATE
        else: self.bank_angle *= 0.95
        if abs(self.bank_angle) < 0.1: self.bank_angle = 0
        self.bank_angle = max(-MAX_BANK_ANGLE, min(self.bank_angle, MAX_BANK_ANGLE))

        turn_rate_degrees = self.bank_angle * TURN_RATE_SCALAR
        self.heading = (self.heading + turn_rate_degrees) % 360

        heading_rad = math.radians(self.heading)
        # Movement from player control
        self.x += self.speed * math.cos(heading_rad)
        self.y += self.speed * math.sin(heading_rad)
        
        # Apply wind effect
        self.x += current_wind_speed_x
        self.y += current_wind_speed_y


        self.image = pygame.transform.rotate(self.original_image, -self.heading)
        self.rect = self.image.get_rect(center=(round(self.x), round(self.y)))

        height_change_due_to_physics = 0
        if self.speed < STALL_SPEED:
            height_change_due_to_physics = -GRAVITY_BASE_PULL - STALL_SINK_PENALTY
        else:
            lift_from_airspeed = self.speed * LIFT_PER_SPEED_UNIT
            net_vertical_force = lift_from_airspeed - GRAVITY_BASE_PULL
            height_change_due_to_physics = max(net_vertical_force, -MINIMUM_SINK_RATE) if net_vertical_force < 0 else net_vertical_force
        self.height += height_change_due_to_physics

        if height_change_due_to_physics < 0:
            self.speed = min(self.speed + abs(height_change_due_to_physics) * DIVE_TO_SPEED_FACTOR, MAX_SPEED)

        self.contrail_frame_counter +=1
        if self.contrail_frame_counter >= CONTRAIL_POINT_DELAY:
            self.contrail_frame_counter = 0
            effective_tail_offset = (self.fuselage_length / 2) - 2
            tail_offset_x = -effective_tail_offset * math.cos(heading_rad)
            tail_offset_y = -effective_tail_offset * math.sin(heading_rad)
            self.trail_points.append((self.rect.centerx + tail_offset_x, self.rect.centery + tail_offset_y))
            if len(self.trail_points) > CONTRAIL_LENGTH: self.trail_points.pop(0)

        margin = max(self.rect.width, self.rect.height) / 2
        if self.x - margin > SCREEN_WIDTH: self.x = -margin
        if self.x + margin < 0: self.x = SCREEN_WIDTH + margin
        if self.y - margin > SCREEN_HEIGHT: self.y = -margin
        if self.y + margin < 0: self.y = SCREEN_HEIGHT + margin


    def apply_lift_from_thermal(self, thermal_lift_power_at_nominal_speed):
        if self.speed < STALL_SPEED:
            return
        lift_this_frame = thermal_lift_power_at_nominal_speed * (INITIAL_SPEED / max(self.speed, MIN_SPEED * 0.5))
        self.height += max(lift_this_frame, thermal_lift_power_at_nominal_speed * 0.2)

    def draw_contrail(self, surface):
        if len(self.trail_points) > 1:
            for i, point in enumerate(self.trail_points):
                alpha = int(200 * (i / CONTRAIL_LENGTH))
                temp_surface = pygame.Surface((4,4), pygame.SRCALPHA)
                pygame.draw.circle(temp_surface, (*GRAY, alpha), (2,2), 2)
                surface.blit(temp_surface, (point[0]-2, point[1]-2))

# --- Thermal Class ---
class Thermal(pygame.sprite.Sprite):
    def __init__(self, center_pos):
        super().__init__()
        self.pos = pygame.math.Vector2(center_pos)
        self.radius = random.randint(MIN_THERMAL_RADIUS, MAX_THERMAL_RADIUS)
        
        if MAX_THERMAL_RADIUS == MIN_THERMAL_RADIUS: normalized_radius = 0.5
        else: normalized_radius = (self.radius - MIN_THERMAL_RADIUS) / (MAX_THERMAL_RADIUS - MIN_THERMAL_RADIUS)

        self.lifespan = MIN_THERMAL_LIFESPAN + (MAX_THERMAL_LIFESPAN - MIN_THERMAL_LIFESPAN) * normalized_radius
        self.initial_lifespan = self.lifespan
        self.lift_power = MAX_THERMAL_LIFT_POWER - (MAX_THERMAL_LIFT_POWER - MIN_THERMAL_LIFT_POWER) * normalized_radius
        
        self.image = pygame.Surface([self.radius * 2, self.radius * 2], pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(self.pos.x, self.pos.y))
        self.creation_time = pygame.time.get_ticks()
        self.update_visuals()

    def update_visuals(self):
        pulse_alpha_factor = (math.sin(pygame.time.get_ticks()*0.005 + self.creation_time*0.01)*0.3 + 0.7)
        age_factor = max(0, self.lifespan / self.initial_lifespan if self.initial_lifespan > 0 else 0)
        alpha = int(THERMAL_BASE_ALPHA * pulse_alpha_factor * age_factor)
        accent_alpha = int(THERMAL_ACCENT_ALPHA * pulse_alpha_factor * age_factor)
        visual_radius_factor = math.sin(pygame.time.get_ticks()*0.002 + self.creation_time*0.005)*0.1 + 0.95
        current_visual_radius = int(self.radius * visual_radius_factor)
        self.image.fill((0,0,0,0))
        pygame.draw.circle(self.image, (*THERMAL_COLOR_PRIMARY_TUPLE, alpha), (self.radius, self.radius), current_visual_radius)
        pygame.draw.circle(self.image, (*THERMAL_COLOR_ACCENT_TUPLE, accent_alpha), (self.radius, self.radius), int(current_visual_radius*0.7), 2)

    def update(self):
        self.lifespan -= 1
        if self.lifespan <= 0: self.kill()
        else: self.update_visuals()
        self.rect.centery = self.pos.y


# --- ForegroundCloud Class ---
class ForegroundCloud(pygame.sprite.Sprite):
    def __init__(self, initial_distribution=False, index=0, total_clouds=1):
        super().__init__()
        global current_wind_speed_x, current_wind_speed_y # Use current wind for cloud speed

        self.width = random.randint(100, 250); self.height = random.randint(40, 80)
        self.image = pygame.Surface([self.width, self.height], pygame.SRCALPHA)
        num_puffs = random.randint(4, 7)
        for _ in range(num_puffs):
            puff_w=random.randint(int(self.width*0.4),int(self.width*0.8)); puff_h=random.randint(int(self.height*0.5),int(self.height*0.9))
            puff_x=random.randint(0,self.width-puff_w); puff_y=random.randint(0,self.height-puff_h)
            alpha = random.randint(CLOUD_MIN_ALPHA, CLOUD_MAX_ALPHA)
            pygame.draw.ellipse(self.image, (*CLOUD_COLOR, alpha), (puff_x, puff_y, puff_w, puff_h))
        
        self.speed_factor = random.uniform(MIN_CLOUD_SPEED_FACTOR, MAX_CLOUD_SPEED_FACTOR)
        # Cloud movement is based on the *current* wind direction and speed
        self.dx = current_wind_speed_x * self.speed_factor 
        self.dy = current_wind_speed_y * self.speed_factor

        if initial_distribution:
            self.x = (index/total_clouds)*SCREEN_WIDTH - self.width/2 + random.uniform(-SCREEN_WIDTH/(total_clouds*2), SCREEN_WIDTH/(total_clouds*2))
            self.y = random.randint(-self.height//2, SCREEN_HEIGHT - self.height//2)
        else: 
            # Spawn off-screen based on their calculated dx, dy
            if self.dx < 0: start_x = SCREEN_WIDTH + random.randint(0,100) + self.width/2
            elif self.dx > 0 : start_x = -random.randint(0,100) - self.width/2
            else: start_x = random.randint(0, SCREEN_WIDTH - self.width) # If no horizontal wind

            if self.dy < 0: start_y = SCREEN_HEIGHT + random.randint(0,50) + self.height/2
            elif self.dy > 0: start_y = -random.randint(0,50) - self.height/2
            else: start_y = random.randint(0, SCREEN_HEIGHT - self.height) # If no vertical wind
        
        self.rect = self.image.get_rect(topleft=(self.x if initial_distribution else start_x, self.y if initial_distribution else start_y))
        self.x = float(self.rect.x); self.y = float(self.rect.y)

    def update(self):
        # Update cloud speed if wind changes (though wind changes per level, clouds are reset then)
        self.dx = current_wind_speed_x * self.speed_factor 
        self.dy = current_wind_speed_y * self.speed_factor

        self.x += self.dx; self.y += self.dy
        self.rect.topleft = (round(self.x), round(self.y))
        off_screen_margin = self.width*1.5 
        if self.dx != 0: # Only kill based on horizontal movement if there is horizontal movement
            if self.dx < 0 and self.rect.right < -off_screen_margin: self.kill()
            elif self.dx > 0 and self.rect.left > SCREEN_WIDTH + off_screen_margin: self.kill()
        if self.dy != 0: # Only kill based on vertical movement if there is vertical movement
            if self.dy < 0 and self.rect.bottom < -off_screen_margin : self.kill()
            elif self.dy > 0 and self.rect.top > SCREEN_HEIGHT + off_screen_margin : self.kill()
        # If a cloud has no movement (wind is zero and it spawned on screen), it might never despawn.
        # This is less likely now that wind is always generated.


# --- Map Data & Functions ---
map_data = []
def generate_map():
    global map_data; map_data = []
    land_types = [LandType.WATER,LandType.PLAINS,LandType.FOREST,LandType.MOUNTAIN_BASE,LandType.SAND]
    weights = [0.15,0.35,0.20,0.15,0.15]
    for _ in range(MAP_GRID_HEIGHT): map_data.append(random.choices(land_types, weights=weights, k=MAP_GRID_WIDTH))

def get_land_type_at_pos(world_x, world_y):
    grid_x = int(world_x // TILE_SIZE)%MAP_GRID_WIDTH
    grid_y = int(world_y // TILE_SIZE)%MAP_GRID_HEIGHT
    return map_data[grid_y][grid_x]

def draw_map(surface):
    for r_idx, row in enumerate(map_data):
        for c_idx, tile_type in enumerate(row):
            pygame.draw.rect(surface, LAND_TYPE_COLORS.get(tile_type,BLACK), (c_idx*TILE_SIZE, r_idx*TILE_SIZE, TILE_SIZE, TILE_SIZE))

# --- Text Rendering Helper ---
def draw_text(surface, text, size, x, y, color=WHITE, font_name=None, center=False, antialias=True):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, antialias, color)
    text_rect = text_surface.get_rect()
    if center: text_rect.center = (x, y)
    else: text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)

# --- Pygame Setup ---
pygame.init(); pygame.mixer.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pastel Glider - Wind Effects")
clock = pygame.time.Clock()

# --- Game Objects & Variables ---
player = Glider()
all_sprites = pygame.sprite.Group(); thermals_group = pygame.sprite.Group(); foreground_clouds_group = pygame.sprite.Group()
game_state = STATE_START_SCREEN
current_level = 1; level_timer_start_ticks = 0; current_thermal_spawn_rate = BASE_THERMAL_SPAWN_RATE
thermal_spawn_timer = 0; final_score = 0
generate_map()

def generate_new_wind():
    global current_wind_speed_x, current_wind_speed_y
    wind_angle_rad = random.uniform(0, 2 * math.pi)
    wind_strength = random.uniform(0.1, MAX_WIND_STRENGTH) # Ensure some wind
    current_wind_speed_x = wind_strength * math.cos(wind_angle_rad)
    current_wind_speed_y = wind_strength * math.sin(wind_angle_rad)

def start_new_level(level_num):
    global current_level,level_timer_start_ticks,current_thermal_spawn_rate,thermal_spawn_timer
    current_level=level_num; level_timer_start_ticks=pygame.time.get_ticks()
    current_thermal_spawn_rate = BASE_THERMAL_SPAWN_RATE + (THERMAL_SPAWN_RATE_INCREASE_PER_LEVEL * (current_level -1))
    thermal_spawn_timer=0
    generate_map()
    generate_new_wind() # Generate new wind for the level
    thermals_group.empty()
    
    # Reset clouds for the new wind direction
    foreground_clouds_group.empty()
    for i in range(NUM_FOREGROUND_CLOUDS): 
        foreground_clouds_group.add(ForegroundCloud(initial_distribution=True,index=i,total_clouds=NUM_FOREGROUND_CLOUDS))

    start_h = START_HEIGHT_NEW_LEVEL if current_level > 1 else INITIAL_HEIGHT
    player.reset(start_height=start_h)
    if player not in all_sprites: all_sprites.add(player)

def reset_to_main_menu():
    global game_state,current_level,final_score, current_wind_speed_x, current_wind_speed_y
    player.reset(); thermals_group.empty(); all_sprites.empty(); all_sprites.add(player)
    foreground_clouds_group.empty()
    # Set a default or no wind for menu screen clouds if desired, or use last game's wind
    current_wind_speed_x = -0.2 # Gentle default for menu
    current_wind_speed_y = 0.05
    for i in range(NUM_FOREGROUND_CLOUDS): foreground_clouds_group.add(ForegroundCloud(initial_distribution=True,index=i,total_clouds=NUM_FOREGROUND_CLOUDS))
    current_level=1; final_score=0; game_state = STATE_START_SCREEN

# --- Screen Drawing Functions ---
def draw_start_screen_content(surface):
    surface.fill(DARK_GRAY)
    draw_text(surface, "Pastel Glider", 64, SCREEN_WIDTH//2, SCREEN_HEIGHT//4 - 40, COLOR_PLAINS, center=True)
    draw_text(surface, "Reach 1000m to advance!", 26, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 120, WHITE, center=True)
    draw_text(surface, "UP/DOWN: Speed | L/R: Bank", 22, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80, WHITE, center=True)
    draw_text(surface, f"Stall < {STALL_SPEED:.1f} speed (no thermal lift!)", 22, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50, WHITE, center=True)
    draw_text(surface, "K_DOWN: Speed for Height | Diving: Height for Speed", 22, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20, WHITE, center=True)
    draw_text(surface, "Small thermals: strong/short. Large: gentle/long.", 22, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 10, WHITE, center=True)
    draw_text(surface, "Thermals rarer & Wind changes each level!", 22, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40, WHITE, center=True)
    draw_text(surface, "ENTER to Start", 30, SCREEN_WIDTH//2, SCREEN_HEIGHT*3//4 + 20, LIGHT_GRAY, center=True)
    draw_text(surface, "ESC for Menu", 20, SCREEN_WIDTH//2, SCREEN_HEIGHT*3//4 + 60, GRAY, center=True)


def draw_level_complete_screen(surface, level, time_taken_seconds):
    surface.fill(DARK_GRAY)
    draw_text(surface, f"Level {level} Complete!", 60, SCREEN_WIDTH//2, SCREEN_HEIGHT//3, GOLD, center=True)
    draw_text(surface, f"Time: {time_taken_seconds:.1f}s", 36, SCREEN_WIDTH//2, SCREEN_HEIGHT//2, WHITE, center=True)
    draw_text(surface, "Press ENTER for Next Level", 36, SCREEN_WIDTH//2, SCREEN_HEIGHT*2//3, LIGHT_GRAY, center=True)

def draw_game_over_screen_content(surface, score, level):
    surface.fill(DARK_GRAY)
    draw_text(surface, "GAME OVER", 72, SCREEN_WIDTH//2, SCREEN_HEIGHT//3, RED, center=True)
    draw_text(surface, f"Reached Level: {level}", 36, SCREEN_WIDTH//2, SCREEN_HEIGHT//2-30, WHITE, center=True)
    draw_text(surface, f"Final Height: {int(score)}m", 36, SCREEN_WIDTH//2, SCREEN_HEIGHT//2+10, WHITE, center=True)
    draw_text(surface, "ENTER for Menu", 32, SCREEN_WIDTH//2, SCREEN_HEIGHT*2//3, LIGHT_GRAY, center=True)

def draw_height_indicator_hud(surface, current_player_height, target_h):
    indicator_bar_height = SCREEN_HEIGHT - HUD_HEIGHT - (2 * INDICATOR_Y_MARGIN_FROM_HUD)
    indicator_x_pos = SCREEN_WIDTH - INDICATOR_WIDTH - INDICATOR_X_MARGIN
    indicator_y_pos = HUD_HEIGHT + INDICATOR_Y_MARGIN_FROM_HUD
    pygame.draw.rect(surface, INDICATOR_COLOR, (indicator_x_pos, indicator_y_pos, INDICATOR_WIDTH, indicator_bar_height))
    max_indicator_height_value = target_h * 1.1
    pygame.draw.line(surface, INDICATOR_GROUND_COLOR, (indicator_x_pos-5, indicator_y_pos+indicator_bar_height), (indicator_x_pos+INDICATOR_WIDTH+5, indicator_y_pos+indicator_bar_height), 3)
    draw_text(surface, "0m", 14, indicator_x_pos+INDICATOR_WIDTH+8, indicator_y_pos+indicator_bar_height-7, WHITE)
    target_marker_y_on_bar = indicator_y_pos
    if max_indicator_height_value > target_h: target_marker_y_on_bar = indicator_y_pos + indicator_bar_height*(1-(target_h/max_indicator_height_value))
    pygame.draw.line(surface, INDICATOR_TARGET_COLOR, (indicator_x_pos-5, target_marker_y_on_bar), (indicator_x_pos+INDICATOR_WIDTH+5, target_marker_y_on_bar), 3)
    draw_text(surface, f"{target_h}m", 14, indicator_x_pos+INDICATOR_WIDTH+8, target_marker_y_on_bar-7, INDICATOR_TARGET_COLOR)
    if current_player_height > 0:
        player_height_ratio = min(current_player_height / max_indicator_height_value, 1.0)
        player_marker_y_on_bar = indicator_y_pos + indicator_bar_height * (1 - player_height_ratio)
        pygame.draw.line(surface, INDICATOR_PLAYER_COLOR, (indicator_x_pos, player_marker_y_on_bar), (indicator_x_pos+INDICATOR_WIDTH, player_marker_y_on_bar), 5)
        text_y = player_marker_y_on_bar - 7
        if abs(text_y - (indicator_y_pos+indicator_bar_height-7)) < 15 : text_y -=15
        if abs(text_y - (target_marker_y_on_bar-7)) < 15 : text_y +=15
        draw_text(surface, f"{int(current_player_height)}m", 14, indicator_x_pos-35, text_y, INDICATOR_PLAYER_COLOR)

# --- Game Loop ---
running = True
while running:
    dt = clock.tick(60) / 1000.0
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

    if game_state == STATE_PLAYING:
        keys = pygame.key.get_pressed()
        player.update(keys)
        thermals_group.update()
        foreground_clouds_group.update()

        if len(foreground_clouds_group) < NUM_FOREGROUND_CLOUDS:
            foreground_clouds_group.add(ForegroundCloud())

        thermal_spawn_timer += 1
        if thermal_spawn_timer >= current_thermal_spawn_rate:
            thermal_spawn_timer = 0
            try_x = random.randint(MAX_THERMAL_RADIUS, SCREEN_WIDTH - MAX_THERMAL_RADIUS)
            try_y = random.randint(MAX_THERMAL_RADIUS, SCREEN_HEIGHT - MAX_THERMAL_RADIUS)
            land_type = get_land_type_at_pos(try_x, try_y)
            if random.random() < LAND_TYPE_THERMAL_PROBABILITY.get(land_type, 0.0):
                new_thermal = Thermal((try_x, try_y))
                all_sprites.add(new_thermal); thermals_group.add(new_thermal)

        player_pos_vec = pygame.math.Vector2(player.rect.centerx, player.rect.centery)
        for thermal in thermals_group:
            distance_to_thermal_center = player_pos_vec.distance_to(thermal.rect.center) 
            if distance_to_thermal_center < thermal.radius + player.radius * 0.3: 
                player.apply_lift_from_thermal(thermal.lift_power)

        if player.height >= TARGET_HEIGHT_PER_LEVEL: game_state = STATE_LEVEL_COMPLETE
        if player.height <= 0: final_score = player.height; player.height = 0; game_state = STATE_GAME_OVER

    # --- Drawing ---
    screen.fill(BLACK) 
    if game_state == STATE_START_SCREEN:
        draw_start_screen_content(screen)
        foreground_clouds_group.draw(screen) # Draw clouds on start screen too
    elif game_state == STATE_LEVEL_COMPLETE:
        draw_level_complete_screen(screen, current_level, (current_ticks-level_timer_start_ticks)/1000.0)
        foreground_clouds_group.draw(screen) # Clouds on level complete screen
    elif game_state == STATE_PLAYING:
        draw_map(screen)
        player.draw_contrail(screen) 
        for sprite in all_sprites: screen.blit(sprite.image, sprite.rect)
        foreground_clouds_group.draw(screen)

        hud_surface = pygame.Surface((SCREEN_WIDTH, HUD_HEIGHT), pygame.SRCALPHA); hud_surface.fill(HUD_PANEL_COLOR); screen.blit(hud_surface, (0,0))
        text_color_on_hud = WHITE; hud_margin = 10; line_spacing = 22; current_y = hud_margin
        draw_text(screen, f"Level: {current_level}", 20, hud_margin, current_y, text_color_on_hud)
        draw_text(screen, f"Target: {TARGET_HEIGHT_PER_LEVEL}m", 20, hud_margin + 120, current_y, text_color_on_hud)
        current_y += line_spacing
        timer_seconds = (current_ticks - level_timer_start_ticks) / 1000.0
        draw_text(screen, f"Time: {timer_seconds:.1f}s", 20, hud_margin, current_y, text_color_on_hud)
        current_y += line_spacing
        draw_text(screen, f"Height: {int(player.height)}m", 20, hud_margin, current_y, text_color_on_hud)
        draw_text(screen, f"Speed: {player.speed:.1f}", 20, hud_margin + 120, current_y, text_color_on_hud)
        
        if player.speed < STALL_SPEED: draw_text(screen, "STALL!", 24, SCREEN_WIDTH//2, hud_margin + line_spacing//2, RED, center=True)
        
        # Display current wind (scaled for readability)
        wind_display_text = f"Wind: <{current_wind_speed_x*10:.0f}, {current_wind_speed_y*10:.0f}>"
        draw_text(screen, wind_display_text, 18, SCREEN_WIDTH - 200, hud_margin + 5, text_color_on_hud)
        draw_text(screen, "ESC for Menu", 18, SCREEN_WIDTH - 200, hud_margin + 5 + line_spacing, text_color_on_hud)
        draw_height_indicator_hud(screen, player.height, TARGET_HEIGHT_PER_LEVEL)
    elif game_state == STATE_GAME_OVER:
        draw_game_over_screen_content(screen, final_score, current_level)
        foreground_clouds_group.draw(screen) # Clouds on game over screen

    pygame.display.flip()
pygame.quit()
