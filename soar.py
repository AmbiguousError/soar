import pygame
import math
import random

# --- Constants ---
SCREEN_WIDTH = 1200 
SCREEN_HEIGHT = 900 
HUD_HEIGHT = 100
MINIMAP_WIDTH = 200
MINIMAP_HEIGHT = 150
MINIMAP_MARGIN = 10
MINIMAP_ALPHA = 200

# Glider Physics & Control
INITIAL_HEIGHT = 500
INITIAL_SPEED = 3
MIN_SPEED = 1.0
MAX_SPEED = 7
ACCELERATION = 0.12
STALL_SPEED = 1.8
STALL_SINK_PENALTY = 0.08
GRAVITY_BASE_PULL = 0.22
LIFT_PER_SPEED_UNIT = 0.03
MINIMUM_SINK_RATE = 0.04 
DIVE_TO_SPEED_FACTOR = 0.08
ZOOM_CLIMB_FACTOR = 1.8
MAX_BANK_ANGLE = 45
BANK_RATE = 2
TURN_RATE_SCALAR = 0.1

# Contrail
CONTRAIL_LENGTH = 60
CONTRAIL_POINT_DELAY = 2

# Thermals
BASE_THERMAL_SPAWN_RATE = 100 
THERMAL_SPAWN_RATE_INCREASE_PER_LEVEL = 18 # Used in Free Fly
NORMAL_MIN_THERMAL_RADIUS = 25
NORMAL_MAX_THERMAL_RADIUS = 60
NORMAL_MIN_THERMAL_LIFESPAN = 450 
NORMAL_MAX_THERMAL_LIFESPAN = 1300 
MIN_THERMAL_LIFT_POWER = 0.22 
MAX_THERMAL_LIFT_POWER = 0.60 
NOOB_MIN_THERMAL_RADIUS = 60
NOOB_MAX_THERMAL_RADIUS = 120
NOOB_MIN_THERMAL_LIFESPAN = 900
NOOB_MAX_THERMAL_LIFESPAN = 2200
EASY_MODE_THERMAL_LIFT_MULTIPLIER = 1.75 
NOOB_MODE_THERMAL_LIFT_MULTIPLIER = 2.75 
THERMAL_SPAWN_AREA_WIDTH = SCREEN_WIDTH + 300 
THERMAL_SPAWN_AREA_HEIGHT = SCREEN_HEIGHT + 300 
THERMAL_BASE_ALPHA = 100 
THERMAL_ACCENT_ALPHA = 120 


# Map
TILE_SIZE = 40
MAP_TILE_OUTLINE_WIDTH = 1 
current_map_offset_x = 0 
current_map_offset_y = 0 

# Race Mode Specific
RACE_MARKER_RADIUS_WORLD = 75 
RACE_MARKER_VISUAL_RADIUS_MAP = 6 # Smaller on minimap
RACE_MARKER_VISUAL_RADIUS_WORLD = 25 # Visual size in world
DEFAULT_RACE_LAPS = 3
race_course_markers = []
total_race_laps = DEFAULT_RACE_LAPS


# Wind
MAX_WIND_STRENGTH = 1.0
current_wind_speed_x = 0.0
current_wind_speed_y = 0.0

# Clouds (Screen-space effects)
NUM_FOREGROUND_CLOUDS = 15 
MIN_CLOUD_SPEED_FACTOR = 1.5
MAX_CLOUD_SPEED_FACTOR = 2.5
CLOUD_MIN_ALPHA = 40
CLOUD_MAX_ALPHA = 100

# Game Mechanics
TARGET_HEIGHT_PER_LEVEL = 1000 # For Free Fly mode
START_HEIGHT_NEW_LEVEL = 250

# Height Indicator (HUD element, screen space)
INDICATOR_WIDTH = 20
INDICATOR_X_MARGIN = 20
INDICATOR_Y_MARGIN_FROM_HUD = 20
VSI_ARROW_SIZE = 8 

# --- Game States ---
STATE_START_SCREEN = 0
STATE_DIFFICULTY_SELECT = 1 
STATE_MODE_SELECT = 2 
STATE_PLAYING_FREE_FLY = 3 
STATE_TARGET_REACHED_OPTIONS = 4 
STATE_TARGET_REACHED_CONTINUE_PLAYING = 5 
STATE_POST_GOAL_MENU = 6 
STATE_RACE_LAPS_SELECT = 7 
STATE_RACE_PLAYING = 8 
STATE_RACE_COMPLETE = 9 
STATE_GAME_OVER = 10 

# --- Game Difficulty ---
DIFFICULTY_NOOB = 0    
DIFFICULTY_EASY = 1
DIFFICULTY_NORMAL = 2
game_difficulty = DIFFICULTY_NORMAL 
difficulty_options_map = {0: "N00b", 1: "Easy", 2: "Normal"} 

# --- Game Mode ---
MODE_FREE_FLY = 0
MODE_RACE = 1
current_game_mode = MODE_FREE_FLY


# --- Pastel Colors ---
PASTEL_BLACK = (50, 50, 60) 
PASTEL_WHITE = (245, 245, 250) 
PASTEL_DARK_GRAY = (180, 180, 190) 
PASTEL_GRAY = (200, 200, 210)
PASTEL_LIGHT_GRAY = (230, 230, 240)
PASTEL_RED = (255, 150, 150) 
PASTEL_GREEN_TARGET = (173, 255, 173) 
PASTEL_GOLD = (255, 230, 150) 
PASTEL_CLOUD = (235, 240, 245) 
PASTEL_HUD_PANEL = (190, 200, 210, 180) 
PASTEL_MINIMAP_BACKGROUND = (170, 180, 190, MINIMAP_ALPHA)
PASTEL_MINIMAP_BORDER = (140, 150, 160)
PASTEL_MARKER_COLOR = (255, 170, 170) # Softer pastel red for non-active markers
PASTEL_ACTIVE_MARKER_COLOR = (173, 255, 173) # Pastel Green for active marker

PASTEL_WATER_DEEP = (190, 220, 240)    
PASTEL_WATER_SHALLOW = (210, 235, 250) 
PASTEL_PLAINS = (200, 240, 200)        
PASTEL_GRASSLAND = (190, 250, 190)     
PASTEL_FOREST_TEMPERATE = (180, 220, 180) 
PASTEL_FOREST_DENSE = (160, 200, 160)    
PASTEL_MOUNTAIN_BASE = (210, 210, 200)  
PASTEL_MOUNTAIN_PEAK = (235, 235, 240)   
PASTEL_SAND_BEACH = (250, 240, 210)    
PASTEL_SAND_DESERT = (245, 230, 200)   
PASTEL_RIVER = (200, 225, 250)         

PASTEL_GLIDER_BODY = (180, 180, 250) 
PASTEL_GLIDER_WING = (200, 200, 255) 

PASTEL_THERMAL_PRIMARY = (255, 200, 200) 
PASTEL_THERMAL_ACCENT = PASTEL_WHITE    

PASTEL_INDICATOR_COLOR = (150, 160, 170) 
PASTEL_INDICATOR_GROUND = (200, 190, 180) 
PASTEL_VSI_CLIMB = (173, 255, 173)      
PASTEL_VSI_SINK = (255, 170, 170)        
PASTEL_TEXT_COLOR_HUD = (70, 70, 80) 
PASTEL_CONTRAIL_COLOR = PASTEL_TEXT_COLOR_HUD 

MAP_TILE_OUTLINE_COLOR = (215, 220, 225) 


# --- Land Types ---
class LandType:
    WATER_DEEP = 0; WATER_SHALLOW = 1; PLAINS = 2; FOREST_TEMPERATE = 3; MOUNTAIN_BASE = 4
    SAND_DESERT = 5; MOUNTAIN_PEAK = 6; RIVER = 7; FOREST_DENSE = 8; GRASSLAND = 9; SAND_BEACH = 10

LAND_TYPE_COLORS = {
    LandType.WATER_DEEP: PASTEL_WATER_DEEP, LandType.WATER_SHALLOW: PASTEL_WATER_SHALLOW,
    LandType.PLAINS: PASTEL_PLAINS, LandType.GRASSLAND: PASTEL_GRASSLAND,
    LandType.FOREST_TEMPERATE: PASTEL_FOREST_TEMPERATE, LandType.FOREST_DENSE: PASTEL_FOREST_DENSE,
    LandType.MOUNTAIN_BASE: PASTEL_MOUNTAIN_BASE, LandType.MOUNTAIN_PEAK: PASTEL_MOUNTAIN_PEAK,
    LandType.SAND_DESERT: PASTEL_SAND_DESERT, LandType.SAND_BEACH: PASTEL_SAND_BEACH,
    LandType.RIVER: PASTEL_RIVER,
}
LAND_TYPE_THERMAL_PROBABILITY = { 
    LandType.WATER_DEEP: 0.00, LandType.WATER_SHALLOW: 0.01,
    LandType.PLAINS: 0.6, LandType.GRASSLAND: 0.7,
    LandType.FOREST_TEMPERATE: 0.3, LandType.FOREST_DENSE: 0.1,
    LandType.MOUNTAIN_BASE: 0.5, LandType.MOUNTAIN_PEAK: 0.05, 
    LandType.SAND_DESERT: 0.9, LandType.SAND_BEACH: 0.8,
    LandType.RIVER: 0.02,
}

# --- Camera ---
camera_x = 0.0
camera_y = 0.0

# --- Glider Class ---
class Glider(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.fuselage_length = 45; self.fuselage_thickness = 4
        self.wing_span = 70; self.wing_chord = 5
        self.tail_plane_span = 18; self.tail_plane_chord = 4; self.tail_fin_height = 8
        canvas_width = self.fuselage_length; canvas_height = self.wing_span
        self.original_image = pygame.Surface([canvas_width, canvas_height], pygame.SRCALPHA)
        fuselage_y_top = (canvas_height - self.fuselage_thickness) / 2
        pygame.draw.rect(self.original_image, PASTEL_GLIDER_BODY, (0, fuselage_y_top, self.fuselage_length, self.fuselage_thickness))
        wing_leading_edge_x_from_tail = self.fuselage_length * 0.65
        pygame.draw.rect(self.original_image, PASTEL_GLIDER_WING, (wing_leading_edge_x_from_tail, 0, self.wing_chord, self.wing_span))
        tail_plane_y_top = (canvas_height - self.tail_plane_span) / 2
        pygame.draw.rect(self.original_image, PASTEL_GLIDER_WING, (0, tail_plane_y_top, self.tail_plane_chord, self.tail_plane_span))
        fin_base_y = fuselage_y_top; fin_tip_y = fin_base_y - self.tail_fin_height
        fin_base_start_x = 0; fin_base_end_x = self.tail_plane_chord
        fin_tip_x = (fin_base_start_x + fin_base_end_x) / 2
        pygame.draw.polygon(self.original_image, PASTEL_GLIDER_BODY, [(fin_base_start_x, fin_base_y), (fin_base_end_x, fin_base_y), (fin_tip_x, fin_tip_y)])
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)) 
        self.radius = min(self.rect.width, self.rect.height) / 3 
        self.world_x = 0.0; self.world_y = 0.0
        self.heading = 0; self.bank_angle = 0
        self.height = INITIAL_HEIGHT; self.speed = INITIAL_SPEED
        self.previous_height = INITIAL_HEIGHT 
        self.vertical_speed = 0.0 
        self.trail_points = []; self.contrail_frame_counter = 0
        self.current_target_marker_index = 0
        self.laps_completed = 0


    def reset(self, start_height=INITIAL_HEIGHT):
        self.world_x = 0.0; self.world_y = 0.0
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2) 
        self.heading = 0; self.bank_angle = 0
        self.height = start_height; self.speed = INITIAL_SPEED
        self.previous_height = start_height
        self.vertical_speed = 0.0
        self.trail_points = []; self.contrail_frame_counter = 0
        self.current_target_marker_index = 0
        self.laps_completed = 0


    def update(self, keys):
        global current_wind_speed_x, current_wind_speed_y, game_state, race_course_markers, total_race_laps, time_taken_for_level, level_timer_start_ticks
        self.previous_height = self.height 

        if keys[pygame.K_UP]: self.speed += ACCELERATION
        elif keys[pygame.K_DOWN]:
            potential_new_speed = self.speed - ACCELERATION
            if potential_new_speed >= MIN_SPEED:
                self.speed = potential_new_speed; self.height += ACCELERATION * ZOOM_CLIMB_FACTOR
            else: self.speed = MIN_SPEED
        self.speed = max(MIN_SPEED, min(self.speed, MAX_SPEED))
        if keys[pygame.K_LEFT]: self.bank_angle -= BANK_RATE
        elif keys[pygame.K_RIGHT]: self.bank_angle += BANK_RATE
        else: self.bank_angle *= 0.95 
        if abs(self.bank_angle) < 0.1: self.bank_angle = 0
        self.bank_angle = max(-MAX_BANK_ANGLE, min(self.bank_angle, MAX_BANK_ANGLE))
        turn_rate_degrees = self.bank_angle * TURN_RATE_SCALAR * (self.speed / INITIAL_SPEED)
        self.heading = (self.heading + turn_rate_degrees) % 360
        heading_rad = math.radians(self.heading)
        self.world_x += self.speed * math.cos(heading_rad) + current_wind_speed_x
        self.world_y += self.speed * math.sin(heading_rad) + current_wind_speed_y
        self.image = pygame.transform.rotate(self.original_image, -self.heading)
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)) 
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
        
        self.vertical_speed = self.height - self.previous_height 

        self.contrail_frame_counter +=1
        if self.contrail_frame_counter >= CONTRAIL_POINT_DELAY:
            self.contrail_frame_counter = 0
            effective_tail_offset = (self.fuselage_length / 2) - 2
            tail_offset_x_world = -effective_tail_offset * math.cos(heading_rad)
            tail_offset_y_world = -effective_tail_offset * math.sin(heading_rad)
            contrail_world_x = self.world_x + tail_offset_x_world
            contrail_world_y = self.world_y + tail_offset_y_world
            self.trail_points.append((contrail_world_x, contrail_world_y))
            if len(self.trail_points) > CONTRAIL_LENGTH: self.trail_points.pop(0)

        if game_state == STATE_RACE_PLAYING and race_course_markers:
            target_marker = race_course_markers[self.current_target_marker_index]
            dist_to_marker = math.hypot(self.world_x - target_marker.world_pos.x, self.world_y - target_marker.world_pos.y)
            if dist_to_marker < target_marker.world_radius: 
                self.current_target_marker_index += 1
                if self.current_target_marker_index >= len(race_course_markers):
                    self.laps_completed += 1
                    self.current_target_marker_index = 0
                    if self.laps_completed >= total_race_laps:
                        game_state = STATE_RACE_COMPLETE
                        race_end_ticks = pygame.time.get_ticks()
                        time_taken_for_level = (race_end_ticks - level_timer_start_ticks) / 1000.0 

    def apply_lift_from_thermal(self, thermal_lift_power_at_nominal_speed):
        global game_difficulty
        if self.speed < STALL_SPEED: return 
        
        actual_lift_power = thermal_lift_power_at_nominal_speed
        if game_difficulty == DIFFICULTY_EASY:
            actual_lift_power *= EASY_MODE_THERMAL_LIFT_MULTIPLIER
        elif game_difficulty == DIFFICULTY_NOOB:
            actual_lift_power *= NOOB_MODE_THERMAL_LIFT_MULTIPLIER

        lift_this_frame = actual_lift_power * (INITIAL_SPEED / max(self.speed, MIN_SPEED * 0.5))
        self.height += max(lift_this_frame, actual_lift_power * 0.2)

    def draw_contrail(self, surface, cam_x, cam_y):
        if len(self.trail_points) > 1:
            for i, world_point in enumerate(self.trail_points):
                alpha = int(200 * (i / CONTRAIL_LENGTH))
                contrail_dot_color = (*PASTEL_CONTRAIL_COLOR, alpha) 
                temp_surface = pygame.Surface((4,4), pygame.SRCALPHA)
                pygame.draw.circle(temp_surface, contrail_dot_color, (2,2), 2)
                screen_px = world_point[0] - cam_x; screen_py = world_point[1] - cam_y
                surface.blit(temp_surface, (screen_px - 2, screen_py - 2))

# --- Thermal Class ---
class Thermal(pygame.sprite.Sprite):
    def __init__(self, world_center_pos):
        super().__init__()
        global game_difficulty 
        self.world_pos = pygame.math.Vector2(world_center_pos)

        min_r, max_r, min_l, max_l = NORMAL_MIN_THERMAL_RADIUS, NORMAL_MAX_THERMAL_RADIUS, NORMAL_MIN_THERMAL_LIFESPAN, NORMAL_MAX_THERMAL_LIFESPAN
        if game_difficulty == DIFFICULTY_NOOB:
            min_r, max_r, min_l, max_l = NOOB_MIN_THERMAL_RADIUS, NOOB_MAX_THERMAL_RADIUS, NOOB_MIN_THERMAL_LIFESPAN, NOOB_MAX_THERMAL_LIFESPAN
        
        self.radius = random.randint(min_r, max_r)
        if max_r == min_r: normalized_radius = 0.5 
        else: normalized_radius = (self.radius - min_r) / (max_r - min_r)
        
        self.lifespan = min_l + (max_l - min_l) * normalized_radius
        self.initial_lifespan = self.lifespan
        self.lift_power = MAX_THERMAL_LIFT_POWER - (MAX_THERMAL_LIFT_POWER - MIN_THERMAL_LIFT_POWER) * normalized_radius
        
        self.image = pygame.Surface([self.radius * 2, self.radius * 2], pygame.SRCALPHA)
        self.rect = self.image.get_rect()
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
        pygame.draw.circle(self.image, (*PASTEL_THERMAL_PRIMARY, alpha), (self.radius, self.radius), current_visual_radius)
        pygame.draw.circle(self.image, (*PASTEL_THERMAL_ACCENT, accent_alpha), (self.radius, self.radius), int(current_visual_radius*0.7), 2)

    def update(self, cam_x, cam_y):
        self.lifespan -= 1
        if self.lifespan <= 0: self.kill()
        else: self.update_visuals()
        self.rect.centerx = self.world_pos.x - cam_x
        self.rect.centery = self.world_pos.y - cam_y

# --- RaceMarker Class ---
class RaceMarker(pygame.sprite.Sprite):
    def __init__(self, world_x, world_y, number):
        super().__init__()
        self.world_pos = pygame.math.Vector2(world_x, world_y)
        self.number = number
        self.world_radius = RACE_MARKER_RADIUS_WORLD  
        self.visual_radius = RACE_MARKER_VISUAL_RADIUS_WORLD 
        
        self.image = pygame.Surface((self.visual_radius * 2, self.visual_radius * 2), pygame.SRCALPHA)
        # Initial draw, will be updated in update method based on active status
        self.rect = self.image.get_rect()
        self._draw_marker_image(False) # Initial draw as non-active

    def _draw_marker_image(self, is_active):
        color_to_use = PASTEL_ACTIVE_MARKER_COLOR if is_active else PASTEL_MARKER_COLOR
        # Make marker 1 (start/finish) always a bit distinct if it's the active one
        if is_active and self.number == 1:
            color_to_use = PASTEL_GOLD # Gold for active start/finish

        self.image.fill((0,0,0,0)) 
        pygame.draw.circle(self.image, color_to_use, (self.visual_radius, self.visual_radius), self.visual_radius)
        pygame.draw.circle(self.image, PASTEL_WHITE, (self.visual_radius, self.visual_radius), int(self.visual_radius * 0.7)) # Inner circle
        
        font = pygame.font.Font(None, int(self.visual_radius * 1.1)) 
        text_surf = font.render(str(self.number), True, PASTEL_BLACK)
        text_rect = text_surf.get_rect(center=(self.visual_radius, self.visual_radius))
        self.image.blit(text_surf, text_rect)

    def update(self, cam_x, cam_y, is_active):
        self.rect.centerx = self.world_pos.x - cam_x
        self.rect.centery = self.world_pos.y - cam_y
        self._draw_marker_image(is_active)


# --- Minimap Class ---
class Minimap:
    def __init__(self, width, height, margin):
        self.width = width
        self.height = height
        self.margin = margin
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.surface.get_rect(topright=(SCREEN_WIDTH - self.margin, self.margin + HUD_HEIGHT))
        self.world_bounds_view_radius = 3000 

    def world_to_minimap(self, world_x, world_y, player_world_x, player_world_y):
        scale_x = self.width / (2 * self.world_bounds_view_radius)
        scale_y = self.height / (2 * self.world_bounds_view_radius)
        rel_x = world_x - player_world_x
        rel_y = world_y - player_world_y
        mini_x = self.width / 2 + rel_x * scale_x
        mini_y = self.height / 2 + rel_y * scale_y
        return int(mini_x), int(mini_y)

    def draw(self, surface, player_glider, course_markers):
        self.surface.fill(PASTEL_MINIMAP_BACKGROUND) 
        player_mini_x, player_mini_y = self.width // 2, self.height // 2 
        pygame.draw.circle(self.surface, PASTEL_GOLD, (player_mini_x, player_mini_y), 5)
        
        for i, marker in enumerate(course_markers):
            mini_x, mini_y = self.world_to_minimap(marker.world_pos.x, marker.world_pos.y, player_glider.world_x, player_glider.world_y)
            
            color = PASTEL_ACTIVE_MARKER_COLOR if i == player_glider.current_target_marker_index else PASTEL_MARKER_COLOR
            if i == player_glider.current_target_marker_index and marker.number == 1: # Special color for active start/finish
                color = PASTEL_GOLD

            pygame.draw.circle(self.surface, color, (mini_x, mini_y), RACE_MARKER_VISUAL_RADIUS_MAP)
            font = pygame.font.Font(None, 16) # Slightly smaller for minimap numbers
            text_surf = font.render(str(marker.number), True, PASTEL_BLACK)
            text_rect = text_surf.get_rect(center=(mini_x, mini_y))
            self.surface.blit(text_surf, text_rect)

        pygame.draw.rect(self.surface, PASTEL_MINIMAP_BORDER, self.surface.get_rect(), 2) 
        surface.blit(self.surface, self.rect)


# --- ForegroundCloud Class ---
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
            pygame.draw.ellipse(self.image, (*PASTEL_CLOUD, alpha), (puff_x, puff_y, puff_w, puff_h)) 
        self.speed_factor = random.uniform(MIN_CLOUD_SPEED_FACTOR, MAX_CLOUD_SPEED_FACTOR)
        self.dx = current_wind_speed_x * self.speed_factor; self.dy = current_wind_speed_y * self.speed_factor
        if initial_distribution:
            self.x = (index/total_clouds)*SCREEN_WIDTH - self.width/2 + random.uniform(-SCREEN_WIDTH/(total_clouds*2), SCREEN_WIDTH/(total_clouds*2))
            self.y = random.randint(-self.height//2, SCREEN_HEIGHT - self.height//2)
        else: 
            if self.dx == 0 and self.dy == 0:
                start_x = random.choice([-self.width - 20, SCREEN_WIDTH + 20]) if random.choice([True,False]) else random.randint(-self.width, SCREEN_WIDTH)
                start_y = random.randint(-self.height, SCREEN_HEIGHT) if start_x == random.choice([-self.width - 20, SCREEN_WIDTH + 20]) else random.choice([-self.height - 20, SCREEN_HEIGHT + 20])
            else:
                if abs(self.dx) > abs(self.dy):
                    start_x = SCREEN_WIDTH + random.randint(0,100) + self.width/2 if self.dx < 0 else -random.randint(0,100) - self.width/2
                    start_y = random.randint(-self.height//2, SCREEN_HEIGHT - self.height//2)
                else:
                    start_y = SCREEN_HEIGHT + random.randint(0,50) + self.height/2 if self.dy < 0 else -random.randint(0,50) - self.height/2
                    start_x = random.randint(-self.width//2, SCREEN_WIDTH - self.width//2)
        self.rect = self.image.get_rect(topleft=(self.x if initial_distribution else start_x, self.y if initial_distribution else start_y))
        self.x = float(self.rect.x); self.y = float(self.rect.y)

    def update(self):
        self.dx = current_wind_speed_x * self.speed_factor; self.dy = current_wind_speed_y * self.speed_factor
        self.x += self.dx; self.y += self.dy
        self.rect.topleft = (round(self.x), round(self.y))
        off_screen_margin_x = self.width*1.5 + abs(self.dx * 10); off_screen_margin_y = self.height*1.5 + abs(self.dy * 10)
        despawn = False
        if self.dx < 0 and self.rect.right < -off_screen_margin_x : despawn = True
        elif self.dx > 0 and self.rect.left > SCREEN_WIDTH + off_screen_margin_x : despawn = True
        if not despawn:
            if self.dy < 0 and self.rect.bottom < -off_screen_margin_y : despawn = True
            elif self.dy > 0 and self.rect.top > SCREEN_HEIGHT + off_screen_margin_y : despawn = True
        if self.dx == 0 and self.dy == 0 and not (-off_screen_margin_x < self.rect.centerx < SCREEN_WIDTH + off_screen_margin_x and -off_screen_margin_y < self.rect.centery < SCREEN_HEIGHT + off_screen_margin_y): despawn = True
        if despawn: self.kill()

# --- Enhanced Endless Map Data & Functions ---
map_tile_random_generator = random.Random()
ELEVATION_CONTINENT_SCALE = 60.0 
ELEVATION_MOUNTAIN_SCALE = 15.0  
ELEVATION_HILL_SCALE = 5.0       
MOISTURE_PRIMARY_SCALE = 40.0    
MOISTURE_SECONDARY_SCALE = 10.0  
RIVER_SYSTEM_SCALE = 70.0 
P_CONT, P_MNT, P_HILL = (73856093, 19349663), (83492791, 52084219), (39119077, 66826529)
P_MOIST_P, P_MOIST_S = (23109781, 92953093), (47834583, 11634271)
NUM_MAJOR_RIVERS = 3 
MAJOR_RIVERS_PARAMS = []
_river_param_random = random.Random() 

def regenerate_river_parameters():
    global MAJOR_RIVERS_PARAMS, _river_param_random
    MAJOR_RIVERS_PARAMS = []
    for i in range(NUM_MAJOR_RIVERS):
        start_tile_x = _river_param_random.uniform(-3000 / TILE_SIZE, 3000 / TILE_SIZE)
        start_tile_y = _river_param_random.uniform(-3000 / TILE_SIZE, 3000 / TILE_SIZE)
        MAJOR_RIVERS_PARAMS.append({
            "amplitude": _river_param_random.uniform(10, 30), 
            "wavelength": _river_param_random.uniform(200, 450), 
            "phase_offset": _river_param_random.uniform(0, 2 * math.pi),
            "base_x_offset": start_tile_x, 
            "base_y_offset": start_tile_y, 
            "orientation": _river_param_random.choice(['horizontal', 'vertical']),
            "width": _river_param_random.randint(1, 2) 
        })

def get_seeded_random_value(tile_x, tile_y, scale, p_pair):
    global current_map_offset_x, current_map_offset_y
    eff_tile_x = tile_x + current_map_offset_x
    eff_tile_y = tile_y + current_map_offset_y
    scaled_x = math.floor(eff_tile_x / scale); scaled_y = math.floor(eff_tile_y / scale)
    map_tile_random_generator.seed((scaled_x * p_pair[0]) ^ (scaled_y * p_pair[1]))
    return map_tile_random_generator.random()

def get_land_type_at_world_pos(world_x, world_y):
    tile_grid_x = math.floor(world_x / TILE_SIZE)
    tile_grid_y = math.floor(world_y / TILE_SIZE)
    e_continent = get_seeded_random_value(tile_grid_x, tile_grid_y, ELEVATION_CONTINENT_SCALE, P_CONT)
    e_mountain = get_seeded_random_value(tile_grid_x, tile_grid_y, ELEVATION_MOUNTAIN_SCALE, P_MNT)
    e_hill = get_seeded_random_value(tile_grid_x, tile_grid_y, ELEVATION_HILL_SCALE, P_HILL)
    elevation = math.pow(0.50 * e_continent + 0.35 * e_mountain + 0.15 * e_hill, 1.8)
    elevation = min(max(elevation, 0.0), 1.0)
    m_primary = get_seeded_random_value(tile_grid_x, tile_grid_y, MOISTURE_PRIMARY_SCALE, P_MOIST_P)
    m_secondary = get_seeded_random_value(tile_grid_x, tile_grid_y, MOISTURE_SECONDARY_SCALE, P_MOIST_S)
    moisture = math.pow(0.7 * m_primary + 0.3 * m_secondary, 1.2)
    moisture = min(max(moisture, 0.0), 1.0)
    final_type = LandType.PLAINS
    deep_water_thresh = 0.18    
    shallow_water_thresh = 0.22 
    beach_thresh = 0.24       
    mountain_base_thresh = 0.60
    mountain_peak_thresh = 0.75
    desert_thresh = 0.20
    grassland_thresh = 0.40
    temperate_forest_thresh = 0.65

    if elevation < deep_water_thresh: final_type = LandType.WATER_DEEP
    elif elevation < shallow_water_thresh: final_type = LandType.WATER_SHALLOW
    elif elevation < beach_thresh:
        if moisture > desert_thresh * 1.5 : 
             final_type = LandType.SAND_BEACH
        else: 
             final_type = LandType.SAND_DESERT if moisture < desert_thresh else LandType.SAND_BEACH
    elif elevation > mountain_peak_thresh: final_type = LandType.MOUNTAIN_PEAK
    elif elevation > mountain_base_thresh: final_type = LandType.MOUNTAIN_BASE
    else: 
        if moisture < desert_thresh: final_type = LandType.SAND_DESERT
        elif moisture < grassland_thresh: final_type = LandType.GRASSLAND
        elif moisture < temperate_forest_thresh: final_type = LandType.PLAINS 
        else: 
            if elevation > mountain_base_thresh * 0.8 : 
                 final_type = LandType.FOREST_TEMPERATE
            else: 
                 final_type = LandType.FOREST_DENSE if moisture > 0.8 else LandType.FOREST_TEMPERATE
    can_have_river = not (final_type == LandType.MOUNTAIN_PEAK or \
                          final_type == LandType.WATER_DEEP or \
                          (final_type == LandType.SAND_DESERT and moisture < desert_thresh * 0.75)) 
    if can_have_river:
        for params in MAJOR_RIVERS_PARAMS:
            if params["orientation"] == 'horizontal':
                river_center_y_tile = params["amplitude"] * math.sin(
                    (tile_grid_x / params["wavelength"]) * 2 * math.pi + params["phase_offset"]
                ) + params["base_y_offset"]
                if abs(tile_grid_y - river_center_y_tile) < params["width"]:
                    final_type = LandType.RIVER; break
            else: 
                river_center_x_tile = params["amplitude"] * math.sin(
                    (tile_grid_y / params["wavelength"]) * 2 * math.pi + params["phase_offset"]
                ) + params["base_x_offset"]
                if abs(tile_grid_x - river_center_x_tile) < params["width"]:
                    final_type = LandType.RIVER; break
    return final_type

def draw_endless_map(surface, cam_x, cam_y):
    start_world_tile_x_coord = math.floor(cam_x / TILE_SIZE) * TILE_SIZE
    start_world_tile_y_coord = math.floor(cam_y / TILE_SIZE) * TILE_SIZE
    num_tiles_x = SCREEN_WIDTH // TILE_SIZE + 2 
    num_tiles_y = SCREEN_HEIGHT // TILE_SIZE + 2 
    for i in range(num_tiles_y):
        for j in range(num_tiles_x):
            current_tile_world_x = start_world_tile_x_coord + j * TILE_SIZE
            current_tile_world_y = start_world_tile_y_coord + i * TILE_SIZE
            tile_screen_x = current_tile_world_x - cam_x
            tile_screen_y = current_tile_world_y - cam_y
            tile_type = get_land_type_at_world_pos(current_tile_world_x, current_tile_world_y)
            color = LAND_TYPE_COLORS.get(tile_type, PASTEL_BLACK) 
            pygame.draw.rect(surface, color, (tile_screen_x, tile_screen_y, TILE_SIZE, TILE_SIZE))
            if MAP_TILE_OUTLINE_WIDTH > 0:
                pygame.draw.rect(surface, MAP_TILE_OUTLINE_COLOR, (tile_screen_x, tile_screen_y, TILE_SIZE, TILE_SIZE), MAP_TILE_OUTLINE_WIDTH)

# --- Text Rendering Helper ---
def draw_text(surface, text, size, x, y, color=PASTEL_WHITE, font_name=None, center=False, antialias=True, shadow=False, shadow_color=PASTEL_DARK_GRAY, shadow_offset=(1,1)):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, antialias, color)
    text_rect = text_surface.get_rect()
    if center: text_rect.center = (x,y)
    else: text_rect.topleft = (x,y)
    if shadow:
        shadow_surface = font.render(text, antialias, shadow_color)
        surface.blit(shadow_surface, (text_rect.x + shadow_offset[0], text_rect.y + shadow_offset[1]))
    surface.blit(text_surface, text_rect)

# --- Pygame Setup ---
pygame.init(); pygame.mixer.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pastel Glider - Floating Dreams") 
clock = pygame.time.Clock()

# --- Game Objects & Variables ---
player = Glider()
all_world_sprites = pygame.sprite.Group() 
thermals_group = pygame.sprite.Group()    
race_markers_group = pygame.sprite.Group() 
foreground_clouds_group = pygame.sprite.Group() 
game_state = STATE_START_SCREEN 
current_level = 1; level_timer_start_ticks = 0; time_taken_for_level = 0
current_thermal_spawn_rate = BASE_THERMAL_SPAWN_RATE
thermal_spawn_timer = 0; final_score = 0
selected_difficulty_option = 0 
selected_mode_option = 0 
selected_laps_option = 1 
lap_options = [1, 3, 5]

minimap = Minimap(MINIMAP_WIDTH, MINIMAP_HEIGHT, MINIMAP_MARGIN)


def generate_race_course(num_markers=8, course_radius=1500):
    global race_course_markers, race_markers_group, all_world_sprites
    race_course_markers.clear()
    race_markers_group.empty()
    for sprite in all_world_sprites: # Remove only old RaceMarker instances
        if isinstance(sprite, RaceMarker):
            sprite.kill()

    # Race course is generated around world origin (0,0)
    # The visual map underneath will shift due to current_map_offset_x/y
    center_x = 0 
    center_y = 0

    for i in range(num_markers):
        angle = (i / num_markers) * 2 * math.pi
        world_x = center_x + course_radius * math.cos(angle)
        world_y = center_y + course_radius * math.sin(angle)
        marker = RaceMarker(world_x, world_y, i + 1)
        race_course_markers.append(marker)
        race_markers_group.add(marker) # Keep a specific group for markers if needed for logic
        all_world_sprites.add(marker) # Add to main drawing group


def generate_new_wind():
    global current_wind_speed_x, current_wind_speed_y
    wind_angle_rad = random.uniform(0, 2 * math.pi)
    wind_strength = random.uniform(0.05, MAX_WIND_STRENGTH) 
    current_wind_speed_x = wind_strength * math.cos(wind_angle_rad)
    current_wind_speed_y = wind_strength * math.sin(wind_angle_rad)

def start_new_level(level_num_or_laps): 
    global current_level,level_timer_start_ticks,current_thermal_spawn_rate,thermal_spawn_timer, game_state
    global current_map_offset_x, current_map_offset_y, _river_param_random, total_race_laps
    
    level_timer_start_ticks=pygame.time.get_ticks() 
    
    current_map_offset_x = random.randint(-200000, 200000) 
    current_map_offset_y = random.randint(-200000, 200000)

    _river_param_random.seed(current_level + pygame.time.get_ticks()) 
    regenerate_river_parameters()
    generate_new_wind()
    
    thermals_group.empty()
    # Clear only relevant sprites from all_world_sprites, or clear all and re-add player
    all_world_sprites.empty() 
    race_markers_group.empty() # Also clear specific race marker group
    race_course_markers.clear()


    foreground_clouds_group.empty()
    for i in range(NUM_FOREGROUND_CLOUDS): foreground_clouds_group.add(ForegroundCloud(initial_distribution=True,index=i,total_clouds=NUM_FOREGROUND_CLOUDS))
    
    player.reset(start_height=INITIAL_HEIGHT) 

    if current_game_mode == MODE_FREE_FLY:
        current_level = level_num_or_laps 
        current_thermal_spawn_rate = BASE_THERMAL_SPAWN_RATE + (THERMAL_SPAWN_RATE_INCREASE_PER_LEVEL * (current_level -1))
        if game_difficulty == DIFFICULTY_NOOB:
            current_thermal_spawn_rate = max(20, current_thermal_spawn_rate // 2) 
        elif game_difficulty == DIFFICULTY_EASY:
            current_thermal_spawn_rate = max(30, int(current_thermal_spawn_rate * 0.75))
        thermal_spawn_timer=0
        game_state = STATE_PLAYING_FREE_FLY
    
    elif current_game_mode == MODE_RACE:
        total_race_laps = level_num_or_laps 
        generate_race_course() 
        current_thermal_spawn_rate = BASE_THERMAL_SPAWN_RATE 
        if game_difficulty == DIFFICULTY_NOOB: current_thermal_spawn_rate = max(20, current_thermal_spawn_rate // 2) 
        thermal_spawn_timer=0
        game_state = STATE_RACE_PLAYING


def reset_to_main_menu():
    global game_state,current_level,final_score, current_wind_speed_x, current_wind_speed_y 
    global selected_difficulty_option, selected_mode_option, selected_laps_option
    player.reset(); thermals_group.empty(); all_world_sprites.empty(); race_markers_group.empty(); race_course_markers.clear()
    foreground_clouds_group.empty()
    current_wind_speed_x = -0.2; current_wind_speed_y = 0.05 
    for i in range(NUM_FOREGROUND_CLOUDS): foreground_clouds_group.add(ForegroundCloud(initial_distribution=True,index=i,total_clouds=NUM_FOREGROUND_CLOUDS))
    current_level=1; final_score=0; 
    selected_difficulty_option = 0 
    selected_mode_option = 0
    selected_laps_option = 1 
    game_state = STATE_START_SCREEN

# --- Screen Drawing Functions ---
def draw_start_screen_content(surface):
    surface.fill(PASTEL_DARK_GRAY) 
    draw_text(surface, "Pastel Glider", 72, SCREEN_WIDTH//2, SCREEN_HEIGHT//4 - 20, PASTEL_PLAINS, center=True, shadow=True, shadow_color=PASTEL_BLACK)
    draw_text(surface, "Press ENTER to Begin", 30, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60, PASTEL_LIGHT_GRAY, center=True, shadow=True, shadow_color=PASTEL_BLACK)
    draw_text(surface, "UP/DOWN: Speed | L/R: Bank", 20, SCREEN_WIDTH//2, SCREEN_HEIGHT*3//4, PASTEL_WHITE, center=True)
    draw_text(surface, "Explore the skies, use thermals or race the course!", 20, SCREEN_WIDTH//2, SCREEN_HEIGHT*3//4 + 30, PASTEL_WHITE, center=True)

def draw_difficulty_select_screen(surface, selected_option):
    surface.fill(PASTEL_DARK_GRAY) 
    draw_text(surface, "Select Difficulty", 56, SCREEN_WIDTH//2, SCREEN_HEIGHT//5, PASTEL_GOLD, center=True, shadow=True, shadow_color=PASTEL_BLACK)
    option_spacing = 100; start_y = SCREEN_HEIGHT//2 - option_spacing 
    noob_color = PASTEL_WHITE if selected_option == DIFFICULTY_NOOB else PASTEL_GRAY
    easy_color = PASTEL_WHITE if selected_option == DIFFICULTY_EASY else PASTEL_GRAY
    normal_color = PASTEL_WHITE if selected_option == DIFFICULTY_NORMAL else PASTEL_GRAY
    draw_text(surface, "N00b", 48, SCREEN_WIDTH//2, start_y, noob_color, center=True, shadow=True, shadow_color=PASTEL_BLACK)
    draw_text(surface, "(Largest, Longest, Strongest Thermals!)", 20, SCREEN_WIDTH//2, start_y + 30, noob_color, center=True)
    draw_text(surface, "Easy", 48, SCREEN_WIDTH//2, start_y + option_spacing, easy_color, center=True, shadow=True, shadow_color=PASTEL_BLACK)
    draw_text(surface, "(Stronger Thermals)", 20, SCREEN_WIDTH//2, start_y + option_spacing + 30, easy_color, center=True)
    draw_text(surface, "Normal", 48, SCREEN_WIDTH//2, start_y + option_spacing*2, normal_color, center=True, shadow=True, shadow_color=PASTEL_BLACK)
    draw_text(surface, "(Standard Challenge)", 20, SCREEN_WIDTH//2, start_y + option_spacing*2 + 30, normal_color, center=True)
    draw_text(surface, "Use UP/DOWN keys, ENTER to confirm", 22, SCREEN_WIDTH//2, SCREEN_HEIGHT*0.85, PASTEL_LIGHT_GRAY, center=True)

def draw_mode_select_screen(surface, selected_option):
    surface.fill(PASTEL_DARK_GRAY)
    draw_text(surface, "Select Mode", 56, SCREEN_WIDTH//2, SCREEN_HEIGHT//4, PASTEL_GOLD, center=True, shadow=True, shadow_color=PASTEL_BLACK)
    free_fly_color = PASTEL_WHITE if selected_option == MODE_FREE_FLY else PASTEL_GRAY
    race_color = PASTEL_WHITE if selected_option == MODE_RACE else PASTEL_GRAY
    draw_text(surface, "Free Fly", 48, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 30, free_fly_color, center=True, shadow=True, shadow_color=PASTEL_BLACK)
    draw_text(surface, "(Explore & Reach Altitude Goals)", 20, SCREEN_WIDTH//2, SCREEN_HEIGHT//2, free_fly_color, center=True)
    draw_text(surface, "Race", 48, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 70, race_color, center=True, shadow=True, shadow_color=PASTEL_BLACK)
    draw_text(surface, "(Fly Through Markers Against Time)", 20, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 100, race_color, center=True)
    draw_text(surface, "Use UP/DOWN keys, ENTER to confirm", 22, SCREEN_WIDTH//2, SCREEN_HEIGHT*3//4 + 50, PASTEL_LIGHT_GRAY, center=True)

def draw_laps_select_screen(surface, selected_lap_idx, lap_choices):
    surface.fill(PASTEL_DARK_GRAY)
    draw_text(surface, "Select Laps", 56, SCREEN_WIDTH//2, SCREEN_HEIGHT//4, PASTEL_GOLD, center=True, shadow=True, shadow_color=PASTEL_BLACK)
    y_offset = SCREEN_HEIGHT//2 - 40
    for i, laps in enumerate(lap_choices):
        color = PASTEL_WHITE if i == selected_lap_idx else PASTEL_GRAY
        draw_text(surface, f"{laps} Lap{'s' if laps > 1 else ''}", 48, SCREEN_WIDTH//2, y_offset + i * 80, color, center=True, shadow=True, shadow_color=PASTEL_BLACK)
    draw_text(surface, "Use UP/DOWN keys, ENTER to start race", 22, SCREEN_WIDTH//2, SCREEN_HEIGHT*3//4 + 50, PASTEL_LIGHT_GRAY, center=True)


def draw_target_reached_options_screen(surface, level, time_taken_seconds_val): 
    surface.fill(PASTEL_DARK_GRAY)
    draw_text(surface, f"Level {level} Goal Reached!", 60, SCREEN_WIDTH//2, SCREEN_HEIGHT//3 - 20, PASTEL_GOLD, center=True, shadow=True, shadow_color=PASTEL_BLACK)
    draw_text(surface, f"Time: {time_taken_seconds_val:.1f}s", 36, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40, PASTEL_WHITE, center=True)
    draw_text(surface, "Press M to Move On to Next Level", 30, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 30, PASTEL_LIGHT_GRAY, center=True)
    draw_text(surface, "Press C to Continue Flying This Level", 30, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 70, PASTEL_LIGHT_GRAY, center=True)

def draw_post_goal_menu_screen(surface, level): 
    surface.fill(PASTEL_DARK_GRAY)
    draw_text(surface, f"Level {level} - Cruising", 50, SCREEN_WIDTH//2, SCREEN_HEIGHT//4, PASTEL_GOLD, center=True, shadow=True, shadow_color=PASTEL_BLACK)
    draw_text(surface, "Press N for Next Level", 30, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 30, PASTEL_LIGHT_GRAY, center=True)
    draw_text(surface, "Press Q to Quit to Main Menu", 30, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 10, PASTEL_LIGHT_GRAY, center=True)
    draw_text(surface, "Press R or ESCAPE to Resume Flying", 30, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50, PASTEL_LIGHT_GRAY, center=True)

def draw_race_complete_screen(surface, total_time_seconds):
    surface.fill(PASTEL_DARK_GRAY)
    draw_text(surface, "Race Finished!", 60, SCREEN_WIDTH//2, SCREEN_HEIGHT//3 -20, PASTEL_GOLD, center=True, shadow=True, shadow_color=PASTEL_BLACK)
    draw_text(surface, f"Total Time: {total_time_seconds:.1f}s", 40, SCREEN_WIDTH//2, SCREEN_HEIGHT//2, PASTEL_WHITE, center=True)
    draw_text(surface, "Press ENTER for Main Menu", 32, SCREEN_WIDTH//2, SCREEN_HEIGHT*2//3, PASTEL_LIGHT_GRAY, center=True)


def draw_game_over_screen_content(surface, score, level):
    surface.fill(PASTEL_DARK_GRAY); draw_text(surface, "GAME OVER", 72, SCREEN_WIDTH//2, SCREEN_HEIGHT//3, PASTEL_RED, center=True, shadow=True, shadow_color=PASTEL_BLACK)
    if current_game_mode == MODE_FREE_FLY: 
        draw_text(surface, f"Reached Level: {level}", 36, SCREEN_WIDTH//2, SCREEN_HEIGHT//2-30, PASTEL_WHITE, center=True)
    draw_text(surface, f"Final Height: {int(score)}m", 36, SCREEN_WIDTH//2, SCREEN_HEIGHT//2+10, PASTEL_WHITE, center=True)
    draw_text(surface, "Press ENTER for Menu", 32, SCREEN_WIDTH//2, SCREEN_HEIGHT*2//3, PASTEL_LIGHT_GRAY, center=True)

def draw_height_indicator_hud(surface, current_player_height, target_h, vertical_speed_val):
    indicator_bar_height = SCREEN_HEIGHT - HUD_HEIGHT - (2 * INDICATOR_Y_MARGIN_FROM_HUD)
    indicator_x_pos = SCREEN_WIDTH - INDICATOR_WIDTH - INDICATOR_X_MARGIN 
    indicator_y_pos = HUD_HEIGHT + INDICATOR_Y_MARGIN_FROM_HUD
    pygame.draw.rect(surface, PASTEL_INDICATOR_COLOR, (indicator_x_pos, indicator_y_pos, INDICATOR_WIDTH, indicator_bar_height))
    max_indicator_height_value = target_h * 1.15 
    if max_indicator_height_value <=0: max_indicator_height_value = 1
    pygame.draw.line(surface, PASTEL_INDICATOR_GROUND, (indicator_x_pos-5, indicator_y_pos+indicator_bar_height), (indicator_x_pos+INDICATOR_WIDTH+5, indicator_y_pos+indicator_bar_height), 3)
    draw_text(surface, "0m", 14, indicator_x_pos+INDICATOR_WIDTH+8, indicator_y_pos+indicator_bar_height-7, PASTEL_TEXT_COLOR_HUD) 
    target_marker_y_on_bar = indicator_y_pos
    if target_h > 0 and current_game_mode == MODE_FREE_FLY : 
        target_ratio = min(target_h / max_indicator_height_value, 1.0)
        target_marker_y_on_bar = indicator_y_pos + indicator_bar_height * (1 - target_ratio)
        pygame.draw.line(surface, PASTEL_GREEN_TARGET, (indicator_x_pos-5, target_marker_y_on_bar), (indicator_x_pos+INDICATOR_WIDTH+5, target_marker_y_on_bar), 3)
        draw_text(surface, f"{target_h}m", 14, indicator_x_pos+INDICATOR_WIDTH+8, target_marker_y_on_bar-7, PASTEL_GREEN_TARGET)
    player_marker_y_on_bar = indicator_y_pos + indicator_bar_height 
    if current_player_height > 0:
        player_height_ratio = min(current_player_height / max_indicator_height_value, 1.0)
        player_marker_y_on_bar = indicator_y_pos + indicator_bar_height * (1 - player_height_ratio)
    pygame.draw.line(surface, PASTEL_GOLD, (indicator_x_pos, player_marker_y_on_bar), (indicator_x_pos+INDICATOR_WIDTH, player_marker_y_on_bar), 5)
    vsi_text_x = indicator_x_pos - 50
    vsi_arrow_x_center = indicator_x_pos - 10 
    vsi_mps = vertical_speed_val * 60 
    vsi_color = PASTEL_VSI_CLIMB if vertical_speed_val > 0.05 else (PASTEL_VSI_SINK if vertical_speed_val < -0.05 else PASTEL_TEXT_COLOR_HUD) 
    draw_text(surface, f"{vsi_mps:+.1f}m/s", 14, vsi_text_x -5 , player_marker_y_on_bar - 7, vsi_color)
    if abs(vertical_speed_val) > 0.05: 
        arrow_points = []
        if vertical_speed_val > 0: 
            arrow_points = [
                (vsi_arrow_x_center, player_marker_y_on_bar - VSI_ARROW_SIZE // 2),
                (vsi_arrow_x_center - VSI_ARROW_SIZE // 2, player_marker_y_on_bar + VSI_ARROW_SIZE // 2),
                (vsi_arrow_x_center + VSI_ARROW_SIZE // 2, player_marker_y_on_bar + VSI_ARROW_SIZE // 2),
            ]
        else: 
            arrow_points = [
                (vsi_arrow_x_center, player_marker_y_on_bar + VSI_ARROW_SIZE // 2),
                (vsi_arrow_x_center - VSI_ARROW_SIZE // 2, player_marker_y_on_bar - VSI_ARROW_SIZE // 2),
                (vsi_arrow_x_center + VSI_ARROW_SIZE // 2, player_marker_y_on_bar - VSI_ARROW_SIZE // 2),
            ]
        pygame.draw.polygon(surface, vsi_color, arrow_points)
    player_height_text_y = player_marker_y_on_bar - 20 
    draw_text(surface, f"{int(current_player_height)}m", 14, vsi_text_x -5, player_height_text_y, PASTEL_GOLD)

def draw_weather_vane(surface, wind_x, wind_y, center_x, center_y, max_strength_for_scaling=MAX_WIND_STRENGTH):
    wind_angle_rad = math.atan2(wind_y, wind_x); wind_magnitude = math.hypot(wind_x, wind_y)
    arrow_base_length = 15; arrow_max_additional_length = 20; arrow_color = PASTEL_TEXT_COLOR_HUD; arrow_thickness = 2 
    vane_circle_radius = 3; vane_circle_color = PASTEL_GRAY; strength_ratio = 0.0
    if max_strength_for_scaling > 0: strength_ratio = min(wind_magnitude / max_strength_for_scaling, 1.0)
    current_arrow_length = arrow_base_length + arrow_max_additional_length * strength_ratio
    tip_x = center_x + current_arrow_length * math.cos(wind_angle_rad); tip_y = center_y + current_arrow_length * math.sin(wind_angle_rad)
    tail_length_factor = 0.3; tail_x = center_x - (arrow_base_length * tail_length_factor) * math.cos(wind_angle_rad); tail_y = center_y - (arrow_base_length * tail_length_factor) * math.sin(wind_angle_rad)
    arrowhead_angle_offset = math.radians(150); arrowhead_length = 8
    barb1_angle = wind_angle_rad + arrowhead_angle_offset; barb1_x = tip_x + arrowhead_length * math.cos(barb1_angle); barb1_y = tip_y + arrowhead_length * math.sin(barb1_angle)
    barb2_angle = wind_angle_rad - arrowhead_angle_offset; barb2_x = tip_x + arrowhead_length * math.cos(barb2_angle); barb2_y = tip_y + arrowhead_length * math.sin(barb2_angle)
    pygame.draw.line(surface, arrow_color, (tail_x, tail_y), (tip_x, tip_y), arrow_thickness)
    pygame.draw.line(surface, arrow_color, (tip_x, tip_y), (barb1_x, barb1_y), arrow_thickness); pygame.draw.line(surface, arrow_color, (tip_x, tip_y), (barb2_x, barb2_y), arrow_thickness)
    pygame.draw.circle(surface, vane_circle_color, (center_x, center_y), vane_circle_radius); pygame.draw.circle(surface, arrow_color, (center_x, center_y), vane_circle_radius, 1)

# --- Game Loop ---
running = True
while running:
    dt = clock.tick(60) / 1000.0; current_ticks = pygame.time.get_ticks()
    keys = pygame.key.get_pressed() 

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN:
            if game_state == STATE_START_SCREEN:
                if event.key == pygame.K_RETURN: game_state = STATE_DIFFICULTY_SELECT
            
            elif game_state == STATE_DIFFICULTY_SELECT:
                if event.key == pygame.K_UP: selected_difficulty_option = (selected_difficulty_option - 1 + 3) % 3 
                elif event.key == pygame.K_DOWN: selected_difficulty_option = (selected_difficulty_option + 1) % 3 
                elif event.key == pygame.K_RETURN:
                    game_difficulty = selected_difficulty_option 
                    game_state = STATE_MODE_SELECT 
            
            elif game_state == STATE_MODE_SELECT:
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN: selected_mode_option = 1 - selected_mode_option
                elif event.key == pygame.K_RETURN:
                    current_game_mode = selected_mode_option
                    if current_game_mode == MODE_FREE_FLY:
                        start_new_level(1) 
                    else: 
                        game_state = STATE_RACE_LAPS_SELECT
            
            elif game_state == STATE_RACE_LAPS_SELECT:
                if event.key == pygame.K_UP: selected_laps_option = (selected_laps_option - 1 + len(lap_options)) % len(lap_options)
                elif event.key == pygame.K_DOWN: selected_laps_option = (selected_laps_option + 1) % len(lap_options)
                elif event.key == pygame.K_RETURN:
                    start_new_level(lap_options[selected_laps_option]) 

            elif game_state == STATE_PLAYING_FREE_FLY: 
                if event.key == pygame.K_ESCAPE: reset_to_main_menu() 
            
            elif game_state == STATE_TARGET_REACHED_OPTIONS:
                if event.key == pygame.K_m: 
                    start_new_level(current_level + 1) 
                elif event.key == pygame.K_c: 
                    game_state = STATE_TARGET_REACHED_CONTINUE_PLAYING
            
            elif game_state == STATE_TARGET_REACHED_CONTINUE_PLAYING:
                if event.key == pygame.K_ESCAPE:
                    game_state = STATE_POST_GOAL_MENU 

            elif game_state == STATE_POST_GOAL_MENU:
                if event.key == pygame.K_n: 
                    start_new_level(current_level + 1) 
                elif event.key == pygame.K_q: 
                    reset_to_main_menu()
                elif event.key == pygame.K_r or event.key == pygame.K_ESCAPE : 
                    game_state = STATE_TARGET_REACHED_CONTINUE_PLAYING
            
            elif game_state == STATE_RACE_PLAYING:
                 if event.key == pygame.K_ESCAPE: reset_to_main_menu() 

            elif game_state == STATE_RACE_COMPLETE:
                if event.key == pygame.K_RETURN: reset_to_main_menu()

            elif game_state == STATE_GAME_OVER: 
                if event.key == pygame.K_RETURN: reset_to_main_menu()


    # --- Updates ---
    if game_state == STATE_PLAYING_FREE_FLY or game_state == STATE_TARGET_REACHED_CONTINUE_PLAYING or game_state == STATE_RACE_PLAYING:
        player.update(keys) 
        camera_x = player.world_x - SCREEN_WIDTH // 2
        camera_y = player.world_y - SCREEN_HEIGHT // 2
        
        if game_state == STATE_PLAYING_FREE_FLY or game_state == STATE_RACE_PLAYING : 
            for thermal_sprite in thermals_group: thermal_sprite.update(camera_x, camera_y)
            thermal_spawn_timer += 1
            if thermal_spawn_timer >= current_thermal_spawn_rate:
                thermal_spawn_timer = 0
                spawn_world_x = camera_x + random.randint(-THERMAL_SPAWN_AREA_WIDTH // 2, THERMAL_SPAWN_AREA_WIDTH // 2)
                spawn_world_y = camera_y + random.randint(-THERMAL_SPAWN_AREA_HEIGHT // 2, THERMAL_SPAWN_AREA_HEIGHT // 2)
                land_type = get_land_type_at_world_pos(spawn_world_x, spawn_world_y)
                if random.random() < LAND_TYPE_THERMAL_PROBABILITY.get(land_type, 0.0):
                    new_thermal = Thermal((spawn_world_x, spawn_world_y))
                    all_world_sprites.add(new_thermal); thermals_group.add(new_thermal)
        else: 
             for thermal_sprite in thermals_group: thermal_sprite.update(camera_x, camera_y)

        if game_state == STATE_RACE_PLAYING:
            for i, marker in enumerate(race_course_markers):
                marker.update(camera_x, camera_y, i == player.current_target_marker_index)


        foreground_clouds_group.update()
        if len(foreground_clouds_group) < NUM_FOREGROUND_CLOUDS: foreground_clouds_group.add(ForegroundCloud())
        
        player_world_pos_vec = pygame.math.Vector2(player.world_x, player.world_y)
        for thermal in thermals_group:
            distance_to_thermal_center = player_world_pos_vec.distance_to(thermal.world_pos)
            if distance_to_thermal_center < thermal.radius + player.radius * 0.7:
                player.apply_lift_from_thermal(thermal.lift_power)
        
        if game_state == STATE_PLAYING_FREE_FLY and player.height >= TARGET_HEIGHT_PER_LEVEL:
            game_state = STATE_TARGET_REACHED_OPTIONS
            level_end_ticks = pygame.time.get_ticks()
            time_taken_for_level = (level_end_ticks - level_timer_start_ticks) / 1000.0
        
        if player.height <= 0: 
            final_score = player.height; player.height = 0; game_state = STATE_GAME_OVER

    # --- Drawing ---
    screen.fill(PASTEL_BLACK) 
    if game_state == STATE_START_SCREEN:
        draw_start_screen_content(screen); foreground_clouds_group.draw(screen)
    elif game_state == STATE_DIFFICULTY_SELECT:
        draw_difficulty_select_screen(screen, selected_difficulty_option); foreground_clouds_group.draw(screen)
    elif game_state == STATE_MODE_SELECT:
        draw_mode_select_screen(screen, selected_mode_option); foreground_clouds_group.draw(screen)
    elif game_state == STATE_RACE_LAPS_SELECT:
        draw_laps_select_screen(screen, selected_laps_option, lap_options); foreground_clouds_group.draw(screen)
    elif game_state == STATE_TARGET_REACHED_OPTIONS: 
        draw_target_reached_options_screen(screen, current_level, time_taken_for_level); foreground_clouds_group.draw(screen)
    elif game_state == STATE_POST_GOAL_MENU:
        draw_post_goal_menu_screen(screen, current_level); foreground_clouds_group.draw(screen)
    elif game_state == STATE_RACE_COMPLETE:
        draw_race_complete_screen(screen, time_taken_for_level); foreground_clouds_group.draw(screen)


    elif game_state == STATE_PLAYING_FREE_FLY or game_state == STATE_TARGET_REACHED_CONTINUE_PLAYING or game_state == STATE_RACE_PLAYING:
        draw_endless_map(screen, camera_x, camera_y)
        player.draw_contrail(screen, camera_x, camera_y)
        all_world_sprites.draw(screen) 
        screen.blit(player.image, player.rect) 
        foreground_clouds_group.draw(screen) 
        
        hud_surface = pygame.Surface((SCREEN_WIDTH, HUD_HEIGHT), pygame.SRCALPHA); hud_surface.fill(PASTEL_HUD_PANEL); screen.blit(hud_surface, (0,0))
        hud_margin = 10; line_spacing = 22; current_y_hud = hud_margin

        if current_game_mode == MODE_FREE_FLY:
            draw_text(screen, f"Level: {current_level}", 20, hud_margin, current_y_hud, PASTEL_TEXT_COLOR_HUD)
            draw_text(screen, f"Target: {TARGET_HEIGHT_PER_LEVEL}m", 20, hud_margin + 120, current_y_hud, PASTEL_TEXT_COLOR_HUD)
        elif current_game_mode == MODE_RACE:
            draw_text(screen, f"Lap: {min(player.laps_completed + 1, total_race_laps)} / {total_race_laps}", 20, hud_margin, current_y_hud, PASTEL_TEXT_COLOR_HUD)
            if race_course_markers and player.current_target_marker_index < len(race_course_markers) and game_state == STATE_RACE_PLAYING :
                target_marker = race_course_markers[player.current_target_marker_index]
                dist_to_marker = math.hypot(player.world_x - target_marker.world_pos.x, player.world_y - target_marker.world_pos.y)
                draw_text(screen, f"Marker {target_marker.number}: {int(dist_to_marker/10)}m", 20, hud_margin + 150, current_y_hud, PASTEL_TEXT_COLOR_HUD)
                
                # Improved HUD Arrow
                marker_screen_x = target_marker.world_pos.x - camera_x
                marker_screen_y = target_marker.world_pos.y - camera_y
                
                hud_arrow_base_x = SCREEN_WIDTH - MINIMAP_WIDTH - MINIMAP_MARGIN - 40 
                hud_arrow_base_y = MINIMAP_MARGIN + HUD_HEIGHT + MINIMAP_HEIGHT // 2
                
                angle_to_marker_screen = math.atan2(marker_screen_y - hud_arrow_base_y, marker_screen_x - hud_arrow_base_x)
                
                arrow_len = 15
                tip_x = hud_arrow_base_x + arrow_len * math.cos(angle_to_marker_screen)
                tip_y = hud_arrow_base_y + arrow_len * math.sin(angle_to_marker_screen)
                
                # Arrow points (triangle)
                p1 = (tip_x, tip_y)
                p2 = (tip_x - arrow_len * 0.5 * math.cos(angle_to_marker_screen + math.pi / 6), 
                      tip_y - arrow_len * 0.5 * math.sin(angle_to_marker_screen + math.pi / 6))
                p3 = (tip_x - arrow_len * 0.5 * math.cos(angle_to_marker_screen - math.pi / 6),
                      tip_y - arrow_len * 0.5 * math.sin(angle_to_marker_screen - math.pi / 6))
                pygame.draw.polygon(screen, PASTEL_ACTIVE_MARKER_COLOR, [p1,p2,p3])


        current_y_hud += line_spacing
        if game_state == STATE_PLAYING_FREE_FLY or game_state == STATE_RACE_PLAYING:
            timer_seconds = (current_ticks - level_timer_start_ticks) / 1000.0
            draw_text(screen, f"Time: {timer_seconds:.1f}s", 20, hud_margin, current_y_hud, PASTEL_TEXT_COLOR_HUD)
        else: 
            draw_text(screen, f"Time: {time_taken_for_level:.1f}s (Goal!)", 20, hud_margin, current_y_hud, PASTEL_TEXT_COLOR_HUD)

        current_y_hud += line_spacing
        draw_text(screen, f"Height: {int(player.height)}m", 20, hud_margin, current_y_hud, PASTEL_TEXT_COLOR_HUD)
        draw_text(screen, f"Speed: {player.speed:.1f}", 20, hud_margin + 120, current_y_hud, PASTEL_TEXT_COLOR_HUD)
        if player.speed < STALL_SPEED: draw_text(screen, "STALL!", 24, SCREEN_WIDTH//2, hud_margin + line_spacing//2, PASTEL_RED, center=True, shadow=True, shadow_color=PASTEL_BLACK)
        
        wind_display_text = f"Wind: <{current_wind_speed_x*10:.0f}, {current_wind_speed_y*10:.0f}>"; wind_text_x_pos = SCREEN_WIDTH - MINIMAP_WIDTH - MINIMAP_MARGIN * 2 - 180 
        draw_text(screen, wind_display_text, 18, wind_text_x_pos, hud_margin + 5, PASTEL_TEXT_COLOR_HUD)
        
        esc_text = "ESC for Menu"
        if game_state == STATE_TARGET_REACHED_CONTINUE_PLAYING: esc_text = "ESC for Options"
        elif game_state == STATE_RACE_PLAYING : esc_text = "ESC for Menu" 
        draw_text(screen, esc_text, 18, wind_text_x_pos, hud_margin + 5 + line_spacing, PASTEL_TEXT_COLOR_HUD)

        draw_weather_vane(screen, current_wind_speed_x, current_wind_speed_y, wind_text_x_pos + 150, hud_margin + 25)
        draw_height_indicator_hud(screen, player.height, TARGET_HEIGHT_PER_LEVEL if current_game_mode == MODE_FREE_FLY else player.height + 100, player.vertical_speed) 

        if current_game_mode == MODE_RACE and (game_state == STATE_RACE_PLAYING or game_state == STATE_RACE_COMPLETE): # Show minimap in race and on race complete
            minimap.draw(screen, player, race_course_markers)
    
    elif game_state == STATE_GAME_OVER:
        draw_game_over_screen_content(screen, final_score, current_level); foreground_clouds_group.draw(screen)
    
    pygame.display.flip()
pygame.quit()
