# MicroBank Backend

A production-grade microservice banking backend built with FastAPI, PostgreSQL, Redis, Celery, Docker, and Traefik.  
Designed for a hands on learning on SDE + DevOps.

## Features

- **JWT Authentication** with role-based access (ADMIN / CUSTOMER)
- **Account management** with unique account numbers
- **Atomic transactions** (deposit, transfer) using PostgreSQL transactions
- **Interest calculation** via Celery background tasks
- **Redis caching** for account balances and login rate limiting
- **Microservice architecture** with four independent services
- **API Gateway** using Traefik (optional)
- **Database migrations** with Alembic
- **Structured logging** with Loguru
- **Fully containerised** with Docker Compose


- **Auth Service** – user registration, login, JWT issuance
- **Account Service** – create account, view balance (Redis cache)
- **Transaction Service** – deposit, transfer, history
- **Admin Service** – user/account listing, interest trigger (Celery)
- **Celery** – background interest calculation
- **Redis** – balance caching, login rate limiting
- **Traefik** – routes requests based on URL prefix (`/auth`, `/accounts`, etc.)

## Tech Stack

| Component       | Technology                           |
|-----------------|--------------------------------------|
| API Framework   | FastAPI                              |
| Database        | PostgreSQL (asyncpg)                 |
| ORM/Models      | SQLModel                             |
| Caching         | Redis                                |
| Background Jobs | Celery with Redis broker             |
| API Gateway     | Traefik                              |
| Auth            | JWT (python-jose, passlib[bcrypt])   |
| Migrations      | Alembic                              |
| Logging         | Loguru                               |
| Containerisation| Docker, Docker Compose               |


## API Endpoints

### Auth Service (`/auth`)

| Method | Endpoint   | Auth | Description                |
|--------|------------|------|----------------------------|
| POST   | `/register`| No   | Register a new user        |
| POST   | `/login`   | No   | Login, receive JWT         |
| GET    | `/me`      | Yes  | Get current user details   |

### Account Service (`/accounts`)

| Method | Endpoint   | Auth | Description                     |
|--------|------------|------|---------------------------------|
| POST   | `/`        | Yes  | Create a new account            |
| GET    | `/me`      | Yes  | Get my account details          |
| GET    | `/balance` | Yes  | Get current balance (cached)    |

### Transaction Service (`/transactions`)

| Method | Endpoint            | Auth | Description                        |
|--------|---------------------|------|------------------------------------|
| POST   | `/deposit`          | Yes  | Deposit money                      |
| POST   | `/transfer`         | Yes  | Transfer money to another account  |
| GET    | `/history`          | Yes  | List all my transactions           |
| GET    | `/{transaction_id}` | Yes  | Get a specific transaction         |

### Admin Service (`/admin`) – requires `ADMIN` role

| Method | Endpoint          | Auth | Description                            |
|--------|-------------------|------|----------------------------------------|
| POST   | `/interest/apply` | Yes  | Trigger interest calculation (Celery)  |
| GET    | `/users`          | Yes  | List all users                         |
| GET    | `/accounts`       | Yes  | List all accounts                      |


## Integration Testing

A standalone integration test script (`tests/integration_test.py`) validates the complete banking flow end‑to‑end directly against the running Docker services (ports 8001‑8004). It covers user registration, login, account creation, deposit, transfer between two users, transaction history, transaction detail, and admin interest calculation.

**Run it after starting the containers** with `docker‑compose up`. Optionally promote a user to `ADMIN` in the database to test the admin endpoints.

```bash
# Set environment variables (Windows example)
set ADMIN_EMAIL=your_admin_email@example.com
set ADMIN_PASSWORD=your_password

# Run the script
python tests/integration_test.py


## CI/CD Pipeline (GitLab)

Every push and merge request is automatically validated by a professional GitLab CI/CD pipeline defined in `.gitlab-ci.yml`. The pipeline ensures code quality, catches vulnerabilities, and verifies the entire microservice stack works end‑to‑end before any code is merged.

### Pipeline Stages

| Stage | What it does |
|-------|--------------|
| **setup** | Installs all Python dependencies (cached for speed) |
| **lint** | Runs Ruff to catch code style issues and potential bugs |
| **security** | Scans dependencies for known vulnerabilities with `pip‑audit` |
| **build** | Builds Docker images for every microservice |
| **integration_test** | Starts the full stack (services + DB + Redis + Celery), waits for health, executes the integration test script, then cleans up |

### Key Features

- **Docker‑in‑Docker (DinD)** – the pipeline builds images and runs containers inside the CI environment
- **Caching** – pip cache is shared between stages to speed up repeated runs
- **Secrets management** – sensitive values (JWT secret, DB credentials) are stored as GitLab CI/CD Variables, never in code
- **Fail‑fast** – if any stage fails, the pipeline stops and the merge is blocked
- **Automatic cleanup** – containers and volumes are destroyed after tests, keeping runners clean

### Setup Instructions

1. Push the `.gitlab-ci.yml` file to your repository (already included).
2. In GitLab, go to **Settings → CI/CD → Variables** and add:

   | Variable | Description |
   |----------|-------------|
   | `JWT_SECRET_KEY` | Secret key for signing JWT tokens |
   | `POSTGRES_USER` | PostgreSQL username (e.g., `postgres`) |
   | `POSTGRES_PASSWORD` | PostgreSQL password |
   | `POSTGRES_HOST` | Database hostname (use `db` for Docker Compose) |
   | `POSTGRES_DB` | Database name (e.g., `microbank`) |
   | `REDIS_HOST` | Redis hostname (use `redis`) |
   | `ADMIN_EMAIL` | Email of an admin user (for admin tests) |
   | `ADMIN_PASSWORD` | Password of that admin user |

   Mask all secret values for safety.

3. After setting the variables, any new commit or merge request will automatically trigger the pipeline.

### Pipeline Badge

To show the current pipeline status in this README, add the badge from **Settings → CI/CD → General pipelines → Pipeline status**.