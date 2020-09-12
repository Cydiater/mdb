import datetime

from django.db import models
from django.utils import timezone
from django.views import generic

class Actor(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    gender = models.CharField(max_length=10, null=True)
    constellation = models.CharField(max_length=50, null=True)
    birthday = models.CharField(max_length=50, null=True)
    birthplace = models.CharField(max_length=200, null=True)
    profession = models.CharField(max_length=200, null=True)
    description = models.CharField(max_length=10000, null=True)
    imagePath = models.CharField(max_length=200, default='/static/image/404/actor.jpg')

    def __str__(self):
        return self.name

class Movie(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=20000, null=True)
    rating = models.FloatField(default=0, null=True)
    actors = models.ManyToManyField(Actor)
    genre = models.CharField(max_length=1000, null=True)
    imagePath = models.CharField(max_length=200, default='/static/image/404/movie.jpg')

    def __str__(self):
        return self.name

class Comment(models.Model):
    content = models.CharField(max_length=200)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    def __str__(self):
        return self.content

