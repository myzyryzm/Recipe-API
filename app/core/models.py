from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
# retrieve settings from django settings file
from django.conf import settings
import uuid
import os

def song_file_path(instance, filename, generate_uuid=False):
    """generate file path for new song"""
    # return extension of file
    if generate_uuid:
        ext = filename.split('.')[-1]
        filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('uploads/songs/', filename)

def recipe_image_file_path(instance, filename):
    """generate file path for new recipe image"""
    # return extension of file
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('uploads/recipe/', filename)

class UserManager(BaseUserManager):
    #take any extra fields that passed into create_user and pass them into extra_fields
    def create_user(self, email, password=None, **extra_fields):
        """Create and saves a new user"""
        if not email:
            raise ValueError('Users must have an email address')
        # way management commands work is that u can call self.model to access the model it controls
        # normalize_email is part of base user class therefore we call self 2 get access 2 it
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        # using statement is for when you are using multiple databases; not necessary but good practice anyways
        user.save(using=self._db)

        return user
    
    def create_superuser(self, email, password):
        """creates superuser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user

# give all features that come with user class but allow us to customize
class User(AbstractBaseUser, PermissionsMixin):
    """create a user model with email instead of username"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    objects = UserManager()
    # sets username field 2 b email
    USERNAME_FIELD = 'email'

class Tag(models.Model):
    """Tag to be used for a recipe"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    
    def __str__(self):
        return self.name

class Ingredient(models.Model):
    """Ingredient to be used for a recipe"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    
    def __str__(self):
        return self.name

class Recipe(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    title= models.CharField(max_length=255)
    time_minutes=models.IntegerField()
    price=models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length = 255, blank=True)
    ingredients = models.ManyToManyField('Ingredient')
    tags = models.ManyToManyField('Tag')
    image = models.ImageField(null=True, upload_to=recipe_image_file_path)
    
    def __str__(self):
        return self.title