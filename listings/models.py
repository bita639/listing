from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db.models import CheckConstraint, Q, UniqueConstraint
from django.core.validators import MinValueValidator, MaxValueValidator
from taggit.managers import TaggableManager
from listings.tasks import set_booked_as_inactive
from django.template.defaultfilters import truncatechars

# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=250)
    image = models.ImageField(
        upload_to="category/%Y/%m/%d/", blank=True, null=True)

    class Meta():
        verbose_name = 'Category'
        verbose_name_plural = '1. Categories'

    def save(self, *args, **kwargs):
        if not self.id:
            # Newly created object, so set slug
            self.slug = slugify(self.name)

        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


def generate_unique_slug(klass, field):
    origin_slug = slugify(field)
    unique_slug = origin_slug
    numb = 1
    while klass.objects.filter(slug=unique_slug).exists():
        unique_slug = '%s-%d' % (origin_slug, numb)
        numb += 1

    return unique_slug


class ActiveListingManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(active=True)


class Listing(models.Model):
    STATUS_CHOICES = (
        ('0', 'Rent'),
        ('1', 'Sale'),
    )

    ROOMS_CHOICES = (
        ('1', 'One'),
        ('2', 'Two'),
        ('3', 'Three'),
        ('4', 'Four'),
        ('5', 'Five'),
        ('6', 'FIx'),
    )

    WASHROOM_CHOICES = (
        ('1', 'One'),
        ('2', 'Two'),
        ('3', 'Three'),
    )

    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user_listings')
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='category_listings')

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    description = models.TextField()

    price = models.FloatField()

    rooms = models.CharField(max_length=10, choices=ROOMS_CHOICES)
    wash_rooms = models.CharField(max_length=10, choices=WASHROOM_CHOICES)

    flat_area = models.FloatField()

    location = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    zip_code = models.CharField(max_length=200)

    active = models.BooleanField(default=True)
    booked = models.BooleanField(default=False)

    start_time = models.DateField()
    end_time = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    tags = TaggableManager()

    objects = models.Manager()
    active_objects = ActiveListingManager()

    class Meta:
        verbose_name = 'Listing'
        verbose_name_plural = '2. Listings'
        ordering = ['-id']

    def save(self, *args, **kwargs):
        if self.slug:
            if slugify(self.title) != self.slug:
                self.slug = generate_unique_slug(Listing, self.title)
        else:
            self.slug = generate_unique_slug(Listing, self.title)
        super(Listing, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('listings:edit_listing', args=[str(self.slug)])

    def __str__(self):
        return self.title


class ListingImage(models.Model):
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name='listing_images')
    image = models.ImageField(upload_to="product/%Y/%m/%d/")

    class Meta:
        verbose_name = 'Listing Image'
        verbose_name_plural = '3. Listing Images'

    def __str__(self):
        return self.listing.title


class ListingExtra(models.Model):
    STATUS_CHOICES = (
        ('0', 'No'),
        ('1', 'Yes'),
    )

    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name='listing_extras')
    facility_name = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    class Meta:
        verbose_name = 'Listing Extra'
        verbose_name_plural = '4. Listing Extras'

    def __str__(self):
        return self.listing.title


class ListingRating(models.Model):
    rating = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)])
    facility = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)])
    staff = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])
    price = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])
    average_rating = models.FloatField()
    review = models.TextField()
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name='listing_ratings')

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user_ratings')

    created_at = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = 'Listing Rating'
        verbose_name_plural = '5. Listing Rating'
        constraints = [
            CheckConstraint(check=Q(rating__range=(0, 5)),
                            name='valid_rating'),
            CheckConstraint(check=Q(facility__range=(0, 5)),
                            name='valid_facility'),
            CheckConstraint(check=Q(staff__range=(0, 10)), name='valid_staff'),
            CheckConstraint(check=Q(price__range=(0, 10)), name='valid_price'),
            UniqueConstraint(fields=['user', 'listing'], name='rating_once')
        ]

    def __str__(self):
        return f"{self.user.username} rates {self.listing.title}"

    def user_average_rating(self):
        return (self.rating + self.facility + self.price + self.staff) / 4


class ListingComment(models.Model):
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name='listing_comments')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user_comments')
    comment = models.TextField()

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = '6. Comments'

    def __str__(self):
        return f"{self.user.username} comments on {self.listing.title}"


class ListingBooking(models.Model):
    STATUS_CHOICES = (
        ('1', 'Pending'),
        ('2', 'Accepted'),
        ('3', 'Rejected'),
        ('4', 'Completed'),
    )

    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name='listing_bookings')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user_bookings')

    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='1', null=True, blank=True)

    start_time = models.DateField()
    end_time = models.DateField()

    # def save(self, *args, **kwargs):
    #     create_task = False
    #     if self.pk is None:
    #         create_task = True

    #     super(ListingBooking, self).save(*args, **kwargs)

    #     if create_task and self.end_time:
    #         print('okskksksk')
    #         set_booked_as_inactive.apply_async(
    #             args=[self.listing.id, self.id], eta=self.end_time)

    class Meta:
        verbose_name = 'Booking'
        verbose_name_plural = '7. Bookings'

    def __str__(self):
        return f"{self.user.username} books {self.listing.title}"


class SiteDetails(models.Model):
    sologan = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=230)
    phone = models.CharField(max_length=20)
    email = models.EmailField()

    facebook_url = models.URLField(max_length=200, null=True, blank=True)
    twitter_url = models.URLField(max_length=200, null=True, blank=True)
    linkdin_url = models.URLField(max_length=200, null=True, blank=True)
    instagram_url = models.URLField(max_length=200, null=True, blank=True)

    class Meta:
        verbose_name = 'Site Setting'
        verbose_name_plural = '8. Site Settings'

    def __str__(self):
        return self.email


class Contact(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()

    class Meta:
        verbose_name = 'Contact'
        verbose_name_plural = '9. Contact'

    @property
    def short_description(self):
        return truncatechars(self.message, 35)

    def __str__(self):
        return self.subject


@receiver(post_save, sender=ListingBooking)
def make_listing_booked(sender, instance, created, **kwargs):
    try:
        if not created:
            if instance.listing.booked == False and instance.status == '2':
                instance.listing.booked = True
                instance.listing.save()
            if instance.listing.booked == True and instance.status == '3':
                instance.listing.booked = False
                instance.listing.save()
            if instance.status == '1' or instance.status == '4':
                instance.listing.booked = False
                instance.listing.save()
    except Exception as e:
        pass
