# Library Management System API

A modern library management system built with FastAPI, Celery, and PostgreSQL. This system provides comprehensive APIs for managing books, patrons, and checkouts, along with automated tasks for notifications and reporting.

## Features

- **Book Management**: CRUD operations for books
- **Patron Management**: CRUD operations for library members
- **Checkout System**: Handle book checkouts and returns
- **Automated Notifications**: 
  - Daily overdue notices
  - Due soon reminders
  - Custom email templates
- **Reporting System**:
  - Weekly checkout reports
  - Monthly analytics
  - Popular books tracking
- **Modern Tech Stack**:
  - FastAPI for high-performance API
  - Celery for background tasks
  - PostgreSQL for reliable data storage
  - Redis for message broker
  - Docker for containerization

## Prerequisites

- Docker and Docker Compose
- Gmail account (for sending notifications)
- Git (for cloning the repository)

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd library-management-api
   ```

2. **Set up environment variables**
   ```bash
   # Copy the example env file
   cp .env.example .env
   
   # Edit .env file with your email credentials
   # For Gmail, you'll need to generate an App Password:
   # 1. Enable 2-Step Verification in your Google Account
   # 2. Go to Security > App Passwords
   # 3. Generate a new app password for "Mail"
   ```

3. **Build and start the containers**
   ```bash
   docker-compose up --build
   ```

4. **Access the services**
   - API Documentation: http://localhost:8000/docs
   - Celery Flower Dashboard: http://localhost:5555

## API Endpoints

### Books
- `GET /books/`: List all books
- `POST /books/`: Add a new book
- `GET /books/{book_id}`: Get book details
- `PUT /books/{book_id}`: Update book information
- `DELETE /books/{book_id}`: Remove a book

### Patrons
- `GET /patrons/`: List all patrons
- `POST /patrons/`: Register a new patron
- `GET /patrons/{patron_id}`: Get patron details
- `PUT /patrons/{patron_id}`: Update patron information
- `DELETE /patrons/{patron_id}`: Remove a patron

### Checkouts
- `POST /checkouts/`: Checkout a book
- `POST /checkouts/{checkout_id}/return`: Return a book
- `GET /checkouts/`: List all checkouts
- `GET /checkouts/overdue`: List overdue checkouts

## Automated Tasks

### Email Notifications
- **Overdue Notices**: Sent daily at 9 AM UTC
- **Due Soon Reminders**: Sent daily at 2 PM UTC
- **Custom Templates**: HTML email templates for better readability

### Reports
- **Weekly Reports**: Generated every Monday at midnight UTC
- **Monthly Analytics**: Generated on the 1st of each month
- Reports include:
  - Total checkouts
  - Active patrons
  - Overdue books
  - Most popular books
  - Average checkout duration

## Development

### Project Structure
```
library-management-api/
├── app/
│   ├── models/        # Database models
│   ├── routes/        # API endpoints
│   ├── tasks/         # Celery tasks
│   ├── templates/     # Email templates
│   └── utils/         # Utility functions
├── docker/           # Docker configuration
├── tests/           # Test cases
├── .env.example     # Environment variables template
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

### Adding New Features

1. **Create new models** in `app/models/`
2. **Add routes** in `app/routes/`
3. **Create migrations** if needed
4. **Add tests** in `tests/`
5. **Update documentation**

### Running Tests
```bash
# Run tests in Docker
docker-compose run web pytest

# Run with coverage
docker-compose run web pytest --cov=app
```

## Monitoring

### Celery Flower
- Access the dashboard at http://localhost:5555
- Monitor task execution
- View worker status
- Check task history

### Health Checks
- API health: http://localhost:8000/health
- Database and Redis health monitored automatically

## Troubleshooting

### Common Issues

1. **Email sending fails**
   - Check SMTP credentials in .env
   - Verify Gmail App Password
   - Check email templates in app/templates/

2. **Database connection issues**
   - Ensure PostgreSQL container is running
   - Check DATABASE_URL in .env
   - Verify database migrations

3. **Celery tasks not running**
   - Check Redis connection
   - Verify Celery worker logs
   - Ensure correct queue configuration

### Logs
```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs web
docker-compose logs celery_worker
docker-compose logs celery_beat
```

## Docker Container Management

### Building and Running Containers

1. **Build the Images**
   ```bash
   # Build all services
   docker-compose build

   # Build specific service
   docker-compose build web
   docker-compose build celery_worker
   ```

2. **Start the Services**
   ```bash
   # Start all services
   docker-compose up

   # Start in detached mode
   docker-compose up -d

   # Start specific services
   docker-compose up web celery_worker
   ```

3. **Stop the Services**
   ```bash
   # Stop all services
   docker-compose down

   # Stop and remove volumes
   docker-compose down -v

   # Stop specific service
   docker-compose stop web
   ```

4. **View Logs**
   ```bash
   # View all logs
   docker-compose logs

   # Follow logs
   docker-compose logs -f

   # View specific service logs
   docker-compose logs web
   docker-compose logs celery_worker
   ```

5. **Container Management**
   ```bash
   # List running containers
   docker-compose ps

   # Restart services
   docker-compose restart

   # Rebuild and restart single service
   docker-compose up -d --build web
   ```

6. **Database Management**
   ```bash
   # Access PostgreSQL
   docker-compose exec db psql -U postgres -d library_db

   # Backup database
   docker-compose exec db pg_dump -U postgres library_db > backup.sql

   # Restore database
   docker-compose exec -T db psql -U postgres library_db < backup.sql
   ```

### Docker Volumes
- `postgres_data`: Persistent PostgreSQL data
- `redis_data`: Persistent Redis data

### Network Configuration
- FastAPI: Port 8000
- PostgreSQL: Port 5433
- Redis: Port 6379
- Flower: Port 5555

## Celery-Beat Task Scheduling

### Task Configuration

Tasks are configured in `app/config/celery_config.py`:

```python
# Example task configuration
beat_schedule = {
    'daily-overdue-notices': {
        'task': 'app.tasks.library_tasks.send_overdue_notices',
        'schedule': crontab(hour=9, minute=0),  # Daily at 9 AM UTC
        'options': {'queue': 'notifications'},
    },
    'weekly-checkout-report': {
        'task': 'app.tasks.library_tasks.generate_weekly_report',
        'schedule': crontab(day_of_week='monday', hour=0, minute=0),
        'options': {'queue': 'reports'},
    }
}
```

### Available Tasks

1. **Email Notifications**
   - `send_overdue_notices`: Daily at 9 AM UTC
   - `send_due_soon_notices`: Daily at 2 PM UTC
   - Queue: notifications

2. **Reports Generation**
   - `generate_weekly_report`: Monday at midnight UTC
   - `generate_monthly_analytics`: 1st of each month
   - Queue: reports

### Scheduling Syntax

Celery-Beat supports various scheduling formats:

1. **Crontab Schedule**
   ```python
   # Format: crontab(minute, hour, day_of_week, day_of_month, month_of_year)
   
   # Every morning at 7:30 AM
   crontab(hour=7, minute=30)
   
   # Every Monday morning at 7:30 AM
   crontab(hour=7, minute=30, day_of_week=1)
   
   # First day of every month at midnight
   crontab(0, 0, day_of_month='1')
   ```

2. **Timedelta Schedule**
   ```python
   # Run every 15 minutes
   'schedule': timedelta(minutes=15)
   
   # Run every hour
   'schedule': timedelta(hours=1)
   ```

### Task Queues

Tasks are distributed across different queues for better resource management:

- `notifications`: Email-related tasks
- `reports`: Report generation tasks

### Monitoring Tasks

1. **Using Flower Dashboard**
   - Access at http://localhost:5555
   - View scheduled tasks
   - Monitor task execution
   - Check worker status

2. **Command Line**
   ```bash
   # View scheduled tasks
   docker-compose exec celery_worker celery -A celery_worker.celery inspect scheduled
   
   # View active tasks
   docker-compose exec celery_worker celery -A celery_worker.celery inspect active
   
   # View registered tasks
   docker-compose exec celery_worker celery -A celery_worker.celery inspect registered
   ```

### Managing Tasks

1. **Manually Running Tasks**
   ```bash
   # Run task from Python shell
   docker-compose exec web python
   >>> from app.tasks.library_tasks import send_overdue_notices
   >>> send_overdue_notices.delay()
   ```

2. **Revoking Tasks**
   ```bash
   # Revoke a task by ID
   docker-compose exec celery_worker celery -A celery_worker.celery revoke <task_id>
   ```

### Troubleshooting Celery-Beat

1. **Task Not Running**
   - Check Celery Beat logs:
     ```bash
     docker-compose logs celery_beat
     ```
   - Verify timezone settings
   - Check task registration

2. **Task Failing**
   - Check worker logs:
     ```bash
     docker-compose logs celery_worker
     ```
   - Verify task dependencies
   - Check database connections

3. **Common Issues**
   - Time zone mismatches
   - Queue configuration
   - Worker connectivity
   - Database access

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
