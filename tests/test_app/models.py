from django.db import models

# Create your models here.
class ModelNoEvent(models.Model):
    int_field = models.IntegerField()
    char_field = models.CharField(max_length=100)
    uuid_field = models.UUIDField()
    dt_field = models.DateTimeField()


class Model1(models.Model):
    int_field = models.IntegerField()
    char_field = models.CharField(max_length=100)
    uuid_field = models.UUIDField()
    dt_field = models.DateTimeField()


class StatusModel(models.Model):
    STATUS_CHOICES = (('created', 'Created'),
                      ('modified', 'Modified'),
                      ('finished', 'Finished'),
                      ('failed', 'Failed'))

    status = models.CharField(max_length=100, choices=STATUS_CHOICES)
    int_field = models.IntegerField()
    char_field = models.CharField(max_length=100)
    uuid_field = models.UUIDField()
    dt_field = models.DateTimeField()


class StatusModel2(models.Model):
    STATUS_CHOICES = (('created', 'Created'),
                      ('modified', 'Modified'),
                      ('finished', 'Finished'),
                      ('failed', 'Failed'))

    state = models.CharField(max_length=100, choices=STATUS_CHOICES)
    int_field = models.IntegerField()
    char_field = models.CharField(max_length=100)
    uuid_field = models.UUIDField()
    dt_field = models.DateTimeField()