import { test, expect } from '@playwright/test';

test.describe('E2E Scenarios (Tier 3 & Tier 4)', () => {

  // ==========================================================
  // TIER 3: CROSS-FEATURE COMBINATIONS (7 tests)
  // ==========================================================

  test('T3.1: Profile updates propagate to Dashboard metrics', async ({ page }) => {
    // 1. Log in
    await page.goto('/login');
    await page.fill('input[name="email"]', 'student@test.com');
    await page.fill('input[name="password"]', 'Password123');
    await page.click('button[type="submit"]');
    
    // 2. Go to profile and update preferences
    await page.click('.nav-item:has-text("My Profile")');
    await page.fill('input[name="name"]', 'Alex CrossTest');
    await page.selectOption('select[name="degreePreference"]', 'Doctorate');
    await page.fill('input[name="ieltsScore"]', '8.5');
    await page.click('button:has-text("Save Changes")');
    await expect(page.locator('.toast-success')).toBeVisible();
    
    // 3. Go to Dashboard and verify updates
    await page.click('.nav-item:has-text("Dashboard")');
    await expect(page.locator('.user-name')).toContainText('Alex CrossTest');
    await expect(page.locator('.stat-card:has-text("Profile Completion") .stat-value')).toHaveText('100%');
    await expect(page.locator('.widget:has-text("Tasks & Deadlines")')).not.toContainText('IELTS'); // Task completed
  });

  test('T3.2: Scholarship bookmark updates Dashboard saved count and list', async ({ page }) => {
    // 1. Log in
    await page.goto('/login');
    await page.fill('input[name="email"]', 'student@test.com');
    await page.fill('input[name="password"]', 'Password123');
    await page.click('button[type="submit"]');
    
    // 2. Go to Scholarships and save one
    await page.click('.nav-item:has-text("Scholarships")');
    const firstCard = page.locator('.scholarship-card').first();
    const title = await firstCard.locator('.scholarship-title').textContent();
    const saveBtn = firstCard.locator('.save-btn');
    await saveBtn.setAttribute('data-saved', 'false'); // Force unsaved state for test repeatability
    await saveBtn.click();
    
    // 3. Go to Dashboard and verify
    await page.click('.nav-item:has-text("Dashboard")');
    await expect(page.locator('.stat-card:has-text("Saved Scholarships") .stat-value')).not.toHaveText('0');
    await expect(page.locator('.widget:has-text("Saved Opportunities"), .widget:has-text("Tasks & Deadlines")')).toContainText(title.trim());
  });

  test('T3.3: Scholarship application updates Dashboard and Application Tracker', async ({ page }) => {
    // 1. Log in
    await page.goto('/login');
    await page.fill('input[name="email"]', 'student@test.com');
    await page.fill('input[name="password"]', 'Password123');
    await page.click('button[type="submit"]');
    
    // 2. Go to Scholarships and click Apply
    await page.click('.nav-item:has-text("Scholarships")');
    await page.click('.scholarship-card:first-child .view-details-btn');
    await page.click('button:has-text("Apply Now")');
    
    // 3. Submit application
    await page.fill('input[name="statementOfPurpose"]', 'Applying for Cross-Feature validation.');
    await page.click('button:has-text("Submit Application")');
    await page.click('button:has-text("View Applications")');
    
    // 4. Verify in tracker
    await expect(page).toHaveURL('/applications');
    const activeApp = page.locator('.application-card').first();
    await expect(activeApp.locator('.application-status')).toHaveText('Submitted');
    
    // 5. Verify on Dashboard
    await page.click('.nav-item:has-text("Dashboard")');
    await expect(page.locator('.stat-card:has-text("Active Applications") .stat-value')).not.toHaveText('0');
    await expect(page.locator('.widget:has-text("Recent Applications")')).toContainText('Submitted');
  });

  test('T3.4: Document upload updates Profile Completeness metric and checklists', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="email"]', 'student@test.com');
    await page.fill('input[name="password"]', 'Password123');
    await page.click('button[type="submit"]');
    
    // Get initial completeness
    const initialText = await page.locator('.stat-card:has-text("Profile Completion") .stat-value').textContent();
    
    // Upload document
    await page.click('.nav-item:has-text("Documents")');
    const fileChooserPromise = page.waitForEvent('filechooser');
    await page.click('.upload-dropzone');
    const fileChooser = await fileChooserPromise;
    await fileChooser.setFiles([{
      name: 'academic-cv.pdf',
      mimeType: 'application/pdf',
      buffer: Buffer.from('cv contents')
    }]);
    
    // Go to Dashboard
    await page.click('.nav-item:has-text("Dashboard")');
    const newText = await page.locator('.stat-card:has-text("Profile Completion") .stat-value').textContent();
    expect(parseInt(newText)).toBeGreaterThan(parseInt(initialText));
  });

  test('T3.5: Remove bookmark directly from Dashboard widget', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="email"]', 'student@test.com');
    await page.fill('input[name="password"]', 'Password123');
    await page.click('button[type="submit"]');
    
    // Ensure at least one saved item is visible on Dashboard
    const savedWidget = page.locator('.widget:has-text("Saved Opportunities"), .widget:has-text("Saved Scholarships")');
    await expect(savedWidget).toBeVisible();
    
    const initialCount = parseInt(await page.locator('.stat-card:has-text("Saved Scholarships") .stat-value').textContent());
    
    // Click unsave in widget
    await savedWidget.locator('.unsave-btn').first().click();
    
    // Verify count decremented
    await expect(page.locator('.stat-card:has-text("Saved Scholarships") .stat-value')).toHaveText((initialCount - 1).toString());
  });

  test('T3.6: Logout clears session state and isolates next user', async ({ page }) => {
    // 1. User A logs in, saves a scholarship
    await page.goto('/login');
    await page.fill('input[name="email"]', 'student@test.com');
    await page.fill('input[name="password"]', 'Password123');
    await page.click('button[type="submit"]');
    
    await page.click('.nav-item:has-text("Scholarships")');
    await page.locator('.scholarship-card .save-btn').first().click();
    
    // Log out User A
    await page.click('.nav-item:has-text("Logout")');
    
    // 2. User B registers new account
    await page.goto('/register');
    await page.fill('input[name="name"]', 'User B');
    await page.fill('input[name="email"]', 'userb@test.com');
    await page.fill('input[name="password"]', 'Password123');
    await page.fill('input[name="confirmPassword"]', 'Password123');
    await page.click('button[type="submit"]');
    
    // 3. User B has empty/clean state
    await expect(page.locator('.stat-card:has-text("Saved Scholarships") .stat-value')).toHaveText('0');
  });

  test('T3.7: Document uploaded during Application process appears in Document Manager', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="email"]', 'student@test.com');
    await page.fill('input[name="password"]', 'Password123');
    await page.click('button[type="submit"]');
    
    // Go to apply
    await page.goto('/scholarships');
    await page.click('.scholarship-card:first-child .view-details-btn');
    await page.click('button:has-text("Apply Now")');
    
    // In application modal, click "Upload new document instead"
    const fileChooserPromise = page.waitForEvent('filechooser');
    await page.click('.modal-upload-btn');
    const fileChooser = await fileChooserPromise;
    await fileChooser.setFiles([{
      name: 'sop-file.pdf',
      mimeType: 'application/pdf',
      buffer: Buffer.from('statement of purpose document')
    }]);
    
    // Submit application
    await page.fill('input[name="statementOfPurpose"]', 'Statement written');
    await page.click('button:has-text("Submit Application")');
    await page.click('button:has-text("Close")');
    
    // Navigate to Documents list, verify new document exists
    await page.click('.nav-item:has-text("Documents")');
    await expect(page.locator('.document-item:has-text("sop-file.pdf")')).toBeVisible();
  });


  // ==========================================================
  // TIER 4: REAL-WORLD APPLICATION SCENARIOS (5 tests)
  // ==========================================================

  test('T4.1: Full Student Onboarding & Discovery Journey', async ({ page }) => {
    // 1. Registration
    await page.goto('/register');
    await page.fill('input[name="name"]', 'Jane Doe');
    await page.fill('input[name="email"]', 'jane.doe@example.com');
    await page.fill('input[name="password"]', 'SecurePass1!');
    await page.fill('input[name="confirmPassword"]', 'SecurePass1!');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/');

    // 2. Profile Customization
    await page.click('.nav-item:has-text("My Profile")');
    await page.fill('input[name="phone"]', '+15550199');
    await page.selectOption('select[name="degreePreference"]', 'Undergraduate');
    await page.fill('input[name="ieltsScore"]', '7.5');
    await page.click('button:has-text("Save Changes")');
    await expect(page.locator('.toast-success')).toBeVisible();

    // 3. Search and filter Universities
    await page.click('.nav-item:has-text("Universities")');
    await page.fill('input[placeholder*="Search universities"]', 'Toronto');
    await page.selectOption('select[name="countryFilter"]', 'Canada');
    await page.click('.university-card:has-text("Toronto") .view-details-btn');
    await expect(page.locator('.university-detail-name')).toContainText('Toronto');

    // 4. Discover and save matching scholarship
    await page.click('.nav-item:has-text("Scholarships")');
    await page.fill('input[placeholder*="Search scholarships"]', 'Undergraduate');
    await page.selectOption('select[name="degreeFilter"]', 'Undergraduate');
    
    const card = page.locator('.scholarship-card:has-text("Undergraduate")').first();
    await card.locator('.save-btn').click();
    const title = await card.locator('.scholarship-title').textContent();

    // 5. Dashboard checks
    await page.click('.nav-item:has-text("Dashboard")');
    await expect(page.locator('.stat-card:has-text("Saved Scholarships") .stat-value')).toHaveText('1');
    await expect(page.locator('.widget:has-text("Saved Opportunities")')).toContainText(title.trim());
  });

  test('T4.2: End-to-End Application & Document Lifecycle', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="email"]', 'student@test.com');
    await page.fill('input[name="password"]', 'Password123');
    await page.click('button[type="submit"]');

    // 1. Pre-upload application documents
    await page.click('.nav-item:has-text("Documents")');
    const fcPromise1 = page.waitForEvent('filechooser');
    await page.click('.upload-dropzone');
    const fc1 = await fcPromise1;
    await fc1.setFiles([{ name: 'recomm_letter.pdf', mimeType: 'application/pdf', buffer: Buffer.from('recomm') }]);
    await expect(page.locator('.document-item:has-text("recomm_letter.pdf")')).toBeVisible();

    // 2. Discover scholarship and apply attaching uploaded document
    await page.click('.nav-item:has-text("Scholarships")');
    await page.click('.scholarship-card:first-child .view-details-btn');
    await page.click('button:has-text("Apply Now")');
    await page.fill('input[name="statementOfPurpose"]', 'Statement for lifecycle E2E.');
    await page.selectOption('select[name="documentId"]', 'recomm_letter.pdf');
    await page.click('button:has-text("Submit Application")');
    await expect(page.locator('.success-modal')).toBeVisible();
    await page.click('button:has-text("View Applications")');

    // 3. Track application on applications tracker
    await expect(page).toHaveURL('/applications');
    const firstApp = page.locator('.application-card').first();
    await expect(firstApp.locator('.application-status')).toHaveText('Submitted');
    
    // 4. Check dashboard widgets update
    await page.click('.nav-item:has-text("Dashboard")');
    await expect(page.locator('.stat-card:has-text("Active Applications") .stat-value')).toHaveText('1');
  });

  test('T4.3: Application Tracking and Status Progression Simulation', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="email"]', 'student@test.com');
    await page.fill('input[name="password"]', 'Password123');
    await page.click('button[type="submit"]');

    // Go to tracker page
    await page.click('.nav-item:has-text("My Applications")');
    await page.click('.application-card:first-child .view-timeline-btn');
    
    // Verify initial "Submitted" status highlight
    await expect(page.locator('.timeline-step:has-text("Submitted") .step-indicator')).toHaveClass(/completed/);
    await expect(page.locator('.timeline-step:has-text("Under Review") .step-indicator')).not.toHaveClass(/completed/);

    // Simulate Status Change (Trigger mock toggle in dev banner)
    await page.click('.dev-status-toggle[data-status="Under Review"]');
    await expect(page.locator('.timeline-step:has-text("Under Review") .step-indicator')).toHaveClass(/completed/);
    
    // Simulate Status Change to "Accepted"
    await page.click('.dev-status-toggle[data-status="Accepted"]');
    await expect(page.locator('.timeline-step:has-text("Accepted") .step-indicator')).toHaveClass(/completed/);
    await expect(page.locator('.congrats-card')).toBeVisible();
    await expect(page.locator('.congrats-card')).toContainText('Congratulations');
  });

  test('T4.4: Comprehensive Data Filtering & Decision Flow', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="email"]', 'student@test.com');
    await page.fill('input[name="password"]', 'Password123');
    await page.click('button[type="submit"]');

    // 1. Go to Scholarships list
    await page.click('.nav-item:has-text("Scholarships")');
    
    // 2. Multi-filter matching
    await page.fill('input[placeholder*="Search scholarships"]', 'Engineering');
    await page.selectOption('select[name="degreeFilter"]', 'Masters');
    await page.selectOption('select[name="regionFilter"]', 'Canada');

    // 3. Save multiple matching options
    const cards = page.locator('.scholarship-card');
    await expect(cards).toHaveCount(2); // Two matching engineering scholarships in Canada
    await cards.nth(0).locator('.save-btn').click();
    await cards.nth(1).locator('.save-btn').click();

    // 4. Compare list (Navigate to Saved bookmarks page/widget)
    await page.click('.nav-item:has-text("Dashboard")');
    await expect(page.locator('.stat-card:has-text("Saved Scholarships") .stat-value')).toHaveText('2');

    // 5. Delete one from bookmarks and apply to the other
    await page.locator('.widget:has-text("Saved Opportunities") .unsave-btn').first().click();
    await expect(page.locator('.stat-card:has-text("Saved Scholarships") .stat-value')).toHaveText('1');
    
    await page.locator('.widget:has-text("Saved Opportunities") .apply-btn').first().click();
    await page.fill('input[name="statementOfPurpose"]', 'Statement for final matched scholarship.');
    await page.click('button:has-text("Submit Application")');
    
    // 6. Check final stats
    await page.click('.nav-item:has-text("Dashboard")');
    await expect(page.locator('.stat-card:has-text("Active Applications") .stat-value')).toHaveText('1');
  });

  test('T4.5: Multi-User Academic Profile Isolation', async ({ page }) => {
    // 1. Login User A (Doctorate)
    await page.goto('/login');
    await page.fill('input[name="email"]', 'usera@test.com');
    await page.fill('input[name="password"]', 'PasswordA1!');
    await page.click('button[type="submit"]');
    
    await page.click('.nav-item:has-text("My Profile")');
    await page.selectOption('select[name="degreePreference"]', 'Doctorate');
    await page.click('button:has-text("Save Changes")');
    
    await page.click('.nav-item:has-text("Logout")');

    // 2. Login User B (Undergraduate)
    await page.goto('/login');
    await page.fill('input[name="email"]', 'userb@test.com');
    await page.fill('input[name="password"]', 'PasswordB1!');
    await page.click('button[type="submit"]');
    
    await page.click('.nav-item:has-text("My Profile")');
    await expect(page.locator('select[name="degreePreference"]')).toHaveValue('Undergraduate'); // Verify independent profile state

    await page.click('.nav-item:has-text("Logout")');

    // 3. Login User A again, check Doctorate still saved
    await page.goto('/login');
    await page.fill('input[name="email"]', 'usera@test.com');
    await page.fill('input[name="password"]', 'PasswordA1!');
    await page.click('button[type="submit"]');
    
    await page.click('.nav-item:has-text("My Profile")');
    await expect(page.locator('select[name="degreePreference"]')).toHaveValue('Doctorate');
  });
});
