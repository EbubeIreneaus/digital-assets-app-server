from django.utils import timezone
from datetime import timedelta
from django.forms import model_to_dict
from ninja import Router
from ninja.responses import codes_5xx
from account.models import Account
from administration.models import InvestmentPlan
from authentication.models import CustomUser
from investment.models import Investment
from server.schema import ResOut
from transaction.models import Transaction
from django.db import transaction
from .schema import BuyPlanIn, ErrorOut, GetPlansOut, MyPlanOut, TradingPlanOutSchema
router = Router()


@router.get('/trading-plan', response={200: TradingPlanOutSchema, 500: ErrorOut})
def get_investment_details(request):
    try:
        account = Account.objects.get(user__id=request.auth['user']['id'])
        plans = InvestmentPlan.objects.all()
        return 200, {'success': True, 'account': account, 'plans': plans}
    except Exception as error:
        return 500, {'success': False, 'msg': str(error)}

@router.get('/plans', response={200: GetPlansOut, 500: ErrorOut}, auth=None)
def get_plans(request):
    try:
        plans = InvestmentPlan.objects.values()
        return 200, {'success': True, 'plans': plans}
    except Exception as error:
        return 500, {"success": False, "msg": str(error)}


@router.get('/plan/{plan}', response={200: MyPlanOut, 500: ErrorOut})
def get_plan(request, plan: str):
    try:
        userID = request.auth['user']['id']
        plan = InvestmentPlan.objects.get(name__iexact=plan)
        account_model = Account.objects.get(user__id=userID)
        account = model_to_dict(account_model)
        transactions = Transaction.objects.filter(
            user__id=userID, type=plan.name)
        return 200, {'success': True, 'account': {'balance': account['balance'], 'planBalance': account[plan.name]}, 'plan': plan, 'transactions': transactions}
    except Exception as error:
        return 500, {"success": False, "msg": str(error)}


@router.post('/buy-plan', response={200:ResOut,400: ErrorOut, 500: ErrorOut})
@transaction.atomic
def buy_plan(request, body: BuyPlanIn):
    try:
        data = body.dict()
        amount = float(data['amount'])
        userId = request.auth['user']['id']
        user = CustomUser.objects.get(id=userId)
        account = Account.objects.select_for_update().get(user__id=userId)
        account_dict = model_to_dict(account)
        plan = InvestmentPlan.objects.get(name__iexact=data['planName'])
        if account.balance < data['amount']:
            return 400, {'success': False, 'msg': 'insufficient Balance'}
        
        next_roi_return = timezone.now() + timedelta(hours=24)
        
        investment = Investment(
            amount=data['amount'], user=user, plan=plan, next_roi_date=next_roi_return)
    
        account.balance = account.balance - data['amount']
        account.total_invested = account.total_invested + data['amount']
        account.__setattr__(
            data['planName'], account_dict[plan.name] + data['amount'])

        transaction = Transaction(
            type=data['planName'], amount=data['amount'], user=user, channel='balance', label=f"purchase of {plan.label.upper()} plan")
        
        account.save()
        investment.save()
        transaction.save()
        return 200, {'success': True}
    except Exception as error:
        return 500, {'success': False, 'msg': 'unkown server error'}

