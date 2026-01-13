import os
import django
from django.db import connection
from django.core.management import execute_from_command_line

# 1. Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangofirst.settings')
django.setup()

def wipe_and_reset():
    print("!! WARNING: This will delete ALL data in your local Postgres database !!")

    # 2. Drop all tables in the 'public' schema
    with connection.cursor() as cursor:
        print("Dropping all existing tables...")
        # This SQL command wipes the schema and recreates it (fastest reset for Postgres)
        try:
            cursor.execute("DROP SCHEMA public CASCADE;")
            cursor.execute("CREATE SCHEMA public;")
            print("Database schema wiped successfully.")
        except Exception as e:
            print(f"Error wiping schema: {e}")
            return

    # 3. Clear Migration Files (Double check to ensure clean slate)
    apps = ['inventory', 'transactions', 'partners']
    base_dir = os.path.dirname(os.path.abspath(__file__))

    print("Cleaning migration files...")
    for app in apps:
        mig_path = os.path.join(base_dir, app, 'migrations')
        if os.path.exists(mig_path):
            for filename in os.listdir(mig_path):
                if filename != "__init__.py" and filename.endswith(".py"):
                    os.remove(os.path.join(mig_path, filename))

    # 4. Rebuild Everything
    print("\n--- Making Migrations ---")
    execute_from_command_line(['manage.py', 'makemigrations'])

    print("\n--- Migrating Database ---")
    execute_from_command_line(['manage.py', 'migrate'])

    print("\n--- Seeding Data ---")
    execute_from_command_line(['manage.py', 'seed_data'])

    print("\nSUCCESS! Your Postgres database is fixed and seeded.")

if __name__ == '__main__':
    wipe_and_reset()
