from ninja import Router

from administration.schema import ChannelSchemaOut
from authentication.schema import ErrorOut
from .models import CryptoChannel

router = Router()

@router.get('/crypto-channels', response={200: ChannelSchemaOut, 500: ErrorOut})
def get_crypto_channels(request):
    try:
        channels = CryptoChannel.objects.values()
        return 200, {'success': True, 'data': channels}
    except Exception as error:
        return 500, {'success': False, 'msg': str(error)}