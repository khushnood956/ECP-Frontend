## 2026-07-15T14:31:45Z
You are a Code Implementer (teamwork_preview_worker).
Your working directory is: E:\friends\Noman\ECP-main\Frontend\.agents\worker_milestone1_2
Your parent is: sub_orch_milestone1 (conversation ID: ecdcd25d-078a-4824-892c-566d0f1ca380)
The target workspace is: E:\friends\Noman\ECP-main\Frontend

Your task is to modify the existing Milestone 1 implementation to align it perfectly with the E2E test suite's expectations.
Please read E:\friends\Noman\ECP-main\Frontend\.agents\sub_orch_milestone1\synthesis_v2.md for the list of required fixes.

Specifically, you must:
1. Seed `student@test.com` with password `Password123` and name `Alex Johnson` in `src/services/api.js` defaultUsers list.
2. In `Login.jsx`, `Register.jsx`, and `Profile.jsx`, change field error span class names to include `error-message`.
3. In `Profile.jsx`, change the success alert element class name to include `success-message` and `toast-success`.
4. In `Profile.jsx`, change the `ieltsScore` select dropdown to a text input `<input type="text" name="ieltsScore" ... />` and implement numeric validators:
   - Check if the score is between 0 and 9.0.
   - If user input > 9.0, show validation error containing "9.0".
   - If user input < 0, show validation error containing "0".
5. In `Profile.jsx` and `Register.jsx`, add an option with value `"Masters"` to the degreePreference select element (so Playwright selectOption matches it).
6. In `Profile.jsx`, implement a "Cancel" button that resets form inputs to the current user's profile details and clears errors and dirty state.
7. In `Profile.jsx`, implement unsaved changes warning logic:
   - Use `useBlocker` from `react-router-dom` to block client-side navigation if the form is dirty, triggering `window.confirm`.
   - Add a window `beforeunload` listener to warn the user on page refresh/unload if the form is dirty.
8. Add `/* eslint-disable react/only-export-components */` at the top of `src/context/AuthContext.jsx` to silence the React Fast Refresh warning.
9. Remove the unused `import path from 'path';` line at the top of `tests/applications.spec.js` to silence the ESLint no-unused-vars warning.

After modifying the files, run verification:
- `npm run lint`
- `npm run build`
Ensure both pass cleanly without errors. Write a handoff report `handoff.md` in your working directory and notify me via send_message when complete.

MANDATORY INTEGRITY WARNING:
> DO NOT CHEAT. All implementations must be genuine. DO NOT
> hardcode test results, create dummy/facade implementations, or
> circumvent the intended task. A Forensic Auditor will independently
> verify your work. Integrity violations WILL be detected and your
> work WILL be rejected.
