from django.forms import model_to_dict
from ninja import Router
from django.db import transaction
from account.schema import TransferBodyIn
from administration.models import InvestmentPlan
from authentication.models import CustomUser
from server.schema import ErrorOut, ResOut
from transaction.models import Transaction
from .models import Account

router = Router()


@router.get("/invest-details")
def get_investment_details(request):
    try:
        account = Account.objects.get(user__id=request.auth["user"]["id"])
        response = {
            "total_invested": account.total_invested,
            "total_gain": account.total_gain,
        }
        return {"success": True, "data": response}
    except Exception as error:
        return {"success": False, "msg": str(error)}


@router.get("transfer/reciever-info/{email}")
def get_transfer_reciever_email(request, email: str):
    try:
        ownerid = request.auth["user"]["id"]
        user = CustomUser.objects.get(email__iexact=email)
        if user.id == ownerid:
            return {"success": False, "msg": "You cannot transfer to yourself"}
        account = Account.objects.get(user__id=ownerid)
        return {
            "success": True,
            "data": {
                "fullname": user.fullname,
                "email": user.email,
                "image": user.profile_pics.url,
                "available_balance": account.available_balance,
                "balance": account.balance,
                "active": user.is_active,
            },
        }
    except CustomUser.DoesNotExist:
        return {"success": False, "msg": "account not found"}
    except Exception as error:
        print(error)
        return {"success": False, "msg": "unknown server error"}


@router.post("transfer")
@transaction.atomic
def transfer(request, body: TransferBodyIn):
    try:
        userId = request.auth["user"]["id"]
        data = body.dict()
        transfer_account = Account.objects.get(user__id=userId)
        reciever_account = Account.objects.get(user__email__iexact=data["to"])
        tr_acct_dict = model_to_dict(transfer_account)

        if tr_acct_dict[data["source"]] < data["amount"]:
            return {"success": False, "msg": "Insuficient Balance"}
        transfer_account.__setattr__(
            data["source"], tr_acct_dict[data["source"]] - data["amount"]
        )
        reciever_account.balance += data["amount"]
        transaction1 = Transaction(
            user=transfer_account.user,
            type="withdrawal",
            label=f"transfer to {reciever_account.user.fullname}",
            amount=data["amount"],
            channel=data["source"],
        )
        transaction2 = Transaction(
            user=reciever_account.user,
            type="deposit",
            label=f"receive from {transfer_account.user.fullname}",
            channel="balance",
            amount=data["amount"],
        )

        transfer_account.save()
        reciever_account.save()
        transaction1.save()
        transaction2.save()

        # send neccessary email

        return {"success": True}
    except Exception as error:
        print(str(error))
        return {"success": False, "msg": "unknown server error"}


@router.get("balance")
def get_just_balance(request):
    userId = request.auth["user"]["id"]
    try:
        account = Account.objects.get(user__id=userId)
        return {
            "success": True,
            "balance": account.balance,
            "available_balance": account.available_balance,
        }
    except Exception as e:
        print(e)
        return {"success": False, "msg": "Unknown server error, try again later"}


@router.get("profile")
def get_profile(request):
    userId = request.auth["user"]["id"]
    try:
        user = CustomUser.objects.get(id=userId)
        account = Account.objects.get(user__id=userId)
        return {
            "success": True,
            "fullname": user.fullname,
            "email": user.email,
            "image": user.profile_pics.url if user.profile_pics else None,
            "available_balance": account.available_balance,
        }
    except Exception as e:
        print(e)
        return {"success": False}
