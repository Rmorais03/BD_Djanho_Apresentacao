from django.shortcuts import render, redirect, get_object_or_404
from django.db import connection
from django.utils import timezone
from django.contrib import messages
from django.apps import apps
from django.core.files.storage import FileSystemStorage
from .models import (
    Users, Companies, Incidents, Tickets, Articles, Assets,
    Documents, Reports, Roles, Permissions, Categories,
    Chats, Messages, Pages, Auditlogs
)
from .forms import CompanyForm, TicketForm, UserForm, DocumentForm, ArticleForm
from .basededados import (
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


# ==============================================================================
# HELPERS
# ==============================================================================
def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

# ==============================================================================
# DASHBOARD
# ==============================================================================
def dashboard(request):
    """Dashboard principal — visão geral da base de dados NeonDB."""
    db_connected = False
    db_version = 'Desconhecida'
    total_tables = 0

    try:
        db_version = get_db_version()
        db_connected = True
    except Exception as e:
        db_version = str(e)

    try:
        total_tables = get_total_tables()
    except Exception:
        pass

    stats = get_entity_counts()
    recent_users = get_recent_users(limit=10)
    recent_companies = get_recent_companies(limit=10)
    compliance_data = get_compliance_data()
    top_incidents_data = get_top_incidents(limit=5)
    documents_monthly_data = get_documents_monthly()
    roles_data = get_roles_distribution()
    tickets_status_data = get_tickets_status()
    avg_resolution_hours = get_avg_resolution_hours()

    context = {
        'active_nav': 'dashboard',
        'stats': stats,
        'recent_users': recent_users,
        'recent_companies': recent_companies,
        'db_connected': db_connected,
        'db_version': db_version,
        'total_tables': total_tables,
        'now': timezone.now(),
        'compliance_data': compliance_data,
        'top_incidents_data': top_incidents_data,
        'documents_monthly_data': documents_monthly_data,
        'roles_data': roles_data,
        'tickets_status_data': tickets_status_data,
        'avg_resolution_hours': avg_resolution_hours,
    }
    return render(request, 'app_db/dashboard.html', context)


# ==============================================================================
# MODELO LÓGICO
# ==============================================================================
def get_model_info():
    """Recolhe metadata de todos os models para gerar os diagramas."""
    models_info = []
    
    app = apps.get_app_config('app_db')
    for model in app.get_models():
        fields = []
        for f in model._meta.get_fields():
            if f.is_relation and (f.many_to_many or f.one_to_many):
                continue
                
            field_info = {
                'name': f.name,
                'type': f.get_internal_type(),
                'is_pk': f.primary_key,
                'is_fk': f.is_relation and f.many_to_one,
            }
            if field_info['is_fk']:
                field_info['related_model'] = f.related_model._meta.db_table
                
            fields.append(field_info)
            
        models_info.append({
            'name': model._meta.object_name,
            'db_table': model._meta.db_table,
            'fields': fields
        })
    return models_info

def modelo_cards(request):
    """Página com os cards interativos do modelo."""
    context = {
        'active_nav': 'modelo_cards',
        'models': get_model_info()
    }
    return render(request, 'app_db/modelo_cards.html', context)

def _build_mermaid_er(models_info):
    """Build a clean Mermaid erDiagram string from model metadata."""
    lines = ['erDiagram']

    # Sanitize type names: remove spaces, keep only alphanumeric + underscore
    def safe_type(t):
        return t.replace(' ', '_')

    # Entities
    for model in models_info:
        table = model['db_table'].replace(' ', '_')
        lines.append(f'    {table} {{')
        for field in model['fields']:
            ftype = safe_type(field['type'])
            fname = field['name'].replace(' ', '_')
            
            # Prevent Mermaid ER parser crash (confuses 'pk' field name with 'PK' keyword)
            if fname.lower() == 'pk':
                fname = 'id'
                
            marker = ''
            if field.get('is_pk'):
                marker = ' PK'
            elif field.get('is_fk'):
                marker = ' FK'
            lines.append(f'        {ftype} {fname}{marker}')
        lines.append('    }')

    # Relationships
    for model in models_info:
        table = model['db_table'].replace(' ', '_')
        for field in model['fields']:
            if field.get('is_fk') and field.get('related_model'):
                related = field['related_model'].replace(' ', '_')
                lines.append(f'    {related} ||--o{{ {table} : "{field["name"]}"')

    return '\n'.join(lines)


def modelo_mermaid(request):
    """Página com os diagramas ER gerados em Mermaid."""
    
    mermaid_fisico = """erDiagram
    %% RELAÇÕES
    Roles ||--o{ Users : "fk_users_roles"
    Roles ||--o{ Role_Permissions : "fk_rp_roles"
    Permissions ||--o{ Role_Permissions : "fk_rp_permissions"
    Companies |o--o{ Users : "fk_users_companies"
    Users ||--o{ Companies : "fk_companies_client_owner"
    Users ||--o{ Companies : "fk_companies_emergency_admin"
    Companies ||--o{ CompanyAdmins : "fk_ca_companies"
    Users ||--o{ CompanyAdmins : "fk_ca_users"
    Users ||--o{ Pages : "fk_pages_users"
    Users ||--o{ Articles : "fk_articles_users"
    Articles ||--o{ Article_Categories : "fk_ac_articles"
    Categories ||--o{ Article_Categories : "fk_ac_categories"
    Companies ||--o{ Assets : "fk_assets_companies"
    Users ||--o{ Assets : "fk_assets_users"
    Companies ||--o{ Documents : "fk_documents_companies"
    Users ||--o{ Documents : "fk_documents_users"
    Companies ||--o{ Reports : "fk_reports_companies"
    Users ||--o{ Reports : "fk_reports_users"
    Companies ||--o{ Incidents : "fk_incidents_companies"
    Users ||--o{ Incidents : "fk_incidents_users"
    Assets |o--o{ Incidents : "fk_incidents_assets"
    Companies ||--o{ Tickets : "fk_tickets_companies"
    Users ||--o{ Tickets : "fk_tickets_opened_by"
    Users ||--o{ Tickets : "fk_tickets_assigned_to"
    Companies ||--o{ Chats : "fk_chats_companies"
    Chats ||--o{ Chat_Users : "fk_cu_chats"
    Users ||--o{ Chat_Users : "fk_cu_users"
    Tickets ||--o{ Messages : "fk_messages_tickets"
    Chats ||--o{ Messages : "fk_messages_chats"
    Users ||--o{ Messages : "fk_messages_sender"
    Users |o--o{ AuditLogs : "fk_auditlogs_users"

    %% ENTIDADES E ATRIBUTOS
    Roles {
        INTEGER id PK "nextval"
        VARCHAR(255) name "NOT NULL"
        TIMESTAMP_TZ created_at "NOT NULL"
        TIMESTAMP_TZ updated_at "NOT NULL"
        TIMESTAMP_TZ deleted_at "Nullable"
    }
    Permissions {
        INTEGER id PK "nextval"
        VARCHAR(255) name "NOT NULL"
        VARCHAR(255) description "Nullable"
    }
    Role_Permissions {
        INTEGER role_id PK, FK "NOT NULL"
        INTEGER permission_id PK, FK "NOT NULL"
    }
    Users {
        INTEGER id PK "nextval"
        INTEGER role_id FK "Nullable"
        INTEGER company_id FK "Nullable"
        VARCHAR(255) name "NOT NULL"
        VARCHAR(255) email "NOT NULL"
        VARCHAR(255) password "Nullable"
        VARCHAR(255) phone "Nullable"
        BOOLEAN is_2fa_enabled "Default: false"
        BOOLEAN is_active "Default: true"
        TIMESTAMP_TZ created_at "NOT NULL"
        TIMESTAMP_TZ updated_at "NOT NULL"
        TIMESTAMP_TZ deleted_at "Nullable"
        VARCHAR(255) activation_token "Nullable"
        TIMESTAMP_TZ token_expires_at "Nullable"
        TEXT avatar "Nullable"
    }
    Companies {
        INTEGER id PK "nextval"
        VARCHAR(255) name "NOT NULL"
        INTEGER nif "NOT NULL"
        VARCHAR(255) phone "Nullable"
        VARCHAR(255) address "Nullable"
        ENUM compliance_status "Default: 'Awaiting'"
        BOOLEAN is_active "Default: true"
        TIMESTAMP_TZ created_at "NOT NULL"
        TIMESTAMP_TZ updated_at "NOT NULL"
        TIMESTAMP_TZ deleted_at "Nullable"
        INTEGER client_owner_id FK "Nullable"
        INTEGER emergency_admin_id FK "Nullable"
    }
    CompanyAdmins {
        TIMESTAMP_TZ created_at "NOT NULL"
        TIMESTAMP_TZ updated_at "NOT NULL"
        INTEGER company_id PK, FK "NOT NULL"
        INTEGER user_id PK, FK "NOT NULL"
    }
    Pages {
        INTEGER id PK "nextval"
        INTEGER author_id FK "NOT NULL"
        VARCHAR(255) title "NOT NULL"
        VARCHAR(255) slug "NOT NULL"
        JSONB content_body "Nullable"
        VARCHAR(255) featured_image "Nullable"
        ENUM status "Default: 'Draft'"
        TIMESTAMP_TZ created_at "NOT NULL"
        TIMESTAMP_TZ updated_at "NOT NULL"
        TIMESTAMP_TZ deleted_at "Nullable"
    }
    Articles {
        INTEGER id PK "nextval"
        INTEGER author_id FK "NOT NULL"
        VARCHAR(255) title "NOT NULL"
        VARCHAR(255) slug "NOT NULL"
        TEXT summary "Nullable"
        TEXT content_body "Nullable"
        VARCHAR(255) cover_image "Nullable"
        DATE published_date "Nullable"
        ENUM status "Default: 'Draft'"
        TIMESTAMP_TZ created_at "NOT NULL"
        TIMESTAMP_TZ updated_at "NOT NULL"
        TIMESTAMP_TZ deleted_at "Nullable"
    }
    Categories {
        INTEGER id PK "nextval"
        VARCHAR(255) name "NOT NULL"
        VARCHAR(255) slug "NOT NULL"
        TIMESTAMP_TZ created_at "NOT NULL"
        TIMESTAMP_TZ updated_at "NOT NULL"
        TIMESTAMP_TZ deleted_at "Nullable"
    }
    Article_Categories {
        INTEGER article_id PK, FK "NOT NULL"
        INTEGER category_id PK, FK "NOT NULL"
    }
    Assets {
        INTEGER id PK "nextval"
        INTEGER company_id FK "NOT NULL"
        INTEGER created_by_user_id FK "NOT NULL"
        VARCHAR(255) asset_code "Nullable"
        VARCHAR(255) name "NOT NULL"
        TEXT description "Nullable"
        ENUM category "NOT NULL"
        VARCHAR(255) owner "Nullable"
        VARCHAR(255) location "Nullable"
        ENUM confidentiality "Default: 'Medium'"
        ENUM integrity "Default: 'Medium'"
        ENUM availability "Default: 'Medium'"
        ENUM status "Default: 'Active'"
        TIMESTAMP_TZ created_at "NOT NULL"
        TIMESTAMP_TZ updated_at "NOT NULL"
        TIMESTAMP_TZ deleted_at "Nullable"
    }
    Documents {
        INTEGER id PK "nextval"
        INTEGER company_id FK "NOT NULL"
        INTEGER uploaded_by_user_id FK "NOT NULL"
        ENUM document_category "NOT NULL"
        VARCHAR(255) title "NOT NULL"
        VARCHAR(255) file_path "NOT NULL"
        BOOLEAN is_action_required "Default: false"
        ENUM status "Default: 'Informational'"
        TIMESTAMP_TZ created_at "NOT NULL"
        TIMESTAMP_TZ updated_at "NOT NULL"
        TIMESTAMP_TZ deleted_at "Nullable"
    }
    Reports {
        INTEGER id PK "nextval"
        INTEGER company_id FK "NOT NULL"
        INTEGER created_by_user_id FK "NOT NULL"
        ENUM report_type "NOT NULL"
        VARCHAR(255) title "NOT NULL"
        INTEGER risk_score "Nullable"
        VARCHAR(255) file_path "NOT NULL"
        ENUM status "Default: 'Draft'"
        TIMESTAMP_TZ created_at "NOT NULL"
        TIMESTAMP_TZ updated_at "NOT NULL"
        TIMESTAMP_TZ deleted_at "Nullable"
    }
    Incidents {
        INTEGER id PK "nextval"
        INTEGER company_id FK "NOT NULL"
        INTEGER asset_id FK "Nullable"
        INTEGER reported_by_user_id FK "NOT NULL"
        VARCHAR(255) title "NOT NULL"
        ENUM severity "Default: 'Medium'"
        ENUM status "Default: 'Open'"
        JSONB cncs_form_data "NOT NULL"
        TIMESTAMP_TZ created_at "NOT NULL"
        TIMESTAMP_TZ updated_at "NOT NULL"
        TIMESTAMP_TZ deleted_at "Nullable"
    }
    Tickets {
        INTEGER id PK "nextval"
        INTEGER company_id FK "NOT NULL"
        INTEGER opened_by_user_id FK "NOT NULL"
        INTEGER assigned_to_user_id FK "Nullable"
        ENUM category "NOT NULL"
        ENUM priority "Default: 'Medium'"
        VARCHAR(255) subject "NOT NULL"
        TEXT description "NOT NULL"
        ENUM status "Default: 'Open'"
        TIMESTAMP_TZ created_at "NOT NULL"
        TIMESTAMP_TZ updated_at "NOT NULL"
        TIMESTAMP_TZ deleted_at "Nullable"
    }
    Chats {
        INTEGER id PK "nextval"
        INTEGER company_id FK "NOT NULL"
        TIMESTAMP_TZ created_at "NOT NULL"
        TIMESTAMP_TZ updated_at "NOT NULL"
        TIMESTAMP_TZ deleted_at "Nullable"
    }
    Chat_Users {
        INTEGER chat_id PK, FK "NOT NULL"
        INTEGER user_id PK, FK "NOT NULL"
    }
    Messages {
        INTEGER id PK "nextval"
        INTEGER sender_id FK "NOT NULL"
        INTEGER ticket_id FK "Nullable"
        INTEGER chat_id FK "Nullable"
        TEXT content "NOT NULL"
        BOOLEAN is_read "Default: false"
        TIMESTAMP_TZ created_at "NOT NULL"
        TIMESTAMP_TZ updated_at "NOT NULL"
        TIMESTAMP_TZ deleted_at "Nullable"
        VARCHAR(255) attachment "Nullable"
    }
    AuditLogs {
        INTEGER id PK "nextval"
        INTEGER user_id FK "Nullable"
        VARCHAR(255) action "NOT NULL"
        VARCHAR(255) entity_type "Nullable"
        INTEGER entity_id "Nullable"
        VARCHAR(255) ip_address "Nullable"
        TIMESTAMP_TZ created_at "NOT NULL"
    }"""
    
    mermaid_logico = """erDiagram
    %% RELAÇÕES
    Roles ||--o{ Users : "possui"
    Roles ||--o{ Role_Permissions : "associa"
    Permissions ||--o{ Role_Permissions : "pertence"
    Companies |o--o{ Users : "contem_clientes"
    Users ||--o{ Companies : "e_dono_de"
    Users ||--o{ Companies : "e_admin_emergencia"
    Companies ||--o{ CompanyAdmins : "associa"
    Users ||--o{ CompanyAdmins : "associa"
    Users ||--o{ Pages : "escreve"
    Users ||--o{ Articles : "escreve"
    Articles ||--o{ Article_Categories : "possui"
    Categories ||--o{ Article_Categories : "pertence_a"
    Companies ||--o{ Assets : "detem"
    Users ||--o{ Assets : "regista"
    Companies ||--o{ Documents : "guarda"
    Users ||--o{ Documents : "carrega"
    Companies ||--o{ Reports : "recebe"
    Users ||--o{ Reports : "gera"
    Companies ||--o{ Incidents : "regista"
    Users ||--o{ Incidents : "reporta"
    Assets |o--o{ Incidents : "afeta"
    Companies ||--o{ Tickets : "abre"
    Users ||--o{ Tickets : "solicita"
    Users ||--o{ Tickets : "atribuido_a"
    Companies ||--o{ Chats : "aloja"
    Chats ||--o{ Chat_Users : "inclui"
    Users ||--o{ Chat_Users : "participa"
    Tickets ||--o{ Messages : "contem"
    Chats ||--o{ Messages : "agrega"
    Users ||--o{ Messages : "envia"
    Users |o--o{ AuditLogs : "despoleta"

    %% ENTIDADES E ATRIBUTOS
    Roles {
        int id PK
        string name
        datetime created_at
        datetime updated_at
        datetime deleted_at
    }
    Permissions {
        int id PK
        string name
        string description
    }
    Role_Permissions {
        int role_id PK, FK
        int permission_id PK, FK
    }
    Users {
        int id PK
        int role_id FK
        int company_id FK
        string name
        string email
        string password
        string phone
        boolean is_2fa_enabled
        boolean is_active
        datetime created_at
        datetime updated_at
        datetime deleted_at
        string activation_token
        datetime token_expires_at
        text avatar
    }
    Companies {
        int id PK
        string name
        int nif
        string phone
        string address
        enum compliance_status
        boolean is_active
        datetime created_at
        datetime updated_at
        datetime deleted_at
        int client_owner_id FK
        int emergency_admin_id FK
    }
    CompanyAdmins {
        int company_id PK, FK
        int user_id PK, FK
        datetime created_at
        datetime updated_at
    }
    Pages {
        int id PK
        int author_id FK
        string title
        string slug
        jsonb content_body
        string featured_image
        enum status
        datetime created_at
        datetime updated_at
        datetime deleted_at
    }
    Articles {
        int id PK
        int author_id FK
        string title
        string slug
        text summary
        text content_body
        string cover_image
        date published_date
        enum status
        datetime created_at
        datetime updated_at
        datetime deleted_at
    }
    Categories {
        int id PK
        string name
        string slug
        datetime created_at
        datetime updated_at
        datetime deleted_at
    }
    Article_Categories {
        int article_id PK, FK
        int category_id PK, FK
    }
    Assets {
        int id PK
        int company_id FK
        int created_by_user_id FK
        string asset_code
        string name
        text description
        enum category
        string owner
        string location
        enum confidentiality
        enum integrity
        enum availability
        enum status
        datetime created_at
        datetime updated_at
        datetime deleted_at
    }
    Documents {
        int id PK
        int company_id FK
        int uploaded_by_user_id FK
        enum document_category
        string title
        string file_path
        boolean is_action_required
        enum status
        datetime created_at
        datetime updated_at
        datetime deleted_at
    }
    Reports {
        int id PK
        int company_id FK
        int created_by_user_id FK
        enum report_type
        string title
        int risk_score
        string file_path
        enum status
        datetime created_at
        datetime updated_at
        datetime deleted_at
    }
    Incidents {
        int id PK
        int company_id FK
        int asset_id FK
        int reported_by_user_id FK
        string title
        enum severity
        enum status
        jsonb cncs_form_data
        datetime created_at
        datetime updated_at
        datetime deleted_at
    }
    Tickets {
        int id PK
        int company_id FK
        int opened_by_user_id FK
        int assigned_to_user_id FK
        enum category
        enum priority
        string subject
        text description
        enum status
        datetime created_at
        datetime updated_at
        datetime deleted_at
    }
    Chats {
        int id PK
        int company_id FK
        datetime created_at
        datetime updated_at
        datetime deleted_at
    }
    Chat_Users {
        int chat_id PK, FK
        int user_id PK, FK
    }
    Messages {
        int id PK
        int sender_id FK
        int ticket_id FK
        int chat_id FK
        text content
        boolean is_read
        datetime created_at
        datetime updated_at
        datetime deleted_at
        string attachment
    }
    AuditLogs {
        int id PK
        int user_id FK
        string action
        string entity_type
        int entity_id
        string ip_address
        datetime created_at
    }
"""

    mermaid_concetual = """erDiagram
    %% RELAÇÕES
    ROLES ||--o{ USERS : "define_permissoes_de"
    ROLES ||--o{ ROLE_PERMISSIONS : "possui"
    PERMISSIONS ||--o{ ROLE_PERMISSIONS : "atribuida_a"
    
    COMPANIES ||--o{ USERS : "possui_clientes"
    USERS ||--o{ COMPANIES : "e_dono_de"
    USERS ||--o{ COMPANIES : "e_admin_emergencia"
    
    COMPANIES ||--o{ COMPANY_ADMINS : "gerida_por"
    USERS ||--o{ COMPANY_ADMINS : "administra"
    
    USERS ||--o{ ARTICLES : "escreve"
    ARTICLES ||--o{ ARTICLE_CATEGORIES : "possui"
    CATEGORIES ||--o{ ARTICLE_CATEGORIES : "pertence_a"
    USERS ||--o{ PAGES : "escreve_pagina"
    
    COMPANIES ||--o{ ASSETS : "detem"
    USERS ||--o{ ASSETS : "regista_ativo"
    
    COMPANIES ||--o{ DOCUMENTS : "guarda"
    USERS ||--o{ DOCUMENTS : "carrega"
    
    COMPANIES ||--o{ REPORTS : "recebe"
    USERS ||--o{ REPORTS : "gera"
    
    COMPANIES ||--o{ INCIDENTS : "sofre"
    USERS ||--o{ INCIDENTS : "reporta"
    ASSETS |o--o{ INCIDENTS : "envolvido_em"
    
    COMPANIES ||--o{ TICKETS : "abre"
    USERS ||--o{ TICKETS : "solicita"
    USERS ||--o{ TICKETS : "atribuido_a"
    
    COMPANIES ||--o{ CHATS : "aloja"
    CHATS ||--o{ CHAT_USERS : "inclui"
    USERS ||--o{ CHAT_USERS : "participa"
    
    TICKETS ||--o{ MESSAGES : "contem"
    CHATS ||--o{ MESSAGES : "agrega"
    USERS ||--o{ MESSAGES : "envia"
    
    USERS |o--o{ AUDIT_LOGS : "despoleta"

    %% ENTIDADES E ATRIBUTOS
    ROLES {
        _ name
        _ created_at
        _ updated_at
        _ deleted_at
    }
    PERMISSIONS {
        _ name
        _ description
    }
    ROLE_PERMISSIONS {
        _ relacao
    }
    USERS {
        _ name
        _ email
        _ password
        _ avatar
        _ activation_token
        _ token_expires_at
        _ phone
        _ is_2fa_enabled
        _ is_active
        _ created_at
        _ updated_at
        _ deleted_at
    }
    COMPANIES {
        _ name
        _ nif
        _ phone
        _ address
        _ compliance_status
        _ is_active
        _ created_at
        _ updated_at
        _ deleted_at
    }
    COMPANY_ADMINS {
        _ created_at
        _ updated_at
    }
    PAGES {
        _ title
        _ slug
        _ content_body
        _ featured_image
        _ status
        _ created_at
        _ updated_at
        _ deleted_at
    }
    ARTICLES {
        _ title
        _ slug
        _ summary
        _ content_body
        _ cover_image
        _ published_date
        _ status
        _ created_at
        _ updated_at
        _ deleted_at
    }
    CATEGORIES {
        _ name
        _ slug
        _ created_at
        _ updated_at
        _ deleted_at
    }
    ARTICLE_CATEGORIES {
        _ relacao
    }
    ASSETS {
        _ asset_code
        _ name
        _ description
        _ category
        _ owner
        _ location
        _ confidentiality
        _ integrity
        _ availability
        _ status
        _ created_at
        _ updated_at
        _ deleted_at
    }
    DOCUMENTS {
        _ document_category
        _ title
        _ file_path
        _ is_action_required
        _ status
        _ created_at
        _ updated_at
        _ deleted_at
    }
    REPORTS {
        _ report_type
        _ title
        _ risk_score
        _ file_path
        _ status
        _ created_at
        _ updated_at
        _ deleted_at
    }
    INCIDENTS {
        _ title
        _ severity
        _ status
        _ cncs_form_data
        _ created_at
        _ updated_at
        _ deleted_at
    }
    TICKETS {
        _ category
        _ priority
        _ subject
        _ description
        _ status
        _ created_at
        _ updated_at
        _ deleted_at
    }
    CHATS {
        _ created_at
        _ updated_at
        _ deleted_at
    }
    CHAT_USERS {
        _ relacao
    }
    MESSAGES {
        _ content
        _ is_read
        _ attachment
        _ created_at
        _ updated_at
        _ deleted_at
    }
    AUDIT_LOGS {
        _ action
        _ entity_type
        _ entity_id
        _ ip_address
        _ created_at
    }
"""

    context = {
        'active_nav': 'modelo_mermaid',
        'mermaid_fisico': mermaid_fisico,
        'mermaid_logico': mermaid_logico,
        'mermaid_concetual': mermaid_concetual,
    }
    return render(request, 'app_db/modelo_mermaid.html', context)


# ==============================================================================
# CRUD GENÉRICO HELPER
# ==============================================================================
def soft_delete(obj):
    if hasattr(obj, 'deleted_at'):
        obj.deleted_at = timezone.now()
        obj.save()
    else:
        obj.delete() # Fallback to hard delete if no deleted_at


# ==============================================================================
# CRUD EMPRESAS
# ==============================================================================
def empresas_list(request):
    items = Companies.objects.filter(deleted_at__isnull=True).order_by('-created_at')
    context = {
        'active_nav': 'empresas',
        'title': 'Empresas',
        'items': items,
        'create_url': 'app_db:empresas_create',
        'update_url': 'app_db:empresas_update',
        'delete_url': 'app_db:empresas_delete',
        'columns': ['id', 'name', 'nif', 'phone', 'compliance_status', 'is_active'],
        'fields': ['id', 'name', 'nif', 'phone', 'compliance_status', 'is_active'],
    }
    return render(request, 'app_db/crud_list.html', context)

def empresas_create(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            company = form.save(commit=False)
            company.created_at = timezone.now()
            company.updated_at = timezone.now()
            company.save()
            messages.success(request, 'Empresa criada com sucesso.')
            return redirect('app_db:empresas_list')
    else:
        form = CompanyForm()
        
    context = {
        'active_nav': 'empresas',
        'title': 'Criar Empresa',
        'form': form,
        'cancel_url': 'app_db:empresas_list',
    }
    return render(request, 'app_db/crud_form.html', context)

def empresas_update(request, pk):
    company = get_object_or_404(Companies, pk=pk, deleted_at__isnull=True)
    if request.method == 'POST':
        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            company = form.save(commit=False)
            company.updated_at = timezone.now()
            company.save()
            messages.success(request, 'Empresa atualizada com sucesso.')
            return redirect('app_db:empresas_list')
    else:
        form = CompanyForm(instance=company)
        
    context = {
        'active_nav': 'empresas',
        'title': f'Editar Empresa: {company.name}',
        'form': form,
        'cancel_url': 'app_db:empresas_list',
    }
    return render(request, 'app_db/crud_form.html', context)

def empresas_delete(request, pk):
    company = get_object_or_404(Companies, pk=pk, deleted_at__isnull=True)
    if request.method == 'POST':
        soft_delete(company)
        messages.success(request, 'Empresa eliminada com sucesso.')
        return redirect('app_db:empresas_list')
        
    context = {
        'active_nav': 'empresas',
        'title': 'Eliminar Empresa',
        'object_name': company.name,
        'cancel_url': 'app_db:empresas_list',
    }
    return render(request, 'app_db/crud_confirm_delete.html', context)


# ==============================================================================
# CRUD TICKETS
# ==============================================================================
def tickets_list(request):
    items = Tickets.objects.select_related('company', 'opened_by_user').filter(deleted_at__isnull=True).order_by('-created_at')
    context = {
        'active_nav': 'tickets',
        'title': 'Tickets',
        'items': items,
        'create_url': 'app_db:tickets_create',
        'update_url': 'app_db:tickets_update',
        'delete_url': 'app_db:tickets_delete',
        'columns': ['id', 'subject', 'company_id', 'opened_by_user_id', 'category', 'priority', 'status'],
        'fields': ['id', 'subject', 'company_id', 'opened_by_user_id', 'category', 'priority', 'status'],
    }
    return render(request, 'app_db/crud_list.html', context)

def tickets_create(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_at = timezone.now()
            ticket.updated_at = timezone.now()
            ticket.save()
            messages.success(request, 'Ticket criado com sucesso.')
            return redirect('app_db:tickets_list')
    else:
        form = TicketForm()
        
    context = {
        'active_nav': 'tickets',
        'title': 'Criar Ticket',
        'form': form,
        'cancel_url': 'app_db:tickets_list',
    }
    return render(request, 'app_db/crud_form.html', context)

def tickets_update(request, pk):
    ticket = get_object_or_404(Tickets, pk=pk, deleted_at__isnull=True)
    if request.method == 'POST':
        form = TicketForm(request.POST, instance=ticket)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.updated_at = timezone.now()
            ticket.save()
            messages.success(request, 'Ticket atualizado com sucesso.')
            return redirect('app_db:tickets_list')
    else:
        form = TicketForm(instance=ticket)
        
    context = {
        'active_nav': 'tickets',
        'title': f'Editar Ticket: {ticket.subject}',
        'form': form,
        'cancel_url': 'app_db:tickets_list',
    }
    return render(request, 'app_db/crud_form.html', context)

def tickets_delete(request, pk):
    ticket = get_object_or_404(Tickets, pk=pk, deleted_at__isnull=True)
    if request.method == 'POST':
        soft_delete(ticket)
        messages.success(request, 'Ticket eliminado com sucesso.')
        return redirect('app_db:tickets_list')
        
    context = {
        'active_nav': 'tickets',
        'title': 'Eliminar Ticket',
        'object_name': ticket.subject,
        'cancel_url': 'app_db:tickets_list',
    }
    return render(request, 'app_db/crud_confirm_delete.html', context)


# ==============================================================================
# CRUD GESTORES
# ==============================================================================
def gestores_list(request):
    items = Users.objects.select_related('company', 'role').filter(company__isnull=False, deleted_at__isnull=True).order_by('-created_at')
    context = {
        'active_nav': 'gestores',
        'title': 'Gestores',
        'items': items,
        'create_url': 'app_db:gestores_create',
        'update_url': 'app_db:gestores_update',
        'delete_url': 'app_db:gestores_delete',
        'columns': ['id', 'name', 'email', 'company_id', 'role_id', 'is_active'],
        'fields': ['id', 'name', 'email', 'company_id', 'role_id', 'is_active'],
    }
    return render(request, 'app_db/crud_list.html', context)

def gestores_create(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.created_at = timezone.now()
            user.updated_at = timezone.now()
            user.save()
            messages.success(request, 'Gestor criado com sucesso.')
            return redirect('app_db:gestores_list')
    else:
        form = UserForm()
        
    context = {
        'active_nav': 'gestores',
        'title': 'Criar Gestor',
        'form': form,
        'cancel_url': 'app_db:gestores_list',
    }
    return render(request, 'app_db/crud_form.html', context)

def gestores_update(request, pk):
    user = get_object_or_404(Users, pk=pk, deleted_at__isnull=True)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            user.updated_at = timezone.now()
            user.save()
            messages.success(request, 'Gestor atualizado com sucesso.')
            return redirect('app_db:gestores_list')
    else:
        form = UserForm(instance=user)
        
    context = {
        'active_nav': 'gestores',
        'title': f'Editar Gestor: {user.name}',
        'form': form,
        'cancel_url': 'app_db:gestores_list',
    }
    return render(request, 'app_db/crud_form.html', context)

def gestores_delete(request, pk):
    user = get_object_or_404(Users, pk=pk, deleted_at__isnull=True)
    if request.method == 'POST':
        soft_delete(user)
        messages.success(request, 'Gestor eliminado com sucesso.')
        return redirect('app_db:gestores_list')
        
    context = {
        'active_nav': 'gestores',
        'title': 'Eliminar Gestor',
        'object_name': user.name,
        'cancel_url': 'app_db:gestores_list',
    }
    return render(request, 'app_db/crud_confirm_delete.html', context)


# ==============================================================================
# CRUD DOCUMENTOS
# ==============================================================================
def documentos_list(request):
    items = Documents.objects.select_related('company', 'uploaded_by_user').filter(deleted_at__isnull=True).order_by('-created_at')
    context = {
        'active_nav': 'documentos',
        'title': 'Documentos',
        'items': items,
        'create_url': 'app_db:documentos_create',
        'update_url': 'app_db:documentos_update',
        'delete_url': 'app_db:documentos_delete',
        'columns': ['id', 'title', 'company_id', 'uploaded_by_user_id', 'document_category', 'status'],
        'fields': ['id', 'title', 'company_id', 'uploaded_by_user_id', 'document_category', 'status'],
    }
    return render(request, 'app_db/crud_list.html', context)

def documentos_create(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            
            if 'upload_file' in request.FILES:
                upload = request.FILES['upload_file']
                fs = FileSystemStorage()
                filename = fs.save(upload.name, upload)
                doc.file_path = fs.url(filename)
            elif not doc.file_path:
                doc.file_path = "" # Fallback if empty
                
            doc.created_at = timezone.now()
            doc.updated_at = timezone.now()
            doc.save()
            messages.success(request, 'Documento criado com sucesso.')
            return redirect('app_db:documentos_list')
    else:
        form = DocumentForm()
        
    context = {
        'active_nav': 'documentos',
        'title': 'Criar Documento',
        'form': form,
        'cancel_url': 'app_db:documentos_list',
    }
    return render(request, 'app_db/crud_form.html', context)

def documentos_update(request, pk):
    doc = get_object_or_404(Documents, pk=pk, deleted_at__isnull=True)
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, instance=doc)
        if form.is_valid():
            doc = form.save(commit=False)
            
            if 'upload_file' in request.FILES:
                upload = request.FILES['upload_file']
                fs = FileSystemStorage()
                filename = fs.save(upload.name, upload)
                doc.file_path = fs.url(filename)
                
            doc.updated_at = timezone.now()
            doc.save()
            messages.success(request, 'Documento atualizado com sucesso.')
            return redirect('app_db:documentos_list')
    else:
        form = DocumentForm(instance=doc)
        
    context = {
        'active_nav': 'documentos',
        'title': f'Editar Documento: {doc.title}',
        'form': form,
        'cancel_url': 'app_db:documentos_list',
    }
    return render(request, 'app_db/crud_form.html', context)

def documentos_delete(request, pk):
    doc = get_object_or_404(Documents, pk=pk, deleted_at__isnull=True)
    if request.method == 'POST':
        soft_delete(doc)
        messages.success(request, 'Documento eliminado com sucesso.')
        return redirect('app_db:documentos_list')
        
    context = {
        'active_nav': 'documentos',
        'title': 'Eliminar Documento',
        'object_name': doc.title,
        'cancel_url': 'app_db:documentos_list',
    }
    return render(request, 'app_db/crud_confirm_delete.html', context)


# ==============================================================================
# CRUD NOTÍCIAS (ARTIGOS)
# ==============================================================================
def noticias_list(request):
    items = Articles.objects.select_related('author').filter(deleted_at__isnull=True).order_by('-created_at')
    context = {
        'active_nav': 'noticias',
        'title': 'Notícias',
        'items': items,
        'create_url': 'app_db:noticias_create',
        'update_url': 'app_db:noticias_update',
        'delete_url': 'app_db:noticias_delete',
        'columns': ['id', 'title', 'author_id', 'published_date', 'status'],
        'fields': ['id', 'title', 'author_id', 'published_date', 'status'],
    }
    return render(request, 'app_db/crud_list.html', context)

def noticias_create(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.created_at = timezone.now()
            article.updated_at = timezone.now()
            article.save()
            messages.success(request, 'Notícia criada com sucesso.')
            return redirect('app_db:noticias_list')
    else:
        form = ArticleForm()
        
    context = {
        'active_nav': 'noticias',
        'title': 'Criar Notícia',
        'form': form,
        'cancel_url': 'app_db:noticias_list',
    }
    return render(request, 'app_db/crud_form.html', context)

def noticias_update(request, pk):
    article = get_object_or_404(Articles, pk=pk, deleted_at__isnull=True)
    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            article = form.save(commit=False)
            article.updated_at = timezone.now()
            article.save()
            messages.success(request, 'Notícia atualizada com sucesso.')
            return redirect('app_db:noticias_list')
    else:
        form = ArticleForm(instance=article)
        
    context = {
        'active_nav': 'noticias',
        'title': f'Editar Notícia: {article.title}',
        'form': form,
        'cancel_url': 'app_db:noticias_list',
    }
    return render(request, 'app_db/crud_form.html', context)

def noticias_delete(request, pk):
    article = get_object_or_404(Articles, pk=pk, deleted_at__isnull=True)
    if request.method == 'POST':
        soft_delete(article)
        messages.success(request, 'Notícia eliminada com sucesso.')
        return redirect('app_db:noticias_list')
        
    context = {
        'active_nav': 'noticias',
        'title': 'Eliminar Notícia',
        'object_name': article.title,
        'cancel_url': 'app_db:noticias_list',
    }
    return render(request, 'app_db/crud_confirm_delete.html', context)



