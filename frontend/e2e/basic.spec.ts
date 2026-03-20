import { test, expect } from '@playwright/test';

test('has title', async ({ page }) => {
  await page.goto('http://localhost:3000');
  // Expect a title "to contain" a substring.
  await expect(page).toHaveTitle(/Legal Lens/);
});

test('check dashboard link', async ({ page }) => {
  await page.goto('http://localhost:3000');
  // Confirm main elements are present
  await expect(page.getByText('Ask Legal Lens')).toBeVisible();
});
