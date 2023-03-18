from rest_framework import generics
from rest_framework.response import Response

from accounts.api.serializers import LoginSerializer, RegisterSerializer


class LoginGenericView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=200)


class RegisterGenericView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
