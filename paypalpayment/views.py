from rest_framework import views
from rest_framework import status
from rest_framework.response import Response

from paypalpayment import utils


class CreatePaymentView(views.APIView):
    """
    This view will be used to create a paypal payment
    """

    def post(self, request, format=None):
        create_payment_success = utils.create_payment(request.data['amount'])
        if create_payment_success:
            return Response({'id': create_payment_success})
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExecutePaymentView(views.APIView):
    """
    This view will be used to execute a paypal payment
    """

    def post(self, request, format=None):
        execute_payment_success = utils.execute_payment(
            request.data['payment_id'], request.data['payer_id'])
        if execute_payment_success:
            return Response()
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
