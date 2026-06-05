from django.urls import path
from . import views

app_name = 'app_db'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Modelo Lógico
    path('modelo/', views.modelo_cards, name='modelo_cards'),
    path('modelo/mermaid/', views.modelo_mermaid, name='modelo_mermaid'),

    # Empresas CRUD
    path('empresas/', views.empresas_list, name='empresas_list'),
    path('empresas/criar/', views.empresas_create, name='empresas_create'),
    path('empresas/<int:pk>/editar/', views.empresas_update, name='empresas_update'),
    path('empresas/<int:pk>/eliminar/', views.empresas_delete, name='empresas_delete'),

    # Tickets CRUD
    path('tickets/', views.tickets_list, name='tickets_list'),
    path('tickets/criar/', views.tickets_create, name='tickets_create'),
    path('tickets/<int:pk>/editar/', views.tickets_update, name='tickets_update'),
    path('tickets/<int:pk>/eliminar/', views.tickets_delete, name='tickets_delete'),

    # Gestores CRUD
    path('gestores/', views.gestores_list, name='gestores_list'),
    path('gestores/criar/', views.gestores_create, name='gestores_create'),
    path('gestores/<int:pk>/editar/', views.gestores_update, name='gestores_update'),
    path('gestores/<int:pk>/eliminar/', views.gestores_delete, name='gestores_delete'),

    # Documentos CRUD
    path('documentos/', views.documentos_list, name='documentos_list'),
    path('documentos/criar/', views.documentos_create, name='documentos_create'),
    path('documentos/<int:pk>/editar/', views.documentos_update, name='documentos_update'),
    path('documentos/<int:pk>/eliminar/', views.documentos_delete, name='documentos_delete'),

    # Notícias CRUD
    path('noticias/', views.noticias_list, name='noticias_list'),
    path('noticias/criar/', views.noticias_create, name='noticias_create'),
    path('noticias/<int:pk>/editar/', views.noticias_update, name='noticias_update'),
    path('noticias/<int:pk>/eliminar/', views.noticias_delete, name='noticias_delete'),
]
