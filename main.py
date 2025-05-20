# main.py
# Main game script for Pastel Glider. Orchestrates game flow.

import pygame
import math # Keep for HUD calculations if any remain here, or move to ui.py
import random # Keep for now, might be used for minor main-loop specific randomness

import config 
from sprites import PlayerGlider, AIGlider, Thermal, RaceMarker, ForegroundCloud 
from map_generation import draw_endless_map 
from ui import (draw_text, Minimap, draw_height_indicator_hud, draw_dial, draw_weather_vane, 
                draw_start_screen_content, draw_difficulty_select_screen, draw_mode_select_screen,
                draw_laps_select_screen, draw_target_reached_options_screen, draw_post_goal_menu_screen,
                draw_pause_menu_screen, draw_race_complete_screen, draw_game_over_screen_content)
import game_state_manager as gsm # Import the new game state manager

# --- Pygame Setup ---
pygame.init()
pygame.mixer.init() 
screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
pygame.display.set_caption("Pastel Glider - Floating Dreams")
clock = pygame.time.Clock()

# --- Game Objects (instantiated once, managed by game_state_manager) ---
# Note: player, sprite groups etc. are now inside game_state_manager.py

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
            if gsm.game_state == config.STATE_PAUSED:
                if event.key == pygame.K_c: 
                    time_spent_paused = pygame.time.get_ticks() - gsm.pause_start_ticks
                    gsm.level_timer_start_ticks += time_spent_paused
                    gsm.player.current_lap_start_ticks += time_spent_paused # Access player via gsm
                    gsm.current_session_flight_start_ticks += time_spent_paused
                    gsm.game_state = gsm.game_state_before_pause
                elif event.key == pygame.K_q:
                    gsm.reset_to_main_menu()
            elif gsm.game_state in (config.STATE_PLAYING_FREE_FLY, config.STATE_RACE_PLAYING, config.STATE_TARGET_REACHED_CONTINUE_PLAYING) and event.key == pygame.K_ESCAPE:
                if gsm.game_state != config.STATE_PAUSED: 
                    gsm.game_state_before_pause = gsm.game_state
                    gsm.game_state = config.STATE_PAUSED
                    gsm.pause_start_ticks = pygame.time.get_ticks()
            elif gsm.game_state == config.STATE_START_SCREEN:
                if event.key == pygame.K_RETURN:
                    gsm.game_state = config.STATE_DIFFICULTY_SELECT
            elif gsm.game_state == config.STATE_DIFFICULTY_SELECT:
                if event.key == pygame.K_UP:
                    gsm.selected_difficulty_option = (gsm.selected_difficulty_option - 1 + len(config.difficulty_options_map)) % len(config.difficulty_options_map)
                elif event.key == pygame.K_DOWN:
                    gsm.selected_difficulty_option = (gsm.selected_difficulty_option + 1) % len(config.difficulty_options_map)
                elif event.key == pygame.K_RETURN:
                    config.game_difficulty = gsm.selected_difficulty_option 
                    gsm.game_state = config.STATE_MODE_SELECT
            elif gsm.game_state == config.STATE_MODE_SELECT:
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    gsm.selected_mode_option = 1 - gsm.selected_mode_option
                elif event.key == pygame.K_RETURN:
                    config.current_game_mode = gsm.selected_mode_option 
                    if config.current_game_mode == config.MODE_FREE_FLY:
                        gsm.start_new_level(1) 
                    else:
                        gsm.game_state = config.STATE_RACE_LAPS_SELECT
            elif gsm.game_state == config.STATE_RACE_LAPS_SELECT:
                if event.key == pygame.K_UP:
                    gsm.selected_laps_option = (gsm.selected_laps_option - 1 + len(gsm.lap_options)) % len(gsm.lap_options)
                elif event.key == pygame.K_DOWN:
                    gsm.selected_laps_option = (gsm.selected_laps_option + 1) % len(gsm.lap_options)
                elif event.key == pygame.K_RETURN:
                    gsm.total_race_laps = gsm.lap_options[gsm.selected_laps_option] 
                    gsm.start_new_level(gsm.lap_options[gsm.selected_laps_option]) 
            elif gsm.game_state == config.STATE_TARGET_REACHED_OPTIONS: 
                if event.key == pygame.K_m:
                    gsm.start_new_level(gsm.current_level + 1)
                elif event.key == pygame.K_c:
                    gsm.game_state = config.STATE_TARGET_REACHED_CONTINUE_PLAYING
            elif gsm.game_state == config.STATE_POST_GOAL_MENU: 
                if event.key == pygame.K_n:
                    gsm.start_new_level(gsm.current_level + 1)
                elif event.key == pygame.K_q:
                    gsm.reset_to_main_menu()
                elif event.key == pygame.K_r or event.key == pygame.K_ESCAPE:
                    gsm.game_state = config.STATE_TARGET_REACHED_CONTINUE_PLAYING
            elif gsm.game_state == config.STATE_RACE_COMPLETE:
                if event.key == pygame.K_RETURN:
                    gsm.reset_to_main_menu()
            elif gsm.game_state == config.STATE_GAME_OVER:
                if event.key == pygame.K_RETURN:
                    gsm.reset_to_main_menu()

    # --- Updates ---
    camera_x_current, camera_y_current = gsm.player.world_x, gsm.player.world_y # Default camera if not updated
    if gsm.game_state not in (config.STATE_PAUSED, config.STATE_START_SCREEN, config.STATE_DIFFICULTY_SELECT, 
                           config.STATE_MODE_SELECT, config.STATE_RACE_LAPS_SELECT, config.STATE_TARGET_REACHED_OPTIONS, 
                           config.STATE_POST_GOAL_MENU, config.STATE_RACE_COMPLETE, config.STATE_GAME_OVER):
        camera_x_current, camera_y_current = gsm.update_game_logic(keys) # This now returns camera positions
    
    # --- Drawing ---
    screen.fill(config.PASTEL_BLACK)
    
    if gsm.game_state in (config.STATE_PLAYING_FREE_FLY, config.STATE_TARGET_REACHED_CONTINUE_PLAYING, config.STATE_RACE_PLAYING, config.STATE_PAUSED):
        draw_endless_map(screen, camera_x_current, camera_y_current, gsm.current_map_offset_x, gsm.current_map_offset_y, gsm.tile_type_cache)
        gsm.player.draw_contrail(screen, camera_x_current, camera_y_current)
        for ags in gsm.ai_gliders:
            ags.draw_contrail(screen, camera_x_current, camera_y_current)
        gsm.all_world_sprites.draw(screen)
        screen.blit(gsm.player.image, gsm.player.rect) 
        gsm.foreground_clouds_group.draw(screen) 
        
        hud_sfc = pygame.Surface((config.SCREEN_WIDTH, config.HUD_HEIGHT), pygame.SRCALPHA)
        hud_sfc.fill(config.PASTEL_HUD_PANEL)
        screen.blit(hud_sfc, (0,0))
        
        hm, ls, cyh = 10, 28, 8 
        
        if config.current_game_mode == config.MODE_FREE_FLY:
            draw_text(screen, f"Level: {gsm.current_level}", config.HUD_FONT_SIZE_NORMAL, hm, cyh, config.PASTEL_TEXT_COLOR_HUD, font_name=config.HUD_FONT_NAME)
            draw_text(screen, f"Target: {config.TARGET_HEIGHT_PER_LEVEL * gsm.current_level}m", config.HUD_FONT_SIZE_NORMAL, hm + 150, cyh, config.PASTEL_TEXT_COLOR_HUD, font_name=config.HUD_FONT_NAME)
        elif config.current_game_mode == config.MODE_RACE:
            draw_text(screen, f"Lap: {min(gsm.player.laps_completed + 1, gsm.total_race_laps)}/{gsm.total_race_laps}", config.HUD_FONT_SIZE_NORMAL, hm, cyh, config.PASTEL_TEXT_COLOR_HUD, font_name=config.HUD_FONT_NAME)
            current_lap_time_display = 0.0
            if gsm.game_state == config.STATE_RACE_PLAYING :
                 current_lap_time_display = (pygame.time.get_ticks() - gsm.player.current_lap_start_ticks) / 1000.0
            elif gsm.player_race_lap_times and gsm.player.laps_completed < gsm.total_race_laps:
                 current_lap_time_display = gsm.player_race_lap_times[-1] if gsm.player_race_lap_times else 0.0
            draw_text(screen, f"Lap Time: {current_lap_time_display:.1f}s", config.HUD_FONT_SIZE_NORMAL, hm + 320, cyh, config.PASTEL_TEXT_COLOR_HUD, font_name=config.HUD_FONT_NAME)
            
            if gsm.race_course_markers and gsm.player.current_target_marker_index < len(gsm.race_course_markers) and gsm.game_state == config.STATE_RACE_PLAYING:
                tm = gsm.race_course_markers[gsm.player.current_target_marker_index]
                draw_text(screen, f"Marker {tm.number}: {int(math.hypot(gsm.player.world_x - tm.world_pos.x, gsm.player.world_y - tm.world_pos.y) / 10.0)} u", config.HUD_FONT_SIZE_NORMAL, hm + 150, cyh, config.PASTEL_TEXT_COLOR_HUD, font_name=config.HUD_FONT_NAME)
                
                marker_dx = tm.world_pos.x - gsm.player.world_x; marker_dy = tm.world_pos.y - gsm.player.world_y
                angle_to_marker_world_rad = math.atan2(marker_dy, marker_dx); angle_to_marker_world_deg = math.degrees(angle_to_marker_world_rad)
                relative_angle_to_marker = (angle_to_marker_world_deg - gsm.player.heading + 360) % 360
                
                marker_dial_x = config.SCREEN_WIDTH - config.MINIMAP_WIDTH - config.MINIMAP_MARGIN - 180 
                draw_dial(screen, marker_dial_x, hm + config.HUD_HEIGHT // 2 - 10, 22, relative_angle_to_marker, config.PASTEL_ACTIVE_MARKER_COLOR) 

        cyh += ls
        timer_s = (current_ticks - gsm.level_timer_start_ticks) / 1000.0 if gsm.game_state in (config.STATE_PLAYING_FREE_FLY, config.STATE_RACE_PLAYING) else gsm.time_taken_for_level
        goal_text = " (Goal!)" if gsm.game_state == config.STATE_TARGET_REACHED_CONTINUE_PLAYING else ""
        draw_text(screen, f"Time: {timer_s:.1f}s{goal_text}", config.HUD_FONT_SIZE_NORMAL, hm, cyh, config.PASTEL_TEXT_COLOR_HUD, font_name=config.HUD_FONT_NAME)
        
        cyh += ls
        draw_text(screen, f"Height: {int(gsm.player.height)}m", config.HUD_FONT_SIZE_NORMAL, hm, cyh, config.PASTEL_TEXT_COLOR_HUD, font_name=config.HUD_FONT_NAME)
        draw_text(screen, f"Speed: {gsm.player.speed:.1f}", config.HUD_FONT_SIZE_NORMAL, hm + 150, cyh, config.PASTEL_TEXT_COLOR_HUD, font_name=config.HUD_FONT_NAME)
        if gsm.player.speed < config.STALL_SPEED:
            draw_text(screen, "STALL!", config.HUD_FONT_SIZE_LARGE, config.SCREEN_WIDTH // 2, hm + ls // 2, config.PASTEL_RED, font_name=config.HUD_FONT_NAME, center=True, shadow=True, shadow_color=config.PASTEL_BLACK)
        
        wind_text_x_pos = config.SCREEN_WIDTH - config.MINIMAP_WIDTH - config.MINIMAP_MARGIN - 125 
        draw_text(screen, f"Wind:", config.HUD_FONT_SIZE_SMALL, wind_text_x_pos - 50, hm + config.HUD_HEIGHT // 2 - 22, config.PASTEL_TEXT_COLOR_HUD, font_name=config.HUD_FONT_NAME) 
        draw_weather_vane(screen, config.current_wind_speed_x, config.current_wind_speed_y, wind_text_x_pos, hm + config.HUD_HEIGHT // 2 - 10 , 22) 
        
        et = "ESC for Menu"
        if gsm.game_state == config.STATE_TARGET_REACHED_CONTINUE_PLAYING: et = "ESC for Options"
        elif gsm.game_state == config.STATE_PLAYING_FREE_FLY or gsm.game_state == config.STATE_RACE_PLAYING: et = "ESC to Pause"
        draw_text(screen, et, config.HUD_FONT_SIZE_SMALL, config.SCREEN_WIDTH - 150, config.SCREEN_HEIGHT - 30, config.PASTEL_LIGHT_GRAY, font_name=config.HUD_FONT_NAME, center=True) 
        
        draw_height_indicator_hud(screen, gsm.player.height, config.TARGET_HEIGHT_PER_LEVEL * gsm.current_level if config.current_game_mode == config.MODE_FREE_FLY else gsm.player.height + 100, gsm.player.vertical_speed, clock)
        
        if config.current_game_mode == config.MODE_RACE and (gsm.game_state == config.STATE_RACE_PLAYING or gsm.game_state == config.STATE_RACE_COMPLETE or gsm.game_state == config.STATE_PAUSED):
            gsm.minimap.draw(screen, gsm.player, gsm.ai_gliders, gsm.race_course_markers)
        
        if gsm.game_state == config.STATE_PAUSED:
            draw_pause_menu_screen(screen)

    elif gsm.game_state == config.STATE_START_SCREEN:
        draw_start_screen_content(screen); gsm.foreground_clouds_group.draw(screen) 
    elif gsm.game_state == config.STATE_DIFFICULTY_SELECT:
        draw_difficulty_select_screen(screen, gsm.selected_difficulty_option); gsm.foreground_clouds_group.draw(screen)
    elif gsm.game_state == config.STATE_MODE_SELECT:
        draw_mode_select_screen(screen, gsm.selected_mode_option); gsm.foreground_clouds_group.draw(screen)
    elif gsm.game_state == config.STATE_RACE_LAPS_SELECT:
        draw_laps_select_screen(screen, gsm.selected_laps_option, gsm.lap_options); gsm.foreground_clouds_group.draw(screen)
    elif gsm.game_state == config.STATE_TARGET_REACHED_OPTIONS:
        draw_target_reached_options_screen(screen, gsm.current_level, gsm.time_taken_for_level); gsm.foreground_clouds_group.draw(screen)
    elif gsm.game_state == config.STATE_POST_GOAL_MENU:
        draw_post_goal_menu_screen(screen, gsm.current_level); gsm.foreground_clouds_group.draw(screen)
    elif gsm.game_state == config.STATE_RACE_COMPLETE:
        draw_race_complete_screen(screen, gsm.time_taken_for_level, gsm.player_race_lap_times); gsm.foreground_clouds_group.draw(screen) 
    elif gsm.game_state == config.STATE_GAME_OVER:
        draw_game_over_screen_content(screen, gsm.final_score, gsm.current_level, gsm.high_scores, config.current_game_mode, gsm.total_race_laps); gsm.foreground_clouds_group.draw(screen) 
    
    pygame.display.flip()
pygame.quit()
