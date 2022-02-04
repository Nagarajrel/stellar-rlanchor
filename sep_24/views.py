import os
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from stellar_sdk import Keypair
from stellar_sdk import TransactionEnvelope as te
from .info import sep24_info
from .serializers import SignTxnSerializer


@api_view(["GET"])
def info(request):
    serializer = SignTxnSerializer(data=request.data)
    try:
        return sep24_info()
    except Exception as e:
        return Response({"data": str(e),
                         "message": "Error from Server"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)