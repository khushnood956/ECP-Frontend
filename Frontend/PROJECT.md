# Project: EduConsultant Student Portal Prototype

## Architecture
- React 19 + Vite frontend application.
- Client-side routing via `react-router-dom` v7.
- Responsive layout featuring a fixed/toggleable Sidebar and dynamic Topbar.
- Unified styling using standard CSS custom properties in `src/index.css` (green/white premium SaaS theme).
- Client-side mock state simulating database and backend responses (sessions, application workflow).
- Architecture prepared for FastAPI backend integration via isolated API services in `src/services/api.js`.

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|---|---|---|---|
| 1 | Milestone 1: Auth & Profile | Login, Register, Profile management, and Logout screens with simulated state. Routes: `/login`, `/register`, `/profile`. | None | IN_PROGRESS (Conv ID: ecdcd25d-078a-4824-892c-566d0f1ca380) |
| 2 | Milestone 2: Discovery UI | Searchable, filterable lists for scholarships & universities. Detailed item profiles, bookmarking, and application apply form UI. Routes: `/scholarships`, `/scholarships/:id`, `/universities`, `/universities/:id`. | Milestone 1 | PLANNED |
| 3 | Milestone 3: Applications & Documents | Application tracking timeline UI and mock file document manager (upload/list/delete UI). Routes: `/applications`, `/documents`. | Milestone 2 | PLANNED |
| 4 | Milestone 4: Dashboard Integration | Integrated Dashboard combining key metrics, recent actions, notifications, and aesthetic polishing. Route: `/`. | Milestone 3 | PLANNED |

## Interface Contracts
### Auth & Profile Store
- Context/Hook `useAuth` providing:
  - `user`: `{ name, email, profileImg, degreePreference, ieltsScore, ... }` (or null if logged out)
  - `isAuthenticated`: boolean
  - `login(email, password)`: validates and logs in
  - `register(userData)`: registers a new account
  - `logout()`: resets auth state
  - `updateProfile(newData)`: updates user details

### Discovery Store
- Context/Hook `useDiscovery` providing:
  - `scholarships`: list of mock scholarships
  - `universities`: list of mock universities
  - `savedScholarships`: list of saved scholarship IDs
  - `toggleSaveScholarship(id)`: saves/unsaves a scholarship
  - `applyToScholarship(applicationData)`: triggers new application entry

### Applications & Documents Store
- Context/Hook `useApplications` providing:
  - `applications`: list of applications with status timeline history (Submitted, Under Review, Accepted, Rejected)
  - `documents`: list of uploaded mock document metadata
  - `uploadDocument(fileData)`: adds file metadata to mock list
  - `deleteDocument(id)`: removes file from mock list

## Code Layout
- `src/components/` - Reusable UI components (Sidebar, Topbar, StatusBadge, Timeline, Modal, Card, Table)
- `src/context/` - Context providers for state simulation
- `src/pages/` - Page view components (Dashboard, Login, Register, Profile, Scholarships, Universities, Applications, Documents)
- `src/services/api.js` - Mock API service wrapper (for future FastAPI mapping)
