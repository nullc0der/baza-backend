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

from authclient.utils import AuthHelperClient

from publicusers.views import make_user_serializeable

from userprofile.models import UserProfile

from proxcdb.models import ProxcAccount, ProxcTransaction
from proxcdb.serializers import ProxcTransactionSerializer
from proxcdb.utils import send_fund_from_proxc_to_real_wallet

# Create your views here.

channel_layer = get_channel_layer()

URL_PROTOCOL = 'http://' if settings.SITE_TYPE == 'local' else 'https://'


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
            ).order_by('-id')
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


class SendFundFromProxcToRealWallet(APIView):
    permission_classes = (IsAuthenticated, TokenHasScope, )
    required_scopes = [
        'baza' if settings.SITE_TYPE == 'production' else 'baza-beta']

    def get(self, request, format=None):
        return Response({
            'balance': request.user.proxcaccount.balance,
            'has_baza_web_wallet': bool(request.user.wallets.count())
        })

    def post(self, request, format=None):
        if request.user.wallets.count():
            # TODO: change this to default wallet address
            to_address = request.user.wallets.all()[0].address
            authhelperclient = AuthHelperClient(
                URL_PROTOCOL +
                settings.CENTRAL_AUTH_INTROSPECT_URL +
                '/authhelper/checkpassword/'
            )
            _, data = authhelperclient.check_user_password(
                request.META['HTTP_AUTHORIZATION'].split(' ')[1],
                request.data['password']
            )
            if data['password_valid']:
                proxcaccount = request.user.proxcaccount
                if proxcaccount.balance >= 5:
                    tx_hash = send_fund_from_proxc_to_real_wallet(
                        proxcaccount, to_address, proxcaccount.balance)
                    if tx_hash:
                        return Response({'transaction_hash': tx_hash})
                    return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    return Response(
                        {'non_field_errors': [
                            'You need to have atleast 5 BAZA to withdraw']},
                        status=status.HTTP_400_BAD_REQUEST)
            return Response(
                {'non_field_errors': [
                    'Please ensure you provided correct password']},
                status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {'non_field_errors': ['You don\'t have a online wallet']},
            status=status.HTTP_400_BAD_REQUEST
        )
