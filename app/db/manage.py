import click
from .init_db import init_db, drop_db

@click.group()
def cli():
    """Database management commands."""
    pass

@cli.command()
def create_tables():
    """Create all database tables."""
    init_db()
    click.echo("Database tables created successfully!")

@cli.command()
def drop_tables():
    """Drop all database tables."""
    if click.confirm("Are you sure you want to drop all tables? This cannot be undone!", abort=True):
        drop_db()
        click.echo("Database tables dropped successfully!")

if __name__ == "__main__":
    cli() 