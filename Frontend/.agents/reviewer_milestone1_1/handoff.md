# Milestone 1: Authentication & Profile UI Review Report

## 1. Observation
I have inspected the target codebase, analyzed all the files required for Milestone 1, run linting and build commands, and analyzed the existing E2E Playwright test suite.

### File Verification List
- `src/services/api.js` (Verified via `view_file`)
- `src/context/AuthContext.jsx` (Verified via `view_file`)
- `src/components/ProtectedRoute.jsx` (Verified via `view_file`)
- `src/components/PublicRoute.jsx` (Verified via `view_file`)
- `src/components/Sidebar.jsx` (Verified via `view_file`)
- `src/components/Topbar.jsx` (Verified via `view_file`)
- `src/components/Layout.jsx` (Verified via `view_file`)
- `src/pages/Dashboard.jsx` (Verified via `view_file`)
- `src/pages/Login.jsx` (Verified via `view_file`)
- `src/pages/Register.jsx` (Verified via `view_file`)
- `src/pages/Profile.jsx` (Verified via `view_file`)
- `src/App.jsx` (Verified via `view_file`)
- `src/index.css` (Verified via `view_file`)

### Build and Lint Output
- **Build (`npm run build`)**: Pass. Output was successfully built using Vite, generating production assets under `dist/`.
- **Lint (`npm run lint` / `oxlint`)**: Warning. Found 2 warnings and 0 errors:
  1. `react(only-export-components)` in `src/context/AuthContext.jsx:99:14` for `useAuth`. Vite's fast refresh works best when files exporting React components do not also export custom hooks.
  2. `eslint(no-unused-vars)` in `tests/applications.spec.js:2:8` for unused import `path`.

---

## 2. Quality Review Report

**Verdict**: **REQUEST_CHANGES**

### Findings

#### [Critical] Finding 1: Default Seeded User Credentials Mismatch
- **Where**: `src/services/api.js` (Lines 10-19)
- **Problem**: The API service seeds a default user with email `alex@example.com` and password `password123`. However, the E2E tests in `tests/auth.spec.js` and `tests/dashboard.spec.js` attempt to log in using the email `student@test.com` and password `Password123` (capital P). Since playwright runs tests in fresh contexts where localstorage is clean, all tests attempting to log in as the default user fail with "User not found".
- **Suggestion**: Update the seeded user email in `src/services/api.js` to `student@test.com` and the password to `Password123`.

#### [Critical] Finding 2: Missing Validation Error Class Names
- **Where**: `src/pages/Login.jsx` (Lines 84, 99), `src/pages/Register.jsx` (Lines 103, 118, 173, 188), and `src/pages/Profile.jsx` (Lines 139, 154)
- **Problem**: The UI components use the className `.field-error` to render validation messages. However, the E2E test suite asserts that validation error messages should be visible via selector `.error-message` (e.g., in `T2.1`, `T2.2`, `T2.3`, `T2.6`, `T2.7`). This mismatch causes validation tests to fail.
- **Suggestion**: Ensure that the validation error elements either include `.error-message` class name, or update the styles to map both classes.

#### [Major] Finding 3: Missing Elements in Profile Page
- **Where**: `src/pages/Profile.jsx`
- **Problem**: 
  1. **Missing Cancel Button**: There is no button with text "Cancel" to discard changes, which causes `T2.8` (discarding changes) to fail.
  2. **Select Dropdown for IELTS**: The IELTS score is rendered as a select dropdown containing values from `6.0` to `9.0`. The test case `T2.7` expects an input field where it can enter invalid boundary scores like `10.5` or `-1.0` and assert on validation error messages containing "9.0" and "0".
  3. **Toast Success Class Name**: Success alert uses `.alert-success` instead of `.toast-success` or `.success-message` expected by `T1.5` and `T2.9`.
  4. **Unsaved Changes Navigation Warning**: No logic is present to warning/alert the user when navigating away with unsaved changes. This causes `T2.10` to fail.
- **Suggestion**: Add a Cancel button that resets form state to `user` details, turn IELTS score input into a text field with number validation, add the `.toast-success` or `.success-message` class to the success alert, and add a router navigation blocker or event listener for dirty forms.

#### [Major] Finding 4: Missing Elements in Topbar & Sidebar Components
- **Where**: `src/components/Topbar.jsx`, `src/components/Sidebar.jsx`
- **Problem**:
  1. **Topbar Bell Dropdown**: The Bell button lacks any functionality. The tests `T1.24` and `T2.34` expect clicking this button to toggle a `.notifications-dropdown` menu containing a list with class `.notifications-list`.
  2. **Sidebar Collapse & Toggle Button**: The sidebar is fixed and does not support collapse/expand. Test `T2.32` expects the sidebar to have a class `.collapsed` and a toggle button `.sidebar-toggle-btn` visible on mobile resolutions.
- **Suggestion**: Implement the bell dropdown toggle state, and implement collapsible sidebar logic with a toggle button that appears on mobile viewports.

#### [Major] Finding 5: Hardcoded Values & Lack of Empty States on Dashboard
- **Where**: `src/pages/Dashboard.jsx`
- **Problem**:
  1. **Hardcoded Stats & Rows**: The stats cards and "Recent Applications" table have hardcoded mock data. For a brand new registered user (as tested in `T2.31`), the stats should read 0, and the table should display a placeholder element with class `.empty-placeholder`.
  2. **Missing Quick Links**: Test `T2.35` expects to click on a quick link with text "Explore Scholarships" or "Browse Scholarships" to route to `/scholarships`. These are completely missing from the Dashboard.
- **Suggestion**: Conditionally render Dashboard elements based on whether the logged in user has applications/saved scholarships (e.g., reading from a centralized store or mock context), and add the quick action links.

### Verified Claims
- **Claim**: Client-side routing via `react-router-dom` v7 for `/login`, `/register`, `/profile` is implemented.
  - *Status*: **Pass** (Verified in `src/App.jsx` and `src/components/Sidebar.jsx` where paths are defined correctly).
- **Claim**: Hook `useAuth` and provider `AuthContext` are implemented.
  - *Status*: **Pass** (Verified in `src/context/AuthContext.jsx`).
- **Claim**: Active preview of profile image exists on the Profile page.
  - *Status*: **Pass** (Verified in `src/pages/Profile.jsx`. Modifying the input value immediately updates the rendering of the `<img>` element on the left).
- **Claim**: Forms enforce validation (email required and format, password matching, required inputs).
  - *Status*: **Pass** (Verified in `src/pages/Login.jsx`, `src/pages/Register.jsx`, and `src/pages/Profile.jsx` logic).

---

## 3. Adversarial Review Report

**Overall risk assessment**: **HIGH**

### Challenges

#### [High] Challenge 1: Lack of Form Validation on Arbitrary Input Submissions
- **Assumption Challenged**: That using standard dropdown selects (like IELTS band or Degree preference) is sufficient UI constraint.
- **Attack Scenario**: If a user bypasses the UI select element or if the implementation changes, there is no validation on input ranges for `ieltsScore` in the form validator or context. An attacker could send a raw profile update payload with invalid numbers (e.g., `-5.0` or `99.9`) which would be saved directly to localStorage.
- **Blast Radius**: Corrupted academic profiles stored in localStorage, which may break rendering of stats, charts, or backend API queries later.
- **Mitigation**: Add numeric value validation checks in `validate()` before updating the profile state.

#### [High] Challenge 2: Client-side Routing Protection Bypass
- **Assumption Challenged**: That client-side `ProtectedRoute` is secure enough to protect sensitive pages.
- **Attack Scenario**: In an integrated environment, simply rendering `Outlet` or redirecting on the client side can be bypassed if the user modifies local React state or if page elements are server-rendered.
- **Blast Radius**: Unauthorized page layout access.
- **Mitigation**: While normal for SPA prototypes, it is critical that any real backend APIs perform robust session checks on requests, and tokens are securely managed.

#### [Medium] Challenge 3: Lack of State Reversion on Failed Profile Updates
- **Assumption Challenged**: That profile updates always succeed or that localStorage updates are atomic.
- **Attack Scenario**: If `api.updateProfile` throws an error mid-flight or if token resolution fails, the local `user` state inside `AuthContext` might get out of sync with the input fields, or vice versa, leaving the user with a modified UI state but an unmodified backend state.
- **Blast Radius**: Local profile UI showing incorrect details that were not persisted.
- **Mitigation**: Ensure that when `api.updateProfile` returns a failure, the profile page re-fetches or resets input fields to match the last known valid state from `useAuth().user`.

---

## 4. Logic Chain
1. I analyzed the test file `tests/auth.spec.js` and observed assertions targeting class names like `.error-message`, `.toast-success`, `.success-message`, and credentials `student@test.com`.
2. I cross-referenced this with `src/services/api.js`, `src/pages/Login.jsx`, `src/pages/Register.jsx`, and `src/pages/Profile.jsx` and found that the implementation uses `.field-error` instead of `.error-message`, `.alert-success` instead of `.toast-success`, and seeds `alex@example.com` instead of `student@test.com`.
3. I observed in `tests/dashboard.spec.js` that tests check for `.notifications-dropdown`, `.sidebar-toggle-btn`, mobile class `.collapsed`, empty states, and quick action cards. None of these elements are implemented in `Topbar.jsx`, `Sidebar.jsx`, or `Dashboard.jsx`.
4. Therefore, I conclude that while the application build and syntax are correct, the implementation fails E2E tests and lacks completeness against the detailed specification, requiring a request for changes.

---

## 5. Caveats
- Since running playwright tests timed out waiting for user confirmation after browser downloads completed, the exact failure stack traces could not be generated programmatically in this run. However, the static analysis of selectors and credentials confirms the mismatches.

---

## 6. Verification Method
- Execute `npm.cmd run lint` to verify linting warnings.
- Execute `npm.cmd run build` to verify the build output.
- Run `npx.cmd playwright test tests/auth.spec.js` to observe the specific failures in authentication tests.
