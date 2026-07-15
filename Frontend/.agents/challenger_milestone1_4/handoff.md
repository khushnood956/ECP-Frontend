# Handoff Report

## 1. Observation

### A. React Router useBlocker Property Typo (Runtime Crash)
- **File Path**: `src/pages/Profile.jsx`
- **Line Numbers**: 54-58
- **Verbatim Code**:
```javascript
  const blocker = useBlocker(
    ({ currentValue, nextLocation }) => {
      return isDirty && currentValue.pathname !== nextLocation.pathname;
    }
  );
```
- **Finding**: The parameter destructured from the callback argument in `useBlocker` is named `currentValue`, but React Router v7's `useBlocker` hook provides `{ currentLocation, nextLocation, historyAction }`. Destructuring `currentValue` sets it to `undefined`, which immediately triggers a runtime exception (`TypeError: Cannot read properties of undefined (reading 'pathname')`) when the blocker triggers, crashing the client router.

### B. Mismatched Phone Input Selector
- **File Paths**: `tests/scenarios.spec.js` and `src/pages/Profile.jsx`
- **Line Number**: 198 in `tests/scenarios.spec.js`
- **Verbatim Code (Test)**:
```javascript
await page.fill('input[name="phone"]', '+15550199');
```
- **Finding**: The test suite attempts to populate a field named `phone` during profile customization. However, no phone input exists in the `Profile.jsx` component structure, nor does any phone field exist in the user profile model in `Register.jsx` or `api.js`. This causes the onboarding E2E test to fail.

### C. Static / Hardcoded Dashboard Component
- **File Paths**: `src/pages/Dashboard.jsx`, `tests/dashboard.spec.js`, and `tests/scenarios.spec.js`
- **Line Numbers**: 20, 30, 38, 46, 67-79 in `src/pages/Dashboard.jsx`
- **Verbatim Code**:
```javascript
<div className="stat-value">85%</div>
...
<div className="stat-value">12</div>
...
<div className="stat-value">3</div>
...
<div className="stat-value">4/5</div>
```
- **Finding**: All dashboard counters, trends, and recent applications lists are completely static and hardcoded. As a result, the dashboard does not reflect the state of the logged-in user. The E2E tests expect dynamic updates (e.g. `T2.31` expects zero-values for a new clean user, and `T3.1` expects updates to propagate). Because of this hardcoding, multiple tests (e.g., `T2.31`, `T3.1`, `T3.2`, `T3.3`, `T3.4`, `T3.5`, `T4.1`, `T4.2`) will fail.

### D. Missing Notifications Dropdown
- **File Paths**: `src/components/Topbar.jsx` and `tests/dashboard.spec.js`
- **Line Number**: 51 in `tests/dashboard.spec.js`
- **Verbatim Code (Test)**:
```javascript
const dropdown = page.locator('.notifications-dropdown');
await expect(dropdown).toBeVisible();
```
- **Finding**: The `Topbar.jsx` file contains a static bell icon but has no logic or UI elements corresponding to a `.notifications-dropdown`. Clicking the bell does not render a dropdown, causing `T1.24` to fail.

### E. Missing Users in Test Data Seeding
- **File Paths**: `tests/scenarios.spec.js` and `src/services/api.js`
- **Line Numbers**: 322-328 in `tests/scenarios.spec.js`
- **Verbatim Code (Test)**:
```javascript
    // 1. Login User A (Doctorate)
    await page.goto('/login');
    await page.fill('input[name="email"]', 'usera@test.com');
    await page.fill('input[name="password"]', 'PasswordA1!');
```
- **Finding**: Test `T4.5` attempts to log in as `usera@test.com` and `userb@test.com`. However, the mock database seeded in `api.js` contains only `student@test.com`. Since there is no prior registration step in this test case or global setup, this login fails with a "User not found" error.

---

## 2. Logic Chain

1. **Typos in useBlocker**:
   - In `Profile.jsx`, the destructured argument is `currentValue`.
   - React Router documentation defines the callback argument object properties as `currentLocation` and `nextLocation`.
   - Therefore, `currentValue` is undefined, causing a runtime crash (`TypeError`) when trying to evaluate `.pathname`.
   
2. **Missing UI fields**:
   - The E2E test `T4.1` attempts to interact with an input named `phone`.
   - `Profile.jsx` contains only inputs for `name`, `email`, `degreePreference`, `ieltsScore`, and `profileImg`.
   - Therefore, the test fails with an element selector timeout.
   
3. **Hardcoded state vs Dynamic tests**:
   - Tests evaluate metrics like "Saved Scholarships" starting from 0, or updating after actions.
   - `Dashboard.jsx` outputs static HTML strings for all values.
   - Therefore, assertions expecting clean state or dynamic changes will fail.

4. **Missing UI components**:
   - Test `T1.24` asserts that a `.notifications-dropdown` is displayed on bell click.
   - `Topbar.jsx` has no dropdown container or activation handler.
   - Therefore, the locator will fail to find `.notifications-dropdown` within the timeout window.

---

## 3. Caveats

- We were unable to execute terminal build and test runs due to CLI prompt permissions timing out on the Windows runner. All findings are derived through exhaustive static code analysis, structural review, and test script dry-runs.
- Assumptions made: It is assumed that the test suite (`tests/`) constitutes the definitive specification of product requirements, and any deviations in the page source are classified as implementation gaps.

---

## 4. Conclusion

- **Validation Error Classes**: `.error-message` classes are correctly configured in `Profile.jsx`, `Login.jsx`, and `Register.jsx`.
- **Success Classes**: `.success-message` and `.toast-success` are correctly rendered conditionally in `Profile.jsx`.
- **Form Canceling**: The Cancel button correctly resets inputs back to context user details.
- **Route Blocker**: The route blocker's integration in `Profile.jsx` contains a typo (`currentValue` instead of `currentLocation`) that results in a severe application crash on dirty state navigation.
- **Test Inconsistencies**: The test suite expects features that do not exist (e.g. `phone` input, notifications dropdown, and dynamic dashboard metrics), which will cause a high failure rate in E2E runs.

---

## 5. Verification Method

To verify these findings manually:
1. Open the project in a web browser, log in, navigate to `My Profile`, modify the name, and click any navigation link (e.g., `Dashboard`). Observe the runtime error crash.
2. Search `src/pages/Profile.jsx` for the string `currentValue` to verify the typo on line 55.
3. Review `src/pages/Profile.jsx` and confirm there is no form field with the name `phone`.
4. Inspect `src/pages/Dashboard.jsx` to confirm that stats indicators and tables are hardcoded.
