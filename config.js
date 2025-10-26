// config.js
// Stores all game constants and configuration settings.

const config = {
    // --- Screen & Display ---
    SCREEN_WIDTH: 1200,
    SCREEN_HEIGHT: 900,
    HUD_HEIGHT: 100,
    MINIMAP_WIDTH: 200,
    MINIMAP_HEIGHT: 150,
    MINIMAP_MARGIN: 10,
    MINIMAP_ALPHA: 200,

    // --- Glider Physics & Control ---
    INITIAL_HEIGHT: 500,
    INITIAL_SPEED: 3,
    MIN_SPEED: 1.0,
    MAX_SPEED: 7,
    ACCELERATION: 0.12,
    STALL_SPEED: 1.8,
    STALL_SINK_PENALTY: 0.25,
    GRAVITY_BASE_PULL: 0.22,
    LIFT_PER_SPEED_UNIT: 0.03,
    MINIMUM_SINK_RATE: 0.04,
    DIVE_TO_SPEED_FACTOR: 0.08,
    ZOOM_CLIMB_FACTOR: 1.8,
    MAX_BANK_ANGLE: 45,
    BANK_RATE: 2,
    BASE_PLAYER_BANK_TO_DEGREES_PER_FRAME: 0.06,
    NOOB_TURN_FACTOR: 2.0,
    EASY_TURN_FACTOR: 1.5,
    NORMAL_TURN_FACTOR: 1.0,
    GLIDER_COLLISION_RADIUS: 20,

    // --- AI Specific ---
    NUM_AI_OPPONENTS: 3, // Max number of racers
    AI_TARGET_RACE_ALTITUDE: 450,
    AI_ALTITUDE_CORRECTION_RATE: 0.2,
    AI_BASE_SPEED_MIN: 2.5,
    AI_BASE_SPEED_MAX: 4.5,
    AI_BASE_TURN_RATE_SCALAR: 0.08,
    AI_MARKER_APPROACH_SLOWDOWN_DISTANCE: 200,
    AI_MARKER_APPROACH_MIN_SPEED_FACTOR: 0.6,
    AI_TARGET_SPEED_UPDATE_INTERVAL: 120,
    AI_SPEED_VARIATION_FACTOR: 0.2,
    AI_STRAIGHT_BOOST_THRESHOLD_ANGLE: 15,
    AI_STRAIGHT_BOOST_MIN_DISTANCE: 400,

    AI_GLIDER_COLORS_LIST: [
        ['#fab4b4', '#ffc8c8'],
        ['#b4fab4', '#c8ffc8'],
        ['#c8b4fa', '#dcc8ff'],
        ['#fafab4', '#ffffc8'],
        ['#b4e6fa', '#c8f0ff'],
        ['#dcdcdc', '#ebebeb'],
    ],

    // Wingman Specific
    MAX_WINGMEN: 5,
    WINGMAN_FOLLOW_DISTANCE_X: -80,
    WINGMAN_FOLLOW_DISTANCE_Y_BASE: 60,
    WINGMAN_FORMATION_SPREAD: 40,
    WINGMAN_CASUALNESS_FACTOR: 0.05,
    WINGMAN_ALTITUDE_CORRECTION_RATE: 0.1,

    // --- Combat Mechanics ---
    PLAYER_MAX_HEALTH: 100,
    AI_MAX_HEALTH: 30, // AI are generally weaker
    BULLET_SPEED: 15,
    BULLET_RANGE: 600, // Max distance a bullet travels
    BULLET_DAMAGE: 10,
    PLAYER_SHOOT_COOLDOWN: 15, // Frames between player shots
    AI_SHOOT_COOLDOWN_BASE: 45, // Base frames between AI shots
    DOGFIGHT_AI_SHOOTING_RANGE: 500,
    DOGFIGHT_AI_SHOOTING_CONE_ANGLE: 10, // Degrees: AI shoots if player is within this angle
    BULLET_COLOR: '#ff6400', // Bright orange/red
    HEALTH_BAR_WIDTH: 50,
    HEALTH_BAR_HEIGHT: 5,
    HEALTH_BAR_COLOR_GOOD: '#00c800',
    HEALTH_BAR_COLOR_MEDIUM: '#c8c800',
    HEALTH_BAR_COLOR_BAD: '#c80000',
    HEALTH_BAR_BACKGROUND_COLOR: '#323232',

    // --- Dogfight Mode Specifics ---
    DOGFIGHT_INITIAL_ENEMIES: 1,
    DOGFIGHT_ENEMIES_PER_ROUND_INCREASE: 1,
    DOGFIGHT_MAX_ENEMIES_ON_SCREEN: 5, // To prevent overwhelming the player/performance
    DOGFIGHT_AI_EVASIVENESS_FACTOR: 0.3, // How much AI tries to dodge (0-1)
    DOGFIGHT_AI_AGGRESSION_FACTOR: 0.7, // How often AI tries to engage vs. reposition (0-1)

    // --- Contrail ---
    CONTRAIL_LENGTH: 60,
    CONTRAIL_POINT_DELAY: 2,

    // --- Thermals ---
    BASE_THERMAL_SPAWN_RATE: 100,
    THERMAL_SPAWN_RATE_INCREASE_PER_LEVEL: 18,
    NORMAL_MIN_THERMAL_RADIUS: 25,
    NORMAL_MAX_THERMAL_RADIUS: 60,
    NORMAL_MIN_THERMAL_LIFESPAN: 450,
    NORMAL_MAX_THERMAL_LIFESPAN: 1300,
    MIN_THERMAL_LIFT_POWER: 0.22,
    MAX_THERMAL_LIFT_POWER: 0.60,
    NOOB_MIN_THERMAL_RADIUS: 60,
    NOOB_MAX_THERMAL_RADIUS: 120,
    NOOB_MIN_THERMAL_LIFESPAN: 900,
    NOOB_MAX_THERMAL_LIFESpan: 2200,
    EASY_MODE_THERMAL_LIFT_MULTIPLIER: 1.75,
    NOOB_MODE_THERMAL_LIFT_MULTIPLIER: 2.75,
    THERMAL_SPAWN_AREA_WIDTH: 1500, // SCREEN_WIDTH + 300
    THERMAL_SPAWN_AREA_HEIGHT: 1200, // SCREEN_HEIGHT + 300
    THERMAL_BASE_ALPHA: 100,
    THERMAL_ACCENT_ALPHA: 120,

    // --- Map ---
    TILE_SIZE: 40,
    MAP_TILE_OUTLINE_WIDTH: 1,
    DEEP_WATER_THRESH: 0.18,
    SHALLOW_WATER_THRESH: 0.22,
    BEACH_THRESH: 0.24,
    MOUNTAIN_BASE_THRESH: 0.60,
    MOUNTAIN_PEAK_THRESH: 0.75,
    DESERT_THRESH: 0.20,
    GRASSLAND_THRESH: 0.40,
    TEMPERATE_FOREST_THRESH: 0.65,
    RUNWAY_MIN_DISTANCE_APART: 1500, // Min distance between start and destination runways
    RUNWAY_MAX_PLACEMENT_ATTEMPTS: 100, // Attempts to find suitable runway spots

    // --- Race Mode Specific ---
    RACE_MARKER_RADIUS_WORLD: 75,
    RACE_MARKER_VISUAL_RADIUS_MAP: 6,
    RACE_MARKER_VISUAL_RADIUS_WORLD: 25,
    DEFAULT_RACE_LAPS: 3,
    RACE_COURSE_AREA_HALFWIDTH: 2500, // Also used for Delivery mode map area

    // --- Delivery Mode Specific ---
    DELIVERY_RUNWAY_VISUAL_RADIUS_WORLD: 40, // Visual size on map
    DELIVERY_RUNWAY_INTERACTION_RADIUS: 90, // For landing detection
    DELIVERY_LANDING_MAX_SPEED: 2.0,       // Max speed for successful landing
    DELIVERY_LANDING_MAX_HEIGHT_ABOVE_GROUND: 50, // Max height above "runway level"
    DELIVERIES_TO_UNLOCK_WINGMAN: 1,      // How many successful deliveries to unlock one wingman
    DELIVERY_START_HEIGHT_OFFSET: 50,     // Start slightly above runway for takeoff
    DELIVERY_START_SPEED_FACTOR: 0.6,     // Start at a fraction of initial speed
    DELIVERY_MIN_DISTANCE_INCREASE_FACTOR: 0.1, // Factor by which min distance between START and END runways increases

    // --- Delivery Mode Checkpoints ---
    DELIVERY_CHECKPOINT_VISUAL_RADIUS_WORLD: 20,
    DELIVERY_CHECKPOINT_INTERACTION_RADIUS: 60,
    DELIVERY_CHECKPOINT_COLOR_INACTIVE: 'rgba(200, 200, 0, 0.58)',  // Dim Yellow
    DELIVERY_CHECKPOINT_COLOR_ACTIVE: 'rgba(255, 255, 0, 0.86)',   // Bright Yellow
    DELIVERY_CHECKPOINTS_ADD_PER_N_LEVELS: 3,
    DELIVERY_MAX_CHECKPOINTS: 5,
    DELIVERY_CHECKPOINT_MINIMAP_RADIUS: 4,
    DELIVERY_CHECKPOINT_OFFSET_RANGE: 300,

    // New constants for varied checkpoint paths and distances:
    DELIVERY_CHECKPOINT_BASE_LEG_DISTANCE: 800,
    DELIVERY_CHECKPOINT_LEG_DISTANCE_SCALE_PER_LEVEL: 75,
    DELIVERY_CHECKPOINT_MAX_ANGLE_DEVIATION: 40,
    DELIVERY_CHECKPOINT_MIN_NEXT_LEG_DISTANCE_FACTOR: 0.5,

    // --- Wind ---
    MAX_WIND_STRENGTH: 1.0,

    // --- Clouds ---
    NUM_FOREGROUND_CLOUDS: 15,
    MIN_CLOUD_SPEED_FACTOR: 1.5,
    MAX_CLOUD_SPEED_FACTOR: 2.5,
    CLOUD_MIN_ALPHA: 40,
    CLOUD_MAX_ALPHA: 100,

    // --- Game Mechanics ---
    TARGET_HEIGHT_PER_LEVEL: 1000,
    START_HEIGHT_NEW_LEVEL: 250,
    EXPLOSION_DURATION_TICKS: 40,

    // --- Height Indicator ---
    INDICATOR_WIDTH: 20,
    INDICATOR_X_MARGIN: 20,
    INDICATOR_Y_MARGIN_FROM_HUD: 20,
    VSI_ARROW_SIZE: 8,

    // --- HUD Font ---
    HUD_FONT_NAME: "Consolas",
    HUD_FONT_SIZE_LARGE: 24,
    HUD_FONT_SIZE_NORMAL: 22,
    HUD_FONT_SIZE_SMALL: 20,

    // --- Game States ---
    STATE_START_SCREEN: 0,
    STATE_DIFFICULTY_SELECT: 1,
    STATE_MODE_SELECT: 2,
    STATE_PLAYING_FREE_FLY: 3,
    STATE_TARGET_REACHED_OPTIONS: 4,
    STATE_TARGET_REACHED_CONTINUE_PLAYING: 5,
    STATE_POST_GOAL_MENU: 6,
    STATE_RACE_LAPS_SELECT: 7,
    STATE_RACE_PLAYING: 8,
    STATE_RACE_COMPLETE: 9,
    STATE_GAME_OVER: 10,
    STATE_PAUSED: 11,
    STATE_RACE_POST_OPTIONS: 12,
    STATE_DOGFIGHT_PLAYING: 13,
    STATE_DOGFIGHT_ROUND_COMPLETE: 14,
    STATE_DOGFIGHT_GAME_OVER_CONTINUE: 15,
    STATE_DELIVERY_PLAYING: 16,
    STATE_DELIVERY_COMPLETE: 17,

    // --- Game Difficulty ---
    DIFFICULTY_NOOB: 0, DIFFICULTY_EASY: 1, DIFFICULTY_NORMAL: 2,
    difficulty_options_map: { 0: "N00b", 1: "Easy", 2: "Normal" },
    game_difficulty: 2, // DIFFICULTY_NORMAL

    // --- Game Mode ---
    MODE_FREE_FLY: 0, MODE_RACE: 1, MODE_DOGFIGHT: 2, MODE_DELIVERY: 3,
    current_game_mode: 0, // MODE_FREE_FLY

    // --- Pastel Colors ---
    PASTEL_BLACK: '#32323c', PASTEL_WHITE: '#f5f5fa', PASTEL_DARK_GRAY: '#b4b4be', PASTEL_GRAY: '#c8c8d2', PASTEL_LIGHT_GRAY: '#e6e6f0',
    PASTEL_RED: '#ff9696', PASTEL_GREEN_TARGET: '#adffad', PASTEL_GOLD: '#ffe696', PASTEL_CLOUD: '#ebf0f5', PASTEL_HUD_PANEL: 'rgba(190, 200, 210, 0.7)',
    PASTEL_MINIMAP_BACKGROUND: 'rgba(170, 180, 190, 0.78)', PASTEL_MINIMAP_BORDER: '#8c96a0', PASTEL_MARKER_COLOR: '#ffaaaa', PASTEL_ACTIVE_MARKER_COLOR: '#adffad',
    PASTEL_WATER_DEEP: '#bec8f0', PASTEL_WATER_SHALLOW: '#d2ebfa', PASTEL_PLAINS: '#c8f0c8', PASTEL_GRASSLAND: '#befabe',
    PASTEL_FOREST_TEMPERATE: '#b4dcb4', PASTEL_FOREST_DENSE: '#a0c8a0', PASTEL_MOUNTAIN_BASE: '#d2d2c8', PASTEL_MOUNTAIN_PEAK: '#ebebfa',
    PASTEL_SAND_BEACH: '#faf0d2', PASTEL_SAND_DESERT: '#f5e6c8', PASTEL_RIVER: '#c8e1fa',
    PASTEL_GLIDER_BODY: '#b4b4fa', PASTEL_GLIDER_WING: '#c8c8ff',
    PASTEL_THERMAL_PRIMARY: '#ffc8c8', PASTEL_THERMAL_ACCENT: '#f5f5fa', PASTEL_INDICATOR_COLOR: '#96a0aa', PASTEL_INDICATOR_GROUND: '#c8bec4',
    PASTEL_VSI_CLIMB: '#adffad', PASTEL_VSI_SINK: '#ffaaaa', PASTEL_TEXT_COLOR_HUD: '#464650', PASTEL_CONTRAIL_COLOR: '#464650',
    MAP_TILE_OUTLINE_COLOR: '#d7dce1',
    PASTEL_RUNWAY_COLOR: '#64646e', // Dark grey for runway
    PASTEL_RUNWAY_DESTINATION_COLOR: '#648264', // Greenish tint for destination
    PASTEL_RUNWAY_START_COLOR: '#826464', // Reddish tint for start

    // --- Touch Controls ---
    TOUCH_CONTROLS_ENABLED: true,
    TOUCH_BUTTON_ALPHA: 0.5,
    TOUCH_BUTTON_COLOR: '#c8c8d2',
    TOUCH_BUTTON_PRESSED_COLOR: '#f5f5fa',
    TOUCH_CONTROLS: {
        'up': { x: 150, y: 700, width: 80, height: 80, label: '▲', key: 'ArrowUp' },
        'down': { x: 150, y: 800, width: 80, height: 80, label: '▼', key: 'ArrowDown' },
        'left': { x: 50, y: 750, width: 80, height: 80, label: '◀', key: 'ArrowLeft' },
        'right': { x: 250, y: 750, width: 80, height: 80, label: '▶', key: 'ArrowRight' },
        'fire': { x: 1050, y: 750, width: 100, height: 100, label: 'FIRE', key: ' ' },
        'exit': { x: 10, y: 10, width: 80, height: 40, label: 'EXIT', key: 'Escape' }
    },

    // --- Land Types ---
    LAND_TYPE_WATER_DEEP: 0, LAND_TYPE_WATER_SHALLOW: 1, LAND_TYPE_PLAINS: 2, LAND_TYPE_FOREST_TEMPERATE: 3, LAND_TYPE_MOUNTAIN_BASE: 4,
    LAND_TYPE_SAND_DESERT: 5, LAND_TYPE_MOUNTAIN_PEAK: 6, LAND_TYPE_RIVER: 7, LAND_TYPE_FOREST_DENSE: 8, LAND_TYPE_GRASSLAND: 9, LAND_TYPE_SAND_BEACH: 10,
    LAND_TYPE_COLORS: {
        0: '#bec8f0', 1: '#d2ebfa', 2: '#c8f0c8', 9: '#befabe', 3: '#b4dcb4', 8: '#a0c8a0', 4: '#d2d2c8', 6: '#ebebfa', 5: '#f5e6c8', 10: '#faf0d2', 7: '#c8e1fa',
    },
    LAND_TYPE_THERMAL_PROBABILITY: {
        0: 0.00, 1: 0.01, 2: 0.6, 9: 0.7, 3: 0.3, 8: 0.1, 4: 0.5, 6: 0.05, 5: 0.9, 10: 0.8, 7: 0.02,
    },
    RUNWAY_SUITABLE_LAND_TYPES: [], // To be populated after LAND_TYPE constants are defined

    // Map Generation Noise Parameters
    ELEVATION_CONTINENT_SCALE: 60.0, ELEVATION_MOUNTAIN_SCALE: 15.0, ELEVATION_HILL_SCALE: 5.0,
    MOISTURE_PRIMARY_SCALE: 40.0, MOISTURE_SECONDARY_SCALE: 10.0,
    P_CONT: [73856093, 19349663], P_MNT: [83492791, 52084219], P_HILL: [39119077, 66826529],
    P_MOIST_P: [23109781, 92953093], P_MOIST_S: [47834583, 11634271],
    NUM_MAJOR_RIVERS: 3,
};

config.RUNWAY_SUITABLE_LAND_TYPES = [config.LAND_TYPE_PLAINS, config.LAND_TYPE_GRASSLAND, config.LAND_TYPE_SAND_DESERT, config.LAND_TYPE_SAND_BEACH];
