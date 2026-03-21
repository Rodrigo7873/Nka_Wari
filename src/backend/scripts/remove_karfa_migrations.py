import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection
with connection.cursor() as cursor:
    cursor.execute("DELETE FROM django_migrations WHERE app='karfa';")
print("Deleted from django_migrations")
