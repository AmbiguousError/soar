# game_state_manager.py
# Manages game state, global variables, and core logic functions.

import pygame
import math
import random
import config
from sprites import PlayerGlider, AIGlider, Thermal, RaceMarker, ForegroundCloud, Bullet, Runway, DeliveryCheckpoint
from map_generation import regenerate_river_parameters, get_land_type_at_world_pos
from ui import Minimap

# --- Game Variables (managed by this module) ---
player = PlayerGlider()
ai_gliders = pygame.sprite.Group()
wingmen_group = pygame.sprite.Group()
dogfight_enemies_group = pygame.sprite.Group()
all_world_sprites = pygame.sprite.Group()
thermals_group = pygame.sprite.Group()
foreground_clouds_group = pygame.sprite.Group()
bullets_group = pygame.sprite.Group()
delivery_runways_group = pygame.sprite.Group()
delivery_checkpoints_group = pygame.sprite.Group()

game_state = config.STATE_START_SCREEN
current_level = 1
level_timer_start_ticks = 0
time_taken_for_level = 0.0
current_thermal_spawn_rate = config.BASE_THERMAL_SPAWN_RATE
thermal_spawn_timer = 0
final_score = 0
unlocked_wingmen_count = 0
wingman_was_actually_unlocked_this_turn = False

selected_difficulty_option = config.DIFFICULTY_NORMAL
config.game_difficulty = selected_difficulty_option
selected_mode_option = config.MODE_FREE_FLY
config.current_game_mode = selected_mode_option
selected_laps_option = 1
lap_options = [1, 3, 5]
total_race_laps = config.DEFAULT_RACE_LAPS

current_map_offset_x = 0
current_map_offset_y = 0
tile_type_cache = {}

high_scores = {
    "longest_flight_time_free_fly": 0.0,
    "max_altitude_free_fly": 0.0,
    "best_lap_time_race": float('inf'),
    "best_total_race_times": {},
    "max_deliveries_completed": 0
}
player_race_lap_times = []
race_course_markers = []

# Delivery mode specific
delivery_start_runway = None
delivery_destination_runway = None
successful_deliveries_count = 0
delivery_checkpoints_list = []
delivery_active_target_object = None
delivery_current_checkpoint_index = -1

game_state_before_pause = None
pause_start_ticks = 0
current_session_flight_start_ticks = 0

dogfight_current_round = 1
dogfight_enemies_to_spawn_this_round = 0
dogfight_enemies_defeated_this_round = 0

minimap = Minimap(config.MINIMAP_WIDTH, config.MINIMAP_HEIGHT, config.MINIMAP_MARGIN)

# --- Core Game Logic Functions ---
def generate_race_course(num_markers=8):
    global race_course_markers, all_world_sprites
    race_course_markers.clear()
    for sprite in list(all_world_sprites):
        if isinstance(sprite, RaceMarker):
            sprite.kill()
    for i in range(num_markers):
        marker = RaceMarker(random.uniform(-config.RACE_COURSE_AREA_HALFWIDTH, config.RACE_COURSE_AREA_HALFWIDTH),
                            random.uniform(-config.RACE_COURSE_AREA_HALFWIDTH, config.RACE_COURSE_AREA_HALFWIDTH), i + 1)
        race_course_markers.append(marker)
        all_world_sprites.add(marker)

def find_suitable_runway_location(existing_locations, map_offset_x, map_offset_y, cache, required_min_distance_apart):
    for _ in range(config.RUNWAY_MAX_PLACEMENT_ATTEMPTS):
        rx = random.uniform(-config.RACE_COURSE_AREA_HALFWIDTH * 0.8, config.RACE_COURSE_AREA_HALFWIDTH * 0.8)
        ry = random.uniform(-config.RACE_COURSE_AREA_HALFWIDTH * 0.8, config.RACE_COURSE_AREA_HALFWIDTH * 0.8)
        land_type = get_land_type_at_world_pos(rx, ry, map_offset_x, map_offset_y, cache)
        too_close = False
        if land_type in config.RUNWAY_SUITABLE_LAND_TYPES:
            for loc in existing_locations:
                if math.hypot(rx - loc[0], ry - loc[1]) < required_min_distance_apart:
                    too_close = True
                    break
            if not too_close:
                return rx, ry
    return None

def _set_next_delivery_target():
    global delivery_active_target_object, delivery_checkpoints_list, delivery_current_checkpoint_index, delivery_destination_runway
    
    if delivery_checkpoints_list and delivery_current_checkpoint_index < len(delivery_checkpoints_list):
        delivery_active_target_object = delivery_checkpoints_list[delivery_current_checkpoint_index]
    elif delivery_destination_runway:
        delivery_active_target_object = delivery_destination_runway
    else:
        delivery_active_target_object = None

def setup_delivery_mission():
    global delivery_start_runway, delivery_destination_runway, delivery_runways_group, all_world_sprites
    global player, game_state, current_map_offset_x, current_map_offset_y, tile_type_cache
    global level_timer_start_ticks, wingman_was_actually_unlocked_this_turn, current_level
    global delivery_checkpoints_list, delivery_checkpoints_group, delivery_active_target_object, delivery_current_checkpoint_index

    # Clear previous runways and checkpoints
    for sprite in delivery_runways_group: sprite.kill()
    delivery_runways_group.empty()
    for sprite in delivery_checkpoints_group: sprite.kill()
    delivery_checkpoints_group.empty()
    delivery_checkpoints_list.clear()

    delivery_start_runway = None
    delivery_destination_runway = None
    delivery_active_target_object = None
    delivery_current_checkpoint_index = 0 

    wingman_was_actually_unlocked_this_turn = False

    num_previous_successes = current_level - 1 
    if num_previous_successes < 0: num_previous_successes = 0
    
    # This dynamic_min_runway_distance scales the direct distance between start and final destination
    dynamic_min_runway_distance = config.RUNWAY_MIN_DISTANCE_APART * (1 + (num_previous_successes * config.DELIVERY_MIN_DISTANCE_INCREASE_FACTOR))
    dynamic_min_runway_distance = max(dynamic_min_runway_distance, config.RUNWAY_MIN_DISTANCE_APART * 0.5)

    start_loc = find_suitable_runway_location([], current_map_offset_x, current_map_offset_y, tile_type_cache, 0)
    if not start_loc:
        print("Error: Could not place start runway.")
        reset_to_main_menu(); return
    delivery_start_runway = Runway(start_loc[0], start_loc[1], is_start_runway=True)
    all_world_sprites.add(delivery_start_runway); delivery_runways_group.add(delivery_start_runway)

    dest_loc = find_suitable_runway_location([start_loc], current_map_offset_x, current_map_offset_y, tile_type_cache, dynamic_min_runway_distance)
    if not dest_loc:
        print(f"Error: Could not place destination runway (dist: {dynamic_min_runway_distance}). Trying base.")
        dest_loc = find_suitable_runway_location([start_loc], current_map_offset_x, current_map_offset_y, tile_type_cache, config.RUNWAY_MIN_DISTANCE_APART)
        if not dest_loc:
            print("Error: Fallback runway placement failed."); reset_to_main_menu(); return
    delivery_destination_runway = Runway(dest_loc[0], dest_loc[1], is_destination_runway=True)
    all_world_sprites.add(delivery_destination_runway); delivery_runways_group.add(delivery_destination_runway)

    # --- New Checkpoint Generation Logic ---
    num_checkpoints_to_add = 0
    if config.DELIVERY_CHECKPOINTS_ADD_PER_N_LEVELS > 0:
        num_checkpoints_to_add = num_previous_successes // config.DELIVERY_CHECKPOINTS_ADD_PER_N_LEVELS
    num_checkpoints_to_add = min(num_checkpoints_to_add, config.DELIVERY_MAX_CHECKPOINTS)

    current_route_point = pygame.math.Vector2(delivery_start_runway.world_pos.x, delivery_start_runway.world_pos.y)
    
    if num_checkpoints_to_add > 0:
        for i in range(num_checkpoints_to_add):
            # Distance for the current leg
            scaled_leg_dist = config.DELIVERY_CHECKPOINT_BASE_LEG_DISTANCE + \
                              (num_previous_successes * config.DELIVERY_CHECKPOINT_LEG_DISTANCE_SCALE_PER_LEVEL)
            
            # Ensure leg distance is not excessively small
            scaled_leg_dist = max(scaled_leg_dist, config.DELIVERY_CHECKPOINT_BASE_LEG_DISTANCE * config.DELIVERY_CHECKPOINT_MIN_NEXT_LEG_DISTANCE_FACTOR)

            # Angle from current_route_point to the *final* destination runway
            angle_to_final_dest_rad = math.atan2(delivery_destination_runway.world_pos.y - current_route_point.y,
                                                 delivery_destination_runway.world_pos.x - current_route_point.x)

            # Determine max angular deviation for this checkpoint
            # For the last checkpoint being placed, reduce deviation to better align with final approach
            current_max_deviation_deg = config.DELIVERY_CHECKPOINT_MAX_ANGLE_DEVIATION
            if i == num_checkpoints_to_add - 1 and num_checkpoints_to_add > 0 : # If this is the last checkpoint before the final destination
                current_max_deviation_deg /= 2.0 
            
            angle_deviation_rad = math.radians(random.uniform(-current_max_deviation_deg, current_max_deviation_deg))
            
            # New heading for this leg
            actual_heading_rad = angle_to_final_dest_rad + angle_deviation_rad

            # Calculate new checkpoint position
            cp_x = current_route_point.x + scaled_leg_dist * math.cos(actual_heading_rad)
            cp_y = current_route_point.y + scaled_leg_dist * math.sin(actual_heading_rad)
            
            # (Optional: Add checks here to ensure checkpoint isn't placed in an undesirable location, e.g., too close to previous or too far out of bounds)
            # For simplicity, we'll omit complex boundary checks for now, assuming the play area is large.

            checkpoint = DeliveryCheckpoint(cp_x, cp_y, i + 1) # Checkpoint numbers 1, 2, ...
            delivery_checkpoints_list.append(checkpoint)
            all_world_sprites.add(checkpoint)
            delivery_checkpoints_group.add(checkpoint)
            
            # Update current_route_point for the next iteration
            current_route_point.x = cp_x
            current_route_point.y = cp_y
            
    _set_next_delivery_target() 

    player_start_height = config.DELIVERY_START_HEIGHT_OFFSET 
    player_start_speed = config.INITIAL_SPEED * config.DELIVERY_START_SPEED_FACTOR
    
    initial_heading_target = delivery_active_target_object if delivery_active_target_object else delivery_destination_runway 
    initial_heading = 0
    if initial_heading_target: # Ensure there's a target to point towards
      h_dx = initial_heading_target.world_pos.x - delivery_start_runway.world_pos.x
      h_dy = initial_heading_target.world_pos.y - delivery_start_runway.world_pos.y
      if h_dx != 0 or h_dy != 0: # Avoid atan2(0,0)
          initial_heading = math.degrees(math.atan2(h_dy, h_dx))

    player.reset(start_height=player_start_height,
                 start_x=delivery_start_runway.world_pos.x,
                 start_y=delivery_start_runway.world_pos.y,
                 start_speed=player_start_speed,
                 start_heading=initial_heading)
    
    level_timer_start_ticks = pygame.time.get_ticks()
    game_state = config.STATE_DELIVERY_PLAYING
    spawn_wingmen()

def generate_new_wind(): # MAKE SURE THIS IS DEFINED **BEFORE** start_new_level
    wind_angle_rad = random.uniform(0, 2 * math.pi)
    wind_strength = random.uniform(0.05, config.MAX_WIND_STRENGTH)
    config.current_wind_speed_x = wind_strength * math.cos(wind_angle_rad)
    config.current_wind_speed_y = wind_strength * math.sin(wind_angle_rad)

def spawn_wingmen():
    global wingmen_group, all_world_sprites, unlocked_wingmen_count, player
    wingmen_group.empty()
    for sprite in list(all_world_sprites):
        if isinstance(sprite, AIGlider) and sprite.ai_mode == "wingman":
            sprite.kill()
    for i in range(unlocked_wingmen_count):
        if i >= config.MAX_WINGMEN: break
        side_multiplier = 1 if i % 2 == 0 else -1
        dist_x = config.WINGMAN_FOLLOW_DISTANCE_X - (i // 2) * 20
        dist_y = (config.WINGMAN_FOLLOW_DISTANCE_Y_BASE + (i // 2) * config.WINGMAN_FORMATION_SPREAD) * side_multiplier
        player_heading_rad = math.radians(player.heading)
        start_x_offset = dist_x * math.cos(player_heading_rad) - dist_y * math.sin(player_heading_rad)
        start_y_offset = dist_x * math.sin(player_heading_rad) + dist_y * math.cos(player_heading_rad)
        start_x = player.world_x + start_x_offset
        start_y = player.world_y + start_y_offset
        body_color, wing_color = config.AI_GLIDER_COLORS_LIST[(config.NUM_AI_OPPONENTS + i + 1) % len(config.AI_GLIDER_COLORS_LIST)]
        profile = {"speed_factor": random.uniform(0.85, 1.05), "turn_factor": random.uniform(0.8, 1.1), "altitude_offset": random.uniform(-40, 10)}
        wingman = AIGlider(start_x, start_y, body_color, wing_color, profile, ai_mode="wingman", player_ref=player)
        wingmen_group.add(wingman); all_world_sprites.add(wingman)

def start_dogfight_round(round_number):
    global dogfight_current_round, dogfight_enemies_to_spawn_this_round, dogfight_enemies_defeated_this_round
    global dogfight_enemies_group, all_world_sprites, player, game_state

    dogfight_current_round = round_number
    dogfight_enemies_defeated_this_round = 0
    for enemy in dogfight_enemies_group: enemy.kill()
    dogfight_enemies_group.empty()
    dogfight_enemies_to_spawn_this_round = min(config.DOGFIGHT_INITIAL_ENEMIES + (dogfight_current_round - 1) * config.DOGFIGHT_ENEMIES_PER_ROUND_INCREASE,
                                               config.DOGFIGHT_MAX_ENEMIES_ON_SCREEN)
    player.health = player.max_health
    for i in range(dogfight_enemies_to_spawn_this_round):
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(config.SCREEN_WIDTH * 0.6, config.SCREEN_WIDTH * 0.9)
        start_x = player.world_x + distance * math.cos(angle)
        start_y = player.world_y + distance * math.sin(angle)
        body_color, wing_color = config.AI_GLIDER_COLORS_LIST[i % len(config.AI_GLIDER_COLORS_LIST)]
        profile = {"speed_factor": random.uniform(0.8, 1.1), "turn_factor": random.uniform(0.9, 1.2), "altitude_offset": random.uniform(-50, 50)}
        enemy = AIGlider(start_x, start_y, body_color, wing_color, profile, ai_mode="dogfight_enemy", player_ref=player)
        dogfight_enemies_group.add(enemy); all_world_sprites.add(enemy)
    game_state = config.STATE_DOGFIGHT_PLAYING

def start_new_level(level_param, continue_map_from_race=False):
    global current_level, level_timer_start_ticks, current_thermal_spawn_rate, thermal_spawn_timer, game_state
    global current_map_offset_x, current_map_offset_y, total_race_laps, ai_gliders, tile_type_cache
    global player_race_lap_times, current_session_flight_start_ticks, race_course_markers, dogfight_current_round
    global delivery_runways_group, delivery_start_runway, delivery_destination_runway, wingman_was_actually_unlocked_this_turn
    global delivery_checkpoints_list, delivery_checkpoints_group, delivery_active_target_object, delivery_current_checkpoint_index

    level_timer_start_ticks = pygame.time.get_ticks()
    wingman_was_actually_unlocked_this_turn = False

    if not continue_map_from_race:
        current_map_offset_x = random.randint(-200000, 200000)
        current_map_offset_y = random.randint(-200000, 200000)
        tile_type_cache.clear()
        regenerate_river_parameters(current_level + pygame.time.get_ticks())
        generate_new_wind() # CALL TO generate_new_wind

    thermals_group.empty()
    for sprite in list(all_world_sprites):
        if isinstance(sprite, (Thermal, AIGlider, RaceMarker, Bullet, Runway, DeliveryCheckpoint)):
            sprite.kill()
    bullets_group.empty()
    race_course_markers.clear()
    ai_gliders.empty()
    wingmen_group.empty()
    dogfight_enemies_group.empty()
    delivery_runways_group.empty()
    delivery_checkpoints_group.empty()
    delivery_checkpoints_list.clear()
    delivery_active_target_object = None
    delivery_current_checkpoint_index = 0

    foreground_clouds_group.empty()
    for i in range(config.NUM_FOREGROUND_CLOUDS):
        foreground_clouds_group.add(ForegroundCloud(initial_distribution=True, index=i))

    current_session_flight_start_ticks = pygame.time.get_ticks()
    player_race_lap_times.clear()

    if config.current_game_mode == config.MODE_FREE_FLY:
        current_level = level_param
        player.reset(start_height=config.INITIAL_HEIGHT)
        current_thermal_spawn_rate = config.BASE_THERMAL_SPAWN_RATE + (config.THERMAL_SPAWN_RATE_INCREASE_PER_LEVEL * (current_level - 1))
        if config.game_difficulty == config.DIFFICULTY_NOOB: current_thermal_spawn_rate = max(20, current_thermal_spawn_rate // 2)
        elif config.game_difficulty == config.DIFFICULTY_EASY: current_thermal_spawn_rate = max(30, int(current_thermal_spawn_rate * 0.75))
        thermal_spawn_timer = 0
        spawn_wingmen()
        game_state = config.STATE_PLAYING_FREE_FLY
    elif config.current_game_mode == config.MODE_RACE:
        total_race_laps = level_param
        player.reset(start_height=config.INITIAL_HEIGHT)
        player.current_lap_start_ticks = pygame.time.get_ticks()
        generate_race_course()
        for i in range(config.NUM_AI_OPPONENTS):
            angle_offset = math.pi + (i - config.NUM_AI_OPPONENTS / 2.0) * (math.pi / 6)
            dist_offset = 100 + i * 40
            ai_start_x = player.world_x + dist_offset * math.cos(angle_offset + math.radians(player.heading))
            ai_start_y = player.world_y + dist_offset * math.sin(angle_offset + math.radians(player.heading))
            body_color, wing_color = config.AI_GLIDER_COLORS_LIST[i % len(config.AI_GLIDER_COLORS_LIST)]
            profile = {"speed_factor": random.uniform(0.9, 1.1), "turn_factor": random.uniform(0.85, 1.15), "altitude_offset": random.uniform(-20, 20)}
            new_ai = AIGlider(ai_start_x, ai_start_y, body_color, wing_color, profile, ai_mode="race")
            ai_gliders.add(new_ai); all_world_sprites.add(new_ai)
        current_thermal_spawn_rate = config.BASE_THERMAL_SPAWN_RATE * 1.5
        if config.game_difficulty == config.DIFFICULTY_NOOB: current_thermal_spawn_rate = max(30, int(current_thermal_spawn_rate * 0.7))
        thermal_spawn_timer = 0
        game_state = config.STATE_RACE_PLAYING
    elif config.current_game_mode == config.MODE_DOGFIGHT:
        dogfight_current_round = level_param
        player.reset(start_height=config.INITIAL_HEIGHT)
        start_dogfight_round(dogfight_current_round)
    elif config.current_game_mode == config.MODE_DELIVERY:
        current_level = level_param
        setup_delivery_mission()
        current_thermal_spawn_rate = config.BASE_THERMAL_SPAWN_RATE
        if config.game_difficulty == config.DIFFICULTY_NOOB: current_thermal_spawn_rate = max(20, current_thermal_spawn_rate // 2)
        elif config.game_difficulty == config.DIFFICULTY_EASY: current_thermal_spawn_rate = max(30, int(current_thermal_spawn_rate * 0.75))
        thermal_spawn_timer = 0

def reset_to_main_menu():
    global game_state, current_level, final_score, selected_difficulty_option, selected_mode_option, selected_laps_option
    global player_race_lap_times, race_course_markers, unlocked_wingmen_count
    global dogfight_current_round, dogfight_enemies_defeated_this_round, dogfight_enemies_to_spawn_this_round
    global delivery_start_runway, delivery_destination_runway, delivery_runways_group, successful_deliveries_count
    global wingman_was_actually_unlocked_this_turn
    global delivery_checkpoints_list, delivery_checkpoints_group, delivery_active_target_object, delivery_current_checkpoint_index

    player.reset()
    thermals_group.empty()
    all_world_sprites.empty()
    race_course_markers.clear()
    ai_gliders.empty()
    wingmen_group.empty()
    dogfight_enemies_group.empty()
    bullets_group.empty()
    delivery_runways_group.empty()
    delivery_checkpoints_group.empty()
    delivery_checkpoints_list.clear()
    foreground_clouds_group.empty()
    tile_type_cache.clear()
    player_race_lap_times.clear()

    unlocked_wingmen_count = 0
    successful_deliveries_count = 0
    dogfight_current_round = 1
    dogfight_enemies_defeated_this_round = 0
    dogfight_enemies_to_spawn_this_round = 0
    delivery_start_runway = None
    delivery_destination_runway = None
    delivery_active_target_object = None
    delivery_current_checkpoint_index = 0
    wingman_was_actually_unlocked_this_turn = False

    config.current_wind_speed_x = -0.2
    config.current_wind_speed_y = 0.05
    for i in range(config.NUM_FOREGROUND_CLOUDS):
        foreground_clouds_group.add(ForegroundCloud(initial_distribution=True, index=i))
    current_level = 1
    final_score = 0
    selected_difficulty_option = config.DIFFICULTY_NORMAL
    config.game_difficulty = selected_difficulty_option
    selected_mode_option = config.MODE_FREE_FLY
    config.current_game_mode = selected_mode_option
    selected_laps_option = 1
    game_state = config.STATE_START_SCREEN

def update_game_logic(keys):
    global game_state, time_taken_for_level, final_score, current_thermal_spawn_rate, thermal_spawn_timer
    global current_map_offset_x, current_map_offset_y, tile_type_cache
    global race_course_markers, total_race_laps, level_timer_start_ticks
    global high_scores, player_race_lap_times, current_session_flight_start_ticks, unlocked_wingmen_count
    global dogfight_enemies_defeated_this_round, dogfight_current_round
    global delivery_destination_runway, successful_deliveries_count, current_level, wingman_was_actually_unlocked_this_turn
    global delivery_active_target_object, delivery_checkpoints_list, delivery_current_checkpoint_index

    game_data_for_player = {
        "current_wind_speed_x": config.current_wind_speed_x,
        "current_wind_speed_y": config.current_wind_speed_y,
        "game_state": game_state,
        "race_course_markers": race_course_markers,
        "total_race_laps": total_race_laps,
        "level_timer_start_ticks": level_timer_start_ticks,
        "game_difficulty": config.game_difficulty,
        "high_scores": high_scores,
        "player_race_lap_times": player_race_lap_times,
        "current_game_mode": config.current_game_mode,
        "time_taken_for_level": time_taken_for_level
    }
    new_gs_from_player, ttf_update = player.update(keys, game_data_for_player, bullets_group, all_world_sprites)
    if new_gs_from_player != game_state: game_state = new_gs_from_player
    time_taken_for_level = ttf_update
    cam_x = player.world_x - config.SCREEN_WIDTH // 2
    cam_y = player.world_y - config.SCREEN_HEIGHT // 2
    bullets_group.update(cam_x, cam_y)

    if game_state == config.STATE_RACE_PLAYING:
        for ai in ai_gliders:
            ai.update(cam_x, cam_y, race_course_markers, total_race_laps, game_state)
        collided_ais = pygame.sprite.spritecollide(player, ai_gliders, False, pygame.sprite.collide_circle)
        for ai_hit in collided_ais: player.apply_collision_effect(); ai_hit.apply_collision_effect()
        ai_list = list(ai_gliders); [(ai1.apply_collision_effect(),ai2.apply_collision_effect()) for i in range(len(ai_list)) for j in range(i+1,len(ai_list)) if(ai1:=ai_list[i],ai2:=ai_list[j],((ai1.world_x-ai2.world_x)**2+(ai1.world_y-ai2.world_y)**2)<(ai1.collision_radius+ai2.collision_radius)**2)]
        for i, marker in enumerate(race_course_markers):
            marker.update(cam_x, cam_y, i == player.current_target_marker_index)

    elif game_state == config.STATE_PLAYING_FREE_FLY or game_state == config.STATE_DELIVERY_PLAYING:
        for wingman in wingmen_group:
            wingman.update(cam_x, cam_y, player, 0, game_state)
            
        if game_state == config.STATE_DELIVERY_PLAYING:
            for runway_sprite in delivery_runways_group: runway_sprite.update(cam_x, cam_y)
            for cp_sprite in delivery_checkpoints_group:
                is_active = (delivery_active_target_object == cp_sprite)
                cp_sprite.update(cam_x, cam_y, is_active)

            wingman_was_actually_unlocked_this_turn = False
            
            if delivery_active_target_object:
                dist_to_target = math.hypot(player.world_x - delivery_active_target_object.world_pos.x,
                                            player.world_y - delivery_active_target_object.world_pos.y)

                if isinstance(delivery_active_target_object, DeliveryCheckpoint):
                    if dist_to_target < delivery_active_target_object.interaction_radius:
                        delivery_current_checkpoint_index += 1
                        _set_next_delivery_target()
                
                elif isinstance(delivery_active_target_object, Runway) and delivery_active_target_object.is_destination: # Check if it's specifically the destination runway
                    is_low_enough = player.height <= config.DELIVERY_LANDING_MAX_HEIGHT_ABOVE_GROUND
                    is_slow_enough = player.speed <= config.DELIVERY_LANDING_MAX_SPEED
                    if dist_to_target < delivery_active_target_object.interaction_radius and is_low_enough and is_slow_enough:
                        successful_deliveries_count += 1
                        current_level += 1
                        if successful_deliveries_count > high_scores["max_deliveries_completed"]:
                            high_scores["max_deliveries_completed"] = successful_deliveries_count

                        if config.DELIVERIES_TO_UNLOCK_WINGMAN > 0 and \
                           successful_deliveries_count % config.DELIVERIES_TO_UNLOCK_WINGMAN == 0 and \
                           unlocked_wingmen_count < config.MAX_WINGMEN:
                            unlocked_wingmen_count += 1
                            wingman_was_actually_unlocked_this_turn = True
                        
                        game_state = config.STATE_DELIVERY_COMPLETE
                        time_taken_for_level = (pygame.time.get_ticks() - level_timer_start_ticks) / 1000.0
    
    elif game_state == config.STATE_DOGFIGHT_PLAYING:
        for enemy in dogfight_enemies_group:
            enemy.update(cam_x, cam_y, player, 0, game_state, bullets_group, all_world_sprites)
        for bullet in bullets_group:
            if bullet.owner == player:
                enemies_hit = pygame.sprite.spritecollide(bullet, dogfight_enemies_group, False, pygame.sprite.collide_circle)
                for enemy_hit in enemies_hit:
                    bullet.kill()
                    if enemy_hit.take_damage(config.BULLET_DAMAGE):
                        dogfight_enemies_defeated_this_round += 1
            else:
                if pygame.sprite.collide_circle(bullet, player):
                    bullet.kill()
                    if player.take_damage(config.BULLET_DAMAGE):
                        game_state = config.STATE_DOGFIGHT_GAME_OVER_CONTINUE
                        final_score = dogfight_current_round
                        break
        if game_state == config.STATE_DOGFIGHT_GAME_OVER_CONTINUE: pass
        elif dogfight_enemies_defeated_this_round >= dogfight_enemies_to_spawn_this_round:
            game_state = config.STATE_DOGFIGHT_ROUND_COMPLETE
            time_taken_for_level = (pygame.time.get_ticks() - level_timer_start_ticks) / 1000.0

    for thermal_sprite in thermals_group: thermal_sprite.update(cam_x, cam_y)
    thermal_spawn_timer += 1
    if thermal_spawn_timer >= current_thermal_spawn_rate:
        thermal_spawn_timer = 0
        spawn_world_x = cam_x + random.randint(-config.THERMAL_SPAWN_AREA_WIDTH // 2, config.THERMAL_SPAWN_AREA_WIDTH // 2)
        spawn_world_y = cam_y + random.randint(-config.THERMAL_SPAWN_AREA_HEIGHT // 2, config.THERMAL_SPAWN_AREA_HEIGHT // 2)
        if random.random() < config.LAND_TYPE_THERMAL_PROBABILITY.get(get_land_type_at_world_pos(spawn_world_x, spawn_world_y, current_map_offset_x, current_map_offset_y, tile_type_cache), 0.0):
            new_thermal = Thermal((spawn_world_x, spawn_world_y), config.game_difficulty)
            all_world_sprites.add(new_thermal); thermals_group.add(new_thermal)

    foreground_clouds_group.update()
    if len(foreground_clouds_group) < config.NUM_FOREGROUND_CLOUDS:
        foreground_clouds_group.add(ForegroundCloud())

    for thermal in thermals_group:
        if math.hypot(player.world_x - thermal.world_pos.x, player.world_y - thermal.world_pos.y) < thermal.radius + (player.collision_radius * 0.5):
            player.apply_lift_from_thermal(thermal.lift_power, config.game_difficulty)

    if game_state == config.STATE_PLAYING_FREE_FLY and player.height >= config.TARGET_HEIGHT_PER_LEVEL * current_level:
        game_state = config.STATE_TARGET_REACHED_OPTIONS
        level_end_ticks = pygame.time.get_ticks()
        time_taken_for_level = (level_end_ticks - level_timer_start_ticks) / 1000.0
        wingman_was_actually_unlocked_this_turn = False
        if unlocked_wingmen_count < config.MAX_WINGMEN:
            unlocked_wingmen_count += 1
        spawn_wingmen()

    if player.height <= 0 and game_state not in [config.STATE_DOGFIGHT_GAME_OVER_CONTINUE, config.STATE_DELIVERY_COMPLETE]:
        if config.current_game_mode == config.MODE_DELIVERY and game_state != config.STATE_DELIVERY_COMPLETE:
            final_score = successful_deliveries_count
        elif config.current_game_mode == config.MODE_FREE_FLY:
            session_duration = (pygame.time.get_ticks() - current_session_flight_start_ticks) / 1000.0
            if session_duration > high_scores["longest_flight_time_free_fly"]:
                high_scores["longest_flight_time_free_fly"] = session_duration
            final_score = player.height
        player.height = 0
        game_state = config.STATE_GAME_OVER
    return cam_x, cam_y