import json

from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view

from api.utils import fetch_movies_data
from movies import models as MoviesModels
from api import serializers


class CustomListPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"


def save_genres(genres, movie):
    for genre in genres:
        if MoviesModels.MovieGenre.objects.filter(name=genre.get("name")).exists():
            genre_obj = MoviesModels.MovieGenre.objects.filter(
                name=genre.get("name")
            ).first()
            genre_obj.increase_movie_count()
        else:
            serializer = serializers.GenreSerializer(data=genre)
            if serializer.is_valid():
                serializer.save()

                genre_obj = MoviesModels.MovieGenre.objects.filter(
                    name=genre.get("name")
                ).first()
        movie.genres.add(genre_obj)
    movie.save()
    return movie


class MoviesListViews(APIView):
    def get(self, request):
        # fetch movies for api
        page_num = request.GET.get("page", 1)
        response = fetch_movies_data(page_num)

        if "error" in response.keys() or "is_success" in response.keys():
            response = fetch_movies_data(page_num)

        # format response data
        # next variable should point to our app
        domain = get_current_site(request).domain
        if response.get("next"):
            response["next"] = "http://{}{}?page={}".format(
                domain, reverse("api:movies-list"), int(page_num) + 1
            )
        if response.get("previous"):
            response["previous"] = "http://{}{}?page={}".format(
                domain, reverse("api:movies-list"), int(page_num) - 1
            )

        return Response(data=response, status=status.HTTP_200_OK)


class CollectListCreateViews(APIView):
    serializer_class = serializers.CollectionSerializer
    model = MoviesModels.Collection
    pagination_class = CustomListPagination

    def get(self, request):
        collections = self.model.objects.all()
        serializer = serializers.CollectionSerializer(collections, many=True)

        favourite_genres = MoviesModels.MovieGenre.objects.all().order_by(
            "movie_count"
        )[:3]
        genre_serializer = serializers.GenreSerializer(favourite_genres, many=True)

        # formatting response
        response_data = dict()
        response_data["is_success"] = True
        response_data["data"] = {
            "collections": serializer.data,
            "favourite_genres": genre_serializer.data,
        }

        return Response(data=response_data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = serializers.CollectionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            collection = MoviesModels.Collection.objects.filter(
                uuid=serializer.data.get("uuid")
            ).first()

            movies = request.data.get("movies")
            movies_serializer = serializers.MovieSerializer(data=movies, many=True)
            if movies_serializer.is_valid():
                movies_serializer.save()

                for movie in movies:
                    movie_obj = MoviesModels.CollectionMovie.objects.filter(
                        uuid=movie.get("uuid")
                    ).first()

                    movie = save_genres(movie.get("genres"), movie_obj)
                    collection.movies.add(movie)
                    collection.save()

            else:
                Response(movies_serializer.errors, status=status.HTTP_409_CONFLICT)

            return Response(
                {"collection_uuid": collection.uuid}, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CollectUpdateViews(APIView):
    serializer_class = serializers.MovieSerializer
    model = MoviesModels.Collection
    pagination_class = CustomListPagination

    def get(self, request, collection_uuid):
        collection = self.model.objects.filter(uuid=collection_uuid).first()
        serializer = serializers.CollectionSerializer(collection)

        response = {
            **serializer.data,
            "movies": serializers.MovieSerializer(
                collection.movies.all(), many=True
            ).data,
        }
        return Response(data=response, status=status.HTTP_200_OK)

    def put(self, request, collection_uuid):
        collection = MoviesModels.Collection.objects.filter(
            uuid=collection_uuid
        ).first()

        movies_serializer = serializers.MovieSerializer(data=request.data)
        if movies_serializer.is_valid():
            movies_serializer.save()

            movie_obj = MoviesModels.CollectionMovie.objects.filter(
                uuid=movies_serializer.data.get("uuid")
            ).first()

            movie = save_genres(request.data.get("genres"), movie_obj)
            collection.movies.add(movie)
            collection.save()

            return Response(
                serializers.MovieSerializer(movie_obj).data,
                status=status.HTTP_201_CREATED,
            )
        return Response(movies_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, collection_uuid):
        collection = MoviesModels.Collection.objects.filter(uuid=collection_uuid)
        if collection:
            collection.delete()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
def RequestView(request):
    request_count = MoviesModels.AppRequest.objects.all().first().request_count

    return Response({"requests": request_count}, status=status.HTTP_200_OK)


@api_view(["POST"])
def RequestResetView(request):
    request_count = MoviesModels.AppRequest.objects.all().first()
    request_count.request_count = 0
    request_count.save()

    return Response({"message": "request count reset successfully"}, status=status.HTTP_201_CREATED)
