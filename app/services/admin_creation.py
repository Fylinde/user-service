import click
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.usermanager import UserManager

@click.command()
@click.option('--email', prompt='Admin email', help='The email for the admin user')
@click.option('--password', prompt='Admin password', help='The password for the admin user', hide_input=True)
@click.option('--full_name', prompt='Admin full name', help='The full name for the admin user')
@click.option('--phone_number', prompt='Admin phone number', help='The phone number for the admin user')
def create_admin(email, password, full_name, phone_number):
    """Create an admin user via CLI"""
    db: Session = next(get_db())
    UserManager.create_admin(db, email=email, phone_number=phone_number, full_name=full_name, password=password)
    click.echo(f"Admin user {full_name} created successfully.")


if __name__ == '__main__':
    create_admin()
