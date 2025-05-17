import pygame
import math
import random

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Glider Physics & Control
INITIAL_HEIGHT = 500       # Start with some altitude
INITIAL_SPEED = 3
MIN_SPEED = 1.0            # Lowered min speed for thermal strategy
MAX_SPEED = 7              # Increased max speed
ACCELERATION = 0.12        # Speed change per key press

# Gravity and Lift
GRAVITY_BASE_PULL = 0.18   # Increased base gravitational pull (was 0.08)
LIFT_PER_SPEED_UNIT = 0.03 # How much lift is generated per unit of speed, counteracting gravity
MINIMUM_SINK_RATE = 0.02   # Glider will always sink at least this much per frame outside thermals

MAX_BANK_ANGLE = 45
BANK_RATE = 2
TURN_RATE_SCALAR = 0.1

# Contrail
CONTRAIL_LENGTH = 60
CONTRAIL_POINT_DELAY = 2

# Thermals
THERMAL_SPAWN_BASE_RATE = 80
THERMAL_LIFESPAN = 700
THERMAL_RADIUS = 25
BASE_THERMAL_STRENGTH = 75 # Renamed from THERMAL_STRENGTH, slightly increased base
# THERMAL_SPEED_EFFECT_FACTOR is implicitly handled by the division in collision logic

# Map
TILE_SIZE = 40
MAP_GRID_WIDTH = SCREEN_WIDTH // TILE_SIZE
MAP_GRID_HEIGHT = SCREEN_HEIGHT // TILE_SIZE

# --- Game States ---
STATE_START_SCREEN = 0
STATE_PLAYING = 1
STATE_GAME_OVER = 2

# --- Colors ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_GRAY = (64, 64, 64) # Standard DARK_GRAY from search
GRAY = (150, 150, 150) # Contrail
LIGHT_GRAY = (200, 200, 200)
RED = (255, 0, 0) # Game Over Text

# Pastel Land Type Colors
COLOR_WATER = (173, 216, 230)
COLOR_PLAINS = (170, 238, 170)
COLOR_FOREST = (144, 200, 144)
COLOR_MOUNTAIN_BASE = (200, 200, 180)
COLOR_SAND = (245, 222, 179)

# Glider Colors
GLIDER_BODY_COLOR = (80, 80, 220)
GLIDER_WING_COLOR = (120, 120, 255)

THERMAL_COLOR_PRIMARY = (255, 150, 150, 100)
THERMAL_COLOR_ACCENT = (255, 255, 255, 120)

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
        
        glider_surface_width = 60 
        glider_surface_height = 30 
        self.original_image = pygame.Surface([glider_surface_width, glider_surface_height], pygame.SRCALPHA)

        self.fuselage_length = 45 # Store as instance attribute
        fuselage_thickness = 5 
        wing_span = 60 
        wing_chord = 6 
        tail_plane_span = 18
        tail_plane_chord = 5
        tail_fin_height = 8
        
        fuselage_y_top = (glider_surface_height - fuselage_thickness) / 2
        
        fuselage_rect = pygame.Rect(glider_surface_width - self.fuselage_length, fuselage_y_top, self.fuselage_length, fuselage_thickness)
        pygame.draw.rect(self.original_image, GLIDER_BODY_COLOR, fuselage_rect)
        
        wing_leading_edge_x = glider_surface_width - self.fuselage_length + (self.fuselage_length * 0.35) 
        
        pygame.draw.rect(self.original_image, GLIDER_WING_COLOR, 
                         (wing_leading_edge_x, (glider_surface_height - wing_span)/2 , wing_chord, wing_span))

        tail_plane_leading_edge_x = glider_surface_width - self.fuselage_length 
        pygame.draw.rect(self.original_image, GLIDER_WING_COLOR,
                         (tail_plane_leading_edge_x, (glider_surface_height - tail_plane_span)/2, tail_plane_chord, tail_plane_span))

        fin_base_y = fuselage_y_top
        fin_tip_y = fuselage_y_top - tail_fin_height
        fin_base_start_x = tail_plane_leading_edge_x + tail_plane_chord 
        fin_base_end_x = tail_plane_leading_edge_x + tail_plane_chord + (fuselage_thickness * 1.5) 
        fin_tip_x = tail_plane_leading_edge_x + tail_plane_chord + (fuselage_thickness * 0.75)
        pygame.draw.polygon(self.original_image, GLIDER_BODY_COLOR, 
                            [(fin_base_start_x, fin_base_y), 
                             (fin_base_end_x, fin_base_y), 
                             (fin_tip_x, fin_tip_y)])

        self.image = self.original_image
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

        self.x = float(self.rect.centerx); self.y = float(self.rect.centery)
        self.heading = 0; self.bank_angle = 0
        self.height = INITIAL_HEIGHT; self.speed = INITIAL_SPEED
        
        self.trail_points = []; self.contrail_frame_counter = 0
        # self.glider_length is the surface width, used for rect calculations primarily
        self.glider_length = glider_surface_width 
        self.in_thermal_lift = 0

    def reset(self):
        self.x = float(SCREEN_WIDTH // 2); self.y = float(SCREEN_HEIGHT // 2)
        self.rect.center = (round(self.x), round(self.y))
        self.heading = 0; self.bank_angle = 0
        self.height = INITIAL_HEIGHT; self.speed = INITIAL_SPEED
        self.trail_points = []; self.contrail_frame_counter = 0
        self.image = pygame.transform.rotate(self.original_image, -self.heading)
        self.in_thermal_lift = 0

    def update(self, keys):
        self.in_thermal_lift = 0 

        # --- Speed Controls ---
        if keys[pygame.K_UP]: self.speed += ACCELERATION
        elif keys[pygame.K_DOWN]: self.speed -= ACCELERATION
        self.speed = max(MIN_SPEED, min(self.speed, MAX_SPEED))

        # --- Banking Controls ---
        if keys[pygame.K_LEFT]: self.bank_angle -= BANK_RATE
        elif keys[pygame.K_RIGHT]: self.bank_angle += BANK_RATE
        else: self.bank_angle *= 0.95
        if abs(self.bank_angle) < 0.1: self.bank_angle = 0
        self.bank_angle = max(-MAX_BANK_ANGLE, min(self.bank_angle, MAX_BANK_ANGLE))

        # --- Turning Logic ---
        turn_rate_degrees = self.bank_angle * TURN_RATE_SCALAR 
        self.heading += turn_rate_degrees
        self.heading %= 360

        # --- Movement ---
        heading_rad = math.radians(self.heading)
        self.x += self.speed * math.cos(heading_rad)
        self.y += self.speed * math.sin(heading_rad)

        self.image = pygame.transform.rotate(self.original_image, -self.heading)
        self.rect = self.image.get_rect(center=(round(self.x), round(self.y)))

        # --- Gravity and Lift Calculation ---
        lift_from_speed = self.speed * LIFT_PER_SPEED_UNIT
        natural_height_change = lift_from_speed - GRAVITY_BASE_PULL
        
        if self.in_thermal_lift <= 0: 
             self.height += max(natural_height_change, -MINIMUM_SINK_RATE if natural_height_change < 0 else natural_height_change)

        # --- Contrail ---
        self.contrail_frame_counter +=1
        if self.contrail_frame_counter >= CONTRAIL_POINT_DELAY:
            self.contrail_frame_counter = 0
            # Use self.fuselage_length here
            effective_tail_offset = (self.fuselage_length / 2) - 5 
            
            tail_offset_x = - effective_tail_offset * math.cos(heading_rad)
            tail_offset_y = - effective_tail_offset * math.sin(heading_rad)
            self.trail_points.append((self.rect.centerx + tail_offset_x, self.rect.centery + tail_offset_y))
            if len(self.trail_points) > CONTRAIL_LENGTH:
                self.trail_points.pop(0)

        # --- Screen Wrap ---
        if self.x - self.rect.width/2 > SCREEN_WIDTH: self.x = -self.rect.width/2
        if self.x + self.rect.width/2 < 0: self.x = SCREEN_WIDTH + self.rect.width/2
        if self.y - self.rect.height/2 > SCREEN_HEIGHT: self.y = -self.rect.height/2
        if self.y + self.rect.height/2 < 0: self.y = SCREEN_HEIGHT + self.rect.height/2

    def apply_thermal_lift(self, thermal_base_strength):
        lift_this_frame = thermal_base_strength * (INITIAL_SPEED / max(self.speed, MIN_SPEED * 0.5)) 
        lift_this_frame = max(lift_this_frame, thermal_base_strength * 0.2) 

        self.height += lift_this_frame
        self.in_thermal_lift += lift_this_frame

    def draw_contrail(self, surface):
        if len(self.trail_points) > 1:
            for i, point in enumerate(self.trail_points):
                alpha = int(200 * (i / CONTRAIL_LENGTH))
                temp_surface = pygame.Surface((4,4), pygame.SRCALPHA)
                pygame.draw.circle(temp_surface, (GRAY[0], GRAY[1], GRAY[2], alpha), (2,2), 2)
                surface.blit(temp_surface, (point[0]-2, point[1]-2))

# --- Thermal Class ---
class Thermal(pygame.sprite.Sprite):
    def __init__(self, center_pos):
        super().__init__()
        self.radius = THERMAL_RADIUS
        self.image = pygame.Surface([self.radius * 2, self.radius * 2], pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=center_pos)
        self.lifespan = THERMAL_LIFESPAN
        self.creation_time = pygame.time.get_ticks()

    def update(self):
        self.lifespan -= 1
        if self.lifespan <= 0: self.kill()

        pulse_alpha_factor = (math.sin(pygame.time.get_ticks() * 0.005 + self.creation_time * 0.01) * 0.3 + 0.7)
        base_alpha = THERMAL_COLOR_PRIMARY[3]
        alpha = int(base_alpha * pulse_alpha_factor * (self.lifespan / THERMAL_LIFESPAN))
        
        current_radius_factor = math.sin(pygame.time.get_ticks() * 0.002 + self.creation_time * 0.005) * 0.1 + 0.95
        current_radius = int(self.radius * current_radius_factor)

        self.image.fill((0,0,0,0))
        pygame.draw.circle(self.image, (*THERMAL_COLOR_PRIMARY[:3], alpha), (self.radius, self.radius), current_radius)
        pygame.draw.circle(self.image, (*THERMAL_COLOR_ACCENT[:3], int(alpha*1.2)), (self.radius, self.radius), int(current_radius * 0.7), 2)

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
pygame.display.set_caption("Pastel Glider - Advanced Physics")
clock = pygame.time.Clock()

# --- Game Objects & Variables ---
player = Glider()
all_sprites = pygame.sprite.Group(); thermals_group = pygame.sprite.Group()
game_state = STATE_START_SCREEN
thermal_spawn_timer = 0; final_score = 0
generate_map()

def reset_game_state():
    global thermal_spawn_timer, final_score
    player.reset(); thermals_group.empty(); all_sprites.empty()
    all_sprites.add(player)
    thermal_spawn_timer = 0; final_score = 0

# --- Screen Drawing Functions ---
def draw_start_screen_content(surface):
    surface.fill(DARK_GRAY)
    draw_text(surface, "Pastel Glider", 64, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4, COLOR_PLAINS, center=True)
    draw_text(surface, "UP/DOWN: Speed | LEFT/RIGHT: Bank", 28, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60, WHITE, center=True)
    draw_text(surface, "Fly slower in thermals for more lift.", 28, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20, WHITE, center=True)
    draw_text(surface, "Higher speed reduces sink rate.", 28, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20, WHITE, center=True)
    draw_text(surface, "Don't hit height zero!", 28, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60, WHITE, center=True)
    draw_text(surface, "Press ENTER to Start", 36, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4, LIGHT_GRAY, center=True)
    draw_text(surface, "ESC during game for Menu", 22, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4 + 50, GRAY, center=True)

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

    # --- Game State Logic & Updates ---
    if game_state == STATE_PLAYING:
        keys = pygame.key.get_pressed()
        player.update(keys) 
        thermals_group.update()

        # Spawn Thermals
        thermal_spawn_timer += 1
        if thermal_spawn_timer >= THERMAL_SPAWN_BASE_RATE:
            thermal_spawn_timer = 0
            try_x = random.randint(THERMAL_RADIUS, SCREEN_WIDTH - THERMAL_RADIUS)
            try_y = random.randint(THERMAL_RADIUS, SCREEN_HEIGHT - THERMAL_RADIUS)
            land_type = get_land_type_at_pos(try_x, try_y)
            if random.random() < LAND_TYPE_THERMAL_PROBABILITY.get(land_type, 0.0):
                new_thermal = Thermal((try_x, try_y))
                all_sprites.add(new_thermal); thermals_group.add(new_thermal)

        # Glider-Thermal Collision
        hit_thermals = pygame.sprite.spritecollide(player, thermals_group, True) 
        for _ in hit_thermals:
            player.apply_thermal_lift(BASE_THERMAL_STRENGTH)

        # Check for Game Over 
        if player.height <= 0:
            final_score = player.height 
            player.height = 0 
            game_state = STATE_GAME_OVER

    # --- Drawing ---
    if game_state == STATE_START_SCREEN:
        draw_start_screen_content(screen)
    elif game_state == STATE_PLAYING:
        draw_map(screen)
        player.draw_contrail(screen)
        all_sprites.draw(screen)
        draw_text(screen, f"Speed: {player.speed:.1f}", 24, 10, 10, BLACK)
        draw_text(screen, f"Bank: {int(player.bank_angle)}°", 24, 10, 35, BLACK)
        draw_text(screen, f"Heading: {int(player.heading)}°", 24, 10, 60, BLACK)
        draw_text(screen, f"Height: {int(player.height)} m", 24, 10, 85, BLACK)
        draw_text(screen, "ESC for Menu", 18, SCREEN_WIDTH - 100, 10, BLACK)
    elif game_state == STATE_GAME_OVER:
        draw_game_over_screen_content(screen, final_score)

    pygame.display.flip()
pygame.quit()
