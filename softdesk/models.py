import uuid
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    '''User identity informations model'''

    birthday = models.DateField(default=None, blank=False)
    can_be_contacted = models.BooleanField(default=False, null=False, verbose_name='Allowed contact')
    can_be_shared = models.BooleanField(default=False, null=False, verbose_name='Share data consent')
    email = models.EmailField(unique=True)
    created_date = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'  # indicates email as identifier in User Model
    REQUIRED_FIELDS = ['password', 'birthday', 'can_be_shared', 'can_be_contacted']


class Project(models.Model):
    '''Project informations: targets Customers applications'''

    PROJECT_TYPES = [
        ('back-end', 'back-end'),
        ('front-end', 'front-end'),
        ('IOS', 'IOS'),
        ('Android', 'Android')
    ]

    name = models.CharField(max_length=128, unique=True, null=False, blank=False)
    author = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE)
    contributors = models.ManyToManyField(CustomUser, related_name='contributions', blank=True)
    project_type = models.CharField(max_length=50, choices=PROJECT_TYPES, default=None, null=False)
    description = models.CharField(max_length=500, null=False, blank=False)
    created_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):

        super(Project, self).save(*args, **kwargs)
        # Force project author to be part of contributors users list
        if not self.contributors.filter(pk=self.author.pk).exists():
            self.contributors.add(self.author)


class Issue(models.Model):
    '''Contains Issues informations related to Projects'''
    PRIORITY = [
        ('LOW', 'LOW'),
        ('MEDIUM', 'MEDIUM'),
        ('HIGH', 'HIGH')
    ]

    ISSUE_TYPE = [
        ('BUG', 'BUG'),
        ('FEATURE', 'FEATURE'),
        ('TASK', 'TASK')
    ]

    STATUS = [
        ('To Do', 'To Do'),
        ('In Progress', 'In Progress'),
        ('Finished', 'Finished')
    ]

    name = models.CharField(max_length=128, unique=True, null=False, blank=False)
    author = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE, related_name='issues_authored')
    assigned_contributor = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE, related_name='issues_assigned')
    project = models.ForeignKey(to=Project, on_delete=models.CASCADE, related_name='issues_list')
    issue_type = models.CharField(max_length=50, choices=ISSUE_TYPE, default=None, null=False)
    priority = models.CharField(max_length=50, choices=PRIORITY, default='LOW', null=False)
    status = models.CharField(max_length=50, choices=STATUS, default='To Do', null=False)
    description = models.CharField(max_length=500, null=False, blank=False)
    created_date = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    ''' Ticket model , related to Issues'''
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    author = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE, related_name='comment_author')
    issue_ref = models.ForeignKey(to=Issue, on_delete=models.CASCADE, related_name='comment_list')
    issue_url = models.URLField(editable=False)
    description = models.CharField(max_length=500, null=False, blank=False)
    created_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.issue_url == '':
            self.issue_url = reverse('issue-detail', kwargs={'project_pk': self.issue_ref.project_id,
                                                             'pk': self.issue_ref.pk})
            super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)
