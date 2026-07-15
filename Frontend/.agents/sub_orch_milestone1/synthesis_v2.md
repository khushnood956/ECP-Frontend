# Synthesis v2: Actions to Address Reviewer & Challenger Feedback

We need to implement the following changes to make the codebase fully aligned with the Playwright acceptance test suite:

1. **Default seeded user** (`src/services/api.js`):
   - Modify the default user database initialization. Seed `student@test.com` with password `Password123` and name `Alex Johnson`.
   
2. **Form validation class names** (`src/pages/Login.jsx`, `src/pages/Register.jsx`, `src/pages/Profile.jsx`):
   - Ensure field validation `<span className="...">` or standard error message container uses the class `error-message`.
   - Update styling in `src/index.css` to cover `.error-message` if needed (or map `.field-error` and `.error-message` to the same styling rules).
   
3. **Success Alert class names** (`src/pages/Profile.jsx`):
   - Ensure the success message element has the class name `success-message` and/or `toast-success` (alongside `alert-success`).

4. **IELTS Score Input** (`src/pages/Profile.jsx`):
   - Replace the select dropdown with an `<input type="text" name="ieltsScore" ... />`.
   - Add validators:
     - Check that value is a number between `0` and `9.0`.
     - If input > 9.0, show an error containing the text `'9.0'`.
     - If input < 0, show an error containing the text `'0'`.

5. **Degree Preference options** (`src/pages/Profile.jsx` and `src/pages/Register.jsx`):
   - Ensure there is an option with value `"Masters"` in `<select name="degreePreference">`.

6. **Cancel Button** (`src/pages/Profile.jsx`):
   - Add a "Cancel" button `<button type="button" ...>Cancel</button>` next to the Save button.
   - Upon clicking, reset form inputs to the values stored in `user` context and clear errors.

7. **Unsaved Changes Route Blocker** (`src/pages/Profile.jsx`):
   - Maintain an `isDirty` state tracking whether form values differ from the saved `user` data.
   - Use `useBlocker` from `react-router-dom` to intercept navigation when `isDirty` is true and prompt via `window.confirm`.
   - Add `beforeunload` event handler on `window` to prevent tab closure/refresh without saving.

8. **Lint Warning Cleanup**:
   - Add `/* eslint-disable react/only-export-components */` at the top of `src/context/AuthContext.jsx`.
   - Remove the unused `import path from 'path';` at the top of `tests/applications.spec.js`.
