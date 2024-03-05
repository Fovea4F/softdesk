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

        def is_author_in_contributions(self, author_id):
            # Check if the author's ID exists in the contributors ManyToManyField of the model instance
            author_exists = self.contributors.filter(id=author_id).exists()
            return author_exists

        super().save(*args, **kwargs)

        if self.pk:
            if not is_author_in_contributions(self, self.author_id):
                # if self.author_id not in self.contributors.all():
                self.contributors.add(self.author_id)

                print('toto')
                super().save()
