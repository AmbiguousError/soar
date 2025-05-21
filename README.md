# Pastel Glider - Floating Dreams ☁️✨

Pastel Glider is a 2D gliding simulation game built with Pygame. Players can explore procedurally generated landscapes in Free Fly mode, utilizing thermals to gain altitude and unlock wingmen, compete against AI opponents in Race mode, or engage in aerial combat in the Dogfight mode. The game features a soft pastel aesthetic and physics-based glider controls.

## Features

* **Four Game Modes:**
    * **Free Fly:** Explore an endless, procedurally generated world. Reach altitude goals to progress through levels and unlock AI wingmen who will fly in formation with you.
    * **Race Mode:** Compete against AI-controlled gliders on a course defined by markers. Race for the best lap times and total race times.
    *  **Dogfight Mode:** Engage in combat against waves of AI enemy gliders. Survive rounds of increasing difficulty by shooting down opponents. Manage your health and strategically engage foes.
+    * **Delivery Mode:** Take on the role of a cargo pilot. Start by taking off from a designated runway, fly to a destination runway, and perform a successful landing to complete the delivery.health and strategically engage foes.
* **Physics-Based Flight:**
    * Control your glider's speed and bank angle.
    * Manage altitude by finding and using thermals for lift.
    * Experience stalls if your speed drops too low, with a significant altitude penalty.
    * Turning circle size is realistically affected by speed.
* **Combat Mechanics (Dogfight Mode):**
    * Player and AI gliders have health.
    * Shoot bullets to damage opponents.
    * Bullets have defined speed, range, and damage.
    * Shooting cooldowns prevent rapid fire.
* **Dynamic AI:**
    * **Race AI:** Opponents have distinct personalities affecting their speed and turning. They employ strategies like boosting on straights and slowing for turns.
    * **Wingmen (Free Fly):** Unlock AI companions who follow the player in a casual formation, each with unique flight characteristics.
    * **Dogfight AI:** Enemies will engage the player, attempting to shoot them down while performing evasive maneuvers based on their aggression and evasiveness factors. They spawn in increasing numbers per round and have varying shooting cooldowns.
* **Procedurally Generated Endless World:**
    * Each new level or game session features a unique map generated using seeded noise functions.
    * Diverse biomes including water, plains, forests, mountains, and deserts.
    * Land types influence thermal generation probability.
* **Dynamic Environment:**
    * Simulated wind affecting glider movement.
    * Foreground clouds for visual depth.
* **User Interface:**
    * HUD displaying critical flight information (altitude, speed, level/lap/round, time, stall warning).
    * In Dogfight mode, the HUD also shows player health and remaining enemies for the current round.
    * Health bars are displayed above gliders in Dogfight mode.
    * Height indicator bar with VSI (Vertical Speed Indicator).
    * Minimap for Race mode showing player, AI, and markers.
    * Wind direction and strength indicator (weather vane).
    * Marker direction dial in Race mode to guide the player.
* **Difficulty Levels:**
    * N00b, Easy, and Normal settings affecting thermal strength/frequency and player glider turning agility.
* **High Score Tracking (Session-based):**
    * Longest flight time (Free Fly).
    * Highest altitude achieved (Free Fly).
    * Best individual lap time (Race).
    * Best total race time for different lap configurations (Race).
    * Highest round reached in Dogfight mode is displayed on Game Over.
* **Pause Functionality:**
    * Pause the game during active play with options to continue or quit.

## How to Run

1.  **Dependencies:**
    * Python 3.x
    * Pygame library: `pip install pygame`

2.  **Running the Game:**
    * Ensure all Python files (`main.py`, `config.py`, `sprites.py`, `map_generation.py`, `ui.py`, `game_state_manager.py`) are in the same directory.
    * Execute the main script from your terminal:
        ```bash
        python main.py
        ```
        (Or `python3 main.py` depending on your Python installation)

## File Structure

The project is organized into the following Python modules:

* `main.py`: The main entry point of the game. Initializes Pygame, manages the main game loop, event handling, and orchestrates calls to other modules.
* `config.py`: Contains all global constants, game settings, color definitions, physics parameters, and combat mechanic values (health, damage, bullet properties, AI behavior in dogfights).
* `sprites.py`: Defines all the game's sprite classes (e.g., `PlayerGlider`, `AIGlider`, `Thermal`, `RaceMarker`, `ForegroundCloud`, `Bullet`). Includes combat-related attributes and methods in glider classes.
* `map_generation.py`: Handles the logic for procedural generation of the endless map and its biomes.
* `ui.py`: Manages user interface elements, including text rendering, the minimap, HUD components, dials, health bars (drawing logic initiated here or in sprites), and drawing functions for various game screens (menus, game over, dogfight round complete/game over screens).
* `game_state_manager.py`: Manages the core game state variables, sprite groups (including dogfight enemies and bullets), and high-level game logic functions like starting new levels/rounds, managing dogfight progression, and resetting the game.

## Controls

* **Up Arrow:** Increase glider speed / Nose down (dive slightly).
* **Down Arrow:** Decrease glider speed / Nose up (climb slightly, trades speed for height).
* **Left Arrow:** Bank glider left.
* **Right Arrow:** Bank glider right.
* **Space Bar:** Shoot (in Dogfight mode).
* **Enter:** Confirm selections in menus.
* **Escape:**
    * Pause the game during active play (Free Fly, Race, or Dogfight).
    * Navigate back or to options in some menu screens.
* **Menu Specific Keys (as indicated on screen):**
    * `C`: Continue (from Pause, Target Reached options, or Dogfight Game Over).
    * `M`: Move to next level (from Target Reached options).
    * `N`: Next Level / New Race / Next Round (from Post-Goal, Post-Race, or Dogfight Round Complete options).
    * `F`: Free Fly This Map (from Post-Race options).
    * `Q`: Quit to Main Menu (from Pause, other option screens, or game over screens).
    * `R`: Resume Flying (from Post-Goal menu).

