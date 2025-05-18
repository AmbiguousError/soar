# Pastel Glider - Floating Dreams ☁️✨

Welcome to Pastel Glider, a tranquil flying experience designed to let you soar through an endless, procedurally generated pastel world. Catch thermals, navigate gentle winds, and enjoy the serene landscapes as you aim for new heights in Free Fly mode, or test your skills against AI opponents in the new Race mode!

## Description

Pastel Glider offers two distinct ways to enjoy the skies:

* **Free Fly Mode**: A chill game about the joy of flight. There are no enemies, no complex scoring systems beyond reaching your altitude goal – just you, your glider, and an ever-changing, soft-hued world to explore. It's perfect for unwinding and enjoying a moment of peace.
* **Race Mode**: Compete against AI-controlled gliders on a randomly generated course. Navigate through a series of markers for a set number of laps and try to achieve the best time.

Both modes feature the same beautiful pastel aesthetics and core gliding mechanics.

## How to Play

### General Controls:
* **UP Arrow**: Increase glider speed (trading potential height for speed).
* **DOWN Arrow**: Decrease glider speed (allowing for zoom climbs, trading speed for height).
* **LEFT/RIGHT Arrows**: Bank the glider to turn.

### Menu Navigation:
* Use **UP/DOWN Arrows** to navigate menu options.
* Press **ENTER** to confirm selections.
* **ESCAPE**:
    * During Free Fly or Race gameplay: Returns to the main menu.
    * After reaching a Free Fly level goal and choosing to "Continue Flying": Opens a menu to go to the next level, quit, or resume.

## Features

* **Endless Pastel World**: Each level or race generates a brand new, unique map with diverse, soft-colored biomes including plains, forests, mountains, deserts, and rivers.
* **Dynamic Wind**: Experience gentle wind changes with each new level/race, affecting your flight path. A handy weather vane on your HUD shows the current wind direction and strength.
* **Thermals**: Ride columns of rising air (thermals) to gain altitude effortlessly. Their strength and size vary, and they are more prominent over certain land types. (Present in both Free Fly and Race modes).
* **Multiple Difficulty Modes**:
    * **N00b**: For a super relaxed experience with very large, long-lasting, and extremely powerful thermals.
    * **Easy**: Thermals are noticeably stronger and more helpful.
    * **Normal**: A balanced, standard gliding challenge.
* **Altitude Meter with VSI**: Keep an eye on your height and your rate of climb/descent with the on-screen indicator.
* **Chilled Aesthetics**: Soft pastel colors for the world, glider, and UI elements create a calming visual experience.
* **Parallax Clouds**: Gentle clouds drift by, adding to the sense of depth and atmosphere.

## Game Modes

### 1. Free Fly Mode
* **Goal**: Reach an altitude of **1000 meters** in each level to advance.
* **Progression**: Each time you complete a level, a new, unique map is generated for the next one.
* **Options After Goal**:
    * **Move On**: Start the next level.
    * **Continue Flying**: Keep exploring the current level at your leisure. Pressing `ESCAPE` during this phase will bring up a menu to proceed to the next level, quit to the main menu, or resume flying the current level.

### 2. Race Mode
* **Goal**: Complete the selected number of laps by flying through a sequence of randomly placed markers.
* **Laps**: Choose between 1, 3, or 5 laps.
* **AI Opponents**: Race against a number of AI-controlled gliders.
* **Collision**: Colliding with an AI glider (or an AI colliding with another AI) will result in a speed penalty and a slight nudge for both.
* **Minimap**: A minimap helps you navigate the course and see the position of markers and opponents.
* **HUD**: Displays current lap, next marker information, and a directional arrow to the active marker.
* **Race Completion**: After finishing all laps, your total race time is displayed.

## Running the Game

Pastel Glider is built with Pygame. To run it:

1.  Ensure you have Python and Pygame installed.
    * If you don't have Pygame, you can usually install it via pip:
        ```bash
        pip install pygame
        ```
2.  Save the game code as a Python file (e.g., `pastel_glider.py` or `soar.py`).
3.  Run the file from your terminal:
    ```bash
    python pastel_glider.py
    ```

Sit back, relax, and enjoy the flight, or feel the thrill of the race!
