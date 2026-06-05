# Auto-generated Django models from NeonDB
# Added __str__ methods for better representation in forms and admin
from django.db import models


class ArticleCategories(models.Model):
    pk = models.CompositePrimaryKey('article_id', 'category_id')
    article_id = models.IntegerField()
    category_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'Article_Categories'

    def __str__(self):
        return f"Artigo {self.article_id} ↔ Categoria {self.category_id}"


class Articles(models.Model):
    author = models.ForeignKey('Users', models.DO_NOTHING)
    title = models.CharField(max_length=255)
    slug = models.CharField(unique=True, max_length=255)
    summary = models.TextField(blank=True, null=True)
    content_body = models.TextField(blank=True, null=True)
    cover_image = models.CharField(max_length=255, blank=True, null=True)
    published_date = models.DateField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)  # This field type is a guess.
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Articles'

    def __str__(self):
        return self.title


class Assets(models.Model):
    company = models.ForeignKey('Companies', models.DO_NOTHING)
    created_by_user_id = models.IntegerField()
    asset_code = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.TextField()  # This field type is a guess.
    owner = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    confidentiality = models.TextField(blank=True, null=True)  # This field type is a guess.
    integrity = models.TextField(blank=True, null=True)  # This field type is a guess.
    availability = models.TextField(blank=True, null=True)  # This field type is a guess.
    status = models.TextField(blank=True, null=True)  # This field type is a guess.
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Assets'

    def __str__(self):
        return self.name


class Auditlogs(models.Model):
    user = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    action = models.CharField(max_length=255)
    entity_type = models.CharField(max_length=255, blank=True, null=True)
    entity_id = models.IntegerField(blank=True, null=True)
    ip_address = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'AuditLogs'

    def __str__(self):
        return f"{self.action} — {self.entity_type}"


class Categories(models.Model):
    name = models.CharField(max_length=255)
    slug = models.CharField(unique=True, max_length=255)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Categories'

    def __str__(self):
        return self.name


class ChatUsers(models.Model):
    pk = models.CompositePrimaryKey('chat_id', 'user_id')
    chat_id = models.IntegerField()
    user_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'Chat_Users'

    def __str__(self):
        return f"Chat {self.chat_id} ↔ User {self.user_id}"


class Chats(models.Model):
    company = models.ForeignKey('Companies', models.DO_NOTHING)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Chats'

    def __str__(self):
        return f"Chat #{self.id}"


class Companies(models.Model):
    name = models.CharField(max_length=255)
    nif = models.IntegerField(unique=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    compliance_status = models.TextField(blank=True, null=True)  # This field type is a guess.
    is_active = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    manager_user = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Companies'

    def __str__(self):
        return self.name


class Documents(models.Model):
    company = models.ForeignKey(Companies, models.DO_NOTHING)
    uploaded_by_user = models.ForeignKey('Users', models.DO_NOTHING)
    document_category = models.TextField()  # This field type is a guess.
    title = models.CharField(max_length=255)
    file_path = models.CharField(max_length=255)
    is_action_required = models.BooleanField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)  # This field type is a guess.
    parent_document = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Documents'

    def __str__(self):
        return self.title


class Incidents(models.Model):
    company = models.ForeignKey(Companies, models.DO_NOTHING)
    asset = models.ForeignKey(Assets, models.DO_NOTHING, blank=True, null=True)
    reported_by_user = models.ForeignKey('Users', models.DO_NOTHING)
    title = models.CharField(max_length=255)
    severity = models.TextField(blank=True, null=True)  # This field type is a guess.
    status = models.TextField(blank=True, null=True)  # This field type is a guess.
    cncs_form_data = models.JSONField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Incidents'

    def __str__(self):
        return self.title


class Messages(models.Model):
    sender = models.ForeignKey('Users', models.DO_NOTHING)
    ticket = models.ForeignKey('Tickets', models.DO_NOTHING, blank=True, null=True)
    chat = models.ForeignKey(Chats, models.DO_NOTHING, blank=True, null=True)
    content = models.TextField()
    is_read = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Messages'

    def __str__(self):
        return f"Mensagem #{self.id}"


class Pages(models.Model):
    author = models.ForeignKey('Users', models.DO_NOTHING)
    title = models.CharField(max_length=255)
    slug = models.CharField(unique=True, max_length=255)
    content_body = models.JSONField(blank=True, null=True)
    featured_image = models.CharField(max_length=255, blank=True, null=True)
    status = models.TextField(blank=True, null=True)  # This field type is a guess.
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Pages'

    def __str__(self):
        return self.title


class Permissions(models.Model):
    name = models.CharField(unique=True, max_length=255)
    description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Permissions'

    def __str__(self):
        return self.name


class Reports(models.Model):
    company = models.ForeignKey(Companies, models.DO_NOTHING)
    created_by_user = models.ForeignKey('Users', models.DO_NOTHING)
    report_type = models.TextField()  # This field type is a guess.
    title = models.CharField(max_length=255)
    risk_score = models.IntegerField(blank=True, null=True)
    file_path = models.CharField(max_length=255)
    status = models.TextField(blank=True, null=True)  # This field type is a guess.
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Reports'

    def __str__(self):
        return self.title


class RolePermissions(models.Model):
    pk = models.CompositePrimaryKey('role_id', 'permission_id')
    role_id = models.IntegerField()
    permission_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'Role_Permissions'

    def __str__(self):
        return f"Role {self.role_id} ↔ Permissão {self.permission_id}"


class Roles(models.Model):
    name = models.CharField(unique=True, max_length=255)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Roles'

    def __str__(self):
        return self.name


class Tickets(models.Model):
    company = models.ForeignKey(Companies, models.DO_NOTHING)
    opened_by_user = models.ForeignKey('Users', models.DO_NOTHING)
    assigned_to_user = models.ForeignKey('Users', models.DO_NOTHING, related_name='tickets_assigned_to_user_set', blank=True, null=True)
    category = models.TextField()  # This field type is a guess.
    priority = models.TextField(blank=True, null=True)  # This field type is a guess.
    subject = models.CharField(max_length=255)
    description = models.TextField()
    status = models.TextField(blank=True, null=True)  # This field type is a guess.
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Tickets'

    def __str__(self):
        return self.subject


class Users(models.Model):
    role = models.ForeignKey(Roles, models.DO_NOTHING, blank=True, null=True)
    company = models.ForeignKey(Companies, models.DO_NOTHING, blank=True, null=True)
    name = models.CharField(max_length=255)
    email = models.CharField(unique=True, max_length=255)
    password = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    is_2fa_enabled = models.BooleanField(blank=True, null=True)
    is_active = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    activation_token = models.CharField(max_length=255, blank=True, null=True)
    token_expires_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Users'

    def __str__(self):
        return self.name
