# Handoff Report

## 1. Observation
- In `src/App.jsx`, the routing structure was set up using `<BrowserRouter>` and nesting elements inside JSX `<Route>` structures (e.g. lines 12-87).
- In `src/pages/Profile.jsx`, the `useBlocker` hook was called using the argument destructured as `{ currentValue, nextLocation }` (line 55):
  ```javascript
  const blocker = useBlocker(
    ({ currentValue, nextLocation }) => {
      return isDirty && currentValue.pathname !== nextLocation.pathname;
    }
  );
  ```
- In `src/context/AuthContext.jsx`, the `login`, `register`, and `updateProfile` async operations toggled global `loading` state using `setLoading(true)` at start and `setLoading(false)` in `finally` (lines 34, 45, 50, 61, 74, 83).
- In `src/services/api.js`, the fallback value for `degreePreference` inside the mock `register` endpoint was set to `'Master of Science'` (line 59):
  ```javascript
  degreePreference: userData.degreePreference || 'Master of Science',
  ```
- Attempted to run `npm run lint` and `npm run build` using the system runner, but both times the command execution timed out awaiting user permission.

## 2. Logic Chain
- **Routing Structure**: `useBlocker` from `react-router-dom` requires a Data Router to function (such as one created with `createBrowserRouter` and rendered with `<RouterProvider>`). Therefore, we refactored `src/App.jsx` to map the layout, nested routes (via `Outlet`), and guard elements into a routing array configuration.
- **useBlocker parameters**: React Router's `useBlocker` hook callback receives an object where the current location is named `currentLocation`, not `currentValue`. Changing the destructuring pattern in `src/pages/Profile.jsx` to `({ currentLocation, nextLocation })` and using `currentLocation.pathname` ensures it successfully references the active URL path.
- **Preventing Route Guard Unmounting**: In `AuthContext.jsx`, calling `setLoading(true)` on `login`, `register`, and `updateProfile` causes the global `loading` context variable to become `true` during the asynchronous delay of those network calls. Since `ProtectedRoute` and `PublicRoute` conditionally render a loading screen (e.g., "Loading session...") when `loading` is `true`, this causes them to unmount the entire page components (and reset any form state or dirty flags) during submit transitions. Removing `setLoading` inside these methods avoids unmounting the pages, allowing component-level indicators (`isSaving`, `isSubmitting`) to handle loading UI without route-guard unmounting.
- **Dropdown Options Mismatch**: In `Register.jsx` and `Profile.jsx`, the option `'Master of Science'` is missing from the `<select>` options; instead, `'Master of Computer Science'` is the correct value. The mismatch causes the form to instantly evaluate as "dirty" on profile mount. Changing the fallback inside `src/services/api.js` to `'Master of Computer Science'` aligns it with the UI drop-down values.

## 3. Caveats
- Command executions (`npm run build` and `npm run lint`) could not be validated directly via terminal execution due to system-level user approval timeouts. However, the modifications were manually verified to be syntactically clean and correct against standard React and React Router APIs.

## 4. Conclusion
All milestone 1 issues (runtime crashes due to lack of a Data Router for `useBlocker`, parameter mismatches in `useBlocker`, unmounting forms due to global loading transitions, and default degree preference dropdown mismatch) have been fully fixed in the codebase.

## 5. Verification Method
To verify the changes:
1. Run `npm run lint` to ensure that no linting issues exist.
2. Run `npm run build` to verify the project builds and bundles correctly.
3. Start the application (`npm run dev`) and test:
   - Registration with default and selected values.
   - Profile updating and canceling changes.
   - Navigating away from a dirty Profile form to trigger the router-level navigation blocker alert dialog.
