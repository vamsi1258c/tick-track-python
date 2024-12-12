import os
import psycopg2
from passlib.hash import pbkdf2_sha256

# Database connection parameters
DATABASE_URL = os.getenv("DATABASE_URL")  # Make sure to set this environment variable

# User data for the admin
user_data = {
    "username": "admin123@gmail.com",  # Admin username
    "password": "Admin@123",  # Replace with your desired password
    "role": "admin@gmail.com",  # Set user role
    "fullname": "vamsi",  # Full name of the admin
    "designation": "Administrator",  # Admin designation
    "approver": None  # If there's no approver, set to None
}


def insert_admin():
    # Hash the password
    hashed_password = pbkdf2_sha256.hash(user_data["password"])

    # Connect to PostgreSQL database
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # Insert user data into the users table
        cursor.execute("""
            INSERT INTO users (username, password, role, fullname, designation, approver)
            VALUES (%s, %s, %s, %s, %s, %s);
        """, (user_data["username"], hashed_password, user_data["role"],
              user_data["fullname"], user_data["designation"], user_data["approver"]))

        # Commit changes
        conn.commit()
        print("Admin user inserted successfully.")

    except Exception as e:
        print(f"Error inserting admin user: {e}")

    finally:
        if conn:
            cursor.close()
            conn.close()


if __name__ == "__main__":
    insert_admin()
