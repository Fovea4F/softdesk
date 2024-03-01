from rest_framework import serializers
# from rest_framework.response import Response
from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'}, required=False)
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'}, required=False)

    class Meta:
        model = CustomUser
        fields = ['email', 'birth_day', 'can_be_shared', 'can_be_contacted', 'password', 'confirm_password',]

        '''def validate(self, data):
            confirm_password = data['confirm_password']
            del data['confirm_password']
            if data['password'] and confirm_password:
                if data['password'] != confirm_password:
                    raise serializers.ValidationError('error: passwords do not match !')
                return data'''

        def create(self, validated_data):
            validated_data.pop('confirm_password')  # Supprimer champ de confirmation du mot de passe avant sauvegarde
            validated_data['username'] = validated_data['email']
            return CustomUser.objects.create_user(**validated_data)

        '''def create(self, validated_data):
            user = CustomUser.objects.create(
                                            email=validated_data['email'],
                                            username=validated_data['email'],
                                            birth_day=validated_data['birth_day'],
                                            can_be_contacted=validated_data['can_be_contacted'],
                                            can_be_shared=validated_data['can_be_shared'],
                                            )
            user.set_password(self.validated_data['password'])
            user.save()
            return user'''

        def update(self, instance, validated_data):
            if validated_data['password'] == instance.password:
                raise serializers.ValidationError("Vous ne pouvez pas saisir le même mot de passe.")
            instance.password = validated_data['password']
            instance.birth_day = validated_data.get('birth_day', instance.birth_day)
            instance.save()
            return instance
