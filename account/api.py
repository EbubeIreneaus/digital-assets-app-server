from ninja import Router
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