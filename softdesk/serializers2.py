from rest_framework import serializers
# from rest_framework.response import Response

from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    # password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    # can_be_contacted = serializers.BooleanField(default=False)
    # can_be_shared = serializers.BooleanField(default=False)

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'birth_day', 'can_be_contacted',
                  'can_be_shared', 'password', 'confirm_password']

    '''def validate(self, data):
        serializer = CustomUserSerializer(data=data)
        if serializer.is_valid():
            password = data.get('password')
            confirm_password = data.get('confirm_password')
            if password != confirm_password:
                raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        return data'''

    def create(self, validated_data):
        validated_data.pop('confirm_password')  # Supprimer champ de confirmation du mot de passe avant sauvegarde
        validated_data['username'] = validated_data['email']
        return CustomUser.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        if validated_data['password'] == instance.password:
            raise serializers.ValidationError("Vous ne pouvez pas saisir le même mot de passe.")
        instance.password = validated_data.get('password', instance.password)
        instance.birth_day = validated_data.get('birth_day', instance.birth_day)
        instance.save()
        return instance
