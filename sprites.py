# sprites.py
# Contains all Pygame sprite class definitions for the game.

import pygame
import math
import random
import config # Import constants

# --- Bullet Class ---
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, heading, owner_glider):
        super().__init__()
        self.owner = owner_glider # The glider that fired this bullet
        self.image = pygame.Surface([6, 3], pygame.SRCALPHA) # Small rectangular bullet
        self.image.fill(config.BULLET_COLOR)
        self.original_image = self.image
        self.rect = self.image.get_rect(center=(x, y))

        self.world_x = float(x)
        self.world_y = float(y)
        self.heading = heading # Degrees
        self.speed = config.BULLET_SPEED
        self.range_traveled = 0
        self.max_range = config.BULLET_RANGE

        # Rotate bullet to match heading
        self.image = pygame.transform.rotate(self.original_image, -self.heading)
        self.rect = self.image.get_rect(center=(self.world_x, self.world_y))


    def update(self, cam_x, cam_y):
        heading_rad = math.radians(self.heading)
        self.world_x += self.speed * math.cos(heading_rad)
        self.world_y += self.speed * math.sin(heading_rad)
        self.range_traveled += self.speed

        if self.range_traveled > self.max_range:
            self.kill() # Remove bullet if out of range

        self.rect.centerx = self.world_x - cam_x
        self.rect.centery = self.world_y - cam_y

        # Kill if off-screen (basic culling)
        if not config.SCREEN_WIDTH * -0.1 < self.rect.centerx < config.SCREEN_WIDTH * 1.1 or \
           not config.SCREEN_HEIGHT * -0.1 < self.rect.centery < config.SCREEN_HEIGHT * 1.1:
            self.kill()


# --- Glider Base Class ---
class GliderBase(pygame.sprite.Sprite):
    def __init__(self, body_color, wing_color, start_world_x=0.0, start_world_y=0.0, max_health=100): # Added max_health
        super().__init__()
        self.body_color = body_color
        self.wing_color = wing_color

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
        pygame.draw.rect(self.original_image, self.body_color, (0, fuselage_y_top, self.fuselage_length, self.fuselage_thickness))
        wing_x_pos = (self.fuselage_length - self.wing_chord) * 0.65
        wing_y_pos = (canvas_height - self.wing_span) / 2
        pygame.draw.rect(self.original_image, self.wing_color, (wing_x_pos, wing_y_pos, self.wing_chord, self.wing_span))
        tail_plane_x_pos = 0
        tail_plane_y_top = (canvas_height - self.tail_plane_span) / 2
        pygame.draw.rect(self.original_image, self.wing_color, (tail_plane_x_pos, tail_plane_y_top, self.tail_plane_chord, self.tail_plane_span))
        fin_base_y_center = fuselage_y_top + self.fuselage_thickness / 2
        fin_bottom_y = fin_base_y_center - self.fuselage_thickness / 2
        fin_tip_y = fin_bottom_y - self.tail_fin_height
        fin_leading_edge_x = tail_plane_x_pos + self.tail_plane_chord * 0.2
        fin_trailing_edge_x = tail_plane_x_pos + self.tail_plane_chord * 0.8
        fin_tip_x = tail_plane_x_pos + self.tail_plane_chord * 0.5
        pygame.draw.polygon(self.original_image, self.body_color, [
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
        self.current_target_marker_index = 0 # Used for Race
        self.current_delivery_destination_runway = None # Used for Delivery
        self.laps_completed = 0

        # Combat attributes
        self.max_health = max_health
        self.health = self.max_health
        self.shoot_cooldown_timer = 0
        self.shoot_cooldown_duration = config.PLAYER_SHOOT_COOLDOWN # Default, can be overridden by subclasses

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

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.kill() # Remove from all sprite groups if health is 0
            return True # Indicates glider is destroyed
        return False

    def shoot(self, bullets_group, all_sprites_group):
        if self.shoot_cooldown_timer <= 0:
            heading_rad = math.radians(self.heading)
            # Bullet starts slightly in front of the glider's nose
            bullet_start_x = self.world_x + (self.fuselage_length / 1.8) * math.cos(heading_rad) # Adjusted offset
            bullet_start_y = self.world_y + (self.fuselage_length / 1.8) * math.sin(heading_rad)

            new_bullet = Bullet(bullet_start_x, bullet_start_y, self.heading, self)
            bullets_group.add(new_bullet)
            all_sprites_group.add(new_bullet)
            self.shoot_cooldown_timer = self.shoot_cooldown_duration
            return True # Shot fired
        return False # Cooldown active

    def draw_health_bar(self, surface, cam_x, cam_y):
        if self.health > 0:
            bar_x = self.world_x - cam_x - config.HEALTH_BAR_WIDTH // 2
            bar_y = self.world_y - cam_y - self.rect.height // 2 - 10 # Above the glider

            health_ratio = self.health / self.max_health
            current_bar_width = int(config.HEALTH_BAR_WIDTH * health_ratio)

            # Determine color based on health
            bar_color = config.HEALTH_BAR_COLOR_BAD
            if health_ratio > 0.66:
                bar_color = config.HEALTH_BAR_COLOR_GOOD
            elif health_ratio > 0.33:
                bar_color = config.HEALTH_BAR_COLOR_MEDIUM

            pygame.draw.rect(surface, config.HEALTH_BAR_BACKGROUND_COLOR, (bar_x, bar_y, config.HEALTH_BAR_WIDTH, config.HEALTH_BAR_HEIGHT))
            pygame.draw.rect(surface, bar_color, (bar_x, bar_y, current_bar_width, config.HEALTH_BAR_HEIGHT))


# --- PlayerGlider Class ---
class PlayerGlider(GliderBase):
    def __init__(self):
        super().__init__(config.PASTEL_GLIDER_BODY, config.PASTEL_GLIDER_WING, max_health=config.PLAYER_MAX_HEALTH)
        self.rect = self.image.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2))
        self.previous_height = config.INITIAL_HEIGHT
        self.vertical_speed = 0.0
        self.current_lap_start_ticks = 0
        self.shoot_cooldown_duration = config.PLAYER_SHOOT_COOLDOWN

    def reset(self, start_height=config.INITIAL_HEIGHT, start_x=0.0, start_y=0.0, start_speed=config.INITIAL_SPEED, start_heading=0):
        self.world_x = start_x
        self.world_y = start_y
        self.rect.center = (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2) # Player always drawn at screen center
        self.heading = start_heading
        self.bank_angle = 0
        self.height = start_height
        self.speed = start_speed
        self.previous_height = start_height
        self.vertical_speed = 0.0
        self.trail_points = []
        self.contrail_frame_counter = 0
        self.current_target_marker_index = 0
        self.current_delivery_destination_runway = None
        self.laps_completed = 0
        self.health = self.max_health # Reset health
        self.shoot_cooldown_timer = 0
        self.update_sprite_rotation_and_position()

    def update(self, keys, game_data, bullets_group_ref, all_sprites_group_ref): # Added bullet groups
        current_wind_speed_x = game_data["current_wind_speed_x"]
        current_wind_speed_y = game_data["current_wind_speed_y"]
        game_state = game_data["game_state"]
        race_course_markers = game_data.get("race_course_markers", []) # Use .get for safety
        total_race_laps = game_data.get("total_race_laps", 0)
        level_timer_start_ticks = game_data["level_timer_start_ticks"]
        game_difficulty = game_data["game_difficulty"]
        high_scores = game_data["high_scores"]

        self.previous_height = self.height
        if self.shoot_cooldown_timer > 0:
            self.shoot_cooldown_timer -= 1

        if game_data["current_game_mode"] == config.MODE_FREE_FLY and self.height > high_scores["max_altitude_free_fly"]:
            high_scores["max_altitude_free_fly"] = self.height

        # Shooting input (only if in dogfight mode)
        if game_data["current_game_mode"] == config.MODE_DOGFIGHT and keys[pygame.K_SPACE]:
            self.shoot(bullets_group_ref, all_sprites_group_ref)


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
    def __init__(self, start_world_x, start_world_y, body_color, wing_color, personality_profile=None, ai_mode="race", player_ref=None):
        max_hp = config.AI_MAX_HEALTH if ai_mode != "wingman" else config.PLAYER_MAX_HEALTH # Wingmen could be tougher
        super().__init__(body_color, wing_color, start_world_x, start_world_y, max_health=max_hp)

        self.ai_mode = ai_mode
        self.player_ref = player_ref

        self.personality = personality_profile if personality_profile else {}
        self.speed_factor = self.personality.get("speed_factor", 1.0)
        self.turn_factor = self.personality.get("turn_factor", 1.0)
        self.altitude_preference_offset = self.personality.get("altitude_offset", random.uniform(-30, 30))

        self.base_min_speed = config.AI_BASE_SPEED_MIN * self.speed_factor
        self.base_max_speed = config.AI_BASE_SPEED_MAX * self.speed_factor
        self.base_turn_rate_scalar = config.AI_BASE_TURN_RATE_SCALAR * self.turn_factor

        self.target_altitude = config.AI_TARGET_RACE_ALTITUDE + self.altitude_preference_offset
        if self.ai_mode == "wingman" and self.player_ref:
            self.target_altitude = self.player_ref.height + self.altitude_preference_offset
        elif self.ai_mode == "dogfight_enemy" and self.player_ref:
             self.target_altitude = self.player_ref.height # Try to match player altitude initially

        self.speed = random.uniform(self.base_min_speed, self.base_max_speed)
        self.height = self.target_altitude + random.uniform(-50, 50)
        self.base_target_speed = random.uniform(self.base_min_speed, self.base_max_speed)
        self.target_speed = self.base_target_speed
        self.speed_update_timer = random.randint(0, config.AI_TARGET_SPEED_UPDATE_INTERVAL // 2)
        self.shoot_cooldown_duration = config.AI_SHOOT_COOLDOWN_BASE + random.randint(-10, 10) # Slight variation in RoF

        # Wingman specific
        self.wingman_offset_angle = random.uniform(-math.pi / 6, math.pi / 6) # Tighter spread
        self.wingman_follow_dist_x = config.WINGMAN_FOLLOW_DISTANCE_X + random.uniform(-15,15)
        self.wingman_follow_dist_y = config.WINGMAN_FOLLOW_DISTANCE_Y_BASE * (1 if random.random() < 0.5 else -1) + random.uniform(-20,20)


    def update_race_behavior(self, race_markers_list, dist_to_marker, angle_diff):
        if dist_to_marker < config.AI_MARKER_APPROACH_SLOWDOWN_DISTANCE:
            self.target_speed = self.base_min_speed + (self.base_max_speed - self.base_min_speed) * \
                                (dist_to_marker / config.AI_MARKER_APPROACH_SLOWDOWN_DISTANCE) * \
                                config.AI_MARKER_APPROACH_MIN_SPEED_FACTOR
            self.target_speed = max(self.base_min_speed * 0.8, self.target_speed)
            self.speed_update_timer = 0
        elif dist_to_marker > config.AI_STRAIGHT_BOOST_MIN_DISTANCE and abs(angle_diff) < config.AI_STRAIGHT_BOOST_THRESHOLD_ANGLE:
            self.target_speed = self.base_max_speed
            self.speed_update_timer = 0
        else:
            self.speed_update_timer += 1
            if self.speed_update_timer >= config.AI_TARGET_SPEED_UPDATE_INTERVAL:
                speed_range = self.base_max_speed - self.base_min_speed
                random_variation = random.uniform(-speed_range * config.AI_SPEED_VARIATION_FACTOR,
                                                 speed_range * config.AI_SPEED_VARIATION_FACTOR)
                self.target_speed = self.base_target_speed + random_variation
                self.target_speed = max(self.base_min_speed, min(self.target_speed, self.base_max_speed))
                self.speed_update_timer = 0

        alt_diff = self.target_altitude - self.height
        self.height += alt_diff * config.AI_ALTITUDE_CORRECTION_RATE

    def update_wingman_behavior(self):
        if not self.player_ref: return 0,0 # Should not happen if mode is wingman

        player_heading_rad = math.radians(self.player_ref.heading)

        # Target position relative to player, rotated by player's heading
        target_x_local = self.wingman_follow_dist_x * math.cos(self.wingman_offset_angle) - self.wingman_follow_dist_y * math.sin(self.wingman_offset_angle)
        target_y_local = self.wingman_follow_dist_x * math.sin(self.wingman_offset_angle) + self.wingman_follow_dist_y * math.cos(self.wingman_offset_angle)

        target_world_x = self.player_ref.world_x + (target_x_local * math.cos(player_heading_rad) - target_y_local * math.sin(player_heading_rad))
        target_world_y = self.player_ref.world_y + (target_x_local * math.sin(player_heading_rad) + target_y_local * math.cos(player_heading_rad))

        dx = target_world_x - self.world_x
        dy = target_world_y - self.world_y

        self.target_speed = self.player_ref.speed * self.speed_factor * 0.9 # Try to fly a bit slower than player
        self.target_speed = max(self.base_min_speed, min(self.target_speed, self.base_max_speed))

        self.target_altitude = self.player_ref.height + self.altitude_preference_offset
        alt_diff = self.target_altitude - self.height
        self.height += alt_diff * config.WINGMAN_ALTITUDE_CORRECTION_RATE
        return dx, dy

    def update_dogfight_enemy_behavior(self, bullets_group_ref, all_sprites_group_ref):
        if not self.player_ref: return 0,0

        dx = self.player_ref.world_x - self.world_x
        dy = self.player_ref.world_y - self.world_y
        dist_to_player = math.hypot(dx, dy)

        # Basic: try to match player speed and altitude, with some variation
        self.target_speed = self.player_ref.speed * self.speed_factor + random.uniform(-1,1)
        self.target_speed = max(self.base_min_speed, min(self.target_speed, self.base_max_speed))

        self.target_altitude = self.player_ref.height + self.altitude_preference_offset
        alt_diff = self.target_altitude - self.height
        self.height += alt_diff * config.AI_ALTITUDE_CORRECTION_RATE * 1.5 # More aggressive altitude change

        # Shooting logic
        if dist_to_player < config.DOGFIGHT_AI_SHOOTING_RANGE:
            angle_to_player_rad = math.atan2(dy, dx)
            angle_to_player_deg = math.degrees(angle_to_player_rad)
            heading_diff = (angle_to_player_deg - self.heading + 540) % 360 - 180
            if abs(heading_diff) < config.DOGFIGHT_AI_SHOOTING_CONE_ANGLE:
                self.shoot(bullets_group_ref, all_sprites_group_ref)
        return dx, dy


    def update(self, cam_x, cam_y, target_or_player_ref, total_laps_in_race, current_game_state, bullets_group_ref=None, all_sprites_group_ref=None): # Added bullet groups
        if self.shoot_cooldown_timer > 0:
            self.shoot_cooldown_timer -=1

        dx, dy = 0, 0 # Default delta for steering
        angle_diff = 0 # Default angle difference

        if self.ai_mode == "race":
            if not target_or_player_ref or current_game_state != config.STATE_RACE_PLAYING:
                self.update_sprite_rotation_and_position(cam_x, cam_y); self.update_contrail(); return
            race_markers_list = target_or_player_ref
            target_marker = race_markers_list[self.current_target_marker_index]
            dx_marker = target_marker.world_pos.x - self.world_x
            dy_marker = target_marker.world_pos.y - self.world_y
            dist_to_marker = math.hypot(dx_marker, dy_marker)
            target_angle_rad = math.atan2(dy_marker, dx_marker)
            target_angle_deg = math.degrees(target_angle_rad)
            angle_diff = (target_angle_deg - self.heading + 540) % 360 - 180
            self.update_race_behavior(race_markers_list, dist_to_marker, angle_diff)
            if dist_to_marker < target_marker.world_radius:
                self.current_target_marker_index += 1
                if self.current_target_marker_index >= len(race_markers_list):
                    self.laps_completed += 1; self.current_target_marker_index = 0

        elif self.ai_mode == "wingman":
            if not self.player_ref or current_game_state not in [config.STATE_PLAYING_FREE_FLY, config.STATE_DELIVERY_PLAYING]: # Wingmen in Free Fly & Delivery
                self.update_sprite_rotation_and_position(cam_x, cam_y); self.update_contrail(); return
            dx, dy = self.update_wingman_behavior()
            target_angle_rad = math.atan2(dy, dx) # atan2 handles signs correctly
            target_angle_deg = math.degrees(target_angle_rad)
            angle_diff = (target_angle_deg - self.heading + 540) % 360 - 180

        elif self.ai_mode == "dogfight_enemy":
            if not self.player_ref or current_game_state != config.STATE_DOGFIGHT_PLAYING:
                self.update_sprite_rotation_and_position(cam_x, cam_y); self.update_contrail(); return
            dx, dy = self.update_dogfight_enemy_behavior(bullets_group_ref, all_sprites_group_ref)
            target_angle_rad = math.atan2(dy, dx)
            target_angle_deg = math.degrees(target_angle_rad)
            angle_diff = (target_angle_deg - self.heading + 540) % 360 - 180
        else:
            self.update_sprite_rotation_and_position(cam_x, cam_y); self.update_contrail(); return

        # Common steering and movement
        turn_rate = self.base_turn_rate_scalar
        if self.ai_mode == "wingman":
            turn_rate *= config.WINGMAN_CASUALNESS_FACTOR # Slower, more casual turning for wingmen

        turn_this_frame = angle_diff * turn_rate
        self.heading = (self.heading + turn_this_frame) % 360

        if self.speed < self.target_speed: self.speed += config.ACCELERATION * 0.5
        elif self.speed > self.target_speed: self.speed -= config.ACCELERATION * 0.5
        self.speed = max(self.base_min_speed * 0.7, min(self.speed, self.base_max_speed * 1.1))

        if self.height < 0: self.height = 0

        heading_rad = math.radians(self.heading)
        self.world_x += self.speed * math.cos(heading_rad)
        self.world_y += self.speed * math.sin(heading_rad)

        self.update_sprite_rotation_and_position(cam_x, cam_y)
        self.update_contrail()


# --- Thermal Class ---
class Thermal(pygame.sprite.Sprite):
    def __init__(self, world_center_pos, game_difficulty_param):
        super().__init__()
        self.world_pos = pygame.math.Vector2(world_center_pos)
        min_r, max_r, min_l, max_l = config.NORMAL_MIN_THERMAL_RADIUS, config.NORMAL_MAX_THERMAL_RADIUS, config.NORMAL_MIN_THERMAL_LIFESPAN, config.NORMAL_MAX_THERMAL_LIFESPAN

        if game_difficulty_param == config.DIFFICULTY_NOOB:
            min_r, max_r, min_l, max_l = config.NOOB_MIN_THERMAL_RADIUS, config.NOOB_MAX_THERMAL_RADIUS, config.NOOB_MIN_THERMAL_LIFESPAN, config.NOOB_MAX_THERMAL_LIFESPAN
        elif game_difficulty_param == config.DIFFICULTY_EASY:
            pass

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
        self.world_radius = config.RACE_MARKER_RADIUS_WORLD # Interaction radius
        self.visual_radius = config.RACE_MARKER_VISUAL_RADIUS_WORLD # Drawing radius
        self.image = pygame.Surface((self.visual_radius * 2, self.visual_radius * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self._draw_marker_image(False) # Initial draw

    def _draw_marker_image(self, is_active):
        color_to_use = config.PASTEL_ACTIVE_MARKER_COLOR if is_active else config.PASTEL_MARKER_COLOR
        self.image.fill((0,0,0,0)) # Clear previous drawing
        pygame.draw.circle(self.image, color_to_use, (self.visual_radius, self.visual_radius), self.visual_radius)
        pygame.draw.circle(self.image, config.PASTEL_WHITE, (self.visual_radius, self.visual_radius), int(self.visual_radius * 0.7))

        font_obj = pygame.font.Font(None, int(self.visual_radius * 1.1))
        text_surf = font_obj.render(str(self.number), True, config.PASTEL_BLACK)
        text_rect = text_surf.get_rect(center=(self.visual_radius, self.visual_radius))
        self.image.blit(text_surf, text_rect)

    def update(self, cam_x, cam_y, is_active):
        self.rect.centerx = self.world_pos.x - cam_x
        self.rect.centery = self.world_pos.y - cam_y
        self._draw_marker_image(is_active) # Redraw if active state changes or for dynamic effects

# --- Runway Class (New for Delivery Mode) ---
class Runway(pygame.sprite.Sprite):
    def __init__(self, world_x, world_y, is_destination_runway=False, is_start_runway=False):
        super().__init__()
        self.world_pos = pygame.math.Vector2(world_x, world_y)
        self.is_destination = is_destination_runway
        self.is_start = is_start_runway
        self.visual_radius = config.DELIVERY_RUNWAY_VISUAL_RADIUS_WORLD
        self.interaction_radius = config.DELIVERY_RUNWAY_INTERACTION_RADIUS # For landing detection

        # Simple visual: a rectangle. Could be more complex.
        # Runway usually longer in one dimension. Let's make it a square for simplicity on map.
        self.image = pygame.Surface((self.visual_radius * 2, self.visual_radius * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self._draw_runway_image()

    def _draw_runway_image(self):
        self.image.fill((0,0,0,0)) # Clear previous drawing
        runway_color = config.PASTEL_RUNWAY_COLOR
        if self.is_destination:
            runway_color = config.PASTEL_RUNWAY_DESTINATION_COLOR
        elif self.is_start:
            runway_color = config.PASTEL_RUNWAY_START_COLOR

        # Draw a simple filled circle for the runway marker on the map
        pygame.draw.circle(self.image, runway_color, (self.visual_radius, self.visual_radius), self.visual_radius)
        
        # Add a letter: 'S' for Start, 'D' for Destination
        letter = ""
        if self.is_start: letter = "S"
        elif self.is_destination: letter = "D"

        if letter:
            font_obj = pygame.font.Font(None, int(self.visual_radius * 1.2)) # Slightly larger font
            text_surf = font_obj.render(letter, True, config.PASTEL_WHITE)
            text_rect = text_surf.get_rect(center=(self.visual_radius, self.visual_radius))
            self.image.blit(text_surf, text_rect)

    def update(self, cam_x, cam_y):
        self.rect.centerx = self.world_pos.x - cam_x
        self.rect.centery = self.world_pos.y - cam_y
        # No need to redraw constantly unless its state changes, but _draw_runway_image is cheap.

# --- ForegroundCloud Class ---
class ForegroundCloud(pygame.sprite.Sprite):
    def __init__(self, initial_distribution=False, index=0, total_clouds=config.NUM_FOREGROUND_CLOUDS):
        super().__init__()
        self.width = random.randint(100, 250)
        self.height = random.randint(40, 80)
        self.image = pygame.Surface([self.width, self.height], pygame.SRCALPHA)
        for _ in range(random.randint(4, 7)):
            puff_w, puff_h = random.randint(int(self.width * 0.4), int(self.width * 0.8)), random.randint(int(self.height * 0.5), int(self.height * 0.9))
            puff_x, puff_y = random.randint(0, self.width - puff_w), random.randint(0, self.height - puff_h)
            pygame.draw.ellipse(self.image, (*config.PASTEL_CLOUD, random.randint(config.CLOUD_MIN_ALPHA, config.CLOUD_MAX_ALPHA)), (puff_x, puff_y, puff_w, puff_h))

        self.speed_factor = random.uniform(config.MIN_CLOUD_SPEED_FACTOR, config.MAX_CLOUD_SPEED_FACTOR)
        self.dx = config.current_wind_speed_x * self.speed_factor
        self.dy = config.current_wind_speed_y * self.speed_factor
        self.x_float = 0.0
        self.y_float = 0.0

        if initial_distribution:
            self.x_float = (index / total_clouds) * config.SCREEN_WIDTH - self.width / 2 + random.uniform(-config.SCREEN_WIDTH / (total_clouds * 2), config.SCREEN_WIDTH / (total_clouds * 2))
            self.y_float = float(random.randint(-self.height // 2, config.SCREEN_HEIGHT - self.height // 2))
        else:
            if self.dx == 0 and self.dy == 0: # Handle no wind case for respawn
                side = random.choice(['left', 'right', 'top', 'bottom'])
                if side == 'left': self.x_float, self.y_float = float(-self.width - 20), float(random.randint(-self.height, config.SCREEN_HEIGHT))
                elif side == 'right': self.x_float, self.y_float = float(config.SCREEN_WIDTH + 20), float(random.randint(-self.height, config.SCREEN_HEIGHT))
                elif side == 'top': self.x_float, self.y_float = float(random.randint(-self.width, config.SCREEN_WIDTH)), float(-self.height - 20)
                else: self.x_float, self.y_float = float(random.randint(-self.width, config.SCREEN_WIDTH)), float(config.SCREEN_HEIGHT + 20)
            else: # Wind determines spawn edge
                if abs(self.dx) > abs(self.dy): # More horizontal wind
                    self.x_float = float(config.SCREEN_WIDTH + random.randint(0, 100) + self.width / 2 if self.dx < 0 else -random.randint(0, 100) - self.width / 2)
                    self.y_float = float(random.randint(-self.height // 2, config.SCREEN_HEIGHT - self.height // 2))
                else: # More vertical wind
                    self.x_float = float(random.randint(-self.width // 2, config.SCREEN_WIDTH - self.width // 2))
                    self.y_float = float(config.SCREEN_HEIGHT + random.randint(0, 50) + self.height / 2 if self.dy < 0 else -random.randint(0, 50) - self.height / 2)

        self.rect = self.image.get_rect(topleft=(round(self.x_float), round(self.y_float)))

    def update(self):
        self.dx = config.current_wind_speed_x * self.speed_factor
        self.dy = config.current_wind_speed_y * self.speed_factor
        self.x_float += self.dx
        self.y_float += self.dy
        self.rect.topleft = (round(self.x_float), round(self.y_float))
        off_screen_margin_x = self.width * 1.5 + abs(self.dx * 20) # Dynamic margin based on speed
        off_screen_margin_y = self.height * 1.5 + abs(self.dy * 20)
        despawn = False
        if (self.dx < 0 and self.rect.right < -off_screen_margin_x) or \
           (self.dx > 0 and self.rect.left > config.SCREEN_WIDTH + off_screen_margin_x) or \
           (self.dy < 0 and self.rect.bottom < -off_screen_margin_y) or \
           (self.dy > 0 and self.rect.top > config.SCREEN_HEIGHT + off_screen_margin_y) or \
           (self.dx == 0 and self.dy == 0 and not (-off_screen_margin_x < self.rect.centerx < config.SCREEN_WIDTH + off_screen_margin_x and \
                                               -off_screen_margin_y < self.rect.centery < config.SCREEN_HEIGHT + off_screen_margin_y)): # Stagnant cloud off screen
            despawn = True
        if despawn:
            self.kill()
