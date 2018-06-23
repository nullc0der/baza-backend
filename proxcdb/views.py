from django.db.models import Q
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from oauth2_provider.contrib.rest_framework import TokenHasScope

from proxcdb.models import ProxcAccount, ProxcTransaction
from proxcdb.serializers import ProxcTransactionSerializer

# Create your views here.

channel_layer = get_channel_layer()


class ProxcTransactionView(APIView):
    permission_classes = (IsAuthenticated, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def get(self, request, format=None):
        wallet_id = request.query_params.get('wallet_id', None)
        if int(wallet_id) == 1:
            proxcaccount = request.user.proxcaccount
            transactions = ProxcTransaction.objects.filter(
                Q(account=proxcaccount) |
                Q(to_account=proxcaccount)
            )
            serialized_transactions = ProxcTransactionSerializer(
                transactions, many=True).data
            return Response(serialized_transactions)
        else:
            return Response([])

    def post(self, request, format=None):
        try:
            to_user = User.objects.get(username=request.data.get('username'))
            if to_user == request.user:
                return Response(
                    {'nonField': 'Can\'t send to self'},
                    status=status.HTTP_400_BAD_REQUEST)
            else:
                transaction = ProxcTransactionSerializer(
                    data=request.data,
                    context={'proxcaccount': request.user.proxcaccount}
                )
                if transaction.is_valid():
                    totalamount = transaction.validated_data.get(
                        'amount') + 0.01
                    transaction.save(
                        account=request.user.proxcaccount,
                        to_account=to_user.proxcaccount,
                        amount=totalamount
                    )
                    async_to_sync(channel_layer.group_send)(
                        'notifications_for_%s' % to_user.username,
                        {
                            'type': 'notification.message',
                            'message': {
                                'type': 'proxcdb-transaction',
                                'data': transaction.data
                            }
                        }
                    )
                    return Response(transaction.data)
                return Response(transaction.errors,
                                status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response(
                {'nonField': 'No such user'},
                status=status.HTTP_400_BAD_REQUEST)


# TODO: Add required scopes here
@api_view()
@permission_classes([IsAuthenticated, ])
def proxcdb_account_autocomplete(request):
    data = []
    query = request.query_params.get('username')
    proxcaccounts = ProxcAccount.objects.filter(
        user__username__istartswith=query
    )
    for proxcaccount in proxcaccounts:
        if not proxcaccount.user == request.user:
            data.append({
                'label': proxcaccount.user.username,
                'value': proxcaccount.user.username
            })
    return Response(data)
