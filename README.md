# Pastel Glider - Floating Dreams ☁️✨

Pastel Glider is a 2D gliding simulation game built with Pygame. Players can explore procedurally generated landscapes in Free Fly mode, utilizing thermals to gain altitude and unlock wingmen, or compete against AI opponents in Race mode. The game features a soft pastel aesthetic and physics-based glider controls.

<video src="https://github.com/AmbiguousError/soar/blob/main/PastelGlider.mp4" data-canonical-src="https://github.com/AmbiguousError/soar/blob/main/PastelGlider.mp4" controls="controls" muted="muted" class="d-block rounded-bottom-2 border-top width-fit" style="max-height:640px; min-height: 200px">
</video> 

## Features

* **Two Game Modes:**
    * **Free Fly:** Explore an endless, procedurally generated world. Reach altitude goals to progress through levels and unlock AI wingmen who will fly in formation with you.
    * **Race Mode:** Compete against AI-controlled gliders on a course defined by markers. Race for the best lap times and total race times.
* **Physics-Based Flight:**
    * Control your glider's speed and bank angle.
    * Manage altitude by finding and using thermals for lift.
    * Experience stalls if your speed drops too low, with a significant altitude penalty.
    * Turning circle size is realistically affected by speed.
* **Dynamic AI:**
    * **Race AI:** Opponents have distinct personalities affecting their speed and turning. They employ strategies like boosting on straights and slowing for turns.
    * **Wingmen (Free Fly):** Unlock AI companions who follow the player in a casual formation, each with unique flight characteristics.
* **Procedurally Generated Endless World:**
    * Each new level or game session features a unique map generated using seeded noise functions.
    * Diverse biomes including water, plains, forests, mountains, and deserts.
    * Land types influence thermal generation probability.
* **Dynamic Environment:**
    * Simulated wind affecting glider movement.
    * Foreground clouds for visual depth.
* **User Interface:**
    * HUD displaying critical flight information (altitude, speed, level/lap, time, stall warning).
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
* `config.py`: Contains all global constants, game settings, color definitions, and physics parameters.
* `sprites.py`: Defines all the game's sprite classes (e.g., `PlayerGlider`, `AIGlider`, `Thermal`, `RaceMarker`, `ForegroundCloud`).
* `map_generation.py`: Handles the logic for procedural generation of the endless map and its biomes.
* `ui.py`: Manages user interface elements, including text rendering, the minimap, HUD components, dials, and drawing functions for various game screens (menus, game over, etc.).
* `game_state_manager.py`: Manages the core game state variables, sprite groups, and high-level game logic functions like starting new levels and resetting the game.

## Controls

* **Up Arrow:** Increase glider speed / Nose down (dive slightly).
* **Down Arrow:** Decrease glider speed / Nose up (climb slightly, trades speed for height).
* **Left Arrow:** Bank glider left.
* **Right Arrow:** Bank glider right.
* **Enter:** Confirm selections in menus.
* **Escape:**
    * Pause the game during active play (Free Fly or Race).
    * Navigate back or to options in some menu screens.
* **Menu Specific Keys (as indicated on screen):**
    * `C`: Continue (from Pause or Target Reached options).
    * `M`: Move to next level (from Target Reached options).
    * `N`: Next Level / New Race (from Post-Goal or Post-Race options).
    * `F`: Free Fly This Map (from Post-Race options).
    * `Q`: Quit to Main Menu (from Pause or other option screens).
    * `R`: Resume Flying (from Post-Goal menu).

## Future Enhancements (Ideas)

* Persistent high scores (saving/loading from a file).
* Sound effects and music.
* More varied thermal types or ridge lift.
* More complex AI behaviors (e.g., AI using thermals).
* Additional glider types with different flight characteristics.
* More detailed terrain features.
* Weather effects (e.g., rain, stronger gusts).

