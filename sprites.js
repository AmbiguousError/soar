// sprites.js

class Player {
    constructor(config) {
        this.config = config;
        this.x = this.config.SCREEN_WIDTH / 2;
        this.y = this.config.SCREEN_HEIGHT / 2;
        this.worldX = 0;
        this.worldY = 0;
        this.speed = this.config.INITIAL_SPEED;
        this.heading = 0; // degrees
        this.bankAngle = 0;
        this.height = this.config.INITIAL_HEIGHT;
        this.verticalSpeed = 0;
        this.previousHeight = this.config.INITIAL_HEIGHT;
        this.health = this.config.PLAYER_MAX_HEALTH;
        this.maxHealth = this.config.PLAYER_MAX_HEALTH;
        this.shootCooldownTimer = 0;
        this.currentTargetMarkerIndex = 0;
    }

    update(keys, gameData) {
        this.previousHeight = this.height;

        // Update speed
        if (keys.ArrowUp) {
            this.speed += this.config.ACCELERATION;
        } else if (keys.ArrowDown) {
            const potentialNewSpeed = this.speed - this.config.ACCELERATION;
            if (potentialNewSpeed >= this.config.MIN_SPEED) {
                this.speed = potentialNewSpeed;
                this.height += this.config.ACCELERATION * this.config.ZOOM_CLIMB_FACTOR;
            } else {
                this.speed = this.config.MIN_SPEED;
            }
        }
        this.speed = Math.max(this.config.MIN_SPEED, Math.min(this.speed, this.config.MAX_SPEED));

        // Update bank angle and heading
        if (keys.ArrowLeft) {
            this.bankAngle -= this.config.BANK_RATE;
        } else if (keys.ArrowRight) {
            this.bankAngle += this.config.BANK_RATE;
        } else {
            this.bankAngle *= 0.95;
        }
        if (Math.abs(this.bankAngle) < 0.1) {
            this.bankAngle = 0;
        }
        this.bankAngle = Math.max(-this.config.MAX_BANK_ANGLE, Math.min(this.bankAngle, this.config.MAX_BANK_ANGLE));

        const turnRateDegrees = this.bankAngle * this.config.BASE_PLAYER_BANK_TO_DEGREES_PER_FRAME;
        this.heading = (this.heading + turnRateDegrees) % 360;

        // Update world position
        const headingRad = this.heading * Math.PI / 180;
        this.worldX += this.speed * Math.cos(headingRad);
        this.worldY += this.speed * Math.sin(headingRad);

        // Update height
        let heightChangeDueToPhysics;
        if (this.speed < this.config.STALL_SPEED) {
            heightChangeDueToPhysics = -this.config.GRAVITY_BASE_PULL - this.config.STALL_SINK_PENALTY;
        } else {
            const liftFromAirspeed = this.speed * this.config.LIFT_PER_SPEED_UNIT;
            const netVerticalForce = liftFromAirspeed - this.config.GRAVITY_BASE_PULL;
            if (netVerticalForce < 0) {
                heightChangeDueToPhysics = Math.max(netVerticalForce, -this.config.MINIMUM_SINK_RATE);
            } else {
                heightChangeDueToPhysics = netVerticalForce;
            }
        }
        this.height += heightChangeDueToPhysics;

        if (heightChangeDueToPhysics < 0) {
            this.speed = Math.min(this.speed + Math.abs(heightChangeDueToPhysics) * this.config.DIVE_TO_SPEED_FACTOR, this.config.MAX_SPEED);
        }

        this.verticalSpeed = this.height - this.previousHeight;
    }

    draw(ctx, isDogfightMode = false) {
        ctx.save();
        ctx.translate(this.x, this.y);
        ctx.rotate(this.heading * Math.PI / 180);
        ctx.fillStyle = this.config.PASTEL_GLIDER_BODY;
        ctx.fillRect(-15, -5, 30, 10); // Fuselage
        ctx.fillStyle = this.config.PASTEL_GLIDER_WING;
        ctx.fillRect(-10, -2, 20, 4); // Wings
        ctx.restore();

        if (isDogfightMode) {
            this.drawHealthBar(ctx, this.x, this.y - 30);
        }
    }

    applyLiftFromThermal(thermalLiftPower) {
        if (this.speed < this.config.STALL_SPEED) return;
        let actualLiftPower = thermalLiftPower;
        // In the future, we can add difficulty modifiers here
        this.height += Math.max(actualLiftPower * (this.config.INITIAL_SPEED / Math.max(this.speed, this.config.MIN_SPEED * 0.5)), actualLiftPower * 0.2);
    }

    takeDamage(amount) {
        this.health -= amount;
        if (this.health < 0) this.health = 0;
    }

    shoot(bullets) {
        if (this.shootCooldownTimer <= 0) {
            const headingRad = this.heading * Math.PI / 180;
            const bulletStartX = this.worldX + 20 * Math.cos(headingRad);
            const bulletStartY = this.worldY + 20 * Math.sin(headingRad);
            bullets.push(new Bullet(this.config, bulletStartX, bulletStartY, this.heading, this));
            this.shootCooldownTimer = this.config.PLAYER_SHOOT_COOLDOWN;
        }
    }

    drawHealthBar(ctx, screenX, screenY) {
        const barWidth = this.config.HEALTH_BAR_WIDTH;
        const barHeight = this.config.HEALTH_BAR_HEIGHT;
        const healthRatio = this.health / this.maxHealth;

        ctx.fillStyle = this.config.HEALTH_BAR_BACKGROUND_COLOR;
        ctx.fillRect(screenX - barWidth / 2, screenY, barWidth, barHeight);

        let barColor = this.config.HEALTH_BAR_COLOR_BAD;
        if (healthRatio > 0.66) {
            barColor = this.config.HEALTH_BAR_COLOR_GOOD;
        } else if (healthRatio > 0.33) {
            barColor = this.config.HEALTH_BAR_COLOR_MEDIUM;
        }
        ctx.fillStyle = barColor;
        ctx.fillRect(screenX - barWidth / 2, screenY, barWidth * healthRatio, barHeight);
    }

    reset() {
        this.worldX = 0;
        this.worldY = 0;
        this.speed = this.config.INITIAL_SPEED;
        this.heading = 0;
        this.bankAngle = 0;
        this.height = this.config.INITIAL_HEIGHT;
        this.health = this.maxHealth;
    }
}

class Thermal {
    constructor(config, worldX, worldY) {
        this.config = config;
        this.worldX = worldX;
        this.worldY = worldY;
        this.radius = Math.random() * (this.config.NORMAL_MAX_THERMAL_RADIUS - this.config.NORMAL_MIN_THERMAL_RADIUS) + this.config.NORMAL_MIN_THERMAL_RADIUS;
        this.lifespan = Math.random() * (this.config.NORMAL_MAX_THERMAL_LIFESPAN - this.config.NORMAL_MIN_THERMAL_LIFESPAN) + this.config.NORMAL_MIN_THERMAL_LIFESPAN;
        this.initialLifespan = this.lifespan;
        const normalizedRadius = (this.radius - this.config.NORMAL_MIN_THERMAL_RADIUS) / (this.config.NORMAL_MAX_THERMAL_RADIUS - this.config.NORMAL_MIN_THERMAL_RADIUS);
        this.liftPower = this.config.MIN_THERMAL_LIFT_POWER + (this.config.MAX_THERMAL_LIFT_POWER - this.config.MIN_THERMAL_LIFT_POWER) * normalizedRadius;
        this.creationTime = Date.now();
    }

    update() {
        this.lifespan--;
    }

    draw(ctx, camX, camY) {
        const screenX = this.worldX - camX;
        const screenY = this.worldY - camY;

        const pulseAlphaFactor = (Math.sin(Date.now() * 0.005 + this.creationTime * 0.01) * 0.3 + 0.7);
        const ageFactor = Math.max(0, this.lifespan / this.initialLifespan);
        const alpha = this.config.THERMAL_BASE_ALPHA * pulseAlphaFactor * ageFactor;
        const accentAlpha = this.config.THERMAL_ACCENT_ALPHA * pulseAlphaFactor * ageFactor;
        const visualRadiusFactor = Math.sin(Date.now() * 0.002 + this.creationTime * 0.005) * 0.1 + 0.95;
        const currentVisualRadius = this.radius * visualRadiusFactor;

        ctx.beginPath();
        ctx.arc(screenX, screenY, currentVisualRadius, 0, 2 * Math.PI, false);
        ctx.fillStyle = `rgba(255, 200, 200, ${alpha / 255})`;
        ctx.fill();

        ctx.beginPath();
        ctx.arc(screenX, screenY, currentVisualRadius * 0.7, 0, 2 * Math.PI, false);
        ctx.strokeStyle = `rgba(245, 245, 250, ${accentAlpha / 255})`;
        ctx.lineWidth = 2;
        ctx.stroke();
    }
}

class AIGlider {
    constructor(config, worldX, worldY, bodyColor, wingColor, personalityProfile = {}, aiMode = "race") {
        this.config = config;
        this.worldX = worldX;
        this.worldY = worldY;
        this.bodyColor = bodyColor;
        this.wingColor = wingColor;
        this.aiMode = aiMode;

        this.speedFactor = personalityProfile.speedFactor || 1.0;
        this.turnFactor = personalityProfile.turnFactor || 1.0;

        this.baseMinSpeed = this.config.AI_BASE_SPEED_MIN * this.speedFactor;
        this.baseMaxSpeed = this.config.AI_BASE_SPEED_MAX * this.speedFactor;
        this.baseTurnRateScalar = this.config.AI_BASE_TURN_RATE_SCALAR * this.turnFactor;

        this.targetAltitude = this.config.AI_TARGET_RACE_ALTITUDE;
        this.speed = Math.random() * (this.baseMaxSpeed - this.baseMinSpeed) + this.baseMinSpeed;
        this.height = this.targetAltitude + Math.random() * 100 - 50;
        this.heading = 0;

        this.currentTargetMarkerIndex = 0;
        this.lapsCompleted = 0;

        this.health = this.config.AI_MAX_HEALTH;
        this.maxHealth = this.config.AI_MAX_HEALTH;
        this.shootCooldownTimer = 0;
    }

    update(player, raceMarkers) {
        if (this.aiMode === 'race') {
            if (!raceMarkers || raceMarkers.length === 0) return;
            const targetMarker = raceMarkers[this.currentTargetMarkerIndex];
            const dx = targetMarker.worldX - this.worldX;
            const dy = targetMarker.worldY - this.worldY;
            const distanceToMarker = Math.hypot(dx, dy);
            const targetAngleRad = Math.atan2(dy, dx);
            const targetAngleDeg = targetAngleRad * 180 / Math.PI;
            let angleDiff = (targetAngleDeg - this.heading + 540) % 360 - 180;

            const turnThisFrame = angleDiff * this.baseTurnRateScalar;
            this.heading = (this.heading + turnThisFrame) % 360;

            let targetSpeed = this.baseMinSpeed + (this.baseMaxSpeed - this.baseMinSpeed) * 0.5;
            if (distanceToMarker < this.config.AI_MARKER_APPROACH_SLOWDOWN_DISTANCE) {
                targetSpeed = this.baseMinSpeed + (this.baseMaxSpeed - this.baseMinSpeed) * (distanceToMarker / this.config.AI_MARKER_APPROACH_SLOWDOWN_DISTANCE) * this.config.AI_MARKER_APPROACH_MIN_SPEED_FACTOR;
            }

            if (this.speed < targetSpeed) {
                this.speed += this.config.ACCELERATION * 0.5;
            } else {
                this.speed -= this.config.ACCELERATION * 0.5;
            }
            this.speed = Math.max(this.baseMinSpeed * 0.7, Math.min(this.speed, this.baseMaxSpeed * 1.1));

            if (distanceToMarker < this.config.RACE_MARKER_RADIUS_WORLD) {
                this.currentTargetMarkerIndex++;
                if (this.currentTargetMarkerIndex >= raceMarkers.length) {
                    this.lapsCompleted++;
                    this.currentTargetMarkerIndex = 0;
                }
            }
        } else if (this.aiMode === 'dogfight') {
            const dx = player.worldX - this.worldX;
            const dy = player.worldY - this.worldY;
            const distanceToPlayer = Math.hypot(dx, dy);
            const targetAngleRad = Math.atan2(dy, dx);
            const targetAngleDeg = targetAngleRad * 180 / Math.PI;
            let angleDiff = (targetAngleDeg - this.heading + 540) % 360 - 180;

            const turnThisFrame = angleDiff * this.baseTurnRateScalar * 2; // More aggressive turning
            this.heading = (this.heading + turnThisFrame) % 360;

            this.speed = this.baseMaxSpeed;
        }

        const headingRad = this.heading * Math.PI / 180;
        this.worldX += this.speed * Math.cos(headingRad);
        this.worldY += this.speed * Math.sin(headingRad);
    }

    draw(ctx, camX, camY) {
        const screenX = this.worldX - camX;
        const screenY = this.worldY - camY;

        ctx.save();
        ctx.translate(screenX, screenY);
        ctx.rotate(this.heading * Math.PI / 180);
        ctx.fillStyle = this.bodyColor;
        ctx.fillRect(-15, -5, 30, 10);
        ctx.fillStyle = this.wingColor;
        ctx.fillRect(-10, -2, 20, 4);
        ctx.restore();

        if (this.aiMode === 'dogfight') {
            this.drawHealthBar(ctx, screenX, screenY - 30);
        }
    }

    takeDamage(amount) {
        this.health -= amount;
        if (this.health < 0) this.health = 0;
    }

    drawHealthBar(ctx, screenX, screenY) {
        const barWidth = this.config.HEALTH_BAR_WIDTH;
        const barHeight = this.config.HEALTH_BAR_HEIGHT;
        const healthRatio = this.health / this.maxHealth;

        ctx.fillStyle = this.config.HEALTH_BAR_BACKGROUND_COLOR;
        ctx.fillRect(screenX - barWidth / 2, screenY, barWidth, barHeight);

        let barColor = this.config.HEALTH_BAR_COLOR_BAD;
        if (healthRatio > 0.66) {
            barColor = this.config.HEALTH_BAR_COLOR_GOOD;
        } else if (healthRatio > 0.33) {
            barColor = this.config.HEALTH_BAR_COLOR_MEDIUM;
        }
        ctx.fillStyle = barColor;
        ctx.fillRect(screenX - barWidth / 2, screenY, barWidth * healthRatio, barHeight);
    }
}

class Bullet {
    constructor(config, worldX, worldY, heading, owner) {
        this.config = config;
        this.worldX = worldX;
        this.worldY = worldY;
        this.heading = heading;
        this.owner = owner;
        this.speed = this.config.BULLET_SPEED;
        this.rangeTraveled = 0;
    }

    update() {
        const headingRad = this.heading * Math.PI / 180;
        this.worldX += this.speed * Math.cos(headingRad);
        this.worldY += this.speed * Math.sin(headingRad);
        this.rangeTraveled += this.speed;
    }

    draw(ctx, camX, camY) {
        const screenX = this.worldX - camX;
        const screenY = this.worldY - camY;

        ctx.save();
        ctx.translate(screenX, screenY);
        ctx.rotate(this.heading * Math.PI / 180);
        ctx.fillStyle = this.config.BULLET_COLOR;
        ctx.fillRect(-3, -1.5, 6, 3);
        ctx.restore();
    }
}

class RaceMarker {
    constructor(config, worldX, worldY, number) {
        this.config = config;
        this.worldX = worldX;
        this.worldY = worldY;
        this.number = number;
    }

    draw(ctx, camX, camY, isActive) {
        const screenX = this.worldX - camX;
        const screenY = this.worldY - camY;

        const color = isActive ? this.config.PASTEL_ACTIVE_MARKER_COLOR : this.config.PASTEL_MARKER_COLOR;
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(screenX, screenY, this.config.RACE_MARKER_VISUAL_RADIUS_WORLD, 0, 2 * Math.PI);
        ctx.fill();

        ctx.fillStyle = this.config.PASTEL_WHITE;
        ctx.beginPath();
        ctx.arc(screenX, screenY, this.config.RACE_MARKER_VISUAL_RADIUS_WORLD * 0.7, 0, 2 * Math.PI);
        ctx.fill();

        drawText(ctx, this.number, this.config.RACE_MARKER_VISUAL_RADIUS_WORLD * 1.1, screenX, screenY + 7, this.config.PASTEL_BLACK, null, true);
    }
}

class Runway {
    constructor(config, worldX, worldY, isDestination = false, isStart = false) {
        this.config = config;
        this.worldX = worldX;
        this.worldY = worldY;
        this.isDestination = isDestination;
        this.isStart = isStart;
    }

    draw(ctx, camX, camY) {
        const screenX = this.worldX - camX;
        const screenY = this.worldY - camY;

        let color = this.config.PASTEL_RUNWAY_COLOR;
        if (this.isDestination) {
            color = this.config.PASTEL_RUNWAY_DESTINATION_COLOR;
        } else if (this.isStart) {
            color = this.config.PASTEL_RUNWAY_START_COLOR;
        }

        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(screenX, screenY, this.config.DELIVERY_RUNWAY_VISUAL_RADIUS_WORLD, 0, 2 * Math.PI);
        ctx.fill();
    }
}

class DeliveryCheckpoint {
    constructor(config, worldX, worldY, number) {
        this.config = config;
        this.worldX = worldX;
        this.worldY = worldY;
        this.number = number;
    }

    draw(ctx, camX, camY, isActive) {
        const screenX = this.worldX - camX;
        const screenY = this.worldY - camY;

        const color = isActive ? this.config.DELIVERY_CHECKPOINT_COLOR_ACTIVE : this.config.DELIVERY_CHECKPOINT_COLOR_INACTIVE;
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.moveTo(screenX, screenY - this.config.DELIVERY_CHECKPOINT_VISUAL_RADIUS_WORLD);
        ctx.lineTo(screenX + this.config.DELIVERY_CHECKPOINT_VISUAL_RADIUS_WORLD, screenY);
        ctx.lineTo(screenX, screenY + this.config.DELIVERY_CHECKPOINT_VISUAL_RADIUS_WORLD);
        ctx.lineTo(screenX - this.config.DELIVERY_CHECKPOINT_VISUAL_RADIUS_WORLD, screenY);
        ctx.closePath();
        ctx.fill();
    }
}
