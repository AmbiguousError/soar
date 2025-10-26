const playwright = require('playwright');

async function runVerification() {
    const browser = await playwright.chromium.launch();
    const page = await browser.newPage();

    try {
        await page.goto('http://127.0.0.1:8080');

        // 1. Main Menu - Verify Container and Controls
        await page.setViewportSize({ width: 800, height: 600 });
        await page.screenshot({ path: 'jules-scratch/verification/01_new_features_main_menu_scaled.png' });

        // 2. Start Free Fly
        await page.click('#gameCanvas', { position: { x: 600, y: 450 } }); // Click center to start
        await page.waitForTimeout(500); // Wait for mode select screen
        await page.click('#gameCanvas', { position: { x: 600, y: 315 } }); // Click "Free Fly"
        await page.waitForTimeout(1000); // Wait for game to load

        // 3. Fly and Verify Tracer/Color
        await page.keyboard.down('ArrowRight');
        await page.waitForTimeout(1000);
        await page.keyboard.up('ArrowRight');
        await page.keyboard.down('ArrowUp');
        await page.waitForTimeout(500);
        await page.keyboard.up('ArrowUp');

        await page.screenshot({ path: 'jules-scratch/verification/02_new_features_free_fly.png' });

    } catch (error) {
        console.error('Verification script failed:', error);
    } finally {
        await browser.close();
    }
}

runVerification();
