// gameStateManager.js

const gameStateManager = {
    // --- Game State ---
    gameState: config.STATE_START_SCREEN,
    selectedModeOption: config.MODE_FREE_FLY,

    // --- Game Variables ---
    minimap: new Minimap(config),
    player: new Player(config),
    thermals: [],
    tileTypeCache: new Map(),
    currentMapOffsetX: Math.random() * 400000 - 200000,
    currentMapOffsetY: Math.random() * 400000 - 200000,
    thermalSpawnTimer: 0,
    currentThermalSpawnRate: config.BASE_THERMAL_SPAWN_RATE,
    raceCourseMarkers: [],
    aiGliders: [],

    // --- Functions ---
    setState(newState) {
        this.gameState = newState;
    },

    startNewLevel() {
        this.player.reset();
        this.thermals = [];
        this.tileTypeCache.clear();
        this.currentMapOffsetX = Math.random() * 400000 - 200000;
        this.currentMapOffsetY = Math.random() * 400000 - 200000;
        regenerateRiverParameters();
        this.setState(config.STATE_PLAYING_FREE_FLY);
    },

    generateRaceCourse(numMarkers = 8) {
        this.raceCourseMarkers = [];
        for (let i = 0; i < numMarkers; i++) {
            const marker = new RaceMarker(
                config,
                Math.random() * config.RACE_COURSE_AREA_HALFWIDTH * 2 - config.RACE_COURSE_AREA_HALFWIDTH,
                Math.random() * config.RACE_COURSE_AREA_HALFWIDTH * 2 - config.RACE_COURSE_AREA_HALFWIDTH,
                i + 1
            );
            this.raceCourseMarkers.push(marker);
        }
    },

    startRace() {
        this.player.reset();
        this.generateRaceCourse();
        this.aiGliders = [];
        for (let i = 0; i < config.NUM_AI_OPPONENTS; i++) {
            const angleOffset = Math.PI + (i - config.NUM_AI_OPPONENTS / 2.0) * (Math.PI / 6);
            const distOffset = 100 + i * 40;
            const aiStartX = this.player.worldX + distOffset * Math.cos(angleOffset + this.player.heading * Math.PI / 180);
            const aiStartY = this.player.worldY + distOffset * Math.sin(angleOffset + this.player.heading * Math.PI / 180);
            const [bodyColor, wingColor] = config.AI_GLIDER_COLORS_LIST[i % config.AI_GLIDER_COLORS_LIST.length];
            const profile = {
                speedFactor: Math.random() * 0.2 + 0.9,
                turnFactor: Math.random() * 0.3 + 0.85,
            };
            this.aiGliders.push(new AIGlider(config, aiStartX, aiStartY, bodyColor, wingColor, profile));
        }
        this.setState(config.STATE_RACE_PLAYING);
    },

    startDogfight() {
        this.player.reset();
        this.dogfightCurrentRound = 1;
        this.startDogfightRound(1);
        this.setState(config.STATE_DOGFIGHT_PLAYING);
    },

    startDogfightRound(roundNumber) {
        this.dogfightCurrentRound = roundNumber;
        this.dogfightEnemiesToSpawnThisRound = Math.min(
            config.DOGFIGHT_INITIAL_ENEMIES + (roundNumber - 1) * config.DOGFIGHT_ENEMIES_PER_ROUND_INCREASE,
            config.DOGFIGHT_MAX_ENEMIES_ON_SCREEN
        );
        this.aiGliders = [];
        for (let i = 0; i < this.dogfightEnemiesToSpawnThisRound; i++) {
            const angle = Math.random() * 2 * Math.PI;
            const distance = Math.random() * (config.SCREEN_WIDTH * 0.3) + config.SCREEN_WIDTH * 0.6;
            const startX = this.player.worldX + distance * Math.cos(angle);
            const startY = this.player.worldY + distance * Math.sin(angle);
            const [bodyColor, wingColor] = config.AI_GLIDER_COLORS_LIST[i % config.AI_GLIDER_COLORS_LIST.length];
            const profile = {
                speedFactor: Math.random() * 0.3 + 0.8,
                turnFactor: Math.random() * 0.3 + 0.9,
            };
            this.aiGliders.push(new AIGlider(config, startX, startY, bodyColor, wingColor, profile, 'dogfight'));
        }
    },

    startDelivery() {
        this.player.reset();
        this.deliveryCurrentLevel = 1;
        this.setupDeliveryMission();
        this.setState(config.STATE_DELIVERY_PLAYING);
    },

    setupDeliveryMission() {
        this.deliveryStartRunway = new Runway(config, Math.random() * -1500 - 500, Math.random() * 2000 - 1000, false, true);
        this.deliveryDestinationRunway = new Runway(config, Math.random() * 1500 + 500, Math.random() * 2000 - 1000, true, false);

        this.deliveryCheckpoints = [];
        const numCheckpoints = Math.floor((this.deliveryCurrentLevel - 1) / config.DELIVERY_CHECKPOINTS_ADD_PER_N_LEVELS);
        let lastPoint = { x: this.deliveryStartRunway.worldX, y: this.deliveryStartRunway.worldY };
        for (let i = 0; i < numCheckpoints; i++) {
            const checkpoint = new DeliveryCheckpoint(
                config,
                lastPoint.x + (this.deliveryDestinationRunway.worldX - lastPoint.x) / (numCheckpoints - i + 1) + Math.random() * 600 - 300,
                lastPoint.y + (this.deliveryDestinationRunway.worldY - lastPoint.y) / (numCheckpoints - i + 1) + Math.random() * 600 - 300,
                i + 1
            );
            this.deliveryCheckpoints.push(checkpoint);
            lastPoint = { x: checkpoint.worldX, y: checkpoint.worldY };
        }

        if (this.deliveryCheckpoints.length > 0) {
            this.deliveryActiveTarget = this.deliveryCheckpoints[0];
        } else {
            this.deliveryActiveTarget = this.deliveryDestinationRunway;
        }
    }
};

regenerateRiverParameters();
