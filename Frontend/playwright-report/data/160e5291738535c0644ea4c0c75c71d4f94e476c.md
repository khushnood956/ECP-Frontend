# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: auth.spec.js >> Authentication & Profile UI - Tier 1 & 2 >> T2.9: Multiple profile updates stability
- Location: tests\auth.spec.js:187:3

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
> 192 |     await page.click('.nav-item:has-text("My Profile")');
      |                ^ Error: page.click: Test timeout of 30000ms exceeded.
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