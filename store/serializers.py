from rest_framework import serializers #type: ignore
from .models import User

class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','username','email')