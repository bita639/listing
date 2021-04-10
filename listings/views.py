from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime, timedelta, date
from django.utils import timezone
from django.db.models import Q
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Avg, Max, Min, Sum, F, IntegerField
from .models import Listing, Category, ListingImage, ListingExtra, ListingRating, ListingComment, ListingBooking, Contact
from django.contrib.auth.models import User
from accounts.mixins import AictiveUserRequiredMixin
from listings.mixins import OwnerShipMixin
from .forms import AddListingForm, EditListingForm, ListingRatingForm, ListingCommentForm, ListingBookingForm, ContactForm
from django.urls import reverse_lazy, reverse
import re
from taggit.models import Tag
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import generic
from django.views import View

# Create your views here.


class HomeView(View):
    def get(self, request, *args, **kwargs):
        conext = {
            'title': 'Home'
        }
        return render(request, 'listings/home.html', conext)


class CategoryListing(generic.ListView):
    model = Listing
    context_object_name = 'listing_list'
    paginate_by = 10
    template_name = 'listings/liting_list.html'

    def get_queryset(self):
        category_slug = self.kwargs.get('slug')
        category_obj = get_object_or_404(Category, slug=category_slug)

        today = datetime.now().date()

        listing_list = Listing.active_objects.filter(
            category=category_obj, booked=False).filter(Q(end_time__gte=today) | Q(end_time=None))

        return listing_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs.get('slug')
        context['title'] = f'{category_slug} Listings'
        return context


class TagListing(generic.ListView):
    model = Listing
    context_object_name = 'listing_list'
    paginate_by = 10
    template_name = 'listings/liting_list.html'

    def get_queryset(self):
        tag_slug = self.kwargs.get('slug')
        tag_obj = get_object_or_404(Tag, slug=tag_slug)

        today = datetime.now().date()

        listing_list = Listing.active_objects.filter(
            tags=tag_obj, booked=False, end_time__gte=today)
        return listing_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag_slug = self.kwargs.get('slug')
        context['title'] = f'{tag_slug} Listings'
        return context


@method_decorator(csrf_exempt, name='dispatch')
class ListingSearchView(generic.ListView):
    model = Listing
    context_object_name = 'listing_list'
    paginate_by = 10
    template_name = 'listings/liting_list.html'

    def get_queryset(self):
        if self.request.GET.get('category'):
            category_id = self.request.GET.get('category')
            try:
                category_obj = get_object_or_404(Category, id=category_id)
                listing_list = category_obj.category_listings.all()
            except Exception as e:
                listing_list = Listing.active_objects.all()
        else:
            listing_list = Listing.active_objects.all()

        if self.request.GET.get('city'):
            city = self.request.GET.get('city')
            listing_list = listing_list.filter(city__exact=city)
        if self.request.GET.get('location'):
            location = self.request.GET.get('location')
            listing_list = listing_list.filter(location__exact=location)
        if self.request.GET.get('query'):
            query = self.request.GET.get('query')
            listing_list = listing_list.filter(title__icontains=query)

        today = datetime.now().date()
        listing_list = listing_list.filter(
            Q(end_time__gte=today) | Q(end_time=None))

        return listing_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag_slug = self.kwargs.get('slug')
        context['title'] = f'Search Result'
        return context


class UserListing(generic.ListView):
    model = Listing
    context_object_name = 'listing_list'
    paginate_by = 10
    template_name = 'listings/user_list.html'

    def get_queryset(self):
        username = self.kwargs.get('username')
        user_obj = get_object_or_404(User, username=username)

        listing_list = Listing.active_objects.filter(owner=user_obj)
        return listing_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.kwargs.get('username')
        user_obj = get_object_or_404(User, username=username)
        context['title'] = f"{username.title()}'s Listings"
        context['user_obj'] = user_obj
        return context


class ListingDetails(generic.DetailView):
    model = Listing
    template_name = 'listings/listing_details.html'

    # def get_queryset(self):
    #     listing_slug = self.kwargs.get('slug')
    #     listing = Listing.objects.filter(slug=listing_slug)
    #     return listing

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = self.object.title
        context['related_listings'] = list(
            Listing.active_objects.filter(category=self.object.category, active=True))[:3]
        context['rating_form'] = ListingRatingForm()

        context['comment_form'] = ListingCommentForm(request=self.request)

        context['booking_form'] = ListingBookingForm(listing_id=self.object.id)

        context['average_listing_rating'] = self.object.listing_ratings.all(
        ).aggregate(avg_rating=Avg(('average_rating'), output_field=IntegerField()))
        context['avg_rating_value'] = self.object.listing_ratings.all(
        ).aggregate(avg_rating_value=Avg(('rating'), output_field=IntegerField()))

        context['avg_price_value'] = self.object.listing_ratings.all(
        ).aggregate(avg_price_value=Avg(('price'), output_field=IntegerField()))

        context['avg_staff_value'] = self.object.listing_ratings.all(
        ).aggregate(avg_staff_value=Avg(('staff'), output_field=IntegerField()))

        context['avg_facility_value'] = self.object.listing_ratings.all(
        ).aggregate(avg_facility_value=Avg(('facility'), output_field=IntegerField()))

        context['reviews'] = ListingRating.objects.filter(listing=self.object)

        return context


class AddListing(AictiveUserRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        add_listing_form = AddListingForm()
        context = {
            'title': 'Add Listing',
            'add_listing_form': add_listing_form
        }

        return render(request, 'listings/add_listing.html', context)

    def post(self, request, *args, **kwargs):
        add_listing_form = AddListingForm(request.POST, request.FILES)

        context = {
            'title': 'Add Listing',
            'add_listing_form': add_listing_form
        }
        if add_listing_form.is_valid():
            facility_name = request.POST.getlist('facility_name')
            facility_status_choice = request.POST.getlist(
                'facility_status_choice')

            add_listing = add_listing_form.save(commit=False)
            add_listing.owner = request.user
            add_listing.save()

            add_listing_form.save_m2m()

            for afile in request.FILES.getlist('images'):
                add_listing.listing_images.create(image=afile)

            for i in range(len(facility_name)):
                add_listing.listing_extras.create(
                    facility_name=facility_name[i], status=facility_status_choice[i])

            messages.success(request, 'Listing Added Successfully....')
            return redirect('listings:add_listing')
        else:
            return render(request, 'listings/add_listing.html', context)


class EditListing(AictiveUserRequiredMixin, OwnerShipMixin, SuccessMessageMixin, generic.edit.UpdateView):
    model = Listing
    form_class = EditListingForm
    template_name = 'accounts/update_listing.html'
    success_message = 'Listing successfully updated!!!!'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.title
        context['images'] = self.object.listing_images
        context['extras'] = self.object.listing_extras
        context['slug'] = self.kwargs.get('slug')
        return context


class UpdateListingImage(AictiveUserRequiredMixin, View):
    def post(self, request, *area, **kwargs):
        listing_slug = self.kwargs.get('slug')
        listing_obj = get_object_or_404(Listing, slug=listing_slug)

        image_count = listing_obj.listing_images.all().count()
        new_image_count = len(request.FILES.getlist('images'))

        if new_image_count == 0:
            messages.error(request, 'Please Select Some Image')
            return redirect('listings:edit_listing', listing_slug)
        elif image_count >= 4:
            messages.error(request, 'Please Delete Images To New One')
            return redirect('listings:edit_listing', listing_slug)
        elif image_count == 3 and new_image_count > 1:
            messages.error(request, 'You Can Add One More Image')
            return redirect('listings:edit_listing', listing_slug)
        elif image_count == 2 and new_image_count > 2:
            messages.error(request, 'You Can Add Two More Image')
            return redirect('listings:edit_listing', listing_slug)
        elif image_count == 1 and new_image_count > 3:
            messages.error(request, 'You Can Add Three More Image')
            return redirect('listings:edit_listing', listing_slug)
        elif image_count == 0 and new_image_count > 4:
            messages.error(request, 'You Can Add Four More Image')
            return redirect('listings:edit_listing', listing_slug)
        else:
            for afile in request.FILES.getlist('images'):
                listing_obj.listing_images.create(image=afile)
        messages.success(request, 'Image Added Successfully')
        return redirect('listings:edit_listing', listing_slug)

    def dispatch(self, request, *args, **kwargs):
        listing_slug = self.kwargs.get('slug')
        listing_obj = get_object_or_404(Listing, slug=listing_slug)

        if listing_obj.owner != self.request.user:
            messages.error(request, ('You are not allowed to edit this Post'))
            return redirect('accounts:dashboard')
        return super(UpdateListingImage, self).dispatch(request, *args, **kwargs)


class DeleteListingImage(AictiveUserRequiredMixin, generic.edit.DeleteView):
    model = ListingImage
    template_name = 'listings/listingimage_confirm_delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete Image'
        return context

    def get_success_url(self):
        if self.kwargs != None:
            return reverse_lazy('listings:edit_listing', kwargs={'slug': self.kwargs['slug']})
        else:
            return reverse_lazy('listings:edit_listing', args=(self.object.listing.slug))

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.listing.owner != self.request.user:
            messages.error(request, ('You are not allowed to edit this Post'))
            return redirect('accounts:dashboard')
        return super(DeleteListingImage, self).dispatch(request, *args, **kwargs)


class UpdateListingExtra(AictiveUserRequiredMixin, View):
    def post(self, request, *area, **kwargs):
        listing_slug = self.kwargs.get('slug')
        listing_obj = get_object_or_404(Listing, slug=listing_slug)

        facility_name = request.POST.getlist('facility_name')
        facility_status_choice = request.POST.getlist(
            'facility_status_choice')

        for i in range(len(facility_name)):
            listing_obj.listing_extras.create(
                facility_name=facility_name[i], status=facility_status_choice[i])
        messages.success(request, 'Listing Extras Added Successfully')
        return redirect('listings:edit_listing', listing_slug)

    def dispatch(self, request, *args, **kwargs):
        listing_slug = self.kwargs.get('slug')
        listing_obj = get_object_or_404(Listing, slug=listing_slug)

        if listing_obj.owner != self.request.user:
            messages.error(request, ('You are not allowed to edit this Post'))
            return redirect('accounts:dashboard')
        return super(UpdateListingExtra, self).dispatch(request, *args, **kwargs)


class DeleteListingExtra(AictiveUserRequiredMixin, generic.edit.DeleteView):
    model = ListingExtra
    template_name = 'listings/listingextra_confirm_delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete Extra'
        return context

    def get_success_url(self):
        if self.kwargs != None:
            return reverse_lazy('listings:edit_listing', kwargs={'slug': self.kwargs['slug']})
        else:
            return reverse_lazy('listings:edit_listing', args=(self.object.listing.slug))

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.listing.owner != self.request.user:
            messages.error(request, ('You are not allowed to edit this Post'))
            return redirect('accounts:dashboard')
        return super(DeleteListingExtra, self).dispatch(request, *args, **kwargs)


class ListingStatusToggle(AictiveUserRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        listing_slug = self.kwargs.get('slug')
        listing_obj = get_object_or_404(Listing, slug=listing_slug)

        listing_obj.active ^= True
        listing_obj.save()

        messages.success(
            request, 'Listing Active Status Changed Successfully...')
        return redirect('accounts:my_listing')

    def dispatch(self, request, *args, **kwargs):
        listing_slug = self.kwargs.get('slug')
        listing_obj = get_object_or_404(Listing, slug=listing_slug)

        if listing_obj.owner != self.request.user:
            messages.error(request, ('You are not allowed to edit this Post'))
            return redirect('accounts:dashboard')
        return super(ListingStatusToggle, self).dispatch(request, *args, **kwargs)


class DeleteListing(AictiveUserRequiredMixin, SuccessMessageMixin, generic.edit.DeleteView):
    model = Listing
    template_name = 'listings/listing_confirm_delete.html'
    success_message = 'Lisitng Deleted Successgully'
    success_url = reverse_lazy('accounts:my_listing')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(DeleteListing, self).delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete Listing'
        return context

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.owner != self.request.user:
            messages.error(request, ('You are not allowed to edit this Post'))
            return redirect('accounts:dashboard')
        return super(DeleteListingExtra, self).dispatch(request, *args, **kwargs)


class ListingRatingView(AictiveUserRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        listing_id = self.kwargs.get('id')
        listing_obj = get_object_or_404(Listing, id=listing_id)

        check_rating = listing_obj.listing_ratings.filter(
            user=request.user).first()
        book_check = ListingBooking.objects.filter(
            listing=listing_obj, user=request.user).first()

        if book_check is None:
            messages.error(request, f'Please First Book This {listing_obj.title} To Rate')
            return redirect('listings:listing_details', listing_obj.slug)

        if check_rating:
            messages.error(request, f'You Already Gave Your Rating For {listing_obj.title}')
            return redirect('listings:listing_details', listing_obj.slug)

        listing_rating_form = ListingRatingForm(request.POST)
        if listing_rating_form.is_valid():
            add_listing_rating = listing_rating_form.save(commit=False)
            add_listing_rating.average_rating = (
                listing_rating_form.cleaned_data.get('rating') +
                listing_rating_form.cleaned_data.get('staff') +
                listing_rating_form.cleaned_data.get('price') +
                listing_rating_form.cleaned_data.get('facility')) / 4
            add_listing_rating.listing = listing_obj
            add_listing_rating.user = request.user
            add_listing_rating.save()
            messages.success(request, 'Thanks For Your Ratings...')
            return redirect('listings:listing_details', listing_obj.slug)
        else:
            return redirect('listings:listing_details', listing_obj.slug)


class ListingCommentView(AictiveUserRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        listing_id = self.kwargs.get('id')
        listing_obj = get_object_or_404(Listing, id=listing_id)

        listing_comment_form = ListingCommentForm(
            request.POST, request=request)
        if listing_comment_form.is_valid():
            add_listing_comment = listing_comment_form.save(commit=False)
            add_listing_comment.listing = listing_obj
            add_listing_comment.user = request.user
            add_listing_comment.save()
            messages.success(request, 'Thanks For Your Comments...')
            return redirect('listings:listing_details', listing_obj.slug)
        else:
            print(listing_comment_form.errors)
            return redirect('listings:listing_details', listing_obj.slug)


class ListingBookingView(AictiveUserRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        listing_id = self.kwargs.get('id')
        listing_obj = get_object_or_404(Listing, id=listing_id)

        listing_booking_form = ListingBookingForm(
            request.POST, listing_id=listing_id)
        if listing_booking_form.is_valid():
            add_listing_booking = listing_booking_form.save(commit=False)
            add_listing_booking.listing = listing_obj
            add_listing_booking.user = request.user
            add_listing_booking.save()
            messages.success(request, 'Your Reuqested Has Been Submited...')
            return redirect('listings:listing_details', listing_obj.slug)
        else:
            messages.info(request, listing_booking_form.errors)
            return redirect('listings:listing_details', listing_obj.slug)


class ContactView(SuccessMessageMixin, generic.CreateView):
    model = Contact
    template_name = 'listings/contact.html'
    form_class = ContactForm
    success_message = 'Thanks For You Message.We Will Contact You Soon'
    success_url = reverse_lazy('listings:contact')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Contact Us'
        return context
