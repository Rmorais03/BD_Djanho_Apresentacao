import os
import django
from django.db import connection

os.environ['DJANGO_SETTINGS_MODULE']='projeto_apresentacao.settings'
django.setup()

cursor = connection.cursor()

# Get compliance_status enum
cursor.execute("SELECT enumlabel FROM pg_enum JOIN pg_type ON pg_enum.enumtypid = pg_type.oid WHERE typname = 'enum_Companies_compliance_status';")
print("Companies compliance_status:", cursor.fetchall())

# Get Ticket status enum
cursor.execute("SELECT enumlabel FROM pg_enum JOIN pg_type ON pg_enum.enumtypid = pg_type.oid WHERE typname = 'enum_Tickets_status';")
print("Tickets status:", cursor.fetchall())

# Get Ticket priority enum
cursor.execute("SELECT enumlabel FROM pg_enum JOIN pg_type ON pg_enum.enumtypid = pg_type.oid WHERE typname = 'enum_Tickets_priority';")
print("Tickets priority:", cursor.fetchall())

# Get Ticket category enum
cursor.execute("SELECT enumlabel FROM pg_enum JOIN pg_type ON pg_enum.enumtypid = pg_type.oid WHERE typname = 'enum_Tickets_category';")
print("Tickets category:", cursor.fetchall())

# Get Documents status enum
cursor.execute("SELECT enumlabel FROM pg_enum JOIN pg_type ON pg_enum.enumtypid = pg_type.oid WHERE typname = 'enum_Documents_status';")
print("Documents status:", cursor.fetchall())

# Get Documents category enum
cursor.execute("SELECT enumlabel FROM pg_enum JOIN pg_type ON pg_enum.enumtypid = pg_type.oid WHERE typname = 'enum_Documents_document_category';")
print("Documents category:", cursor.fetchall())

# Get Articles status enum
cursor.execute("SELECT enumlabel FROM pg_enum JOIN pg_type ON pg_enum.enumtypid = pg_type.oid WHERE typname = 'enum_Articles_status';")
print("Articles status:", cursor.fetchall())

