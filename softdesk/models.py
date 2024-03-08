from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):

    birthday = models.DateField(default=None, blank=False)
    can_be_contacted = models.BooleanField(default=False, null=False, verbose_name='Allowed contact')
    can_be_shared = models.BooleanField(default=False, null=False, verbose_name='Share data consent')
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'  # indicates email as identifier in User Model
    REQUIRED_FIELDS = ['password', 'birthday', 'can_be_shared', 'can_be_contacted']


class Project(models.Model):

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

        if self.pk and self.contributors != None:  # Si l'instance n'existe pas encore dans la base de données
            self.contributors.add(self.author.id)
        else:
            self.contributors.set(self.author.id)
            # Ajouter l'auteur à la liste des contributeurs
        super(Project, self).save(*args, **kwargs)
