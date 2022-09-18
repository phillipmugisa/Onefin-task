from rest_framework import serializers
from movies import models as MoviesModels


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoviesModels.MovieGenre
        fields = ("name",)


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoviesModels.CollectionMovie
        fields = ("title", "uuid", "description")

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["genres"] = list()
        for genre in instance.genres.all():
            serializer = GenreSerializer(genre)
            representation["genres"].append(serializer.data)
        return representation


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoviesModels.Collection
        fields = ("title", "uuid", "description")
