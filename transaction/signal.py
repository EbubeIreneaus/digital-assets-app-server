from decimal import Decimal
from django.forms import model_to_dict
from account.models import Account
from authentication.models import CustomUser
import logging
logger = logging.getLogger(__name__)


def transaction_signal_handling(instance):
    type = instance.type
    user = instance.user
    amount = instance.amount
    status = instance.status
    channel = instance.channel
    account = Account.objects.get(user=user)

    if type == "deposit" and status == "successful":
        from .views import sendCreditAlert
        from transaction.models import Transaction

        try:
            account.balance += amount
            account.save()
            sendCreditAlert(instance)
            if user.referred_by and not user.has_first_deposit:
                bonus = amount * Decimal("0.05")
                user_model = CustomUser.objects.get(id=user.id)
                r_account = Account.objects.get(user=user_model.referred_by)
                r_account.balance += bonus
                Transaction.objects.create(
                    user=user_model.referred_by,
                    amount=bonus,
                    label="Referral bonus",
                    status="successful",
                    type='deposit',
                    channel='Referral Bonus'
                )
                r_account.save()
                user_model.has_first_deposit = True
                user_model.save(update_fields=["has_first_deposit"])
        except Exception as error:
            logger.exception("Referral bonus processing failed")

    elif type == "withdraw" and status == "successful":
        from .views import sendDebitAlert

        if hasattr(account, channel):
            current_channel_amount = getattr(account, channel)
            if isinstance(current_channel_amount, (float, int, Decimal)):
                if current_channel_amount >= amount:
                    setattr(account, channel, current_channel_amount - amount)
                    sendDebitAlert(instance)
                    account.save()
