from rest_framework import serializers

from tests.test_app.models import Model1


class Model1Serializer(serializers.ModelSerializer):
    class Meta:
        model = Model1
        fields = ('id', 'int_field', 'char_field', )
