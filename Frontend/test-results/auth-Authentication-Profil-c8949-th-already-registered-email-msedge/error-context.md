# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: auth.spec.js >> Authentication & Profile UI - Tier 1 & 2 >> T2.4: Register with already registered email
- Location: tests\auth.spec.js:121:3

# Error details

```
Error: expect(locator).toContainText(expected) failed

Locator: locator('.error-message, .alert-error')
Expected substring: "exists"
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toContainText" with timeout 5000ms
  - waiting for locator('.error-message, .alert-error')

```

```yaml
- text: EduConsultant
- list:
  - listitem:
    - link "Dashboard":
      - /url: /
  - listitem:
    - link "Scholarships":
      - /url: /scholarships
  - listitem:
    - link "Universities":
      - /url: /universities
  - listitem:
    - link "My Applications":
      - /url: /applications
  - listitem:
    - link "My Profile":
      - /url: /profile
  - listitem:
    - link "Settings":
      - /url: /settings
  - listitem:
    - button "Logout"
- textbox "Search scholarships, universities..."
- button
- button
- img "Alex Johnson"
- text: Alex Johnson Student
- heading "Student Dashboard" [level=1]
- paragraph: Track your applications and explore opportunities.
- text: Profile Completion 85% +15% since last login Saved Scholarships 12 2 deadlines approaching Active Applications 3 1 under review Documents Verified 4/5 Pending IELTS score
- heading "Recent Applications" [level=3]
- link "View All →":
  - /url: /applications
- table:
  - rowgroup:
    - row "University Program Intake Status":
      - columnheader "University"
      - columnheader "Program"
      - columnheader "Intake"
      - columnheader "Status"
  - rowgroup:
    - row "University of Toronto MSc Computer Science Fall 2026 Submitted":
      - cell "University of Toronto"
      - cell "MSc Computer Science"
      - cell "Fall 2026"
      - cell "Submitted"
    - row "University of Melbourne Master of Data Science Spring 2027 In Review":
      - cell "University of Melbourne"
      - cell "Master of Data Science"
      - cell "Spring 2027"
      - cell "In Review"
- heading "Tasks & Deadlines" [level=3]
- text: Upload IELTS Certificate Due in 2 days Review Scholarship Essay Due in 5 days
```

# Test source

```ts
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
> 129 |     await expect(page.locator('.error-message, .alert-error')).toContainText('exists');
      |                                                                ^ Error: expect(locator).toContainText(expected) failed
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
  174 |     await page.fill('input[name="password"]', 'Password123');
  175 |     await page.click('button[type="submit"]');
  176 |     await page.click('.nav-item:has-text("My Profile")');
  177 |     
  178 |     const initialName = await page.inputValue('input[name="name"]');
  179 |     
  180 |     await page.fill('input[name="name"]', 'Temporary Name');
  181 |     await page.click('button:has-text("Cancel")');
  182 |     
  183 |     // Reverted
  184 |     await expect(page.locator('input[name="name"]')).toHaveValue(initialName);
  185 |   });
  186 | 
  187 |   test('T2.9: Multiple profile updates stability', async ({ page }) => {
  188 |     await page.goto('/login');
  189 |     await page.fill('input[name="email"]', 'student@test.com');
  190 |     await page.fill('input[name="password"]', 'Password123');
  191 |     await page.click('button[type="submit"]');
  192 |     await page.click('.nav-item:has-text("My Profile")');
  193 |     
  194 |     // First save
  195 |     await page.fill('input[name="name"]', 'User Update 1');
  196 |     await page.click('button:has-text("Save Changes")');
  197 |     await expect(page.locator('.toast-success')).toBeVisible();
  198 |     
  199 |     // Immediate second save
  200 |     await page.fill('input[name="name"]', 'User Update 2');
  201 |     await page.click('button:has-text("Save Changes")');
  202 |     await expect(page.locator('.toast-success')).toBeVisible();
  203 |     
  204 |     await expect(page.locator('input[name="name"]')).toHaveValue('User Update 2');
  205 |   });
  206 | 
  207 |   test('T2.10: Unsaved profile changes warn on navigation', async ({ page }) => {
  208 |     await page.goto('/login');
  209 |     await page.fill('input[name="email"]', 'student@test.com');
  210 |     await page.fill('input[name="password"]', 'Password123');
  211 |     await page.click('button[type="submit"]');
  212 |     await page.click('.nav-item:has-text("My Profile")');
  213 |     
  214 |     // Change input without saving
  215 |     await page.fill('input[name="name"]', 'Modified Unsaved');
  216 |     
  217 |     // Handle dialog
  218 |     let dialogTriggered = false;
  219 |     page.on('dialog', async dialog => {
  220 |       dialogTriggered = true;
  221 |       await dialog.dismiss(); // Cancel navigation
  222 |     });
  223 |     
  224 |     await page.click('.nav-item:has-text("Dashboard")');
  225 |     expect(dialogTriggered).toBe(true);
  226 |     await expect(page).toHaveURL('/profile'); // Remains on profile
  227 |   });
  228 | });
  229 | 
```