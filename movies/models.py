from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save, pre_delete

import uuid


class MovieGenre(models.Model):
    uuid = models.CharField(_("uuid"), max_length=50, null=True, blank=True)
    name = models.CharField(_("name"), max_length=256)
    movie_count = models.IntegerField(_("Count"), default=1)

    def increase_movie_count(self):
        self.movie_count = self.movie_count + 1
        self.save()

    def __str__(self):
        return self.name


class CollectionMovie(models.Model):
    uuid = models.CharField(_("uuid"), max_length=50, null=True, blank=True)
    title = models.CharField(_("Title"), max_length=256)
    description = models.TextField(_("Description"))
    genres = models.ManyToManyField(to=MovieGenre, related_name="genres")
    created_on = models.DateField(_("Created On"), default=timezone.now)

    def __str__(self):
        return self.title


# Create your models here.
class Collection(models.Model):
    uuid = models.CharField(_("uuid"), max_length=50, null=True, blank=True)
    title = models.CharField(_("Title"), max_length=256)
    description = models.TextField(_("Description"))
    movies = models.ManyToManyField(to=CollectionMovie, related_name="movies")
    created_on = models.DateField(_("Created On"), default=timezone.now)

    def __str__(self):
        return self.title


class AppRequest(models.Model):
    request_count = models.IntegerField(_("Request Count"), default=0)


def set_uuid(sender, instance, **kwargs):
    # generating uuid
    if not instance.uuid:
        gen_id = str(uuid.uuid4()).replace("-", "")
        instance.uuid = gen_id
        instance.save()


@receiver(pre_delete, sender=Collection)
def delete_related(sender, instance, *args, **kwargs):
    movies = instance.movies.all()
    for movie in movies:
        for genre in movie.genres.all():
            genre.delete()
        movie.delete()


@receiver(pre_delete, sender=CollectionMovie)
def delete_related(sender, instance, *args, **kwargs):
    for genre in instance.genres.all():
        genre.delete()


post_save.connect(set_uuid, sender=MovieGenre)
post_save.connect(set_uuid, sender=Collection)
