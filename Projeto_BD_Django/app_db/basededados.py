# =============================================================================
# basededados.py — Camada de acesso à Base de Dados (Raw SQL)
# =============================================================================
# Por exigência académica, TODAS as queries utilizam instruções SELECT puras
# executadas via django.db.connection.cursor(). Não se utiliza a ORM do Django.
# =============================================================================

from django.db import connection


# -----------------------------------------------------------------------------
# Helper
# -----------------------------------------------------------------------------
def _dictfetchall(cursor):
    """Converte todas as linhas de um cursor num lista de dicionários."""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def _dictfetchone(cursor):
    """Converte uma única linha de um cursor num dicionário (ou None)."""
    columns = [col[0] for col in cursor.description]
    row = cursor.fetchone()
    return dict(zip(columns, row)) if row else None


# =============================================================================
# DASHBOARD — Informação da Base de Dados
# =============================================================================

def get_db_version():
    """SELECT version() — retorna a versão do PostgreSQL."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT version();")
        raw = cursor.fetchone()[0]
        return raw.split(',')[0]


def get_total_tables():
    """Conta o total de tabelas no schema 'public'."""
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) FROM information_schema.tables "
            "WHERE table_schema = 'public';"
        )
        return cursor.fetchone()[0]


# =============================================================================
# DASHBOARD — KPIs (Contagens por Entidade)
# =============================================================================

def get_entity_counts():
    """
    Retorna as contagens de registos ativos (deleted_at IS NULL)
    para todas as entidades principais, numa única ida à BD.
    """
    queries = {
        'Utilizadores': 'SELECT COUNT(*) FROM "Users"       WHERE deleted_at IS NULL',
        'Empresas':     'SELECT COUNT(*) FROM "Companies"    WHERE deleted_at IS NULL',
        'Incidentes':   'SELECT COUNT(*) FROM "Incidents"    WHERE deleted_at IS NULL',
        'Tickets':      'SELECT COUNT(*) FROM "Tickets"      WHERE deleted_at IS NULL',
        'Artigos':      'SELECT COUNT(*) FROM "Articles"     WHERE deleted_at IS NULL',
        'Ativos':       'SELECT COUNT(*) FROM "Assets"       WHERE deleted_at IS NULL',
        'Documentos':   'SELECT COUNT(*) FROM "Documents"    WHERE deleted_at IS NULL',
        'Relatórios':   'SELECT COUNT(*) FROM "Reports"      WHERE deleted_at IS NULL',
    }
    colors = {
        'Utilizadores': '#3b82f6',
        'Empresas':     '#06b6d4',
        'Incidentes':   '#ef4444',
        'Tickets':      '#f59e0b',
        'Artigos':      '#10b981',
        'Ativos':       '#8b5cf6',
        'Documentos':   '#ec4899',
        'Relatórios':   '#f97316',
    }

    stats = []
    with connection.cursor() as cursor:
        for label, sql in queries.items():
            try:
                cursor.execute(sql)
                count = cursor.fetchone()[0]
            except Exception:
                count = 0
            stats.append({
                'label': label,
                'count': count,
                'color': colors[label],
            })
    return stats


# =============================================================================
# DASHBOARD — Registos Recentes (Raw SQL)
# =============================================================================

def get_recent_users(limit=10):
    """Últimos utilizadores criados (SELECT puro, sem ORM)."""
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT u.name, u.email, u.company_id, u.role_id
            FROM "Users" u
            WHERE u.deleted_at IS NULL
            ORDER BY u.created_at DESC
            LIMIT %s
        ''', [limit])
        return _dictfetchall(cursor)


def get_recent_companies(limit=10):
    """Últimas empresas criadas (SELECT puro, sem ORM)."""
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT c.name, c.nif, c.is_active
            FROM "Companies" c
            WHERE c.deleted_at IS NULL
            ORDER BY c.created_at DESC
            LIMIT %s
        ''', [limit])
        return _dictfetchall(cursor)


# =============================================================================
# DASHBOARD — 5 Relatórios SQL (Requisitos Académicos)
# =============================================================================

def get_compliance_data():
    """
    1) Número de clientes por estado de conformidade NIS2
       (Conforme, Em avaliação, Com pendências).
    """
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT compliance_status, COUNT(id) AS total
            FROM "Companies"
            WHERE deleted_at IS NULL
            GROUP BY compliance_status
        ''')
        return _dictfetchall(cursor)


def get_top_incidents(limit=5):
    """
    2) Top 5 clientes com mais incidentes de segurança registados.
    """
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT c.name, COUNT(i.id) AS incident_count
            FROM "Companies" c
            JOIN "Incidents" i ON c.id = i.company_id
            WHERE c.deleted_at IS NULL
              AND i.deleted_at IS NULL
            GROUP BY c.id, c.name
            ORDER BY incident_count DESC
            LIMIT %s
        ''', [limit])
        return _dictfetchall(cursor)


def get_documents_monthly():
    """
    3) Total de documentos submetidos por cliente e por mês.
    """
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT c.name,
                   DATE_TRUNC('month', d.created_at) AS month,
                   COUNT(d.id) AS doc_count
            FROM "Companies" c
            JOIN "Documents" d ON c.id = d.company_id
            WHERE c.deleted_at IS NULL
              AND d.deleted_at IS NULL
            GROUP BY c.name, DATE_TRUNC('month', d.created_at)
            ORDER BY month, c.name
        ''')
        return _dictfetchall(cursor)


def get_roles_distribution():
    """
    4) Distribuição de utilizadores por perfil
       (Administrador, Colaborador, Cliente).
    """
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT r.name, COUNT(u.id) AS user_count
            FROM "Roles" r
            JOIN "Users" u ON r.id = u.role_id
            WHERE r.deleted_at IS NULL
              AND u.deleted_at IS NULL
            GROUP BY r.id, r.name
        ''')
        return _dictfetchall(cursor)


def get_tickets_status():
    """
    5a) Estado dos pedidos/tickets de suporte — contagem por estado.
    """
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT status, COUNT(id) AS total
            FROM "Tickets"
            WHERE deleted_at IS NULL
            GROUP BY status
        ''')
        return _dictfetchall(cursor)


def get_avg_resolution_hours():
    """
    5b) Tempo médio de resolução dos tickets (em horas).
    """
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT AVG(
                EXTRACT(EPOCH FROM (updated_at - created_at))
            ) AS avg_seconds
            FROM "Tickets"
            WHERE status IN ('Resolved', 'Closed')
              AND deleted_at IS NULL
        ''')
        row = cursor.fetchone()
        avg_seconds = row[0] if row and row[0] else 0
        return round(float(avg_seconds) / 3600.0, 2) if avg_seconds else 0
