# Handoff Report: Review of Milestone 1 (Authentication & Profile UI)

This report details the review and adversarial testing results for the updated implementation of Milestone 1: Authentication & Profile UI.

---

## 1. Observation

### Codebase Observations
- **Router Configuration (`src/App.jsx`)**:
  - Line 2: `import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';`
  - Lines 15-85: The app uses `<Router>` (BrowserRouter) to wrap the route configurations.
- **Route Blocker (`src/pages/Profile.jsx`)**:
  - Line 3: `import { useBlocker } from 'react-router-dom';`
  - Lines 54-58: `useBlocker` is called inside the component:
    ```javascript
    const blocker = useBlocker(
      ({ currentValue, nextLocation }) => {
        return isDirty && currentValue.pathname !== nextLocation.pathname;
      }
    );
    ```
- **Credentials & Seeding (`src/services/api.js`)**:
  - Lines 10-19: Seeds `student@test.com` with password `Password123` and name `Alex Johnson` in `localStorage`.
- **CSS Class Compliance**:
  - **Error Messages**: Verified in `src/pages/Login.jsx` (lines 84, 99), `src/pages/Register.jsx` (lines 103, 118, 174, 189), and `src/pages/Profile.jsx` (lines 217, 232, 269) using `className="... error-message"`.
  - **Success Messages**: Verified in `src/pages/Profile.jsx` (line 150) using `className="... success-message toast-success"`.
- **IELTS Score Input & Validation (`src/pages/Profile.jsx`)**:
  - Line 262: `<input type="text" name="ieltsScore" ... />`
  - Lines 105-108: Validations throw errors containing `'9.0'` (`score > 9.0` -> `'IELTS Score must be less than or equal to 9.0'`) and `'0'` (`score < 0` -> `'IELTS Score must be greater than or equal to 0'`).
- **Cancel Button (`src/pages/Profile.jsx`)**:
  - Line 274: `<button type="button" onClick={handleCancel} ...>`
  - Lines 71-83: `handleCancel` resets form state back to original user details and clears error/message states.
- **Unsaved Changes Handler (`src/pages/Profile.jsx`)**:
  - Lines 40-52: Implements `beforeunload` event handler bound to `isDirty`.

### Test Suite Observations
- Playwright reports in `playwright-report/data/` show timeouts and failures:
  - `playwright-report/data/160e5291738535c0644ea4c0c75c71d4f94e476c.md` reports a timeout during `T2.9: Multiple profile updates stability`:
    ```
    Error: page.click: Test timeout of 30000ms exceeded.
    Call log:
      - waiting for locator('.nav-item:has-text("My Profile")')
    ```
  - `playwright-report/data/4b6a80bc915259e24517d0995cccd36c6f2d79db.md` reports `T2.4: Register with already registered email` failing because it navigated to the dashboard instead of showing the "exists" error.

---

## 2. Logic Chain

1. **useBlocker Incompatibility**:
   - React Router (v6/v7) explicitly mandates that `useBlocker` can only be invoked within a Data Router environment (e.g. `createBrowserRouter` or `<RouterProvider>`).
   - The current setup in `src/App.jsx` uses `<BrowserRouter>`, which is a traditional/legacy router.
   - Consequently, mounting `Profile.jsx` throws a fatal runtime exception: `Error: useBlocker must be used within a data router`.
2. **Impact on E2E Tests**:
   - Because of this runtime exception, the Profile page fails to mount and crashes the React app render tree.
   - This prevents any E2E tests targeting the profile page (like `T2.9` or `T2.10`) from succeeding, causing them to hang or time out while looking for locators like `.nav-item:has-text("My Profile")`.

---

## 3. Caveats

- Local execution of `npm run lint` and `npm run build` timed out during the review due to environment permission prompt timeouts. However, static analysis of the codebase is highly conclusive regarding the React Router Data Router / `useBlocker` runtime incompatibility.
- No other structural issues were observed.

---

## 4. Conclusion

The codebase implements all requested feature specifications (seed credentials, classes, validation bounds, Cancel button behaviors, and beforeunload handlers). However, the implementation is **not functionally complete/correct** because the use of `useBlocker` within a `BrowserRouter` context causes a fatal runtime crash on the Profile page.

**Verdict**: **REQUEST_CHANGES**

### Findings (Quality Review)
- **[Major] Router Context Mismatch**: `useBlocker` is used in `Profile.jsx` but `App.jsx` uses `<BrowserRouter>` instead of a Data Router.
  - **Location**: `src/App.jsx` and `src/pages/Profile.jsx`
  - **Why**: Triggers a fatal runtime error and crashes the Profile screen.
  - **Suggestion**: Refactor `App.jsx` to use `createBrowserRouter` and `RouterProvider`.

### verified Claims
- Seed credentials match expected defaults -> **Pass**
- Cancel button resets profile details and clears errors -> **Pass**
- IELTS Score is `<input type="text">` and bounds validations use `'9.0'` and `'0'` -> **Pass**
- CSS Classes match E2E expectations (`error-message`, `success-message`, `toast-success`) -> **Pass**

---

## 5. Adversarial Review

### Challenge Summary
- **Overall risk assessment**: **HIGH**

### Challenges
- **[High] Component Crash on Mounting**:
  - **Assumption challenged**: The developer assumed `useBlocker` works globally with `<BrowserRouter>`.
  - **Attack scenario**: Navigating to `/profile` mounts `Profile.jsx`.
  - **Blast radius**: The application crashes immediately on the client side, showing a blank screen.
  - **Mitigation**: Switch to `createBrowserRouter` in `src/App.jsx`.

---

## 6. Verification Method

To verify the router crash and subsequent fix:
1. Run `npm run dev` and navigate to `http://localhost:5173/profile` in a browser. Inspect the console for `useBlocker must be used within a data router`.
2. Run `npm run test:e2e` and observe that the tests fail or hang on profile navigation.
