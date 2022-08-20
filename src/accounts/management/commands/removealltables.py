from django.core.management.base import BaseCommand, CommandError
from django.db import connection


# Import any models, django modules or packages here

class Command(BaseCommand):
    help = "Drop all the tables from the database"

    def handle(self, *args, **options):
        try:
            print("🛑 Do you really want to DROP (delete) ALL THE PUBLIC TABLES from the database? 🛑")
            choice = input("Type the following sentence to confirm: yes, drop all! ")
            if choice.lower() == "yes, drop all!":
                print("You will lose 💣💥 everything in the database !!! ")
                choice = input("If you really want to remove all the public tables, type: remove all tables!  ")
                if choice.lower() == "remove all tables!":
                    cursor = connection.cursor()
                    cursor.execute("SELECT table_name FROM INFORMATION_SCHEMA.tables where table_schema = 'public';")
                    parts = ('DROP TABLE IF EXISTS %s CASCADE;' % table for (table,) in cursor.fetchall())
                    sql = '\n'.join(parts) + '\n'
                    connection.cursor().execute(sql)
                    print("Done! There are no more public tables in the database.")
                else:
                    print("Finaly, you have chosen not to remove the public tables.")
            else:
                print("You have chosen not to remove the public tables.")

        except Exception as e:

            raise CommandError(f"Error: {e}")
