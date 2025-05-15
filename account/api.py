from django.forms import model_to_dict
from ninja import Router
from django.db import transaction
from account.schema import SellPlanIn, SwapPlanIn
from administration.models import InvestmentPlan
from authentication.models import CustomUser
from server.schema import ErrorOut, ResOut
from transaction.models import Transaction
from .models import Account
router = Router()

@router.get('/invest-details')
def get_investment_details(request):
    try:
        account =  Account.objects.get(user__id=request.auth['user']['id'])
        response = {'total_invested': account.total_invested, 'total_gain':account.total_gain }
        return {'success': True, 'data': response}
    except Exception as error:
        return {'success': False, 'msg': str(error)}

@router.post('/sell-plan', response={200: ResOut, 400: ErrorOut, 500: ErrorOut})
@transaction.atomic
def sell_plan(request, body: SellPlanIn):
    try:
        data = body.dict()
        userId = request.auth['user']['id']
        account = Account.objects.select_for_update().get(user__id=userId)
        plan = InvestmentPlan.objects.get(name__iexact=data['plan'])
        user = CustomUser.objects.get(id=userId)
        account_dict = model_to_dict(account)
        if account_dict[data['plan']] < data['amount']:
            return 400, {"success": False, 'msg': f'Insufficien {plan.label} Balance'}
        account.__setattr__(data['plan'], account_dict[data['plan']] - data['amount'])
        account.__setattr__(data['to'], account_dict[data['to']] + data['amount'])
        transaction = Transaction(
            type=data['plan'], amount=data['amount'], user=user, channel='balance', label=f"sale of {plan.label.lower()} shares")
        account.save()
        transaction.save()
        return 200, {'success': True}
    except Exception as error:
        print(error)
        return 500, {'success': False, 'msg': 'unknown server error'}
    
    
@router.post('/swap-plan', response={200: ResOut, 400: ErrorOut, 500: ErrorOut})
@transaction.atomic
def swap_plan(request, body: SwapPlanIn):
    try:
        userId = request.auth['user']['id']
        data = body.dict()
        user = CustomUser.objects.get(id=userId)
        account = Account.objects.select_for_update().get(user__id=userId)
        account_dict = model_to_dict(account)
        plan = InvestmentPlan.objects.get(name__iexact=data['source'])
        if account_dict[data['source']] < data['amount']:
            return 400, {'success': False, 'msg': f'Insufficien {plan.label} Balance'}
        account.__setattr__(data['source'], account_dict[data['source']] - data['amount'])
        account.__setattr__(data['destination'], account_dict[data['source']] + data['amount'])
        transaction = Transaction(
            type=data['destination'], amount=data['amount'], user=user, channel=data['source'], label=f"recieve shares from {plan.label}")
        account.save()
        transaction.save()
        return 200, {'success': True}
    except Exception as error:
        print(error)
        return 500, {'success': False, 'msg': 'unknown server error'}