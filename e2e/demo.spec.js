/**
 * e2e/demo.spec.js — T12: Playwright end-to-end test.
 * 
 * Setup: cd ui && npm install && npx playwright install
 * Run:   npx playwright test ../e2e/
 * 
 * Requires both backend (port 8000) and frontend (port 5173) running.
 */
import { test, expect } from '@playwright/test';

const BASE = 'http://localhost:5173';

test.describe('Antenatal Review Board E2E', () => {
  test('landing page loads', async ({ page }) => {
    await page.goto(BASE);
    await expect(page.locator('h1')).toContainText('Obstetric Safety');
    await expect(page.locator('text=Launch Dashboard')).toBeVisible();
  });

  test('navigates to dashboard', async ({ page }) => {
    await page.goto(BASE);
    await page.click('text=Launch Dashboard');
    await expect(page).toHaveURL(/\/dashboard/);
  });

  test('navigates to about page', async ({ page }) => {
    await page.goto(BASE);
    await page.click('text=About');
    await expect(page).toHaveURL(/\/about/);
    await expect(page.locator('text=8 Golden Rules')).toBeVisible();
  });

  test('submit C-0001 loads the dashboard', async ({ page }) => {
    await page.goto(BASE + '/dashboard');
    await expect(page.locator('text=Enter Case Data')).toBeVisible();
    await page.click('text=C-0001');
    await expect(page.locator('textarea').last()).toHaveValue(/C-0001/);
  });
});
