// ui.js

function drawText(ctx, text, size, x, y, color = config.PASTEL_WHITE, fontName = config.HUD_FONT_NAME, center = false, shadow = false, shadowColor = config.PASTEL_DARK_GRAY, shadowOffset = { x: 1, y: 1 }) {
    ctx.font = `${size}px ${fontName}`;
    ctx.fillStyle = color;
    if (center) {
        ctx.textAlign = 'center';
    } else {
        ctx.textAlign = 'left';
    }
    if (shadow) {
        ctx.fillStyle = shadowColor;
        ctx.fillText(text, x + shadowOffset.x, y + shadowOffset.y);
        ctx.fillStyle = color;
    }
    ctx.fillText(text, x, y);
}

function drawHud(ctx, player, gameState, deliveryData = {}, dogfightData = {}) {
    // Draw HUD background
    ctx.fillStyle = config.PASTEL_HUD_PANEL;
    ctx.fillRect(0, 0, config.SCREEN_WIDTH, config.HUD_HEIGHT);

    // Draw HUD text
    const hm = 10;
    const ls = 28;
    let cyh = 8;

    if (gameState === config.STATE_DOGFIGHT_PLAYING) {
        drawText(ctx, `Round: ${dogfightData.round}`, config.HUD_FONT_SIZE_NORMAL, hm, cyh, config.PASTEL_TEXT_COLOR_HUD, config.HUD_FONT_NAME);
        drawText(ctx, `Enemies: ${dogfightData.enemiesLeft}`, config.HUD_FONT_SIZE_NORMAL, hm + 150, cyh, config.PASTEL_TEXT_COLOR_HUD, config.HUD_FONT_NAME);
        drawText(ctx, `Health: ${player.health}`, config.HUD_FONT_SIZE_NORMAL, hm + 320, cyh, config.PASTEL_TEXT_COLOR_HUD, config.HUD_FONT_NAME);
    } else if (gameState === config.STATE_DELIVERY_PLAYING) {
        let distStr = "N/A";
        if (deliveryData.target) {
            const dist = Math.hypot(player.worldX - deliveryData.target.worldX, player.worldY - deliveryData.target.worldY);
            distStr = `${Math.round(dist / 10)}u`;
        }
        drawText(ctx, `Delivery: ${deliveryData.level}`, config.HUD_FONT_SIZE_NORMAL, hm, cyh, config.PASTEL_TEXT_COLOR_HUD, config.HUD_FONT_NAME);
        drawText(ctx, `Target: ${distStr}`, config.HUD_FONT_SIZE_NORMAL, hm + 150, cyh, config.PASTEL_TEXT_COLOR_HUD, config.HUD_FONT_NAME);
    } else {
        drawText(ctx, `Height: ${Math.round(player.height)}m`, config.HUD_FONT_SIZE_NORMAL, hm, cyh + ls * 2, config.PASTEL_TEXT_COLOR_HUD, config.HUD_FONT_NAME);
        drawText(ctx, `Speed: ${player.speed.toFixed(1)}`, config.HUD_FONT_SIZE_NORMAL, hm + 150, cyh + ls * 2, config.PASTEL_TEXT_COLOR_HUD, config.HUD_FONT_NAME);
    }

    if (player.speed < config.STALL_SPEED) {
        drawText(ctx, "STALL!", config.HUD_FONT_SIZE_LARGE, config.SCREEN_WIDTH / 2, hm + ls / 2 + 5, config.PASTEL_RED, config.HUD_FONT_NAME, true, true, config.PASTEL_BLACK);
    }

    drawHeightIndicator(ctx, player.height, player.verticalSpeed);
}

function drawHeightIndicator(ctx, currentHeight, verticalSpeed) {
    const indicatorBarHeight = config.SCREEN_HEIGHT - config.HUD_HEIGHT - (2 * config.INDICATOR_Y_MARGIN_FROM_HUD);
    const indicatorXPos = config.SCREEN_WIDTH - config.INDICATOR_WIDTH - config.INDICATOR_X_MARGIN;
    const indicatorYPos = config.HUD_HEIGHT + config.INDICATOR_Y_MARGIN_FROM_HUD;

    // Draw indicator bar
    ctx.fillStyle = config.PASTEL_INDICATOR_COLOR;
    ctx.fillRect(indicatorXPos, indicatorYPos, config.INDICATOR_WIDTH, indicatorBarHeight);

    const maxIndicatorHeight = currentHeight + 500;
    const groundLineY = indicatorYPos + indicatorBarHeight;

    // Draw ground line
    ctx.strokeStyle = config.PASTEL_INDICATOR_GROUND;
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(indicatorXPos - 5, groundLineY);
    ctx.lineTo(indicatorXPos + config.INDICATOR_WIDTH + 5, groundLineY);
    ctx.stroke();
    drawText(ctx, "0m", 14, indicatorXPos + config.INDICATOR_WIDTH + 8, groundLineY - 7, config.PASTEL_TEXT_COLOR_HUD, config.HUD_FONT_NAME);

    // Draw player marker
    const playerMarkerYOnBar = groundLineY - (currentHeight / maxIndicatorHeight) * indicatorBarHeight;
    ctx.strokeStyle = config.PASTEL_GOLD;
    ctx.lineWidth = 5;
    ctx.beginPath();
    ctx.moveTo(indicatorXPos, playerMarkerYOnBar);
    ctx.lineTo(indicatorXPos + config.INDICATOR_WIDTH, playerMarkerYOnBar);
    ctx.stroke();

    // Draw VSI
    const vsiMps = verticalSpeed * 60; // Approximate m/s
    const vsiColor = vsiMps > 0.5 ? config.PASTEL_VSI_CLIMB : (vsiMps < -0.5 ? config.PASTEL_VSI_SINK : config.PASTEL_TEXT_COLOR_HUD);
    drawText(ctx, `${vsiMps.toFixed(1)}m/s`, 14, indicatorXPos - 70, playerMarkerYOnBar - 7, vsiColor, config.HUD_FONT_NAME);

    // Draw VSI arrow
    if (Math.abs(vsiMps) > 0.5) {
        const vsiArrowXCenter = indicatorXPos - 10;
        ctx.fillStyle = vsiColor;
        ctx.beginPath();
        if (vsiMps > 0) {
            ctx.moveTo(vsiArrowXCenter, playerMarkerYOnBar - config.VSI_ARROW_SIZE);
            ctx.lineTo(vsiArrowXCenter - config.VSI_ARROW_SIZE / 2, playerMarkerYOnBar);
            ctx.lineTo(vsiArrowXCenter + config.VSI_ARROW_SIZE / 2, playerMarkerYOnBar);
        } else {
            ctx.moveTo(vsiArrowXCenter, playerMarkerYOnBar + config.VSI_ARROW_SIZE);
            ctx.lineTo(vsiArrowXCenter - config.VSI_ARROW_SIZE / 2, playerMarkerYOnBar);
            ctx.lineTo(vsiArrowXCenter + config.VSI_ARROW_SIZE / 2, playerMarkerYOnBar);
        }
        ctx.closePath();
        ctx.fill();
    }
}

function drawMainMenu(ctx) {
    ctx.fillStyle = config.PASTEL_DARK_GRAY;
    ctx.fillRect(0, 0, config.SCREEN_WIDTH, config.SCREEN_HEIGHT);
    const titleY = config.SCREEN_HEIGHT / 4 - 50;
    drawText(ctx, "Pastel Glider", 72, config.SCREEN_WIDTH / 2, titleY, config.PASTEL_PLAINS, config.HUD_FONT_NAME, true, true, config.PASTEL_BLACK);
    const infoY = titleY + 80;
    const lineSpacing = 28;
    const infoFontSize = 22;
    drawText(ctx, "Welcome, pilot! Soar through endless skies.", infoFontSize, config.SCREEN_WIDTH / 2, infoY, config.PASTEL_LIGHT_GRAY, config.HUD_FONT_NAME, true);
    drawText(ctx, "Use thermals to gain altitude and explore.", infoFontSize, config.SCREEN_WIDTH / 2, infoY + lineSpacing, config.PASTEL_LIGHT_GRAY, config.HUD_FONT_NAME, true);
    drawText(ctx, "Press ENTER to Begin Your Flight", 30, config.SCREEN_WIDTH / 2, infoY + lineSpacing * 4, config.PASTEL_GOLD, config.HUD_FONT_NAME, true, true, config.PASTEL_BLACK);
}

function drawModeSelectScreen(ctx, selectedOption) {
    ctx.fillStyle = config.PASTEL_DARK_GRAY;
    ctx.fillRect(0, 0, config.SCREEN_WIDTH, config.SCREEN_HEIGHT);
    drawText(ctx, "Select Mode", 56, config.SCREEN_WIDTH / 2, config.SCREEN_HEIGHT / 4 - 40, config.PASTEL_GOLD, config.HUD_FONT_NAME, true, true, config.PASTEL_BLACK);

    const modes = [
        { name: "Free Fly", desc: "(Explore & Reach Altitude Goals)", mode: config.MODE_FREE_FLY },
        { name: "Race", desc: "(Fly Through Markers Against AI)", mode: config.MODE_RACE },
        { name: "Dogfight", desc: "(Survive Enemy Waves!)", mode: config.MODE_DOGFIGHT },
        { name: "Delivery", desc: "(Transport Goods Between Runways)", mode: config.MODE_DELIVERY },
    ];

    const optionBaseY = config.SCREEN_HEIGHT / 2 - (modes.length / 2 * 70);
    for (let i = 0; i < modes.length; i++) {
        const mode = modes[i];
        const color = selectedOption === mode.mode ? config.PASTEL_WHITE : config.PASTEL_GRAY;
        const yPos = optionBaseY + i * 70;
        drawText(ctx, mode.name, 44, config.SCREEN_WIDTH / 2, yPos, color, config.HUD_FONT_NAME, true, true, config.PASTEL_BLACK);
        drawText(ctx, mode.desc, 20, config.SCREEN_WIDTH / 2, yPos + 30, color, config.HUD_FONT_NAME, true);
    }

    drawText(ctx, "Use UP/DOWN keys, ENTER to confirm", 22, config.SCREEN_WIDTH / 2, config.SCREEN_HEIGHT * 3 / 4 + 80, config.PASTEL_LIGHT_GRAY, config.HUD_FONT_NAME, true);
}

class Minimap {
    constructor(config) {
        this.config = config;
        this.width = this.config.MINIMAP_WIDTH;
        this.height = this.config.MINIMAP_HEIGHT;
        this.margin = this.config.MINIMAP_MARGIN;
        this.x = this.config.SCREEN_WIDTH - this.width - this.margin;
        this.y = this.margin + this.config.HUD_HEIGHT;
        this.worldBoundsViewRadius = 3000;
    }

    worldToMinimap(worldX, worldY, playerWorldX, playerWorldY) {
        const scale = this.width / (2 * this.worldBoundsViewRadius);
        const relX = worldX - playerWorldX;
        const relY = worldY - playerWorldY;
        const miniX = this.width / 2 + relX * scale;
        const miniY = this.height / 2 + relY * scale;
        return { x: miniX, y: miniY };
    }

    draw(ctx, player, aiGliders, raceMarkers, deliveryData = {}) {
        ctx.save();
        ctx.translate(this.x, this.y);

        ctx.fillStyle = this.config.PASTEL_MINIMAP_BACKGROUND;
        ctx.fillRect(0, 0, this.width, this.height);

        // Draw player
        ctx.fillStyle = this.config.PASTEL_GOLD;
        ctx.beginPath();
        ctx.arc(this.width / 2, this.height / 2, 5, 0, 2 * Math.PI);
        ctx.fill();

        // Draw AI
        for (const ai of aiGliders) {
            const pos = this.worldToMinimap(ai.worldX, ai.worldY, player.worldX, player.worldY);
            if (pos.x >= 0 && pos.x <= this.width && pos.y >= 0 && pos.y <= this.height) {
                ctx.fillStyle = ai.bodyColor;
                ctx.beginPath();
                ctx.arc(pos.x, pos.y, 4, 0, 2 * Math.PI);
                ctx.fill();
            }
        }

        // Draw race markers
        for (const marker of raceMarkers) {
            const pos = this.worldToMinimap(marker.worldX, marker.worldY, player.worldX, player.worldY);
            if (pos.x >= 0 && pos.x <= this.width && pos.y >= 0 && pos.y <= this.height) {
                ctx.fillStyle = marker.number - 1 === player.currentTargetMarkerIndex ? this.config.PASTEL_ACTIVE_MARKER_COLOR : this.config.PASTEL_MARKER_COLOR;
                ctx.beginPath();
                ctx.arc(pos.x, pos.y, this.config.RACE_MARKER_VISUAL_RADIUS_MAP, 0, 2 * Math.PI);
                ctx.fill();
            }
        }

        // Draw delivery items
        if (deliveryData.startRunway) {
            const pos = this.worldToMinimap(deliveryData.startRunway.worldX, deliveryData.startRunway.worldY, player.worldX, player.worldY);
            if (pos.x >= 0 && pos.x <= this.width && pos.y >= 0 && pos.y <= this.height) {
                ctx.fillStyle = this.config.PASTEL_RUNWAY_START_COLOR;
                ctx.beginPath();
                ctx.arc(pos.x, pos.y, 4, 0, 2 * Math.PI);
                ctx.fill();
            }
        }
        if (deliveryData.destinationRunway) {
            const pos = this.worldToMinimap(deliveryData.destinationRunway.worldX, deliveryData.destinationRunway.worldY, player.worldX, player.worldY);
            if (pos.x >= 0 && pos.x <= this.width && pos.y >= 0 && pos.y <= this.height) {
                ctx.fillStyle = this.config.PASTEL_RUNWAY_DESTINATION_COLOR;
                ctx.beginPath();
                ctx.arc(pos.x, pos.y, 4, 0, 2 * Math.PI);
                ctx.fill();
            }
        }
        for (const checkpoint of deliveryData.checkpoints || []) {
            const pos = this.worldToMinimap(checkpoint.worldX, checkpoint.worldY, player.worldX, player.worldY);
            if (pos.x >= 0 && pos.x <= this.width && pos.y >= 0 && pos.y <= this.height) {
                ctx.fillStyle = this.config.DELIVERY_CHECKPOINT_COLOR_ACTIVE;
                ctx.beginPath();
                ctx.rect(pos.x - 3, pos.y - 3, 6, 6);
                ctx.fill();
            }
        }

        ctx.strokeStyle = this.config.PASTEL_MINIMAP_BORDER;
        ctx.lineWidth = 2;
        ctx.strokeRect(0, 0, this.width, this.height);

        ctx.restore();
    }
}
