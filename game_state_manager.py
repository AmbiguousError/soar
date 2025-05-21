# game_state_manager.py
# Manages game state, global variables, and core logic functions.

import pygame
import math
import random
import config
from sprites import PlayerGlider, AIGlider, Thermal, RaceMarker, ForegroundCloud, Bullet, Runway # Added Runway
from map_generation import regenerate_river_parameters, get_land_type_at_world_pos
from ui import Minimap

# --- Game Variables (managed by this module) ---
player = PlayerGlider()
ai_gliders = pygame.sprite.Group() # For race AI
wingmen_group = pygame.sprite.Group() # For Free Fly & Delivery wingmen
dogfight_enemies_group = pygame.sprite.Group() # For Dogfight AI
all_world_sprites = pygame.sprite.Group() # Player is not in this, drawn separately
thermals_group = pygame.sprite.Group()
foreground_clouds_group = pygame.sprite.Group()
bullets_group = pygame.sprite.Group() # For all bullets
delivery_runways_group = pygame.sprite.Group() # For Delivery mode runways

game_state = config.STATE_START_SCREEN
current_level = 1 # Used for Free Fly level and Dogfight round, and Delivery mission count
level_timer_start_ticks = 0
time_taken_for_level = 0.0
current_thermal_spawn_rate = config.BASE_THERMAL_SPAWN_RATE
thermal_spawn_timer = 0
final_score = 0
unlocked_wingmen_count = 0 # Unlocked across modes
wingman_was_actually_unlocked_this_turn = False # New flag

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
successful_deliveries_count = 0 # Current session deliveries

game_state_before_pause = None
pause_start_ticks = 0
current_session_flight_start_ticks = 0

# Dogfight specific variables
dogfight_current_round = 1
dogfight_enemies_to_spawn_this_round = 0
dogfight_enemies_defeated_this_round = 0

minimap = Minimap(config.MINIMAP_WIDTH, config.MINIMAP_HEIGHT, config.MINIMAP_MARGIN)

# --- Core Game Logic Functions ---
def generate_race_course(num_markers=8):
    global race_course_markers, all_world_sprites
    race_course_markers.clear()
    for sprite in list(all_world_sprites): # Clear only race markers
        if isinstance(sprite, RaceMarker):
            sprite.kill()
    for i in range(num_markers):
        marker = RaceMarker(random.uniform(-config.RACE_COURSE_AREA_HALFWIDTH, config.RACE_COURSE_AREA_HALFWIDTH),
                            random.uniform(-config.RACE_COURSE_AREA_HALFWIDTH, config.RACE_COURSE_AREA_HALFWIDTH), i + 1)
        race_course_markers.append(marker)
        all_world_sprites.add(marker)

def find_suitable_runway_location(existing_locations, map_offset_x, map_offset_y, cache):
    """Finds a random suitable location for a runway."""
    for _ in range(config.RUNWAY_MAX_PLACEMENT_ATTEMPTS):
        rx = random.uniform(-config.RACE_COURSE_AREA_HALFWIDTH * 0.8, config.RACE_COURSE_AREA_HALFWIDTH * 0.8)
        ry = random.uniform(-config.RACE_COURSE_AREA_HALFWIDTH * 0.8, config.RACE_COURSE_AREA_HALFWIDTH * 0.8)

        land_type = get_land_type_at_world_pos(rx, ry, map_offset_x, map_offset_y, cache)

        too_close = False
        if land_type in config.RUNWAY_SUITABLE_LAND_TYPES:
            for loc in existing_locations:
                if math.hypot(rx - loc[0], ry - loc[1]) < config.RUNWAY_MIN_DISTANCE_APART:
                    too_close = True
                    break
            if not too_close:
                return rx, ry
    return None # Could not find a suitable spot

def setup_delivery_mission():
    global delivery_start_runway, delivery_destination_runway, delivery_runways_group, all_world_sprites
    global player, game_state, current_map_offset_x, current_map_offset_y, tile_type_cache
    global level_timer_start_ticks, wingman_was_actually_unlocked_this_turn # Make sure this is global if modified

    # Clear previous runways
    for runway_sprite in delivery_runways_group:
        runway_sprite.kill()
    delivery_runways_group.empty()
    delivery_start_runway = None
    delivery_destination_runway = None
    wingman_was_actually_unlocked_this_turn = False # Reset for new mission

    # Find start runway location
    start_loc = find_suitable_runway_location([], current_map_offset_x, current_map_offset_y, tile_type_cache)
    if not start_loc:
        print("Error: Could not place start runway for delivery mission.")
        reset_to_main_menu() # Fallback
        return

    delivery_start_runway = Runway(start_loc[0], start_loc[1], is_start_runway=True)
    all_world_sprites.add(delivery_start_runway)
    delivery_runways_group.add(delivery_start_runway)

    # Find destination runway location
    dest_loc = find_suitable_runway_location([start_loc], current_map_offset_x, current_map_offset_y, tile_type_cache)
    if not dest_loc:
        print("Error: Could not place destination runway for delivery mission.")
        reset_to_main_menu() # Fallback
        return

    delivery_destination_runway = Runway(dest_loc[0], dest_loc[1], is_destination_runway=True)
    all_world_sprites.add(delivery_destination_runway)
    delivery_runways_group.add(delivery_destination_runway)

    player.current_delivery_destination_runway = delivery_destination_runway

    # Position player at start runway
    player_start_height = config.DELIVERY_START_HEIGHT_OFFSET
    player_start_speed = config.INITIAL_SPEED * config.DELIVERY_START_SPEED_FACTOR
    # Optional: Set player heading towards destination initially, or random takeoff
    dx = delivery_destination_runway.world_pos.x - delivery_start_runway.world_pos.x
    dy = delivery_destination_runway.world_pos.y - delivery_start_runway.world_pos.y
    initial_heading = math.degrees(math.atan2(dy, dx))

    player.reset(start_height=player_start_height,
                 start_x=delivery_start_runway.world_pos.x,
                 start_y=delivery_start_runway.world_pos.y,
                 start_speed=player_start_speed,
                 start_heading=initial_heading)

    level_timer_start_ticks = pygame.time.get_ticks() # Timer for the delivery attempt
    game_state = config.STATE_DELIVERY_PLAYING
    spawn_wingmen() # Spawn any unlocked wingmen

def generate_new_wind():
    wind_angle_rad = random.uniform(0, 2 * math.pi)
    wind_strength = random.uniform(0.05, config.MAX_WIND_STRENGTH)
    config.current_wind_speed_x = wind_strength * math.cos(wind_angle_rad)
    config.current_wind_speed_y = wind_strength * math.sin(wind_angle_rad)

def spawn_wingmen():
    global wingmen_group, all_world_sprites, unlocked_wingmen_count, player
    wingmen_group.empty()
    for sprite in list(all_world_sprites): # Remove old wingmen
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
        body_color, wing_color = config.AI_GLIDER_COLORS_LIST[(config.NUM_AI_OPPONENTS + i + 1) % len(config.AI_GLIDER_COLORS_LIST)] # Offset color index
        profile = {"speed_factor": random.uniform(0.85, 1.05), "turn_factor": random.uniform(0.8, 1.1), "altitude_offset": random.uniform(-40, 10)}
        wingman = AIGlider(start_x, start_y, body_color, wing_color, profile, ai_mode="wingman", player_ref=player)
        wingmen_group.add(wingman); all_world_sprites.add(wingman)

def start_dogfight_round(round_number):
    global dogfight_current_round, dogfight_enemies_to_spawn_this_round, dogfight_enemies_defeated_this_round
    global dogfight_enemies_group, all_world_sprites, player, game_state

    dogfight_current_round = round_number
    dogfight_enemies_defeated_this_round = 0

    for enemy in dogfight_enemies_group: # Clear previous enemies
        enemy.kill()
    dogfight_enemies_group.empty()

    dogfight_enemies_to_spawn_this_round = min(config.DOGFIGHT_INITIAL_ENEMIES + (dogfight_current_round - 1) * config.DOGFIGHT_ENEMIES_PER_ROUND_INCREASE,
                                               config.DOGFIGHT_MAX_ENEMIES_ON_SCREEN)

    player.health = player.max_health # Replenish player health

    for i in range(dogfight_enemies_to_spawn_this_round):
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(config.SCREEN_WIDTH * 0.6, config.SCREEN_WIDTH * 0.9)
        start_x = player.world_x + distance * math.cos(angle)
        start_y = player.world_y + distance * math.sin(angle)

        body_color, wing_color = config.AI_GLIDER_COLORS_LIST[i % len(config.AI_GLIDER_COLORS_LIST)]
        profile = {
            "speed_factor": random.uniform(0.8, 1.1),
            "turn_factor": random.uniform(0.9, 1.2),
            "altitude_offset": random.uniform(-50, 50)
        }
        enemy = AIGlider(start_x, start_y, body_color, wing_color, profile, ai_mode="dogfight_enemy", player_ref=player)
        dogfight_enemies_group.add(enemy)
        all_world_sprites.add(enemy)

    game_state = config.STATE_DOGFIGHT_PLAYING


def start_new_level(level_param, continue_map_from_race=False):
    global current_level, level_timer_start_ticks, current_thermal_spawn_rate, thermal_spawn_timer, game_state
    global current_map_offset_x, current_map_offset_y, total_race_laps, ai_gliders, tile_type_cache
    global player_race_lap_times, current_session_flight_start_ticks, race_course_markers, dogfight_current_round
    global delivery_runways_group, delivery_start_runway, delivery_destination_runway, wingman_was_actually_unlocked_this_turn

    level_timer_start_ticks = pygame.time.get_ticks()
    wingman_was_actually_unlocked_this_turn = False # Reset for new level/mode start

    if not continue_map_from_race: # New map unless specified
        current_map_offset_x = random.randint(-200000, 200000)
        current_map_offset_y = random.randint(-200000, 200000)
        tile_type_cache.clear()
        regenerate_river_parameters(current_level + pygame.time.get_ticks()) # Use global current_level here
        generate_new_wind()

    # Clear common sprites
    thermals_group.empty()
    for sprite in list(all_world_sprites): # Clear relevant sprites from all_world_sprites
        if isinstance(sprite, (Thermal, AIGlider, RaceMarker, Bullet, Runway)):
            sprite.kill()
    bullets_group.empty()
    race_course_markers.clear()
    ai_gliders.empty()
    wingmen_group.empty() # Wingmen are respawned based on mode
    dogfight_enemies_group.empty()
    delivery_runways_group.empty() # Clear runways specifically

    foreground_clouds_group.empty()
    for i in range(config.NUM_FOREGROUND_CLOUDS):
        foreground_clouds_group.add(ForegroundCloud(initial_distribution=True, index=i))

    # Player reset is mode-dependent for start position/speed
    current_session_flight_start_ticks = pygame.time.get_ticks() # For high scores like longest flight
    player_race_lap_times.clear()


    if config.current_game_mode == config.MODE_FREE_FLY:
        current_level = level_param # Set global current_level
        player.reset(start_height=config.INITIAL_HEIGHT) # Standard reset
        current_thermal_spawn_rate = config.BASE_THERMAL_SPAWN_RATE + (config.THERMAL_SPAWN_RATE_INCREASE_PER_LEVEL * (current_level - 1))
        # Difficulty adjustment for thermals
        if config.game_difficulty == config.DIFFICULTY_NOOB: current_thermal_spawn_rate = max(20, current_thermal_spawn_rate // 2)
        elif config.game_difficulty == config.DIFFICULTY_EASY: current_thermal_spawn_rate = max(30, int(current_thermal_spawn_rate * 0.75))
        thermal_spawn_timer = 0
        spawn_wingmen()
        game_state = config.STATE_PLAYING_FREE_FLY
    elif config.current_game_mode == config.MODE_RACE:
        total_race_laps = level_param
        player.reset(start_height=config.INITIAL_HEIGHT) # Standard reset for race
        player.current_lap_start_ticks = pygame.time.get_ticks()
        generate_race_course()
        for i in range(config.NUM_AI_OPPONENTS): # Spawn AI racers
            angle_offset = math.pi + (i - config.NUM_AI_OPPONENTS / 2.0) * (math.pi / 6)
            dist_offset = 100 + i * 40
            ai_start_x = player.world_x + dist_offset * math.cos(angle_offset + math.radians(player.heading))
            ai_start_y = player.world_y + dist_offset * math.sin(angle_offset + math.radians(player.heading))
            body_color, wing_color = config.AI_GLIDER_COLORS_LIST[i % len(config.AI_GLIDER_COLORS_LIST)]
            profile = {"speed_factor": random.uniform(0.9, 1.1), "turn_factor": random.uniform(0.85, 1.15), "altitude_offset": random.uniform(-20, 20)}
            new_ai = AIGlider(ai_start_x, ai_start_y, body_color, wing_color, profile, ai_mode="race")
            ai_gliders.add(new_ai); all_world_sprites.add(new_ai)
        current_thermal_spawn_rate = config.BASE_THERMAL_SPAWN_RATE * 1.5 # More thermals in race
        if config.game_difficulty == config.DIFFICULTY_NOOB: current_thermal_spawn_rate = max(30, int(current_thermal_spawn_rate * 0.7))
        thermal_spawn_timer = 0
        game_state = config.STATE_RACE_PLAYING
    elif config.current_game_mode == config.MODE_DOGFIGHT:
        dogfight_current_round = level_param # Use level_param as starting round
        player.reset(start_height=config.INITIAL_HEIGHT) # Standard reset for dogfight
        start_dogfight_round(dogfight_current_round) # This sets game_state
    elif config.current_game_mode == config.MODE_DELIVERY:
        current_level = level_param # Tracks current delivery mission number for display, set global current_level
        # Player reset is handled within setup_delivery_mission
        setup_delivery_mission() # This sets game_state and player position
        # Thermals for delivery mode (can be adjusted)
        current_thermal_spawn_rate = config.BASE_THERMAL_SPAWN_RATE
        if config.game_difficulty == config.DIFFICULTY_NOOB: current_thermal_spawn_rate = max(20, current_thermal_spawn_rate // 2)
        elif config.game_difficulty == config.DIFFICULTY_EASY: current_thermal_spawn_rate = max(30, int(current_thermal_spawn_rate * 0.75))
        thermal_spawn_timer = 0
        # Wingmen are spawned in setup_delivery_mission via spawn_wingmen()


def reset_to_main_menu():
    global game_state, current_level, final_score
    global selected_difficulty_option, selected_mode_option, selected_laps_option
    global player_race_lap_times, race_course_markers, unlocked_wingmen_count
    global dogfight_current_round, dogfight_enemies_defeated_this_round, dogfight_enemies_to_spawn_this_round
    global delivery_start_runway, delivery_destination_runway, delivery_runways_group, successful_deliveries_count
    global wingman_was_actually_unlocked_this_turn

    player.reset() # Generic reset
    thermals_group.empty()
    all_world_sprites.empty() # Clears AI, markers, runways etc.
    race_course_markers.clear()
    ai_gliders.empty()
    wingmen_group.empty()
    dogfight_enemies_group.empty()
    bullets_group.empty()
    delivery_runways_group.empty()
    foreground_clouds_group.empty()
    tile_type_cache.clear()
    player_race_lap_times.clear()

    # Reset mode-specific progress trackers
    unlocked_wingmen_count = 0 # Reset global wingman count on full menu reset
    successful_deliveries_count = 0
    dogfight_current_round = 1
    dogfight_enemies_defeated_this_round = 0
    dogfight_enemies_to_spawn_this_round = 0
    delivery_start_runway = None
    delivery_destination_runway = None
    wingman_was_actually_unlocked_this_turn = False


    config.current_wind_speed_x = -0.2
    config.current_wind_speed_y = 0.05
    for i in range(config.NUM_FOREGROUND_CLOUDS):
        foreground_clouds_group.add(ForegroundCloud(initial_distribution=True, index=i))

    current_level = 1 # Reset global current_level
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

    game_data_for_player = {
        "current_wind_speed_x": config.current_wind_speed_x,
        "current_wind_speed_y": config.current_wind_speed_y,
        "game_state": game_state,
        "race_course_markers": race_course_markers, # For player's race logic
        "total_race_laps": total_race_laps,
        "level_timer_start_ticks": level_timer_start_ticks,
        "game_difficulty": config.game_difficulty,
        "high_scores": high_scores,
        "player_race_lap_times": player_race_lap_times,
        "current_game_mode": config.current_game_mode,
        "time_taken_for_level": time_taken_for_level
    }

    new_gs_from_player, ttf_update = player.update(keys, game_data_for_player, bullets_group, all_world_sprites)

    if new_gs_from_player != game_state: game_state = new_gs_from_player # Player update can change game state (e.g., race complete)
    time_taken_for_level = ttf_update

    cam_x = player.world_x - config.SCREEN_WIDTH // 2
    cam_y = player.world_y - config.SCREEN_HEIGHT // 2

    bullets_group.update(cam_x, cam_y) # Update all bullets

    # Mode-specific AI and object updates
    if game_state == config.STATE_RACE_PLAYING:
        for ai in ai_gliders:
            ai.update(cam_x, cam_y, race_course_markers, total_race_laps, game_state)
        collided_ais = pygame.sprite.spritecollide(player, ai_gliders, False, pygame.sprite.collide_circle)
        for ai_hit in collided_ais: player.apply_collision_effect(); ai_hit.apply_collision_effect()
        ai_list = list(ai_gliders); [(ai1.apply_collision_effect(),ai2.apply_collision_effect()) for i in range(len(ai_list)) for j in range(i+1,len(ai_list)) if(ai1:=ai_list[i],ai2:=ai_list[j],((ai1.world_x-ai2.world_x)**2+(ai1.world_y-ai2.world_y)**2)<(ai1.collision_radius+ai2.collision_radius)**2)]
        for i, marker in enumerate(race_course_markers): # Update marker appearance
            marker.update(cam_x, cam_y, i == player.current_target_marker_index)

    elif game_state == config.STATE_PLAYING_FREE_FLY or game_state == config.STATE_DELIVERY_PLAYING: # Wingmen active in these modes
        for wingman in wingmen_group:
            wingman.update(cam_x, cam_y, player, 0, game_state) # Wingmen follow player
        if game_state == config.STATE_DELIVERY_PLAYING:
            for runway_sprite in delivery_runways_group: # Update runway positions
                runway_sprite.update(cam_x, cam_y)
            
            wingman_was_actually_unlocked_this_turn = False # Reset before check
            # Landing Check for Delivery
            if delivery_destination_runway:
                dist_to_dest = math.hypot(player.world_x - delivery_destination_runway.world_pos.x,
                                          player.world_y - delivery_destination_runway.world_pos.y)
                is_low_enough = player.height <= config.DELIVERY_LANDING_MAX_HEIGHT_ABOVE_GROUND
                is_slow_enough = player.speed <= config.DELIVERY_LANDING_MAX_SPEED

                if dist_to_dest < delivery_destination_runway.interaction_radius and is_low_enough and is_slow_enough:
                    successful_deliveries_count += 1
                    current_level +=1 # Increment mission number for display (NOW USES GLOBAL current_level)
                    if successful_deliveries_count > high_scores["max_deliveries_completed"]:
                        high_scores["max_deliveries_completed"] = successful_deliveries_count

                    # Unlock wingman
                    if config.DELIVERIES_TO_UNLOCK_WINGMAN > 0 and \
                       successful_deliveries_count % config.DELIVERIES_TO_UNLOCK_WINGMAN == 0 and \
                       unlocked_wingmen_count < config.MAX_WINGMEN:
                        unlocked_wingmen_count += 1
                        wingman_was_actually_unlocked_this_turn = True # Set flag
                    # spawn_wingmen() # Spawn immediately or wait for next mission setup? Let's do it on next setup.

                    game_state = config.STATE_DELIVERY_COMPLETE
                    time_taken_for_level = (pygame.time.get_ticks() - level_timer_start_ticks) / 1000.0


    elif game_state == config.STATE_DOGFIGHT_PLAYING:
        for enemy in dogfight_enemies_group:
            enemy.update(cam_x, cam_y, player, 0, game_state, bullets_group, all_world_sprites)
        # Bullet Collisions (Dogfight)
        for bullet in bullets_group:
            if bullet.owner == player: # Player bullets hitting AI
                enemies_hit = pygame.sprite.spritecollide(bullet, dogfight_enemies_group, False, pygame.sprite.collide_circle)
                for enemy_hit in enemies_hit:
                    bullet.kill()
                    if enemy_hit.take_damage(config.BULLET_DAMAGE):
                        dogfight_enemies_defeated_this_round += 1
            else: # AI bullets hitting Player
                if pygame.sprite.collide_circle(bullet, player):
                    bullet.kill()
                    if player.take_damage(config.BULLET_DAMAGE):
                        game_state = config.STATE_DOGFIGHT_GAME_OVER_CONTINUE
                        final_score = dogfight_current_round # Score is rounds survived
                        break
        if game_state == config.STATE_DOGFIGHT_GAME_OVER_CONTINUE: pass # Handled in main loop
        elif dogfight_enemies_defeated_this_round >= dogfight_enemies_to_spawn_this_round:
            game_state = config.STATE_DOGFIGHT_ROUND_COMPLETE
            time_taken_for_level = (pygame.time.get_ticks() - level_timer_start_ticks) / 1000.0

    # Common updates for all active play states (thermals, clouds)
    for thermal_sprite in thermals_group:
        thermal_sprite.update(cam_x, cam_y)

    thermal_spawn_timer += 1
    if thermal_spawn_timer >= current_thermal_spawn_rate:
        thermal_spawn_timer = 0
        spawn_world_x = cam_x + random.randint(-config.THERMAL_SPAWN_AREA_WIDTH // 2, config.THERMAL_SPAWN_AREA_WIDTH // 2)
        spawn_world_y = cam_y + random.randint(-config.THERMAL_SPAWN_AREA_HEIGHT // 2, config.THERMAL_SPAWN_AREA_HEIGHT // 2)
        if random.random() < config.LAND_TYPE_THERMAL_PROBABILITY.get(get_land_type_at_world_pos(spawn_world_x, spawn_world_y, current_map_offset_x, current_map_offset_y, tile_type_cache), 0.0):
            new_thermal = Thermal((spawn_world_x, spawn_world_y), config.game_difficulty)
            all_world_sprites.add(new_thermal)
            thermals_group.add(new_thermal)

    foreground_clouds_group.update()
    if len(foreground_clouds_group) < config.NUM_FOREGROUND_CLOUDS:
        foreground_clouds_group.add(ForegroundCloud())

    # Player interaction with thermals
    for thermal in thermals_group:
        if math.hypot(player.world_x - thermal.world_pos.x, player.world_y - thermal.world_pos.y) < thermal.radius + (player.collision_radius * 0.5):
            player.apply_lift_from_thermal(thermal.lift_power, config.game_difficulty)

    # Free Fly goal check
    if game_state == config.STATE_PLAYING_FREE_FLY and player.height >= config.TARGET_HEIGHT_PER_LEVEL * current_level: # Uses global current_level
        game_state = config.STATE_TARGET_REACHED_OPTIONS
        level_end_ticks = pygame.time.get_ticks()
        time_taken_for_level = (level_end_ticks - level_timer_start_ticks) / 1000.0
        
        wingman_was_actually_unlocked_this_turn = False # Reset for Free Fly unlock
        if unlocked_wingmen_count < config.MAX_WINGMEN: # Free fly also unlocks wingmen
            unlocked_wingmen_count += 1
            wingman_was_actually_unlocked_this_turn = True # Though not directly used on this screen in UI
        spawn_wingmen() # Update wingmen based on new count

    # Player crash / Game Over condition (if not already handled by a specific mode's fail state)
    if player.height <= 0 and game_state not in [config.STATE_DOGFIGHT_GAME_OVER_CONTINUE, config.STATE_DELIVERY_COMPLETE]:
        # For Delivery mode, if height <=0 and not at destination, it's a crash.
        if config.current_game_mode == config.MODE_DELIVERY and game_state != config.STATE_DELIVERY_COMPLETE:
            final_score = successful_deliveries_count # Score is number of successful deliveries
        elif config.current_game_mode == config.MODE_FREE_FLY:
            session_duration = (pygame.time.get_ticks() - current_session_flight_start_ticks) / 1000.0
            if session_duration > high_scores["longest_flight_time_free_fly"]:
                high_scores["longest_flight_time_free_fly"] = session_duration
            final_score = player.height # Or current_level for Free Fly
        # Other modes might set final_score differently (e.g., Dogfight sets it on player death)

        player.height = 0 # Ensure height is exactly 0 for game over screen
        game_state = config.STATE_GAME_OVER

    return cam_x, cam_y