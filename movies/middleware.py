from movies import models as MoviesModels


class AppMiddleWare:
    def __init__(self, get_response):
        self.get_response = get_response

        app_request = MoviesModels.AppRequest.objects.all()
        if not app_request:
            app_request = MoviesModels.AppRequest.objects.create()

    def __call__(self, request):

        if "admin" not in request.path:
            app_request = MoviesModels.AppRequest.objects.all().first()
            app_request.request_count = app_request.request_count + 1
            app_request.save()

        response = self.get_response(request)
        return response
