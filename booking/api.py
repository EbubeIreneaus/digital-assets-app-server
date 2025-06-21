from ninja import Router

from authentication.models import CustomUser
from booking.models import Flight, Visa
from booking.schema import FlightSchemaIn, VisaSchemaIn

router = Router()

@router.post('/flight')
def create_flight(request, body: FlightSchemaIn):
    try:
        userId = request.auth['user']['id']
        data = body.dict()
        user = CustomUser.objects.get(id=userId)
        flight = Flight.objects.create(**data, user=user)
        return {"success": True}
    except Exception as error:
        print(error)
        return {"success": False, 'msg': 'Unknown server error occured'}

@router.post('/visa')
def create_visa(request, body: VisaSchemaIn):
    try:
        userId = request.auth['user']['id']
        data = body.dict()
        if not data['confirm']:
            return {'status': False, 'msg': 'Please confirm all information are correct'}
        del data['confirm']
        user = CustomUser.objects.get(id=userId)
        Visa.objects.create(**data, user=user)
        return {"success": True}
    except Exception as error:
        print(error)
        return {"success": False, 'msg': 'Unknown server error occured'}
    