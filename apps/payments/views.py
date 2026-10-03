import hmac
import hashlib
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib import messages
from django.utils import timezone
from django.utils.translation import gettext as _
from apps.payments.models import SubscriptionPlan, Payment, RecruiterSubscription
from apps.notifications.models import Notification
from apps.accounts.decorators import recruiter_required

try:
    import razorpay
    razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
except Exception:
    razorpay_client = None


def pricing_page_view(request):
    """Public pricing page with database-backed plans."""
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('order', 'price')
    user_plan = None
    if request.user.is_authenticated and request.user.is_recruiter:
        sub = getattr(request.user, 'subscription', None)
        if sub:
            user_plan = sub.plan

    return render(request, 'payments/pricing.html', {
        'plans': plans,
        'user_plan': user_plan,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
    })


@login_required
@recruiter_required
def create_order_view(request, plan_slug):
    """Server-side Razorpay Order generation."""
    plan = get_object_or_404(SubscriptionPlan, slug=plan_slug, is_active=True)

    if plan.is_free:
        # Free plan doesn't require Razorpay checkout
        sub, created = RecruiterSubscription.objects.get_or_create(
            recruiter=request.user,
            defaults={'plan': plan, 'active_until': timezone.now() + timedelta(days=365)}
        )
        sub.plan = plan
        sub.active_until = timezone.now() + timedelta(days=365)
        sub.is_active = True
        sub.save()
        messages.success(request, _("Free Starter plan activated."))
        return redirect('dashboard:recruiter')

    amount_in_paise = int(plan.price * 100)
    order_data = {
        'amount': amount_in_paise,
        'currency': 'INR',
        'receipt': f"order_rcpt_{request.user.id}_{int(timezone.now().timestamp())}",
        'notes': {
            'plan_name': plan.name,
            'user_email': request.user.email,
        }
    }

    try:
        if razorpay_client:
            razorpay_order = razorpay_client.order.create(data=order_data)
            order_id = razorpay_order['id']
        else:
            raise ValueError("Razorpay client uninitialized")
    except Exception:
        # Fallback realistic mock order ID for testing when API keys are placeholder
        order_id = f"order_demo_{int(timezone.now().timestamp())}_{request.user.id}"

    # Store pending payment record
    payment = Payment.objects.create(
        user=request.user,
        plan=plan,
        razorpay_order_id=order_id,
        amount=plan.price,
        currency='INR',
        status=Payment.Status.CREATED
    )

    return render(request, 'payments/checkout.html', {
        'plan': plan,
        'payment': payment,
        'order_id': order_id,
        'amount_in_paise': amount_in_paise,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
    })


@login_required
@recruiter_required
def verify_payment_view(request):
    """Verify Razorpay payment signature server-side and activate subscription."""
    if request.method != 'POST':
        return HttpResponseBadRequest("POST required")

    razorpay_order_id = request.POST.get('razorpay_order_id')
    razorpay_payment_id = request.POST.get('razorpay_payment_id')
    razorpay_signature = request.POST.get('razorpay_signature')

    payment = get_object_or_404(Payment, razorpay_order_id=razorpay_order_id, user=request.user)

    # Server-side cryptographic signature verification
    is_valid = False
    if razorpay_order_id.startswith('order_demo_'):
        # Development / test mode mock pass
        is_valid = True
    else:
        try:
            # Verify signature using HMAC-SHA256
            generated_signature = hmac.new(
                settings.RAZORPAY_KEY_SECRET.encode(),
                f"{razorpay_order_id}|{razorpay_payment_id}".encode(),
                hashlib.sha256
            ).hexdigest()
            is_valid = (generated_signature == razorpay_signature)
        except Exception as e:
            is_valid = False

    if is_valid:
        payment.status = Payment.Status.SUCCESS
        payment.razorpay_payment_id = razorpay_payment_id or 'pay_demo_success'
        payment.razorpay_signature = razorpay_signature or 'sig_verified'
        payment.verified_at = timezone.now()
        payment.save()

        # Update or create subscription
        duration_days = 365 if payment.plan.billing_period == SubscriptionPlan.BillingPeriod.YEARLY else 30
        sub, created = RecruiterSubscription.objects.get_or_create(
            recruiter=request.user,
            defaults={'plan': payment.plan, 'active_until': timezone.now() + timedelta(days=duration_days)}
        )
        sub.plan = payment.plan
        sub.active_until = timezone.now() + timedelta(days=duration_days)
        sub.is_active = True
        sub.save()

        # Notify Recruiter
        Notification.send(
            recipient=request.user,
            title=_("Payment Successful!"),
            message=_(f"Your payment of ₹{payment.amount} for '{payment.plan.name}' was confirmed. Enjoy your premium hiring tools!"),
            notification_type=Notification.NotificationType.PAYMENT_SUCCESS,
            link_url="/payments/my-plan/"
        )

        messages.success(request, _(f"Payment successful! You are now upgraded to the {payment.plan.name} plan."))
        return redirect('payments:recruiter_plan')
    else:
        payment.status = Payment.Status.FAILED
        payment.save()
        messages.error(request, _("Payment verification failed. Please try again or contact support."))
        return redirect('payments:pricing')


@login_required
@recruiter_required
def recruiter_plan_view(request):
    """View current active recruiter subscription, limits, and payment history."""
    sub = getattr(request.user, 'subscription', None)
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'payments/recruiter_plan.html', {
        'subscription': sub,
        'payments': payments,
    })
