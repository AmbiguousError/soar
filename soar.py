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
STALL_SINK_PENALTY = 0.25 
GRAVITY_BASE_PULL = 0.22
LIFT_PER_SPEED_UNIT = 0.03
MINIMUM_SINK_RATE = 0.04
DIVE_TO_SPEED_FACTOR = 0.08
ZOOM_CLIMB_FACTOR = 1.8
MAX_BANK_ANGLE = 45
BANK_RATE = 2
BASE_PLAYER_BANK_TO_DEGREES_PER_FRAME = 0.12 
NOOB_TURN_FACTOR = 1.5    
EASY_TURN_FACTOR = 1.2    
NORMAL_TURN_FACTOR = 1.0  
GLIDER_COLLISION_RADIUS = 20

# AI Specific
NUM_AI_OPPONENTS = 3
AI_TARGET_RACE_ALTITUDE = 450
AI_ALTITUDE_CORRECTION_RATE = 0.2
AI_SPEED_MIN = 2.5
AI_SPEED_MAX = 4.5
AI_TURN_RATE_SCALAR = 0.08
AI_MARKER_APPROACH_SLOWDOWN_DISTANCE = 200
AI_MARKER_APPROACH_MIN_SPEED_FACTOR = 0.6
AI_TARGET_SPEED_UPDATE_INTERVAL = 120 
AI_SPEED_VARIATION_FACTOR = 0.2 

# Contrail
CONTRAIL_LENGTH = 60
CONTRAIL_POINT_DELAY = 2

# Thermals
BASE_THERMAL_SPAWN_RATE = 100
THERMAL_SPAWN_RATE_INCREASE_PER_LEVEL = 18
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
tile_type_cache = {}

# Race Mode Specific
RACE_MARKER_RADIUS_WORLD = 75
RACE_MARKER_VISUAL_RADIUS_MAP = 6
RACE_MARKER_VISUAL_RADIUS_WORLD = 25
DEFAULT_RACE_LAPS = 3
RACE_COURSE_AREA_HALFWIDTH = 2500
race_course_markers = []
total_race_laps = DEFAULT_RACE_LAPS

# Wind
MAX_WIND_STRENGTH = 1.0
current_wind_speed_x = 0.0
current_wind_speed_y = 0.0

# Clouds
NUM_FOREGROUND_CLOUDS = 15
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
VSI_ARROW_SIZE = 8

# HUD Font
HUD_FONT_NAME = "Consolas" 
HUD_FONT_SIZE_LARGE = 24
HUD_FONT_SIZE_NORMAL = 22
HUD_FONT_SIZE_SMALL = 20


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
STATE_PAUSED = 11

# --- Game Difficulty & Mode ---
DIFFICULTY_NOOB = 0
DIFFICULTY_EASY = 1
DIFFICULTY_NORMAL = 2
game_difficulty = DIFFICULTY_NORMAL
difficulty_options_map = {0: "N00b", 1: "Easy", 2: "Normal"}
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
PASTEL_MARKER_COLOR = (255, 170, 170) 
PASTEL_ACTIVE_MARKER_COLOR = PASTEL_GREEN_TARGET 
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
PASTEL_AI_GLIDER_BODY = (250, 180, 180)
PASTEL_AI_GLIDER_WING = (255, 200, 200)
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
LAND_TYPE_WATER_DEEP = 0
LAND_TYPE_WATER_SHALLOW = 1
LAND_TYPE_PLAINS = 2
LAND_TYPE_FOREST_TEMPERATE = 3
LAND_TYPE_MOUNTAIN_BASE = 4
LAND_TYPE_SAND_DESERT = 5
LAND_TYPE_MOUNTAIN_PEAK = 6
LAND_TYPE_RIVER = 7
LAND_TYPE_FOREST_DENSE = 8
LAND_TYPE_GRASSLAND = 9
LAND_TYPE_SAND_BEACH = 10

LAND_TYPE_COLORS = {
    LAND_TYPE_WATER_DEEP: PASTEL_WATER_DEEP, LAND_TYPE_WATER_SHALLOW: PASTEL_WATER_SHALLOW,
    LAND_TYPE_PLAINS: PASTEL_PLAINS, LAND_TYPE_GRASSLAND: PASTEL_GRASSLAND,
    LAND_TYPE_FOREST_TEMPERATE: PASTEL_FOREST_TEMPERATE, LAND_TYPE_FOREST_DENSE: PASTEL_FOREST_DENSE,
    LAND_TYPE_MOUNTAIN_BASE: PASTEL_MOUNTAIN_BASE, LAND_TYPE_MOUNTAIN_PEAK: PASTEL_MOUNTAIN_PEAK,
    LAND_TYPE_SAND_DESERT: PASTEL_SAND_DESERT, LAND_TYPE_SAND_BEACH: PASTEL_SAND_BEACH,
    LAND_TYPE_RIVER: PASTEL_RIVER,
}
LAND_TYPE_THERMAL_PROBABILITY = {
    LAND_TYPE_WATER_DEEP: 0.00, LAND_TYPE_WATER_SHALLOW: 0.01,
    LAND_TYPE_PLAINS: 0.6, LAND_TYPE_GRASSLAND: 0.7,
    LAND_TYPE_FOREST_TEMPERATE: 0.3, LAND_TYPE_FOREST_DENSE: 0.1,
    LAND_TYPE_MOUNTAIN_BASE: 0.5, LAND_TYPE_MOUNTAIN_PEAK: 0.05,
    LAND_TYPE_SAND_DESERT: 0.9, LAND_TYPE_SAND_BEACH: 0.8,
    LAND_TYPE_RIVER: 0.02,
}

# --- Camera ---
camera_x = 0.0
camera_y = 0.0

# --- High Scores & Lap Times Data ---
high_scores = {
    "longest_flight_time_free_fly": 0.0,
    "max_altitude_free_fly": 0.0,
    "best_lap_time_race": float('inf'),
    "best_total_race_times": {} 
}
player_race_lap_times = []

# --- Pause State Variables ---
game_state_before_pause = None
pause_start_ticks = 0
current_session_flight_start_ticks = 0

# --- Glider Base Class ---
class GliderBase(pygame.sprite.Sprite):
    def __init__(self, body_color, wing_color, start_world_x=0.0, start_world_y=0.0):
        super().__init__()
        self.fuselage_length = 45
        self.fuselage_thickness = 4
        self.wing_span = 70
        self.wing_chord = 5
        self.tail_plane_span = 18
        self.tail_plane_chord = 4
        self.tail_fin_height = 8
        
        canvas_width = self.fuselage_length 
        canvas_height = self.wing_span    
        self.original_image = pygame.Surface([canvas_width, canvas_height], pygame.SRCALPHA)
        
        fuselage_y_top = (canvas_height - self.fuselage_thickness) / 2
        pygame.draw.rect(self.original_image, body_color, (0, fuselage_y_top, self.fuselage_length, self.fuselage_thickness))
        
        wing_x_pos = (self.fuselage_length - self.wing_chord) * 0.65 
        wing_y_pos = (canvas_height - self.wing_span) / 2 
        pygame.draw.rect(self.original_image, wing_color, (wing_x_pos, wing_y_pos, self.wing_chord, self.wing_span))
        
        tail_plane_x_pos = 0 
        tail_plane_y_top = (canvas_height - self.tail_plane_span) / 2
        pygame.draw.rect(self.original_image, wing_color, (tail_plane_x_pos, tail_plane_y_top, self.tail_plane_chord, self.tail_plane_span))
        
        fin_base_y_center = fuselage_y_top + self.fuselage_thickness / 2 
        fin_bottom_y = fin_base_y_center - self.fuselage_thickness / 2 
        fin_tip_y = fin_bottom_y - self.tail_fin_height
        fin_leading_edge_x = tail_plane_x_pos + self.tail_plane_chord * 0.2
        fin_trailing_edge_x = tail_plane_x_pos + self.tail_plane_chord * 0.8
        fin_tip_x = tail_plane_x_pos + self.tail_plane_chord * 0.5
        pygame.draw.polygon(self.original_image, body_color, [
            (fin_leading_edge_x, fin_bottom_y), (fin_trailing_edge_x, fin_bottom_y), (fin_tip_x, fin_tip_y)
        ])
        
        self.image = self.original_image 
        self.rect = self.image.get_rect()
        self.collision_radius = GLIDER_COLLISION_RADIUS
        self.world_x = start_world_x
        self.world_y = start_world_y
        self.heading = 0 
        self.bank_angle = 0 
        self.height = INITIAL_HEIGHT 
        self.speed = INITIAL_SPEED 
        self.trail_points = [] 
        self.contrail_frame_counter = 0
        self.current_target_marker_index = 0
        self.laps_completed = 0

    def update_sprite_rotation_and_position(self, cam_x=None, cam_y=None):
        self.image = pygame.transform.rotate(self.original_image, -self.heading) 
        if isinstance(self, PlayerGlider): 
            self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        elif cam_x is not None and cam_y is not None: 
            self.rect = self.image.get_rect(center=(self.world_x - cam_x, self.world_y - cam_y))

    def update_contrail(self):
        heading_rad = math.radians(self.heading)
        self.contrail_frame_counter +=1
        if self.contrail_frame_counter >= CONTRAIL_POINT_DELAY:
            self.contrail_frame_counter = 0
            effective_tail_offset = (self.fuselage_length / 2) - 2 
            tail_offset_x_world = -effective_tail_offset * math.cos(heading_rad)
            tail_offset_y_world = -effective_tail_offset * math.sin(heading_rad)
            self.trail_points.append((self.world_x + tail_offset_x_world, self.world_y + tail_offset_y_world))
            if len(self.trail_points) > CONTRAIL_LENGTH: 
                self.trail_points.pop(0) 

    def draw_contrail(self, surface, cam_x, cam_y):
        if len(self.trail_points) > 1:
            for i, world_point in enumerate(self.trail_points):
                alpha = int(200 * (i / CONTRAIL_LENGTH))
                screen_px = world_point[0] - cam_x
                screen_py = world_point[1] - cam_y
                if 0 <= screen_px <= SCREEN_WIDTH and 0 <= screen_py <= SCREEN_HEIGHT:
                    try: 
                        pygame.draw.circle(surface, (*PASTEL_CONTRAIL_COLOR, alpha), (screen_px, screen_py), 2)
                    except pygame.error: 
                        pass # Ignore if color format error occurs

    def apply_collision_effect(self):
        self.speed *= 0.5
        knockback_angle = random.uniform(0, 2 * math.pi)
        knockback_dist = 5 
        self.world_x += knockback_dist * math.cos(knockback_angle)
        self.world_y += knockback_dist * math.sin(knockback_angle)

# --- PlayerGlider Class ---
class PlayerGlider(GliderBase):
    def __init__(self):
        super().__init__(PASTEL_GLIDER_BODY, PASTEL_GLIDER_WING)
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.previous_height = INITIAL_HEIGHT 
        self.vertical_speed = 0.0
        self.current_lap_start_ticks = 0

    def reset(self, start_height=INITIAL_HEIGHT):
        global player_race_lap_times, current_session_flight_start_ticks
        self.world_x = 0.0
        self.world_y = 0.0
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.heading = 0
        self.bank_angle = 0
        self.height = start_height
        self.speed = INITIAL_SPEED
        self.previous_height = start_height
        self.vertical_speed = 0.0
        self.trail_points = []
        self.contrail_frame_counter = 0
        self.current_target_marker_index = 0
        self.laps_completed = 0
        self.current_lap_start_ticks = pygame.time.get_ticks() 
        player_race_lap_times = [] 
        current_session_flight_start_ticks = pygame.time.get_ticks()
        self.update_sprite_rotation_and_position() 

    def update(self, keys):
        global current_wind_speed_x, current_wind_speed_y, game_state, race_course_markers, total_race_laps, time_taken_for_level, level_timer_start_ticks, game_difficulty, high_scores, player_race_lap_times
        
        self.previous_height = self.height

        if current_game_mode == MODE_FREE_FLY and self.height > high_scores["max_altitude_free_fly"]:
            high_scores["max_altitude_free_fly"] = self.height

        if keys[pygame.K_UP]: 
            self.speed += ACCELERATION
        elif keys[pygame.K_DOWN]: 
            potential_new_speed = self.speed - ACCELERATION
            if potential_new_speed >= MIN_SPEED: 
                self.speed = potential_new_speed
                self.height += ACCELERATION * ZOOM_CLIMB_FACTOR 
            else: 
                self.speed = MIN_SPEED 
        self.speed = max(MIN_SPEED, min(self.speed, MAX_SPEED)) 

        if keys[pygame.K_LEFT]: 
            self.bank_angle -= BANK_RATE
        elif keys[pygame.K_RIGHT]: 
            self.bank_angle += BANK_RATE
        else: 
            self.bank_angle *= 0.95 
        if abs(self.bank_angle) < 0.1: 
            self.bank_angle = 0 
        self.bank_angle = max(-MAX_BANK_ANGLE, min(self.bank_angle, MAX_BANK_ANGLE)) 
        
        actual_turn_rate_factor = BASE_PLAYER_BANK_TO_DEGREES_PER_FRAME
        if game_difficulty == DIFFICULTY_NOOB: 
            actual_turn_rate_factor *= NOOB_TURN_FACTOR
        elif game_difficulty == DIFFICULTY_EASY: 
            actual_turn_rate_factor *= EASY_TURN_FACTOR
        else: 
            actual_turn_rate_factor *= NORMAL_TURN_FACTOR
        turn_rate_degrees = self.bank_angle * actual_turn_rate_factor
        self.heading = (self.heading + turn_rate_degrees) % 360
        
        heading_rad = math.radians(self.heading)
        self.world_x += self.speed * math.cos(heading_rad) + current_wind_speed_x
        self.world_y += self.speed * math.sin(heading_rad) + current_wind_speed_y
        
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
            self.speed = min(self.speed + abs(height_change_due_to_physics) * DIVE_TO_SPEED_FACTOR, MAX_SPEED)
        
        self.vertical_speed = self.height - self.previous_height
        self.update_sprite_rotation_and_position()
        self.update_contrail()
        
        if game_state == STATE_RACE_PLAYING and race_course_markers:
            target_marker = race_course_markers[self.current_target_marker_index]
            if math.hypot(self.world_x - target_marker.world_pos.x, self.world_y - target_marker.world_pos.y) < target_marker.world_radius: 
                self.current_target_marker_index += 1
                if self.current_target_marker_index >= len(race_course_markers): 
                    self.laps_completed += 1
                    lap_time_seconds = (pygame.time.get_ticks() - self.current_lap_start_ticks) / 1000.0
                    player_race_lap_times.append(lap_time_seconds)
                    if lap_time_seconds < high_scores["best_lap_time_race"]:
                        high_scores["best_lap_time_race"] = lap_time_seconds
                    self.current_lap_start_ticks = pygame.time.get_ticks()
                    self.current_target_marker_index = 0 
                    if self.laps_completed >= total_race_laps: 
                        game_state = STATE_RACE_COMPLETE
                        time_taken_for_level = (pygame.time.get_ticks() - level_timer_start_ticks) / 1000.0 
                        if total_race_laps not in high_scores["best_total_race_times"] or \
                           time_taken_for_level < high_scores["best_total_race_times"][total_race_laps]:
                            high_scores["best_total_race_times"][total_race_laps] = time_taken_for_level

    def apply_lift_from_thermal(self, thermal_lift_power_at_nominal_speed):
        global game_difficulty; 
        if self.speed < STALL_SPEED: return 
        actual_lift_power = thermal_lift_power_at_nominal_speed
        if game_difficulty == DIFFICULTY_EASY: 
            actual_lift_power *= EASY_MODE_THERMAL_LIFT_MULTIPLIER
        elif game_difficulty == DIFFICULTY_NOOB: 
            actual_lift_power *= NOOB_MODE_THERMAL_LIFT_MULTIPLIER
        self.height += max(actual_lift_power * (INITIAL_SPEED / max(self.speed, MIN_SPEED * 0.5)), actual_lift_power * 0.2)

# --- AI Glider Class ---
class AIGlider(GliderBase):
    def __init__(self, start_world_x, start_world_y):
        super().__init__(PASTEL_AI_GLIDER_BODY, PASTEL_AI_GLIDER_WING, start_world_x, start_world_y)
        self.speed = random.uniform(AI_SPEED_MIN, AI_SPEED_MAX)
        self.height = AI_TARGET_RACE_ALTITUDE + random.uniform(-50, 50) 
        self.target_speed = self.speed 
        self.speed_update_timer = random.randint(0, AI_TARGET_SPEED_UPDATE_INTERVAL // 2)

    def update(self, cam_x, cam_y, race_markers_list, total_laps_in_race):
        global game_state
        if not race_markers_list or game_state != STATE_RACE_PLAYING: 
            self.update_sprite_rotation_and_position(cam_x, cam_y)
            self.update_contrail()
            return
        
        target_marker = race_markers_list[self.current_target_marker_index]
        dx = target_marker.world_pos.x - self.world_x
        dy = target_marker.world_pos.y - self.world_y
        dist_to_marker = math.hypot(dx, dy)
        
        target_angle_rad = math.atan2(dy, dx)
        target_angle_deg = math.degrees(target_angle_rad)
        current_heading_deg = self.heading % 360
        target_angle_deg %= 360
        angle_diff = target_angle_deg - current_heading_deg
        if angle_diff > 180: angle_diff -= 360
        if angle_diff < -180: angle_diff += 360
        self.heading = (self.heading + (angle_diff * AI_TURN_RATE_SCALAR)) % 360
        
        if dist_to_marker < AI_MARKER_APPROACH_SLOWDOWN_DISTANCE:
            self.target_speed = AI_SPEED_MIN + (AI_SPEED_MAX - AI_SPEED_MIN) * \
                                (dist_to_marker / AI_MARKER_APPROACH_SLOWDOWN_DISTANCE) * \
                                AI_MARKER_APPROACH_MIN_SPEED_FACTOR
            self.target_speed = max(AI_SPEED_MIN * 0.8, self.target_speed)
            self.speed_update_timer = 0
        else:
            self.speed_update_timer += 1
            if self.speed_update_timer >= AI_TARGET_SPEED_UPDATE_INTERVAL:
                speed_range = AI_SPEED_MAX - AI_SPEED_MIN
                random_variation = random.uniform(-speed_range * AI_SPEED_VARIATION_FACTOR, 
                                                 speed_range * AI_SPEED_VARIATION_FACTOR)
                self.target_speed = self.speed + random_variation
                self.target_speed = max(AI_SPEED_MIN, min(self.target_speed, AI_SPEED_MAX))
                self.speed_update_timer = 0

        if self.speed < self.target_speed: 
            self.speed += ACCELERATION * 0.5 
        elif self.speed > self.target_speed: 
            self.speed -= ACCELERATION * 0.5
        self.speed = max(AI_SPEED_MIN * 0.7, min(self.speed, AI_SPEED_MAX * 1.1)) 
        
        alt_diff = AI_TARGET_RACE_ALTITUDE - self.height
        self.height += alt_diff * AI_ALTITUDE_CORRECTION_RATE 
        if self.height < 0: 
            self.height = 0 
        
        heading_rad = math.radians(self.heading)
        self.world_x += self.speed * math.cos(heading_rad)
        self.world_y += self.speed * math.sin(heading_rad)
        
        if dist_to_marker < target_marker.world_radius: 
            self.current_target_marker_index += 1
            if self.current_target_marker_index >= len(race_markers_list): 
                self.laps_completed += 1
                self.current_target_marker_index = 0
        
        self.update_sprite_rotation_and_position(cam_x, cam_y)
        self.update_contrail()

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
        normalized_radius = 0.5 if max_r == min_r else (self.radius - min_r) / (max_r - min_r)
        self.lifespan = min_l + (max_l - min_l) * normalized_radius
        self.initial_lifespan = self.lifespan
        self.lift_power = MAX_THERMAL_LIFT_POWER - (MAX_THERMAL_LIFT_POWER - MIN_THERMAL_LIFT_POWER) * (1 - normalized_radius)
        self.image = pygame.Surface([self.radius * 2, self.radius * 2], pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.creation_time = pygame.time.get_ticks()
        self.update_visuals()

    def update_visuals(self):
        pulse_alpha_factor = (math.sin(pygame.time.get_ticks() * 0.005 + self.creation_time * 0.01) * 0.3 + 0.7)
        age_factor = max(0, self.lifespan / self.initial_lifespan if self.initial_lifespan > 0 else 0)
        alpha = int(THERMAL_BASE_ALPHA * pulse_alpha_factor * age_factor)
        accent_alpha = int(THERMAL_ACCENT_ALPHA * pulse_alpha_factor * age_factor)
        visual_radius_factor = math.sin(pygame.time.get_ticks() * 0.002 + self.creation_time * 0.005) * 0.1 + 0.95
        current_visual_radius = int(self.radius * visual_radius_factor)
        self.image.fill((0, 0, 0, 0))
        pygame.draw.circle(self.image, (*PASTEL_THERMAL_PRIMARY, alpha), (self.radius, self.radius), current_visual_radius)
        pygame.draw.circle(self.image, (*PASTEL_THERMAL_ACCENT, accent_alpha), (self.radius, self.radius), int(current_visual_radius * 0.7), 2)

    def update(self, cam_x, cam_y):
        self.lifespan -= 1
        if self.lifespan <= 0:
            self.kill()
        else:
            self.update_visuals()
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
        self.rect = self.image.get_rect()
        self._draw_marker_image(False)

    def _draw_marker_image(self, is_active):
        if is_active:
            color_to_use = PASTEL_ACTIVE_MARKER_COLOR 
        else:
            color_to_use = PASTEL_MARKER_COLOR
        
        self.image.fill((0,0,0,0))
        pygame.draw.circle(self.image, color_to_use, (self.visual_radius, self.visual_radius), self.visual_radius)
        pygame.draw.circle(self.image, PASTEL_WHITE, (self.visual_radius, self.visual_radius), int(self.visual_radius * 0.7))
        font_obj = get_cached_font(None, int(self.visual_radius * 1.1))
        text_surf = font_obj.render(str(self.number), True, PASTEL_BLACK)
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
        scale = self.width / (2 * self.world_bounds_view_radius)
        rel_x = world_x - player_world_x
        rel_y = world_y - player_world_y
        mini_x = self.width / 2 + rel_x * scale
        mini_y = self.height / 2 + rel_y * scale
        return int(mini_x), int(mini_y)

    def draw(self, surface, player_glider, ai_gliders_list, course_markers):
        self.surface.fill(PASTEL_MINIMAP_BACKGROUND)
        player_mini_x, player_mini_y = self.width // 2, self.height // 2
        pygame.draw.circle(self.surface, PASTEL_GOLD, (player_mini_x, player_mini_y), 5)
        for ai in ai_gliders_list:
            ai_mini_x, ai_mini_y = self.world_to_minimap(ai.world_x, ai.world_y, player_glider.world_x, player_glider.world_y)
            if 0 <= ai_mini_x <= self.width and 0 <= ai_mini_y <= self.height:
                pygame.draw.circle(self.surface, PASTEL_AI_GLIDER_BODY, (ai_mini_x, ai_mini_y), 4)
        for i, marker_obj in enumerate(course_markers):
            mini_x, mini_y = self.world_to_minimap(marker_obj.world_pos.x, marker_obj.world_pos.y, player_glider.world_x, player_glider.world_y)
            if 0 <= mini_x <= self.width and 0 <= mini_y <= self.height:
                color_to_use = PASTEL_MARKER_COLOR 
                if i == player_glider.current_target_marker_index:
                    color_to_use = PASTEL_ACTIVE_MARKER_COLOR
                
                pygame.draw.circle(self.surface, color_to_use, (mini_x, mini_y), RACE_MARKER_VISUAL_RADIUS_MAP)
                font_obj = get_cached_font(None, 16)
                text_surf = font_obj.render(str(marker_obj.number), True, PASTEL_BLACK)
                text_rect = text_surf.get_rect(center=(mini_x, mini_y))
                self.surface.blit(text_surf, text_rect)
        pygame.draw.rect(self.surface, PASTEL_MINIMAP_BORDER, self.surface.get_rect(), 2)
        surface.blit(self.surface, self.rect)

# --- ForegroundCloud Class ---
class ForegroundCloud(pygame.sprite.Sprite):
    def __init__(self, initial_distribution=False, index=0, total_clouds=NUM_FOREGROUND_CLOUDS):
        super().__init__()
        global current_wind_speed_x, current_wind_speed_y
        self.width = random.randint(100, 250)
        self.height = random.randint(40, 80)
        self.image = pygame.Surface([self.width, self.height], pygame.SRCALPHA)
        for _ in range(random.randint(4, 7)):
            puff_w, puff_h = random.randint(int(self.width * 0.4), int(self.width * 0.8)), random.randint(int(self.height * 0.5), int(self.height * 0.9))
            puff_x, puff_y = random.randint(0, self.width - puff_w), random.randint(0, self.height - puff_h)
            pygame.draw.ellipse(self.image, (*PASTEL_CLOUD, random.randint(CLOUD_MIN_ALPHA, CLOUD_MAX_ALPHA)), (puff_x, puff_y, puff_w, puff_h))
        self.speed_factor = random.uniform(MIN_CLOUD_SPEED_FACTOR, MAX_CLOUD_SPEED_FACTOR)
        self.dx = current_wind_speed_x * self.speed_factor
        self.dy = current_wind_speed_y * self.speed_factor
        self.x_float = 0.0
        self.y_float = 0.0
        if initial_distribution:
            self.x_float = (index / total_clouds) * SCREEN_WIDTH - self.width / 2 + random.uniform(-SCREEN_WIDTH / (total_clouds * 2), SCREEN_WIDTH / (total_clouds * 2))
            self.y_float = float(random.randint(-self.height // 2, SCREEN_HEIGHT - self.height // 2))
        else:
            if self.dx == 0 and self.dy == 0:
                self.x_float, self.y_float = (float(random.choice([-self.width - 20, SCREEN_WIDTH + 20])), float(random.randint(-self.height, SCREEN_HEIGHT))) if random.choice([True, False]) else (float(random.randint(-self.width, SCREEN_WIDTH)), float(random.choice([-self.height - 20, SCREEN_HEIGHT + 20])))
            else:
                self.x_float, self.y_float = (float(SCREEN_WIDTH + random.randint(0, 100) + self.width / 2 if self.dx < 0 else -random.randint(0, 100) - self.width / 2), float(random.randint(-self.height // 2, SCREEN_HEIGHT - self.height // 2))) if abs(self.dx) > abs(self.dy) else (float(random.randint(-self.width // 2, SCREEN_WIDTH - self.width // 2)), float(SCREEN_HEIGHT + random.randint(0, 50) + self.height / 2 if self.dy < 0 else -random.randint(0, 50) - self.height / 2))
        self.rect = self.image.get_rect(topleft=(round(self.x_float), round(self.y_float)))

    def update(self):
        self.dx = current_wind_speed_x * self.speed_factor
        self.dy = current_wind_speed_y * self.speed_factor
        self.x_float += self.dx
        self.y_float += self.dy
        self.rect.topleft = (round(self.x_float), round(self.y_float))
        off_screen_margin_x = self.width * 1.5 + abs(self.dx * 20)
        off_screen_margin_y = self.height * 1.5 + abs(self.dy * 20)
        despawn = False
        if (self.dx < 0 and self.rect.right < -off_screen_margin_x) or \
           (self.dx > 0 and self.rect.left > SCREEN_WIDTH + off_screen_margin_x) or \
           (self.dy < 0 and self.rect.bottom < -off_screen_margin_y) or \
           (self.dy > 0 and self.rect.top > SCREEN_HEIGHT + off_screen_margin_y) or \
           (self.dx == 0 and self.dy == 0 and not (-off_screen_margin_x < self.rect.centerx < SCREEN_WIDTH + off_screen_margin_x and -off_screen_margin_y < self.rect.centery < SCREEN_HEIGHT + off_screen_margin_y)):
            despawn = True
        if despawn:
            self.kill()

# --- Endless Map Data & Functions ---
map_tile_random_generator = random.Random()
ELEVATION_CONTINENT_SCALE = 60.0
ELEVATION_MOUNTAIN_SCALE = 15.0
ELEVATION_HILL_SCALE = 5.0       
MOISTURE_PRIMARY_SCALE = 40.0
MOISTURE_SECONDARY_SCALE = 10.0
P_CONT = (73856093, 19349663)
P_MNT = (83492791, 52084219)
P_HILL = (39119077, 66826529)
P_MOIST_P = (23109781, 92953093)
P_MOIST_S = (47834583, 11634271)
NUM_MAJOR_RIVERS = 3
MAJOR_RIVERS_PARAMS = []
_river_param_random = random.Random() 

def regenerate_river_parameters():
    global MAJOR_RIVERS_PARAMS, _river_param_random
    MAJOR_RIVERS_PARAMS = []
    for _ in range(NUM_MAJOR_RIVERS):
        start_tile_x = _river_param_random.uniform(-RACE_COURSE_AREA_HALFWIDTH / TILE_SIZE / 3, RACE_COURSE_AREA_HALFWIDTH / TILE_SIZE / 3)
        start_tile_y = _river_param_random.uniform(-RACE_COURSE_AREA_HALFWIDTH / TILE_SIZE / 3, RACE_COURSE_AREA_HALFWIDTH / TILE_SIZE / 3)
        MAJOR_RIVERS_PARAMS.append({
            "amplitude": _river_param_random.uniform(10, 30), 
            "wavelength": _river_param_random.uniform(200, 450), 
            "phase_offset": _river_param_random.uniform(0, 2 * math.pi), 
            "base_x_offset": start_tile_x, 
            "base_y_offset": start_tile_y, 
            "orientation": _river_param_random.choice(['horizontal', 'vertical']),
            "width": _river_param_random.randint(1, 2) 
        })

def get_seeded_random_value_direct(unique_tile_x, unique_tile_y, scale, p_pair):
    global map_tile_random_generator
    scaled_x = math.floor(unique_tile_x / scale)
    scaled_y = math.floor(unique_tile_y / scale)
    map_tile_random_generator.seed((scaled_x * p_pair[0]) ^ (scaled_y * p_pair[1]))
    return map_tile_random_generator.random() 

def get_land_type_at_world_pos(world_x, world_y):
    global current_map_offset_x, current_map_offset_y, tile_type_cache
    unique_tile_x = math.floor((world_x + current_map_offset_x) / TILE_SIZE)
    unique_tile_y = math.floor((world_y + current_map_offset_y) / TILE_SIZE)
    cache_key = (unique_tile_x, unique_tile_y)
    if cache_key in tile_type_cache:
        return tile_type_cache[cache_key]
    
    e_continent = get_seeded_random_value_direct(unique_tile_x, unique_tile_y, ELEVATION_CONTINENT_SCALE, P_CONT)
    e_mountain  = get_seeded_random_value_direct(unique_tile_x, unique_tile_y, ELEVATION_MOUNTAIN_SCALE, P_MNT)
    e_hill      = get_seeded_random_value_direct(unique_tile_x, unique_tile_y, ELEVATION_HILL_SCALE, P_HILL)
    elevation = math.pow(0.50 * e_continent + 0.35 * e_mountain + 0.15 * e_hill, 1.8)
    elevation = min(max(elevation, 0.0), 1.0) 

    m_primary   = get_seeded_random_value_direct(unique_tile_x, unique_tile_y, MOISTURE_PRIMARY_SCALE, P_MOIST_P)
    m_secondary = get_seeded_random_value_direct(unique_tile_x, unique_tile_y, MOISTURE_SECONDARY_SCALE, P_MOIST_S)
    moisture = math.pow(0.7 * m_primary + 0.3 * m_secondary, 1.2)
    moisture = min(max(moisture, 0.0), 1.0) 
    
    final_type = LAND_TYPE_PLAINS 
    deep_water_thresh, shallow_water_thresh, beach_thresh = 0.18, 0.22, 0.24
    mountain_base_thresh, mountain_peak_thresh = 0.60, 0.75
    desert_thresh, grassland_thresh, temperate_forest_thresh = 0.20, 0.40, 0.65

    if elevation < deep_water_thresh:
        final_type = LAND_TYPE_WATER_DEEP
    elif elevation < shallow_water_thresh:
        final_type = LAND_TYPE_WATER_SHALLOW
    elif elevation < beach_thresh:
        final_type = LAND_TYPE_SAND_DESERT if moisture < desert_thresh * 1.2 else LAND_TYPE_SAND_BEACH
    elif elevation > mountain_peak_thresh:
        final_type = LAND_TYPE_MOUNTAIN_PEAK
    elif elevation > mountain_base_thresh:
        final_type = LAND_TYPE_MOUNTAIN_BASE
    else: 
        if moisture < desert_thresh:
            final_type = LAND_TYPE_SAND_DESERT
        elif moisture < grassland_thresh:
            final_type = LAND_TYPE_GRASSLAND
        elif moisture < temperate_forest_thresh:
            final_type = LAND_TYPE_PLAINS
        else:
            final_type = LAND_TYPE_FOREST_DENSE if moisture > 0.8 and elevation < mountain_base_thresh * 0.9 else LAND_TYPE_FOREST_TEMPERATE
    
    can_have_river = final_type not in (LAND_TYPE_MOUNTAIN_PEAK, LAND_TYPE_WATER_DEEP) and \
                     not (final_type == LAND_TYPE_SAND_DESERT and moisture < desert_thresh * 0.75)
    if can_have_river:
        for params in MAJOR_RIVERS_PARAMS:
            if params["orientation"] == 'horizontal':
                river_center_y_tile = params["amplitude"] * math.sin((unique_tile_x / params["wavelength"]) * 2 * math.pi + params["phase_offset"]) + params["base_y_offset"]
                if abs(unique_tile_y - river_center_y_tile) < params["width"]:
                    final_type = LAND_TYPE_RIVER
                    break
            else: 
                river_center_x_tile = params["amplitude"] * math.sin((unique_tile_y / params["wavelength"]) * 2 * math.pi + params["phase_offset"]) + params["base_x_offset"]
                if abs(unique_tile_x - river_center_x_tile) < params["width"]:
                    final_type = LAND_TYPE_RIVER
                    break
    
    tile_type_cache[cache_key] = final_type
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
font_cache = {}
def get_cached_font(font_name, size):
    key = (font_name, size)
    if key not in font_cache:
        if font_name: # If a specific font name is given, try to load it as a system font
            try:
                font_cache[key] = pygame.font.SysFont(font_name, size)
            except pygame.error: # Fallback if specified system font is not found or error
                font_cache[key] = pygame.font.Font(None, size) # Pygame's default font
        else: # If font_name is None, use Pygame's default font
            font_cache[key] = pygame.font.Font(None, size)
    return font_cache[key]

def draw_text(surface, text, size, x, y, color=PASTEL_WHITE, font_name=None, center=False, antialias=True, shadow=False, shadow_color=PASTEL_DARK_GRAY, shadow_offset=(1,1)):
    font = get_cached_font(font_name, size)
    text_surface = font.render(text, antialias, color)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.center = (x,y)
    else:
        text_rect.topleft = (x,y)
    if shadow:
        shadow_surface = font.render(text, antialias, shadow_color)
        surface.blit(shadow_surface, (text_rect.x + shadow_offset[0], text_rect.y + shadow_offset[1]))
    surface.blit(text_surface, text_rect) 

# --- Pygame Setup ---
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pastel Glider - Floating Dreams")
clock = pygame.time.Clock()

# --- Game Objects & Variables ---
player = PlayerGlider()
ai_gliders = pygame.sprite.Group() 
all_world_sprites = pygame.sprite.Group()
thermals_group = pygame.sprite.Group()
race_markers_group = pygame.sprite.Group() 
foreground_clouds_group = pygame.sprite.Group() 
game_state = STATE_START_SCREEN
current_level = 1
level_timer_start_ticks = 0
time_taken_for_level = 0.0 
current_thermal_spawn_rate = BASE_THERMAL_SPAWN_RATE
thermal_spawn_timer = 0
final_score = 0 
selected_difficulty_option = DIFFICULTY_NORMAL
selected_mode_option = MODE_FREE_FLY
selected_laps_option = 1 
lap_options = [1, 3, 5]                      
minimap = Minimap(MINIMAP_WIDTH, MINIMAP_HEIGHT, MINIMAP_MARGIN)

def generate_race_course(num_markers=8):
    global race_course_markers, all_world_sprites
    race_course_markers.clear() 
    for sprite in list(all_world_sprites): 
        if isinstance(sprite, RaceMarker):
            sprite.kill() 
    for i in range(num_markers):
        marker = RaceMarker(random.uniform(-RACE_COURSE_AREA_HALFWIDTH, RACE_COURSE_AREA_HALFWIDTH), 
                            random.uniform(-RACE_COURSE_AREA_HALFWIDTH, RACE_COURSE_AREA_HALFWIDTH), i + 1) 
        race_course_markers.append(marker)
        all_world_sprites.add(marker)      

def generate_new_wind():
    global current_wind_speed_x, current_wind_speed_y
    wind_angle_rad = random.uniform(0, 2 * math.pi)
    wind_strength = random.uniform(0.05, MAX_WIND_STRENGTH) 
    current_wind_speed_x = wind_strength * math.cos(wind_angle_rad)
    current_wind_speed_y = wind_strength * math.sin(wind_angle_rad)

def start_new_level(level_param):
    global current_level, level_timer_start_ticks, current_thermal_spawn_rate, thermal_spawn_timer, game_state
    global current_map_offset_x, current_map_offset_y, _river_param_random, total_race_laps, ai_gliders, tile_type_cache
    global player_race_lap_times, current_session_flight_start_ticks
    
    level_timer_start_ticks = pygame.time.get_ticks()
    current_map_offset_x = random.randint(-200000, 200000)
    current_map_offset_y = random.randint(-200000, 200000)
    tile_type_cache.clear() 
    _river_param_random.seed(current_level + pygame.time.get_ticks())
    regenerate_river_parameters()
    generate_new_wind() 
    
    thermals_group.empty()
    all_world_sprites.empty()
    race_course_markers.clear()
    ai_gliders.empty()
    foreground_clouds_group.empty()
    for i in range(NUM_FOREGROUND_CLOUDS):
        foreground_clouds_group.add(ForegroundCloud(initial_distribution=True, index=i))
    
    player.reset(start_height=INITIAL_HEIGHT) 
    player.current_lap_start_ticks = pygame.time.get_ticks() 
    current_session_flight_start_ticks = pygame.time.get_ticks()

    if current_game_mode == MODE_FREE_FLY:
        current_level = level_param
        current_thermal_spawn_rate = BASE_THERMAL_SPAWN_RATE + (THERMAL_SPAWN_RATE_INCREASE_PER_LEVEL * (current_level - 1))
        if game_difficulty == DIFFICULTY_NOOB:
            current_thermal_spawn_rate = max(20, current_thermal_spawn_rate // 2)
        elif game_difficulty == DIFFICULTY_EASY:
            current_thermal_spawn_rate = max(30, int(current_thermal_spawn_rate * 0.75))
        thermal_spawn_timer = 0
        game_state = STATE_PLAYING_FREE_FLY
    elif current_game_mode == MODE_RACE:
        total_race_laps = level_param
        generate_race_course() 
        for i in range(NUM_AI_OPPONENTS):
            angle_offset = math.pi + (i - NUM_AI_OPPONENTS / 2.0) * (math.pi / 6)
            dist_offset = 70 + i * 30 
            ai_start_x = player.world_x + dist_offset * math.cos(math.radians(player.heading) + angle_offset)
            ai_start_y = player.world_y + dist_offset * math.sin(math.radians(player.heading) + angle_offset)
            new_ai = AIGlider(ai_start_x, ai_start_y)
            ai_gliders.add(new_ai)
            all_world_sprites.add(new_ai) 
        current_thermal_spawn_rate = BASE_THERMAL_SPAWN_RATE * 1.5 
        if game_difficulty == DIFFICULTY_NOOB:
            current_thermal_spawn_rate = max(30, int(current_thermal_spawn_rate * 0.7))
        thermal_spawn_timer = 0
        game_state = STATE_RACE_PLAYING

def reset_to_main_menu():
    global game_state, current_level, final_score, current_wind_speed_x, current_wind_speed_y
    global selected_difficulty_option, selected_mode_option, selected_laps_option, ai_gliders, tile_type_cache, player_race_lap_times
    
    player.reset()
    thermals_group.empty()
    all_world_sprites.empty()
    race_markers_group.empty()
    race_course_markers.clear()
    ai_gliders.empty()
    foreground_clouds_group.empty()
    tile_type_cache.clear()
    player_race_lap_times = []
    
    current_wind_speed_x = -0.2
    current_wind_speed_y = 0.05
    for i in range(NUM_FOREGROUND_CLOUDS):
        foreground_clouds_group.add(ForegroundCloud(initial_distribution=True, index=i))
    
    current_level = 1
    final_score = 0
    selected_difficulty_option = DIFFICULTY_NORMAL
    selected_mode_option = MODE_FREE_FLY
    selected_laps_option = 1 
    game_state = STATE_START_SCREEN

# --- Screen Drawing Functions ---
def draw_start_screen_content(surface):
    surface.fill(PASTEL_DARK_GRAY) 
    draw_text(surface, "Pastel Glider", 72, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 - 20, PASTEL_PLAINS, font_name=HUD_FONT_NAME, center=True, shadow=True, shadow_color=PASTEL_BLACK)
    draw_text(surface, "Press ENTER to Begin", 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60, PASTEL_LIGHT_GRAY, font_name=HUD_FONT_NAME, center=True, shadow=True, shadow_color=PASTEL_BLACK)
    draw_text(surface, "UP/DOWN: Speed | L/R: Bank", 22, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4, PASTEL_WHITE, font_name=HUD_FONT_NAME, center=True)
    draw_text(surface, "Explore the skies, use thermals or race the course!", 22, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4 + 30, PASTEL_WHITE, font_name=HUD_FONT_NAME, center=True)

def draw_difficulty_select_screen(surface, selected_option_idx): 
    surface.fill(PASTEL_DARK_GRAY)
    draw_text(surface, "Select Difficulty", 56, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 5, PASTEL_GOLD, font_name=HUD_FONT_NAME, center=True, shadow=True, shadow_color=PASTEL_BLACK)
    option_spacing = 100
    start_y = SCREEN_HEIGHT // 2 - option_spacing
    difficulties_display = [
        ("N00b", "(More Thermals, Agile Turning)", DIFFICULTY_NOOB),
        ("Easy", "(Stronger Thermals, Easier Turning)", DIFFICULTY_EASY),
        ("Normal", "(Standard Challenge & Turning)", DIFFICULTY_NORMAL)
    ]
    for i, (name, desc, diff_const) in enumerate(difficulties_display):
        color = PASTEL_WHITE if selected_option_idx == diff_const else PASTEL_GRAY
        draw_text(surface, name, 48, SCREEN_WIDTH // 2, start_y + i * option_spacing, color, font_name=HUD_FONT_NAME, center=True, shadow=True, shadow_color=PASTEL_BLACK)
        draw_text(surface, desc, 22, SCREEN_WIDTH // 2, start_y + i * option_spacing + 35, color, font_name=HUD_FONT_NAME, center=True) 
    draw_text(surface, "Use UP/DOWN keys, ENTER to confirm", 22, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.85, PASTEL_LIGHT_GRAY, font_name=HUD_FONT_NAME, center=True)

def draw_mode_select_screen(surface, selected_option_idx): 
    surface.fill(PASTEL_DARK_GRAY)
    draw_text(surface, "Select Mode", 56, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4, PASTEL_GOLD, font_name=HUD_FONT_NAME, center=True, shadow=True, shadow_color=PASTEL_BLACK)
    modes_display = [
        ("Free Fly", "(Explore & Reach Altitude Goals)", MODE_FREE_FLY),
        ("Race", "(Fly Through Markers Against AI)", MODE_RACE)
    ]
    for i, (name, desc, mode_const) in enumerate(modes_display):
        color = PASTEL_WHITE if selected_option_idx == mode_const else PASTEL_GRAY
        y_pos = SCREEN_HEIGHT // 2 - 30 + i * 100 
        draw_text(surface, name, 48, SCREEN_WIDTH // 2, y_pos, color, font_name=HUD_FONT_NAME, center=True, shadow=True, shadow_color=PASTEL_BLACK)
        draw_text(surface, desc, 22, SCREEN_WIDTH // 2, y_pos + 35, color, font_name=HUD_FONT_NAME, center=True) 
    draw_text(surface, "Use UP/DOWN keys, ENTER to confirm", 22, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4 + 50, PASTEL_LIGHT_GRAY, font_name=HUD_FONT_NAME, center=True)

def draw_laps_select_screen(surface, selected_lap_idx, lap_choices_list): 
    surface.fill(PASTEL_DARK_GRAY)
    draw_text(surface, "Select Laps", 56, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4, PASTEL_GOLD, font_name=HUD_FONT_NAME, center=True, shadow=True, shadow_color=PASTEL_BLACK)
    y_offset = SCREEN_HEIGHT // 2 - (len(lap_choices_list) - 1) * 40 
    for i, laps in enumerate(lap_choices_list):
        color = PASTEL_WHITE if i == selected_lap_idx else PASTEL_GRAY
        draw_text(surface, f"{laps} Lap{'s' if laps > 1 else ''}", 48, SCREEN_WIDTH // 2, y_offset + i * 80, color, font_name=HUD_FONT_NAME, center=True, shadow=True, shadow_color=PASTEL_BLACK)
    draw_text(surface, "Use UP/DOWN keys, ENTER to start race", 22, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4 + 50, PASTEL_LIGHT_GRAY, font_name=HUD_FONT_NAME, center=True)

def draw_target_reached_options_screen(surface, level, time_taken_seconds_val):
    surface.fill(PASTEL_DARK_GRAY)
    draw_text(surface, f"Level {level} Goal Reached!", 60, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 - 20, PASTEL_GOLD, font_name=HUD_FONT_NAME, center=True, shadow=True, shadow_color=PASTEL_BLACK)
    draw_text(surface, f"Time: {time_taken_seconds_val:.1f}s", 36, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40, PASTEL_WHITE, font_name=HUD_FONT_NAME, center=True)
    draw_text(surface, "Press M to Move On to Next Level", 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30, PASTEL_LIGHT_GRAY, font_name=HUD_FONT_NAME, center=True)
    draw_text(surface, "Press C to Continue Flying This Level", 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70, PASTEL_LIGHT_GRAY, font_name=HUD_FONT_NAME, center=True)

def draw_post_goal_menu_screen(surface, level): 
    surface.fill(PASTEL_DARK_GRAY)
    draw_text(surface, f"Level {level} - Cruising", 50, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4, PASTEL_GOLD, font_name=HUD_FONT_NAME, center=True, shadow=True, shadow_color=PASTEL_BLACK)
    draw_text(surface, "Press N for Next Level", 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30, PASTEL_LIGHT_GRAY, font_name=HUD_FONT_NAME, center=True)
    draw_text(surface, "Press Q to Quit to Main Menu", 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10, PASTEL_LIGHT_GRAY, font_name=HUD_FONT_NAME, center=True)
    draw_text(surface, "Press R or ESCAPE to Resume Flying", 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50, PASTEL_LIGHT_GRAY, font_name=HUD_FONT_NAME, center=True)

def draw_pause_menu_screen(surface):
    dim_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    dim_surface.fill((0, 0, 0, 100)) 
    surface.blit(dim_surface, (0,0))
    draw_text(surface, "Paused", 72, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3, PASTEL_GOLD, font_name=HUD_FONT_NAME, center=True, shadow=True)
    draw_text(surface, "Press C to Continue", 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, PASTEL_LIGHT_GRAY, font_name=HUD_FONT_NAME, center=True)
    draw_text(surface, "Press Q for Main Menu", 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40, PASTEL_LIGHT_GRAY, font_name=HUD_FONT_NAME, center=True)

def draw_race_complete_screen(surface, total_time_seconds):
    surface.fill(PASTEL_DARK_GRAY)
    draw_text(surface, "Race Finished!", 60, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 - 20, PASTEL_GOLD, font_name=HUD_FONT_NAME, center=True, shadow=True, shadow_color=PASTEL_BLACK)
    draw_text(surface, f"Total Time: {total_time_seconds:.1f}s", 40, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20, PASTEL_WHITE, font_name=HUD_FONT_NAME, center=True)
    if player_race_lap_times:
        draw_text(surface, "Lap Times:", HUD_FONT_SIZE_LARGE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20, PASTEL_WHITE, font_name=HUD_FONT_NAME, center=True)
        for i, lap_time in enumerate(player_race_lap_times):
            draw_text(surface, f"Lap {i+1}: {lap_time:.1f}s", HUD_FONT_SIZE_NORMAL, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 55 + (i * 28), PASTEL_LIGHT_GRAY, font_name=HUD_FONT_NAME, center=True)
    draw_text(surface, "Press ENTER for Main Menu", 32, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 5 // 6, PASTEL_LIGHT_GRAY, font_name=HUD_FONT_NAME, center=True)

def draw_game_over_screen_content(surface, final_player_height, level_reached):
    surface.fill(PASTEL_DARK_GRAY)
    draw_text(surface, "GAME OVER", 72, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4, PASTEL_RED, font_name=HUD_FONT_NAME, center=True, shadow=True, shadow_color=PASTEL_BLACK)
    y_offset = SCREEN_HEIGHT // 2 - 80 
    if current_game_mode == MODE_FREE_FLY:
        draw_text(surface, f"Reached Level: {level_reached}", HUD_FONT_SIZE_LARGE, SCREEN_WIDTH // 2, y_offset, PASTEL_WHITE, font_name=HUD_FONT_NAME, center=True); y_offset += 35
        draw_text(surface, f"Max Altitude: {int(high_scores['max_altitude_free_fly'])}m", HUD_FONT_SIZE_LARGE, SCREEN_WIDTH // 2, y_offset, PASTEL_WHITE, font_name=HUD_FONT_NAME, center=True); y_offset += 35
        draw_text(surface, f"Longest Flight: {high_scores['longest_flight_time_free_fly']:.1f}s", HUD_FONT_SIZE_LARGE, SCREEN_WIDTH // 2, y_offset, PASTEL_WHITE, font_name=HUD_FONT_NAME, center=True); y_offset += 35
    elif current_game_mode == MODE_RACE:
        if total_race_laps in high_scores["best_total_race_times"]:
             draw_text(surface, f"Best Race ({total_race_laps} Laps): {high_scores['best_total_race_times'][total_race_laps]:.1f}s", HUD_FONT_SIZE_NORMAL, SCREEN_WIDTH // 2, y_offset, PASTEL_WHITE, font_name=HUD_FONT_NAME, center=True); y_offset += 30
        if high_scores["best_lap_time_race"] != float('inf'):
            draw_text(surface, f"Best Lap: {high_scores['best_lap_time_race']:.1f}s", HUD_FONT_SIZE_NORMAL, SCREEN_WIDTH // 2, y_offset, PASTEL_WHITE, font_name=HUD_FONT_NAME, center=True); y_offset += 30
    draw_text(surface, f"Final Height: {int(final_player_height)}m", HUD_FONT_SIZE_LARGE, SCREEN_WIDTH // 2, y_offset, PASTEL_WHITE, font_name=HUD_FONT_NAME, center=True); y_offset += 40
    draw_text(surface, "Press ENTER for Menu", 32, SCREEN_WIDTH // 2, y_offset + 20, PASTEL_LIGHT_GRAY, font_name=HUD_FONT_NAME, center=True)

def draw_height_indicator_hud(surface, current_player_height, target_h_for_level, vertical_speed_val):
    indicator_bar_height = SCREEN_HEIGHT - HUD_HEIGHT - (2 * INDICATOR_Y_MARGIN_FROM_HUD)
    indicator_x_pos = SCREEN_WIDTH - INDICATOR_WIDTH - INDICATOR_X_MARGIN
    indicator_y_pos = HUD_HEIGHT + INDICATOR_Y_MARGIN_FROM_HUD
    pygame.draw.rect(surface, PASTEL_INDICATOR_COLOR, (indicator_x_pos, indicator_y_pos, INDICATOR_WIDTH, indicator_bar_height))
    
    max_indicator_height_value = target_h_for_level * 1.15 if current_game_mode == MODE_FREE_FLY else current_player_height + 500
    max_indicator_height_value = max(1, max_indicator_height_value) 
    
    ground_line_y = indicator_y_pos + indicator_bar_height
    pygame.draw.line(surface, PASTEL_INDICATOR_GROUND, (indicator_x_pos - 5, ground_line_y), (indicator_x_pos + INDICATOR_WIDTH + 5, ground_line_y), 3)
    draw_text(surface, "0m", 14, indicator_x_pos + INDICATOR_WIDTH + 8, ground_line_y - 7, PASTEL_TEXT_COLOR_HUD, font_name=HUD_FONT_NAME)
    
    if current_game_mode == MODE_FREE_FLY and target_h_for_level > 0:
        target_ratio = min(target_h_for_level / max_indicator_height_value, 1.0) 
        target_marker_y_on_bar = indicator_y_pos + indicator_bar_height * (1 - target_ratio) 
        pygame.draw.line(surface, PASTEL_GREEN_TARGET, (indicator_x_pos - 5, target_marker_y_on_bar), (indicator_x_pos + INDICATOR_WIDTH + 5, target_marker_y_on_bar), 3)
        draw_text(surface, f"{target_h_for_level}m", 14, indicator_x_pos + INDICATOR_WIDTH + 8, target_marker_y_on_bar - 7, PASTEL_GREEN_TARGET, font_name=HUD_FONT_NAME)
    
    player_marker_y_on_bar = ground_line_y 
    if current_player_height > 0:
        player_marker_y_on_bar = indicator_y_pos + indicator_bar_height * (1 - min(current_player_height / max_indicator_height_value, 1.0))
    player_marker_y_on_bar = max(indicator_y_pos, min(player_marker_y_on_bar, ground_line_y))
    pygame.draw.line(surface, PASTEL_GOLD, (indicator_x_pos, player_marker_y_on_bar), (indicator_x_pos + INDICATOR_WIDTH, player_marker_y_on_bar), 5)
    
    vsi_text_x = indicator_x_pos - 70
    vsi_arrow_x_center = indicator_x_pos - 10 
    vsi_mps = vertical_speed_val * clock.get_fps() if clock.get_fps() > 0 else vertical_speed_val * 60 
    vsi_color = PASTEL_VSI_CLIMB if vsi_mps > 0.5 else (PASTEL_VSI_SINK if vsi_mps < -0.5 else PASTEL_TEXT_COLOR_HUD)
    draw_text(surface, f"{vsi_mps:+.1f}m/s", 14, vsi_text_x , player_marker_y_on_bar - 7, vsi_color, font_name=HUD_FONT_NAME)
    
    if abs(vsi_mps) > 0.5: 
        arrow_points = []
        if vsi_mps > 0: 
            arrow_points = [(vsi_arrow_x_center, player_marker_y_on_bar - VSI_ARROW_SIZE), 
                            (vsi_arrow_x_center - VSI_ARROW_SIZE // 2, player_marker_y_on_bar), 
                            (vsi_arrow_x_center + VSI_ARROW_SIZE // 2, player_marker_y_on_bar)] 
        else: 
            arrow_points = [(vsi_arrow_x_center, player_marker_y_on_bar + VSI_ARROW_SIZE), 
                            (vsi_arrow_x_center - VSI_ARROW_SIZE // 2, player_marker_y_on_bar), 
                            (vsi_arrow_x_center + VSI_ARROW_SIZE // 2, player_marker_y_on_bar)]
        pygame.draw.polygon(surface, vsi_color, arrow_points)
    
    player_height_text_y = player_marker_y_on_bar - 20 
    if player_height_text_y < indicator_y_pos + 5:
        player_height_text_y = player_marker_y_on_bar + 15 
    draw_text(surface, f"{int(current_player_height)}m", 14, vsi_text_x, player_height_text_y, PASTEL_GOLD, font_name=HUD_FONT_NAME)

def draw_dial(surface, center_x, center_y, radius, hand_angle_degrees, hand_color, dial_color=PASTEL_GRAY, border_color=PASTEL_TEXT_COLOR_HUD):
    pygame.draw.circle(surface, dial_color, (center_x, center_y), radius)
    pygame.draw.circle(surface, border_color, (center_x, center_y), radius, 1)
    draw_text(surface, "N", HUD_FONT_SIZE_SMALL - 6 , center_x, center_y - radius + 7, border_color, font_name=HUD_FONT_NAME, center=True)

    hand_angle_rad = math.radians(hand_angle_degrees - 90) 
    hand_end_x = center_x + (radius * 0.8) * math.cos(hand_angle_rad)
    hand_end_y = center_y + (radius * 0.8) * math.sin(hand_angle_rad)
    pygame.draw.line(surface, hand_color, (center_x, center_y), (hand_end_x, hand_end_y), 2)

def draw_weather_vane(surface, wind_x, wind_y, center_x, center_y, radius=22, max_strength_for_scaling=MAX_WIND_STRENGTH):
    vane_angle_rad = math.atan2(wind_y, wind_x) + math.pi
    wind_magnitude = math.hypot(wind_x, wind_y)
    arrow_color = PASTEL_TEXT_COLOR_HUD
    arrow_thickness = 2
    dial_color = PASTEL_GRAY
    border_color = PASTEL_TEXT_COLOR_HUD
    
    pygame.draw.circle(surface, dial_color, (center_x, center_y), radius)
    pygame.draw.circle(surface, border_color, (center_x, center_y), radius, 1)
    draw_text(surface, "N", HUD_FONT_SIZE_SMALL -6, center_x, center_y - radius + 7, border_color, font_name=HUD_FONT_NAME, center=True)

    strength_ratio = min(wind_magnitude / max_strength_for_scaling, 1.0) if max_strength_for_scaling > 0 else 0.0
    current_arrow_length = radius * (0.5 + strength_ratio * 0.4) 

    tip_x = center_x + current_arrow_length * math.cos(vane_angle_rad)
    tip_y = center_y + current_arrow_length * math.sin(vane_angle_rad)
    tail_x = center_x - current_arrow_length * 0.3 * math.cos(vane_angle_rad) 
    tail_y = center_y - current_arrow_length * 0.3 * math.sin(vane_angle_rad)
    
    pygame.draw.line(surface, arrow_color, (tail_x, tail_y), (tip_x, tip_y), arrow_thickness)
    
    barb_length = radius * 0.35
    barb_angle_offset = math.radians(150) 
    pygame.draw.line(surface, arrow_color, (tip_x, tip_y), (tip_x + barb_length * math.cos(vane_angle_rad + barb_angle_offset), tip_y + barb_length * math.sin(vane_angle_rad + barb_angle_offset)), arrow_thickness)
    pygame.draw.line(surface, arrow_color, (tip_x, tip_y), (tip_x + barb_length * math.cos(vane_angle_rad - barb_angle_offset), tip_y + barb_length * math.sin(vane_angle_rad - barb_angle_offset)), arrow_thickness)
    
# --- Game Loop ---
running = True
while running:
    dt = clock.tick(60) / 1000.0
    current_ticks = pygame.time.get_ticks()
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if game_state == STATE_PAUSED:
                if event.key == pygame.K_c: 
                    time_spent_paused = pygame.time.get_ticks() - pause_start_ticks
                    level_timer_start_ticks += time_spent_paused
                    player.current_lap_start_ticks += time_spent_paused
                    current_session_flight_start_ticks += time_spent_paused
                    game_state = game_state_before_pause
                elif event.key == pygame.K_q:
                    reset_to_main_menu()
            elif game_state in (STATE_PLAYING_FREE_FLY, STATE_RACE_PLAYING, STATE_TARGET_REACHED_CONTINUE_PLAYING) and event.key == pygame.K_ESCAPE:
                if game_state != STATE_PAUSED: 
                    game_state_before_pause = game_state
                    game_state = STATE_PAUSED
                    pause_start_ticks = pygame.time.get_ticks()
            elif game_state == STATE_START_SCREEN:
                if event.key == pygame.K_RETURN:
                    game_state = STATE_DIFFICULTY_SELECT
            elif game_state == STATE_DIFFICULTY_SELECT:
                if event.key == pygame.K_UP:
                    selected_difficulty_option = (selected_difficulty_option - 1 + len(difficulty_options_map)) % len(difficulty_options_map)
                elif event.key == pygame.K_DOWN:
                    selected_difficulty_option = (selected_difficulty_option + 1) % len(difficulty_options_map)
                elif event.key == pygame.K_RETURN:
                    game_difficulty = selected_difficulty_option
                    game_state = STATE_MODE_SELECT
            elif game_state == STATE_MODE_SELECT:
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    selected_mode_option = 1 - selected_mode_option
                elif event.key == pygame.K_RETURN:
                    current_game_mode = selected_mode_option
                    if current_game_mode == MODE_FREE_FLY:
                        start_new_level(1) 
                    else:
                        game_state = STATE_RACE_LAPS_SELECT
            elif game_state == STATE_RACE_LAPS_SELECT:
                if event.key == pygame.K_UP:
                    selected_laps_option = (selected_laps_option - 1 + len(lap_options)) % len(lap_options)
                elif event.key == pygame.K_DOWN:
                    selected_laps_option = (selected_laps_option + 1) % len(lap_options)
                elif event.key == pygame.K_RETURN:
                    start_new_level(lap_options[selected_laps_option]) 
            elif game_state == STATE_TARGET_REACHED_OPTIONS: 
                if event.key == pygame.K_m:
                    start_new_level(current_level + 1)
                elif event.key == pygame.K_c:
                    game_state = STATE_TARGET_REACHED_CONTINUE_PLAYING
            elif game_state == STATE_POST_GOAL_MENU: 
                if event.key == pygame.K_n:
                    start_new_level(current_level + 1)
                elif event.key == pygame.K_q:
                    reset_to_main_menu()
                elif event.key == pygame.K_r or event.key == pygame.K_ESCAPE:
                    game_state = STATE_TARGET_REACHED_CONTINUE_PLAYING
            elif game_state == STATE_RACE_COMPLETE:
                if event.key == pygame.K_RETURN:
                    reset_to_main_menu()
            elif game_state == STATE_GAME_OVER:
                if event.key == pygame.K_RETURN:
                    reset_to_main_menu()

    if game_state not in (STATE_PAUSED, STATE_START_SCREEN, STATE_DIFFICULTY_SELECT, STATE_MODE_SELECT, STATE_RACE_LAPS_SELECT, STATE_TARGET_REACHED_OPTIONS, STATE_POST_GOAL_MENU, STATE_RACE_COMPLETE, STATE_GAME_OVER):
        player.update(keys)
        camera_x = player.world_x - SCREEN_WIDTH // 2
        camera_y = player.world_y - SCREEN_HEIGHT // 2
        
        if game_state == STATE_RACE_PLAYING:
            for ai in ai_gliders:
                ai.update(camera_x, camera_y, race_course_markers, total_race_laps)
            collided_ais = pygame.sprite.spritecollide(player, ai_gliders, False, pygame.sprite.collide_circle)
            for ai_hit in collided_ais:
                player.apply_collision_effect()
                ai_hit.apply_collision_effect()
            ai_list = list(ai_gliders)
            for i in range(len(ai_list)):
                for j in range(i + 1, len(ai_list)):
                    ai1, ai2 = ai_list[i], ai_list[j]
                    if ((ai1.world_x - ai2.world_x)**2 + (ai1.world_y - ai2.world_y)**2) < (ai1.collision_radius + ai2.collision_radius)**2:
                        ai1.apply_collision_effect()
                        ai2.apply_collision_effect()
        
        for thermal_sprite in thermals_group:
            thermal_sprite.update(camera_x, camera_y)
        
        thermal_spawn_timer += 1
        if thermal_spawn_timer >= current_thermal_spawn_rate:
            thermal_spawn_timer = 0
            spawn_world_x = camera_x + random.randint(-THERMAL_SPAWN_AREA_WIDTH // 2, THERMAL_SPAWN_AREA_WIDTH // 2)
            spawn_world_y = camera_y + random.randint(-THERMAL_SPAWN_AREA_HEIGHT // 2, THERMAL_SPAWN_AREA_HEIGHT // 2)
            if random.random() < LAND_TYPE_THERMAL_PROBABILITY.get(get_land_type_at_world_pos(spawn_world_x, spawn_world_y), 0.0):
                new_thermal = Thermal((spawn_world_x, spawn_world_y))
                all_world_sprites.add(new_thermal)
                thermals_group.add(new_thermal)
        
        if game_state == STATE_RACE_PLAYING:
            for i, marker in enumerate(race_course_markers):
                marker.update(camera_x, camera_y, i == player.current_target_marker_index)
        
        foreground_clouds_group.update()
        if len(foreground_clouds_group) < NUM_FOREGROUND_CLOUDS:
            foreground_clouds_group.add(ForegroundCloud())
        
        for thermal in thermals_group:
            if math.hypot(player.world_x - thermal.world_pos.x, player.world_y - thermal.world_pos.y) < thermal.radius + (player.collision_radius * 0.5):
                player.apply_lift_from_thermal(thermal.lift_power)
        
        if game_state == STATE_PLAYING_FREE_FLY and player.height >= TARGET_HEIGHT_PER_LEVEL * current_level:
            game_state = STATE_TARGET_REACHED_OPTIONS
            level_end_ticks = pygame.time.get_ticks()
            time_taken_for_level = (level_end_ticks - level_timer_start_ticks) / 1000.0
        
        if player.height <= 0:
            final_score = player.height 
            player.height = 0
            game_state = STATE_GAME_OVER
            if current_game_mode == MODE_FREE_FLY:
                session_duration = (pygame.time.get_ticks() - current_session_flight_start_ticks) / 1000.0
                if session_duration > high_scores["longest_flight_time_free_fly"]:
                    high_scores["longest_flight_time_free_fly"] = session_duration
    
    screen.fill(PASTEL_BLACK)
    
    if game_state in (STATE_PLAYING_FREE_FLY, STATE_TARGET_REACHED_CONTINUE_PLAYING, STATE_RACE_PLAYING, STATE_PAUSED): # Corrected this line
        draw_endless_map(screen, camera_x, camera_y)
        player.draw_contrail(screen, camera_x, camera_y)
        for ags in ai_gliders:
            ags.draw_contrail(screen, camera_x, camera_y)
        all_world_sprites.draw(screen)
        screen.blit(player.image, player.rect) 
        foreground_clouds_group.draw(screen) 
        
        hud_sfc = pygame.Surface((SCREEN_WIDTH, HUD_HEIGHT), pygame.SRCALPHA)
        hud_sfc.fill(PASTEL_HUD_PANEL)
        screen.blit(hud_sfc, (0,0))
        
        hm, ls, cyh = 10, 28, 8 
        
        if current_game_mode == MODE_FREE_FLY:
            draw_text(screen, f"Level: {current_level}", HUD_FONT_SIZE_NORMAL, hm, cyh, PASTEL_TEXT_COLOR_HUD, font_name=HUD_FONT_NAME)
            draw_text(screen, f"Target: {TARGET_HEIGHT_PER_LEVEL * current_level}m", HUD_FONT_SIZE_NORMAL, hm + 150, cyh, PASTEL_TEXT_COLOR_HUD, font_name=HUD_FONT_NAME)
        elif current_game_mode == MODE_RACE:
            draw_text(screen, f"Lap: {min(player.laps_completed + 1, total_race_laps)}/{total_race_laps}", HUD_FONT_SIZE_NORMAL, hm, cyh, PASTEL_TEXT_COLOR_HUD, font_name=HUD_FONT_NAME)
            current_lap_time_display = 0.0
            if game_state == STATE_RACE_PLAYING :
                 current_lap_time_display = (pygame.time.get_ticks() - player.current_lap_start_ticks) / 1000.0
            elif player_race_lap_times and player.laps_completed < total_race_laps:
                 current_lap_time_display = player_race_lap_times[-1] if player_race_lap_times else 0.0
            draw_text(screen, f"Lap Time: {current_lap_time_display:.1f}s", HUD_FONT_SIZE_NORMAL, hm + 320, cyh, PASTEL_TEXT_COLOR_HUD, font_name=HUD_FONT_NAME)
            
            if race_course_markers and player.current_target_marker_index < len(race_course_markers) and game_state == STATE_RACE_PLAYING:
                tm = race_course_markers[player.current_target_marker_index]
                draw_text(screen, f"Marker {tm.number}: {int(math.hypot(player.world_x - tm.world_pos.x, player.world_y - tm.world_pos.y) / 10.0)} u", HUD_FONT_SIZE_NORMAL, hm + 150, cyh, PASTEL_TEXT_COLOR_HUD, font_name=HUD_FONT_NAME)
                
                marker_dx = tm.world_pos.x - player.world_x; marker_dy = tm.world_pos.y - player.world_y
                angle_to_marker_world_rad = math.atan2(marker_dy, marker_dx); angle_to_marker_world_deg = math.degrees(angle_to_marker_world_rad)
                relative_angle_to_marker = (angle_to_marker_world_deg - player.heading + 360) % 360
                
                marker_dial_x = SCREEN_WIDTH - MINIMAP_WIDTH - MINIMAP_MARGIN - 180 
                draw_dial(screen, marker_dial_x, hm + HUD_HEIGHT // 2 - 10, 22, relative_angle_to_marker, PASTEL_ACTIVE_MARKER_COLOR) 

        cyh += ls
        timer_s = (current_ticks - level_timer_start_ticks) / 1000.0 if game_state in (STATE_PLAYING_FREE_FLY, STATE_RACE_PLAYING) else time_taken_for_level
        goal_text = " (Goal!)" if game_state == STATE_TARGET_REACHED_CONTINUE_PLAYING else ""
        draw_text(screen, f"Time: {timer_s:.1f}s{goal_text}", HUD_FONT_SIZE_NORMAL, hm, cyh, PASTEL_TEXT_COLOR_HUD, font_name=HUD_FONT_NAME)
        
        cyh += ls
        draw_text(screen, f"Height: {int(player.height)}m", HUD_FONT_SIZE_NORMAL, hm, cyh, PASTEL_TEXT_COLOR_HUD, font_name=HUD_FONT_NAME)
        draw_text(screen, f"Speed: {player.speed:.1f}", HUD_FONT_SIZE_NORMAL, hm + 150, cyh, PASTEL_TEXT_COLOR_HUD, font_name=HUD_FONT_NAME)
        if player.speed < STALL_SPEED:
            draw_text(screen, "STALL!", HUD_FONT_SIZE_LARGE, SCREEN_WIDTH // 2, hm + ls // 2, PASTEL_RED, font_name=HUD_FONT_NAME, center=True, shadow=True, shadow_color=PASTEL_BLACK)
        
        wind_text_x_pos = SCREEN_WIDTH - MINIMAP_WIDTH - MINIMAP_MARGIN - 125 
        draw_text(screen, f"Wind:", HUD_FONT_SIZE_SMALL, wind_text_x_pos - 50, hm + HUD_HEIGHT // 2 - 22, PASTEL_TEXT_COLOR_HUD, font_name=HUD_FONT_NAME) 
        draw_weather_vane(screen, current_wind_speed_x, current_wind_speed_y, wind_text_x_pos, hm + HUD_HEIGHT // 2 - 10 , 22) 
        
        et = "ESC for Menu"
        if game_state == STATE_TARGET_REACHED_CONTINUE_PLAYING: et = "ESC for Options"
        elif game_state == STATE_PLAYING_FREE_FLY or game_state == STATE_RACE_PLAYING: et = "ESC to Pause"
        draw_text(screen, et, HUD_FONT_SIZE_SMALL, SCREEN_WIDTH - 150, SCREEN_HEIGHT - 30, PASTEL_LIGHT_GRAY, font_name=HUD_FONT_NAME, center=True) 
        
        draw_height_indicator_hud(screen, player.height, TARGET_HEIGHT_PER_LEVEL * current_level if current_game_mode == MODE_FREE_FLY else player.height + 100, player.vertical_speed)
        
        if current_game_mode == MODE_RACE and (game_state == STATE_RACE_PLAYING or game_state == STATE_RACE_COMPLETE or game_state == STATE_PAUSED):
            minimap.draw(screen, player, ai_gliders, race_course_markers)
        
        if game_state == STATE_PAUSED:
            draw_pause_menu_screen(screen)

    elif game_state == STATE_START_SCREEN:
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
    elif game_state == STATE_GAME_OVER:
        draw_game_over_screen_content(screen, final_score, current_level); foreground_clouds_group.draw(screen)
    
    pygame.display.flip()
pygame.quit()

