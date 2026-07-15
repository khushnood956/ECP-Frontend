# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: auth.spec.js >> Authentication & Profile UI - Tier 1 & 2 >> T1.3: User Logout Happy Path
- Location: tests\auth.spec.js:33:3

# Error details

```
Error: expect(page).toHaveURL(expected) failed

Expected: "http://localhost:5173/"
Received: "http://localhost:5173/login"
Timeout:  5000ms

Call log:
  - Expect "toHaveURL" with timeout 5000ms
    14 × unexpected value "http://localhost:5173/login"

```

```yaml
- text: EduConsultant
- heading "Welcome back" [level=2]
- paragraph: Sign in to your student account
- text: Email Address
- textbox "Email Address":
  - /placeholder: alex@example.com
- text: Password
- textbox "Password":
  - /placeholder: ••••••••
- button "Sign In"
- paragraph:
  - text: Don't have an account?
  - link "Register here":
    - /url: /register
```

# Test source

```ts
  1   | import { test, expect } from '@playwright/test';
  2   | 
  3   | test.describe('Authentication & Profile UI - Tier 1 & 2', () => {
  4   |   
  5   |   // ==========================================
  6   |   // TIER 1: FEATURE COVERAGE (HAPPY PATHS)
  7   |   // ==========================================
  8   |   
  9   |   test('T1.1: User Registration Happy Path', async ({ page }) => {
  10  |     await page.goto('/register');
  11  |     await page.fill('input[name="name"]', 'Test Student');
  12  |     await page.fill('input[name="email"]', 'student@test.com');
  13  |     await page.fill('input[name="password"]', 'Password123');
  14  |     await page.fill('input[name="confirmPassword"]', 'Password123');
  15  |     await page.click('button[type="submit"]');
  16  |     
  17  |     // Redirect to Dashboard (home page) or Profile upon successful registration
  18  |     await expect(page).toHaveURL('/');
  19  |     await expect(page.locator('.user-name')).toContainText('Test Student');
  20  |   });
  21  | 
  22  |   test('T1.2: User Login Happy Path', async ({ page }) => {
  23  |     await page.goto('/login');
  24  |     await page.fill('input[name="email"]', 'student@test.com');
  25  |     await page.fill('input[name="password"]', 'Password123');
  26  |     await page.click('button[type="submit"]');
  27  |     
  28  |     // Redirect to Dashboard
  29  |     await expect(page).toHaveURL('/');
  30  |     await expect(page.locator('.user-name')).toContainText('Alex Johnson'); // Mock user default name or logged in name
  31  |   });
  32  | 
  33  |   test('T1.3: User Logout Happy Path', async ({ page }) => {
  34  |     // Log in first
  35  |     await page.goto('/login');
  36  |     await page.fill('input[name="email"]', 'student@test.com');
  37  |     await page.fill('input[name="password"]', 'Password123');
  38  |     await page.click('button[type="submit"]');
> 39  |     await expect(page).toHaveURL('/');
      |                        ^ Error: expect(page).toHaveURL(expected) failed
  40  |     
  41  |     // Trigger Logout
  42  |     await page.click('.nav-item:has-text("Logout")');
  43  |     
  44  |     // Redirected to Login
  45  |     await expect(page).toHaveURL('/login');
  46  |     
  47  |     // Restricted page profile should not be accessible
  48  |     await page.goto('/profile');
  49  |     await expect(page).toHaveURL('/login');
  50  |   });
  51  | 
  52  |   test('T1.4: View Profile Details', async ({ page }) => {
  53  |     await page.goto('/login');
  54  |     await page.fill('input[name="email"]', 'student@test.com');
  55  |     await page.fill('input[name="password"]', 'Password123');
  56  |     await page.click('button[type="submit"]');
  57  |     
  58  |     // Navigate to profile
  59  |     await page.click('.nav-item:has-text("My Profile")');
  60  |     await expect(page).toHaveURL('/profile');
  61  |     
  62  |     // Check fields exist and show mock data
  63  |     await expect(page.locator('input[name="name"]')).toHaveValue('Alex Johnson');
  64  |     await expect(page.locator('input[name="email"]')).toHaveValue('student@test.com');
  65  |   });
  66  | 
  67  |   test('T1.5: Update Profile details', async ({ page }) => {
  68  |     await page.goto('/login');
  69  |     await page.fill('input[name="email"]', 'student@test.com');
  70  |     await page.fill('input[name="password"]', 'Password123');
  71  |     await page.click('button[type="submit"]');
  72  |     
  73  |     await page.click('.nav-item:has-text("My Profile")');
  74  |     
  75  |     // Edit details
  76  |     await page.fill('input[name="name"]', 'Alex Updated');
  77  |     await page.selectOption('select[name="degreePreference"]', 'Masters');
  78  |     await page.fill('input[name="ieltsScore"]', '8.0');
  79  |     await page.click('button:has-text("Save Changes")');
  80  |     
  81  |     // Check success state
  82  |     await expect(page.locator('.toast-success, .success-message')).toBeVisible();
  83  |     await expect(page.locator('.user-name')).toContainText('Alex Updated');
  84  |   });
  85  | 
  86  |   // ==========================================
  87  |   // TIER 2: BOUNDARY & CORNER CASES
  88  |   // ==========================================
  89  | 
  90  |   test('T2.1: Login with empty inputs displays validation errors', async ({ page }) => {
  91  |     await page.goto('/login');
  92  |     await page.click('button[type="submit"]');
  93  |     
  94  |     // Check validation feedback
  95  |     await expect(page.locator('.error-message')).toBeVisible();
  96  |     await expect(page).toHaveURL('/login');
  97  |   });
  98  | 
  99  |   test('T2.2: Login with invalid email format', async ({ page }) => {
  100 |     await page.goto('/login');
  101 |     await page.fill('input[name="email"]', 'invalidemail');
  102 |     await page.fill('input[name="password"]', 'Password123');
  103 |     await page.click('button[type="submit"]');
  104 |     
  105 |     await expect(page.locator('.error-message')).toContainText('Email');
  106 |     await expect(page).toHaveURL('/login');
  107 |   });
  108 | 
  109 |   test('T2.3: Register with password mismatch', async ({ page }) => {
  110 |     await page.goto('/register');
  111 |     await page.fill('input[name="name"]', 'New Student');
  112 |     await page.fill('input[name="email"]', 'new@test.com');
  113 |     await page.fill('input[name="password"]', 'Password123');
  114 |     await page.fill('input[name="confirmPassword"]', 'Password456');
  115 |     await page.click('button[type="submit"]');
  116 |     
  117 |     await expect(page.locator('.error-message')).toContainText('match');
  118 |     await expect(page).toHaveURL('/register');
  119 |   });
  120 | 
  121 |   test('T2.4: Register with already registered email', async ({ page }) => {
  122 |     await page.goto('/register');
  123 |     await page.fill('input[name="name"]', 'Alex Johnson');
  124 |     await page.fill('input[name="email"]', 'student@test.com'); // Existing mock email
  125 |     await page.fill('input[name="password"]', 'Password123');
  126 |     await page.fill('input[name="confirmPassword"]', 'Password123');
  127 |     await page.click('button[type="submit"]');
  128 |     
  129 |     await expect(page.locator('.error-message, .alert-error')).toContainText('exists');
  130 |   });
  131 | 
  132 |   test('T2.5: Session expiry / Unauthorized navigation redirects to login', async ({ page }) => {
  133 |     // Unauthenticated state
  134 |     await page.goto('/profile');
  135 |     await expect(page).toHaveURL('/login');
  136 |   });
  137 | 
  138 |   test('T2.6: Profile empty name input is rejected', async ({ page }) => {
  139 |     // Log in and go to profile
```