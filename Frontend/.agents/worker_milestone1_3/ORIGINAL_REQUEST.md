## 2026-07-15T14:41:20Z
You are a Code Implementer (teamwork_preview_worker).
Your working directory is: E:\friends\Noman\ECP-main\Frontend\.agents\worker_milestone1_3
Your parent is: sub_orch_milestone1 (conversation ID: ecdcd25d-078a-4824-892c-566d0f1ca380)
The target workspace is: E:\friends\Noman\ECP-main\Frontend

Your task is to fix the runtime crashes, router mismatches, and route-guard loader issues in the Milestone 1 codebase.
Please read the synthesis report E:\friends\Noman\ECP-main\Frontend\.agents\sub_orch_milestone1\synthesis_v3.md for instructions.

Specifically:
1. Refactor `src/App.jsx` to use a Data Router:
   - Use `createBrowserRouter` and `<RouterProvider>` instead of `<BrowserRouter>`.
   - Setup layout and routing structure using the routing array.
2. Fix `useBlocker` destructured parameters in `src/pages/Profile.jsx`:
   - Change `({ currentValue, nextLocation })` to `({ currentLocation, nextLocation })`.
3. In `src/context/AuthContext.jsx`, remove the calls to `setLoading(true)` / `setLoading(false)` inside `login`, `register`, and `updateProfile` to prevent route guards from unmounting forms during async loading transitions.
4. In `src/services/api.js`, change the fallback value for `degreePreference` from `'Master of Science'` to `'Master of Computer Science'` (which exists in the dropdown options of both Register.jsx and Profile.jsx).

After making these modifications, verify:
- `npm run lint`
- `npm run build`
Ensure both compile successfully without errors or warnings. Output a handoff report `handoff.md` in your working directory and notify me via send_message when complete.

MANDATORY INTEGRITY WARNING:
> DO NOT CHEAT. All implementations must be genuine. DO NOT
> hardcode test results, create dummy/facade implementations, or
> circumvent the intended task. A Forensic Auditor will independently
> verify your work. Integrity violations WILL be detected and your
> work WILL be rejected.
