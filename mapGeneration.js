// mapGeneration.js

class SeededRandom {
    constructor(seed) {
        this.seed = seed;
    }

    random() {
        const x = Math.sin(this.seed++) * 10000;
        return x - Math.floor(x);
    }
}

let mapTileRandomGenerator = new SeededRandom(0);
let riverParamRandom = new SeededRandom(0);
let MAJOR_RIVERS_PARAMS = [];

function regenerateRiverParameters(seedValue = null) {
    if (seedValue !== null) {
        riverParamRandom = new SeededRandom(seedValue);
    }

    MAJOR_RIVERS_PARAMS = [];
    for (let i = 0; i < config.NUM_MAJOR_RIVERS; i++) {
        const startTileX = riverParamRandom.random() * (config.RACE_COURSE_AREA_HALFWIDTH / config.TILE_SIZE / 1.5) - (config.RACE_COURSE_AREA_HALFWIDTH / config.TILE_SIZE / 3);
        const startTileY = riverParamRandom.random() * (config.RACE_COURSE_AREA_HALFWIDTH / config.TILE_SIZE / 1.5) - (config.RACE_COURSE_AREA_HALFWIDTH / config.TILE_SIZE / 3);
        MAJOR_RIVERS_PARAMS.push({
            amplitude: riverParamRandom.random() * 20 + 10,
            wavelength: riverParamRandom.random() * 250 + 200,
            phase_offset: riverParamRandom.random() * 2 * Math.PI,
            base_x_offset: startTileX,
            base_y_offset: startTileY,
            orientation: riverParamRandom.random() < 0.5 ? 'horizontal' : 'vertical',
            width: Math.floor(riverParamRandom.random() * 2) + 1,
        });
    }
}

function getSeededRandomValueDirect(uniqueTileX, uniqueTileY, scale, pPair) {
    const scaledX = Math.floor(uniqueTileX / scale);
    const scaledY = Math.floor(uniqueTileY / scale);
    mapTileRandomGenerator = new SeededRandom((scaledX * pPair[0]) ^ (scaledY * pPair[1]));
    return mapTileRandomGenerator.random();
}

function getLandTypeAtWorldPos(worldX, worldY, currentMapOffsetX, currentMapOffsetY, tileTypeCache) {
    const uniqueTileX = Math.floor((worldX + currentMapOffsetX) / config.TILE_SIZE);
    const uniqueTileY = Math.floor((worldY + currentMapOffsetY) / config.TILE_SIZE);
    const cacheKey = `${uniqueTileX},${uniqueTileY}`;
    if (tileTypeCache.has(cacheKey)) {
        return tileTypeCache.get(cacheKey);
    }

    const eContinent = getSeededRandomValueDirect(uniqueTileX, uniqueTileY, config.ELEVATION_CONTINENT_SCALE, config.P_CONT);
    const eMountain = getSeededRandomValueDirect(uniqueTileX, uniqueTileY, config.ELEVATION_MOUNTAIN_SCALE, config.P_MNT);
    const eHill = getSeededRandomValueDirect(uniqueTileX, uniqueTileY, config.ELEVATION_HILL_SCALE, config.P_HILL);
    let elevation = Math.pow(0.50 * eContinent + 0.35 * eMountain + 0.15 * eHill, 1.8);
    elevation = Math.min(Math.max(elevation, 0.0), 1.0);

    const mPrimary = getSeededRandomValueDirect(uniqueTileX, uniqueTileY, config.MOISTURE_PRIMARY_SCALE, config.P_MOIST_P);
    const mSecondary = getSeededRandomValueDirect(uniqueTileX, uniqueTileY, config.MOISTURE_SECONDARY_SCALE, config.P_MOIST_S);
    let moisture = Math.pow(0.7 * mPrimary + 0.3 * mSecondary, 1.2);
    moisture = Math.min(Math.max(moisture, 0.0), 1.0);

    let finalType = config.LAND_TYPE_PLAINS;

    if (elevation < config.DEEP_WATER_THRESH) finalType = config.LAND_TYPE_WATER_DEEP;
    else if (elevation < config.SHALLOW_WATER_THRESH) finalType = config.LAND_TYPE_WATER_SHALLOW;
    else if (elevation < config.BEACH_THRESH) finalType = moisture < config.DESERT_THRESH * 1.2 ? config.LAND_TYPE_SAND_DESERT : config.LAND_TYPE_SAND_BEACH;
    else if (elevation > config.MOUNTAIN_PEAK_THRESH) finalType = config.LAND_TYPE_MOUNTAIN_PEAK;
    else if (elevation > config.MOUNTAIN_BASE_THRESH) finalType = config.LAND_TYPE_MOUNTAIN_BASE;
    else {
        if (moisture < config.DESERT_THRESH) finalType = config.LAND_TYPE_SAND_DESERT;
        else if (moisture < config.GRASSLAND_THRESH) finalType = config.LAND_TYPE_GRASSLAND;
        else if (moisture < config.TEMPERATE_FOREST_THRESH) finalType = config.LAND_TYPE_PLAINS;
        else finalType = moisture > 0.8 && elevation < config.MOUNTAIN_BASE_THRESH * 0.9 ? config.LAND_TYPE_FOREST_DENSE : config.LAND_TYPE_FOREST_TEMPERATE;
    }

    const canHaveRiver = finalType !== config.LAND_TYPE_MOUNTAIN_PEAK && finalType !== config.LAND_TYPE_WATER_DEEP && !(finalType === config.LAND_TYPE_SAND_DESERT && moisture < config.DESERT_THRESH * 0.75);
    if (canHaveRiver) {
        for (const params of MAJOR_RIVERS_PARAMS) {
            if (params.orientation === 'horizontal') {
                const riverCenterYTile = params.amplitude * Math.sin((uniqueTileX / params.wavelength) * 2 * Math.PI + params.phase_offset) + params.base_y_offset;
                if (Math.abs(uniqueTileY - riverCenterYTile) < params.width) {
                    finalType = config.LAND_TYPE_RIVER;
                    break;
                }
            } else {
                const riverCenterXTile = params.amplitude * Math.sin((uniqueTileY / params.wavelength) * 2 * Math.PI + params.phase_offset) + params.base_x_offset;
                if (Math.abs(uniqueTileX - riverCenterXTile) < params.width) {
                    finalType = config.LAND_TYPE_RIVER;
                    break;
                }
            }
        }
    }

    tileTypeCache.set(cacheKey, finalType);
    return finalType;
}

function drawEndlessMap(ctx, camX, camY, currentMapOffsetX, currentMapOffsetY, tileTypeCache) {
    const startWorldTileXCoord = Math.floor(camX / config.TILE_SIZE) * config.TILE_SIZE;
    const startWorldTileYCoord = Math.floor(camY / config.TILE_SIZE) * config.TILE_SIZE;
    const numTilesX = Math.ceil(config.SCREEN_WIDTH / config.TILE_SIZE) + 2;
    const numTilesY = Math.ceil(config.SCREEN_HEIGHT / config.TILE_SIZE) + 2;

    for (let i = 0; i < numTilesY; i++) {
        for (let j = 0; j < numTilesX; j++) {
            const currentTileWorldX = startWorldTileXCoord + j * config.TILE_SIZE;
            const currentTileWorldY = startWorldTileYCoord + i * config.TILE_SIZE;
            const tileScreenX = currentTileWorldX - camX;
            const tileScreenY = currentTileWorldY - camY;
            const tileType = getLandTypeAtWorldPos(currentTileWorldX, currentTileWorldY, currentMapOffsetX, currentMapOffsetY, tileTypeCache);
            const color = config.LAND_TYPE_COLORS[tileType] || config.PASTEL_BLACK;
            ctx.fillStyle = color;
            ctx.fillRect(tileScreenX, tileScreenY, config.TILE_SIZE, config.TILE_SIZE);
            if (config.MAP_TILE_OUTLINE_WIDTH > 0) {
                ctx.strokeStyle = config.MAP_TILE_OUTLINE_COLOR;
                ctx.lineWidth = config.MAP_TILE_OUTLINE_WIDTH;
                ctx.strokeRect(tileScreenX, tileScreenY, config.TILE_SIZE, config.TILE_SIZE);
            }
        }
    }
}
