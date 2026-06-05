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
    """Página com o diagrama ER gerado em Mermaid."""
    models_info = get_model_info()
    context = {
        'active_nav': 'modelo_mermaid',
        'models': models_info,
        'mermaid_code': _build_mermaid_er(models_info),
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



