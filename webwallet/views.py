import logging

from django.conf import settings

from rest_framework import views
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from oauth2_provider.contrib.rest_framework import TokenHasScope

from webwallet.api_wrapper import ApiWrapper
from webwallet.serializers import (
    UserWebWalletSerializer, UserWebWalletTxSerializer)
from webwallet.models import UserWebWallet
from webwallet.permissions import IsOwnerOfWallet

logger = logging.getLogger(__name__)


class UserWebWalletView(views.APIView):
    """
    This API will create a subwallet for the request.user
    """
    permission_classes = (IsAuthenticated, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def get(self, request, format=None):
        serializer = UserWebWalletSerializer(
            request.user.wallets.all(), many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = UserWebWalletSerializer(data=request.data)
        if serializer.is_valid():
            apiwrapper = ApiWrapper()
            res = apiwrapper.create_subwallet()
            if res.status_code == 201:
                data = res.json()
                userwebwallet = serializer.save(
                    address=data['address'], user=request.user)
                data['name'] = userwebwallet.name
                return Response(data, res.status_code)
            return Response(
                {'status': 'failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserWebWalletDetailsView(views.APIView):
    """
    This API will return all details about selected subwallet
    """
    permission_classes = (IsAuthenticated, TokenHasScope, IsOwnerOfWallet, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def get(self, request, format=None):
        data = {}
        userwebwallet = UserWebWallet.objects.get(
            id=request.query_params['id'])
        self.check_object_permissions(request, userwebwallet)
        apiwrapper = ApiWrapper()
        balance_res = apiwrapper.get_subwallet_balance(userwebwallet.address)
        tx_res = apiwrapper.get_subwallet_transactions(userwebwallet.address)
        if balance_res.status_code == 200 and tx_res.status_code == 200:
            data['balance'] = balance_res.json()
            data['transactions'] = tx_res.json()['transactions']
            return Response(data)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserWebWalletTxView(views.APIView):
    """
    This API will send a transaction to user specified address
    """
    permission_classes = (IsAuthenticated, TokenHasScope, IsOwnerOfWallet, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def post(self, request, format=None):
        serializer = UserWebWalletTxSerializer(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            apiwrapper = ApiWrapper()
            res = apiwrapper.send_subwallet_transaction(
                serializer.validated_data['destination_address'],
                serializer.validated_data['source_address'],
                serializer.validated_data['amount']
            )
            if res.status_code == 200:
                data = res.json()
                return Response({
                    'transaction_hash': data['transactionHash']
                })
            logger.warning(res.content)
            logger.warning(res.content)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
