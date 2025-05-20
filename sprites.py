# sprites.py
# Contains all Pygame sprite class definitions for the game.

import pygame
import math
import random
import config # Import constants

# --- Glider Base Class ---
class GliderBase(pygame.sprite.Sprite):
    def __init__(self, body_color, wing_color, start_world_x=0.0, start_world_y=0.0):
        super().__init__()
        self.fuselage_length = config.GLIDER_COLLISION_RADIUS * 2.25 
        self.fuselage_thickness = config.GLIDER_COLLISION_RADIUS * 0.2
        self.wing_span = config.GLIDER_COLLISION_RADIUS * 3.5
        self.wing_chord = config.GLIDER_COLLISION_RADIUS * 0.25
        self.tail_plane_span = config.GLIDER_COLLISION_RADIUS * 0.9
        self.tail_plane_chord = config.GLIDER_COLLISION_RADIUS * 0.2
        self.tail_fin_height = config.GLIDER_COLLISION_RADIUS * 0.4
        
        self.fuselage_length = max(1, self.fuselage_length)
        self.fuselage_thickness = max(1, self.fuselage_thickness)
        self.wing_span = max(1, self.wing_span)
        self.wing_chord = max(1, self.wing_chord)
        self.tail_plane_span = max(1, self.tail_plane_span)
        self.tail_plane_chord = max(1, self.tail_plane_chord)
        self.tail_fin_height = max(1, self.tail_fin_height)

        canvas_width = self.fuselage_length 
        canvas_height = self.wing_span    
        self.original_image = pygame.Surface([int(canvas_width), int(canvas_height)], pygame.SRCALPHA)
        
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
        self.collision_radius = config.GLIDER_COLLISION_RADIUS
        self.world_x = start_world_x
        self.world_y = start_world_y
        self.heading = 0 
        self.bank_angle = 0 
        self.height = config.INITIAL_HEIGHT 
        self.speed = config.INITIAL_SPEED 
        self.trail_points = [] 
        self.contrail_frame_counter = 0
        self.current_target_marker_index = 0
        self.laps_completed = 0

    def update_sprite_rotation_and_position(self, cam_x=None, cam_y=None):
        self.image = pygame.transform.rotate(self.original_image, -self.heading) 
        if isinstance(self, PlayerGlider): 
            self.rect = self.image.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2))
        elif cam_x is not None and cam_y is not None: 
            self.rect = self.image.get_rect(center=(self.world_x - cam_x, self.world_y - cam_y))
        else:
             self.rect = self.image.get_rect(center=(self.world_x, self.world_y))


    def update_contrail(self):
        heading_rad = math.radians(self.heading)
        self.contrail_frame_counter +=1
        if self.contrail_frame_counter >= config.CONTRAIL_POINT_DELAY:
            self.contrail_frame_counter = 0
            effective_tail_offset = (self.fuselage_length / 2) - 2 
            tail_offset_x_world = -effective_tail_offset * math.cos(heading_rad)
            tail_offset_y_world = -effective_tail_offset * math.sin(heading_rad)
            self.trail_points.append((self.world_x + tail_offset_x_world, self.world_y + tail_offset_y_world))
            if len(self.trail_points) > config.CONTRAIL_LENGTH: 
                self.trail_points.pop(0) 

    def draw_contrail(self, surface, cam_x, cam_y):
        if len(self.trail_points) > 1:
            for i, world_point in enumerate(self.trail_points):
                alpha = int(200 * (i / config.CONTRAIL_LENGTH))
                screen_px = world_point[0] - cam_x
                screen_py = world_point[1] - cam_y
                if 0 <= screen_px <= config.SCREEN_WIDTH and 0 <= screen_py <= config.SCREEN_HEIGHT:
                    try: 
                        pygame.draw.circle(surface, (*config.PASTEL_CONTRAIL_COLOR, alpha), (screen_px, screen_py), 2)
                    except pygame.error: 
                        pass 

    def apply_collision_effect(self):
        self.speed *= 0.5
        knockback_angle = random.uniform(0, 2 * math.pi)
        knockback_dist = 5 
        self.world_x += knockback_dist * math.cos(knockback_angle)
        self.world_y += knockback_dist * math.sin(knockback_angle)

# --- PlayerGlider Class ---
class PlayerGlider(GliderBase):
    def __init__(self):
        super().__init__(config.PASTEL_GLIDER_BODY, config.PASTEL_GLIDER_WING)
        self.rect = self.image.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2))
        self.previous_height = config.INITIAL_HEIGHT 
        self.vertical_speed = 0.0
        self.current_lap_start_ticks = 0

    def reset(self, start_height=config.INITIAL_HEIGHT):
        self.world_x = 0.0
        self.world_y = 0.0
        self.rect.center = (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2)
        self.heading = 0
        self.bank_angle = 0
        self.height = start_height
        self.speed = config.INITIAL_SPEED
        self.previous_height = start_height
        self.vertical_speed = 0.0
        self.trail_points = []
        self.contrail_frame_counter = 0
        self.current_target_marker_index = 0
        self.laps_completed = 0
        # self.current_lap_start_ticks is reset in game_state_manager's start_new_level or reset_to_main_menu
        self.update_sprite_rotation_and_position() 

    def update(self, keys, game_data): 
        current_wind_speed_x = game_data["current_wind_speed_x"]
        current_wind_speed_y = game_data["current_wind_speed_y"]
        game_state = game_data["game_state"]
        race_course_markers = game_data["race_course_markers"]
        total_race_laps = game_data["total_race_laps"]
        level_timer_start_ticks = game_data["level_timer_start_ticks"]
        game_difficulty = game_data["game_difficulty"] # This is now correctly passed
        high_scores = game_data["high_scores"]
        # player_race_lap_times is modified directly in game_data dictionary by main logic

        self.previous_height = self.height

        if game_data["current_game_mode"] == config.MODE_FREE_FLY and self.height > high_scores["max_altitude_free_fly"]:
            high_scores["max_altitude_free_fly"] = self.height

        if keys[pygame.K_UP]: 
            self.speed += config.ACCELERATION
        elif keys[pygame.K_DOWN]: 
            potential_new_speed = self.speed - config.ACCELERATION
            if potential_new_speed >= config.MIN_SPEED: 
                self.speed = potential_new_speed
                self.height += config.ACCELERATION * config.ZOOM_CLIMB_FACTOR 
            else: 
                self.speed = config.MIN_SPEED 
        self.speed = max(config.MIN_SPEED, min(self.speed, config.MAX_SPEED)) 

        if keys[pygame.K_LEFT]: 
            self.bank_angle -= config.BANK_RATE
        elif keys[pygame.K_RIGHT]: 
            self.bank_angle += config.BANK_RATE
        else: 
            self.bank_angle *= 0.95 
        if abs(self.bank_angle) < 0.1: 
            self.bank_angle = 0 
        self.bank_angle = max(-config.MAX_BANK_ANGLE, min(self.bank_angle, config.MAX_BANK_ANGLE)) 
        
        actual_turn_rate_factor = config.BASE_PLAYER_BANK_TO_DEGREES_PER_FRAME
        if game_difficulty == config.DIFFICULTY_NOOB: 
            actual_turn_rate_factor *= config.NOOB_TURN_FACTOR
        elif game_difficulty == config.DIFFICULTY_EASY: 
            actual_turn_rate_factor *= config.EASY_TURN_FACTOR
        else: 
            actual_turn_rate_factor *= config.NORMAL_TURN_FACTOR
        turn_rate_degrees = self.bank_angle * actual_turn_rate_factor
        self.heading = (self.heading + turn_rate_degrees) % 360
        
        heading_rad = math.radians(self.heading)
        self.world_x += self.speed * math.cos(heading_rad) + current_wind_speed_x
        self.world_y += self.speed * math.sin(heading_rad) + current_wind_speed_y
        
        if self.speed < config.STALL_SPEED:
            height_change_due_to_physics = -config.GRAVITY_BASE_PULL - config.STALL_SINK_PENALTY
        else:
            lift_from_airspeed = self.speed * config.LIFT_PER_SPEED_UNIT
            net_vertical_force = lift_from_airspeed - config.GRAVITY_BASE_PULL
            if net_vertical_force < 0:
                height_change_due_to_physics = max(net_vertical_force, -config.MINIMUM_SINK_RATE)
            else:
                height_change_due_to_physics = net_vertical_force
        self.height += height_change_due_to_physics

        if height_change_due_to_physics < 0: 
            self.speed = min(self.speed + abs(height_change_due_to_physics) * config.DIVE_TO_SPEED_FACTOR, config.MAX_SPEED)
        
        self.vertical_speed = self.height - self.previous_height
        self.update_sprite_rotation_and_position()
        self.update_contrail()
        
        new_game_state = game_state
        time_taken_for_level_update = game_data["time_taken_for_level"]

        if game_state == config.STATE_RACE_PLAYING and race_course_markers:
            target_marker = race_course_markers[self.current_target_marker_index]
            if math.hypot(self.world_x - target_marker.world_pos.x, self.world_y - target_marker.world_pos.y) < target_marker.world_radius: 
                self.current_target_marker_index += 1
                if self.current_target_marker_index >= len(race_course_markers): 
                    self.laps_completed += 1
                    lap_time_seconds = (pygame.time.get_ticks() - self.current_lap_start_ticks) / 1000.0
                    game_data["player_race_lap_times"].append(lap_time_seconds) 
                    if lap_time_seconds < high_scores["best_lap_time_race"]:
                        high_scores["best_lap_time_race"] = lap_time_seconds
                    self.current_lap_start_ticks = pygame.time.get_ticks()
                    self.current_target_marker_index = 0 
                    if self.laps_completed >= total_race_laps: 
                        new_game_state = config.STATE_RACE_COMPLETE
                        time_taken_for_level_update = (pygame.time.get_ticks() - level_timer_start_ticks) / 1000.0 
                        if total_race_laps not in high_scores["best_total_race_times"] or \
                           time_taken_for_level_update < high_scores["best_total_race_times"][total_race_laps]:
                            high_scores["best_total_race_times"][total_race_laps] = time_taken_for_level_update
        
        return new_game_state, time_taken_for_level_update


    def apply_lift_from_thermal(self, thermal_lift_power_at_nominal_speed, game_difficulty_param):
        if self.speed < config.STALL_SPEED: return 
        actual_lift_power = thermal_lift_power_at_nominal_speed
        if game_difficulty_param == config.DIFFICULTY_EASY: 
            actual_lift_power *= config.EASY_MODE_THERMAL_LIFT_MULTIPLIER
        elif game_difficulty_param == config.DIFFICULTY_NOOB: 
            actual_lift_power *= config.NOOB_MODE_THERMAL_LIFT_MULTIPLIER
        self.height += max(actual_lift_power * (config.INITIAL_SPEED / max(self.speed, config.MIN_SPEED * 0.5)), actual_lift_power * 0.2)

# --- AI Glider Class ---
class AIGlider(GliderBase):
    def __init__(self, start_world_x, start_world_y):
        super().__init__(config.PASTEL_AI_GLIDER_BODY, config.PASTEL_AI_GLIDER_WING, start_world_x, start_world_y)
        self.speed = random.uniform(config.AI_SPEED_MIN, config.AI_SPEED_MAX)
        self.height = config.AI_TARGET_RACE_ALTITUDE + random.uniform(-50, 50) 
        self.target_speed = self.speed 
        self.speed_update_timer = random.randint(0, config.AI_TARGET_SPEED_UPDATE_INTERVAL // 2)

    def update(self, cam_x, cam_y, race_markers_list, total_laps_in_race, current_game_state):
        if not race_markers_list or current_game_state != config.STATE_RACE_PLAYING: 
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
        self.heading = (self.heading + (angle_diff * config.AI_TURN_RATE_SCALAR)) % 360
        
        if dist_to_marker < config.AI_MARKER_APPROACH_SLOWDOWN_DISTANCE:
            self.target_speed = config.AI_SPEED_MIN + (config.AI_SPEED_MAX - config.AI_SPEED_MIN) * \
                                (dist_to_marker / config.AI_MARKER_APPROACH_SLOWDOWN_DISTANCE) * \
                                config.AI_MARKER_APPROACH_MIN_SPEED_FACTOR
            self.target_speed = max(config.AI_SPEED_MIN * 0.8, self.target_speed)
            self.speed_update_timer = 0
        else:
            self.speed_update_timer += 1
            if self.speed_update_timer >= config.AI_TARGET_SPEED_UPDATE_INTERVAL:
                speed_range = config.AI_SPEED_MAX - config.AI_SPEED_MIN
                random_variation = random.uniform(-speed_range * config.AI_SPEED_VARIATION_FACTOR, 
                                                 speed_range * config.AI_SPEED_VARIATION_FACTOR)
                self.target_speed = self.speed + random_variation
                self.target_speed = max(config.AI_SPEED_MIN, min(self.target_speed, config.AI_SPEED_MAX))
                self.speed_update_timer = 0

        if self.speed < self.target_speed: 
            self.speed += config.ACCELERATION * 0.5 
        elif self.speed > self.target_speed: 
            self.speed -= config.ACCELERATION * 0.5
        self.speed = max(config.AI_SPEED_MIN * 0.7, min(self.speed, config.AI_SPEED_MAX * 1.1)) 
        
        alt_diff = config.AI_TARGET_RACE_ALTITUDE - self.height
        self.height += alt_diff * config.AI_ALTITUDE_CORRECTION_RATE 
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
    def __init__(self, world_center_pos, game_difficulty_param): # Pass game_difficulty
        super().__init__()
        self.world_pos = pygame.math.Vector2(world_center_pos)
        min_r, max_r, min_l, max_l = config.NORMAL_MIN_THERMAL_RADIUS, config.NORMAL_MAX_THERMAL_RADIUS, config.NORMAL_MIN_THERMAL_LIFESPAN, config.NORMAL_MAX_THERMAL_LIFESPAN
        
        if game_difficulty_param == config.DIFFICULTY_NOOB:
            min_r, max_r, min_l, max_l = config.NOOB_MIN_THERMAL_RADIUS, config.NOOB_MAX_THERMAL_RADIUS, config.NOOB_MIN_THERMAL_LIFESPAN, config.NOOB_MAX_THERMAL_LIFESPAN
        elif game_difficulty_param == config.DIFFICULTY_EASY: 
            # Assuming Easy uses Normal radius/lifespan but gets lift multiplier in PlayerGlider
            pass # Or define specific Easy params in config.py

        self.radius = random.randint(min_r, max_r)
        normalized_radius = 0.5 if max_r == min_r else (self.radius - min_r) / (max_r - min_r)
        self.lifespan = min_l + (max_l - min_l) * normalized_radius
        self.initial_lifespan = self.lifespan
        self.lift_power = config.MAX_THERMAL_LIFT_POWER - (config.MAX_THERMAL_LIFT_POWER - config.MIN_THERMAL_LIFT_POWER) * (1 - normalized_radius)
        self.image = pygame.Surface([self.radius * 2, self.radius * 2], pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.creation_time = pygame.time.get_ticks()
        self.update_visuals()

    def update_visuals(self):
        pulse_alpha_factor = (math.sin(pygame.time.get_ticks() * 0.005 + self.creation_time * 0.01) * 0.3 + 0.7)
        age_factor = max(0, self.lifespan / self.initial_lifespan if self.initial_lifespan > 0 else 0)
        alpha = int(config.THERMAL_BASE_ALPHA * pulse_alpha_factor * age_factor)
        accent_alpha = int(config.THERMAL_ACCENT_ALPHA * pulse_alpha_factor * age_factor)
        visual_radius_factor = math.sin(pygame.time.get_ticks() * 0.002 + self.creation_time * 0.005) * 0.1 + 0.95
        current_visual_radius = int(self.radius * visual_radius_factor)
        self.image.fill((0, 0, 0, 0))
        pygame.draw.circle(self.image, (*config.PASTEL_THERMAL_PRIMARY, alpha), (self.radius, self.radius), current_visual_radius)
        pygame.draw.circle(self.image, (*config.PASTEL_THERMAL_ACCENT, accent_alpha), (self.radius, self.radius), int(current_visual_radius * 0.7), 2)

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
        self.world_radius = config.RACE_MARKER_RADIUS_WORLD
        self.visual_radius = config.RACE_MARKER_VISUAL_RADIUS_WORLD
        self.image = pygame.Surface((self.visual_radius * 2, self.visual_radius * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self._draw_marker_image(False)

    def _draw_marker_image(self, is_active):
        if is_active:
            color_to_use = config.PASTEL_ACTIVE_MARKER_COLOR 
        else:
            color_to_use = config.PASTEL_MARKER_COLOR
        
        self.image.fill((0,0,0,0))
        pygame.draw.circle(self.image, color_to_use, (self.visual_radius, self.visual_radius), self.visual_radius)
        pygame.draw.circle(self.image, config.PASTEL_WHITE, (self.visual_radius, self.visual_radius), int(self.visual_radius * 0.7))
        
        # Using pygame.font.Font directly here, or pass get_cached_font from ui.py
        font_obj = pygame.font.Font(None, int(self.visual_radius * 1.1)) 
        text_surf = font_obj.render(str(self.number), True, config.PASTEL_BLACK)
        text_rect = text_surf.get_rect(center=(self.visual_radius, self.visual_radius))
        self.image.blit(text_surf, text_rect)

    def update(self, cam_x, cam_y, is_active):
        self.rect.centerx = self.world_pos.x - cam_x
        self.rect.centery = self.world_pos.y - cam_y
        self._draw_marker_image(is_active)

# --- ForegroundCloud Class ---
class ForegroundCloud(pygame.sprite.Sprite):
    def __init__(self, initial_distribution=False, index=0, total_clouds=config.NUM_FOREGROUND_CLOUDS):
        super().__init__()
        # Wind speeds are now read from config, which should be updated by game_state_manager
        self.width = random.randint(100, 250)
        self.height = random.randint(40, 80)
        self.image = pygame.Surface([self.width, self.height], pygame.SRCALPHA)
        for _ in range(random.randint(4, 7)):
            puff_w, puff_h = random.randint(int(self.width * 0.4), int(self.width * 0.8)), random.randint(int(self.height * 0.5), int(self.height * 0.9))
            puff_x, puff_y = random.randint(0, self.width - puff_w), random.randint(0, self.height - puff_h)
            pygame.draw.ellipse(self.image, (*config.PASTEL_CLOUD, random.randint(config.CLOUD_MIN_ALPHA, config.CLOUD_MAX_ALPHA)), (puff_x, puff_y, puff_w, puff_h))
        
        self.speed_factor = random.uniform(config.MIN_CLOUD_SPEED_FACTOR, config.MAX_CLOUD_SPEED_FACTOR)
        self.dx = config.current_wind_speed_x * self.speed_factor # Read from config
        self.dy = config.current_wind_speed_y * self.speed_factor # Read from config
        self.x_float = 0.0
        self.y_float = 0.0

        if initial_distribution:
            self.x_float = (index / total_clouds) * config.SCREEN_WIDTH - self.width / 2 + random.uniform(-config.SCREEN_WIDTH / (total_clouds * 2), config.SCREEN_WIDTH / (total_clouds * 2))
            self.y_float = float(random.randint(-self.height // 2, config.SCREEN_HEIGHT - self.height // 2))
        else:
            if self.dx == 0 and self.dy == 0:
                self.x_float, self.y_float = (float(random.choice([-self.width - 20, config.SCREEN_WIDTH + 20])), float(random.randint(-self.height, config.SCREEN_HEIGHT))) if random.choice([True, False]) else (float(random.randint(-self.width, config.SCREEN_WIDTH)), float(random.choice([-self.height - 20, config.SCREEN_HEIGHT + 20])))
            else:
                self.x_float, self.y_float = (float(config.SCREEN_WIDTH + random.randint(0, 100) + self.width / 2 if self.dx < 0 else -random.randint(0, 100) - self.width / 2), float(random.randint(-self.height // 2, config.SCREEN_HEIGHT - self.height // 2))) if abs(self.dx) > abs(self.dy) else (float(random.randint(-self.width // 2, config.SCREEN_WIDTH - self.width // 2)), float(config.SCREEN_HEIGHT + random.randint(0, 50) + self.height / 2 if self.dy < 0 else -random.randint(0, 50) - self.height / 2))
        self.rect = self.image.get_rect(topleft=(round(self.x_float), round(self.y_float)))

    def update(self):
        self.dx = config.current_wind_speed_x * self.speed_factor # Re-fetch from config in case wind changed
        self.dy = config.current_wind_speed_y * self.speed_factor
        self.x_float += self.dx
        self.y_float += self.dy
        self.rect.topleft = (round(self.x_float), round(self.y_float))
        off_screen_margin_x = self.width * 1.5 + abs(self.dx * 20)
        off_screen_margin_y = self.height * 1.5 + abs(self.dy * 20)
        despawn = False
        if (self.dx < 0 and self.rect.right < -off_screen_margin_x) or \
           (self.dx > 0 and self.rect.left > config.SCREEN_WIDTH + off_screen_margin_x) or \
           (self.dy < 0 and self.rect.bottom < -off_screen_margin_y) or \
           (self.dy > 0 and self.rect.top > config.SCREEN_HEIGHT + off_screen_margin_y) or \
           (self.dx == 0 and self.dy == 0 and not (-off_screen_margin_x < self.rect.centerx < config.SCREEN_WIDTH + off_screen_margin_x and \
                                               -off_screen_margin_y < self.rect.centery < config.SCREEN_HEIGHT + off_screen_margin_y)):
            despawn = True
        if despawn:
            self.kill()
