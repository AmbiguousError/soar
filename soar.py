import pygame
import math
import random

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

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
THERMAL_SPAWN_BASE_RATE = 90
MIN_THERMAL_RADIUS = 20
MAX_THERMAL_RADIUS = 50

# New Thermal Characteristics based on size
MIN_THERMAL_LIFESPAN = 400   # Lifespan of the smallest thermals (frames)
MAX_THERMAL_LIFESPAN = 1200  # Lifespan of the largest thermals (frames)
MIN_THERMAL_LIFT_POWER = 0.20 # Lift power of the largest thermals (gentle)
MAX_THERMAL_LIFT_POWER = 0.55 # Lift power of the smallest thermals (strong)


# Map
TILE_SIZE = 40
MAP_GRID_WIDTH = SCREEN_WIDTH // TILE_SIZE
MAP_GRID_HEIGHT = SCREEN_HEIGHT // TILE_SIZE

# Wind
WIND_SPEED_X = -0.5
WIND_SPEED_Y = 0.05

# Clouds
NUM_FOREGROUND_CLOUDS = 10
MIN_CLOUD_SPEED_FACTOR = 1.5
MAX_CLOUD_SPEED_FACTOR = 2.5
CLOUD_MIN_ALPHA = 40
CLOUD_MAX_ALPHA = 100

# --- Game States ---
STATE_START_SCREEN = 0
STATE_PLAYING = 1
STATE_GAME_OVER = 2

# --- Colors ---
BLACK = (0, 0, 0); WHITE = (255, 255, 255); DARK_GRAY = (64, 64, 64)
GRAY = (150, 150, 150); LIGHT_GRAY = (200, 200, 200); RED = (255, 0, 0)
CLOUD_COLOR = (220, 220, 240)

COLOR_WATER = (173, 216, 230); COLOR_PLAINS = (170, 238, 170)
COLOR_FOREST = (144, 200, 144); COLOR_MOUNTAIN_BASE = (200, 200, 180)
COLOR_SAND = (245, 222, 179)

GLIDER_BODY_COLOR = (100, 100, 230); GLIDER_WING_COLOR = (150, 150, 255)

THERMAL_COLOR_PRIMARY_TUPLE = (255, 150, 150); THERMAL_COLOR_ACCENT_TUPLE = (255, 255, 255)
THERMAL_BASE_ALPHA = 100; THERMAL_ACCENT_ALPHA = 120

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

    def reset(self):
        self.x = float(SCREEN_WIDTH // 2); self.y = float(SCREEN_HEIGHT // 2)
        self.rect.center = (round(self.x), round(self.y))
        self.heading = 0; self.bank_angle = 0
        self.height = INITIAL_HEIGHT; self.speed = INITIAL_SPEED
        self.trail_points = []; self.contrail_frame_counter = 0
        self.image = pygame.transform.rotate(self.original_image, -self.heading)

    def update(self, keys):
        if keys[pygame.K_UP]:
            self.speed += ACCELERATION
        elif keys[pygame.K_DOWN]:
            potential_new_speed = self.speed - ACCELERATION
            if potential_new_speed >= MIN_SPEED:
                self.speed = potential_new_speed
                height_gain_from_zoom = ACCELERATION * ZOOM_CLIMB_FACTOR
                self.height += height_gain_from_zoom
            else:
                self.speed = MIN_SPEED
        self.speed = max(MIN_SPEED, min(self.speed, MAX_SPEED))

        if keys[pygame.K_LEFT]: self.bank_angle -= BANK_RATE
        elif keys[pygame.K_RIGHT]: self.bank_angle += BANK_RATE
        else: self.bank_angle *= 0.95
        if abs(self.bank_angle) < 0.1: self.bank_angle = 0
        self.bank_angle = max(-MAX_BANK_ANGLE, min(self.bank_angle, MAX_BANK_ANGLE))

        turn_rate_degrees = self.bank_angle * TURN_RATE_SCALAR
        self.heading = (self.heading + turn_rate_degrees) % 360

        heading_rad = math.radians(self.heading)
        self.x += self.speed * math.cos(heading_rad)
        self.y += self.speed * math.sin(heading_rad)

        self.image = pygame.transform.rotate(self.original_image, -self.heading)
        self.rect = self.image.get_rect(center=(round(self.x), round(self.y)))

        height_change_due_to_physics = 0
        if self.speed < STALL_SPEED:
            height_change_due_to_physics = -GRAVITY_BASE_PULL - STALL_SINK_PENALTY
        else:
            lift_from_airspeed = self.speed * LIFT_PER_SPEED_UNIT
            net_vertical_force = lift_from_airspeed - GRAVITY_BASE_PULL
            if net_vertical_force < 0:
                height_change_due_to_physics = max(net_vertical_force, -MINIMUM_SINK_RATE)
            else:
                height_change_due_to_physics = net_vertical_force
        self.height += height_change_due_to_physics

        if height_change_due_to_physics < 0:
            speed_gain_from_dive = abs(height_change_due_to_physics) * DIVE_TO_SPEED_FACTOR
            self.speed = min(self.speed + speed_gain_from_dive, MAX_SPEED)

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
        lift_this_frame = thermal_lift_power_at_nominal_speed * (INITIAL_SPEED / max(self.speed, MIN_SPEED * 0.5))
        lift_this_frame = max(lift_this_frame, thermal_lift_power_at_nominal_speed * 0.2)
        self.height += lift_this_frame

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
        
        # --- Determine lifespan and lift power based on radius ---
        # Normalized radius (0.0 for min_radius, 1.0 for max_radius)
        if MAX_THERMAL_RADIUS == MIN_THERMAL_RADIUS: # Avoid division by zero if radii are the same
            normalized_radius = 0.5
        else:
            normalized_radius = (self.radius - MIN_THERMAL_RADIUS) / (MAX_THERMAL_RADIUS - MIN_THERMAL_RADIUS)

        # Lifespan: Larger thermals live longer
        self.lifespan = MIN_THERMAL_LIFESPAN + (MAX_THERMAL_LIFESPAN - MIN_THERMAL_LIFESPAN) * normalized_radius
        
        # Lift Power: Smaller thermals are stronger (inverse relationship with normalized_radius)
        self.lift_power = MAX_THERMAL_LIFT_POWER - (MAX_THERMAL_LIFT_POWER - MIN_THERMAL_LIFT_POWER) * normalized_radius
        
        self.image = pygame.Surface([self.radius * 2, self.radius * 2], pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=center_pos)
        self.creation_time = pygame.time.get_ticks()
        self.update_visuals() # Initial draw

    def update_visuals(self):
        pulse_alpha_factor = (math.sin(pygame.time.get_ticks() * 0.005 + self.creation_time * 0.01) * 0.3 + 0.7)
        # Use the dynamically set self.lifespan for age calculation
        # Ensure self.lifespan is not zero if it was just set (e.g. during init before first update)
        current_lifespan_for_age = self.lifespan if hasattr(self, 'lifespan') and self.lifespan > 0 else MAX_THERMAL_LIFESPAN
        # We need the initial lifespan to correctly calculate age_factor
        # This requires storing the initial_lifespan or recalculating normalized_radius
        # For simplicity, let's assume the current self.lifespan is the remaining, and THERMAL_LIFESPAN_BASE was the start
        # This is tricky. Let's store initial_lifespan.
        if not hasattr(self, 'initial_lifespan'): # Store it once
            self.initial_lifespan = self.lifespan

        age_factor = max(0, self.lifespan / self.initial_lifespan if self.initial_lifespan > 0 else 0)
        
        alpha = int(THERMAL_BASE_ALPHA * pulse_alpha_factor * age_factor)
        accent_alpha = int(THERMAL_ACCENT_ALPHA * pulse_alpha_factor * age_factor)
        visual_radius_factor = math.sin(pygame.time.get_ticks() * 0.002 + self.creation_time * 0.005) * 0.1 + 0.95
        current_visual_radius = int(self.radius * visual_radius_factor)
        self.image.fill((0,0,0,0))
        pygame.draw.circle(self.image, (*THERMAL_COLOR_PRIMARY_TUPLE, alpha), (self.radius, self.radius), current_visual_radius)
        pygame.draw.circle(self.image, (*THERMAL_COLOR_ACCENT_TUPLE, accent_alpha), (self.radius, self.radius), int(current_visual_radius * 0.7), 2)

    def update(self):
        self.lifespan -= 1
        if self.lifespan <= 0: self.kill()
        else: self.update_visuals()

# --- ForegroundCloud Class ---
class ForegroundCloud(pygame.sprite.Sprite):
    def __init__(self, initial_distribution=False, index=0, total_clouds=1):
        super().__init__()
        self.width = random.randint(100, 250)
        self.height = random.randint(40, 80)
        self.image = pygame.Surface([self.width, self.height], pygame.SRCALPHA)
        
        num_puffs = random.randint(4, 7)
        for _ in range(num_puffs):
            puff_w = random.randint(int(self.width*0.4), int(self.width*0.8))
            puff_h = random.randint(int(self.height*0.5), int(self.height*0.9))
            puff_x = random.randint(0, self.width - puff_w)
            puff_y = random.randint(0, self.height - puff_h)
            alpha = random.randint(CLOUD_MIN_ALPHA, CLOUD_MAX_ALPHA)
            pygame.draw.ellipse(self.image, (*CLOUD_COLOR, alpha), (puff_x, puff_y, puff_w, puff_h))

        self.speed_factor = random.uniform(MIN_CLOUD_SPEED_FACTOR, MAX_CLOUD_SPEED_FACTOR)
        self.dx = WIND_SPEED_X * self.speed_factor
        self.dy = WIND_SPEED_Y * self.speed_factor

        if initial_distribution:
            self.x = (index / total_clouds) * SCREEN_WIDTH - self.width / 2 + random.uniform(-SCREEN_WIDTH/(total_clouds*2), SCREEN_WIDTH/(total_clouds*2))
            self.y = random.randint(-self.height // 2, SCREEN_HEIGHT - self.height // 2)
            self.rect = self.image.get_rect(topleft=(self.x, self.y))
        else: 
            if self.dx < 0: start_x = SCREEN_WIDTH + random.randint(0, 100) + self.width / 2
            else: start_x = -random.randint(0, 100) - self.width / 2
            if self.dy < 0: start_y = SCREEN_HEIGHT + random.randint(0,50) + self.height / 2
            elif self.dy > 0: start_y = -random.randint(0,50) - self.height / 2
            else: start_y = random.randint(0, SCREEN_HEIGHT - self.height)
            self.rect = self.image.get_rect(center=(start_x, start_y))
        
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)

    def update(self):
        self.x += self.dx; self.y += self.dy
        self.rect.topleft = (round(self.x), round(self.y))

        off_screen_margin = self.width * 1.5 
        if self.dx < 0 and self.rect.right < -off_screen_margin: self.kill()
        elif self.dx > 0 and self.rect.left > SCREEN_WIDTH + off_screen_margin: self.kill()
        if self.dy < 0 and self.rect.bottom < -off_screen_margin : self.kill()
        elif self.dy > 0 and self.rect.top > SCREEN_HEIGHT + off_screen_margin : self.kill()

# --- Map Data & Functions ---
map_data = []
def generate_map():
    global map_data; map_data = []
    land_types = [LandType.WATER, LandType.PLAINS, LandType.FOREST, LandType.MOUNTAIN_BASE, LandType.SAND]
    weights =    [0.15, 0.35, 0.20, 0.15, 0.15]
    for _ in range(MAP_GRID_HEIGHT):
        map_data.append(random.choices(land_types, weights=weights, k=MAP_GRID_WIDTH))

def get_land_type_at_pos(world_x, world_y):
    grid_x = int(world_x // TILE_SIZE) % MAP_GRID_WIDTH
    grid_y = int(world_y // TILE_SIZE) % MAP_GRID_HEIGHT
    return map_data[grid_y][grid_x]

def draw_map(surface):
    for r_idx, row in enumerate(map_data):
        for c_idx, tile_type in enumerate(row):
            color = LAND_TYPE_COLORS.get(tile_type, BLACK)
            rect = pygame.Rect(c_idx * TILE_SIZE, r_idx * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(surface, color, rect)

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
pygame.display.set_caption("Pastel Glider - Dynamic Thermals")
clock = pygame.time.Clock()

# --- Game Objects & Variables ---
player = Glider()
all_sprites = pygame.sprite.Group()
thermals_group = pygame.sprite.Group()
foreground_clouds_group = pygame.sprite.Group()
game_state = STATE_START_SCREEN
thermal_spawn_timer = 0; final_score = 0
generate_map()

def reset_game_state():
    global thermal_spawn_timer, final_score
    player.reset(); thermals_group.empty(); all_sprites.empty(); foreground_clouds_group.empty()
    all_sprites.add(player)
    for i in range(NUM_FOREGROUND_CLOUDS):
        cloud = ForegroundCloud(initial_distribution=True, index=i, total_clouds=NUM_FOREGROUND_CLOUDS)
        foreground_clouds_group.add(cloud)
    thermal_spawn_timer = 0; final_score = 0

# --- Screen Drawing Functions ---
def draw_start_screen_content(surface):
    surface.fill(DARK_GRAY)
    draw_text(surface, "Pastel Glider", 64, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 - 30, COLOR_PLAINS, center=True)
    draw_text(surface, "UP/DOWN: Speed | LEFT/RIGHT: Bank", 24, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100, WHITE, center=True)
    draw_text(surface, f"Beware of stalling below {STALL_SPEED:.1f} speed!", 24, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 65, WHITE, center=True)
    draw_text(surface, "Pull UP (K_DOWN) to trade speed for height.", 24, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30, WHITE, center=True)
    draw_text(surface, "Diving converts height loss to speed.", 24, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 5, WHITE, center=True)
    draw_text(surface, "Small thermals: strong, short lift. Large: gentle, long.", 24, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40, WHITE, center=True)
    draw_text(surface, "Don't hit height zero!", 24, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 75, WHITE, center=True)
    draw_text(surface, "Press ENTER to Start", 32, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4 + 40, LIGHT_GRAY, center=True)
    draw_text(surface, "ESC during game for Menu", 20, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4 + 80, GRAY, center=True)

def draw_game_over_screen_content(surface, score):
    surface.fill(DARK_GRAY)
    draw_text(surface, "GAME OVER", 72, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3, RED, center=True)
    draw_text(surface, f"Final Height: {int(score)} m", 40, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, WHITE, center=True)
    draw_text(surface, "Press ENTER to Return to Menu", 36, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3, LIGHT_GRAY, center=True)

# --- Game Loop ---
running = True
while running:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if game_state == STATE_START_SCREEN and event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            reset_game_state(); game_state = STATE_PLAYING
        elif game_state == STATE_PLAYING and event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            game_state = STATE_START_SCREEN
        elif game_state == STATE_GAME_OVER and event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            game_state = STATE_START_SCREEN

    if game_state == STATE_PLAYING:
        keys = pygame.key.get_pressed()
        player.update(keys)
        thermals_group.update()
        foreground_clouds_group.update()

        if len(foreground_clouds_group) < NUM_FOREGROUND_CLOUDS:
            cloud = ForegroundCloud() 
            foreground_clouds_group.add(cloud)

        thermal_spawn_timer += 1
        if thermal_spawn_timer >= THERMAL_SPAWN_BASE_RATE:
            thermal_spawn_timer = 0
            try_x = random.randint(MAX_THERMAL_RADIUS, SCREEN_WIDTH - MAX_THERMAL_RADIUS)
            try_y = random.randint(MAX_THERMAL_RADIUS, SCREEN_HEIGHT - MAX_THERMAL_RADIUS)
            land_type = get_land_type_at_pos(try_x, try_y)
            if random.random() < LAND_TYPE_THERMAL_PROBABILITY.get(land_type, 0.0):
                new_thermal = Thermal((try_x, try_y))
                all_sprites.add(new_thermal); thermals_group.add(new_thermal)

        player_pos_vec = pygame.math.Vector2(player.rect.center)
        for thermal in thermals_group:
            distance_to_thermal_center = player_pos_vec.distance_to(thermal.pos)
            if distance_to_thermal_center < thermal.radius + player.radius * 0.3: 
                player.apply_lift_from_thermal(thermal.lift_power)

        if player.height <= 0:
            final_score = player.height; player.height = 0
            game_state = STATE_GAME_OVER

    # --- Drawing ---
    screen.fill(BLACK) 
    if game_state == STATE_START_SCREEN:
        draw_start_screen_content(screen)
    elif game_state == STATE_PLAYING:
        draw_map(screen)
        player.draw_contrail(screen)
        all_sprites.draw(screen) 
        foreground_clouds_group.draw(screen)

        draw_text(screen, f"Speed: {player.speed:.1f}", 24, 10, 10, BLACK)
        draw_text(screen, f"Bank: {int(player.bank_angle)}°", 24, 10, 35, BLACK)
        draw_text(screen, f"Heading: {int(player.heading)}°", 24, 10, 60, BLACK)
        draw_text(screen, f"Height: {int(player.height)} m", 24, 10, 85, BLACK)
        if player.speed < STALL_SPEED:
             draw_text(screen, "STALL!", 26, SCREEN_WIDTH // 2, 10, RED, center=True)
        wind_display_text = f"Wind: <{WIND_SPEED_X*10:.0f}, {WIND_SPEED_Y*10:.0f}>"
        draw_text(screen, wind_display_text, 18, SCREEN_WIDTH - 150, 10, BLACK)
        draw_text(screen, "ESC for Menu", 18, SCREEN_WIDTH - 150, 30, BLACK)
    elif game_state == STATE_GAME_OVER:
        draw_game_over_screen_content(screen, final_score)

    pygame.display.flip()
pygame.quit()
