from django.db import models
import uuid
from django.utils.translation import gettext_lazy as _
# Create your models here.

class PersonModel(models.Model):
    class GENDER_CHOICES(models.TextChoices):
        MALE = 'male', _('male')
        FEMALE = 'female', _('female')
    
    class AGE_GROUP_CHOICES(models.TextChoices):
        CHILD = 'child', _('child')
        TEENAGER = 'teenager', _('teenager')
        ADULT = 'adult', _('adult')
        SENIOR = 'senior', _('senior')

    # id = models.UUIDField(default=uuid.uuid7, editable=False, primary_key=True)
    # name = models.CharField(max_length=75, verbose_name=_("Name"))
    # gender = models.CharField(choices=GENDER_CHOICES.choices, max_length=7, verbose_name=_("Gender"))
    # gender_probability = models.DecimalField(decimal_places=2, max_digits=10, verbose_name=_('Gender probability'))
    # sample_size = models.PositiveIntegerField(verbose_name=_("Sample size"))
    # age = models.PositiveIntegerField(verbose_name=_("Age"))
    # age_group = models.CharField(choices=AGE_GROUP_CHOICES.choices, max_length=10, verbose_name=_("Age Group"))
    # country_id = models.CharField(max_length=5, verbose_name=_("Country ID"))
    # country_probability = models.DecimalField(decimal_places=2, max_digits=10, verbose_name=_('Country probability'))
    # created_at = models.DateTimeField(auto_now_add=True)
    
    id = models.UUIDField(default=uuid.uuid7, editable=False, primary_key=True)
    name = models.CharField(max_length=75, verbose_name=_("Name"))
    gender = models.CharField(choices=GENDER_CHOICES.choices, max_length=7, verbose_name=_("Gender"))
    gender_probability = models.DecimalField(decimal_places=2, max_digits=10, verbose_name=_('Gender probability'))
    age = models.PositiveIntegerField(verbose_name=_("Age"))
    age_group = models.CharField(choices=AGE_GROUP_CHOICES.choices, max_length=10, verbose_name=_("Age Group"))
    country_id = models.CharField(max_length=5, verbose_name=_("Country ID"))
    country_name = models.CharField(max_length=75, verbose_name=_("Country Name"))
    country_probability = models.DecimalField(decimal_places=2, max_digits=10, verbose_name=_('Country probability'))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['id', 'name'])
        ]
        db_table='profiles'
        verbose_name="profile"
        verbose_name_plural = "profiles"
    def __str__(self):
        return self.name