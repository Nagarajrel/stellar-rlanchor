from rest_framework import serializers


class SignTxnSerializer(serializers.Serializer):
    transaction = serializers.CharField(required=True)
