'''
Created on 3 Dec 2011

@author: dgorissen
'''
from django.db import models

# Create your models here.

class Rule(models.Model):
    def __init__(self):
        self.name = models.CharField()
        self.description = models.CharField()
        self.active = models.BooleanField(default=True)

class Record(models.Model):
    def __init__(self):
        self.key = models.CharField()
        self.value = models.CharField()

class Dataset(models.Model):
    def __init__(self):
        self.name = models.CharField()
        self.records = models.ForeignKey(Record)
        