from django.utils import timezone
from datetime import timedelta
from django.forms import model_to_dict
from ninja import Router
from ninja.responses import codes_5xx
from account.models import Account
from administration.models import InvestmentPlan
from authentication.models import CustomUser
from investment.models import Investment
from server.schema import ResOut
from transaction.models import Transaction
from django.db import transaction
from .schema import (
    BuyPlanIn,
    ErrorOut,
    GetPlansOut,
    MyPlanOut,
    SellPlanIn,
    SwapPlanIn,
    TradingPlanOutSchema,
)

router = Router()
from functools import reduce
from django.core.mail import send_mail


@router.get("/trading-plan", response={200: TradingPlanOutSchema, 500: ErrorOut})
def get_investment_details(request):
    try:
        account = Account.objects.get(user__id=request.auth["user"]["id"])
        plans = InvestmentPlan.objects.all()
        return 200, {"success": True, "account": account, "plans": plans}
    except Exception as error:
        return 500, {"success": False, "msg": str(error)}


@router.get("/plans", response={200: GetPlansOut, 500: ErrorOut}, auth=None)
def get_plans(request):
    try:
        plans = InvestmentPlan.objects.values()
        return 200, {"success": True, "plans": plans}
    except Exception as error:
        return 500, {"success": False, "msg": str(error)}


@router.get("/plan/{plan}", response={200: MyPlanOut, 500: ErrorOut})
def get_plan(request, plan: str):
    try:
        userID = request.auth["user"]["id"]
        plan = InvestmentPlan.objects.get(name__iexact=plan)
        balance = 0
        transactions = Transaction.objects.filter(
            user__id=userID, type=plan.name
        ).order_by("-id")

        investments = Investment.objects.filter(user__id=userID, plan=plan)

        if len(investments) >= 1:
            balance = sum(inv.amount for inv in investments)

        return 200, {
            "success": True,
            "balance": balance,
            "plan": plan,
            "transactions": transactions,
        }
    except Exception as error:
        return 500, {"success": False, "msg": str(error)}


@router.post("/buy-plan", response={200: ResOut, 400: ErrorOut, 500: ErrorOut})
@transaction.atomic
def buy_plan(request, body: BuyPlanIn):
    try:
        data = body.dict()
        amount = float(data["amount"])
        userId = request.auth["user"]["id"]
        user = CustomUser.objects.get(id=userId)
        account = Account.objects.select_for_update().get(user__id=userId)
        account_dict = model_to_dict(account)
        plan = InvestmentPlan.objects.get(name__iexact=data["planName"])
        if account.balance < data["amount"]:
            return 400, {"success": False, "msg": "insufficient Balance"}

        next_roi_return = timezone.now() + timedelta(hours=24)

        investment = Investment(
            amount=data["amount"], user=user, plan=plan, next_roi_date=next_roi_return
        )

        account.balance = account.balance - data["amount"]
        account.total_invested = account.total_invested + data["amount"]

        transaction = Transaction(
            type=data["planName"],
            amount=data["amount"],
            user=user,
            channel="balance",
            label=f"purchase of {plan.label.upper()} plan",
            status='successful'
        )

        account.save()
        investment.save()
        transaction.save()

        try:
            # send email
            subject = "Investment Plan Purchase"
            message = f"""
                New Investment Plan Purchase

                {user.fullname} just purchased a {plan.label.upper()} plan
                Amount: ${amount}
                Date: {timezone.now()}
                Ref: {transaction.id}

                Kindly visit admin dashboard to update Investment status
            """
            send_mail(
                subject = subject,
                message = message,
                from_email = settings.DEFAULT_FROM_EMAIL,
                recipient_list = ['service@digitalassetsweb.com', 'alfredebube7@gmail.com']
            )
        except:
            pass
        return 200, {"success": True}
    except Exception as error:
        return 500, {"success": False, "msg": "unkown server error"}


@router.post("/sell-plan", response={200: ResOut, 400: ErrorOut, 500: ErrorOut})
@transaction.atomic
def sell_plan(request, body: SellPlanIn):
    try:
        data = body.dict()
        userId = request.auth["user"]["id"]
        plan = InvestmentPlan.objects.get(name__iexact=data["plan"])
        amount = data["amount"]
        to = data["to"]
        user = CustomUser.objects.get(id=userId)
        account = Account.objects.get(user__id=userId)
        investments = Investment.objects.filter(
            plan__name=plan.name, user__id=userId
        ).order_by("id")

        total_shares = sum(inv.amount for inv in investments)

        if amount > total_shares:
            return 400, {"success": False, "msg": "insufficient shares funds"}

        tf_amount = amount
        for investment in investments:
            if tf_amount <= 0:
                break
            elif tf_amount >= investment.amount:
                tf_amount = tf_amount - investment.amount
                investment.delete()
            else:
                investment.amount = investment.amount - tf_amount
                investment.save()
                tf_amount = 0

        account.__setattr__(to, amount)
        account.save()
        transaction = Transaction(
            type=data["plan"],
            amount=data["amount"],
            user=user,
            channel=to,
            label=f"sale of {plan.label.lower()} shares",
            status='successful'
        )
        transaction.save()

        try:
            # send email
            subject = "Investment Plan Sale"
            message = f"""
                New Plan Sales Request

                {user.fullname} just sold {amount} shares of {plan.label.upper()} plan

                Date: {timezone.now()}
                Ref: {transaction.id}

                Kindly visit admin dashboard to update investment status
            """
            send_mail(
                subject = subject,
                message = message,
                from_email = settings.DEFAULT_FROM_EMAIL,
                recipient_list = ['service@digitalassetsweb.com', 'alfredebube7@gmail.com']
            )
        except:
            pass

        return 200, {"success": True}
    except Exception as error:
        print(error)
        return 500, {"success": False, "msg": "unknown server error"}


@router.post("/swap-plan", response={200: ResOut, 400: ErrorOut, 500: ErrorOut})
@transaction.atomic
def swap_plan(request, body: SwapPlanIn):
    try:
        userId = request.auth["user"]["id"]
        data = body.dict()
        source = data["source"]
        destination = data["destination"]
        amount = data["amount"]
        user = CustomUser.objects.get(id=userId)
        source_plan = InvestmentPlan.objects.get(name=source)
        dest_plan = InvestmentPlan.objects.get(name=destination)
        source_investments = Investment.objects.filter(
            plan__name=source, user=user
        ).order_by("id")

        source_total_value = sum(inv.amount for inv in source_investments)
        if source.lower() == destination.lower():
            return 400, {
                "success": False,
                "msg": "Source and destination plans cannot be the same",
            }

        if amount > source_total_value:
            return 400, {
                "success": False,
                "msg": f"Insuffucient {source} shares value".title(),
            }

        source_remaining = amount
        for source_inv in source_investments:
            if source_remaining <= 0:
                break
            elif source_inv.amount <= source_remaining:
                source_remaining = source_remaining - source_inv.amount
                source_inv.delete()
            else:
                source_inv.amount = source_inv.amount - source_remaining
                source_inv.save()
                source_remaining = 0

        next_roi_return = timezone.now() + timedelta(hours=24)
        dest_investment = Investment(
            user=user, plan=dest_plan, amount=amount, next_roi_date=next_roi_return
        )
        source_transaction = Transaction(
            type=source,
            amount=amount,
            user=user,
            channel=source,
            label=f"sales of {source_plan.label} shares",
            status='successful'
        )
        dest_transaction = Transaction(
            type=destination,
            amount=amount,
            user=user,
            channel=destination,
            label=f"purchase of {dest_plan.label} plan",
            status='successful'
        )
        dest_investment.save()
        source_transaction.save()
        dest_transaction.save()

        try:
            # send email
            subject = "Investment Plan Swap"
            message = f"""
                New Investment Plan Swap

                {user.fullname} just swapped a {source_plan.label.upper()} plan to {dest_plan.label.upper()} plan
                Amount: ${amount}
                Date: {timezone.now()}
                Ref: {transaction.id}

                Kindly visit admin dashboard to see investment status
            """
            send_mail(
                subject = subject,
                message = message,
                from_email = settings.EMAIL_HOST_USER,
                recipient_list = ['service@digitalassetsweb.com', 'alfredebube7@gmail.com']
            )
        except:
            pass

        return 200, {"success": True}
    except Exception as error:
        print(error)
        return 500, {"success": False, "msg": "unknown server error"}
