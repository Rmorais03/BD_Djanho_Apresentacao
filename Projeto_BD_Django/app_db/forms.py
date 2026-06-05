from django import forms
from .models import Companies, Tickets, Users, Documents, Articles, Roles


class CompanyForm(forms.ModelForm):
    """Formulário para criar/editar Empresas."""

    COMPLIANCE_CHOICES = [
        ('', '— Selecionar —'),
        ('Awaiting', 'Awaiting'),
        ('Auditing', 'Auditing'),
        ('Compliant', 'Compliant'),
    ]

    compliance_status = forms.ChoiceField(
        choices=COMPLIANCE_CHOICES, required=False, label='compliance_status'
    )
    is_active = forms.BooleanField(required=False, label='is_active')

    class Meta:
        model = Companies
        fields = ['name', 'nif', 'phone', 'address', 'compliance_status', 'is_active']
        labels = {
            'name': 'name',
            'nif': 'nif',
            'phone': 'phone',
            'address': 'address',
        }

    def clean_compliance_status(self):
        val = self.cleaned_data.get('compliance_status')
        return val if val else None


class TicketForm(forms.ModelForm):
    """Formulário para criar/editar Tickets."""

    CATEGORY_CHOICES = [
        ('', '— Selecionar —'),
        ('Support', 'Suporte'),
        ('Billing', 'Faturação'),
        ('Emergency', 'Emergência'),
        ('Technical', 'Técnico'),
    ]
    PRIORITY_CHOICES = [
        ('', '— Selecionar —'),
        ('Low', 'Baixa'),
        ('Medium', 'Média'),
        ('High', 'Alta'),
        ('Critical', 'Crítica'),
    ]
    STATUS_CHOICES = [
        ('', '— Selecionar —'),
        ('Open', 'Aberto'),
        ('In Progress', 'Em Curso'),
        ('Resolved', 'Resolvido'),
        ('Closed', 'Fechado'),
    ]

    category = forms.ChoiceField(choices=CATEGORY_CHOICES, label='category')
    priority = forms.ChoiceField(choices=PRIORITY_CHOICES, required=False, label='priority')
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False, label='status')

    class Meta:
        model = Tickets
        fields = ['company', 'opened_by_user', 'assigned_to_user', 'category',
                  'priority', 'subject', 'description', 'status']
        labels = {
            'company': 'company_id',
            'opened_by_user': 'opened_by_user_id',
            'assigned_to_user': 'assigned_to_user_id',
            'subject': 'subject',
            'description': 'description',
        }

    def clean_priority(self):
        val = self.cleaned_data.get('priority')
        return val if val else None

    def clean_status(self):
        val = self.cleaned_data.get('status')
        return val if val else None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['company'].queryset = Companies.objects.filter(deleted_at__isnull=True)
        self.fields['opened_by_user'].queryset = Users.objects.filter(deleted_at__isnull=True)
        self.fields['assigned_to_user'].queryset = Users.objects.filter(deleted_at__isnull=True)


class UserForm(forms.ModelForm):
    """Formulário para criar/editar Gestores (Users com empresa)."""

    is_active = forms.BooleanField(required=False, label='is_active')

    class Meta:
        model = Users
        fields = ['name', 'email', 'phone', 'role', 'company', 'is_active']
        labels = {
            'name': 'name',
            'email': 'email',
            'phone': 'phone',
            'role': 'role_id',
            'company': 'company_id',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].queryset = Roles.objects.filter(deleted_at__isnull=True)
        self.fields['company'].queryset = Companies.objects.filter(deleted_at__isnull=True)
        self.fields['company'].required = True  # Gestores must have a company


class DocumentForm(forms.ModelForm):
    """Formulário para criar/editar Documentos."""

    DOC_CATEGORY_CHOICES = [
        ('', '— Selecionar —'),
        ('Policies', 'Políticas'),
        ('Network', 'Rede'),
        ('Training', 'Formação'),
        ('Incident_Response', 'Resposta a Incidentes'),
        ('Templates', 'Modelos'),
        ('Other', 'Outro'),
    ]
    STATUS_CHOICES = [
        ('', '— Selecionar —'),
        ('Informational', 'Informativo'),
        ('Pending_Client', 'Pendente Cliente'),
        ('Submitted', 'Submetido'),
        ('Approved', 'Aprovado'),
        ('Rejected', 'Rejeitado'),
    ]

    document_category = forms.ChoiceField(choices=DOC_CATEGORY_CHOICES, label='document_category')
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False, label='status')
    is_action_required = forms.BooleanField(required=False, label='is_action_required')
    upload_file = forms.FileField(required=False, label='file_upload (Anexar PDF/Docs)')

    class Meta:
        model = Documents
        fields = ['company', 'uploaded_by_user', 'document_category', 'title',
                  'is_action_required', 'status']
        labels = {
            'company': 'company_id',
            'uploaded_by_user': 'uploaded_by_user_id',
            'title': 'title',
        }

    def clean_status(self):
        val = self.cleaned_data.get('status')
        return val if val else None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['company'].queryset = Companies.objects.filter(deleted_at__isnull=True)
        self.fields['uploaded_by_user'].queryset = Users.objects.filter(deleted_at__isnull=True)


class ArticleForm(forms.ModelForm):
    """Formulário para criar/editar Notícias (Articles)."""

    STATUS_CHOICES = [
        ('', '— Selecionar —'),
        ('Draft', 'Rascunho'),
        ('Published', 'Publicado'),
    ]

    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False, label='status')

    class Meta:
        model = Articles
        fields = ['author', 'title', 'slug', 'summary', 'content_body',
                  'published_date', 'status']
        labels = {
            'author': 'author_id',
            'title': 'title',
            'slug': 'slug',
            'summary': 'summary',
            'content_body': 'content_body',
            'published_date': 'published_date',
        }
        widgets = {
            'published_date': forms.DateInput(attrs={'type': 'date'}),
            'summary': forms.Textarea(attrs={'rows': 3}),
            'content_body': forms.Textarea(attrs={'rows': 6}),
        }

    def clean_status(self):
        val = self.cleaned_data.get('status')
        return val if val else None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['author'].queryset = Users.objects.filter(deleted_at__isnull=True)
