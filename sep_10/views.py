import os
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from stellar_sdk import Keypair
from stellar_sdk import TransactionEnvelope as te
from .serializers import SignTxnSerializer


@api_view(["POST"])
def sign_txn(request):
    try:
        serializer = SignTxnSerializer(data=request.data)
        if serializer.is_valid():
            seed = os.environ.get('SIGNING_SEED')
            NETWORK_PASSPHRASE = os.environ.get('STELLAR_NETWORK_PASSPHRASE')
            # keypair = Keypair.from_secret(seed)
            s_te = te.from_xdr(serializer.data["transaction"], NETWORK_PASSPHRASE)
            s_te.sign(seed)
            response = s_te.to_xdr()
            return Response(response,
                            status=status.HTTP_200_OK)
        return Response({"data": serializer.errors,
                         "message": "Request Data Missing"},
                        status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"data": str(e),
                         "message": "Error from Server"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
