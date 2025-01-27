import os
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import create_engine, func, case
from sqlalchemy.orm import sessionmaker
import asyncio

from celery_worker import celery
from app.models.models import Book, Patron, Checkout
from app.utils.email import send_email
from app.database.database import SQLALCHEMY_DATABASE_URL

def get_db_session():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()

@celery.task
def send_overdue_notices():
    print("Starting overdue notices task (these should run each minute)..")
    db = get_db_session()
    current_time = datetime.utcnow()
    print(f"Current time: {current_time}")
    
    try:
        # Get all overdue checkouts
        print("Querying overdue checkouts...")
        overdue_checkouts = (
            db.query(Checkout)
            .filter(
                Checkout.due_date < current_time,
                Checkout.is_returned == False
            )
            .all()
        )
        print(f"Found {len(overdue_checkouts)} overdue checkouts")
        
        # Group checkouts by patron
        patron_checkouts = {}
        for checkout in overdue_checkouts:
            if checkout.patron_id not in patron_checkouts:
                patron_checkouts[checkout.patron_id] = []
            patron_checkouts[checkout.patron_id].append(checkout)
        print(f"Grouped checkouts for {len(patron_checkouts)} patrons")
        
        # Send emails to each patron
        for patron_id, checkouts in patron_checkouts.items():
            print(f"Processing patron {patron_id}...")
            patron = db.query(Patron).filter(Patron.id == patron_id).first()
            if not patron:
                print(f"Patron {patron_id} not found, skipping...")
                continue
                
            overdue_books = []
            for checkout in checkouts:
                book = db.query(Book).filter(Book.id == checkout.book_id).first()
                if book:
                    days_overdue = (current_time - checkout.due_date).days
                    overdue_books.append({
                        "title": book.title,
                        "author": book.author,
                        "due_date": checkout.due_date,
                        "days_overdue": days_overdue
                    })
            
            # Send email asynchronously
            template_data = {
                "patron_name": patron.name,
                "overdue_books": overdue_books
            }
            
            print(f"Sending email to {patron.email}...")
            asyncio.run(send_email(
                to_email=patron.email,
                subject="Library Books Overdue Notice",
                template_name="overdue_notice",
                template_data=template_data
            ))
            print(f"Email sent to {patron.email}")
            
    finally:
        db.close()
        print("Overdue notices task completed")

@celery.task
def generate_weekly_report():
    print("Starting weekly report task...")
    db = get_db_session()
    current_time = datetime.utcnow()
    week_ago = current_time - timedelta(days=7)
    
    try:
        # Get checkout statistics
        print("Querying checkout statistics...")
        checkouts = (
            db.query(Checkout)
            .filter(Checkout.checkout_date >= week_ago)
            .all()
        )
        print(f"Found {len(checkouts)} checkouts")
        
        # Prepare data for the report
        checkout_data = []
        for checkout in checkouts:
            book = db.query(Book).filter(Book.id == checkout.book_id).first()
            patron = db.query(Patron).filter(Patron.id == checkout.patron_id).first()
            
            if book and patron:
                checkout_data.append({
                    "book_title": book.title,
                    "book_author": book.author,
                    "patron_name": patron.name,
                    "checkout_date": checkout.checkout_date,
                    "due_date": checkout.due_date,
                    "is_returned": checkout.is_returned,
                    "return_date": checkout.return_date
                })
        
        # Create DataFrame and generate Excel report
        df = pd.DataFrame(checkout_data)
        
        # Create reports directory if it doesn't exist
        reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        # Save report
        report_path = os.path.join(reports_dir, f"weekly_report_{current_time.strftime('%Y%m%d')}.xlsx")
        with pd.ExcelWriter(report_path, engine='openpyxl') as writer:
            # Checkout Summary
            df.to_excel(writer, sheet_name='Checkouts', index=False)
            
            # Additional statistics
            stats = pd.DataFrame([
                {"Metric": "Total Checkouts", "Value": len(checkouts)},
                {"Metric": "Books Returned", "Value": len([c for c in checkouts if c.is_returned])},
                {"Metric": "Books Outstanding", "Value": len([c for c in checkouts if not c.is_returned])},
                {"Metric": "Overdue Books", "Value": len([c for c in checkouts if not c.is_returned and c.due_date < current_time])}
            ])
            stats.to_excel(writer, sheet_name='Statistics', index=False)
            
        print(f"Weekly report saved to {report_path}")
        return report_path
        
    finally:
        db.close()
        print("Weekly report task completed")

@celery.task
def send_due_soon_notices():
    """Send reminders for books due in the next 2 days."""
    print("Starting due soon notices task...")
    db = get_db_session()
    current_time = datetime.utcnow()
    due_soon = current_time + timedelta(days=2)
    
    try:
        # Get checkouts due in the next 2 days
        print("Querying due soon checkouts...")
        upcoming_due = (
            db.query(Checkout)
            .filter(
                Checkout.due_date.between(current_time, due_soon),
                Checkout.is_returned == False
            )
            .all()
        )
        print(f"Found {len(upcoming_due)} due soon checkouts")
        
        # Group by patron
        patron_checkouts = {}
        for checkout in upcoming_due:
            if checkout.patron_id not in patron_checkouts:
                patron_checkouts[checkout.patron_id] = []
            patron_checkouts[checkout.patron_id].append(checkout)
        
        # Send emails
        for patron_id, checkouts in patron_checkouts.items():
            print(f"Processing patron {patron_id}...")
            patron = db.query(Patron).filter(Patron.id == patron_id).first()
            if not patron:
                print(f"Patron {patron_id} not found, skipping...")
                continue
            
            due_books = []
            for checkout in checkouts:
                book = db.query(Book).filter(Book.id == checkout.book_id).first()
                if book:
                    due_books.append({
                        "title": book.title,
                        "author": book.author,
                        "due_date": checkout.due_date
                    })
            
            # Send reminder email
            template_data = {
                "patron_name": patron.name,
                "due_books": due_books
            }
            
            print(f"Sending email to {patron.email}...")
            asyncio.run(send_email(
                to_email=patron.email,
                subject="Books Due Soon Reminder",
                template_name="due_soon_notice",
                template_data=template_data
            ))
            print(f"Email sent to {patron.email}")
    
    finally:
        db.close()
        print("Due soon notices task completed")

@celery.task
def generate_monthly_analytics():
    """Generate monthly analytics report with detailed statistics."""
    print("Starting monthly analytics task...")
    db = get_db_session()
    current_time = datetime.utcnow()
    month_ago = current_time - timedelta(days=30)
    
    try:
        # Gather monthly statistics
        print("Querying monthly statistics...")
        monthly_data = {
            "total_checkouts": db.query(Checkout).filter(
                Checkout.checkout_date >= month_ago
            ).count(),
            
            "active_patrons": db.query(Checkout).filter(
                Checkout.checkout_date >= month_ago
            ).distinct(Checkout.patron_id).count(),
            
            "overdue_books": db.query(Checkout).filter(
                Checkout.due_date < current_time,
                Checkout.is_returned == False
            ).count(),
            
            "most_popular_books": db.query(
                Book.title,
                Book.author,
                func.count(Checkout.id).label('checkout_count')
            ).join(Checkout).filter(
                Checkout.checkout_date >= month_ago
            ).group_by(Book.id).order_by(
                func.count(Checkout.id).desc()
            ).limit(10).all(),
            
            "average_checkout_duration": db.query(
                func.avg(
                    case(
                        (Checkout.return_date != None,
                         Checkout.return_date - Checkout.checkout_date),
                        else_=current_time - Checkout.checkout_date
                    )
                )
            ).filter(Checkout.checkout_date >= month_ago).scalar()
        }
        print("Monthly statistics gathered")
        
        # Create reports directory if it doesn't exist
        reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        # Generate Excel report
        report_path = os.path.join(reports_dir, f"monthly_analytics_{current_time.strftime('%Y%m')}.xlsx")
        
        with pd.ExcelWriter(report_path, engine='openpyxl') as writer:
            # Summary Statistics
            summary_df = pd.DataFrame([{
                "Metric": "Total Checkouts",
                "Value": monthly_data["total_checkouts"]
            }, {
                "Metric": "Active Patrons",
                "Value": monthly_data["active_patrons"]
            }, {
                "Metric": "Overdue Books",
                "Value": monthly_data["overdue_books"]
            }, {
                "Metric": "Average Checkout Duration (days)",
                "Value": monthly_data["average_checkout_duration"].days if monthly_data["average_checkout_duration"] else 0
            }])
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Popular Books
            popular_books_df = pd.DataFrame(monthly_data["most_popular_books"],
                                          columns=['Title', 'Author', 'Checkouts'])
            popular_books_df.to_excel(writer, sheet_name='Popular Books', index=False)
        
        print(f"Monthly analytics report saved to {report_path}")
        return report_path
        
    finally:
        db.close()
        print("Monthly analytics task completed")
