from django.db.models import Q
from django.conf import settings

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from oauth2_provider.contrib.rest_framework import TokenHasScope
from oauth2_provider.decorators import protected_resource

from publicusers.views import make_user_serializeable

from userprofile.models import UserProfile

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
            to_user = UserProfile.objects.get(
                Q(username=request.data.get('username')) |
                Q(user__username=request.data.get('username'))
            ).user
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
        except UserProfile.DoesNotExist:
            return Response(
                {'nonField': 'No such user'},
                status=status.HTTP_400_BAD_REQUEST)


@api_view()
@permission_classes([IsAuthenticated, ])
@protected_resource(scopes=[
    'baza' if settings.SITE_TYPE == 'production' else 'baza-beta'])
def proxcdb_account_autocomplete(request):
    data = []
    query = request.query_params.get('username')
    proxcaccounts = ProxcAccount.objects.filter(
        Q(user__profile__username__istartswith=query) |
        Q(user__username__istartswith=query)
    ).exclude(user=request.user).exclude(user__username='system')
    for proxcaccount in proxcaccounts:
        data.append({
            'label': proxcaccount.user.profile.username
            or proxcaccount.user.username,
            'value': proxcaccount.user.profile.username
            or proxcaccount.user.username,
            'user': make_user_serializeable(proxcaccount.user)
        })
    return Response(data)
