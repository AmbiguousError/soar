# main.py
# Main game script for Pastel Glider. Orchestrates game flow.

import pygame
import math
import random

import config
from sprites import PlayerGlider, AIGlider, Thermal, RaceMarker, ForegroundCloud, Bullet, Runway, DeliveryCheckpoint # Added DeliveryCheckpoint
from map_generation import draw_endless_map
from ui import (draw_text, Minimap, draw_height_indicator_hud, draw_dial, draw_weather_vane,
                draw_start_screen_content, draw_difficulty_select_screen, draw_mode_select_screen,
                draw_laps_select_screen, draw_target_reached_options_screen, draw_post_goal_menu_screen,
                draw_pause_menu_screen, draw_race_post_options_screen, draw_game_over_screen_content,
                draw_dogfight_round_complete_screen, draw_dogfight_game_over_continue_screen,
                draw_delivery_complete_screen) 
import game_state_manager as gsm 
from sprites import DeliveryCheckpoint, Runway # Ensure these are imported if type checking (already imported above, but good to double check context)


# --- Pygame Setup ---
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
pygame.display.set_caption("Pastel Glider - Floating Dreams")
clock = pygame.time.Clock()

# --- Initial Camera Position ---
camera_x_current = 0.0
camera_y_current = 0.0

# --- Game Loop ---
running = True
while running:
    dt = clock.tick(60) / 1000.0 # Delta time, not heavily used yet but good practice
    current_ticks = pygame.time.get_ticks()
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            # PAUSE Handling (universal for active play states)
            if gsm.game_state == config.STATE_PAUSED:
                if event.key == pygame.K_c: # Continue
                    time_spent_paused = pygame.time.get_ticks() - gsm.pause_start_ticks
                    gsm.level_timer_start_ticks += time_spent_paused
                    if gsm.game_state_before_pause == config.STATE_RACE_PLAYING: # Adjust lap timer if it was a race
                        gsm.player.current_lap_start_ticks += time_spent_paused
                    # Adjust session start for high scores if applicable
                    gsm.current_session_flight_start_ticks += time_spent_paused
                    gsm.game_state = gsm.game_state_before_pause
                elif event.key == pygame.K_q: # Quit to menu
                    gsm.reset_to_main_menu()
            elif gsm.game_state in (config.STATE_PLAYING_FREE_FLY, config.STATE_RACE_PLAYING,
                                    config.STATE_TARGET_REACHED_CONTINUE_PLAYING, config.STATE_DOGFIGHT_PLAYING,
                                    config.STATE_DELIVERY_PLAYING) and event.key == pygame.K_ESCAPE:
                if gsm.game_state != config.STATE_PAUSED: # Avoid re-pausing
                    gsm.game_state_before_pause = gsm.game_state
                    gsm.game_state = config.STATE_PAUSED
                    gsm.pause_start_ticks = pygame.time.get_ticks()

            # START SCREEN
            elif gsm.game_state == config.STATE_START_SCREEN:
                if event.key == pygame.K_RETURN:
                    gsm.game_state = config.STATE_MODE_SELECT 
            
            # MODE SELECT
            elif gsm.game_state == config.STATE_MODE_SELECT:
                num_modes = 4 # Free Fly, Race, Dogfight, Delivery
                if event.key == pygame.K_UP:
                    gsm.selected_mode_option = (gsm.selected_mode_option - 1 + num_modes) % num_modes
                elif event.key == pygame.K_DOWN:
                    gsm.selected_mode_option = (gsm.selected_mode_option + 1) % num_modes
                elif event.key == pygame.K_RETURN:
                    config.current_game_mode = gsm.selected_mode_option
                    gsm.game_state = config.STATE_DIFFICULTY_SELECT 
                elif event.key == pygame.K_ESCAPE: 
                    gsm.game_state = config.STATE_START_SCREEN

            # DIFFICULTY SELECT
            elif gsm.game_state == config.STATE_DIFFICULTY_SELECT:
                if event.key == pygame.K_UP:
                    gsm.selected_difficulty_option = (gsm.selected_difficulty_option - 1 + len(config.difficulty_options_map)) % len(config.difficulty_options_map)
                elif event.key == pygame.K_DOWN:
                    gsm.selected_difficulty_option = (gsm.selected_difficulty_option + 1) % len(config.difficulty_options_map)
                elif event.key == pygame.K_RETURN:
                    config.game_difficulty = gsm.selected_difficulty_option
                    if config.current_game_mode == config.MODE_FREE_FLY:
                        gsm.start_new_level(1) 
                    elif config.current_game_mode == config.MODE_RACE:
                        gsm.game_state = config.STATE_RACE_LAPS_SELECT 
                    elif config.current_game_mode == config.MODE_DOGFIGHT:
                        gsm.dogfight_current_round = 1
                        gsm.start_new_level(gsm.dogfight_current_round) 
                    elif config.current_game_mode == config.MODE_DELIVERY:
                        gsm.successful_deliveries_count = 0 
                        gsm.current_level = 1 
                        gsm.start_new_level(1) 
                elif event.key == pygame.K_ESCAPE: 
                    gsm.game_state = config.STATE_MODE_SELECT
            
            # RACE LAPS SELECT
            elif gsm.game_state == config.STATE_RACE_LAPS_SELECT:
                if event.key == pygame.K_UP:
                    gsm.selected_laps_option = (gsm.selected_laps_option - 1 + len(gsm.lap_options)) % len(gsm.lap_options)
                elif event.key == pygame.K_DOWN:
                    gsm.selected_laps_option = (gsm.selected_laps_option + 1) % len(gsm.lap_options)
                elif event.key == pygame.K_RETURN:
                    gsm.total_race_laps = gsm.lap_options[gsm.selected_laps_option]
                    gsm.start_new_level(gsm.lap_options[gsm.selected_laps_option]) 
                elif event.key == pygame.K_ESCAPE: 
                    gsm.game_state = config.STATE_DIFFICULTY_SELECT

            # FREE FLY TARGET REACHED
            elif gsm.game_state == config.STATE_TARGET_REACHED_OPTIONS:
                if event.key == pygame.K_m: 
                    gsm.start_new_level(gsm.current_level + 1)
                elif event.key == pygame.K_c: 
                    gsm.game_state = config.STATE_TARGET_REACHED_CONTINUE_PLAYING
            # FREE FLY POST GOAL MENU
            elif gsm.game_state == config.STATE_POST_GOAL_MENU:
                if event.key == pygame.K_n: 
                    gsm.start_new_level(gsm.current_level + 1)
                elif event.key == pygame.K_q: 
                    gsm.reset_to_main_menu()
                elif event.key == pygame.K_r or event.key == pygame.K_ESCAPE: 
                    gsm.game_state = config.STATE_TARGET_REACHED_CONTINUE_PLAYING
            # RACE COMPLETE 
            elif gsm.game_state == config.STATE_RACE_COMPLETE:
                gsm.game_state = config.STATE_RACE_POST_OPTIONS 
            # RACE POST OPTIONS
            elif gsm.game_state == config.STATE_RACE_POST_OPTIONS:
                if event.key == pygame.K_n: 
                    gsm.game_state = config.STATE_RACE_LAPS_SELECT 
                elif event.key == pygame.K_f: 
                    config.current_game_mode = config.MODE_FREE_FLY
                    gsm.start_new_level(1, continue_map_from_race=True)
                elif event.key == pygame.K_q: 
                    gsm.reset_to_main_menu()
            # DOGFIGHT ROUND COMPLETE
            elif gsm.game_state == config.STATE_DOGFIGHT_ROUND_COMPLETE:
                if event.key == pygame.K_n: 
                    gsm.start_dogfight_round(gsm.dogfight_current_round + 1)
                elif event.key == pygame.K_q: 
                    gsm.reset_to_main_menu()
            # DOGFIGHT GAME OVER 
            elif gsm.game_state == config.STATE_DOGFIGHT_GAME_OVER_CONTINUE:
                if event.key == pygame.K_c: 
                    gsm.start_dogfight_round(gsm.dogfight_current_round)
                elif event.key == pygame.K_q: 
                    gsm.reset_to_main_menu()
            # DELIVERY COMPLETE
            elif gsm.game_state == config.STATE_DELIVERY_COMPLETE:
                if event.key == pygame.K_n: 
                    # current_level in gsm was already incremented upon successful delivery for the *next* mission.
                    gsm.start_new_level(gsm.current_level) 
                elif event.key == pygame.K_q: 
                    gsm.reset_to_main_menu()
            # GAME OVER (universal)
            elif gsm.game_state == config.STATE_GAME_OVER:
                if event.key == pygame.K_RETURN:
                    gsm.reset_to_main_menu()

    # --- Updates ---
    active_play_states = [
        config.STATE_PLAYING_FREE_FLY, config.STATE_TARGET_REACHED_CONTINUE_PLAYING,
        config.STATE_RACE_PLAYING, config.STATE_DOGFIGHT_PLAYING, config.STATE_DELIVERY_PLAYING
    ]
    if gsm.game_state in active_play_states:
        camera_x_current, camera_y_current = gsm.update_game_logic(keys)
    elif gsm.game_state == config.STATE_PAUSED: 
        camera_x_current = gsm.player.world_x - config.SCREEN_WIDTH // 2
        camera_y_current = gsm.player.world_y - config.SCREEN_HEIGHT // 2


    # --- Drawing ---
    screen.fill(config.PASTEL_BLACK) 

    if gsm.game_state in active_play_states or gsm.game_state == config.STATE_PAUSED:
        draw_endless_map(screen, camera_x_current, camera_y_current, gsm.current_map_offset_x, gsm.current_map_offset_y, gsm.tile_type_cache)
        
        gsm.player.draw_contrail(screen, camera_x_current, camera_y_current)
        for ags in gsm.ai_gliders: ags.draw_contrail(screen, camera_x_current, camera_y_current)
        for wg in gsm.wingmen_group: wg.draw_contrail(screen, camera_x_current, camera_y_current)
        for enemy in gsm.dogfight_enemies_group: enemy.draw_contrail(screen, camera_x_current, camera_y_current)
        
        gsm.all_world_sprites.draw(screen) 
        
        current_display_state = gsm.game_state if gsm.game_state != config.STATE_PAUSED else gsm.game_state_before_pause
        if current_display_state == config.STATE_DOGFIGHT_PLAYING:
            gsm.player.draw_health_bar(screen, camera_x_current, camera_y_current)
            for enemy in gsm.dogfight_enemies_group:
                enemy.draw_health_bar(screen, camera_x_current, camera_y_current)
        
        screen.blit(gsm.player.image, gsm.player.rect)
        gsm.foreground_clouds_group.draw(screen)

        # --- HUD Drawing ---
        hud_sfc = pygame.Surface((config.SCREEN_WIDTH, config.HUD_HEIGHT), pygame.SRCALPHA)
        hud_sfc.fill(config.PASTEL_HUD_PANEL)
        screen.blit(hud_sfc, (0,0))
        hm, ls, cyh = 10, 28, 8

        if config.current_game_mode == config.MODE_FREE_FLY:
            draw_text(screen, f"Level: {gsm.current_level}", config.HUD_FONT_SIZE_NORMAL, hm, cyh, config.PASTEL_TEXT_COLOR_HUD, font_name=config.HUD_FONT_NAME)
            draw_text(screen, f"Target: {config.TARGET_HEIGHT_PER_LEVEL * gsm.current_level}m", config.HUD_FONT_SIZE_NORMAL, hm + 150, cyh, config.PASTEL_TEXT_COLOR_HUD, font_name=config.HUD_FONT_NAME)
            draw_text(screen, f"Wingmen: {gsm.unlocked_wingmen_count}", config.HUD_FONT_SIZE_NORMAL, hm + 380, cyh, config.PASTEL_TEXT_COLOR_HUD, font_name=config.HUD_FONT_NAME)
        elif config.current_game_mode == config.MODE_RACE:
            draw_text(screen, f"Lap: {min(gsm.player.laps_completed + 1, gsm.total_race_laps)}/{gsm.total_race_laps}", config.HUD_FONT_SIZE_NORMAL, hm, cyh, config.PASTEL_TEXT_COLOR_HUD, font_name=config.HUD_FONT_NAME)
            current_lap_time_display = 0.0
            if gsm.game_state == config.STATE_RACE_PLAYING :
                 current_lap_time_display = (pygame.time.get_ticks() - gsm.player.current_lap_start_ticks) / 1000.0
            elif gsm.player_race_lap_times and gsm.player.laps_completed < gsm.total_race_laps: 
                 current_lap_time_display = gsm.player_race_lap_times[-1] if gsm.player_race_lap_times else 0.0
            draw_text(screen, f"Lap Time: {current_lap_time_display:.1f}s", config.HUD_FONT_SIZE_NORMAL, hm + 380, cyh, config.PASTEL_TEXT_COLOR_HUD, font_name=config.HUD_FONT_NAME)
            if gsm.race_course_markers and gsm.player.current_target_marker_index < len(gsm.race_course_markers) and gsm.game_state == config.STATE_RACE_PLAYING:
                tm = gsm.race_course_markers[gsm.player.current_target_marker_index]
                draw_text(screen, f"Marker {tm.number}: {int(math.hypot(gsm.player.world_x - tm.world_pos.x, gsm.player.world_y - tm.world_pos.y) / 10.0)} u", config.HUD_FONT_SIZE_NORMAL, hm + 150, cyh, config.PASTEL_TEXT_COLOR_HUD, font_name=config.HUD_FONT_NAME)
                marker_dx = tm.world_pos.x - gsm.player.world_x; marker_dy = tm.world_pos.y - gsm.player.world_y
                angle_to_marker_world_rad = math.atan2(marker_dy, marker_dx); angle_to_marker_world_deg = math.degrees(angle_to_marker_world_rad)
                relative_angle_to_marker = (angle_to_marker_world_deg - gsm.player.heading + 360) % 360
                marker_dial_x = config.SCREEN_WIDTH - config.MINIMAP_WIDTH - config.MINIMAP_MARGIN - 180
                draw_dial(screen, marker_dial_x, hm + config.HUD_HEIGHT // 2 - 10, 22, relative_angle_to_marker, config.PASTEL_ACTIVE_MARKER_COLOR, label="M")
        elif config.current_game_mode == config.MODE_DOGFIGHT:
            draw_text(screen, f"Round: {gsm.dogfight_current_round}", config.HUD_FONT_SIZE_NORMAL, hm, cyh, config.PASTEL_TEXT_COLOR_HUD, font_name=config.HUD_FONT_NAME)
            enemies_left = gsm.dogfight_enemies_to_spawn_this_round - gsm.dogfight_enemies_defeated_this_round
            draw_text(screen, f"Enemies: {enemies_left}", config.HUD_FONT_SIZE_NORMAL, hm + 150, cyh, config.PASTEL_TEXT_COLOR_HUD, font_name=config.HUD_FONT_NAME)
            draw_text(screen, f"Health: {gsm.player.health}", config.HUD_FONT_SIZE_NORMAL, hm + 320, cyh, config.PASTEL_TEXT_COLOR_HUD, font_name=config.HUD_FONT_NAME)
        elif config.current_game_mode == config.MODE_DELIVERY:
            target_label_str = "Dest"
            target_dial_char = "D"
            target_dial_color = config.PASTEL_RUNWAY_DESTINATION_COLOR 
            dist_to_target_display_str = "N/A"
            num_total_checkpoints = len(gsm.delivery_checkpoints_list)

            active_target = gsm.delivery_active_target_object
            if active_target:
                dist_to_target_val = math.hypot(gsm.player.world_x - active_target.world_pos.x, gsm.player.world_y - active_target.world_pos.y)
                dist_to_target_display_str = f"{int(dist_to_target_val / 10.0)} u"
                
                target_dx = active_target.world_pos.x - gsm.player.world_x
                target_dy = active_target.world_pos.y - gsm.player.world_y
                angle_to_target_rad = math.atan2(target_dy, target_dx)
                angle_to_target_deg = math.degrees(angle_to_target_rad)
                relative_angle_to_target = (angle_to_target_deg - gsm.player.heading + 360) % 360
                dial_x_pos = config.SCREEN_WIDTH - config.MINIMAP_WIDTH - config.MINIMAP_MARGIN - 180
                
                if isinstance(active_target, DeliveryCheckpoint):
                    target_label_str = f"CP {active_target.number}/{num_total_checkpoints}"
                    target_dial_char = f"C{active_target.number}" if active_target.number < 10 else "C"
                    target_dial_color = config.DELIVERY_CHECKPOINT_COLOR_ACTIVE
                
                draw_dial(screen, dial_x_pos, hm + config.HUD_HEIGHT // 2 - 10, 22, relative_angle_to_target, target_dial_color, label=target_dial_char)

            draw_text(screen, f"Delivery: {gsm.current_level}", config.HUD_FONT_SIZE_NORMAL, hm, cyh, config.PASTEL_TEXT_COLOR_HUD, font_name=config.HUD_FONT_NAME)
            draw_text(screen, f"{target_label_str}: {dist_to_target_display_str}", config.HUD_FONT_SIZE_NORMAL, hm + 150, cyh, config.PASTEL_TEXT_COLOR_HUD, font_name=config.HUD_FONT_NAME)
            draw_text(screen, f"Wingmen: {gsm.unlocked_wingmen_count}", config.HUD_FONT_SIZE_NORMAL, hm + 380, cyh, config.PASTEL_TEXT_COLOR_HUD, font_name=config.HUD_FONT_NAME)
            draw_text(screen, f"Completed: {gsm.successful_deliveries_count}", config.HUD_FONT_SIZE_NORMAL, hm + 520, cyh, config.PASTEL_TEXT_COLOR_HUD, font_name=config.HUD_FONT_NAME)


        cyh += ls
        timer_s = (current_ticks - gsm.level_timer_start_ticks) / 1000.0 if gsm.game_state in active_play_states else gsm.time_taken_for_level
        goal_text = " (Goal!)" if gsm.game_state == config.STATE_TARGET_REACHED_CONTINUE_PLAYING else ""
        draw_text(screen, f"Time: {timer_s:.1f}s{goal_text}", config.HUD_FONT_SIZE_NORMAL, hm, cyh, config.PASTEL_TEXT_COLOR_HUD, font_name=config.HUD_FONT_NAME)
        cyh += ls
        draw_text(screen, f"Height: {int(gsm.player.height)}m", config.HUD_FONT_SIZE_NORMAL, hm, cyh, config.PASTEL_TEXT_COLOR_HUD, font_name=config.HUD_FONT_NAME)
        draw_text(screen, f"Speed: {gsm.player.speed:.1f}", config.HUD_FONT_SIZE_NORMAL, hm + 150, cyh, config.PASTEL_TEXT_COLOR_HUD, font_name=config.HUD_FONT_NAME)
        if gsm.player.speed < config.STALL_SPEED:
            draw_text(screen, "STALL!", config.HUD_FONT_SIZE_LARGE, config.SCREEN_WIDTH // 2, hm + ls // 2 - 5, config.PASTEL_RED, font_name=config.HUD_FONT_NAME, center=True, shadow=True, shadow_color=config.PASTEL_BLACK)
        
        wind_text_x_pos = config.SCREEN_WIDTH - config.MINIMAP_WIDTH - config.MINIMAP_MARGIN - 125
        if config.current_game_mode != config.MODE_DOGFIGHT: 
            draw_text(screen, f"Wind:", config.HUD_FONT_SIZE_SMALL, wind_text_x_pos - 50, hm + config.HUD_HEIGHT // 2 - 10, config.PASTEL_TEXT_COLOR_HUD, font_name=config.HUD_FONT_NAME)
            draw_weather_vane(screen, config.current_wind_speed_x, config.current_wind_speed_y, wind_text_x_pos, hm + config.HUD_HEIGHT // 2 - 10 , 22)
        
        et = "ESC for Menu"
        if gsm.game_state == config.STATE_TARGET_REACHED_CONTINUE_PLAYING: et = "ESC for Options"
        elif gsm.game_state in active_play_states: et = "ESC to Pause"
        if gsm.game_state in active_play_states or gsm.game_state == config.STATE_TARGET_REACHED_CONTINUE_PLAYING :
            draw_text(screen, et, config.HUD_FONT_SIZE_SMALL, config.SCREEN_WIDTH - 150, config.SCREEN_HEIGHT - 30, config.PASTEL_LIGHT_GRAY, font_name=config.HUD_FONT_NAME, center=True)
        
        draw_height_indicator_hud(screen, gsm.player.height, config.TARGET_HEIGHT_PER_LEVEL * gsm.current_level if config.current_game_mode == config.MODE_FREE_FLY else gsm.player.height + 100, gsm.player.vertical_speed, clock, config.current_game_mode)

        # Minimap
        if config.current_game_mode == config.MODE_RACE and \
           (gsm.game_state == config.STATE_RACE_PLAYING or gsm.game_state == config.STATE_RACE_COMPLETE or \
            (gsm.game_state == config.STATE_PAUSED and gsm.game_state_before_pause == config.STATE_RACE_PLAYING)):
            gsm.minimap.draw(screen, gsm.player, gsm.ai_gliders, gsm.race_course_markers)
        elif config.current_game_mode == config.MODE_DELIVERY and \
             (gsm.game_state == config.STATE_DELIVERY_PLAYING or gsm.game_state == config.STATE_DELIVERY_COMPLETE or \
              (gsm.game_state == config.STATE_PAUSED and gsm.game_state_before_pause == config.STATE_DELIVERY_PLAYING)):
            
            delivery_map_objects_to_draw = []
            if gsm.delivery_start_runway: delivery_map_objects_to_draw.append(gsm.delivery_start_runway)
            delivery_map_objects_to_draw.extend(gsm.delivery_checkpoints_list) 
            if gsm.delivery_destination_runway: delivery_map_objects_to_draw.append(gsm.delivery_destination_runway)
            
            gsm.minimap.draw(screen, gsm.player, [], delivery_map_objects_to_draw, is_delivery_mode=True, delivery_active_target=gsm.delivery_active_target_object)

        if gsm.game_state == config.STATE_PAUSED:
            draw_pause_menu_screen(screen)

    elif gsm.game_state == config.STATE_START_SCREEN:
        draw_start_screen_content(screen); gsm.foreground_clouds_group.draw(screen)
    elif gsm.game_state == config.STATE_DIFFICULTY_SELECT:
        draw_difficulty_select_screen(screen, gsm.selected_difficulty_option); draw_text(screen, "ESC for Mode Select", 18, 100, config.SCREEN_HEIGHT - 30, config.PASTEL_LIGHT_GRAY, font_name=config.HUD_FONT_NAME, center=True); gsm.foreground_clouds_group.draw(screen) 
    elif gsm.game_state == config.STATE_MODE_SELECT:
        draw_mode_select_screen(screen, gsm.selected_mode_option); draw_text(screen, "ESC for Start Screen", 18, 100, config.SCREEN_HEIGHT - 30, config.PASTEL_LIGHT_GRAY, font_name=config.HUD_FONT_NAME, center=True); gsm.foreground_clouds_group.draw(screen) 
    elif gsm.game_state == config.STATE_RACE_LAPS_SELECT:
        draw_laps_select_screen(screen, gsm.selected_laps_option, gsm.lap_options); draw_text(screen, "ESC for Difficulty Select", 18, 120, config.SCREEN_HEIGHT - 30, config.PASTEL_LIGHT_GRAY, font_name=config.HUD_FONT_NAME, center=True); gsm.foreground_clouds_group.draw(screen) 
    elif gsm.game_state == config.STATE_TARGET_REACHED_OPTIONS: 
        draw_target_reached_options_screen(screen, gsm.current_level, gsm.time_taken_for_level); gsm.foreground_clouds_group.draw(screen)
    elif gsm.game_state == config.STATE_POST_GOAL_MENU: 
        draw_post_goal_menu_screen(screen, gsm.current_level); gsm.foreground_clouds_group.draw(screen)
    elif gsm.game_state == config.STATE_RACE_POST_OPTIONS: 
        draw_race_post_options_screen(screen, gsm.time_taken_for_level, gsm.player_race_lap_times); gsm.foreground_clouds_group.draw(screen)
    elif gsm.game_state == config.STATE_DOGFIGHT_ROUND_COMPLETE:
        draw_dogfight_round_complete_screen(screen, gsm.dogfight_current_round, gsm.time_taken_for_level); gsm.foreground_clouds_group.draw(screen)
    elif gsm.game_state == config.STATE_DOGFIGHT_GAME_OVER_CONTINUE:
        draw_dogfight_game_over_continue_screen(screen, gsm.dogfight_current_round); gsm.foreground_clouds_group.draw(screen)
    elif gsm.game_state == config.STATE_DELIVERY_COMPLETE:
        # current_level was incremented for the *next* mission in gsm.update_game_logic
        # So for display of the completed mission, use current_level - 1
        completed_delivery_mission_number = gsm.current_level - 1 if gsm.current_level > 0 else 0 # Should always be > 0 here
        
        wingman_newly_acquired = gsm.wingman_was_actually_unlocked_this_turn 
        current_total_wingmen = gsm.unlocked_wingmen_count 
        draw_delivery_complete_screen(screen, completed_delivery_mission_number, gsm.time_taken_for_level, wingman_newly_acquired, current_total_wingmen); gsm.foreground_clouds_group.draw(screen)
    elif gsm.game_state == config.STATE_GAME_OVER:
        draw_game_over_screen_content(screen, gsm.final_score, gsm.current_level, gsm.high_scores, config.current_game_mode, gsm.total_race_laps, gsm.dogfight_current_round, gsm.successful_deliveries_count); gsm.foreground_clouds_group.draw(screen)

    pygame.display.flip()
pygame.quit()