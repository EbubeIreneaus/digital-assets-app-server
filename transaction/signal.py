from decimal import Decimal
from django.forms import model_to_dict
from account.models import Account


def transaction_signal_handling(instance):
    type= instance.type
    user = instance.user
    amount = instance.amount
    status = instance.status
    channel = instance.channel
    account = Account.objects.get(user=user)
    
    if type == 'deposit' and status == 'successful':
        from .views import sendCreditAlert
        try:
            account.balance += amount
            account.save()
            sendCreditAlert(instance)
        except Exception as error:
            pass
    
    elif type == 'withdraw' and status == 'successful':
        from .views import sendDebitAlert
        if hasattr(account, channel):
            current_channel_amount = getattr(account, channel)
            if isinstance(current_channel_amount, (float,int, Decimal)):
                 if current_channel_amount >= amount:
                     setattr(account, channel, current_channel_amount - amount)
                     sendDebitAlert(instance)
                     account.save()
            
        
        