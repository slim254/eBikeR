# eBikeR - Enterprise E-Bike Rental Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![React 18 & TypeScript](https://img.shields.io/badge/frontend-React%2018%20%2F%20TypeScript-informational)](https://react.dev/)
[![Django REST Framework](https://img.shields.io/badge/backend-Django%20REST-green.svg)](https://www.django-rest-framework.org/)
[![Docker & Compose](https://img.shields.io/badge/container-Docker%20%2F%20Compose-blueviolet)](https://www.docker.com/)

**eBikeR** is an enterprise-grade, full-stack microservice platform engineered for urban e-bike fleet management, real-time telemetry tracking, automated booking workflows, user authentication, reviews, ratings, and favorites management.

---

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Tech Stack](#tech-stack)
3. [Project Structure (`ebikeRent`)](#project-structure-ebikerent)
4. [Prerequisites & Environment Setup](#prerequisites--environment-setup)
5. [Quick Start with Docker](#quick-start-with-docker)
6. [Manual Local Development](#manual-local-development)
7. [Testing Suite](#testing-suite)
8. [API Documentation](#api-documentation)
9. [Contributing Guidelines](#contributing-guidelines)
10. [License](#license)

---

## Architecture Overview

```
                        ┌─────────────────────────┐
                        │    React TypeScript     │
                        │     Frontend (Vite)     │
                        └────────────┬────────────┘
                                     │ REST API / JWT
                                     ▼
                        ┌─────────────────────────┐
                        │   Django REST Backend   │
                        │  (Authentication, Bikes,│
                        │    Bookings, Reviews)   │
                        └────────────┬────────────┘
                                     │
                                     ▼
                        ┌─────────────────────────┐
                        │ PostgreSQL / SQLite DB  │
                        └─────────────────────────┘
```

The platform is decoupled into a high-performance **Django REST Framework** backend providing robust JWT-secured endpoints, and a responsive **React 18 / TypeScript / TailwindCSS** single-page application frontend.

---

## Tech Stack

### Backend (`ebikeRent/backend/`)
- **Language**: Python 3.11+
- **Framework**: Django 5.x & Django REST Framework (DRF)
- **Authentication**: SimpleJWT (JSON Web Tokens)
- **Database**: SQLite (Development) / PostgreSQL (Production)
- **Testing**: Pytest, pytest-django, factory_boy

### Frontend (`ebikeRent/frontend/`)
- **Framework**: React 18 with Vite
- **Language**: TypeScript
- **Styling**: Tailwind CSS & Lucide Icons
- **State Management**: React Hooks & Context API
- **HTTP Client**: Fetch API with interceptors

---

## Project Structure (`ebikeRent`)

```
eBikeR/
├── README.md               # Comprehensive system documentation
├── CONTRIBUTING.md         # Contribution workflow and guidelines
├── LICENSE                 # MIT Open Source License
├── Dockerfile              # Multi-stage production container build
├── docker-compose.yml      # Orchestration configuration
├── docs/                   # System architecture and API guides
│   ├── architecture.md
│   └── api_reference.md
└── ebikeRent/              # Core project directory
    ├── backend/            # Django backend application
    │   ├── backend/        # Core settings and URL configurations
    │   ├── bikes/          # E-bike catalog, status, and management
    │   ├── bookings/       # Rental management and booking workflows
    │   ├── favorites/      # User favorites management
    │   ├── ratings/        # Rating and review systems
    │   ├── users/          # Authentication and profile management
    │   ├── tests/          # Comprehensive pytest test suite
    │   ├── manage.py
    │   └── requirements.txt
    └── frontend/           # React TypeScript frontend application
        ├── src/
        ├── package.json
        └── vite.config.ts
```

---

## Quick Start with Docker

The fastest way to spin up the entire eBikeR stack is using **Docker Compose**:

1. Clone the repository and navigate to root:
   ```bash
   cd eBikeR
   ```
2. Build and start containers:
   ```bash
   docker compose up --build
   ```
3. Access services:
   - **Frontend Dashboard**: [http://localhost:3000](http://localhost:3000) (or configured port)
   - **Backend API**: [http://localhost:8000/api/](http://localhost:8000/api/)

---

## Manual Local Development

### 1. Backend Setup
```bash
cd ebikeRent/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8000
```

### 2. Frontend Setup
```bash
cd ebikeRent/frontend
npm install
npm run dev
```

---

## Testing Suite

Run comprehensive backend unit and integration tests using `pytest`:
```bash
cd ebikeRent/backend
pytest --cov=. --verbose
```

---

## Contributing
Please refer to [CONTRIBUTING.md](CONTRIBUTING.md) for coding standards, pull request workflows, and issue reporting.

## License
Distributed under the MIT License. See [LICENSE](LICENSE) for more information.
