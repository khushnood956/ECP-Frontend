# Synthesis v3: Final Architectural & Runtime Fixes

To resolve the remaining critical bugs identified by the reviewers and challengers:

1. **Refactor to Data Router** (`src/App.jsx`):
   - Replace `<BrowserRouter>` (imported as `Router`) with `createBrowserRouter` and `<RouterProvider>`.
   - Setup layout and nesting using the array-based router configuration. This is required for `useBlocker` to function.

2. **Fix `useBlocker` parameter destructuring** (`src/pages/Profile.jsx`):
   - Correct the `useBlocker` callback arguments: use `currentLocation` instead of `currentValue`.
   - The code should read:
     ```javascript
     const blocker = useBlocker(
       ({ currentLocation, nextLocation }) =>
         isDirty && currentLocation.pathname !== nextLocation.pathname
     );
     ```

3. **Prevent Route Guard Unmounting** (`src/context/AuthContext.jsx`):
   - Do NOT call `setLoading(true)` inside the `login`, `register`, or `updateProfile` methods.
   - The global `loading` state should only represent the initial session restore check (`useEffect` on mount).
   - Component-level buttons and submission UI should rely on their own local loading states (`isSubmitting` / `isSaving`) to prevent route guards from unmounting the page components and wiping validation/error states during async API delays.

4. **Align Dropdown Default Values** (`src/services/api.js`):
   - In `api.register` and any other defaults, set the fallback `degreePreference` to `'Master of Computer Science'` (which exists in the dropdown options) instead of `'Master of Science'` (which is missing and causes immediate form dirty state mismatch).
