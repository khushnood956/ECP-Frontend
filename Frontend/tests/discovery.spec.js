import { test, expect } from '@playwright/test';

test.describe('Scholarship & University Discovery UI - Tier 1 & 2', () => {

  test.beforeEach(async ({ page }) => {
    // Log in to access the portal
    await page.goto('/login');
    await page.fill('input[name="email"]', 'student@test.com');
    await page.fill('input[name="password"]', 'Password123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/');
  });

  // ==========================================
  // TIER 1: FEATURE COVERAGE (HAPPY PATHS)
  // ==========================================

  test('T1.6: Browse Scholarships List rendering', async ({ page }) => {
    await page.click('.nav-item:has-text("Scholarships")');
    await expect(page).toHaveURL('/scholarships');
    
    const cards = page.locator('.scholarship-card');
    await expect(cards).not.toHaveCount(0);
    await expect(cards.first().locator('.scholarship-title')).toBeVisible();
    await expect(cards.first().locator('.scholarship-amount')).toBeVisible();
  });

  test('T1.7: Search Scholarships by text keyword', async ({ page }) => {
    await page.goto('/scholarships');
    await page.fill('input[placeholder*="Search scholarships"]', 'Merit');
    await page.keyboard.press('Enter');
    
    const titles = page.locator('.scholarship-title');
    const count = await titles.count();
    for (let i = 0; i < count; i++) {
      const text = await titles.nth(i).textContent();
      expect(text.toLowerCase()).toContain('merit');
    }
  });

  test('T1.8: Filter Scholarships by degree preference', async ({ page }) => {
    await page.goto('/scholarships');
    await page.selectOption('select[name="degreeFilter"]', 'Masters');
    
    const tags = page.locator('.scholarship-degree-tag');
    const count = await tags.count();
    for (let i = 0; i < count; i++) {
      await expect(tags.nth(i)).toHaveText('Masters');
    }
  });

  test('T1.9: View Scholarship Detailed Profile', async ({ page }) => {
    await page.goto('/scholarships');
    await page.click('.scholarship-card:first-child .view-details-btn');
    
    await expect(page).toHaveURL(/\/scholarships\/\d+/);
    await expect(page.locator('.detail-title')).toBeVisible();
    await expect(page.locator('.detail-description')).toBeVisible();
    await expect(page.locator('.detail-eligibility')).toBeVisible();
  });

  test('T1.10: Bookmark/Save Scholarship from list', async ({ page }) => {
    await page.goto('/scholarships');
    const firstCard = page.locator('.scholarship-card').first();
    const saveBtn = firstCard.locator('.save-btn');
    
    const isInitiallySaved = await saveBtn.getAttribute('data-saved') === 'true';
    await saveBtn.click();
    
    // Check toggle works
    const afterClickSaved = await saveBtn.getAttribute('data-saved') === 'true';
    expect(afterClickSaved).toBe(!isInitiallySaved);
  });

  test('T1.11: Browse Universities List rendering', async ({ page }) => {
    await page.click('.nav-item:has-text("Universities")');
    await expect(page).toHaveURL('/universities');
    
    const cards = page.locator('.university-card');
    await expect(cards).not.toHaveCount(0);
    await expect(cards.first().locator('.university-name')).toBeVisible();
    await expect(cards.first().locator('.university-country')).toBeVisible();
  });

  test('T1.12: Search Universities by name/keyword', async ({ page }) => {
    await page.goto('/universities');
    await page.fill('input[placeholder*="Search universities"]', 'Toronto');
    await page.keyboard.press('Enter');
    
    const names = page.locator('.university-name');
    const count = await names.count();
    for (let i = 0; i < count; i++) {
      const text = await names.nth(i).textContent();
      expect(text.toLowerCase()).toContain('toronto');
    }
  });

  test('T1.13: Filter Universities by country', async ({ page }) => {
    await page.goto('/universities');
    await page.selectOption('select[name="countryFilter"]', 'Canada');
    
    const countries = page.locator('.university-country');
    const count = await countries.count();
    for (let i = 0; i < count; i++) {
      await expect(countries.nth(i)).toHaveText('Canada');
    }
  });

  test('T1.14: View University Detailed Profile', async ({ page }) => {
    await page.goto('/universities');
    await page.click('.university-card:first-child .view-details-btn');
    
    await expect(page).toHaveURL(/\/universities\/\d+/);
    await expect(page.locator('.university-detail-name')).toBeVisible();
    await expect(page.locator('.university-description')).toBeVisible();
  });

  test('T1.15: Browse University Programs list', async ({ page }) => {
    await page.goto('/universities');
    await page.click('.university-card:first-child .view-details-btn');
    
    const programs = page.locator('.program-item');
    await expect(programs).not.toHaveCount(0);
  });

  // ==========================================
  // TIER 2: BOUNDARY & CORNER CASES
  // ==========================================

  test('T2.11: Search scholarships with no results displays empty state', async ({ page }) => {
    await page.goto('/scholarships');
    await page.fill('input[placeholder*="Search scholarships"]', 'NonExistentScholarshipName123');
    await page.keyboard.press('Enter');
    
    await expect(page.locator('.empty-state-message')).toBeVisible();
    await expect(page.locator('.empty-state-message')).toContainText('No scholarships found');
    await expect(page.locator('button:has-text("Reset Filters")')).toBeVisible();
  });

  test('T2.12: Search scholarships with special characters handles safely', async ({ page }) => {
    await page.goto('/scholarships');
    await page.fill('input[placeholder*="Search scholarships"]', '!@#%^&*()_+');
    await page.keyboard.press('Enter');
    
    // Should not crash, displays empty state or runs fine
    await expect(page.locator('.empty-state-message')).toBeVisible();
  });

  test('T2.13: Filter combinations yielding zero results', async ({ page }) => {
    await page.goto('/scholarships');
    await page.selectOption('select[name="degreeFilter"]', 'PhD');
    await page.selectOption('select[name="fieldFilter"]', 'Music Therapy'); // Rare combination
    
    await expect(page.locator('.empty-state-message')).toBeVisible();
  });

  test('T2.14: Access non-existent scholarship ID via URL redirects to list', async ({ page }) => {
    await page.goto('/scholarships/999999'); // Invalid ID
    await expect(page).toHaveURL('/scholarships');
  });

  test('T2.15: Search universities with no results displays empty state', async ({ page }) => {
    await page.goto('/universities');
    await page.fill('input[placeholder*="Search universities"]', 'Atlantis Academy');
    await page.keyboard.press('Enter');
    
    await expect(page.locator('.empty-state-message')).toContainText('No universities found');
  });

  test('T2.16: Search universities with leading/trailing spaces trims and succeeds', async ({ page }) => {
    await page.goto('/universities');
    await page.fill('input[placeholder*="Search universities"]', '   Melbourne   ');
    await page.keyboard.press('Enter');
    
    const cards = page.locator('.university-card');
    await expect(cards).not.toHaveCount(0);
    await expect(cards.first().locator('.university-name')).toContainText('Melbourne');
  });

  test('T2.17: Access non-existent university ID via URL redirects to list', async ({ page }) => {
    await page.goto('/universities/888888');
    await expect(page).toHaveURL('/universities');
  });

  test('T2.18: Multi-filter scholarship combinations work conjunctively', async ({ page }) => {
    await page.goto('/scholarships');
    await page.selectOption('select[name="degreeFilter"]', 'Masters');
    await page.selectOption('select[name="regionFilter"]', 'North America');
    
    const cards = page.locator('.scholarship-card');
    const count = await cards.count();
    for (let i = 0; i < count; i++) {
      await expect(cards.nth(i).locator('.scholarship-degree-tag')).toHaveText('Masters');
      await expect(cards.nth(i).locator('.scholarship-region-tag')).toHaveText('North America');
    }
  });

  test('T2.19: Multi-filter university combinations work conjunctively', async ({ page }) => {
    await page.goto('/universities');
    await page.selectOption('select[name="countryFilter"]', 'Australia');
    await page.selectOption('select[name="programTypeFilter"]', 'Engineering');
    
    const cards = page.locator('.university-card');
    const count = await cards.count();
    for (let i = 0; i < count; i++) {
      await expect(cards.nth(i).locator('.university-country')).toHaveText('Australia');
    }
  });

  test('T2.20: Toggle save/bookmark multiple times rapidly', async ({ page }) => {
    await page.goto('/scholarships');
    const saveBtn = page.locator('.scholarship-card .save-btn').first();
    
    const initialSaved = await saveBtn.getAttribute('data-saved') === 'true';
    
    // Rapid clicks
    await saveBtn.click();
    await saveBtn.click();
    await saveBtn.click();
    
    // State should toggle exactly 3 times (net 1 change)
    const finalSaved = await saveBtn.getAttribute('data-saved') === 'true';
    expect(finalSaved).toBe(!initialSaved);
  });
});
