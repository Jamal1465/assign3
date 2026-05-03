"""
Script to add the email column to the existing users table.
Run this script once to migrate your database schema.
"""
from sqlalchemy import text
import database

def add_email_column():
    """Add email column to users table if it doesn't exist"""
    with database.engine.connect() as connection:
        # Check if column already exists
        result = connection.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='users' AND column_name='email'
        """))
        
        if result.fetchone():
            print("Email column already exists in users table.")
            return
        
        # Add the email column
        try:
            connection.execute(text("""
                ALTER TABLE users 
                ADD COLUMN email VARCHAR UNIQUE
            """))
            connection.commit()
            print("Successfully added email column to users table.")
            
            # Create index on email column
            connection.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_users_email ON users(email)
            """))
            connection.commit()
            print("Successfully created index on email column.")
            
        except Exception as e:
            print(f"Error adding email column: {e}")
            connection.rollback()

if __name__ == "__main__":
    add_email_column()

