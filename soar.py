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
MAX_BANK_ANGLE = 45  # Player's max bank
BANK_RATE = 2
TURN_RATE_SCALAR = 0.1
GLIDER_COLLISION_RADIUS = 20  # For player and AI

# AI Specific
NUM_AI_OPPONENTS = 3  # Number of AI racers
AI_TARGET_RACE_ALTITUDE = 450  # AI will try to stay around this height
AI_ALTITUDE_CORRECTION_RATE = 0.2
AI_SPEED_MIN = 2.5
AI_SPEED_MAX = 4.5
AI_TURN_RATE_SCALAR = 0.08  # How sharply AI can turn
AI_MARKER_APPROACH_SLOWDOWN_DISTANCE = 200  # Distance to start slowing for a marker
AI_MARKER_APPROACH_MIN_SPEED_FACTOR = 0.6  # Slow down to this factor of their max speed

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
current_map_offset_x = 0 # World units
current_map_offset_y = 0 # World units
tile_type_cache = {} # Cache for generated tile types: key=(unique_tile_x, unique_tile_y), value=type

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

# Clouds (Screen-space effects)
NUM_FOREGROUND_CLOUDS = 15
MIN_CLOUD_SPEED_FACTOR = 1.5
MAX_CLOUD_SPEED_FACTOR = 2.5
CLOUD_MIN_ALPHA = 40
CLOUD_MAX_ALPHA = 100

# Game Mechanics
TARGET_HEIGHT_PER_LEVEL = 1000 # Base target height, scales with level in Free Fly
START_HEIGHT_NEW_LEVEL = 250 # Not currently used, player resets to INITIAL_HEIGHT

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
PASTEL_MARKER_COLOR = (255, 170, 170)
PASTEL_ACTIVE_MARKER_COLOR = (173, 255, 173)

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
PASTEL_CONTRAIL_COLOR = PASTEL_TEXT_COLOR_HUD # RGB for contrail base

MAP_TILE_OUTLINE_COLOR = (215, 220, 225)


# --- Land Types (Replaced Class with simple constants) ---
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

# --- Glider Base Class (for Player and AI) ---
class GliderBase(pygame.sprite.Sprite):
    def __init__(self, body_color, wing_color, start_world_x=0.0, start_world_y=0.0):
        super().__init__()
        # Glider dimensions
        self.fuselage_length = 45; self.fuselage_thickness = 4
        self.wing_span = 70; self.wing_chord = 5 # Main wing
        self.tail_plane_span = 18; self.tail_plane_chord = 4; self.tail_fin_height = 8 # Tail assembly
        
        # Create the base image (facing right, for 0 heading)
        # Canvas size needs to accommodate the largest dimension (wing_span if centered, or fuselage_length)
        # Let's make canvas centered around fuselage, wide enough for fuselage, tall enough for wingspan
        canvas_width = self.fuselage_length # Glider points along X axis
        canvas_height = self.wing_span    # Wings spread along Y axis
        self.original_image = pygame.Surface([canvas_width, canvas_height], pygame.SRCALPHA)
        
        # Fuselage (centered vertically on canvas, extends along full canvas_width)
        fuselage_y_top = (canvas_height - self.fuselage_thickness) / 2
        pygame.draw.rect(self.original_image, body_color, (0, fuselage_y_top, self.fuselage_length, self.fuselage_thickness))
        
        # Main Wing (centered on fuselage length-wise, extends full wing_span)
        wing_x_pos = (self.fuselage_length - self.wing_chord) * 0.65 # Position wing towards the front
        wing_y_pos = (canvas_height - self.wing_span) / 2 # This would be 0 if canvas_height = wing_span
        pygame.draw.rect(self.original_image, wing_color, (wing_x_pos, wing_y_pos, self.wing_chord, self.wing_span))
        
        # Tail Plane (horizontal stabilizer, at the rear of fuselage)
        tail_plane_x_pos = 0 # At the very back
        tail_plane_y_top = (canvas_height - self.tail_plane_span) / 2
        pygame.draw.rect(self.original_image, wing_color, (tail_plane_x_pos, tail_plane_y_top, self.tail_plane_chord, self.tail_plane_span))
        
        # Tail Fin (vertical stabilizer, on top of fuselage at the rear)
        fin_base_y_center = fuselage_y_top + self.fuselage_thickness / 2 # Center of fuselage
        fin_bottom_y = fin_base_y_center - self.fuselage_thickness / 2 # Top of fuselage
        fin_tip_y = fin_bottom_y - self.tail_fin_height
        fin_leading_edge_x = tail_plane_x_pos + self.tail_plane_chord * 0.2
        fin_trailing_edge_x = tail_plane_x_pos + self.tail_plane_chord * 0.8
        fin_tip_x = tail_plane_x_pos + self.tail_plane_chord * 0.5
        pygame.draw.polygon(self.original_image, body_color, [
            (fin_leading_edge_x, fin_bottom_y), (fin_trailing_edge_x, fin_bottom_y), (fin_tip_x, fin_tip_y)
        ])
        
        self.image = self.original_image # Current image for drawing
        self.rect = self.image.get_rect()
        self.collision_radius = GLIDER_COLLISION_RADIUS

        # World state
        self.world_x = start_world_x; self.world_y = start_world_y
        self.heading = 0 # Degrees, 0 is East/right, 90 is South/down
        self.bank_angle = 0 # Degrees
        self.height = INITIAL_HEIGHT # Altitude
        self.speed = INITIAL_SPEED # Airspeed

        # Contrail
        self.trail_points = [] # List of (world_x, world_y) for contrail
        self.contrail_frame_counter = 0

        # Race specific (initialized for both, used by AI and Player in race mode)
        self.current_target_marker_index = 0
        self.laps_completed = 0

    def update_sprite_rotation_and_position(self, cam_x=None, cam_y=None):
        # Rotate the original image based on heading
        self.image = pygame.transform.rotate(self.original_image, -self.heading) # Pygame rotates counter-clockwise
        
        # Set the rect for drawing
        if isinstance(self, PlayerGlider): # Player is always centered on screen
             self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        elif cam_x is not None and cam_y is not None: # AI gliders are world-positioned
             screen_x = self.world_x - cam_x
             screen_y = self.world_y - cam_y
             self.rect = self.image.get_rect(center=(screen_x, screen_y))


    def update_contrail(self):
        heading_rad = math.radians(self.heading)
        self.contrail_frame_counter +=1
        if self.contrail_frame_counter >= CONTRAIL_POINT_DELAY:
            self.contrail_frame_counter = 0
            # Calculate contrail point from the tail of the glider
            # Offset from glider's center (world_x, world_y) to its tail
            effective_tail_offset = (self.fuselage_length / 2) - 2 # Small offset from actual tail tip
            # Tail is behind the center when heading is 0 (pointing right)
            tail_offset_x_world = -effective_tail_offset * math.cos(heading_rad)
            tail_offset_y_world = -effective_tail_offset * math.sin(heading_rad)
            
            contrail_world_x = self.world_x + tail_offset_x_world
            contrail_world_y = self.world_y + tail_offset_y_world
            
            self.trail_points.append((contrail_world_x, contrail_world_y))
            if len(self.trail_points) > CONTRAIL_LENGTH:
                self.trail_points.pop(0) # Remove oldest point

    def draw_contrail(self, surface, cam_x, cam_y):
        if len(self.trail_points) > 1:
            for i, world_point in enumerate(self.trail_points):
                alpha = int(200 * (i / CONTRAIL_LENGTH)) # Fade out older points
                # Optimized: Draw circle directly instead of creating a temp surface
                # Ensure PASTEL_CONTRAIL_COLOR is just RGB, alpha is applied here
                contrail_dot_color_with_alpha = (*PASTEL_CONTRAIL_COLOR, alpha)
                
                screen_px = world_point[0] - cam_x
                screen_py = world_point[1] - cam_y
                
                # Draw only if on screen (basic culling)
                if 0 <= screen_px <= SCREEN_WIDTH and 0 <= screen_py <= SCREEN_HEIGHT:
                    try:
                        pygame.draw.circle(surface, contrail_dot_color_with_alpha, (screen_px, screen_py), 2)
                    except pygame.error as e:
                        # This can happen if color format is wrong (e.g. alpha not supported by surface)
                        # Or if coordinates are massively out of bounds for some reason.
                        # For now, just skip drawing this point if an error occurs.
                        # print(f"Error drawing contrail circle: {e}, color: {contrail_dot_color_with_alpha}")
                        pass


    def apply_collision_effect(self):
        self.speed *= 0.5 # Lose half speed
        # Apply a small random knockback
        knockback_angle = random.uniform(0, 2 * math.pi)
        knockback_dist = 5 # Small displacement
        self.world_x += knockback_dist * math.cos(knockback_angle)
        self.world_y += knockback_dist * math.sin(knockback_angle)


# --- PlayerGlider Class ---
class PlayerGlider(GliderBase):
    def __init__(self):
        super().__init__(PASTEL_GLIDER_BODY, PASTEL_GLIDER_WING)
        # Player is always drawn at the screen center
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.previous_height = INITIAL_HEIGHT # For VSI calculation
        self.vertical_speed = 0.0 # Per-frame height change

    def reset(self, start_height=INITIAL_HEIGHT):
        self.world_x = 0.0; self.world_y = 0.0 # Start at world origin
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2) # Visual center
        self.heading = 0; self.bank_angle = 0
        self.height = start_height; self.speed = INITIAL_SPEED
        self.previous_height = start_height
        self.vertical_speed = 0.0
        self.trail_points = []; self.contrail_frame_counter = 0
        self.current_target_marker_index = 0
        self.laps_completed = 0
        self.update_sprite_rotation_and_position() # Initial sprite setup


    def update(self, keys):
        global current_wind_speed_x, current_wind_speed_y, game_state, race_course_markers, total_race_laps, time_taken_for_level, level_timer_start_ticks
        self.previous_height = self.height

        # Speed control
        if keys[pygame.K_UP]: self.speed += ACCELERATION
        elif keys[pygame.K_DOWN]: # "Pull up" - trades speed for height, or slows down
            potential_new_speed = self.speed - ACCELERATION
            if potential_new_speed >= MIN_SPEED:
                self.speed = potential_new_speed
                self.height += ACCELERATION * ZOOM_CLIMB_FACTOR # Gain some height when slowing down actively
            else:
                self.speed = MIN_SPEED # Don't go below min speed
        self.speed = max(MIN_SPEED, min(self.speed, MAX_SPEED)) # Clamp speed

        # Banking and Turning
        if keys[pygame.K_LEFT]: self.bank_angle -= BANK_RATE
        elif keys[pygame.K_RIGHT]: self.bank_angle += BANK_RATE
        else: self.bank_angle *= 0.95 # Gradually return to level flight if no input
        if abs(self.bank_angle) < 0.1: self.bank_angle = 0 # Snap to zero if very small
        self.bank_angle = max(-MAX_BANK_ANGLE, min(self.bank_angle, MAX_BANK_ANGLE)) # Clamp bank angle

        turn_rate_degrees = self.bank_angle * TURN_RATE_SCALAR * (self.speed / INITIAL_SPEED) # Turn rate depends on bank and speed
        self.heading = (self.heading + turn_rate_degrees) % 360
        heading_rad = math.radians(self.heading)

        # Update world position
        self.world_x += self.speed * math.cos(heading_rad) + current_wind_speed_x
        self.world_y += self.speed * math.sin(heading_rad) + current_wind_speed_y

        # Altitude physics
        height_change_due_to_physics = 0
        if self.speed < STALL_SPEED:
            height_change_due_to_physics = -GRAVITY_BASE_PULL - STALL_SINK_PENALTY # Increased sink in stall
        else:
            lift_from_airspeed = self.speed * LIFT_PER_SPEED_UNIT
            net_vertical_force = lift_from_airspeed - GRAVITY_BASE_PULL
            # Sink rate is at least MINIMUM_SINK_RATE if net force is negative (sinking)
            height_change_due_to_physics = max(net_vertical_force, -MINIMUM_SINK_RATE) if net_vertical_force < 0 else net_vertical_force
        
        self.height += height_change_due_to_physics
        
        # Diving converts potential energy (height) to kinetic energy (speed)
        if height_change_due_to_physics < 0: # If sinking due to physics (not thermals)
            self.speed = min(self.speed + abs(height_change_due_to_physics) * DIVE_TO_SPEED_FACTOR, MAX_SPEED)

        self.vertical_speed = self.height - self.previous_height # VSI calculation
        self.update_sprite_rotation_and_position() # Update visual sprite
        self.update_contrail()

        # Race mode: Check for passing markers
        if game_state == STATE_RACE_PLAYING and race_course_markers:
            target_marker = race_course_markers[self.current_target_marker_index]
            dist_to_marker = math.hypot(self.world_x - target_marker.world_pos.x, self.world_y - target_marker.world_pos.y)
            if dist_to_marker < target_marker.world_radius: # Player passed through marker
                self.current_target_marker_index += 1
                if self.current_target_marker_index >= len(race_course_markers): # Completed a lap
                    self.laps_completed += 1
                    self.current_target_marker_index = 0 # Reset to first marker for next lap
                    if self.laps_completed >= total_race_laps:
                        game_state = STATE_RACE_COMPLETE
                        race_end_ticks = pygame.time.get_ticks()
                        time_taken_for_level = (race_end_ticks - level_timer_start_ticks) / 1000.0 # Store race time

    def apply_lift_from_thermal(self, thermal_lift_power_at_nominal_speed):
        global game_difficulty
        if self.speed < STALL_SPEED: return # No lift if stalled

        actual_lift_power = thermal_lift_power_at_nominal_speed
        # Apply difficulty multiplier
        if game_difficulty == DIFFICULTY_EASY:
            actual_lift_power *= EASY_MODE_THERMAL_LIFT_MULTIPLIER
        elif game_difficulty == DIFFICULTY_NOOB:
            actual_lift_power *= NOOB_MODE_THERMAL_LIFT_MULTIPLIER

        # Lift is stronger if flying slower (more time in thermal for same horizontal distance)
        # Ensure speed is not too low to avoid division by zero or extreme lift
        lift_this_frame = actual_lift_power * (INITIAL_SPEED / max(self.speed, MIN_SPEED * 0.5))
        # Ensure some minimum lift even if speed is very high
        self.height += max(lift_this_frame, actual_lift_power * 0.2)

# --- AI Glider Class ---
class AIGlider(GliderBase):
    def __init__(self, start_world_x, start_world_y):
        super().__init__(PASTEL_AI_GLIDER_BODY, PASTEL_AI_GLIDER_WING, start_world_x, start_world_y)
        self.speed = random.uniform(AI_SPEED_MIN, AI_SPEED_MAX)
        self.height = AI_TARGET_RACE_ALTITUDE + random.uniform(-50, 50) # Start near target race altitude
        self.target_speed = self.speed # Desired speed

    def update(self, cam_x, cam_y, race_markers_list, total_laps_in_race):
        global game_state
        if not race_markers_list or game_state != STATE_RACE_PLAYING: # Only update AI logic during race
            self.update_sprite_rotation_and_position(cam_x, cam_y)
            self.update_contrail()
            return

        target_marker = race_markers_list[self.current_target_marker_index]
        dx = target_marker.world_pos.x - self.world_x
        dy = target_marker.world_pos.y - self.world_y
        dist_to_marker = math.hypot(dx, dy)
        
        # --- Steering ---
        target_angle_rad = math.atan2(dy, dx)
        target_angle_deg = math.degrees(target_angle_rad)
        
        # Normalize angles and find shortest turn
        current_heading_deg = self.heading % 360
        target_angle_deg = target_angle_deg % 360
        angle_diff = target_angle_deg - current_heading_deg
        if angle_diff > 180: angle_diff -= 360
        if angle_diff < -180: angle_diff += 360
        
        turn_this_frame = angle_diff * AI_TURN_RATE_SCALAR # Simple proportional steering
        self.heading = (self.heading + turn_this_frame) % 360
        
        # --- Speed Control ---
        if dist_to_marker < AI_MARKER_APPROACH_SLOWDOWN_DISTANCE:
            # Slow down when approaching marker
            self.target_speed = AI_SPEED_MIN + \
                                (AI_SPEED_MAX - AI_SPEED_MIN) * \
                                (dist_to_marker / AI_MARKER_APPROACH_SLOWDOWN_DISTANCE) * \
                                AI_MARKER_APPROACH_MIN_SPEED_FACTOR
            self.target_speed = max(AI_SPEED_MIN * 0.8, self.target_speed) # Don't slow down too much
        else:
            self.target_speed = random.uniform(AI_SPEED_MIN, AI_SPEED_MAX) # Maintain a cruising speed

        if self.speed < self.target_speed: self.speed += ACCELERATION * 0.5 # Slower acceleration for AI
        elif self.speed > self.target_speed: self.speed -= ACCELERATION * 0.5
        self.speed = max(AI_SPEED_MIN * 0.7, min(self.speed, AI_SPEED_MAX * 1.1)) # Clamp AI speed

        # --- Altitude Control ---
        alt_diff = AI_TARGET_RACE_ALTITUDE - self.height
        self.height += alt_diff * AI_ALTITUDE_CORRECTION_RATE # Gradually correct altitude
        if self.height < 0: self.height = 0 # Don't fly into ground

        # --- Movement ---
        heading_rad = math.radians(self.heading)
        self.world_x += self.speed * math.cos(heading_rad) # No wind for AI to simplify
        self.world_y += self.speed * math.sin(heading_rad)

        # --- Marker Progression ---
        if dist_to_marker < target_marker.world_radius: # AI passed marker
            self.current_target_marker_index += 1
            if self.current_target_marker_index >= len(race_markers_list):
                self.laps_completed += 1
                self.current_target_marker_index = 0
                # AI completing laps doesn't end the game, player does.
                # if self.laps_completed >= total_laps_in_race:
                #     pass # AI finished its laps

        self.update_sprite_rotation_and_position(cam_x, cam_y)
        self.update_contrail()


# --- Thermal Class ---
class Thermal(pygame.sprite.Sprite):
    def __init__(self, world_center_pos):
        super().__init__()
        global game_difficulty
        self.world_pos = pygame.math.Vector2(world_center_pos) # World coordinates of thermal center

        # Determine thermal properties based on difficulty
        min_r, max_r, min_l, max_l = NORMAL_MIN_THERMAL_RADIUS, NORMAL_MAX_THERMAL_RADIUS, NORMAL_MIN_THERMAL_LIFESPAN, NORMAL_MAX_THERMAL_LIFESPAN
        if game_difficulty == DIFFICULTY_NOOB:
            min_r, max_r, min_l, max_l = NOOB_MIN_THERMAL_RADIUS, NOOB_MAX_THERMAL_RADIUS, NOOB_MIN_THERMAL_LIFESPAN, NOOB_MAX_THERMAL_LIFESPAN
        
        self.radius = random.randint(min_r, max_r)
        # Normalized radius (0-1) to scale lifespan and power (bigger thermals are often stronger/longer)
        if max_r == min_r: normalized_radius = 0.5 # Avoid division by zero if min=max
        else: normalized_radius = (self.radius - min_r) / (max_r - min_r)
        
        self.lifespan = min_l + (max_l - min_l) * normalized_radius # Frames
        self.initial_lifespan = self.lifespan # For fading effect
        # Stronger thermals (larger radius) have more lift, up to MAX_THERMAL_LIFT_POWER
        self.lift_power = MAX_THERMAL_LIFT_POWER - (MAX_THERMAL_LIFT_POWER - MIN_THERMAL_LIFT_POWER) * (1 - normalized_radius) # Inverted: larger normalized_radius = more power
        
        # Image for drawing (transparent circle)
        self.image = pygame.Surface([self.radius * 2, self.radius * 2], pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.creation_time = pygame.time.get_ticks() # For pulsing animation timing
        self.update_visuals() # Initial draw of thermal appearance

    def update_visuals(self):
        # Pulsing and fading effect for thermal
        pulse_alpha_factor = (math.sin(pygame.time.get_ticks()*0.005 + self.creation_time*0.01)*0.3 + 0.7) # Sin wave for pulsing (0.7 to 1.0 range)
        age_factor = max(0, self.lifespan / self.initial_lifespan if self.initial_lifespan > 0 else 0) # Fades out as it ages (1.0 to 0)
        
        alpha = int(THERMAL_BASE_ALPHA * pulse_alpha_factor * age_factor)
        accent_alpha = int(THERMAL_ACCENT_ALPHA * pulse_alpha_factor * age_factor)
        
        # Slight size pulse
        visual_radius_factor = math.sin(pygame.time.get_ticks()*0.002 + self.creation_time*0.005)*0.1 + 0.95 # Sin wave for radius (0.85 to 1.05 range)
        current_visual_radius = int(self.radius * visual_radius_factor)
        
        self.image.fill((0,0,0,0)) # Clear previous frame on the thermal's surface
        pygame.draw.circle(self.image, (*PASTEL_THERMAL_PRIMARY, alpha), (self.radius, self.radius), current_visual_radius)
        pygame.draw.circle(self.image, (*PASTEL_THERMAL_ACCENT, accent_alpha), (self.radius, self.radius), int(current_visual_radius*0.7), 2) # Accent ring

    def update(self, cam_x, cam_y):
        self.lifespan -= 1
        if self.lifespan <= 0:
            self.kill() # Remove from all sprite groups
        else:
            self.update_visuals() # Redraw thermal appearance if still alive

        # Update screen position based on camera
        self.rect.centerx = self.world_pos.x - cam_x
        self.rect.centery = self.world_pos.y - cam_y

# --- RaceMarker Class ---
class RaceMarker(pygame.sprite.Sprite):
    def __init__(self, world_x, world_y, number):
        super().__init__()
        self.world_pos = pygame.math.Vector2(world_x, world_y)
        self.number = number # Marker number in the sequence
        self.world_radius = RACE_MARKER_RADIUS_WORLD  # Collision radius in world units
        self.visual_radius = RACE_MARKER_VISUAL_RADIUS_WORLD # Visual size on screen
        
        self.image = pygame.Surface((self.visual_radius * 2, self.visual_radius * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self._draw_marker_image(False) # Initial draw (not active)

    def _draw_marker_image(self, is_active):
        color_to_use = PASTEL_ACTIVE_MARKER_COLOR if is_active else PASTEL_MARKER_COLOR
        if is_active and self.number == 1: # Highlight first marker of the lap (start/finish)
            color_to_use = PASTEL_GOLD

        self.image.fill((0,0,0,0)) # Clear surface
        pygame.draw.circle(self.image, color_to_use, (self.visual_radius, self.visual_radius), self.visual_radius)
        pygame.draw.circle(self.image, PASTEL_WHITE, (self.visual_radius, self.visual_radius), int(self.visual_radius * 0.7)) # Inner circle
        
        # Draw marker number
        font_obj = get_cached_font(None, int(self.visual_radius * 1.1)) # Use cached font
        text_surf = font_obj.render(str(self.number), True, PASTEL_BLACK)
        text_rect = text_surf.get_rect(center=(self.visual_radius, self.visual_radius))
        self.image.blit(text_surf, text_rect)

    def update(self, cam_x, cam_y, is_active):
        # Update screen position
        self.rect.centerx = self.world_pos.x - cam_x
        self.rect.centery = self.world_pos.y - cam_y
        self._draw_marker_image(is_active) # Redraw if active status might have changed


# --- Minimap Class ---
class Minimap:
    def __init__(self, width, height, margin):
        self.width = width
        self.height = height
        self.margin = margin
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA) # Minimap's own drawing surface
        self.rect = self.surface.get_rect(topright=(SCREEN_WIDTH - self.margin, self.margin + HUD_HEIGHT))
        self.world_bounds_view_radius = 3000 # How far (in world units) the minimap "sees" from the player

    def world_to_minimap(self, world_x, world_y, player_world_x, player_world_y):
        # Calculate scale to fit world_bounds_view_radius into minimap width/height
        scale = self.width / (2 * self.world_bounds_view_radius) # Assuming square view for simplicity
        
        # Relative position of world_point to player
        rel_x = world_x - player_world_x
        rel_y = world_y - player_world_y
        
        # Scale and offset to minimap coordinates (player is at minimap center)
        mini_x = self.width / 2 + rel_x * scale
        mini_y = self.height / 2 + rel_y * scale
        return int(mini_x), int(mini_y)

    def draw(self, surface, player_glider, ai_gliders_list, course_markers):
        self.surface.fill(PASTEL_MINIMAP_BACKGROUND) # Semi-transparent background
        
        # Player is always at the center of the minimap
        player_mini_x, player_mini_y = self.width // 2, self.height // 2
        pygame.draw.circle(self.surface, PASTEL_GOLD, (player_mini_x, player_mini_y), 5) # Player dot
        
        # Draw AI gliders
        for ai in ai_gliders_list:
            ai_mini_x, ai_mini_y = self.world_to_minimap(ai.world_x, ai.world_y, player_glider.world_x, player_glider.world_y)
            # Basic culling for minimap objects
            if 0 <= ai_mini_x <= self.width and 0 <= ai_mini_y <= self.height:
                 pygame.draw.circle(self.surface, PASTEL_AI_GLIDER_BODY, (ai_mini_x, ai_mini_y), 4) # AI dots

        # Draw race markers
        for i, marker in enumerate(course_markers):
            mini_x, mini_y = self.world_to_minimap(marker.world_pos.x, marker.world_pos.y, player_glider.world_x, player_glider.world_y)
            
            if 0 <= mini_x <= self.width and 0 <= mini_y <= self.height: # Culling
                color = PASTEL_ACTIVE_MARKER_COLOR if i == player_glider.current_target_marker_index else PASTEL_MARKER_COLOR
                if i == player_glider.current_target_marker_index and marker.number == 1: # Start/finish line
                    color = PASTEL_GOLD

                pygame.draw.circle(self.surface, color, (mini_x, mini_y), RACE_MARKER_VISUAL_RADIUS_MAP)
                font_obj = get_cached_font(None, 16) # Use cached font
                text_surf = font_obj.render(str(marker.number), True, PASTEL_BLACK)
                text_rect = text_surf.get_rect(center=(mini_x, mini_y))
                self.surface.blit(text_surf, text_rect)

        pygame.draw.rect(self.surface, PASTEL_MINIMAP_BORDER, self.surface.get_rect(), 2) # Border for minimap
        surface.blit(self.surface, self.rect) # Draw the minimap onto the main screen


# --- ForegroundCloud Class ---
class ForegroundCloud(pygame.sprite.Sprite):
    def __init__(self, initial_distribution=False, index=0, total_clouds=NUM_FOREGROUND_CLOUDS): # Added default for total_clouds
        super().__init__()
        global current_wind_speed_x, current_wind_speed_y # Access global wind
        
        self.width = random.randint(100, 250); self.height = random.randint(40, 80)
        self.image = pygame.Surface([self.width, self.height], pygame.SRCALPHA) # Transparent surface
        
        # Create a puffy cloud shape
        num_puffs = random.randint(4, 7)
        for _ in range(num_puffs):
            puff_w=random.randint(int(self.width*0.4),int(self.width*0.8))
            puff_h=random.randint(int(self.height*0.5),int(self.height*0.9))
            puff_x=random.randint(0,self.width-puff_w)
            puff_y=random.randint(0,self.height-puff_h)
            alpha = random.randint(CLOUD_MIN_ALPHA, CLOUD_MAX_ALPHA)
            pygame.draw.ellipse(self.image, (*PASTEL_CLOUD, alpha), (puff_x, puff_y, puff_w, puff_h))
            
        self.speed_factor = random.uniform(MIN_CLOUD_SPEED_FACTOR, MAX_CLOUD_SPEED_FACTOR)
        # Initial speed based on current wind (will be updated if wind changes)
        self.dx = current_wind_speed_x * self.speed_factor
        self.dy = current_wind_speed_y * self.speed_factor

        self.x_float = 0.0 # Use float for precise position tracking
        self.y_float = 0.0

        if initial_distribution: # Spread clouds across screen at start
            # Distribute horizontally, random vertically
            self.x_float = (index / total_clouds) * SCREEN_WIDTH - self.width / 2 + \
                           random.uniform(-SCREEN_WIDTH / (total_clouds * 2), SCREEN_WIDTH / (total_clouds * 2))
            self.y_float = float(random.randint(-self.height // 2, SCREEN_HEIGHT - self.height // 2))
        else: # Spawn new clouds off-screen based on wind direction
            if self.dx == 0 and self.dy == 0: # No wind, spawn randomly at edges
                if random.choice([True, False]): # Horizontal edge
                    self.x_float = float(random.choice([-self.width - 20, SCREEN_WIDTH + 20]))
                    self.y_float = float(random.randint(-self.height, SCREEN_HEIGHT))
                else: # Vertical edge
                    self.y_float = float(random.choice([-self.height - 20, SCREEN_HEIGHT + 20]))
                    self.x_float = float(random.randint(-self.width, SCREEN_WIDTH))
            else: # Wind is blowing
                if abs(self.dx) > abs(self.dy): # Primarily horizontal wind
                    self.x_float = float(SCREEN_WIDTH + random.randint(0,100) + self.width/2 if self.dx < 0 else -random.randint(0,100) - self.width/2) # Spawn upwind
                    self.y_float = float(random.randint(-self.height//2, SCREEN_HEIGHT - self.height//2))
                else: # Primarily vertical wind
                    self.y_float = float(SCREEN_HEIGHT + random.randint(0,50) + self.height/2 if self.dy < 0 else -random.randint(0,50) - self.height/2) # Spawn upwind
                    self.x_float = float(random.randint(-self.width//2, SCREEN_WIDTH - self.width//2))
        
        self.rect = self.image.get_rect(topleft=(round(self.x_float), round(self.y_float)))


    def update(self):
        # Update speed in case wind changes
        self.dx = current_wind_speed_x * self.speed_factor
        self.dy = current_wind_speed_y * self.speed_factor
        
        self.x_float += self.dx; self.y_float += self.dy
        self.rect.topleft = (round(self.x_float), round(self.y_float))

        # Despawn if cloud moves too far off-screen
        off_screen_margin_x = self.width * 1.5 + abs(self.dx * 20) # Generous margin
        off_screen_margin_y = self.height * 1.5 + abs(self.dy * 20)

        despawn = False
        if self.dx < 0 and self.rect.right < -off_screen_margin_x: despawn = True
        elif self.dx > 0 and self.rect.left > SCREEN_WIDTH + off_screen_margin_x: despawn = True
        
        if not despawn:
            if self.dy < 0 and self.rect.bottom < -off_screen_margin_y: despawn = True
            elif self.dy > 0 and self.rect.top > SCREEN_HEIGHT + off_screen_margin_y: despawn = True
        
        if self.dx == 0 and self.dy == 0: # If no wind, check if drifted out of bounds
            if not (-off_screen_margin_x < self.rect.centerx < SCREEN_WIDTH + off_screen_margin_x and \
                    -off_screen_margin_y < self.rect.centery < SCREEN_HEIGHT + off_screen_margin_y):
                despawn = True
        
        if despawn: self.kill()

# --- Enhanced Endless Map Data & Functions ---
map_tile_random_generator = random.Random() # Dedicated generator for map tiles
ELEVATION_CONTINENT_SCALE = 60.0 # Larger scale features
ELEVATION_MOUNTAIN_SCALE = 15.0  # Medium scale features
ELEVATION_HILL_SCALE = 5.0       # Smaller scale features
MOISTURE_PRIMARY_SCALE = 40.0
MOISTURE_SECONDARY_SCALE = 10.0
# Prime pairs for seeding, helps ensure different noise patterns for different features
P_CONT, P_MNT, P_HILL = (73856093, 19349663), (83492791, 52084219), (39119077, 66826529)
P_MOIST_P, P_MOIST_S = (23109781, 92953093), (47834583, 11634271)

NUM_MAJOR_RIVERS = 3
MAJOR_RIVERS_PARAMS = [] # Stores parameters for each major river system
_river_param_random = random.Random() # Separate generator for river parameters

def regenerate_river_parameters():
    global MAJOR_RIVERS_PARAMS, _river_param_random
    MAJOR_RIVERS_PARAMS = []
    for _ in range(NUM_MAJOR_RIVERS):
        # River parameters are in tile units, relative to the "origin" of the current map offset
        # This means river patterns will shift with current_map_offset_x/y
        start_tile_x = _river_param_random.uniform(-RACE_COURSE_AREA_HALFWIDTH / TILE_SIZE / 3, RACE_COURSE_AREA_HALFWIDTH / TILE_SIZE / 3)
        start_tile_y = _river_param_random.uniform(-RACE_COURSE_AREA_HALFWIDTH / TILE_SIZE / 3, RACE_COURSE_AREA_HALFWIDTH / TILE_SIZE / 3)

        MAJOR_RIVERS_PARAMS.append({
            "amplitude": _river_param_random.uniform(10, 30), # How much it "wiggles" in tiles
            "wavelength": _river_param_random.uniform(200, 450), # Length of one wiggle in tiles
            "phase_offset": _river_param_random.uniform(0, 2 * math.pi), # Shifts the wiggle
            "base_x_offset": start_tile_x, # General X position offset in tiles
            "base_y_offset": start_tile_y, # General Y position offset in tiles
            "orientation": _river_param_random.choice(['horizontal', 'vertical']),
            "width": _river_param_random.randint(1, 2) # River width in tiles
        })

# Generates a seeded random value for a given unique tile coordinate.
# unique_tile_x/y are absolute tile indices in the infinite world.
def get_seeded_random_value_direct(unique_tile_x, unique_tile_y, scale, p_pair):
    global map_tile_random_generator
    # Scale down the unique tile coordinates to get a coarser grid for this noise layer
    scaled_x = math.floor(unique_tile_x / scale)
    scaled_y = math.floor(unique_tile_y / scale)
    # Seed the generator based on these scaled coordinates and prime pair
    map_tile_random_generator.seed((scaled_x * p_pair[0]) ^ (scaled_y * p_pair[1]))
    return map_tile_random_generator.random() # Return a value between 0.0 and 1.0

def get_land_type_at_world_pos(world_x, world_y):
    global current_map_offset_x, current_map_offset_y, tile_type_cache

    # Calculate the unique tile index by incorporating the current_map_offset.
    # This unique index is used for caching and for seeding the noise functions.
    unique_tile_x = math.floor((world_x + current_map_offset_x) / TILE_SIZE)
    unique_tile_y = math.floor((world_y + current_map_offset_y) / TILE_SIZE)
    
    cache_key = (unique_tile_x, unique_tile_y)
    if cache_key in tile_type_cache:
        return tile_type_cache[cache_key]

    # If not in cache, calculate land type using noise functions
    # Pass the unique_tile_x/y to the noise value generator
    e_continent = get_seeded_random_value_direct(unique_tile_x, unique_tile_y, ELEVATION_CONTINENT_SCALE, P_CONT)
    e_mountain  = get_seeded_random_value_direct(unique_tile_x, unique_tile_y, ELEVATION_MOUNTAIN_SCALE, P_MNT)
    e_hill      = get_seeded_random_value_direct(unique_tile_x, unique_tile_y, ELEVATION_HILL_SCALE, P_HILL)
    # Combine noise layers for elevation, with some weighting and power for shaping
    elevation = math.pow(0.50 * e_continent + 0.35 * e_mountain + 0.15 * e_hill, 1.8)
    elevation = min(max(elevation, 0.0), 1.0) # Clamp to 0-1 range

    m_primary   = get_seeded_random_value_direct(unique_tile_x, unique_tile_y, MOISTURE_PRIMARY_SCALE, P_MOIST_P)
    m_secondary = get_seeded_random_value_direct(unique_tile_x, unique_tile_y, MOISTURE_SECONDARY_SCALE, P_MOIST_S)
    moisture = math.pow(0.7 * m_primary + 0.3 * m_secondary, 1.2)
    moisture = min(max(moisture, 0.0), 1.0) # Clamp to 0-1 range
    
    # Determine land type based on elevation and moisture thresholds
    final_type = LAND_TYPE_PLAINS # Default
    deep_water_thresh, shallow_water_thresh, beach_thresh = 0.18, 0.22, 0.24
    mountain_base_thresh, mountain_peak_thresh = 0.60, 0.75
    desert_thresh, grassland_thresh, temperate_forest_thresh = 0.20, 0.40, 0.65

    if elevation < deep_water_thresh: final_type = LAND_TYPE_WATER_DEEP
    elif elevation < shallow_water_thresh: final_type = LAND_TYPE_WATER_SHALLOW
    elif elevation < beach_thresh: # Coastal areas
        final_type = LAND_TYPE_SAND_DESERT if moisture < desert_thresh * 1.2 else LAND_TYPE_SAND_BEACH
    elif elevation > mountain_peak_thresh: final_type = LAND_TYPE_MOUNTAIN_PEAK
    elif elevation > mountain_base_thresh: final_type = LAND_TYPE_MOUNTAIN_BASE
    else: # General land types for mid-elevations
        if moisture < desert_thresh: final_type = LAND_TYPE_SAND_DESERT
        elif moisture < grassland_thresh: final_type = LAND_TYPE_GRASSLAND
        elif moisture < temperate_forest_thresh: final_type = LAND_TYPE_PLAINS
        else: # Wetter areas
            final_type = LAND_TYPE_FOREST_DENSE if moisture > 0.8 and elevation < mountain_base_thresh * 0.9 else LAND_TYPE_FOREST_TEMPERATE

    # River generation: Check if current unique_tile_x/y falls within a river path
    # Rivers are less likely on peaks, deep water, or very dry deserts.
    can_have_river = final_type not in (LAND_TYPE_MOUNTAIN_PEAK, LAND_TYPE_WATER_DEEP) and \
                     not (final_type == LAND_TYPE_SAND_DESERT and moisture < desert_thresh * 0.75)

    if can_have_river:
        for params in MAJOR_RIVERS_PARAMS:
            # River path is calculated using unique_tile_x/y and pre-generated river parameters
            if params["orientation"] == 'horizontal':
                # base_y_offset is relative to the "origin" of the current map view (influenced by current_map_offset_y)
                # The sine wave is based on the absolute unique_tile_x
                river_center_y_tile = params["amplitude"] * math.sin(
                    (unique_tile_x / params["wavelength"]) * 2 * math.pi + params["phase_offset"]
                ) + params["base_y_offset"]
                if abs(unique_tile_y - river_center_y_tile) < params["width"]:
                    final_type = LAND_TYPE_RIVER; break
            else: # Vertical river
                river_center_x_tile = params["amplitude"] * math.sin(
                    (unique_tile_y / params["wavelength"]) * 2 * math.pi + params["phase_offset"]
                ) + params["base_x_offset"]
                if abs(unique_tile_x - river_center_x_tile) < params["width"]:
                    final_type = LAND_TYPE_RIVER; break
    
    tile_type_cache[cache_key] = final_type # Store in cache
    return final_type


def draw_endless_map(surface, cam_x, cam_y):
    # Determine the range of world tiles visible on screen
    start_world_tile_x_coord = math.floor(cam_x / TILE_SIZE) * TILE_SIZE
    start_world_tile_y_coord = math.floor(cam_y / TILE_SIZE) * TILE_SIZE
    num_tiles_x = SCREEN_WIDTH // TILE_SIZE + 2 # Add buffer for smooth scrolling
    num_tiles_y = SCREEN_HEIGHT // TILE_SIZE + 2

    for i in range(num_tiles_y): # Iterate over rows of tiles
        for j in range(num_tiles_x): # Iterate over columns of tiles
            # Calculate world coordinates of the current tile's top-left corner
            current_tile_world_x = start_world_tile_x_coord + j * TILE_SIZE
            current_tile_world_y = start_world_tile_y_coord + i * TILE_SIZE
            
            # Calculate screen coordinates for drawing this tile
            tile_screen_x = current_tile_world_x - cam_x
            tile_screen_y = current_tile_world_y - cam_y

            # Get the land type for this world position (uses caching)
            tile_type = get_land_type_at_world_pos(current_tile_world_x, current_tile_world_y)
            color = LAND_TYPE_COLORS.get(tile_type, PASTEL_BLACK) # Default to black if type unknown
            
            pygame.draw.rect(surface, color, (tile_screen_x, tile_screen_y, TILE_SIZE, TILE_SIZE))
            if MAP_TILE_OUTLINE_WIDTH > 0:
                pygame.draw.rect(surface, MAP_TILE_OUTLINE_COLOR, (tile_screen_x, tile_screen_y, TILE_SIZE, TILE_SIZE), MAP_TILE_OUTLINE_WIDTH)

# --- Text Rendering Helper with Font Caching ---
font_cache = {} # Global cache for font objects: key=(font_name, size), value=FontObject
def get_cached_font(font_name, size):
    key = (font_name, size)
    if key not in font_cache:
        font_cache[key] = pygame.font.Font(font_name, size) # Create and cache if not found
    return font_cache[key]

def draw_text(surface, text, size, x, y, color=PASTEL_WHITE, font_name=None, center=False, antialias=True, shadow=False, shadow_color=PASTEL_DARK_GRAY, shadow_offset=(1,1)):
    font = get_cached_font(font_name, size) # Use cached font
    text_surface = font.render(text, antialias, color)
    text_rect = text_surface.get_rect()
    if center: text_rect.center = (x,y)
    else: text_rect.topleft = (x,y)
    
    if shadow: # Draw shadow text first if enabled
        shadow_surface = font.render(text, antialias, shadow_color)
        surface.blit(shadow_surface, (text_rect.x + shadow_offset[0], text_rect.y + shadow_offset[1]))
    surface.blit(text_surface, text_rect) # Draw main text

# --- Pygame Setup ---
pygame.init()
pygame.mixer.init() # Initialize mixer for potential sound effects later
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pastel Glider - Floating Dreams")
clock = pygame.time.Clock()

# --- Game Objects & Variables ---
player = PlayerGlider()
ai_gliders = pygame.sprite.Group() # For AI glider sprites

# Sprite groups for managing different types of game objects
all_world_sprites = pygame.sprite.Group() # Contains sprites positioned in world space (thermals, AI, markers)
thermals_group = pygame.sprite.Group()    # Specifically for thermals (for collision and updates)
race_markers_group = pygame.sprite.Group() # For race markers (could be part of all_world_sprites too)
foreground_clouds_group = pygame.sprite.Group() # For screen-space clouds

# Game state and progression variables
game_state = STATE_START_SCREEN
current_level = 1
level_timer_start_ticks = 0
time_taken_for_level = 0.0 # Seconds
current_thermal_spawn_rate = BASE_THERMAL_SPAWN_RATE # Frames per spawn attempt
thermal_spawn_timer = 0
final_score = 0 # Could be height in Free Fly, or time in Race

# Menu selection variables
selected_difficulty_option = DIFFICULTY_NORMAL # Default difficulty
selected_mode_option = MODE_FREE_FLY         # Default game mode
selected_laps_option = 1                     # Index for lap_options (default to 3 laps)
lap_options = [1, 3, 5]                      # Available lap counts for Race mode

minimap = Minimap(MINIMAP_WIDTH, MINIMAP_HEIGHT, MINIMAP_MARGIN)


def generate_race_course(num_markers=8):
    global race_course_markers, race_markers_group, all_world_sprites
    race_course_markers.clear() # Clear the list of marker objects
    
    # Efficiently remove old markers from sprite groups
    for sprite in list(all_world_sprites): # Iterate over a copy if modifying the group
        if isinstance(sprite, RaceMarker):
            sprite.kill() # Removes from all groups it's in (all_world_sprites, race_markers_group)
    # race_markers_group.empty() # This would also work if it only contains RaceMarkers

    for i in range(num_markers):
        # Place markers within a defined area for the race
        world_x = random.uniform(-RACE_COURSE_AREA_HALFWIDTH, RACE_COURSE_AREA_HALFWIDTH)
        world_y = random.uniform(-RACE_COURSE_AREA_HALFWIDTH, RACE_COURSE_AREA_HALFWIDTH)
        marker = RaceMarker(world_x, world_y, i + 1) # Create new marker
        race_course_markers.append(marker) # Add to list for ordered access
        all_world_sprites.add(marker)      # Add to group for drawing and updates
        # race_markers_group.add(marker)   # Could add here too if separate handling needed


def generate_new_wind():
    global current_wind_speed_x, current_wind_speed_y
    wind_angle_rad = random.uniform(0, 2 * math.pi)
    wind_strength = random.uniform(0.05, MAX_WIND_STRENGTH) # Ensure some variability
    current_wind_speed_x = wind_strength * math.cos(wind_angle_rad)
    current_wind_speed_y = wind_strength * math.sin(wind_angle_rad)

def start_new_level(level_param): # Parameter can be level number or lap count
    global current_level,level_timer_start_ticks,current_thermal_spawn_rate,thermal_spawn_timer, game_state
    global current_map_offset_x, current_map_offset_y, _river_param_random, total_race_laps, ai_gliders
    global tile_type_cache

    level_timer_start_ticks = pygame.time.get_ticks() # Reset timer for the new level/race

    # Generate a new map offset to "move" to a new area of the infinite world
    current_map_offset_x = random.randint(-200000, 200000) # World units
    current_map_offset_y = random.randint(-200000, 200000) # World units
    tile_type_cache.clear() # CRUCIAL: Map has shifted, invalidate tile cache

    _river_param_random.seed(current_level + pygame.time.get_ticks()) # Re-seed for new river patterns
    regenerate_river_parameters()
    generate_new_wind() # New wind conditions for the level

    # Clear out old game objects from previous level/race
    thermals_group.empty()
    all_world_sprites.empty() # Clears AI, thermals, markers from this group
    # race_markers_group.empty() # Implicitly cleared if markers were only in all_world_sprites
    race_course_markers.clear()
    ai_gliders.empty() # Specifically clear AI gliders group

    # Reset foreground clouds
    foreground_clouds_group.empty()
    for i in range(NUM_FOREGROUND_CLOUDS):
        foreground_clouds_group.add(ForegroundCloud(initial_distribution=True,index=i))

    player.reset(start_height=INITIAL_HEIGHT) # Reset player state

    if current_game_mode == MODE_FREE_FLY:
        current_level = level_param # level_param is the new level number
        # Adjust thermal spawn rate based on level and difficulty
        current_thermal_spawn_rate = BASE_THERMAL_SPAWN_RATE + (THERMAL_SPAWN_RATE_INCREASE_PER_LEVEL * (current_level -1))
        if game_difficulty == DIFFICULTY_NOOB:
            current_thermal_spawn_rate = max(20, current_thermal_spawn_rate // 2)
        elif game_difficulty == DIFFICULTY_EASY:
            current_thermal_spawn_rate = max(30, int(current_thermal_spawn_rate * 0.75))
        thermal_spawn_timer=0 # Reset thermal spawn counter
        game_state = STATE_PLAYING_FREE_FLY

    elif current_game_mode == MODE_RACE:
        total_race_laps = level_param # level_param is the number of laps
        generate_race_course() # Create new race markers
        
        # Spawn AI opponents for the race
        for i in range(NUM_AI_OPPONENTS):
            # Stagger AI start positions slightly behind/around player
            # Angle relative to player's initial heading (0 degrees = right)
            angle_offset_from_player_heading = math.pi + (i - NUM_AI_OPPONENTS / 2.0) * (math.pi / 6) # Spread behind
            dist_offset = 70 + i * 30 # Stagger distance
            
            ai_start_x = player.world_x + dist_offset * math.cos(math.radians(player.heading) + angle_offset_from_player_heading)
            ai_start_y = player.world_y + dist_offset * math.sin(math.radians(player.heading) + angle_offset_from_player_heading)
            new_ai = AIGlider(ai_start_x, ai_start_y)
            ai_gliders.add(new_ai)
            all_world_sprites.add(new_ai) # Add AI to the main drawing group

        # Thermals in race mode (usually less frequent or powerful than free fly, adjust as needed)
        current_thermal_spawn_rate = BASE_THERMAL_SPAWN_RATE * 1.5 # Less frequent for races
        if game_difficulty == DIFFICULTY_NOOB: current_thermal_spawn_rate = max(30, int(current_thermal_spawn_rate * 0.7))
        thermal_spawn_timer=0
        game_state = STATE_RACE_PLAYING


def reset_to_main_menu():
    global game_state,current_level,final_score, current_wind_speed_x, current_wind_speed_y
    global selected_difficulty_option, selected_mode_option, selected_laps_option, ai_gliders
    global tile_type_cache

    # Clear all dynamic game objects
    player.reset()
    thermals_group.empty()
    all_world_sprites.empty()
    race_markers_group.empty() # Ensure this is cleared if used separately
    race_course_markers.clear()
    ai_gliders.empty()
    foreground_clouds_group.empty()
    tile_type_cache.clear() # Clear map tile cache

    # Reset wind for menu screen (gentle drift)
    current_wind_speed_x = -0.2 
    current_wind_speed_y = 0.05
    for i in range(NUM_FOREGROUND_CLOUDS): # Re-populate clouds for menu
        foreground_clouds_group.add(ForegroundCloud(initial_distribution=True,index=i))
    
    # Reset game progress and menu selections
    current_level=1
    final_score=0
    selected_difficulty_option = DIFFICULTY_NORMAL # Default to Normal
    selected_mode_option = MODE_FREE_FLY         # Default to Free Fly
    selected_laps_option = 1                     # Default to 3 laps (index 1 of lap_options)
    game_state = STATE_START_SCREEN

# --- Screen Drawing Functions (Menus, HUD) ---
def draw_start_screen_content(surface):
    surface.fill(PASTEL_DARK_GRAY) # Menu background
    draw_text(surface, "Pastel Glider", 72, SCREEN_WIDTH//2, SCREEN_HEIGHT//4 - 20, PASTEL_PLAINS, center=True, shadow=True, shadow_color=PASTEL_BLACK)
    draw_text(surface, "Press ENTER to Begin", 30, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60, PASTEL_LIGHT_GRAY, center=True, shadow=True, shadow_color=PASTEL_BLACK)
    draw_text(surface, "UP/DOWN: Speed | L/R: Bank", 20, SCREEN_WIDTH//2, SCREEN_HEIGHT*3//4, PASTEL_WHITE, center=True)
    draw_text(surface, "Explore the skies, use thermals or race the course!", 20, SCREEN_WIDTH//2, SCREEN_HEIGHT*3//4 + 30, PASTEL_WHITE, center=True)

def draw_difficulty_select_screen(surface, selected_option_idx): # selected_option_idx is 0, 1, or 2
    surface.fill(PASTEL_DARK_GRAY)
    draw_text(surface, "Select Difficulty", 56, SCREEN_WIDTH//2, SCREEN_HEIGHT//5, PASTEL_GOLD, center=True, shadow=True, shadow_color=PASTEL_BLACK)
    option_spacing = 100; start_y = SCREEN_HEIGHT//2 - option_spacing
    
    # Map difficulty constants to their display names and descriptions
    difficulties_display = [
        ("N00b", "(Largest, Longest, Strongest Thermals!)", DIFFICULTY_NOOB),
        ("Easy", "(Stronger Thermals)", DIFFICULTY_EASY),
        ("Normal", "(Standard Challenge)", DIFFICULTY_NORMAL)
    ]
    
    for i, (name, desc, diff_const) in enumerate(difficulties_display):
        color = PASTEL_WHITE if selected_option_idx == diff_const else PASTEL_GRAY
        draw_text(surface, name, 48, SCREEN_WIDTH//2, start_y + i * option_spacing, color, center=True, shadow=True, shadow_color=PASTEL_BLACK)
        draw_text(surface, desc, 20, SCREEN_WIDTH//2, start_y + i * option_spacing + 30, color, center=True)
        
    draw_text(surface, "Use UP/DOWN keys, ENTER to confirm", 22, SCREEN_WIDTH//2, SCREEN_HEIGHT*0.85, PASTEL_LIGHT_GRAY, center=True)

def draw_mode_select_screen(surface, selected_option_idx): # selected_option_idx is 0 or 1
    surface.fill(PASTEL_DARK_GRAY)
    draw_text(surface, "Select Mode", 56, SCREEN_WIDTH//2, SCREEN_HEIGHT//4, PASTEL_GOLD, center=True, shadow=True, shadow_color=PASTEL_BLACK)
    
    modes_display = [
        ("Free Fly", "(Explore & Reach Altitude Goals)", MODE_FREE_FLY),
        ("Race", "(Fly Through Markers Against AI)", MODE_RACE)
    ]
    
    for i, (name, desc, mode_const) in enumerate(modes_display):
        color = PASTEL_WHITE if selected_option_idx == mode_const else PASTEL_GRAY
        y_pos = SCREEN_HEIGHT//2 - 30 + i * 100 # Spacing for two options
        draw_text(surface, name, 48, SCREEN_WIDTH//2, y_pos, color, center=True, shadow=True, shadow_color=PASTEL_BLACK)
        draw_text(surface, desc, 20, SCREEN_WIDTH//2, y_pos + 30, color, center=True)
        
    draw_text(surface, "Use UP/DOWN keys, ENTER to confirm", 22, SCREEN_WIDTH//2, SCREEN_HEIGHT*3//4 + 50, PASTEL_LIGHT_GRAY, center=True)

def draw_laps_select_screen(surface, selected_lap_idx, lap_choices_list): # selected_lap_idx is index in lap_choices_list
    surface.fill(PASTEL_DARK_GRAY)
    draw_text(surface, "Select Laps", 56, SCREEN_WIDTH//2, SCREEN_HEIGHT//4, PASTEL_GOLD, center=True, shadow=True, shadow_color=PASTEL_BLACK)
    y_offset = SCREEN_HEIGHT//2 - (len(lap_choices_list) -1) * 40 # Center options vertically
    for i, laps in enumerate(lap_choices_list):
        color = PASTEL_WHITE if i == selected_lap_idx else PASTEL_GRAY
        draw_text(surface, f"{laps} Lap{'s' if laps > 1 else ''}", 48, SCREEN_WIDTH//2, y_offset + i * 80, color, center=True, shadow=True, shadow_color=PASTEL_BLACK)
    draw_text(surface, "Use UP/DOWN keys, ENTER to start race", 22, SCREEN_WIDTH//2, SCREEN_HEIGHT*3//4 + 50, PASTEL_LIGHT_GRAY, center=True)


def draw_target_reached_options_screen(surface, level, time_taken_seconds_val):
    surface.fill(PASTEL_DARK_GRAY)
    draw_text(surface, f"Level {level} Goal Reached!", 60, SCREEN_WIDTH//2, SCREEN_HEIGHT//3 - 20, PASTEL_GOLD, center=True, shadow=True, shadow_color=PASTEL_BLACK)
    draw_text(surface, f"Time: {time_taken_seconds_val:.1f}s", 36, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40, PASTEL_WHITE, center=True)
    draw_text(surface, "Press M to Move On to Next Level", 30, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 30, PASTEL_LIGHT_GRAY, center=True)
    draw_text(surface, "Press C to Continue Flying This Level", 30, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 70, PASTEL_LIGHT_GRAY, center=True)

def draw_post_goal_menu_screen(surface, level): # Menu after choosing to continue flying post-goal
    surface.fill(PASTEL_DARK_GRAY)
    draw_text(surface, f"Level {level} - Cruising", 50, SCREEN_WIDTH//2, SCREEN_HEIGHT//4, PASTEL_GOLD, center=True, shadow=True, shadow_color=PASTEL_BLACK)
    draw_text(surface, "Press N for Next Level", 30, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 30, PASTEL_LIGHT_GRAY, center=True)
    draw_text(surface, "Press Q to Quit to Main Menu", 30, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 10, PASTEL_LIGHT_GRAY, center=True)
    draw_text(surface, "Press R or ESCAPE to Resume Flying", 30, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50, PASTEL_LIGHT_GRAY, center=True)

def draw_race_complete_screen(surface, total_time_seconds):
    surface.fill(PASTEL_DARK_GRAY)
    draw_text(surface, "Race Finished!", 60, SCREEN_WIDTH//2, SCREEN_HEIGHT//3 -20, PASTEL_GOLD, center=True, shadow=True, shadow_color=PASTEL_BLACK)
    draw_text(surface, f"Total Time: {total_time_seconds:.1f}s", 40, SCREEN_WIDTH//2, SCREEN_HEIGHT//2, PASTEL_WHITE, center=True)
    # Future: Add player's place if AI times are tracked.
    draw_text(surface, "Press ENTER for Main Menu", 32, SCREEN_WIDTH//2, SCREEN_HEIGHT*2//3, PASTEL_LIGHT_GRAY, center=True)


def draw_game_over_screen_content(surface, final_player_height, level_reached):
    surface.fill(PASTEL_DARK_GRAY)
    draw_text(surface, "GAME OVER", 72, SCREEN_WIDTH//2, SCREEN_HEIGHT//3, PASTEL_RED, center=True, shadow=True, shadow_color=PASTEL_BLACK)
    if current_game_mode == MODE_FREE_FLY:
        draw_text(surface, f"Reached Level: {level_reached}", 36, SCREEN_WIDTH//2, SCREEN_HEIGHT//2-30, PASTEL_WHITE, center=True)
    # Display final height for both modes, as it's a common metric.
    draw_text(surface, f"Final Height: {int(final_player_height)}m", 36, SCREEN_WIDTH//2, SCREEN_HEIGHT//2+10, PASTEL_WHITE, center=True)
    draw_text(surface, "Press ENTER for Menu", 32, SCREEN_WIDTH//2, SCREEN_HEIGHT*2//3, PASTEL_LIGHT_GRAY, center=True)

def draw_height_indicator_hud(surface, current_player_height, target_h_for_level, vertical_speed_val):
    indicator_bar_height = SCREEN_HEIGHT - HUD_HEIGHT - (2 * INDICATOR_Y_MARGIN_FROM_HUD) # Full height of the bar
    indicator_x_pos = SCREEN_WIDTH - INDICATOR_WIDTH - INDICATOR_X_MARGIN # Right side of screen
    indicator_y_pos = HUD_HEIGHT + INDICATOR_Y_MARGIN_FROM_HUD # Top of the bar

    pygame.draw.rect(surface, PASTEL_INDICATOR_COLOR, (indicator_x_pos, indicator_y_pos, INDICATOR_WIDTH, indicator_bar_height))

    # Max height shown on the indicator. Dynamic for Race mode, fixed for Free Fly target.
    max_indicator_height_value = target_h_for_level * 1.15 if current_game_mode == MODE_FREE_FLY else current_player_height + 500
    if max_indicator_height_value <=0: max_indicator_height_value = 1 # Avoid division by zero

    # Ground line and "0m" text
    ground_line_y = indicator_y_pos + indicator_bar_height
    pygame.draw.line(surface, PASTEL_INDICATOR_GROUND, (indicator_x_pos-5, ground_line_y), (indicator_x_pos+INDICATOR_WIDTH+5, ground_line_y), 3)
    draw_text(surface, "0m", 14, indicator_x_pos+INDICATOR_WIDTH+8, ground_line_y-7, PASTEL_TEXT_COLOR_HUD)

    # Target height marker (only in Free Fly mode)
    if current_game_mode == MODE_FREE_FLY and target_h_for_level > 0:
        target_ratio = min(target_h_for_level / max_indicator_height_value, 1.0) # Proportion of target on bar
        target_marker_y_on_bar = indicator_y_pos + indicator_bar_height * (1 - target_ratio) # Y pos from top
        pygame.draw.line(surface, PASTEL_GREEN_TARGET, (indicator_x_pos-5, target_marker_y_on_bar), (indicator_x_pos+INDICATOR_WIDTH+5, target_marker_y_on_bar), 3)
        draw_text(surface, f"{target_h_for_level}m", 14, indicator_x_pos+INDICATOR_WIDTH+8, target_marker_y_on_bar-7, PASTEL_GREEN_TARGET)

    # Player's current height marker on the bar
    player_marker_y_on_bar = ground_line_y # Default to ground if height is 0 or less
    if current_player_height > 0:
        player_height_ratio = min(current_player_height / max_indicator_height_value, 1.0)
        player_marker_y_on_bar = indicator_y_pos + indicator_bar_height * (1 - player_height_ratio)
    # Clamp marker to be within the bar's visible area
    player_marker_y_on_bar = max(indicator_y_pos, min(player_marker_y_on_bar, ground_line_y))
    pygame.draw.line(surface, PASTEL_GOLD, (indicator_x_pos, player_marker_y_on_bar), (indicator_x_pos+INDICATOR_WIDTH, player_marker_y_on_bar), 5)

    # VSI (Vertical Speed Indicator) text and arrow, next to player marker
    vsi_text_x = indicator_x_pos - 70 # Position VSI text to the left of the bar
    vsi_arrow_x_center = indicator_x_pos - 10 # Arrow closer to the bar
    
    vsi_mps = vertical_speed_val * clock.get_fps() if clock.get_fps() > 0 else vertical_speed_val * 60 # m/s
    vsi_color = PASTEL_VSI_CLIMB if vsi_mps > 0.5 else (PASTEL_VSI_SINK if vsi_mps < -0.5 else PASTEL_TEXT_COLOR_HUD)
    draw_text(surface, f"{vsi_mps:+.1f}m/s", 14, vsi_text_x , player_marker_y_on_bar - 7, vsi_color)

    if abs(vsi_mps) > 0.5: # Draw VSI arrow if significant vertical speed
        arrow_points = []
        if vsi_mps > 0: # Climbing arrow (points up)
            arrow_points = [ (vsi_arrow_x_center, player_marker_y_on_bar - VSI_ARROW_SIZE), # Tip
                             (vsi_arrow_x_center - VSI_ARROW_SIZE // 2, player_marker_y_on_bar), # Bottom-left
                             (vsi_arrow_x_center + VSI_ARROW_SIZE // 2, player_marker_y_on_bar),] # Bottom-right
        else: # Sinking arrow (points down)
            arrow_points = [ (vsi_arrow_x_center, player_marker_y_on_bar + VSI_ARROW_SIZE), # Tip
                             (vsi_arrow_x_center - VSI_ARROW_SIZE // 2, player_marker_y_on_bar), # Top-left
                             (vsi_arrow_x_center + VSI_ARROW_SIZE // 2, player_marker_y_on_bar),] # Top-right
        pygame.draw.polygon(surface, vsi_color, arrow_points)

    # Player's current height text, also near the VSI text
    player_height_text_y = player_marker_y_on_bar - 20 # Above VSI text
    if player_height_text_y < indicator_y_pos + 5 : player_height_text_y = player_marker_y_on_bar + 15 # Reposition if too high
    draw_text(surface, f"{int(current_player_height)}m", 14, vsi_text_x, player_height_text_y, PASTEL_GOLD)

def draw_weather_vane(surface, wind_x, wind_y, center_x, center_y, max_strength_for_scaling=MAX_WIND_STRENGTH):
    # Wind vector (wind_x, wind_y) indicates where the wind is blowing TO.
    # A weather vane points INTO the wind (direction wind is COMING FROM).
    vane_angle_rad = math.atan2(wind_y, wind_x) + math.pi # Add 180 deg to point into wind
    wind_magnitude = math.hypot(wind_x, wind_y)
    
    arrow_base_length = 15
    arrow_max_additional_length = 20
    arrow_color = PASTEL_TEXT_COLOR_HUD
    arrow_thickness = 2
    vane_circle_radius = 3
    vane_circle_color = PASTEL_GRAY
    
    strength_ratio = 0.0
    if max_strength_for_scaling > 0:
        strength_ratio = min(wind_magnitude / max_strength_for_scaling, 1.0)
    current_arrow_length = arrow_base_length + arrow_max_additional_length * strength_ratio

    # Vane "pointer" end
    tip_x = center_x + current_arrow_length * 0.7 * math.cos(vane_angle_rad) # Pointy end is longer
    tip_y = center_y + current_arrow_length * 0.7 * math.sin(vane_angle_rad)
    # Vane "tail" end
    tail_x = center_x - current_arrow_length * 0.3 * math.cos(vane_angle_rad) # Tail is shorter
    tail_y = center_y - current_arrow_length * 0.3 * math.sin(vane_angle_rad)
    
    pygame.draw.line(surface, arrow_color, (tail_x, tail_y), (tip_x, tip_y), arrow_thickness)

    # Arrowhead barbs at the 'tip_x, tip_y' (pointer end)
    barb_length = 8
    barb_angle_offset = math.radians(150) # Angle of barbs relative to shaft (pointing backwards from tip)
    
    barb1_angle = vane_angle_rad + barb_angle_offset
    barb1_x = tip_x + barb_length * math.cos(barb1_angle)
    barb1_y = tip_y + barb_length * math.sin(barb1_angle)
    pygame.draw.line(surface, arrow_color, (tip_x, tip_y), (barb1_x, barb1_y), arrow_thickness)

    barb2_angle = vane_angle_rad - barb_angle_offset
    barb2_x = tip_x + barb_length * math.cos(barb2_angle)
    barb2_y = tip_y + barb_length * math.sin(barb2_angle)
    pygame.draw.line(surface, arrow_color, (tip_x, tip_y), (barb2_x, barb2_y), arrow_thickness)
    
    # Center circle of the vane
    pygame.draw.circle(surface, vane_circle_color, (center_x, center_y), vane_circle_radius)
    pygame.draw.circle(surface, arrow_color, (center_x, center_y), vane_circle_radius, 1) # Outline for circle


# --- Game Loop ---
running = True
while running:
    dt = clock.tick(60) / 1000.0 # Delta time in seconds
    current_ticks = pygame.time.get_ticks()
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN:
            # --- Global Key (Escape to quit/menu, for most states) ---
            # if event.key == pygame.K_ESCAPE:
            #     if game_state in (STATE_PLAYING_FREE_FLY, STATE_RACE_PLAYING, STATE_TARGET_REACHED_CONTINUE_PLAYING):
            #         reset_to_main_menu() # Or go to an in-game menu
            #     # elif game_state != STATE_START_SCREEN: # If in a menu, ESC might go back or quit
            #     #    reset_to_main_menu()

            # --- State-Specific Key Handling ---
            if game_state == STATE_START_SCREEN:
                if event.key == pygame.K_RETURN: game_state = STATE_DIFFICULTY_SELECT
            
            elif game_state == STATE_DIFFICULTY_SELECT:
                if event.key == pygame.K_UP: selected_difficulty_option = (selected_difficulty_option - 1 + len(difficulty_options_map)) % len(difficulty_options_map)
                elif event.key == pygame.K_DOWN: selected_difficulty_option = (selected_difficulty_option + 1) % len(difficulty_options_map)
                elif event.key == pygame.K_RETURN:
                    game_difficulty = selected_difficulty_option # This is 0, 1, or 2
                    game_state = STATE_MODE_SELECT
            
            elif game_state == STATE_MODE_SELECT:
                # selected_mode_option is 0 (FreeFly) or 1 (Race)
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN: selected_mode_option = 1 - selected_mode_option
                elif event.key == pygame.K_RETURN:
                    current_game_mode = selected_mode_option
                    if current_game_mode == MODE_FREE_FLY:
                        start_new_level(1) # Start Free Fly at level 1
                    else: # MODE_RACE
                        game_state = STATE_RACE_LAPS_SELECT
            
            elif game_state == STATE_RACE_LAPS_SELECT:
                if event.key == pygame.K_UP: selected_laps_option = (selected_laps_option - 1 + len(lap_options)) % len(lap_options)
                elif event.key == pygame.K_DOWN: selected_laps_option = (selected_laps_option + 1) % len(lap_options)
                elif event.key == pygame.K_RETURN:
                    start_new_level(lap_options[selected_laps_option]) # Pass actual lap count to start_new_level

            elif game_state == STATE_PLAYING_FREE_FLY:
                if event.key == pygame.K_ESCAPE: reset_to_main_menu()
            
            elif game_state == STATE_TARGET_REACHED_OPTIONS: # After reaching height goal in Free Fly
                if event.key == pygame.K_m: # Move to next level
                    start_new_level(current_level + 1)
                elif event.key == pygame.K_c: # Continue current level
                    game_state = STATE_TARGET_REACHED_CONTINUE_PLAYING
            
            elif game_state == STATE_TARGET_REACHED_CONTINUE_PLAYING: # Flying after goal, can open menu
                if event.key == pygame.K_ESCAPE:
                    game_state = STATE_POST_GOAL_MENU
            
            elif game_state == STATE_POST_GOAL_MENU: # Menu while continuing to fly
                if event.key == pygame.K_n: # Next level from this menu
                    start_new_level(current_level + 1)
                elif event.key == pygame.K_q: # Quit to main menu
                    reset_to_main_menu()
                elif event.key == pygame.K_r or event.key == pygame.K_ESCAPE : # Resume flying
                    game_state = STATE_TARGET_REACHED_CONTINUE_PLAYING
            
            elif game_state == STATE_RACE_PLAYING:
                 if event.key == pygame.K_ESCAPE: reset_to_main_menu()

            elif game_state == STATE_RACE_COMPLETE: # After finishing a race
                if event.key == pygame.K_RETURN: reset_to_main_menu()

            elif game_state == STATE_GAME_OVER: # After crashing
                if event.key == pygame.K_RETURN: reset_to_main_menu()


    # --- Updates (Logic for active game states) ---
    if game_state in (STATE_PLAYING_FREE_FLY, STATE_TARGET_REACHED_CONTINUE_PLAYING, STATE_RACE_PLAYING):
        player.update(keys) # Update player based on input and physics
        # Camera follows player
        camera_x = player.world_x - SCREEN_WIDTH // 2
        camera_y = player.world_y - SCREEN_HEIGHT // 2

        # Update AI Gliders (only in race mode)
        if game_state == STATE_RACE_PLAYING:
            for ai in ai_gliders: # ai_gliders is a Group
                ai.update(camera_x, camera_y, race_course_markers, total_race_laps)
            
            # Player vs AI collisions (using spritecollide with circle check)
            collided_ais = pygame.sprite.spritecollide(player, ai_gliders, False, pygame.sprite.collide_circle)
            for ai_hit in collided_ais: # Renamed to avoid conflict
                player.apply_collision_effect()
                ai_hit.apply_collision_effect()
            
            # AI vs AI collisions
            ai_list_for_collision = list(ai_gliders)
            for i in range(len(ai_list_for_collision)):
                for j in range(i + 1, len(ai_list_for_collision)):
                    ai1 = ai_list_for_collision[i]
                    ai2 = ai_list_for_collision[j]
                    dist_sq = (ai1.world_x - ai2.world_x)**2 + (ai1.world_y - ai2.world_y)**2
                    if dist_sq < (ai1.collision_radius + ai2.collision_radius)**2:
                        ai1.apply_collision_effect()
                        ai2.apply_collision_effect()
        
        # Update Thermals (lifespan, visuals)
        for thermal_sprite in thermals_group:
            thermal_sprite.update(camera_x, camera_y)

        # Spawn New Thermals based on rate and land type probability
        thermal_spawn_timer += 1
        if thermal_spawn_timer >= current_thermal_spawn_rate:
            thermal_spawn_timer = 0
            spawn_world_x = camera_x + random.randint(-THERMAL_SPAWN_AREA_WIDTH // 2, THERMAL_SPAWN_AREA_WIDTH // 2)
            spawn_world_y = camera_y + random.randint(-THERMAL_SPAWN_AREA_HEIGHT // 2, THERMAL_SPAWN_AREA_HEIGHT // 2)
            
            land_type_at_spawn = get_land_type_at_world_pos(spawn_world_x, spawn_world_y)
            if random.random() < LAND_TYPE_THERMAL_PROBABILITY.get(land_type_at_spawn, 0.0):
                new_thermal = Thermal((spawn_world_x, spawn_world_y))
                all_world_sprites.add(new_thermal)
                thermals_group.add(new_thermal)

        # Update Race Markers (visual state, position) - only in race mode
        if game_state == STATE_RACE_PLAYING:
            for i, marker in enumerate(race_course_markers):
                marker.update(camera_x, camera_y, i == player.current_target_marker_index)

        # Update Foreground Clouds (movement, despawning)
        foreground_clouds_group.update()
        if len(foreground_clouds_group) < NUM_FOREGROUND_CLOUDS: # Maintain cloud count
            foreground_clouds_group.add(ForegroundCloud())

        # Player interaction with Thermals (gain lift)
        for thermal in thermals_group:
            dist_to_thermal_center = math.hypot(player.world_x - thermal.world_pos.x, player.world_y - thermal.world_pos.y)
            # Player is inside thermal if distance to center is less than thermal's radius
            # (Can add player's radius/size for more precise collision)
            if dist_to_thermal_center < thermal.radius + (player.collision_radius * 0.5):
                player.apply_lift_from_thermal(thermal.lift_power)
        
        # Check for game state changes from active play
        # Free Fly: Reached target height for the current level
        if game_state == STATE_PLAYING_FREE_FLY and player.height >= TARGET_HEIGHT_PER_LEVEL * current_level:
            game_state = STATE_TARGET_REACHED_OPTIONS
            level_end_ticks = pygame.time.get_ticks()
            time_taken_for_level = (level_end_ticks - level_timer_start_ticks) / 1000.0
        
        # Game Over: Player crashed (height <= 0)
        if player.height <= 0:
            final_score = player.height # Store final height (will be 0 or slightly less)
            player.height = 0 # Ensure height doesn't display as negative
            game_state = STATE_GAME_OVER

    # --- Drawing ---
    screen.fill(PASTEL_BLACK) # Base background for all states

    # Draw based on current game state
    if game_state == STATE_START_SCREEN:
        draw_start_screen_content(screen)
        foreground_clouds_group.draw(screen) # Clouds on menus
    elif game_state == STATE_DIFFICULTY_SELECT:
        draw_difficulty_select_screen(screen, selected_difficulty_option)
        foreground_clouds_group.draw(screen)
    elif game_state == STATE_MODE_SELECT:
        draw_mode_select_screen(screen, selected_mode_option)
        foreground_clouds_group.draw(screen)
    elif game_state == STATE_RACE_LAPS_SELECT:
        draw_laps_select_screen(screen, selected_laps_option, lap_options)
        foreground_clouds_group.draw(screen)
    elif game_state == STATE_TARGET_REACHED_OPTIONS:
        draw_target_reached_options_screen(screen, current_level, time_taken_for_level)
        foreground_clouds_group.draw(screen)
    elif game_state == STATE_POST_GOAL_MENU:
        draw_post_goal_menu_screen(screen, current_level)
        foreground_clouds_group.draw(screen)
    elif game_state == STATE_RACE_COMPLETE:
        draw_race_complete_screen(screen, time_taken_for_level)
        foreground_clouds_group.draw(screen)
    
    elif game_state in (STATE_PLAYING_FREE_FLY, STATE_TARGET_REACHED_CONTINUE_PLAYING, STATE_RACE_PLAYING):
        # Active gameplay drawing
        draw_endless_map(screen, camera_x, camera_y)
        
        player.draw_contrail(screen, camera_x, camera_y)
        for ai_glider_sprite in ai_gliders: # Iterate through group
            ai_glider_sprite.draw_contrail(screen, camera_x, camera_y)
        
        all_world_sprites.draw(screen) # Draws thermals, AI gliders, Race Markers
        screen.blit(player.image, player.rect) # Draw player on top
        
        foreground_clouds_group.draw(screen) # Clouds drawn over game world
        
        # --- HUD Drawing ---
        hud_surface = pygame.Surface((SCREEN_WIDTH, HUD_HEIGHT), pygame.SRCALPHA) # Semi-transparent panel
        hud_surface.fill(PASTEL_HUD_PANEL)
        screen.blit(hud_surface, (0,0)) # Blit HUD panel at top of screen

        hud_margin = 10; line_spacing = 22; current_y_hud = hud_margin

        # HUD: Level/Lap info
        if current_game_mode == MODE_FREE_FLY:
            draw_text(screen, f"Level: {current_level}", 20, hud_margin, current_y_hud, PASTEL_TEXT_COLOR_HUD)
            draw_text(screen, f"Target: {TARGET_HEIGHT_PER_LEVEL * current_level}m", 20, hud_margin + 120, current_y_hud, PASTEL_TEXT_COLOR_HUD)
        elif current_game_mode == MODE_RACE:
            draw_text(screen, f"Lap: {min(player.laps_completed + 1, total_race_laps)} / {total_race_laps}", 20, hud_margin, current_y_hud, PASTEL_TEXT_COLOR_HUD)
            # HUD: Race marker info
            if race_course_markers and player.current_target_marker_index < len(race_course_markers) and game_state == STATE_RACE_PLAYING :
                target_marker = race_course_markers[player.current_target_marker_index]
                dist_to_marker = math.hypot(player.world_x - target_marker.world_pos.x, player.world_y - target_marker.world_pos.y)
                draw_text(screen, f"Marker {target_marker.number}: {int(dist_to_marker/10.0)} u", 20, hud_margin + 150, current_y_hud, PASTEL_TEXT_COLOR_HUD)
                
                # Arrow pointing to next marker (on HUD)
                # This requires marker's screen position, which is updated in its own update method.
                # We need a robust way to get screen pos or angle if marker is off-screen.
                # Simple on-screen arrow if marker is visible:
                if target_marker.rect.right > 0 and target_marker.rect.left < SCREEN_WIDTH and \
                   target_marker.rect.bottom > 0 and target_marker.rect.top < SCREEN_HEIGHT:
                    
                    marker_screen_x = target_marker.rect.centerx
                    marker_screen_y = target_marker.rect.centery
                    
                    # Arrow base on HUD, e.g., near minimap or fixed point
                    hud_arrow_base_x = SCREEN_WIDTH - MINIMAP_WIDTH - MINIMAP_MARGIN - 50 # Adjusted position
                    hud_arrow_base_y = MINIMAP_MARGIN + HUD_HEIGHT + MINIMAP_HEIGHT // 2
                    
                    angle_to_marker_screen = math.atan2(marker_screen_y - hud_arrow_base_y, marker_screen_x - hud_arrow_base_x)
                    
                    arrow_len = 20
                    tip_x = hud_arrow_base_x + arrow_len * math.cos(angle_to_marker_screen)
                    tip_y = hud_arrow_base_y + arrow_len * math.sin(angle_to_marker_screen)
                    
                    # Draw a simple triangle arrow
                    # Points: tip, and two base points perpendicular to shaft, forming arrowhead
                    p1 = (tip_x, tip_y) # Tip
                    p2 = (tip_x - arrow_len * 0.5 * math.cos(angle_to_marker_screen + math.radians(150)), # Barb 1
                          tip_y - arrow_len * 0.5 * math.sin(angle_to_marker_screen + math.radians(150)))
                    p3 = (tip_x - arrow_len * 0.5 * math.cos(angle_to_marker_screen - math.radians(150)), # Barb 2
                          tip_y - arrow_len * 0.5 * math.sin(angle_to_marker_screen - math.radians(150)))
                    pygame.draw.polygon(screen, PASTEL_ACTIVE_MARKER_COLOR, [p1,p2,p3])


        current_y_hud += line_spacing
        # HUD: Timer
        if game_state == STATE_PLAYING_FREE_FLY or game_state == STATE_RACE_PLAYING:
            timer_seconds = (current_ticks - level_timer_start_ticks) / 1000.0
            draw_text(screen, f"Time: {timer_seconds:.1f}s", 20, hud_margin, current_y_hud, PASTEL_TEXT_COLOR_HUD)
        else: # Continue playing after goal, show frozen goal time
            draw_text(screen, f"Time: {time_taken_for_level:.1f}s (Goal!)", 20, hud_margin, current_y_hud, PASTEL_TEXT_COLOR_HUD)

        current_y_hud += line_spacing
        # HUD: Height and Speed
        draw_text(screen, f"Height: {int(player.height)}m", 20, hud_margin, current_y_hud, PASTEL_TEXT_COLOR_HUD)
        draw_text(screen, f"Speed: {player.speed:.1f}", 20, hud_margin + 120, current_y_hud, PASTEL_TEXT_COLOR_HUD)
        if player.speed < STALL_SPEED: # Stall warning
            draw_text(screen, "STALL!", 24, SCREEN_WIDTH//2, hud_margin + line_spacing//2, PASTEL_RED, center=True, shadow=True, shadow_color=PASTEL_BLACK)
        
        # HUD: Wind display and Weather Vane
        wind_display_text = f"Wind: <{current_wind_speed_x*10:.0f}, {current_wind_speed_y*10:.0f}>" # Scaled for readability
        wind_text_x_pos = SCREEN_WIDTH - MINIMAP_WIDTH - MINIMAP_MARGIN * 2 - 200 # Position near minimap
        draw_text(screen, wind_display_text, 18, wind_text_x_pos, hud_margin + 5, PASTEL_TEXT_COLOR_HUD)
        
        esc_text = "ESC for Menu"
        if game_state == STATE_TARGET_REACHED_CONTINUE_PLAYING: esc_text = "ESC for Options"
        draw_text(screen, esc_text, 18, wind_text_x_pos, hud_margin + 5 + line_spacing, PASTEL_TEXT_COLOR_HUD)

        draw_weather_vane(screen, current_wind_speed_x, current_wind_speed_y, wind_text_x_pos + 170, hud_margin + 25) # Position vane
        
        # HUD: Height Indicator Bar (right side of screen)
        target_h_indicator = TARGET_HEIGHT_PER_LEVEL * current_level if current_game_mode == MODE_FREE_FLY else player.height + 100
        draw_height_indicator_hud(screen, player.height, target_h_indicator, player.vertical_speed)

        # HUD: Minimap (Race mode only)
        if current_game_mode == MODE_RACE and (game_state == STATE_RACE_PLAYING or game_state == STATE_RACE_COMPLETE):
            minimap.draw(screen, player, ai_gliders, race_course_markers)
    
    elif game_state == STATE_GAME_OVER:
        draw_game_over_screen_content(screen, final_score, current_level) # Pass relevant score info
        foreground_clouds_group.draw(screen)
    
    pygame.display.flip() # Update the full display

pygame.quit()
