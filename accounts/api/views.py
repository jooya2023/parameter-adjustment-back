from rest_framework import generics
from rest_framework.response import Response

from accounts.api.serializers import LoginSerializer, RegisterSerializer

from core.helper.redis import Redis


class LoginGenericView(generics.GenericAPIView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.redis = Redis()

    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        username = serializer.data.get("username")
        refresh_token = serializer.data["tokens"]["refresh"]
        self.redis.redis_add_refresh_token(username, refresh_token)
        return Response(serializer.data, status=200)


class RegisterGenericView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
