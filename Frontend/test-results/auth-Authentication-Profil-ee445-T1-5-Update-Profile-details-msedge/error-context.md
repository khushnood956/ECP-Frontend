# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: auth.spec.js >> Authentication & Profile UI - Tier 1 & 2 >> T1.5: Update Profile details
- Location: tests\auth.spec.js:67:3

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: page.click: Test timeout of 30000ms exceeded.
Call log:
  - waiting for locator('.nav-item:has-text("My Profile")')

```

# Page snapshot

```yaml
- generic [ref=e4]:
  - generic [ref=e5]:
    - img [ref=e6]
    - generic [ref=e9]: EduConsultant
  - heading "Welcome back" [level=2] [ref=e10]
  - paragraph [ref=e11]: Sign in to your student account
  - generic [ref=e12]:
    - generic [ref=e13]:
      - generic [ref=e14]: Email Address
      - textbox "Email Address" [ref=e15]:
        - /placeholder: alex@example.com
    - generic [ref=e16]:
      - generic [ref=e17]: Password
      - textbox "Password" [ref=e18]:
        - /placeholder: ••••••••
    - button "Sign In" [ref=e19] [cursor=pointer]
  - paragraph [ref=e20]:
    - text: Don't have an account?
    - link "Register here" [ref=e21] [cursor=pointer]:
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
  39  |     await expect(page).toHaveURL('/');
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
> 73  |     await page.click('.nav-item:has-text("My Profile")');
      |                ^ Error: page.click: Test timeout of 30000ms exceeded.
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
  140 |     await page.goto('/login');
  141 |     await page.fill('input[name="email"]', 'student@test.com');
  142 |     await page.fill('input[name="password"]', 'Password123');
  143 |     await page.click('button[type="submit"]');
  144 |     await page.click('.nav-item:has-text("My Profile")');
  145 |     
  146 |     // Try empty name
  147 |     await page.fill('input[name="name"]', '');
  148 |     await page.click('button:has-text("Save Changes")');
  149 |     
  150 |     await expect(page.locator('.error-message')).toContainText('Name');
  151 |   });
  152 | 
  153 |   test('T2.7: Profile invalid IELTS score boundary', async ({ page }) => {
  154 |     await page.goto('/login');
  155 |     await page.fill('input[name="email"]', 'student@test.com');
  156 |     await page.fill('input[name="password"]', 'Password123');
  157 |     await page.click('button[type="submit"]');
  158 |     await page.click('.nav-item:has-text("My Profile")');
  159 |     
  160 |     // IELTS score > 9.0
  161 |     await page.fill('input[name="ieltsScore"]', '10.5');
  162 |     await page.click('button:has-text("Save Changes")');
  163 |     await expect(page.locator('.error-message')).toContainText('9.0');
  164 |     
  165 |     // IELTS score < 0
  166 |     await page.fill('input[name="ieltsScore"]', '-1.0');
  167 |     await page.click('button:has-text("Save Changes")');
  168 |     await expect(page.locator('.error-message')).toContainText('0');
  169 |   });
  170 | 
  171 |   test('T2.8: Profile discard changes on Cancel click', async ({ page }) => {
  172 |     await page.goto('/login');
  173 |     await page.fill('input[name="email"]', 'student@test.com');
```