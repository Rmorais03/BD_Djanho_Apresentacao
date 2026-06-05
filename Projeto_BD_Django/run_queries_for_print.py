import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projeto_apresentacao.settings')
django.setup()

from django.db import connection

queries = [
    {
        "title": "1) Clientes por estado de conformidade NIS2",
        "sql": """SELECT compliance_status, COUNT(id) AS total
FROM "Companies"
WHERE deleted_at IS NULL
GROUP BY compliance_status;"""
    },
    {
        "title": "2) Top 5 clientes com mais incidentes registados",
        "sql": """SELECT c.name, COUNT(i.id) AS incident_count
FROM "Companies" c
JOIN "Incidents" i ON c.id = i.company_id
WHERE c.deleted_at IS NULL
  AND i.deleted_at IS NULL
GROUP BY c.id, c.name
ORDER BY incident_count DESC
LIMIT 5;"""
    },
    {
        "title": "3) Total de documentos submetidos por cliente/mês",
        "sql": """SELECT c.name,
       DATE_TRUNC('month', d.created_at) AS month,
       COUNT(d.id) AS doc_count
FROM "Companies" c
JOIN "Documents" d ON c.id = d.company_id
WHERE c.deleted_at IS NULL
  AND d.deleted_at IS NULL
GROUP BY c.name, DATE_TRUNC('month', d.created_at)
ORDER BY month, c.name;"""
    },
    {
        "title": "4) Distribuição de utilizadores por perfil",
        "sql": """SELECT r.name, COUNT(u.id) AS user_count
FROM "Roles" r
JOIN "Users" u ON r.id = u.role_id
WHERE r.deleted_at IS NULL
  AND u.deleted_at IS NULL
GROUP BY r.id, r.name;"""
    },
    {
        "title": "5a) Estado dos tickets (contagem)",
        "sql": """SELECT status, COUNT(id) AS total
FROM "Tickets"
WHERE deleted_at IS NULL
GROUP BY status;"""
    },
    {
        "title": "5b) Tempo médio de resolução dos tickets (em segundos)",
        "sql": """SELECT AVG(EXTRACT(EPOCH FROM (updated_at - created_at))) AS avg_seconds
FROM "Tickets"
WHERE status IN ('Resolved', 'Closed')
  AND deleted_at IS NULL;"""
    }
]

def print_table(cursor):
    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    
    # Calculate column widths
    col_widths = [len(col) for col in columns]
    for row in rows:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(val)))
            
    # Print Header
    header = " | ".join(str(col).ljust(width) for col, width in zip(columns, col_widths))
    print(header)
    print("-" * len(header))
    
    # Print Rows
    for row in rows:
        print(" | ".join(str(val).ljust(width) for val, width in zip(row, col_widths)))

with connection.cursor() as cursor:
    for q in queries:
        print("======================================================================")
        print(f"--- {q['title']} ---")
        print("======================================================================")
        print("QUERY SQL:")
        print(q['sql'])
        print("\nRESULTADO:")
        try:
            cursor.execute(q['sql'])
            print_table(cursor)
        except Exception as e:
            print(f"Erro ao executar a query: {e}")
        print("\n\n")

print("--- FIM DA EXECUÇÃO ---")
