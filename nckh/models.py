from django.db import models
from django.utils import timezone
import datetime
from datetime import date
from django.core.validators import MinValueValidator, MaxValueValidator
# Create your models here.

class Submit(models.Model):
    comment = models.CharField(max_length=1024,default='')
    date_pub = models.DateTimeField(default=timezone.now)

    _sentiment = models.CharField(max_length=1,default=None)
    def set_sentiment(self,stm):
        _sentiment = stm

class Brand(models.Model):
    trademark = models.TextField()
    amount = models.IntegerField()
    url = models.URLField(default="")
    def __str__(self):
        return self.trademark

class Phone(models.Model):
    brand = models.ForeignKey(Brand,on_delete=models.CASCADE)
    name = models.TextField()
    rating = models.FloatField()
    sold = models.IntegerField()
    price = models.IntegerField()
    imageURL = models.URLField(default="")
    productURL = models.URLField()
    typeOF = models.CharField(max_length=20,default="Tiki")
    store = models.CharField(max_length=20,default="Tiki Trading")
    sku = models.CharField(max_length=20,default="")
    def __str__(self):
        return self.name
class Comment(models.Model):
    phone = models.ForeignKey(Phone,on_delete=models.CASCADE)
    cment = models.TextField(default="")
    stmAS = models.IntegerField(validators=[MinValueValidator(0),MaxValueValidator(5)])
    star = models.FloatField(validators=[MinValueValidator(0),MaxValueValidator(5)])
    def __str__(self):
        return self.cment
class Learn(models.Model):
    lcmt = models.CharField(max_length=1024,default='')
    tag = models.IntegerField(validators=[MinValueValidator(0),MaxValueValidator(1)])
    date_publich = models.DateTimeField(default=timezone.now)