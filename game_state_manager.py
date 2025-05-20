# game_state_manager.py
# Manages game state, global variables, and core logic functions.

import pygame
import math
import random
import config
from sprites import PlayerGlider, AIGlider, Thermal, RaceMarker, ForegroundCloud
from map_generation import regenerate_river_parameters, get_land_type_at_world_pos 
from ui import Minimap 

# --- Game Variables (managed by this module) ---
# These are defined at the module level to be accessible via gsm.<variable_name>

game_state = config.STATE_START_SCREEN 

player = PlayerGlider() 
ai_gliders = pygame.sprite.Group() 
wingmen_group = pygame.sprite.Group() # For Free Fly wingmen
all_world_sprites = pygame.sprite.Group() 
thermals_group = pygame.sprite.Group()    
foreground_clouds_group = pygame.sprite.Group() 

current_level = 1
level_timer_start_ticks = 0 
time_taken_for_level = 0.0  
current_thermal_spawn_rate = config.BASE_THERMAL_SPAWN_RATE
thermal_spawn_timer = 0
final_score = 0 
unlocked_wingmen_count = 0

selected_difficulty_option = config.DIFFICULTY_NORMAL 
config.game_difficulty = selected_difficulty_option # Initialize in config

selected_mode_option = config.MODE_FREE_FLY
config.current_game_mode = selected_mode_option # Initialize in config

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
    "best_total_race_times": {} 
}
player_race_lap_times = []
race_course_markers = [] 

game_state_before_pause = None
pause_start_ticks = 0
current_session_flight_start_ticks = 0 

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

def generate_new_wind():
    wind_angle_rad = random.uniform(0, 2 * math.pi)
    wind_strength = random.uniform(0.05, config.MAX_WIND_STRENGTH) 
    config.current_wind_speed_x = wind_strength * math.cos(wind_angle_rad)
    config.current_wind_speed_y = wind_strength * math.sin(wind_angle_rad)

def spawn_wingmen(): # Moved from main.py to here
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
        
        body_color, wing_color = config.AI_GLIDER_COLORS_LIST[(config.NUM_AI_OPPONENTS + i) % len(config.AI_GLIDER_COLORS_LIST)] 
        
        profile = {
            "speed_factor": random.uniform(0.85, 1.05), 
            "turn_factor": random.uniform(0.8, 1.1), 
            "altitude_offset": random.uniform(-40, 10) 
        }
        wingman = AIGlider(start_x, start_y, body_color, wing_color, profile, ai_mode="wingman", player_ref=player)
        wingmen_group.add(wingman)
        all_world_sprites.add(wingman)


def start_new_level(level_param, continue_map_from_race=False): 
    global current_level, level_timer_start_ticks, current_thermal_spawn_rate, thermal_spawn_timer, game_state
    global current_map_offset_x, current_map_offset_y, total_race_laps, ai_gliders, tile_type_cache
    global player_race_lap_times, current_session_flight_start_ticks, race_course_markers
    
    level_timer_start_ticks = pygame.time.get_ticks()
    
    if not continue_map_from_race: 
        current_map_offset_x = random.randint(-200000, 200000)
        current_map_offset_y = random.randint(-200000, 200000)
        tile_type_cache.clear() 
        regenerate_river_parameters(current_level + pygame.time.get_ticks()) 
        generate_new_wind() 
    
    thermals_group.empty()
    for sprite in list(all_world_sprites):
        if isinstance(sprite, (Thermal, AIGlider, RaceMarker)): 
            sprite.kill()
    
    race_course_markers.clear() 
    ai_gliders.empty() 
    wingmen_group.empty() 

    foreground_clouds_group.empty() 
    for i in range(config.NUM_FOREGROUND_CLOUDS):
        foreground_clouds_group.add(ForegroundCloud(initial_distribution=True, index=i))
    
    player.reset(start_height=config.INITIAL_HEIGHT) 
    player.current_lap_start_ticks = pygame.time.get_ticks() 
    current_session_flight_start_ticks = pygame.time.get_ticks()
    player_race_lap_times.clear()

    if config.current_game_mode == config.MODE_FREE_FLY: 
        current_level = level_param
        current_thermal_spawn_rate = config.BASE_THERMAL_SPAWN_RATE + (config.THERMAL_SPAWN_RATE_INCREASE_PER_LEVEL * (current_level - 1))
        if config.game_difficulty == config.DIFFICULTY_NOOB: 
            current_thermal_spawn_rate = max(20, current_thermal_spawn_rate // 2)
        elif config.game_difficulty == config.DIFFICULTY_EASY:
            current_thermal_spawn_rate = max(30, int(current_thermal_spawn_rate * 0.75))
        thermal_spawn_timer = 0
        spawn_wingmen() 
        game_state = config.STATE_PLAYING_FREE_FLY
    elif config.current_game_mode == config.MODE_RACE:
        total_race_laps = level_param 
        generate_race_course() 
        for i in range(config.NUM_AI_OPPONENTS):
            angle_offset = math.pi + (i - config.NUM_AI_OPPONENTS / 2.0) * (math.pi / 6) 
            dist_offset = 100 + i * 40 
            
            ai_start_x = player.world_x + dist_offset * math.cos(angle_offset + math.radians(player.heading)) 
            ai_start_y = player.world_y + dist_offset * math.sin(angle_offset + math.radians(player.heading))

            body_color, wing_color = config.AI_GLIDER_COLORS_LIST[i % len(config.AI_GLIDER_COLORS_LIST)]
            
            profile = {
                "speed_factor": random.uniform(0.9, 1.1), 
                "turn_factor": random.uniform(0.85, 1.15), 
                "altitude_offset": random.uniform(-20, 20) 
            }
            new_ai = AIGlider(ai_start_x, ai_start_y, body_color, wing_color, profile, ai_mode="race")
            ai_gliders.add(new_ai)
            all_world_sprites.add(new_ai) 
        current_thermal_spawn_rate = config.BASE_THERMAL_SPAWN_RATE * 1.5 
        if config.game_difficulty == config.DIFFICULTY_NOOB:
            current_thermal_spawn_rate = max(30, int(current_thermal_spawn_rate * 0.7))
        thermal_spawn_timer = 0
        game_state = config.STATE_RACE_PLAYING

def reset_to_main_menu():
    global game_state, current_level, final_score
    global selected_difficulty_option, selected_mode_option, selected_laps_option
    global player_race_lap_times, race_course_markers, unlocked_wingmen_count
    
    player.reset() 
    thermals_group.empty()
    all_world_sprites.empty()
    race_course_markers.clear() 
    ai_gliders.empty()
    wingmen_group.empty()
    foreground_clouds_group.empty()
    tile_type_cache.clear()
    player_race_lap_times.clear() 
    unlocked_wingmen_count = 0 
    
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
    
    new_gs_from_player, ttf_update = player.update(keys, game_data_for_player)
    
    if new_gs_from_player != game_state:
        game_state = new_gs_from_player
    time_taken_for_level = ttf_update

    cam_x = player.world_x - config.SCREEN_WIDTH // 2
    cam_y = player.world_y - config.SCREEN_HEIGHT // 2
    
    if game_state == config.STATE_RACE_PLAYING: 
        for ai in ai_gliders:
            ai.update(cam_x, cam_y, race_course_markers, total_race_laps, game_state)
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
    elif game_state == config.STATE_PLAYING_FREE_FLY:
        for wingman in wingmen_group:
            wingman.update(cam_x, cam_y, player, 0, game_state) 

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
    
    if game_state == config.STATE_RACE_PLAYING: 
        for i, marker in enumerate(race_course_markers):
            marker.update(cam_x, cam_y, i == player.current_target_marker_index)
    
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
        if unlocked_wingmen_count < config.MAX_WINGMEN:
            unlocked_wingmen_count += 1
        spawn_wingmen() 
    
    if player.height <= 0:
        final_score = player.height 
        player.height = 0
        game_state = config.STATE_GAME_OVER
        if config.current_game_mode == config.MODE_FREE_FLY:
            session_duration = (pygame.time.get_ticks() - current_session_flight_start_ticks) / 1000.0
            if session_duration > high_scores["longest_flight_time_free_fly"]:
                high_scores["longest_flight_time_free_fly"] = session_duration
    
    return cam_x, cam_y
