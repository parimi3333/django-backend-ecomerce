from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import MyUser

class MyUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = MyUser
        fields = ('id', 'email', 'phone', 'name', 'password', 'is_active', 'is_admin')

        extra_kwargs = {
            'id': {'read_only': True},
            'is_active': {'read_only': True},
            'is_admin': {'read_only': True},
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data.get('password'))
        return super(MyUserSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        instance = super(MyUserSerializer, self).update(instance, validated_data)

        if password:
            instance.password = make_password(password)
            instance.save()

        return instance

