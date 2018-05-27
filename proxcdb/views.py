from django.db.models import Q
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from proxcdb.models import ProxcAccount, ProxcTransaction
from proxcdb.serializers import ProxcTransactionSerializer

# Create your views here.


class ProxcTransactionView(APIView):
    permission_classes = (IsAuthenticated, )

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
                    transaction.save(
                        account=request.user.proxcaccount,
                        to_account=to_user.proxcaccount
                    )
                    return Response(transaction.data)
                return Response(transaction.errors,
                                status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response(
                {'nonField': 'No such user'},
                status=status.HTTP_400_BAD_REQUEST)


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
