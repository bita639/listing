from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from accounts.tokens import account_activation_token
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from accounts.forms import SignUpForm, UpdateProfile
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from listings.models import Listing, ListingRating, ListingBooking
from listings.forms import ChangeBookingStatus
import json
from django.db.models import Q
import datetime
from django.db.models import Count
from django.db.models.functions import TruncMonth
from .mixins import AictiveUserRequiredMixin
from listings.mixins import OwnerShipMixin
from django.views import View, generic

# Create your views here.


class RegisterView(View):
    def get(self, request, *args, **kwrags):
        signup_form = SignUpForm()
        context = {
            'signup_form': signup_form,
            'title': 'Register'
        }
        return render(request, 'accounts/register.html', context)

    def post(self, request, *args, **kwrags):
        signup_form = SignUpForm(request.POST)
        if signup_form.is_valid():
            user = signup_form.save()
            user.refresh_from_db()
            user.user_profile.phone_number = signup_form.cleaned_data.get(
                'phone_number')
            user.user_profile.address = signup_form.cleaned_data.get('address')
            user.save()

            current_site = get_current_site(request)
            subject = 'Activate Your Account'
            message = render_to_string('acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)
            messages.success(
                request, ('Registration Completed.Please Confirm Your Email Address'))
            return redirect('accounts:login')
        else:
            context = {
                'signup_form': signup_form,
                'title': 'Register'
            }
            return render(request, 'accounts/register.html', context)


def activate(request, uidb64, token):
    try:
        uid = force_bytes(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.user_profile.email_confirmed = True
        user.user_profile.save()
        messages.success(
            request, ('Thank You For Confirm The Email.Your Account Will Be Activated Soon'))
        return redirect('accounts:login')
    else:
        messages.success(request, ('Activation link is invalid!'))
        return redirect('accounts:login')


class Dashboard(AictiveUserRequiredMixin, View):
    def get(self, request, *args, **kwrags):
        booking_request = ListingBooking.objects.filter(
            listing__owner=self.request.user).annotate(month=TruncMonth('end_time')).values('month').annotate(total=Count('id'))

        my_booking = ListingBooking.objects.filter(
            user=self.request.user).annotate(month=TruncMonth('end_time')).values('month').annotate(total=Count('id'))

        booking_request_count = ListingBooking.objects.filter(
            listing__owner=self.request.user).count()

        my_booking_count = ListingBooking.objects.filter(
            user=self.request.user).count()

        my_listing_count = Listing.objects.filter(
            owner=self.request.user).count()

        my_listing_review_count = ListingRating.objects.filter(
            listing__owner=self.request.user).count()

        booking_request_labels = []
        booking_request_data = []
        for m_b in booking_request:
            booking_request_labels.append(m_b['month'].strftime("%B"))
            booking_request_data.append(m_b['total'])

        my_booking_labels = []
        my_booking_data = []
        for m_b in my_booking:
            my_booking_labels.append(m_b['month'].strftime("%B"))
            my_booking_data.append(m_b['total'])

        context = {
            'title': 'Dashboard',
            'booking_request_count': booking_request_count,
            'my_booking_count': my_booking_count,
            'my_listing_count': my_listing_count,
            'my_listing_review_count': my_listing_review_count,
            'booking_request_labels': booking_request_labels,
            'booking_request_data': booking_request_data,
            'my_booking_labels': my_booking_labels,
            'my_booking_data': my_booking_data
        }
        return render(request, 'accounts/dashboard.html', context)


class MyProfile(AictiveUserRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        update_profile_form = UpdateProfile(request=request)
        chanage_password_form = PasswordChangeForm(user=request.user)
        context = {
            'title': 'My Profile',
            'update_profile_form': update_profile_form,
            'chanage_password_form': chanage_password_form

        }
        return render(request, 'accounts/my_profile.html', context)

    def post(self, request, *args, **kwargs):

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        about = request.POST.get('about')
        profile_image = request.FILES.get('profile_image')

        if first_name:
            request.user.first_name = first_name
        if last_name:
            request.user.last_name = last_name
        if phone_number:
            request.user.user_profile.phone_number = phone_number
        if address:
            request.user.user_profile.address = address
        if about:
            request.user.user_profile.about = about
        if profile_image:
            request.user.user_profile.profile_pic = profile_image

        request.user.save()
        request.user.user_profile.save()

        messages.success(request, "Profile Updated Successfully")
        return redirect('accounts:my_profile')


class ChangePassword(AictiveUserRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        chanage_password_form = PasswordChangeForm(
            data=request.POST, user=request.user)
        update_profile_form = UpdateProfile(request=request)
        context = {
            'chanage_password_form': chanage_password_form,
            'update_profile_form': update_profile_form
        }
        if chanage_password_form.is_valid():
            chanage_password_form.save()
            update_session_auth_hash(request, chanage_password_form.user)
            messages.success(request, ('You have Changed Your Password...'))
            return redirect('accounts:my_profile')
        else:
            return render(request, 'accounts/my_profile.html', context)


class MyListing(AictiveUserRequiredMixin, generic.ListView):
    model = Listing
    context_object_name = 'listing_list'
    paginate_by = 10
    template_name = 'accounts/liting_list.html'

    def get_queryset(self):
        listing_list = Listing.objects.filter(owner=self.request.user)

        return listing_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"{self.request.user.get_full_name()}'s Listings"
        return context


class MyListingReview(AictiveUserRequiredMixin, generic.ListView):
    model = ListingRating
    context_object_name = 'listing_review_list'
    paginate_by = 10
    template_name = 'accounts/listing_review_list.html'

    def get_queryset(self):
        listing_review_list = ListingRating.objects.filter(
            listing__owner=self.request.user)
        return listing_review_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"{self.request.user.username.title()}'s Listings Review"
        return context


class MyBookingView(AictiveUserRequiredMixin, generic.ListView):
    model = ListingBooking
    context_object_name = 'booking_list'
    paginate_by = 10
    template_name = 'accounts/booking_list.html'

    def get_queryset(self):
        booking_list = ListingBooking.objects.filter(
            Q(user=self.request.user) | Q(listing__owner=self.request.user))

        return booking_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Booking List'
        context['change_booking_status'] = ChangeBookingStatus()
        return context


class ChangeBookingStatusView(AictiveUserRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        booking_id = kwargs.get('id')
        booking_object = get_object_or_404(ListingBooking, id=booking_id)

        booking_status = request.POST.get('status')

        if booking_status == '':
            messages.error(request, ('Please select A Value...'))
            return redirect('accounts:my_booking')
        else:
            booking_object.status = booking_status
            booking_object.save()
            messages.success(request, ('You have Changed Booking Status...'))
            return redirect('accounts:my_booking')

    def dispatch(self, request, *args, **kwargs):
        booking_id = kwargs.get('id')
        booking_object = get_object_or_404(ListingBooking, id=booking_id)

        if booking_object.listing.owner != self.request.user:
            messages.error(request, ('You are not allowed to edit this Post'))
            return redirect('accounts:my_booking')
        return super(ChangeBookingStatusView, self).dispatch(request, *args, **kwargs)


class MyWalletView(AictiveUserRequiredMixin, generic.ListView):
    model = ListingBooking
    context_object_name = 'booking_list'
    paginate_by = 10
    template_name = 'accounts/wallet_list.html'

    def get_queryset(self):
        booking_list = ListingBooking.objects.filter(
            listing__owner=self.request.user)

        return booking_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['booking_request_count'] = ListingBooking.objects.filter(
            listing__owner=self.request.user).count()
        context['my_listing_count'] = Listing.objects.filter(
            owner=self.request.user).count()

        context['title'] = 'Wallet List'
        return context


class LogoutView(AictiveUserRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, ('You Have Been Logged Out..'))
        return redirect('accounts:login')
