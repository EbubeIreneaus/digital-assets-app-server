from decimal import Decimal
from django.forms import model_to_dict
from account.models import Account
from authentication.models import CustomUser
import logging
logger = logging.getLogger(__name__)


def transaction_signal_handling(instance):
    _type = instance.type
    user = instance.user
    amount = instance.amount
    status = instance.status
    channel = instance.channel
    account = Account.objects.get(user=user)

    if _type == "deposit" and status == "successful":
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

    elif _type == "withdraw" and status == "successful":
        print({"Reached here"})
        from .views import sendDebitAlert
        try:
            account.available_balance -= amount
            account.save()
            sendDebitAlert(instance)
        except Exception as error:
            print(error)
            logger.exception("Withdrawal processing failed")

def swap_handling(instance):
    source = instance.source
    destination = instance.destination
    amount = instance.amount
    user = instance.user
    account = Account.objects.get(user=user)

    if instance.status == "successful":
        if source == "balance" and destination == "available":
            account.balance -= amount
            account.available_balance += amount
            account.save()
        elif source == "available" and destination == "balance":
            account.available_balance -= amount
            account.balance += amount
            account.save()
    elif instance.status == "failed":
        pass
    
    
