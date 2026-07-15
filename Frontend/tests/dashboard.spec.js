import { test, expect } from '@playwright/test';

test.describe('Dashboard & Navigation UI - Tier 1 & 2', () => {

  test.beforeEach(async ({ page }) => {
    // Log in
    await page.goto('/login');
    await page.fill('input[name="email"]', 'student@test.com');
    await page.fill('input[name="password"]', 'Password123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/');
  });

  // ==========================================
  // TIER 1: FEATURE COVERAGE (HAPPY PATHS)
  // ==========================================

  test('T1.21: Dashboard Stats Widget Rendering', async ({ page }) => {
    await expect(page.locator('.stat-card:has-text("Profile Completion")')).toBeVisible();
    await expect(page.locator('.stat-card:has-text("Saved Scholarships")')).toBeVisible();
    await expect(page.locator('.stat-card:has-text("Active Applications")')).toBeVisible();
    await expect(page.locator('.stat-card:has-text("Documents Verified")')).toBeVisible();
    
    // Check specific values exist
    const activeCount = await page.locator('.stat-card:has-text("Active Applications") .stat-value').textContent();
    expect(parseInt(activeCount.trim())).toBeGreaterThanOrEqual(0);
  });

  test('T1.22: Recent Applications Widget Rendering', async ({ page }) => {
    const widget = page.locator('.widget:has-text("Recent Applications")');
    await expect(widget).toBeVisible();
    
    // Check table headers
    await expect(widget.locator('th:has-text("University")')).toBeVisible();
    await expect(widget.locator('th:has-text("Program")')).toBeVisible();
    await expect(widget.locator('th:has-text("Status")')).toBeVisible();
  });

  test('T1.23: Tasks & Deadlines Widget Rendering', async ({ page }) => {
    const widget = page.locator('.widget:has-text("Tasks & Deadlines")');
    await expect(widget).toBeVisible();
    
    // Check tasks list
    await expect(widget.locator('.task-item, div:has-text("IELTS")')).toBeVisible();
  });

  test('T1.24: Notifications Bell Menu Open/Close', async ({ page }) => {
    const bellBtn = page.locator('.topbar-actions button:has(.lucide-bell), .icon-btn:has-text("Bell")');
    await bellBtn.click();
    
    const dropdown = page.locator('.notifications-dropdown');
    await expect(dropdown).toBeVisible();
    
    // Click outside to close
    await page.click('.page-title');
    await expect(dropdown).not.toBeVisible();
  });

  test('T1.25: Sidebar Nav Routing Verification', async ({ page }) => {
    const sidebar = page.locator('.sidebar');
    
    // Scholarships routing
    await sidebar.locator('.nav-item:has-text("Scholarships")').click();
    await expect(page).toHaveURL('/scholarships');
    await expect(sidebar.locator('.nav-item:has-text("Scholarships")')).toHaveClass(/active/);
    
    // Profile routing
    await sidebar.locator('.nav-item:has-text("My Profile")').click();
    await expect(page).toHaveURL('/profile');
    
    // Dashboard routing
    await sidebar.locator('.nav-item:has-text("Dashboard")').click();
    await expect(page).toHaveURL('/');
  });

  // ==========================================
  // TIER 2: BOUNDARY & CORNER CASES
  // ==========================================

  test('T2.31: Dashboard shows empty/zero states for brand new users', async ({ page }) => {
    // Log out current user and register new one to get clean state
    await page.click('.nav-item:has-text("Logout")');
    await page.goto('/register');
    await page.fill('input[name="name"]', 'New Clean User');
    await page.fill('input[name="email"]', 'clean@test.com');
    await page.fill('input[name="password"]', 'Password123');
    await page.fill('input[name="confirmPassword"]', 'Password123');
    await page.click('button[type="submit"]');
    
    await expect(page).toHaveURL('/');
    
    // Check clean user stats
    await expect(page.locator('.stat-card:has-text("Saved Scholarships") .stat-value')).toHaveText('0');
    await expect(page.locator('.stat-card:has-text("Active Applications") .stat-value')).toHaveText('0');
    await expect(page.locator('.stat-card:has-text("Documents Verified") .stat-value')).toHaveText('0/5');
    
    // Recent applications empty placeholder
    await expect(page.locator('.widget:has-text("Recent Applications") .empty-placeholder')).toBeVisible();
  });

  test('T2.32: Dashboard sidebar and content scaling on mobile (320px width)', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 320, height: 568 });
    
    // Sidebar should collapse, toggle button should appear
    const sidebar = page.locator('.sidebar');
    const toggleBtn = page.locator('.sidebar-toggle-btn');
    
    await expect(sidebar).toHaveClass(/collapsed/);
    await expect(toggleBtn).toBeVisible();
    
    // Click toggle to open
    await toggleBtn.click();
    await expect(sidebar).not.toHaveClass(/collapsed/);
  });

  test('T2.33: Dashboard grid layouts on ultra-wide viewports (1440px+)', async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 });
    
    // Check that layout grid is active and cards fit side-by-side (no wrap to 1 column)
    const statsGrid = page.locator('.stats-grid');
    await expect(statsGrid).toHaveCSS('display', 'grid');
    
    const columns = await statsGrid.evaluate(el => getComputedStyle(el).gridTemplateColumns.split(' ').length);
    expect(columns).toBe(4); // 4 columns for 4 stats cards
  });

  test('T2.34: Notifications dropdown handles large counts with scrollbar', async ({ page }) => {
    // Open notifications
    const bellBtn = page.locator('.topbar-actions button:has(.lucide-bell), .icon-btn:has-text("Bell")');
    await bellBtn.click();
    
    const dropdownList = page.locator('.notifications-list');
    await expect(dropdownList).toBeVisible();
    
    // Verify list scroll overflow styling
    const overflowY = await dropdownList.evaluate(el => getComputedStyle(el).overflowY);
    expect(overflowY).toBe('auto');
  });

  test('T2.35: Dashboard quick actions direct links clickability', async ({ page }) => {
    // Click quick link to Browse Scholarships
    const quickAction = page.locator('.quick-action-card:has-text("Explore Scholarships"), .quick-link:has-text("Browse Scholarships")');
    await quickAction.click();
    
    await expect(page).toHaveURL('/scholarships');
  });
});
