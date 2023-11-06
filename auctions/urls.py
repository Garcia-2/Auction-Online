from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('create_listing/', views.create_listing, name='create_listing'),
    path("listing_page/<int:listing_id>", views.listing_page, name="listing_page"),
    path("add_to_watchlist/<int:listing_id>", views.add_to_watchlist, name="add_to_watchlist"),
    path("remove_from_watchlist/<int:listing_id>", views.remove_from_watchlist, name="remove_from_watchlist"),
    path("place_bid/<int:listing_id>", views.place_bid, name="place_bid"),
    path('close_auction/<int:listing_id>', views.close_auction, name='close_auction'),
    path('listing_page/<int:listing_id>/comment', views.add_comment, name='add_comment'),
    path("watchlist", views.watchlist, name="watchlist"),
    path('categories/', views.category_list, name='categories'),
    path('category_listings/<int:category_id>', views.category_listings, name='category_listings'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)