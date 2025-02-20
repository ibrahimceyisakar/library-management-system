# Library Management System API

A modern, role-based library management system built with FastAPI, Celery, and PostgreSQL. This system provides comprehensive APIs for managing books, patrons, and checkouts, with advanced authentication and automated tasks.

## Key Features

### Authentication and Access Control
- Role-based authentication system
- Admin and normal user roles
- Secure token-based authentication
- Granular access control for different API endpoints

### Book Management
- Create, Read, Update, Delete (CRUD) operations for books
- Admin-only book management
- Book search and filtering capabilities

### Patron Management
- User registration and profile management
- Role-based user permissions
- Patron account tracking

### Checkout System
- Book checkout and return workflows
- Overdue book tracking
- Admin endpoints for comprehensive checkout management
  - List all checkouts
  - View overdue books

### Automated Tasks
- Daily overdue book notifications (scheduled at 9 AM UTC)
- Background task processing with Celery
- Email notifications for various library events

### Technical Architecture
- **Backend**: FastAPI
- **Task Queue**: Celery
- **Database**: PostgreSQL
- **Message Broker**: Redis
- **Containerization**: Docker
- **Authentication**: OAuth2 with JWT

## Prerequisites

- Docker
- Docker Compose
- Git
- SMTP email account for notifications

## Quick Start Guide

### 1. Clone the Repository
```bash
git clone https://github.com/ibrahimceyisakar/fast-library.git
cd library-management-api
```

### 2. Configure Environment

#### SMTP Configuration
1. Prepare an SMTP email account (Gmail recommended)
2. Open `docker-compose.yml`
3. Replace placeholder values:
   - `SMTP_USERNAME`: Your email username
   - `SMTP_PASSWORD`: Your email app password
   - `SMTP_FROM_EMAIL`: Sender email address

### 3. Build and Run with Docker
```bash
# Build containers
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### 4. Create Superuser
```bash
# Access the web container
docker-compose exec web python -m app.management_commands.create_superuser \
    --email admin@example.com \
    --password yourpassword
```

### 5. Access Services
- **API Docs**: http://localhost:8000/docs
- **Swagger UI**: http://localhost:8000/redoc

## Security Notes
- Never commit sensitive credentials to version control
- Use environment variables for configuration
- Regularly update dependencies
- Enable two-factor authentication for your accounts

## Services
- **Web API**: FastAPI application
- **Celery Worker**: Background task processing
- **Celery Beat**: Scheduled tasks
- **PostgreSQL**: Primary database
- **Redis**: Message broker and cache

## Contributing
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
[Specify your license here]

## Issues
Report issues on the GitHub repository's issue tracker.
