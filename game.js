const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

const player = {
    x: canvas.width / 2,
    y: canvas.height / 2,
    speed: 0,
    angle: 0,
    width: 20,
    height: 10
};

const keys = {
    ArrowUp: false,
    ArrowDown: false,
    ArrowLeft: false,
    ArrowRight: false
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

function update() {
    if (keys.ArrowUp) {
        player.speed += 0.1;
    }
    if (keys.ArrowDown) {
        player.speed -= 0.1;
    }
    if (keys.ArrowLeft) {
        player.angle -= 0.05;
    }
    if (keys.ArrowRight) {
        player.angle += 0.05;
    }

    player.x += player.speed * Math.cos(player.angle);
    player.y += player.speed * Math.sin(player.angle);

    // Keep player within bounds
    if (player.x > canvas.width) player.x = 0;
    if (player.x < 0) player.x = canvas.width;
    if (player.y > canvas.height) player.y = 0;
    if (player.y < 0) player.y = canvas.height;
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.save();
    ctx.translate(player.x, player.y);
    ctx.rotate(player.angle);
    ctx.fillStyle = 'white';
    ctx.fillRect(-player.width / 2, -player.height / 2, player.width, player.height);
    ctx.restore();
}

function gameLoop() {
    update();
    draw();
    requestAnimationFrame(gameLoop);
}

gameLoop();
