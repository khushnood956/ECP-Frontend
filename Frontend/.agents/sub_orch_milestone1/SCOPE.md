# Scope: Milestone 1 - Authentication & Profile UI

## Architecture
- Context provider `AuthContext` in `src/context/AuthContext.jsx` containing mock session state.
- Pages: `Login`, `Register`, `Profile` in `src/pages/`.
- Updated main routing structure in `src/App.jsx` using `react-router-dom` v7.
- Integration of auth state in `Sidebar` and `Topbar` components.
- Mock API calls encapsulated in `src/services/api.js` to prepare for backend integration.

## Sub-Milestones / Tasks
| # | Task | Scope | Status |
|---|---|---|---|
| 1 | Exploration & Architecture Plan | Investigate existing routes and design code layout | PLANNED |
| 2 | Mock API Service Creation | Implement mock auth API calls in `src/services/api.js` | PLANNED |
| 3 | Auth Context & Hook | Implement `AuthContext` (`useAuth`) to manage user session and profile | PLANNED |
| 4 | Routing & Guard Setup | Configure routing via `react-router-dom` v7 with public/protected page guards | PLANNED |
| 5 | Authentication Screens | Implement UI & form validation for `Login` and `Register` screens | PLANNED |
| 6 | Profile Management Screen | Implement UI & form validation for `Profile` screen with update support | PLANNED |
| 7 | Layout Integration | Connect `Sidebar` and `Topbar` with `useAuth` state and logout handler | PLANNED |
| 8 | Build & Lint Validation | Ensure `npm run build` and `npm run lint` compile cleanly without errors | PLANNED |

## Interface Contracts
### Auth Context / `useAuth` Hook
- `user`: `{ name, email, profileImg, degreePreference, ieltsScore, ... }` or null.
- `isAuthenticated`: boolean.
- `login(email, password)`: validates mock credentials and sets user session.
- `register(userData)`: registers a new mock user and sets session.
- `logout()`: clears mock user session.
- `updateProfile(newData)`: updates current user's profile details.
