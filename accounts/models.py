from datetime import timedelta

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.validators import FileExtensionValidator, RegexValidator, MinValueValidator, MaxValueValidator
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.text import slugify
from django.utils import timezone


class BaseModel(models.Model):
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)

   class Meta:
      abstract = True


class UserManager(BaseUserManager):

   def create_user(self, email, name, password=None, **extra_fields):
      if not email:
         return ValueError("Email field must be set!")
      
      if not password:
         return ValueError("Password field must be set!")
      
      email = self.normalize_email(email)

      user = self.model(email=email, name=name, **extra_fields)
      if password:
         user.set_password(password)

      user.save(using=self.db)
      
      return user


   def create_superuser(self, email, name, password=None, **extra_fields):
      extra_fields.setdefault('is_staff', True)
      extra_fields.setdefault('is_superuser', True)
      extra_fields.setdefault('is_active', True)
      extra_fields.setdefault('role', "MANAGER")

      if extra_fields.get('is_staff') is not True:
         raise ValueError("Superuser must have is_staff=True.")
        
      if extra_fields.get('is_superuser') is not True:
         raise ValueError("Superuser must have is_superuser=True.")
      
      return self.create_user(email, name, password, **extra_fields)



class User(BaseModel, AbstractBaseUser, PermissionsMixin):
   ROLE_CHOICE = (
      ('PLAYER', "Player"),
      ('MANAGER', 'Manager')
   )

   username = None
   email = models.EmailField(unique=True)
   name = models.CharField(max_length=155)
   description = models.TextField(null=True, blank=True)
   date_of_birth = models.DateField(null=True, blank=True)
   photo = models.ImageField(upload_to='player_photo/', blank=True,  default='player_photo/default_player.png', validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])])
   contact = models.CharField(
      max_length=15,
      null=True,
      blank=True,
      validators=[
         RegexValidator(
            regex=r'^9\d{9}$',
            message="Contact Number must start with '9' and have exactly 10 digits.",
            code='invalid_contact'
         )
      ]
   )
   favorite_player = models.CharField(max_length=255, null=True, blank=True, default="Cristiano Ronaldo")
   favorite_team = models.CharField(max_length=355, null=True, blank=True, default="Real Madrid")

   role = models.CharField(max_length=25, choices=ROLE_CHOICE, default='PLAYER')

   is_active = models.BooleanField(default=True)
   is_staff = models.BooleanField(default=False)

   otp = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(100000), MaxValueValidator(999999)])
   otp_expiry = models.DateTimeField(null=True, blank=True)

   USERNAME_FIELD = 'email'
   REQUIRED_FIELDS = ['name']

   objects = UserManager()

   class Meta:
      verbose_name = "User"
      verbose_name_plural = "Users"


   def save(self, *args, **kwargs):
      super().save(*args, **kwargs) 


   def __str__(self):
      return f'{self.name}'

   
   @property
   def age(self):
      if not self.date_of_birth:
         return 0
      today = timezone.now().date()

      age = today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
      return age


   def has_perm(self, perm, obj=None):
      """Check if the user has a specific permission."""
      return True


   def has_module_perms(self, app_label):
      """Check if the user has permissions to access the specified app."""
      return True
   

@receiver(post_save, sender=User)
def create_user_player(sender, instance, created, **kwargs):
   if created and instance.role == "PLAYER":
      Player.objects.create(
         user = instance,
      )


def create_player_slug(slug):
   base_slug = slugify(slug)
   slug = base_slug
   count = 1

   while Player.objects.filter(slug=slug).exists():
      slug = f"{base_slug}-{count}"
      count += 1
   
   return slug



class Player(models.Model):
   user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='player')
   rating = models.IntegerField(default=50, validators=[MinValueValidator(0), MaxValueValidator(100)])
   goals = models.IntegerField(default=0, validators=[MinValueValidator(0)])
   assists = models.IntegerField(default=0, validators=[MinValueValidator(0)])
   games_played = models.IntegerField(default=0, validators=[MinValueValidator(0)])

   slug = models.SlugField(unique=True)

   def __str__(self):
      return self.user.name if hasattr(self, 'user') and self.user else f"Player {self.id}"
   
   def save(self, *args, **kwargs):
      if not self.slug:
         slug = create_player_slug(self.user.name)
         self.slug = slug

      if self.pk:
         self.rating = self.calculate_player_rating()

      super().save(*args, **kwargs)


   def calculate_player_rating(self):
      if not self.pk:
         return 50

      game_ratings = self.player_game_rating.all()
      review_ratings = self.player_game_review_rating.all()

      game_count = 1
      review_count = 1
      game_rating_total = 0
      review_rating_total = 0

      if game_ratings:
         for game_rating in game_ratings:
            game_rating_total = ((game_rating.rating + game_rating_total)/game_count)/10*100
            game_count += 1

      if review_ratings:
         for review_rating in review_ratings:
            review_rating_total = ((review_rating.rating + review_rating_total)/review_count)/5*100
            review_count += 1

      if game_ratings and review_ratings:
         rating = (50+ game_rating_total + review_rating_total)/3
      if game_ratings:
         rating = (50+ game_rating_total)/2
      else:
         rating = 50

      return rating
   

class InvitedManager(models.Model):
   email = models.EmailField(unique=True)
   created_at = models.DateTimeField(default=timezone.now)
   expiry = models.DateTimeField(null=True)

   def __str__(self):
      return self.email