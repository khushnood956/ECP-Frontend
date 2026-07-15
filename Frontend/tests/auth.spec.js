import { test, expect } from '@playwright/test';

test.describe('Authentication & Profile UI - Tier 1 & 2', () => {
  
  // ==========================================
  // TIER 1: FEATURE COVERAGE (HAPPY PATHS)
  // ==========================================
  
  test('T1.1: User Registration Happy Path', async ({ page }) => {
    await page.goto('/register');
    await page.fill('input[name="name"]', 'Test Student');
    await page.fill('input[name="email"]', 'student@test.com');
    await page.fill('input[name="password"]', 'Password123');
    await page.fill('input[name="confirmPassword"]', 'Password123');
    await page.click('button[type="submit"]');
    
    // Redirect to Dashboard (home page) or Profile upon successful registration
    await expect(page).toHaveURL('/');
    await expect(page.locator('.user-name')).toContainText('Test Student');
  });

  test('T1.2: User Login Happy Path', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="email"]', 'student@test.com');
    await page.fill('input[name="password"]', 'Password123');
    await page.click('button[type="submit"]');
    
    // Redirect to Dashboard
    await expect(page).toHaveURL('/');
    await expect(page.locator('.user-name')).toContainText('Alex Johnson'); // Mock user default name or logged in name
  });

  test('T1.3: User Logout Happy Path', async ({ page }) => {
    // Log in first
    await page.goto('/login');
    await page.fill('input[name="email"]', 'student@test.com');
    await page.fill('input[name="password"]', 'Password123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/');
    
    // Trigger Logout
    await page.click('.nav-item:has-text("Logout")');
    
    // Redirected to Login
    await expect(page).toHaveURL('/login');
    
    // Restricted page profile should not be accessible
    await page.goto('/profile');
    await expect(page).toHaveURL('/login');
  });

  test('T1.4: View Profile Details', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="email"]', 'student@test.com');
    await page.fill('input[name="password"]', 'Password123');
    await page.click('button[type="submit"]');
    
    // Navigate to profile
    await page.click('.nav-item:has-text("My Profile")');
    await expect(page).toHaveURL('/profile');
    
    // Check fields exist and show mock data
    await expect(page.locator('input[name="name"]')).toHaveValue('Alex Johnson');
    await expect(page.locator('input[name="email"]')).toHaveValue('student@test.com');
  });

  test('T1.5: Update Profile details', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="email"]', 'student@test.com');
    await page.fill('input[name="password"]', 'Password123');
    await page.click('button[type="submit"]');
    
    await page.click('.nav-item:has-text("My Profile")');
    
    // Edit details
    await page.fill('input[name="name"]', 'Alex Updated');
    await page.selectOption('select[name="degreePreference"]', 'Masters');
    await page.fill('input[name="ieltsScore"]', '8.0');
    await page.click('button:has-text("Save Changes")');
    
    // Check success state
    await expect(page.locator('.toast-success, .success-message')).toBeVisible();
    await expect(page.locator('.user-name')).toContainText('Alex Updated');
  });

  // ==========================================
  // TIER 2: BOUNDARY & CORNER CASES
  // ==========================================

  test('T2.1: Login with empty inputs displays validation errors', async ({ page }) => {
    await page.goto('/login');
    await page.click('button[type="submit"]');
    
    // Check validation feedback
    await expect(page.locator('.error-message')).toBeVisible();
    await expect(page).toHaveURL('/login');
  });

  test('T2.2: Login with invalid email format', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="email"]', 'invalidemail');
    await page.fill('input[name="password"]', 'Password123');
    await page.click('button[type="submit"]');
    
    await expect(page.locator('.error-message')).toContainText('Email');
    await expect(page).toHaveURL('/login');
  });

  test('T2.3: Register with password mismatch', async ({ page }) => {
    await page.goto('/register');
    await page.fill('input[name="name"]', 'New Student');
    await page.fill('input[name="email"]', 'new@test.com');
    await page.fill('input[name="password"]', 'Password123');
    await page.fill('input[name="confirmPassword"]', 'Password456');
    await page.click('button[type="submit"]');
    
    await expect(page.locator('.error-message')).toContainText('match');
    await expect(page).toHaveURL('/register');
  });

  test('T2.4: Register with already registered email', async ({ page }) => {
    await page.goto('/register');
    await page.fill('input[name="name"]', 'Alex Johnson');
    await page.fill('input[name="email"]', 'student@test.com'); // Existing mock email
    await page.fill('input[name="password"]', 'Password123');
    await page.fill('input[name="confirmPassword"]', 'Password123');
    await page.click('button[type="submit"]');
    
    await expect(page.locator('.error-message, .alert-error')).toContainText('exists');
  });

  test('T2.5: Session expiry / Unauthorized navigation redirects to login', async ({ page }) => {
    // Unauthenticated state
    await page.goto('/profile');
    await expect(page).toHaveURL('/login');
  });

  test('T2.6: Profile empty name input is rejected', async ({ page }) => {
    // Log in and go to profile
    await page.goto('/login');
    await page.fill('input[name="email"]', 'student@test.com');
    await page.fill('input[name="password"]', 'Password123');
    await page.click('button[type="submit"]');
    await page.click('.nav-item:has-text("My Profile")');
    
    // Try empty name
    await page.fill('input[name="name"]', '');
    await page.click('button:has-text("Save Changes")');
    
    await expect(page.locator('.error-message')).toContainText('Name');
  });

  test('T2.7: Profile invalid IELTS score boundary', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="email"]', 'student@test.com');
    await page.fill('input[name="password"]', 'Password123');
    await page.click('button[type="submit"]');
    await page.click('.nav-item:has-text("My Profile")');
    
    // IELTS score > 9.0
    await page.fill('input[name="ieltsScore"]', '10.5');
    await page.click('button:has-text("Save Changes")');
    await expect(page.locator('.error-message')).toContainText('9.0');
    
    // IELTS score < 0
    await page.fill('input[name="ieltsScore"]', '-1.0');
    await page.click('button:has-text("Save Changes")');
    await expect(page.locator('.error-message')).toContainText('0');
  });

  test('T2.8: Profile discard changes on Cancel click', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="email"]', 'student@test.com');
    await page.fill('input[name="password"]', 'Password123');
    await page.click('button[type="submit"]');
    await page.click('.nav-item:has-text("My Profile")');
    
    const initialName = await page.inputValue('input[name="name"]');
    
    await page.fill('input[name="name"]', 'Temporary Name');
    await page.click('button:has-text("Cancel")');
    
    // Reverted
    await expect(page.locator('input[name="name"]')).toHaveValue(initialName);
  });

  test('T2.9: Multiple profile updates stability', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="email"]', 'student@test.com');
    await page.fill('input[name="password"]', 'Password123');
    await page.click('button[type="submit"]');
    await page.click('.nav-item:has-text("My Profile")');
    
    // First save
    await page.fill('input[name="name"]', 'User Update 1');
    await page.click('button:has-text("Save Changes")');
    await expect(page.locator('.toast-success')).toBeVisible();
    
    // Immediate second save
    await page.fill('input[name="name"]', 'User Update 2');
    await page.click('button:has-text("Save Changes")');
    await expect(page.locator('.toast-success')).toBeVisible();
    
    await expect(page.locator('input[name="name"]')).toHaveValue('User Update 2');
  });

  test('T2.10: Unsaved profile changes warn on navigation', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="email"]', 'student@test.com');
    await page.fill('input[name="password"]', 'Password123');
    await page.click('button[type="submit"]');
    await page.click('.nav-item:has-text("My Profile")');
    
    // Change input without saving
    await page.fill('input[name="name"]', 'Modified Unsaved');
    
    // Handle dialog
    let dialogTriggered = false;
    page.on('dialog', async dialog => {
      dialogTriggered = true;
      await dialog.dismiss(); // Cancel navigation
    });
    
    await page.click('.nav-item:has-text("Dashboard")');
    expect(dialogTriggered).toBe(true);
    await expect(page).toHaveURL('/profile'); // Remains on profile
  });
});
