from django.contrib.auth.models import User
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=64)


class Institution(models.Model):
    institution_choices = ((1, "fundacja"),
                           (2, "organizacja pozarządowa"),
                           (3, "zbiórka lokalna"),
                           )
    name = models.CharField(max_length=64)
    description = models.TextField()
    type = models.IntegerField(choices=institution_choices, default=1)
    categories = models.ManyToManyField(Category)

    # @property
    # def institution_value(self):
    #     return self.get_type_display()
    #
    # @property
    # def categories_str(self):
    #     return ', '.join([category.name for category in self.categories.all()])
    #
    # @property
    # def categories_list(self):
    #     return [category.name for category in self.categories.all()]


class Donation(models.Model):
    quantity = models.IntegerField()
    categories = models.ManyToManyField(Category)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    address = models.CharField(max_length=128)
    phone_number = models.IntegerField()
    city = models.CharField(max_length=64)
    zip_code = models.IntegerField()
    pick_up_date = models.DateField()
    pick_up_time = models.TimeField()
    pick_up_comment = models.TextField()
    user = models.ForeignKey(User, null=True, default=None, on_delete=models.SET_NULL)
