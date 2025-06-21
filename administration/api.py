from django.forms import model_to_dict
from ninja import Router

from administration.schema import ChannelSchemaOut
from authentication.schema import ErrorOut
from .models import CryptoChannel, SupportChannel

router = Router()

@router.get('/crypto-channels', response={200: ChannelSchemaOut, 500: ErrorOut})
def get_crypto_channels(request):
    try:
        channels = CryptoChannel.objects.values()
        return 200, {'success': True, 'data': channels}
    except Exception as error:
        return 500, {'success': False, 'msg': str(error)}

@router.get("/support")
def get_support_channel(request):
    try:
        support_channel= SupportChannel.objects.all().last()
        return {"success": True, "data": model_to_dict(support_channel), 'liveChat': 'https://digitalassetsweb.com/support-agent.html'}
    except Exception as error:
        return {'success': False, 'msg': str(error)}
