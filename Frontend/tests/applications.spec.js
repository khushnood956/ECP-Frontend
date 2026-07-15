import { test, expect } from '@playwright/test';

test.describe('Applications & Document Management UI - Tier 1 & 2', () => {

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

  test('T1.16: Submit Scholarship Application form modal', async ({ page }) => {
    await page.goto('/scholarships');
    await page.click('.scholarship-card:first-child .view-details-btn');
    await page.click('button:has-text("Apply Now")');
    
    // Fill Application Form Modal
    await page.fill('input[name="statementOfPurpose"]', 'This is my statement of purpose for this scholarship application.');
    await page.selectOption('select[name="documentId"]', { index: 1 }); // Select first uploaded document
    await page.click('button:has-text("Submit Application")');
    
    // Check confirmation screen / redirect
    await expect(page.locator('.success-modal, .toast-success')).toBeVisible();
    await page.click('button:has-text("View Applications")');
    await expect(page).toHaveURL('/applications');
  });

  test('T1.17: View active applications list', async ({ page }) => {
    await page.click('.nav-item:has-text("My Applications")');
    await expect(page).toHaveURL('/applications');
    
    const items = page.locator('.application-card');
    await expect(items).not.toHaveCount(0);
    await expect(items.first().locator('.program-title')).toBeVisible();
    await expect(items.first().locator('.application-status')).toBeVisible();
  });

  test('T1.18: Track application status timeline highlight', async ({ page }) => {
    await page.goto('/applications');
    await page.click('.application-card:first-child .view-timeline-btn');
    
    // Timeline contains statuses
    const timelineSteps = page.locator('.timeline-step');
    await expect(timelineSteps).not.toHaveCount(0);
    // At least one active state exists
    await expect(timelineSteps.locator('.active')).toBeVisible();
  });

  test('T1.19: Upload document in Document Manager', async ({ page }) => {
    await page.click('.nav-item:has-text("Documents")');
    await expect(page).toHaveURL('/documents');
    
    // Upload a test PDF file
    const fileChooserPromise = page.waitForEvent('filechooser');
    await page.click('.upload-dropzone');
    const fileChooser = await fileChooserPromise;
    
    // Use simulated buffer as file
    await fileChooser.setFiles([{
      name: 'transcript.pdf',
      mimeType: 'application/pdf',
      buffer: Buffer.from('dummy pdf content')
    }]);
    
    await expect(page.locator('.document-item:has-text("transcript.pdf")')).toBeVisible();
  });

  test('T1.20: Delete document in Document Manager', async ({ page }) => {
    await page.goto('/documents');
    
    // Ensure we have a document to delete
    const fileChooserPromise = page.waitForEvent('filechooser');
    await page.click('.upload-dropzone');
    const fileChooser = await fileChooserPromise;
    await fileChooser.setFiles([{
      name: 'delete-me.pdf',
      mimeType: 'application/pdf',
      buffer: Buffer.from('delete content')
    }]);
    
    const docItem = page.locator('.document-item:has-text("delete-me.pdf")');
    await expect(docItem).toBeVisible();
    
    // Click delete
    await docItem.locator('.delete-btn').click();
    await page.click('.confirm-delete-btn'); // Confirm delete modal
    
    await expect(docItem).not.toBeVisible();
  });

  // ==========================================
  // TIER 2: BOUNDARY & CORNER CASES
  // ==========================================

  test('T2.21: Apply modal validation rejects empty required fields', async ({ page }) => {
    await page.goto('/scholarships');
    await page.click('.scholarship-card:first-child .view-details-btn');
    await page.click('button:has-text("Apply Now")');
    
    // Try to submit blank statement
    await page.fill('input[name="statementOfPurpose"]', '');
    await page.click('button:has-text("Submit Application")');
    
    await expect(page.locator('.error-message')).toContainText('Statement');
  });

  test('T2.22: Double application submit prevention', async ({ page }) => {
    await page.goto('/scholarships');
    await page.click('.scholarship-card:first-child .view-details-btn');
    await page.click('button:has-text("Apply Now")');
    await page.fill('input[name="statementOfPurpose"]', 'Statement of purpose text.');
    await page.selectOption('select[name="documentId"]', { index: 1 });
    
    // Click submit multiple times quickly
    const submitBtn = page.locator('button:has-text("Submit Application")');
    await submitBtn.click();
    await expect(submitBtn).toBeDisabled(); // Button should disable immediately on first submit
  });

  test('T2.23: Apply button disabled for already applied scholarship', async ({ page }) => {
    // Go to scholarship details that we have already applied to
    await page.goto('/scholarships');
    // Assuming first scholarship is applied
    await page.click('.scholarship-card:first-child .view-details-btn');
    
    // Check Apply button state
    const applyBtn = page.locator('button:has-text("Apply Now"), button:has-text("Applied")');
    await expect(applyBtn).toBeDisabled();
    await expect(applyBtn).toHaveText('Applied');
  });

  test('T2.24: Document upload rejects invalid file extension', async ({ page }) => {
    await page.goto('/documents');
    
    const fileChooserPromise = page.waitForEvent('filechooser');
    await page.click('.upload-dropzone');
    const fileChooser = await fileChooserPromise;
    
    // Try uploading a .exe file
    await fileChooser.setFiles([{
      name: 'malware.exe',
      mimeType: 'application/octet-stream',
      buffer: Buffer.from('malicious code')
    }]);
    
    await expect(page.locator('.error-message, .toast-error')).toContainText('PDF');
  });

  test('T2.25: Document upload rejects file exceeding size limit', async ({ page }) => {
    await page.goto('/documents');
    
    const fileChooserPromise = page.waitForEvent('filechooser');
    await page.click('.upload-dropzone');
    const fileChooser = await fileChooserPromise;
    
    // Simulate a 12MB file (limit is 5MB)
    const largeBuffer = Buffer.alloc(12 * 1024 * 1024);
    await fileChooser.setFiles([{
      name: 'huge-file.pdf',
      mimeType: 'application/pdf',
      buffer: largeBuffer
    }]);
    
    await expect(page.locator('.error-message, .toast-error')).toContainText('size');
  });

  test('T2.26: Duplicate document filename appends count', async ({ page }) => {
    await page.goto('/documents');
    
    // Upload first file
    const fileChooserPromise1 = page.waitForEvent('filechooser');
    await page.click('.upload-dropzone');
    const fileChooser1 = await fileChooserPromise1;
    await fileChooser1.setFiles([{
      name: 'resume.pdf',
      mimeType: 'application/pdf',
      buffer: Buffer.from('resume 1')
    }]);
    
    // Upload duplicate file name
    const fileChooserPromise2 = page.waitForEvent('filechooser');
    await page.click('.upload-dropzone');
    const fileChooser2 = await fileChooserPromise2;
    await fileChooser2.setFiles([{
      name: 'resume.pdf',
      mimeType: 'application/pdf',
      buffer: Buffer.from('resume 2')
    }]);
    
    await expect(page.locator('.document-item:has-text("resume (1).pdf")')).toBeVisible();
  });

  test('T2.27: Cancel application form modal discards input', async ({ page }) => {
    await page.goto('/scholarships');
    await page.click('.scholarship-card:first-child .view-details-btn');
    await page.click('button:has-text("Apply Now")');
    
    await page.fill('input[name="statementOfPurpose"]', 'Discard this text');
    await page.click('button:has-text("Cancel")');
    
    // Re-open, input should be empty
    await page.click('button:has-text("Apply Now")');
    await expect(page.locator('input[name="statementOfPurpose"]')).toHaveValue('');
  });

  test('T2.28: Delete document confirmation modal cancellation', async ({ page }) => {
    await page.goto('/documents');
    
    // Click delete
    const firstItem = page.locator('.document-item').first();
    const docName = await firstItem.locator('.document-name').textContent();
    await firstItem.locator('.delete-btn').click();
    
    // Click cancel in confirmation modal
    await page.click('.cancel-delete-btn');
    
    // Document should still be present
    await expect(page.locator(`.document-item:has-text("${docName}")`)).toBeVisible();
  });

  test('T2.29: Empty document manager state renders helper guide', async ({ page }) => {
    await page.goto('/documents');
    
    // If we have documents, delete all of them first
    const deleteButtons = page.locator('.document-item .delete-btn');
    const count = await deleteButtons.count();
    for (let i = 0; i < count; i++) {
      await page.locator('.document-item .delete-btn').first().click();
      await page.click('.confirm-delete-btn');
    }
    
    await expect(page.locator('.empty-state-message')).toContainText('No documents uploaded');
  });

  test('T2.30: Document upload form dropzone drag over states change colors', async ({ page }) => {
    await page.goto('/documents');
    const dropzone = page.locator('.upload-dropzone');
    
    // Emulate drag-over by adding class
    await dropzone.evaluate(el => el.dispatchEvent(new Event('dragenter')));
    await expect(dropzone).toHaveClass(/drag-active/);
    
    await dropzone.evaluate(el => el.dispatchEvent(new Event('dragleave')));
    await expect(dropzone).not.toHaveClass(/drag-active/);
  });
});
