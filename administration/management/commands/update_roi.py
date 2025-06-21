from decimal import Decimal
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from account.models import Account
from authentication.models import CustomUser
from investment.models import Investment
from django.core.mail import send_mail
from django.db.models import Prefetch
from django.db import transaction
from datetime import timedelta

from transaction.models import Transaction


class Command(BaseCommand):
    help = "Update Investment Returns"

    def handle(self, *args, **options):
        with transaction.atomic():
            today = timezone.now()
            try:
                users = CustomUser.objects.prefetch_related(
                    Prefetch(
                        "investments",
                        queryset=Investment.objects.filter(next_roi_date__lt=today),
                        to_attr="overdue_investments",
                    )
                )

                for user in users:
                    if not user.overdue_investments:
                        continue

                    accumulated_roi = 0
                    accumulated_roi_per_plan = {}

                    for investment in user.overdue_investments:
                        roi = roi = investment.amount * (Decimal(investment.plan.roi) / Decimal("100"))
                        next_date = investment.next_roi_date + timedelta(hours=24)

                        try:
                            investment.next_roi_date = next_date
                            investment.amount += roi
                            investment.save()

                            accumulated_roi += roi
                            accumulated_roi_per_plan[investment.plan] = (
                                accumulated_roi_per_plan.get(investment.plan, 0) + roi
                            )
                        except Exception as ie:
                            self.stdout.write(
                                self.style.ERROR(
                                    f"Could not update Investment {investment.id} for user {user.email} {str(ie)}"
                                )
                            )

                    if accumulated_roi == 0:
                        continue

                    try:
                        account = Account.objects.get(user=user)
                        account.Total_earnings = account.Total_earnings + accumulated_roi
                        account.save()
                    except Exception as acc_exc:
                        self.stdout.write(self.style.ERROR(
                            f"Account update failed for {user.email}: {acc_exc}"
                        ))

                    try:
                        for planName, planAmount in accumulated_roi_per_plan.items():
                            Transaction.objects.create(
                                user=user,
                                amount=planAmount,
                                type=planName.name.lower(),
                                channel=planName.name.lower(),
                                label=f'Return on {planName.name} shares',
                                status='successful'
                            )
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error Creating transactions: {str(e)}'))

                    try:
                        plain_message = "Today's Return on Investment:\n"
                        for plan, roi_amount in accumulated_roi_per_plan.items():
                            plain_message += f"{plan.name}: ${roi_amount:,.2f}\n"
                        plain_message += "\nThank you for trusting us."

                        html_message = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6;">
    <h2>Today's Return on Investment</h2>
    <ul>
    {''.join(f'<li><strong>{plan.name.upper()}</strong>: ${roi_amount:,.2f}</li>' for plan, roi_amount in accumulated_roi_per_plan.items())}
    </ul>
    <p>Thank you for trusting us.</p>
</body>
</html>
"""
                        send_mail(
                            subject="Your ROI Summary for Today",
                            message=plain_message,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[user.email],
                            fail_silently=False,
                            html_message=html_message,
                        )
                    except Exception as email_exc:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Failed to send email to {user.email}: {email_exc}"
                            )
                        )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"ROI updated for all users today {today.date()}"
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"Could not update users' transactions today {today.date()}.\nError: {str(e)}"
                    )
                )
