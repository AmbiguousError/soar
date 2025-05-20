# map_generation.py
# Handles procedural map generation and drawing.

import pygame
import math
import random
import config # Import constants

map_tile_random_generator = random.Random() # For general tile noise
_river_param_random = random.Random() # Specific generator for river parameters
MAJOR_RIVERS_PARAMS = [] 

def regenerate_river_parameters(seed_value=None): # Accept an optional seed
    global MAJOR_RIVERS_PARAMS # _river_param_random is already in module scope
    
    if seed_value is not None:
        _river_param_random.seed(seed_value) # Seed the internal generator
    
    MAJOR_RIVERS_PARAMS = [] # Clear previous params
    for _ in range(config.NUM_MAJOR_RIVERS):
        start_tile_x = _river_param_random.uniform(-config.RACE_COURSE_AREA_HALFWIDTH / config.TILE_SIZE / 3, 
                                                 config.RACE_COURSE_AREA_HALFWIDTH / config.TILE_SIZE / 3)
        start_tile_y = _river_param_random.uniform(-config.RACE_COURSE_AREA_HALFWIDTH / config.TILE_SIZE / 3, 
                                                 config.RACE_COURSE_AREA_HALFWIDTH / config.TILE_SIZE / 3)
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

def get_land_type_at_world_pos(world_x, world_y, current_map_offset_x_param, current_map_offset_y_param, tile_type_cache_param):
    unique_tile_x = math.floor((world_x + current_map_offset_x_param) / config.TILE_SIZE)
    unique_tile_y = math.floor((world_y + current_map_offset_y_param) / config.TILE_SIZE)
    cache_key = (unique_tile_x, unique_tile_y)
    if cache_key in tile_type_cache_param:
        return tile_type_cache_param[cache_key]
    
    e_continent = get_seeded_random_value_direct(unique_tile_x, unique_tile_y, config.ELEVATION_CONTINENT_SCALE, config.P_CONT)
    e_mountain  = get_seeded_random_value_direct(unique_tile_x, unique_tile_y, config.ELEVATION_MOUNTAIN_SCALE, config.P_MNT)
    e_hill      = get_seeded_random_value_direct(unique_tile_x, unique_tile_y, config.ELEVATION_HILL_SCALE, config.P_HILL)
    elevation = math.pow(0.50 * e_continent + 0.35 * e_mountain + 0.15 * e_hill, 1.8)
    elevation = min(max(elevation, 0.0), 1.0) 

    m_primary   = get_seeded_random_value_direct(unique_tile_x, unique_tile_y, config.MOISTURE_PRIMARY_SCALE, config.P_MOIST_P)
    m_secondary = get_seeded_random_value_direct(unique_tile_x, unique_tile_y, config.MOISTURE_SECONDARY_SCALE, config.P_MOIST_S)
    moisture = math.pow(0.7 * m_primary + 0.3 * m_secondary, 1.2)
    moisture = min(max(moisture, 0.0), 1.0) 
    
    final_type = config.LAND_TYPE_PLAINS 
    
    # Define thresholds (ensure these are in config.py or defined if not)
    DEEP_WATER_THRESH = getattr(config, "DEEP_WATER_THRESH", 0.18)
    SHALLOW_WATER_THRESH = getattr(config, "SHALLOW_WATER_THRESH", 0.22)
    BEACH_THRESH = getattr(config, "BEACH_THRESH", 0.24)
    MOUNTAIN_PEAK_THRESH = getattr(config, "MOUNTAIN_PEAK_THRESH", 0.75)
    MOUNTAIN_BASE_THRESH = getattr(config, "MOUNTAIN_BASE_THRESH", 0.60)
    DESERT_THRESH = getattr(config, "DESERT_THRESH", 0.20)
    GRASSLAND_THRESH = getattr(config, "GRASSLAND_THRESH", 0.40)
    TEMPERATE_FOREST_THRESH = getattr(config, "TEMPERATE_FOREST_THRESH", 0.65)

    if elevation < DEEP_WATER_THRESH: final_type = config.LAND_TYPE_WATER_DEEP
    elif elevation < SHALLOW_WATER_THRESH: final_type = config.LAND_TYPE_WATER_SHALLOW
    elif elevation < BEACH_THRESH: final_type = config.LAND_TYPE_SAND_DESERT if moisture < DESERT_THRESH * 1.2 else config.LAND_TYPE_SAND_BEACH
    elif elevation > MOUNTAIN_PEAK_THRESH: final_type = config.LAND_TYPE_MOUNTAIN_PEAK
    elif elevation > MOUNTAIN_BASE_THRESH: final_type = config.LAND_TYPE_MOUNTAIN_BASE
    else: 
        if moisture < DESERT_THRESH: final_type = config.LAND_TYPE_SAND_DESERT
        elif moisture < GRASSLAND_THRESH: final_type = config.LAND_TYPE_GRASSLAND
        elif moisture < TEMPERATE_FOREST_THRESH: final_type = config.LAND_TYPE_PLAINS
        else: final_type = config.LAND_TYPE_FOREST_DENSE if moisture > 0.8 and elevation < MOUNTAIN_BASE_THRESH * 0.9 else config.LAND_TYPE_FOREST_TEMPERATE

    can_have_river = final_type not in (config.LAND_TYPE_MOUNTAIN_PEAK, config.LAND_TYPE_WATER_DEEP) and \
                     not (final_type == config.LAND_TYPE_SAND_DESERT and moisture < DESERT_THRESH * 0.75)
    if can_have_river:
        for params in MAJOR_RIVERS_PARAMS: 
            if params["orientation"] == 'horizontal':
                river_center_y_tile = params["amplitude"] * math.sin((unique_tile_x / params["wavelength"]) * 2 * math.pi + params["phase_offset"]) + params["base_y_offset"]
                if abs(unique_tile_y - river_center_y_tile) < params["width"]:
                    final_type = config.LAND_TYPE_RIVER
                    break
            else: 
                river_center_x_tile = params["amplitude"] * math.sin((unique_tile_y / params["wavelength"]) * 2 * math.pi + params["phase_offset"]) + params["base_x_offset"]
                if abs(unique_tile_x - river_center_x_tile) < params["width"]:
                    final_type = config.LAND_TYPE_RIVER
                    break
    
    tile_type_cache_param[cache_key] = final_type
    return final_type

def draw_endless_map(surface, cam_x, cam_y, current_map_offset_x_param, current_map_offset_y_param, tile_type_cache_param):
    start_world_tile_x_coord = math.floor(cam_x / config.TILE_SIZE) * config.TILE_SIZE
    start_world_tile_y_coord = math.floor(cam_y / config.TILE_SIZE) * config.TILE_SIZE
    num_tiles_x = config.SCREEN_WIDTH // config.TILE_SIZE + 2
    num_tiles_y = config.SCREEN_HEIGHT // config.TILE_SIZE + 2

    for i in range(num_tiles_y): 
        for j in range(num_tiles_x): 
            current_tile_world_x = start_world_tile_x_coord + j * config.TILE_SIZE
            current_tile_world_y = start_world_tile_y_coord + i * config.TILE_SIZE
            tile_screen_x = current_tile_world_x - cam_x
            tile_screen_y = current_tile_world_y - cam_y
            tile_type = get_land_type_at_world_pos(current_tile_world_x, current_tile_world_y, current_map_offset_x_param, current_map_offset_y_param, tile_type_cache_param)
            color = config.LAND_TYPE_COLORS.get(tile_type, config.PASTEL_BLACK) 
            pygame.draw.rect(surface, color, (tile_screen_x, tile_screen_y, config.TILE_SIZE, config.TILE_SIZE))
            if config.MAP_TILE_OUTLINE_WIDTH > 0:
                pygame.draw.rect(surface, config.MAP_TILE_OUTLINE_COLOR, (tile_screen_x, tile_screen_y, config.TILE_SIZE, config.TILE_SIZE), config.MAP_TILE_OUTLINE_WIDTH)
