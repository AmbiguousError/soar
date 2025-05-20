# ui.py
# Handles UI elements, text rendering, and screen drawing functions.

import pygame
import math
import config # Import constants

font_cache = {}
def get_cached_font(font_name, size):
    key = (font_name, size)
    if key not in font_cache:
        if font_name:
            try:
                font_cache[key] = pygame.font.SysFont(font_name, size)
            except pygame.error: 
                font_cache[key] = pygame.font.Font(None, size) 
        else: 
            font_cache[key] = pygame.font.Font(None, size)
    return font_cache[key]

def draw_text(surface, text, size, x, y, color=config.PASTEL_WHITE, font_name=None, center=False, antialias=True, shadow=False, shadow_color=config.PASTEL_DARK_GRAY, shadow_offset=(1,1)):
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

class Minimap:
    def __init__(self, width, height, margin):
        self.width = width
        self.height = height
        self.margin = margin
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.surface.get_rect(topright=(config.SCREEN_WIDTH - self.margin, self.margin + config.HUD_HEIGHT))
        self.world_bounds_view_radius = 3000

    def world_to_minimap(self, world_x, world_y, player_world_x, player_world_y):
        scale = self.width / (2 * self.world_bounds_view_radius)
        rel_x = world_x - player_world_x
        rel_y = world_y - player_world_y
        mini_x = self.width / 2 + rel_x * scale
        mini_y = self.height / 2 + rel_y * scale
        return int(mini_x), int(mini_y)

    def draw(self, surface, player_glider, ai_gliders_list, course_markers):
        self.surface.fill(config.PASTEL_MINIMAP_BACKGROUND)
        player_mini_x, player_mini_y = self.width // 2, self.height // 2
        pygame.draw.circle(self.surface, config.PASTEL_GOLD, (player_mini_x, player_mini_y), 5)
        for ai in ai_gliders_list: 
            ai_mini_x, ai_mini_y = self.world_to_minimap(ai.world_x, ai.world_y, player_glider.world_x, player_glider.world_y)
            if 0 <= ai_mini_x <= self.width and 0 <= ai_mini_y <= self.height:
                 pygame.draw.circle(self.surface, ai.body_color, (ai_mini_x, ai_mini_y), 4) 
        for i, marker_obj in enumerate(course_markers):
            mini_x, mini_y = self.world_to_minimap(marker_obj.world_pos.x, marker_obj.world_pos.y, player_glider.world_x, player_glider.world_y)
            if 0 <= mini_x <= self.width and 0 <= mini_y <= self.height:
                color_to_use = config.PASTEL_MARKER_COLOR 
                if i == player_glider.current_target_marker_index:
                    color_to_use = config.PASTEL_ACTIVE_MARKER_COLOR
                
                pygame.draw.circle(self.surface, color_to_use, (mini_x, mini_y), config.RACE_MARKER_VISUAL_RADIUS_MAP)
                font_obj = get_cached_font(None, 16) 
                text_surf = font_obj.render(str(marker_obj.number), True, config.PASTEL_BLACK)
                text_rect = text_surf.get_rect(center=(mini_x, mini_y))
                self.surface.blit(text_surf, text_rect)
        pygame.draw.rect(self.surface, config.PASTEL_MINIMAP_BORDER, self.surface.get_rect(), 2)
        surface.blit(self.surface, self.rect)

def draw_height_indicator_hud(surface, current_player_height, target_h_for_level, vertical_speed_val, clock_ref, current_game_mode_param):
    indicator_bar_height = config.SCREEN_HEIGHT - config.HUD_HEIGHT - (2 * config.INDICATOR_Y_MARGIN_FROM_HUD)
    indicator_x_pos = config.SCREEN_WIDTH - config.INDICATOR_WIDTH - config.INDICATOR_X_MARGIN
    indicator_y_pos = config.HUD_HEIGHT + config.INDICATOR_Y_MARGIN_FROM_HUD
    pygame.draw.rect(surface, config.PASTEL_INDICATOR_COLOR, (indicator_x_pos, indicator_y_pos, config.INDICATOR_WIDTH, indicator_bar_height))
    
    max_indicator_height_value = target_h_for_level * 1.15 if current_game_mode_param == config.MODE_FREE_FLY else current_player_height + 500
    max_indicator_height_value = max(1, max_indicator_height_value) 
    
    ground_line_y = indicator_y_pos + indicator_bar_height
    pygame.draw.line(surface, config.PASTEL_INDICATOR_GROUND, (indicator_x_pos - 5, ground_line_y), (indicator_x_pos + config.INDICATOR_WIDTH + 5, ground_line_y), 3)
    draw_text(surface, "0m", 14, indicator_x_pos + config.INDICATOR_WIDTH + 8, ground_line_y - 7, config.PASTEL_TEXT_COLOR_HUD, font_name=config.HUD_FONT_NAME)
    
    if current_game_mode_param == config.MODE_FREE_FLY and target_h_for_level > 0:
        target_ratio = min(target_h_for_level / max_indicator_height_value, 1.0) 
        target_marker_y_on_bar = indicator_y_pos + indicator_bar_height * (1 - target_ratio) 
        pygame.draw.line(surface, config.PASTEL_GREEN_TARGET, (indicator_x_pos - 5, target_marker_y_on_bar), (indicator_x_pos + config.INDICATOR_WIDTH + 5, target_marker_y_on_bar), 3)
        draw_text(surface, f"{target_h_for_level}m", 14, indicator_x_pos + config.INDICATOR_WIDTH + 8, target_marker_y_on_bar - 7, config.PASTEL_GREEN_TARGET, font_name=config.HUD_FONT_NAME)
    
    player_marker_y_on_bar = ground_line_y 
    if current_player_height > 0:
        player_marker_y_on_bar = indicator_y_pos + indicator_bar_height * (1 - min(current_player_height / max_indicator_height_value, 1.0))
    player_marker_y_on_bar = max(indicator_y_pos, min(player_marker_y_on_bar, ground_line_y))
    pygame.draw.line(surface, config.PASTEL_GOLD, (indicator_x_pos, player_marker_y_on_bar), (indicator_x_pos + config.INDICATOR_WIDTH, player_marker_y_on_bar), 5)
    
    vsi_text_x = indicator_x_pos - 70
    vsi_arrow_x_center = indicator_x_pos - 10 
    vsi_mps = vertical_speed_val * clock_ref.get_fps() if clock_ref.get_fps() > 0 else vertical_speed_val * 60 
    vsi_color = config.PASTEL_VSI_CLIMB if vsi_mps > 0.5 else (config.PASTEL_VSI_SINK if vsi_mps < -0.5 else config.PASTEL_TEXT_COLOR_HUD)
    draw_text(surface, f"{vsi_mps:+.1f}m/s", 14, vsi_text_x , player_marker_y_on_bar - 7, vsi_color, font_name=config.HUD_FONT_NAME)
    
    if abs(vsi_mps) > 0.5: 
        arrow_points = []
        if vsi_mps > 0: 
            arrow_points = [(vsi_arrow_x_center, player_marker_y_on_bar - config.VSI_ARROW_SIZE), 
                            (vsi_arrow_x_center - config.VSI_ARROW_SIZE // 2, player_marker_y_on_bar), 
                            (vsi_arrow_x_center + config.VSI_ARROW_SIZE // 2, player_marker_y_on_bar)] 
        else: 
            arrow_points = [(vsi_arrow_x_center, player_marker_y_on_bar + config.VSI_ARROW_SIZE), 
                            (vsi_arrow_x_center - config.VSI_ARROW_SIZE // 2, player_marker_y_on_bar), 
                            (vsi_arrow_x_center + config.VSI_ARROW_SIZE // 2, player_marker_y_on_bar)]
        pygame.draw.polygon(surface, vsi_color, arrow_points)
    
    player_height_text_y = player_marker_y_on_bar - 20 
    if player_height_text_y < indicator_y_pos + 5:
        player_height_text_y = player_marker_y_on_bar + 15 
    draw_text(surface, f"{int(current_player_height)}m", 14, vsi_text_x, player_height_text_y, config.PASTEL_GOLD, font_name=config.HUD_FONT_NAME)

def draw_dial(surface, center_x, center_y, radius, hand_angle_degrees, hand_color, dial_color=config.PASTEL_GRAY, border_color=config.PASTEL_TEXT_COLOR_HUD):
    pygame.draw.circle(surface, dial_color, (center_x, center_y), radius)
    pygame.draw.circle(surface, border_color, (center_x, center_y), radius, 1)
    draw_text(surface, "N", config.HUD_FONT_SIZE_SMALL - 6 , center_x, center_y - radius + 7, border_color, font_name=config.HUD_FONT_NAME, center=True)

    hand_angle_rad = math.radians(hand_angle_degrees - 90) 
    hand_end_x = center_x + (radius * 0.8) * math.cos(hand_angle_rad)
    hand_end_y = center_y + (radius * 0.8) * math.sin(hand_angle_rad)
    pygame.draw.line(surface, hand_color, (center_x, center_y), (hand_end_x, hand_end_y), 2)

def draw_weather_vane(surface, wind_x, wind_y, center_x, center_y, radius=22, max_strength_for_scaling=config.MAX_WIND_STRENGTH):
    vane_angle_rad = math.atan2(wind_y, wind_x) + math.pi
    wind_magnitude = math.hypot(wind_x, wind_y)
    arrow_color = config.PASTEL_TEXT_COLOR_HUD
    arrow_thickness = 2
    dial_color = config.PASTEL_GRAY
    border_color = config.PASTEL_TEXT_COLOR_HUD
    
    pygame.draw.circle(surface, dial_color, (center_x, center_y), radius)
    pygame.draw.circle(surface, border_color, (center_x, center_y), radius, 1)
    draw_text(surface, "N", config.HUD_FONT_SIZE_SMALL -6, center_x, center_y - radius + 7, border_color, font_name=config.HUD_FONT_NAME, center=True)

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
    
# --- Screen Drawing Functions ---
def draw_start_screen_content(surface):
    surface.fill(config.PASTEL_DARK_GRAY) 
    
    title_y = config.SCREEN_HEIGHT // 4 - 50
    draw_text(surface, "Pastel Glider", 72, config.SCREEN_WIDTH // 2, title_y, 
              config.PASTEL_PLAINS, font_name=config.HUD_FONT_NAME, center=True, shadow=True, shadow_color=config.PASTEL_BLACK)

    info_y = title_y + 80
    line_spacing = 28
    info_font_size = 22

    draw_text(surface, "Welcome, pilot! Soar through endless skies.", info_font_size, config.SCREEN_WIDTH // 2, info_y, 
              config.PASTEL_LIGHT_GRAY, font_name=config.HUD_FONT_NAME, center=True)
    info_y += line_spacing
    draw_text(surface, "Use thermals to gain altitude and explore.", info_font_size, config.SCREEN_WIDTH // 2, info_y, 
              config.PASTEL_LIGHT_GRAY, font_name=config.HUD_FONT_NAME, center=True)
    info_y += line_spacing * 1.5 

    draw_text(surface, "Game Modes:", info_font_size + 2, config.SCREEN_WIDTH // 2, info_y, 
              config.PASTEL_WHITE, font_name=config.HUD_FONT_NAME, center=True)
    info_y += line_spacing
    draw_text(surface, "- Free Fly: Reach altitude goals & unlock wingmen.", info_font_size, config.SCREEN_WIDTH // 2, info_y, 
              config.PASTEL_LIGHT_GRAY, font_name=config.HUD_FONT_NAME, center=True)
    info_y += line_spacing
    draw_text(surface, "- Race: Compete against AI through challenging courses.", info_font_size, config.SCREEN_WIDTH // 2, info_y, 
              config.PASTEL_LIGHT_GRAY, font_name=config.HUD_FONT_NAME, center=True)
    info_y += line_spacing * 1.5

    draw_text(surface, "Press ENTER to Begin Your Flight", 30, config.SCREEN_WIDTH // 2, info_y + 40, 
              config.PASTEL_GOLD, font_name=config.HUD_FONT_NAME, center=True, shadow=True, shadow_color=config.PASTEL_BLACK)
    
    controls_y = info_y + 100
    draw_text(surface, "Controls: UP/DOWN Arrows for Speed | LEFT/RIGHT Arrows to Bank", 20, config.SCREEN_WIDTH // 2, controls_y, 
              config.PASTEL_WHITE, font_name=config.HUD_FONT_NAME, center=True)


def draw_difficulty_select_screen(surface, selected_option_idx): 
    surface.fill(config.PASTEL_DARK_GRAY)
    draw_text(surface, "Select Difficulty", 56, config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 5, config.PASTEL_GOLD, font_name=config.HUD_FONT_NAME, center=True, shadow=True, shadow_color=config.PASTEL_BLACK)
    option_spacing = 100
    start_y = config.SCREEN_HEIGHT // 2 - option_spacing
    difficulties_display = [ # Updated descriptions for turning
        ("N00b", "(More Thermals, Most Agile Turning)", config.DIFFICULTY_NOOB),
        ("Easy", "(Stronger Thermals, Agile Turning)", config.DIFFICULTY_EASY),
        ("Normal", "(Standard Challenge, Larger Turning Circle)", config.DIFFICULTY_NORMAL)
    ]
    for i, (name, desc, diff_const) in enumerate(difficulties_display):
        color = config.PASTEL_WHITE if selected_option_idx == diff_const else config.PASTEL_GRAY
        draw_text(surface, name, 48, config.SCREEN_WIDTH // 2, start_y + i * option_spacing, color, font_name=config.HUD_FONT_NAME, center=True, shadow=True, shadow_color=config.PASTEL_BLACK)
        draw_text(surface, desc, 22, config.SCREEN_WIDTH // 2, start_y + i * option_spacing + 35, color, font_name=config.HUD_FONT_NAME, center=True) 
    draw_text(surface, "Use UP/DOWN keys, ENTER to confirm", 22, config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT * 0.85, config.PASTEL_LIGHT_GRAY, font_name=config.HUD_FONT_NAME, center=True)

def draw_mode_select_screen(surface, selected_option_idx): 
    surface.fill(config.PASTEL_DARK_GRAY)
    draw_text(surface, "Select Mode", 56, config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 4, config.PASTEL_GOLD, font_name=config.HUD_FONT_NAME, center=True, shadow=True, shadow_color=config.PASTEL_BLACK)
    modes_display = [
        ("Free Fly", "(Explore & Reach Altitude Goals)", config.MODE_FREE_FLY),
        ("Race", "(Fly Through Markers Against AI)", config.MODE_RACE)
    ]
    for i, (name, desc, mode_const) in enumerate(modes_display):
        color = config.PASTEL_WHITE if selected_option_idx == mode_const else config.PASTEL_GRAY
        y_pos = config.SCREEN_HEIGHT // 2 - 30 + i * 100 
        draw_text(surface, name, 48, config.SCREEN_WIDTH // 2, y_pos, color, font_name=config.HUD_FONT_NAME, center=True, shadow=True, shadow_color=config.PASTEL_BLACK)
        draw_text(surface, desc, 22, config.SCREEN_WIDTH // 2, y_pos + 35, color, font_name=config.HUD_FONT_NAME, center=True) 
    draw_text(surface, "Use UP/DOWN keys, ENTER to confirm", 22, config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT * 3 // 4 + 50, config.PASTEL_LIGHT_GRAY, font_name=config.HUD_FONT_NAME, center=True)

def draw_laps_select_screen(surface, selected_lap_idx, lap_choices_list): 
    surface.fill(config.PASTEL_DARK_GRAY)
    draw_text(surface, "Select Laps", 56, config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 4, config.PASTEL_GOLD, font_name=config.HUD_FONT_NAME, center=True, shadow=True, shadow_color=config.PASTEL_BLACK)
    y_offset = config.SCREEN_HEIGHT // 2 - (len(lap_choices_list) - 1) * 40 
    for i, laps in enumerate(lap_choices_list):
        color = config.PASTEL_WHITE if i == selected_lap_idx else config.PASTEL_GRAY
        draw_text(surface, f"{laps} Lap{'s' if laps > 1 else ''}", 48, config.SCREEN_WIDTH // 2, y_offset + i * 80, color, font_name=config.HUD_FONT_NAME, center=True, shadow=True, shadow_color=config.PASTEL_BLACK)
    draw_text(surface, "Use UP/DOWN keys, ENTER to start race", 22, config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT * 3 // 4 + 50, config.PASTEL_LIGHT_GRAY, font_name=config.HUD_FONT_NAME, center=True)

def draw_target_reached_options_screen(surface, level, time_taken_seconds_val):
    surface.fill(config.PASTEL_DARK_GRAY)
    draw_text(surface, f"Level {level} Goal Reached!", 60, config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 3 - 20, config.PASTEL_GOLD, font_name=config.HUD_FONT_NAME, center=True, shadow=True, shadow_color=config.PASTEL_BLACK)
    draw_text(surface, f"Time: {time_taken_seconds_val:.1f}s", 36, config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 - 40, config.PASTEL_WHITE, font_name=config.HUD_FONT_NAME, center=True)
    draw_text(surface, "Press M to Move On to Next Level", 30, config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 + 30, config.PASTEL_LIGHT_GRAY, font_name=config.HUD_FONT_NAME, center=True)
    draw_text(surface, "Press C to Continue Flying This Level", 30, config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 + 70, config.PASTEL_LIGHT_GRAY, font_name=config.HUD_FONT_NAME, center=True)

def draw_post_goal_menu_screen(surface, level): 
    surface.fill(config.PASTEL_DARK_GRAY)
    draw_text(surface, f"Level {level} - Cruising", 50, config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 4, config.PASTEL_GOLD, font_name=config.HUD_FONT_NAME, center=True, shadow=True, shadow_color=config.PASTEL_BLACK)
    draw_text(surface, "Press N for Next Level", 30, config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 - 30, config.PASTEL_LIGHT_GRAY, font_name=config.HUD_FONT_NAME, center=True)
    draw_text(surface, "Press Q to Quit to Main Menu", 30, config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 + 10, config.PASTEL_LIGHT_GRAY, font_name=config.HUD_FONT_NAME, center=True)
    draw_text(surface, "Press R or ESCAPE to Resume Flying", 30, config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 + 50, config.PASTEL_LIGHT_GRAY, font_name=config.HUD_FONT_NAME, center=True)

def draw_pause_menu_screen(surface):
    dim_surface = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
    dim_surface.fill((0, 0, 0, 100)) 
    surface.blit(dim_surface, (0,0))
    draw_text(surface, "Paused", 72, config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 3, config.PASTEL_GOLD, font_name=config.HUD_FONT_NAME, center=True, shadow=True)
    draw_text(surface, "Press C to Continue", 30, config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2, config.PASTEL_LIGHT_GRAY, font_name=config.HUD_FONT_NAME, center=True)
    draw_text(surface, "Press Q for Main Menu", 30, config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 + 40, config.PASTEL_LIGHT_GRAY, font_name=config.HUD_FONT_NAME, center=True)

def draw_race_post_options_screen(surface, total_time_seconds, lap_times_list): 
    surface.fill(config.PASTEL_DARK_GRAY)
    draw_text(surface, "Race Finished!", 60, config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 4 - 30, config.PASTEL_GOLD, font_name=config.HUD_FONT_NAME, center=True, shadow=True, shadow_color=config.PASTEL_BLACK)
    draw_text(surface, f"Total Time: {total_time_seconds:.1f}s", 36, config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 4 + 30, config.PASTEL_WHITE, font_name=config.HUD_FONT_NAME, center=True)
    
    y_offset = config.SCREEN_HEIGHT // 2 - 50
    if lap_times_list:
        draw_text(surface, "Lap Times:", config.HUD_FONT_SIZE_NORMAL, config.SCREEN_WIDTH // 2, y_offset, config.PASTEL_WHITE, font_name=config.HUD_FONT_NAME, center=True)
        y_offset += 30
        for i, lap_time in enumerate(lap_times_list):
            draw_text(surface, f"Lap {i+1}: {lap_time:.1f}s", config.HUD_FONT_SIZE_SMALL, config.SCREEN_WIDTH // 2, y_offset + (i * 25), config.PASTEL_LIGHT_GRAY, font_name=config.HUD_FONT_NAME, center=True)
        y_offset += (len(lap_times_list) * 25) + 20 

    draw_text(surface, "N: New Race", 30, config.SCREEN_WIDTH // 2, y_offset, config.PASTEL_LIGHT_GRAY, font_name=config.HUD_FONT_NAME, center=True)
    y_offset += 40
    draw_text(surface, "F: Free Fly This Map", 30, config.SCREEN_WIDTH // 2, y_offset, config.PASTEL_LIGHT_GRAY, font_name=config.HUD_FONT_NAME, center=True)
    y_offset += 40
    draw_text(surface, "Q: Main Menu", 30, config.SCREEN_WIDTH // 2, y_offset, config.PASTEL_LIGHT_GRAY, font_name=config.HUD_FONT_NAME, center=True)

def draw_race_complete_screen(surface, total_time_seconds, lap_times_list): 
    # This function is now effectively replaced by draw_race_post_options_screen
    # but kept in case of direct calls or future use.
    surface.fill(config.PASTEL_DARK_GRAY)
    draw_text(surface, "Race Finished!", 60, config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 3 - 20, config.PASTEL_GOLD, font_name=config.HUD_FONT_NAME, center=True, shadow=True, shadow_color=config.PASTEL_BLACK)
    draw_text(surface, f"Total Time: {total_time_seconds:.1f}s", 40, config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 - 20, config.PASTEL_WHITE, font_name=config.HUD_FONT_NAME, center=True)
    if lap_times_list:
        draw_text(surface, "Lap Times:", config.HUD_FONT_SIZE_LARGE, config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 + 20, config.PASTEL_WHITE, font_name=config.HUD_FONT_NAME, center=True)
        for i, lap_time in enumerate(lap_times_list):
            draw_text(surface, f"Lap {i+1}: {lap_time:.1f}s", config.HUD_FONT_SIZE_NORMAL, config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 + 55 + (i * 28), config.PASTEL_LIGHT_GRAY, font_name=config.HUD_FONT_NAME, center=True)
    draw_text(surface, "Press ENTER for Main Menu", 32, config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT * 5 // 6, config.PASTEL_LIGHT_GRAY, font_name=config.HUD_FONT_NAME, center=True)


def draw_game_over_screen_content (surface, final_player_height, level_reached, high_scores_data, current_game_mode_data, total_laps_data): 
    surface.fill(config.PASTEL_DARK_GRAY)
    draw_text(surface, "GAME OVER", 72, config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 4, config.PASTEL_RED, font_name=config.HUD_FONT_NAME, center=True, shadow=True, shadow_color=config.PASTEL_BLACK)
    y_offset = config.SCREEN_HEIGHT // 2 - 80 
    if current_game_mode_data == config.MODE_FREE_FLY:
        draw_text(surface, f"Reached Level: {level_reached}", config.HUD_FONT_SIZE_LARGE, config.SCREEN_WIDTH // 2, y_offset, config.PASTEL_WHITE, font_name=config.HUD_FONT_NAME, center=True); y_offset += 35
        draw_text(surface, f"Max Altitude: {int(high_scores_data['max_altitude_free_fly'])}m", config.HUD_FONT_SIZE_LARGE, config.SCREEN_WIDTH // 2, y_offset, config.PASTEL_WHITE, font_name=config.HUD_FONT_NAME, center=True); y_offset += 35
        draw_text(surface, f"Longest Flight: {high_scores_data['longest_flight_time_free_fly']:.1f}s", config.HUD_FONT_SIZE_LARGE, config.SCREEN_WIDTH // 2, y_offset, config.PASTEL_WHITE, font_name=config.HUD_FONT_NAME, center=True); y_offset += 35
    elif current_game_mode_data == config.MODE_RACE:
        if total_laps_data in high_scores_data["best_total_race_times"]:
             draw_text(surface, f"Best Race ({total_laps_data} Laps): {high_scores_data['best_total_race_times'][total_laps_data]:.1f}s", config.HUD_FONT_SIZE_NORMAL, config.SCREEN_WIDTH // 2, y_offset, config.PASTEL_WHITE, font_name=config.HUD_FONT_NAME, center=True); y_offset += 30
        if high_scores_data["best_lap_time_race"] != float('inf'):
            draw_text(surface, f"Best Lap: {high_scores_data['best_lap_time_race']:.1f}s", config.HUD_FONT_SIZE_NORMAL, config.SCREEN_WIDTH // 2, y_offset, config.PASTEL_WHITE, font_name=config.HUD_FONT_NAME, center=True); y_offset += 30
    draw_text(surface, f"Final Height: {int(final_player_height)}m", config.HUD_FONT_SIZE_LARGE, config.SCREEN_WIDTH // 2, y_offset, config.PASTEL_WHITE, font_name=config.HUD_FONT_NAME, center=True); y_offset += 40
    draw_text(surface, "Press ENTER for Menu", 32, config.SCREEN_WIDTH // 2, y_offset + 20, config.PASTEL_LIGHT_GRAY, font_name=config.HUD_FONT_NAME, center=True)
