from celery.decorators import task
from django.shortcuts import get_object_or_404


@task()
def set_booked_as_inactive(listing_id, booking_id):
    from .models import Listing, ListingBooking
    listing_object = get_object_or_404(Listing, id=listing_id)
    booking_object = get_object_or_404(ListingBooking, id=booking_id)

    listing_object.booked = False
    if booking_object.status == '2':
        booking_object.status = '4'

    listing_object.save()
    booking_object.save()
