const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

canvas.width = config.SCREEN_WIDTH;
canvas.height = config.SCREEN_HEIGHT;

let scaleX = 1;
let scaleY = 1;

function resizeCanvas() {
    const rect = canvas.getBoundingClientRect();
    scaleX = canvas.width / rect.width;
    scaleY = canvas.height / rect.height;
}

window.addEventListener('resize', resizeCanvas);
// Call it initially to set the correct scale
window.addEventListener('load', resizeCanvas);


const keys = {
    ArrowUp: false,
    ArrowDown: false,
    ArrowLeft: false,
    ArrowRight: false,
    Enter: false,
    ' ': false
};

document.addEventListener('keydown', (e) => {
    if (e.key in keys) {
        keys[e.key] = true;
    }
});

document.addEventListener('keyup', (e) => {
    if (e.key in keys) {
        keys[e.key] = false;
    }
});

function handleTouch(event, isStart) {
    event.preventDefault();
    const touches = event.changedTouches;
    const rect = canvas.getBoundingClientRect();

    for (let i = 0; i < touches.length; i++) {
        const touch = touches[i];
        const x = (touch.clientX - rect.left) * scaleX;
        const y = (touch.clientY - rect.top) * scaleY;

        for (const key in config.TOUCH_CONTROLS) {
            const button = config.TOUCH_CONTROLS[key];
            if (x >= button.x && x <= button.x + button.width &&
                y >= button.y && y <= button.y + button.height) {
                keys[button.key] = isStart;
            }
        }
    }
}

canvas.addEventListener('touchstart', (e) => handleTouch(e, true), { passive: false });
canvas.addEventListener('touchend', (e) => handleTouch(e, false), { passive: false });
canvas.addEventListener('touchcancel', (e) => handleTouch(e, false), { passive: false });


function handleInput() {
    if (gameStateManager.gameState === config.STATE_START_SCREEN) {
        if (keys.Enter) {
            gameStateManager.setState(config.STATE_MODE_SELECT);
            keys.Enter = false; // Prevent immediate selection in the next screen
        }
    } else if (gameStateManager.gameState === config.STATE_MODE_SELECT) {
        if (keys.ArrowUp) {
            gameStateManager.selectedModeOption = (gameStateManager.selectedModeOption - 1 + 4) % 4;
            keys.ArrowUp = false;
        }
        if (keys.ArrowDown) {
            gameStateManager.selectedModeOption = (gameStateManager.selectedModeOption + 1) % 4;
            keys.ArrowDown = false;
        }
        if (keys.Enter) {
            if (gameStateManager.selectedModeOption === config.MODE_FREE_FLY) {
                gameStateManager.startNewLevel();
            } else if (gameStateManager.selectedModeOption === config.MODE_RACE) {
                gameStateManager.startRace();
            } else if (gameStateManager.selectedModeOption === config.MODE_DOGFIGHT) {
                gameStateManager.startDogfight();
            } else if (gameStateManager.selectedModeOption === config.MODE_DELIVERY) {
                gameStateManager.startDelivery();
            }
            keys.Enter = false;
        }
    }
}

function update() {
    handleInput();
    if (gameStateManager.gameState === config.STATE_PLAYING_FREE_FLY) {
        updateFreeFly();
    } else if (gameStateManager.gameState === config.STATE_RACE_PLAYING) {
        updateRace();
    } else if (gameStateManager.gameState === config.STATE_DOGFIGHT_PLAYING) {
        updateDogfight();
    } else if (gameStateManager.gameState === config.STATE_DELIVERY_PLAYING) {
        updateDelivery();
    }
}

function updateFreeFly() {
    gameStateManager.player.update(keys, {});
    // Update thermals
    gameStateManager.thermalSpawnTimer++;
    if (gameStateManager.thermalSpawnTimer >= gameStateManager.currentThermalSpawnRate) {
        gameStateManager.thermalSpawnTimer = 0;
        const camX = gameStateManager.player.worldX - canvas.width / 2;
        const camY = gameStateManager.player.worldY - canvas.height / 2;
        const spawnWorldX = camX + Math.random() * config.THERMAL_SPAWN_AREA_WIDTH - config.THERMAL_SPAWN_AREA_WIDTH / 2;
        const spawnWorldY = camY + Math.random() * config.THERMAL_SPAWN_AREA_HEIGHT - config.THERMAL_SPAWN_AREA_HEIGHT / 2;
        const landType = getLandTypeAtWorldPos(spawnWorldX, spawnWorldY, gameStateManager.currentMapOffsetX, gameStateManager.currentMapOffsetY, gameStateManager.tileTypeCache);
        if (Math.random() < config.LAND_TYPE_THERMAL_PROBABILITY[landType]) {
            gameStateManager.thermals.push(new Thermal(config, spawnWorldX, spawnWorldY));
        }
    }

    for (let i = gameStateManager.thermals.length - 1; i >= 0; i--) {
        const thermal = gameStateManager.thermals[i];
        thermal.update();
        if (thermal.lifespan <= 0) {
            gameStateManager.thermals.splice(i, 1);
        }
    }

    // Check for thermal interaction
    for (const thermal of gameStateManager.thermals) {
        const distance = Math.hypot(gameStateManager.player.worldX - thermal.worldX, gameStateManager.player.worldY - thermal.worldY);
        if (distance < thermal.radius) {
            gameStateManager.player.applyLiftFromThermal(thermal.liftPower);
        }
    }
}

function updateRace() {
    gameStateManager.player.update(keys, {});
    for (const ai of gameStateManager.aiGliders) {
        ai.update(gameStateManager.raceCourseMarkers);
    }
}

function updateDogfight() {
    gameStateManager.player.update(keys, {});
    if (keys[' ']) {
        gameStateManager.player.shoot(gameStateManager.bullets);
    }

    for (let i = gameStateManager.bullets.length - 1; i >= 0; i--) {
        const bullet = gameStateManager.bullets[i];
        bullet.update();
        if (bullet.rangeTraveled > bullet.config.BULLET_RANGE) {
            gameStateManager.bullets.splice(i, 1);
            continue;
        }

        if (bullet.owner === gameStateManager.player) {
            for (const ai of gameStateManager.aiGliders) {
                const distance = Math.hypot(bullet.worldX - ai.worldX, bullet.worldY - ai.worldY);
                if (distance < config.GLIDER_COLLISION_RADIUS) {
                    ai.takeDamage(config.BULLET_DAMAGE);
                    gameStateManager.bullets.splice(i, 1);
                    break;
                }
            }
        } else {
            const distance = Math.hypot(bullet.worldX - gameStateManager.player.worldX, bullet.worldY - gameStateManager.player.worldY);
            if (distance < config.GLIDER_COLLISION_RADIUS) {
                gameStateManager.player.takeDamage(config.BULLET_DAMAGE);
                gameStateManager.bullets.splice(i, 1);
            }
        }
    }

    for (const ai of gameStateManager.aiGliders) {
        ai.update(gameStateManager.player);
    }
}

function updateDelivery() {
    gameStateManager.player.update(keys, {});

    if (gameStateManager.deliveryActiveTarget) {
        const distanceToTarget = Math.hypot(gameStateManager.player.worldX - gameStateManager.deliveryActiveTarget.worldX, gameStateManager.player.worldY - gameStateManager.deliveryActiveTarget.worldY);
        if (distanceToTarget < config.DELIVERY_CHECKPOINT_INTERACTION_RADIUS) {
            if (gameStateManager.deliveryActiveTarget instanceof DeliveryCheckpoint) {
                gameStateManager.player.currentTargetMarkerIndex++;
                if (gameStateManager.player.currentTargetMarkerIndex < gameStateManager.deliveryCheckpoints.length) {
                    gameStateManager.deliveryActiveTarget = gameStateManager.deliveryCheckpoints[gameStateManager.player.currentTargetMarkerIndex];
                } else {
                    gameStateManager.deliveryActiveTarget = gameStateManager.deliveryDestinationRunway;
                }
            } else if (gameStateManager.deliveryActiveTarget instanceof Runway) {
                if (gameStateManager.player.speed <= config.DELIVERY_LANDING_MAX_SPEED && gameStateManager.player.height <= config.DELIVERY_LANDING_MAX_HEIGHT_ABOVE_GROUND) {
                    gameStateManager.deliveryCurrentLevel++;
                    gameStateManager.setupDeliveryMission();
                }
            }
        }
    }
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (gameStateManager.gameState === config.STATE_START_SCREEN) {
        drawMainMenu(ctx);
    } else if (gameStateManager.gameState === config.STATE_MODE_SELECT) {
        drawModeSelectScreen(ctx, gameStateManager.selectedModeOption);
    } else if (gameStateManager.gameState === config.STATE_PLAYING_FREE_FLY) {
        drawFreeFly();
    } else if (gameStateManager.gameState === config.STATE_RACE_PLAYING) {
        drawRace();
    } else if (gameStateManager.gameState === config.STATE_DOGFIGHT_PLAYING) {
        drawDogfight();
    } else if (gameStateManager.gameState === config.STATE_DELIVERY_PLAYING) {
        drawDelivery();
    }

    // Always draw touch controls on top if enabled
    drawTouchControls(ctx, keys);
}

function drawFreeFly() {
    const camX = gameStateManager.player.worldX - canvas.width / 2;
    const camY = gameStateManager.player.worldY - canvas.height / 2;

    drawEndlessMap(ctx, camX, camY, gameStateManager.currentMapOffsetX, gameStateManager.currentMapOffsetY, gameStateManager.tileTypeCache);

    for (const thermal of gameStateManager.thermals) {
        thermal.draw(ctx, camX, camY);
    }

    gameStateManager.player.draw(ctx);
    drawHud(ctx, gameStateManager.player, gameStateManager.gameState);
    gameStateManager.minimap.draw(ctx, gameStateManager.player, gameStateManager.aiGliders, gameStateManager.raceCourseMarkers);
}

function drawRace() {
    const camX = gameStateManager.player.worldX - canvas.width / 2;
    const camY = gameStateManager.player.worldY - canvas.height / 2;

    drawEndlessMap(ctx, camX, camY, gameStateManager.currentMapOffsetX, gameStateManager.currentMapOffsetY, gameStateManager.tileTypeCache);

    for (let i = 0; i < gameStateManager.raceCourseMarkers.length; i++) {
        const marker = gameStateManager.raceCourseMarkers[i];
        marker.draw(ctx, camX, camY, i === gameStateManager.player.currentTargetMarkerIndex);
    }

    for (const ai of gameStateManager.aiGliders) {
        ai.draw(ctx, camX, camY);
    }

    gameStateManager.player.draw(ctx);
    drawHud(ctx, gameStateManager.player, gameStateManager.gameState);
    gameStateManager.minimap.draw(ctx, gameStateManager.player, gameStateManager.aiGliders, gameStateManager.raceCourseMarkers);
}

function drawDogfight() {
    const camX = gameStateManager.player.worldX - canvas.width / 2;
    const camY = gameStateManager.player.worldY - canvas.height / 2;

    drawEndlessMap(ctx, camX, camY, gameStateManager.currentMapOffsetX, gameStateManager.currentMapOffsetY, gameStateManager.tileTypeCache);

    for (const bullet of gameStateManager.bullets) {
        bullet.draw(ctx, camX, camY);
    }

    for (const ai of gameStateManager.aiGliders) {
        ai.draw(ctx, camX, camY, true);
    }

    gameStateManager.player.draw(ctx, true);
    const dogfightData = {
        round: gameStateManager.dogfightCurrentRound,
        enemiesLeft: gameStateManager.aiGliders.length,
    };
    drawHud(ctx, gameStateManager.player, gameStateManager.gameState, {}, dogfightData);
}

function drawDelivery() {
    const camX = gameStateManager.player.worldX - canvas.width / 2;
    const camY = gameStateManager.player.worldY - canvas.height / 2;

    drawEndlessMap(ctx, camX, camY, gameStateManager.currentMapOffsetX, gameStateManager.currentMapOffsetY, gameStateManager.tileTypeCache);

    gameStateManager.deliveryStartRunway.draw(ctx, camX, camY);
    gameStateManager.deliveryDestinationRunway.draw(ctx, camX, camY);

    for (const checkpoint of gameStateManager.deliveryCheckpoints) {
        checkpoint.draw(ctx, camX, camY, checkpoint === gameStateManager.deliveryActiveTarget);
    }

    gameStateManager.player.draw(ctx);
    const deliveryData = {
        level: gameStateManager.deliveryCurrentLevel,
        target: gameStateManager.deliveryActiveTarget,
    };
    drawHud(ctx, gameStateManager.player, gameStateManager.gameState, deliveryData);
    gameStateManager.minimap.draw(ctx, gameStateManager.player, [], [], {
        startRunway: gameStateManager.deliveryStartRunway,
        destinationRunway: gameStateManager.deliveryDestinationRunway,
        checkpoints: gameStateManager.deliveryCheckpoints,
    });
}

function gameLoop() {
    update();
    draw();
    requestAnimationFrame(gameLoop);
}

gameLoop();
