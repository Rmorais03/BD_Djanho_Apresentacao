import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projeto_apresentacao.settings')
django.setup()

from app_db.basededados import (
    get_db_version,
    get_total_tables,
    get_entity_counts,
    get_recent_users,
    get_recent_companies,
    get_compliance_data,
    get_top_incidents,
    get_documents_monthly,
    get_roles_distribution,
    get_tickets_status,
    get_avg_resolution_hours,
)

functions_to_test = [
    get_db_version,
    get_total_tables,
    get_entity_counts,
    get_recent_users,
    get_recent_companies,
    get_compliance_data,
    get_top_incidents,
    get_documents_monthly,
    get_roles_distribution,
    get_tickets_status,
    get_avg_resolution_hours,
]

print("A INICIAR TESTE DO FICHEIRO basededados.py...\n")

all_passed = True

for func in functions_to_test:
    try:
        if func in [get_recent_users, get_recent_companies, get_top_incidents]:
            res = func(limit=2)
        else:
            res = func()
        print(f"[OK] - {func.__name__}")
    except Exception as e:
        print(f"[ERRO] - {func.__name__} falhou! Erro: {e}")
        all_passed = False

print("\n")
if all_passed:
    print("VERIFICAÇÃO CONCLUÍDA: O ficheiro basededados.py está 100% operacional!")
else:
    print("VERIFICAÇÃO CONCLUÍDA: Foram encontrados erros.")
