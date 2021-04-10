from django.urls import path
from . import views

app_name = "listings"

urlpatterns = [
    path('', views.HomeView.as_view(), name="home"),

    path('category/listings/<slug:slug>',
         views.CategoryListing.as_view(), name="category_listing"),

    path('tag/listings/<slug:slug>',
         views.TagListing.as_view(), name="tag_listing"),

    path('user/listings/<str:username>',
         views.UserListing.as_view(), name="user_listing"),

    path('listing/details/<slug:slug>',
         views.ListingDetails.as_view(), name="listing_details"),


    path('listing/add-listing', views.AddListing.as_view(), name="add_listing"),
    path('listing/edit-listing/<slug:slug>',
         views.EditListing.as_view(), name="edit_listing"),

    path('listing/update-listing-image/<slug:slug>',
         views.UpdateListingImage.as_view(), name="update_listing_image"),
    path('listing/delete-listing-image/<int:pk>/<str:slug>',
         views.DeleteListingImage.as_view(), name="delete_listing_image"),

    path('listing/update-listing-extra/<slug:slug>',
         views.UpdateListingExtra.as_view(), name="update_listing_extra"),
    path('listing/delete-listing-extra/<int:pk>/<str:slug>',
         views.DeleteListingExtra.as_view(), name="delete_listing_extra"),

    path('listing/listing-active-status-toggle/<slug:slug>',
         views.ListingStatusToggle.as_view(), name="listing_status_toggle"),
    path('listing/delete/<int:pk>',
         views.DeleteListing.as_view(), name="delete_listing"),


    path('listing/rating/<int:id>',
         views.ListingRatingView.as_view(), name="listing_rating"),

    path('listing/comment/<int:id>',
         views.ListingCommentView.as_view(), name="listing_comment"),


    path('listing/booking/<int:id>',
         views.ListingBookingView.as_view(), name="listing_booking"),

    path('listing/search',
         views.ListingSearchView.as_view(), name="listing_search"),

    path('listing/contact',
         views.ContactView.as_view(), name="contact"),

]
