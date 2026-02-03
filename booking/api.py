from ninja import Router
from django.utils.dateparse import parse_datetime
from authentication.models import CustomUser
from booking.models import Flight, Visa
from booking.schema import FlightSchemaIn, VisaSchemaIn
from django.utils import timezone

router = Router()

@router.post('/flight')
def create_flight(request, body: FlightSchemaIn):
    try:
        userId = request.auth['user']['id']
        data = body.dict()
        user = CustomUser.objects.get(id=userId)
        departure = parse_datetime(data['departure_date'])
        if departure is None:
            raise ValueError("Invalid departure_date format")

        if timezone.is_naive(departure):
            departure = timezone.make_aware(departure)

        arrival = None
        if data.get('arrival_date'):
            arrival = parse_datetime(data['arrival_date'])
            if timezone.is_naive(arrival):
                arrival = timezone.make_aware(arrival)
        data['departure_date'] = departure
        data['arrival_date'] = arrival
        Flight.objects.create(**data, user=user)
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
    