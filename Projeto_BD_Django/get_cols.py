import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projeto_apresentacao.settings')
django.setup()
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute('SELECT * FROM "Companies" LIMIT 0')
    print([desc[0] for desc in cursor.description])
