import json
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from auth_app import models as AuthModels
from movies import models as MoviesModels


class TestApi(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.test_user = AuthModels.User.objects.create_user(
            username="testuser", password="test_user2393"
        )
        self.client.login(username=self.test_user.username, password="test_user2393")

        refresh = RefreshToken.for_user(self.test_user)
        self.refresh_token = refresh
        self.access_token = refresh.access_token

    def test_movies_list_endpoint(self):

        headers = {"HTTP_AUTHORIZATION": f"JWT {self.access_token}"}

        # all requests must have access token
        response = self.client.get(
            reverse("api:movies-list"), content_type="application/json", **headers
        )

        self.assertEquals(response.status_code, status.HTTP_200_OK)

        # response must contain count variable
        self.assertIn("count", response.data.keys())

    def test_collection_list_endpoint(self):

        headers = {"HTTP_AUTHORIZATION": f"JWT {self.access_token}"}

        # all requests must have access token
        response = self.client.get(
            reverse("api:collection-list"), content_type="application/json", **headers
        )

        self.assertEquals(response.status_code, status.HTTP_200_OK)

        # response must contain count variable
        self.assertIn("is_success", response.data.keys())

    def test_collection_create_endpoint(self):

        headers = {"HTTP_AUTHORIZATION": f"JWT {self.access_token}"}

        # all requests must have access token
        response = self.client.post(
            reverse("api:collection-list"),
            {
                "title": "test collection",
                "description": "test collection",
                "movies": [
                    {
                        "title": "testtt",
                        "description": "tesetberv",
                        "genres": [{"name": "action"}, {"name": "romance"}],
                        "uuid": "vwevwevwevwevs",
                    }
                ],
            },
            **headers,
            format="json",
        )

        last_collection = MoviesModels.Collection.objects.all().last()
        self.assertEquals(last_collection.title, "test collection")

        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # test collection update

        response = self.client.put(
            reverse("api:collection", args=[last_collection.uuid]),
            {
                "title": "testtt-2",
                "description": "tesetberv-2",
                "genres": [{"name": "action"}, {"name": "fantasy"}],
                "uuid": "1236543245543",
            },
            **headers,
            format="json",
        )

        self.assertEquals(response.data.get("title"), "testtt-2")

        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        # test collection retrieve

        response = self.client.get(
            reverse("api:collection", args=[last_collection.uuid]),
            **headers,
            format="json",
        )

        self.assertEquals(response.data.get("title"), "test collection")

        self.assertEquals(response.status_code, status.HTTP_200_OK)

        # test collection delete

        response = self.client.delete(
            reverse("api:collection", args=[last_collection.uuid]),
            **headers,
            format="json",
        )

        self.assertFalse(
            MoviesModels.Collection.objects.filter(uuid=last_collection.uuid).exists()
        )
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_request_track(self):

        headers = {"HTTP_AUTHORIZATION": f"JWT {self.access_token}"}

        # all requests must have access token
        response = self.client.get(
            reverse("api:collection-list"), content_type="application/json", **headers
        )

        response = self.client.get(
            reverse("api:request_count"), content_type="application/json", **headers
        )
        self.assertGreaterEqual(response.data.get("requests"), 2)
