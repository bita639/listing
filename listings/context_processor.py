from .models import Category, Listing, SiteDetails


def categories(request):
    all_cats = Category.objects.all()
    return {'all_categories': all_cats}


def common_tags(request):
    common_tags = Listing.tags.most_common()[:4]
    return {'common_tags': common_tags}


def cities(request):
    all_city = Listing.objects.order_by(
        'city').values_list('city', flat=True).distinct()
    return {'all_city': all_city}


def all_location(request):
    all_location = Listing.objects.order_by(
        'location').values_list('location', flat=True).distinct()
    return {'all_location': all_location}


def recent_listings(reques):
    recent_listings = Listing.active_objects.filter(
        booked=False).order_by('-created_at')[:4]
    return {'recent_listings': recent_listings}


def setting(request):
    setting = SiteDetails.objects.all().first()
    return {'setting': setting}
