# EduConsultant Frontend

A premium, modern React 19 + Vite client application for the EduConsultant platform. This portal features a beautiful, fluid, function-driven design tailored for both Students and Agencies, featuring smooth transitions, clean typography, and a green-accented SaaS theme.

## Tech Stack
- **Framework**: React 19
- **Build Tool**: Vite
- **Routing**: React Router DOM (v7)
- **State & Data Fetching**: TanStack React Query (v5)
- **Styling**: Vanilla CSS with custom utility variables (`index.css`)
- **Testing**: Playwright & Vitest ready
- **Code Quality**: Oxlint

---

## Key Features

### 👨‍🎓 Student Portal
- **Dashboard**: High-level summary of applications, documents, deadlines, and personalized notifications.
- **Scholarship & University Search**: Multi-filter discovery interface allowing students to find scholarships, courses, and institutions based on country, eligibility, and fields of study.
- **Detailed Profiles**: Rich dynamic pages for each university and scholarship opportunity.
- **Application Tracking**: Transparent visual timeline tracking each application from submission, to review, offer, and visa stages.
- **Document Hub**: Fully integrated upload, status tracking, and deletion manager for academic and identity documents.

### 🏢 Agency Portal
- **Agency Dashboard**: Track student leads, registration statuses, and ongoing scholarship applications.
- **Leads Management**: Detailed logs, qualification status changes, and pipeline tracking for all incoming student prospects.
- **Scholarships Creation/Editing**: Directly publish and update scholarship programs available through the agency.
- **Profile Customization**: Detailed agency profiles, branding configurations, and credential reviews.

---

## Directory Structure

```
Frontend/
├── public/                 # Static assets
├── src/
│   ├── assets/             # Images and local SVGs
│   ├── components/         # Reusable presentation and layout components (Sidebar, Topbar, Layout)
│   │   └── shared/         # Common inputs, buttons, cards, skeletons, and route guards (RoleGuard)
│   ├── context/            # AuthContext and AppContext for state management
│   ├── hooks/              # Custom React hooks (useLeads, useCurrentAgency, etc.)
│   ├── pages/              # Primary page views (Dashboard, Login, Register, Profile, etc.)
│   │   └── agency/         # Specialized pages for Agency accounts
│   ├── services/           # API integration clients (using Axios/Fetch)
│   ├── utils/              # Helper functions
│   ├── App.jsx             # Router definition and context provider wrapping
│   ├── index.css           # Global CSS variables, design tokens, and core styling
│   └── main.jsx            # Application entry point
├── tests/                  # Integration and unit tests
└── vite.config.js          # Vite configurations
```

---

## Getting Started

### 1. Install Dependencies
Make sure you have Node.js 18+ installed. Run:
```bash
npm install
```

### 2. Start the Development Server
```bash
npm run dev
```
The application will launch on [http://localhost:5173](http://localhost:5173).

### 3. Production Build
To build the application for production deployment:
```bash
npm run build
```
The output files will be built into the `dist/` directory.

### 4. Running Linting
To check code quality and formatting rules:
```bash
npx oxlint
```
