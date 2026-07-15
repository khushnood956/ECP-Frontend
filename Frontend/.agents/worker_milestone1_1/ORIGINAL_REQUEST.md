## 2026-07-15T14:13:42Z
You are a Code Implementer (teamwork_preview_worker).
Your working directory is: E:\friends\Noman\ECP-main\Frontend\.agents\worker_milestone1_1
Your parent is: sub_orch_milestone1 (conversation ID: ecdcd25d-078a-4824-892c-566d0f1ca380)
The target workspace is: E:\friends\Noman\ECP-main\Frontend

Your task is to implement Milestone 1: Authentication & Profile UI features.
Please refer to the synthesized design decisions in E:\friends\Noman\ECP-main\Frontend\.agents\sub_orch_milestone1\synthesis.md and the explorer design specifications in E:\friends\Noman\ECP-main\Frontend\.agents\teamwork_preview_explorer_milestone1_1\handoff.md.

Specifically, you need to create/modify the following files in the workspace:
1. Create `src/services/api.js` (Mock API clients using localStorage to store accounts/token and simulate latency).
2. Create `src/context/AuthContext.jsx` (AuthContext, AuthProvider, and useAuth hook managing user, isAuthenticated, loading states).
3. Create `src/components/ProtectedRoute.jsx` and `src/components/PublicRoute.jsx` (Route guards blocking/allowing user navigation based on isAuthenticated state).
4. Create `src/components/Sidebar.jsx` and `src/components/Topbar.jsx` (Extracted layout components bound to the useAuth state, handling logout and display details).
5. Create `src/components/Layout.jsx` (Nested layout wrapping protected pages).
6. Create `src/pages/Dashboard.jsx` (Cleanly extracted dashboard page component).
7. Create `src/pages/Login.jsx`, `src/pages/Register.jsx`, and `src/pages/Profile.jsx` (Stateful components with validations, alerts, inputs, and image preview).
8. Modify `src/App.jsx` to register the routes (/login, /register, /profile, /) wrapped in AuthProvider, ProtectedRoute/PublicRoute, and Layout.
9. Modify `src/index.css` to append the styling overrides for forms, auth cards, inputs, error states, and responsive elements.

After implementation, you MUST verify your work by running:
1. `npm run lint` (to verify no syntax errors/warnings exist)
2. `npm run build` (to ensure Vite successfully compiles and bundles the workspace)

Document all commands and verification results in your handoff report (`handoff.md` in your working directory) and let me know you're done via send_message.

MANDATORY INTEGRITY WARNING:
> DO NOT CHEAT. All implementations must be genuine. DO NOT
> hardcode test results, create dummy/facade implementations, or
> circumvent the intended task. A Forensic Auditor will independently
> verify your work. Integrity violations WILL be detected and your
> work WILL be rejected.
