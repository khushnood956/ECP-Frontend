# Challenger Handoff Report - Milestone 1 Verification

This report provides the verification and empirical challenges for the Milestone 1 Authentication & Profile UI implementation.

---

## 1. Observation

### Build and Lint Commands
- Command: `npm.cmd run lint` (using `.cmd` due to Windows execution policy)
  - Result: Completed successfully with 0 errors and 2 warnings.
  - Verbatim Output:
    ```
    Found 2 warnings and 0 errors.
    Finished in 18ms on 20 files with 91 rules using 12 threads.
    ```
- Command: `npm.cmd run build`
  - Result: Completed successfully with 0 errors.
  - Verbatim Output:
    ```
    vite v8.1.4 building client environment for production...
    transforming...✓ 1792 modules transformed.
    rendering chunks...
    computing gzip size...
    dist/index.html                   0.45 kB │ gzip:  0.29 kB
    dist/assets/index-iOMzPRdo.css    6.10 kB │ gzip:  1.63 kB
    dist/assets/index-DTmHvWGi.js   264.00 kB │ gzip: 81.49 kB
    ✓ built in 752ms
    ```

### Code Base Inspection
- **File**: `src/context/AuthContext.jsx` (Lines 10–30)
  ```javascript
  useEffect(() => {
    const initializeAuth = async () => {
      const token = localStorage.getItem('educonsultant_token');
      if (token) {
        try {
          const profile = await api.getCurrentUser(token);
          if (profile) {
            setUser(profile);
          } else {
            localStorage.removeItem('educonsultant_token');
          }
        } catch (error) {
          console.error('Failed to restore session:', error);
          localStorage.removeItem('educonsultant_token');
        }
      }
      setLoading(false);
    };

    initializeAuth();
  }, []);
  ```
- **File**: `src/components/ProtectedRoute.jsx` (Lines 8–18)
  ```javascript
  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', color: 'var(--primary-green)' }}>
        Loading session...
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  ```
- **File**: `src/components/PublicRoute.jsx` (Lines 8–18)
  ```javascript
  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', color: 'var(--primary-green)' }}>
        Loading...
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }
  ```
- **File**: `src/services/api.js` (Lines 46–70, `register` function)
  ```javascript
  register: async (userData) => {
    await delay();
    const users = getStoredUsers();
    
    if (users.some(u => u.email.toLowerCase() === userData.email.toLowerCase())) {
      throw new Error('An account with this email already exists.');
    }

    const newUser = {
      name: userData.name,
      email: userData.email,
      password: userData.password,
      profileImg: userData.profileImg || `https://api.dicebear.com/7.x/adventurer/svg?seed=${encodeURIComponent(userData.name)}`,
      degreePreference: userData.degreePreference || 'Master of Science',
      ieltsScore: userData.ieltsScore || '7.0'
    };
    ...
  ```
- **File**: `src/pages/Profile.jsx` (Lines 182–197)
  ```javascript
  <select
    name="ieltsScore"
    value={formData.ieltsScore}
    onChange={handleChange}
    className="form-input"
    disabled={isSaving}
  >
    <option value="6.0">6.0</option>
    ...
  </select>
  ```
- **File**: `tests/auth.spec.js`
  - Line 30: `await expect(page.locator('.user-name')).toContainText('Alex Johnson');` (logs in as `student@test.com` which belongs to 'Test Student')
  - Line 77: `await page.selectOption('select[name="degreePreference"]', 'Masters');`
  - Line 78: `await page.fill('input[name="ieltsScore"]', '8.0');`
  - Line 82: `await expect(page.locator('.toast-success, .success-message')).toBeVisible();`
  - Line 95: `await expect(page.locator('.error-message')).toBeVisible();`
  - Line 161: `await page.fill('input[name="ieltsScore"]', '10.5');`
  - Line 181: `await page.click('button:has-text("Cancel")');`
  - Line 224: `await page.click('.nav-item:has-text("Dashboard")');` (testing dirty form unload dialog)

---

## 2. Logic Chain

1. **Race Conditions in AuthContext Loading State**:
   - `initializeAuth` is an async function in `useEffect`. If a user/test script invokes `login()` concurrently before `getCurrentUser()` completes, `login()` will succeed, update `user`, write the token, and set `loading` to `false`.
   - Once `getCurrentUser()` finishes, it will overwrite the newly logged-in user with the old profile context. If the old token was invalid, it clears the new token (`localStorage.removeItem('educonsultant_token')`), logging the user out immediately.
   - However, during normal UI flows, the routes are protected by `ProtectedRoute` / `PublicRoute` which render a blocking loading page, preventing user interaction with forms before `initializeAuth` resolves.

2. **Route Access Verification**:
   - `ProtectedRoute` intercepts all authenticated screens (`/`, `/profile`, placeholders) and redirects to `/login` if not authenticated.
   - `PublicRoute` intercepts public screens (`/login`, `/register`) and redirects to `/` if authenticated.
   - Session checks and redirects occur correctly based on the `isAuthenticated` state and `loading` flags.

3. **Form Validations Bypassability**:
   - All validation rules (email pattern, password length >= 6, matching passwords, name length) are implemented client-side in the React components (`Login.jsx`, `Register.jsx`, `Profile.jsx`).
   - The mock service layer `src/services/api.js` does NOT check name length, email patterns, password constraints, or matching criteria.
   - Therefore, a direct invocation of the `register` or `updateProfile` API functions (by executing them in the console or intercepting context) bypasses all validations, allowing empty names, malformed emails, and insecure passwords to be stored.

4. **Session Persistence**:
   - Session data is correctly written to `localStorage` using the key `educonsultant_token` on successful authentication.
   - On page refresh, the `useEffect` initializes correctly, retrieves the token from `localStorage`, and fetches user info from the mock store, preserving the logged-in session.

5. **Test Suite Out-of-Sync Errors**:
   - Comparing `tests/auth.spec.js` to implementation files exposes multiple discrepancies:
     - Tests query `.error-message` while the page renders `.field-error`.
     - Tests treat `ieltsScore` as an `<input>` text box while the UI implements it as a `<select>`.
     - Tests select option `'Masters'` from `degreePreference` which doesn't exist (valid values are long strings like `'Master of Computer Science'`).
     - Tests look for `.toast-success` or `.success-message` which do not exist (`Profile.jsx` renders `.alert-success`).
     - Tests try to click a non-existent "Cancel" button on the profile page.
     - Tests try to assert unsaved navigation warnings which are not implemented in the application code.

---

## 3. Caveats

- We attempted to run Playwright tests locally on Chromium, but the test runner execution timed out due to Windows developer prompt approval restrictions. We proceeded with direct source code analysis and manual verification.
- Our assessment assumes standard single-tab usage. In a multi-tab scenario, changes in one tab will not instantly update the AuthContext of another tab unless storage events are listened to.

---

## 4. Conclusion

- **Overall Risk Assessment**: **MEDIUM** (routing, happy-path session restoration, and form visual feedback work correctly, but API-level validation is missing, a race condition exists in simultaneous mock updates, and the test suite is entirely broken).
- **Core Findings**:
  1. **Race Condition**: Potential overwrites/token deletion in `AuthContext` if auth methods are called while the initial mount check is pending.
  2. **Bypassable Validations**: Mock backend functions (`api.register`, `api.updateProfile`) lack input validation, allowing bypass of UI restrictions.
  3. **Broken Test Suite**: `tests/auth.spec.js` will consistently fail due to incorrect CSS class queries, input selector mismatch (fill vs. select), and nonexistent button interactions.

---

## 5. Verification Method

To verify the test failures or run the application:
1. Run the build to verify build integrity:
   ```powershell
   npm.cmd run build
   ```
2. Inspect the discrepancy between selectors in `tests/auth.spec.js` and pages (`Login.jsx`, `Register.jsx`, `Profile.jsx`) to confirm the broken tests:
   - Check error CSS class: `.error-message` (test) vs `.field-error` (UI).
   - Check success CSS class: `.toast-success` (test) vs `.alert-success` (UI).
   - Check Cancel button: `button:has-text("Cancel")` (test) vs no Cancel button (UI).
