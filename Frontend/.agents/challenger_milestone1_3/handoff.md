# Handoff Report — Challenger Milestone 1 Verification

This report provides the verification findings, logical analysis, and concrete recommendations for the Milestone 1 implementation of the EduConsultant Student Portal Frontend.

---

## 1. Observation

Direct observations and code excerpts from the codebase:

### A. Router Setup in `src/App.jsx`
- **File Path**: `src/App.jsx` (lines 12–15)
- **Code excerpt**:
  ```jsx
  const App = () => {
    return (
      <AuthProvider>
        <Router>
  ```
  Where `Router` is imported as (line 2):
  `import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';`

### B. Navigation Blocker in `src/pages/Profile.jsx`
- **File Path**: `src/pages/Profile.jsx` (lines 54–68)
- **Code excerpt**:
  ```jsx
  const blocker = useBlocker(
    ({ currentValue, nextLocation }) => {
      return isDirty && currentValue.pathname !== nextLocation.pathname;
    }
  );

  useEffect(() => {
    if (blocker.state === 'blocked') {
      const confirmProceed = window.confirm('You have unsaved changes. Are you sure you want to leave?');
      if (confirmProceed) {
        blocker.proceed();
      } else {
        blocker.reset();
      }
    }
  }, [blocker, isDirty]);
  ```

### C. Loader Wrapper Unmounting in `src/components/PublicRoute.jsx`
- **File Path**: `src/components/PublicRoute.jsx` (lines 8–14)
- **Code excerpt**:
  ```jsx
  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', color: 'var(--primary-green)' }}>
        Loading...
      </div>
    );
  }
  ```

### D. Form Error Message CSS Selector Verification
- **File Path**: `src/pages/Profile.jsx` (line 217)
  ```jsx
  {errors.name && <span className="field-error error-message">{errors.name}</span>}
  ```
- **File Path**: `src/pages/Login.jsx` (line 84)
  ```jsx
  {errors.email && <span className="field-error error-message">{errors.email}</span>}
  ```
- **File Path**: `src/pages/Register.jsx` (line 189)
  ```jsx
  {errors.confirmPassword && <span className="field-error error-message">{errors.confirmPassword}</span>}
  ```

### E. Success Message Selector Verification
- **File Path**: `src/pages/Profile.jsx` (lines 149–154)
  ```jsx
  {message.text && (
    <div className={`alert ${message.type === 'success' ? 'alert-success success-message toast-success' : 'alert-error'}`} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
      {message.type === 'success' ? <Check size={18} /> : <ShieldAlert size={18} />}
      <span>{message.text}</span>
    </div>
  )}
  ```

### F. Cancel Button State Revert Verification
- **File Path**: `src/pages/Profile.jsx` (lines 71–83)
  ```jsx
  const handleCancel = () => {
    if (user) {
      setFormData({
        name: user.name || '',
        email: user.email || '',
        degreePreference: user.degreePreference || '',
        ieltsScore: user.ieltsScore || '',
        profileImg: user.profileImg || ''
      });
    }
    setErrors({});
    setMessage({ text: '', type: '' });
  };
  ```

### G. Dropdown Options Mismatch in `src/pages/Profile.jsx` vs `src/services/api.js`
- **File Path**: `src/services/api.js` (line 59)
  ```javascript
  degreePreference: userData.degreePreference || 'Master of Science',
  ```
- **File Path**: `src/pages/Profile.jsx` (lines 248–254)
  The select dropdown lists these options:
  - `Bachelor of Computer Science`
  - `Master of Computer Science`
  - `Master of Data Science`
  - `MBA`
  - `PhD in Engineering`
  - `Masters`
  *(Note: 'Master of Science' is not present in this list).*

---

## 2. Logic Chain

1. **Routing blocker fatal crash**: 
   - React Router v6 and v7 enforce that the `useBlocker` hook is only usable within components rendered by a Data Router (e.g. `createBrowserRouter` and `<RouterProvider>`).
   - Observations show `App.jsx` renders `<BrowserRouter>` (imported as `<Router>`) and does not configure a Data Router.
   - When the user navigates to `/profile`, `Profile.jsx` is mounted and invokes `useBlocker`. This triggers a fatal React crash: `Error: useBlocker must be used within a data router`.
   - Therefore, the Profile view is completely broken and crashes on load.

2. **Form unmounting during asynchronous actions**:
   - `AuthContext` changes `loading` to `true` during the async operations `login` and `register`.
   - `PublicRoute` and `ProtectedRoute` listen to `useAuth()` and, upon seeing `loading === true`, instantly replace their children component trees with the `Loading...` placeholder.
   - Consequently, the form components (`Login` and `Register`) are unmounted during submission.
   - If an operation fails, the form mounts *fresh*, losing user inputs and hiding errors because `setApiError` updates the unmounted instance state rather than the new one.

3. **Selector and UI Reset verification**:
   - The validation messages on `Login`, `Register`, and `Profile` forms correctly apply `.error-message` classes on error rendering spans.
   - Profile update success alerts correctly include both `success-message` and `toast-success` class names.
   - Cancel button handler correctly restores all fields of `formData` state to `user` state fields and resets form errors and alert messages.

4. **Dropdown options mismatch**:
   - If a user defaults to `Master of Science` upon registering (e.g. when no preference is selected), the value is saved in the database.
   - Upon visiting `/profile`, the dropdown select is unable to match the `'Master of Science'` string, defaulting the display representation to empty.
   - This causes `isDirty` to evaluate to `true` immediately because `'Master of Science'` (database value) is compared against `'Bachelor of Computer Science'` (or empty option value), preventing seamless navigation out of `/profile` without prompt warnings.

---

## 3. Caveats

- **Runtime Command Limitations**: Local command execution (`npm run lint` and `npm run test:e2e`) could not be evaluated live as terminal approvals timed out in the headless runner environment. The review is based on direct static analysis of code structures, configuration files, and previously saved Playwright test contexts.
- **Vite compilation warnings**: While the JS code structure is clean and builds successfully statically, minor ESLint warnings regarding unused imports or config overrides might exist depending on specific rule sets in `oxlint`.

---

## 4. Conclusion

- **Overall Assessment**: **HIGH RISK / BLOCKING FLAW FOUND**
- **Flaws Detected**:
  1. *[CRITICAL]* The Profile page throws a fatal React crash on load due to `useBlocker` mismatch with `BrowserRouter`.
  2. *[HIGH]* Form inputs and API error messages are completely lost/wiped out during login/register attempts due to premature loader unmounting.
  3. *[LOW]* The select element in `Profile.jsx` fails to list the default `'Master of Science'` preference, causing immediate dirty state warnings on loading profile.
- **Actionable Mitigations**:
  - Convert `App.jsx` to use a Data Router (i.e. `createBrowserRouter`) and render it via `<RouterProvider router={router} />`.
  - Modify `PublicRoute` and `ProtectedRoute` loader fallbacks to only apply on the initial session restore (`initializeAuth`) and not for form submissions.
  - Standardize `degreePreference` values between `api.js` defaults and `Profile.jsx` selection options.

---

## 5. Verification Method

To verify these findings:

1. **Check Router crash**:
   - Run the application: `npm run dev`
   - Attempt to navigate to `http://localhost:5173/profile` (after registering/logging in).
   - *Expected failure condition*: Component fails to load, throwing `Error: useBlocker must be used within a data router` in browser developer console.
2. **Check E2E Test Suite**:
   - Run `npm run test:e2e` (Playwright).
   - *Expected failure condition*: All profile tests (`T1.4`, `T1.5`, `T2.6-T2.10`) fail or time out.
3. **Verify Selectors**:
   - Inspect elements on forms when errors are triggered; verify they display `<span class="field-error error-message">`.
