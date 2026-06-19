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
