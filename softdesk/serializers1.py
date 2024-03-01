from rest_framework import serializers
# from rest_framework.response import Response

from .models import CustomUser


class CustomUserListSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(style={'input_type': 'password'}, required=True, write_only=True)
    # password = serializers.CharField(write_only=False, style={'input_type': 'password'}, required=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'birth_day', 'can_be_contacted',
                  'can_be_shared', 'password', 'confirm_password']
        extra_kwargs = {'password': {'write_only': True},
                        'confirm_password': {'write_only': True}
                        }

        password = ''

        def save(self, validated_data):
            if (validated_data['password'] != '') and (validated_data['confirm_password'] != ''):
                confirm_password = validated_data.pop('confirm_password')
                password = validated_data.pop('password')
                if password != confirm_password:
                    raise serializers.ValidationError({'Error': 'Password do not match'})
                return password

            if self.validated_data['email']:
                if CustomUser.objects.filter(email=self.validated_data['email']).exists():
                    raise serializers.ValidationError({'Error': 'Email already registered !'})

            if not self.validated_data['can_be_contacted']:
                can_be_contacted = False
            else:
                can_be_contacted = True

            if not self.validated_data['can_be_shared']:
                can_be_shared = False
            else:
                can_be_shared = True

            user = CustomUser(email=self.validated_data['email'],
                              username=self.validated_data['email'],
                              can_be_contacted=can_be_contacted,
                              can_be_shared=can_be_shared
                              )

            if password != '':
                user.set_password(password)

            user.save()

            return user


class CustomUserDetailSerializer1(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'birth_day', 'can_be_contacted',
                  'can_be_shared', 'password', 'confirm_password']


class CustomUserDetailSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(style={'input_type': 'password'}, required=False, write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'birth_day', 'can_be_contacted',
                  'can_be_shared', 'password', 'confirm_password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def update(self):
        confirm_password = self.validated_data['confirm_password']
        password = self.validated_data['password']

        if password and confirm_password:
            if password != confirm_password:
                raise serializers.ValidationError({'Error': 'Password do not match'})

        if CustomUser.objects.filter(email=self.validated_data['email']).exists():
            raise serializers.ValidationError({'Error': 'Email already registered !'})

        if self.validated_data['birth_day'] == '':
            raise serializers.ValidationError({'Error': 'BirthDay is not valid'})

        user = CustomUser(
            email=self.validated_data['email'],
            username=self.validated_data['email'],
            birth_day=self.validated_data['birth_day'],
            can_be_contacted=self.validated_data['can_be_contacted'],
            can_be_shared=self.validated_data['can_be_shared'],
            )

        user.set_password(password)
        user.save()

        return user

    def partial_update(self):
        print('toto')
        pass


class CustomUserCreateSerializer(serializers.ModelSerializer):

    pass
