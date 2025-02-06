from celery.schedules import crontab

# Task Queue Settings
task_serializer = 'json'
accept_content = ['json']
result_serializer = 'json'
timezone = 'UTC'
enable_utc = True

# Task Routing
task_routes = {
    'app.tasks.library_tasks.send_overdue_notices': {'queue': 'notifications'},
    'app.tasks.library_tasks.generate_weekly_report': {'queue': 'reports'},
}

# Beat Schedule Configuration
beat_schedule = {
    # Overdue Book Notifications
    'daily-overdue-notices': {
        'task': 'app.tasks.library_tasks.send_overdue_notices',
        'schedule': crontab(hour=9, minute=0),  # Run daily at 9 AM UTC
        'options': {'queue': 'notifications'},
    },
    
    # Weekly Reports
    'weekly-checkout-report': {
        'task': 'app.tasks.library_tasks.generate_weekly_report',
        'schedule': crontab(day_of_week='monday', hour=0, minute=0),  # Weekly on Monday at midnight UTC
        'options': {'queue': 'reports'},
    },
    
    # Additional Tasks
    'almost-due-reminders': {
        'task': 'app.tasks.library_tasks.send_due_soon_notices',
        'schedule': crontab(hour=14, minute=0),  # Daily at 2 PM UTC
        'options': {'queue': 'notifications'},
    },
    
    'monthly-analytics': {
        'task': 'app.tasks.library_tasks.generate_monthly_analytics',
        'schedule': crontab(0, 0, day_of_month='1'),  # Monthly on the 1st
        'options': {'queue': 'reports'},
    },
}

# Task Execution Settings
task_annotations = {
    'app.tasks.library_tasks.send_overdue_notices': {
        'rate_limit': '10/m',  # Limit to 10 tasks per minute
    },
    'app.tasks.library_tasks.generate_weekly_report': {
        'time_limit': 300,  # 5 minutes timeout
        'soft_time_limit': 240,  # Soft timeout at 4 minutes
    },
}
