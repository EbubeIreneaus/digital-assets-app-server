from ninja import NinjaAPI
from ninja.security import HttpBearer
from ninja.errors import ValidationError
from authentication.api import router as AuthRouter
from django.http import JsonResponse
from account.models import Account
from authentication.models import CustomUser
from authentication.schema import ErrorOut
from .schema import DashboardDataSchema

from extras.jwt import JwtVerify

def custom_validation_exception(request, exc: ValidationError):
    # Extract and format the first error message
    first_error = exc.errors[0]
    field = first_error["loc"][-1]
    msg = first_error["msg"]
    
    return JsonResponse({"msg": f"{field}: {msg}"}, status=422)

class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        if not token:
            return False
        return JwtVerify(token)
    
api = NinjaAPI(auth=AuthBearer())

api.add_exception_handler(ValidationError, custom_validation_exception)

api.add_router('auth/', AuthRouter, auth=None)
api.add_router('admin/', 'administration.api.router', auth=None)
api.add_router('transaction/', 'transaction.api.router')
api.add_router('account/', 'account.api.router')

@api.get('/db-data', response={200: DashboardDataSchema, 500: ErrorOut})
def get_dashboard_data(request):
    try:
        userId = request.auth['user']['id']
        user = CustomUser.objects.get(id=userId)
        account = Account.objects.get(user__id=userId)
        return 200, {'success': True, 'account': account, 'user': user}
    except Exception as error:
        return 500, {'success': False, 'msg': str(error)}