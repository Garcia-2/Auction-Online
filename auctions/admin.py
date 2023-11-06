from django.contrib import admin
from .models import Category, Listings, User, Comment, Bid, Watchlist


# Register your models here.
admin.site.register(User)
admin.site.register(Category)
admin.site.register(Listings)
admin.site.register(Comment)
admin.site.register(Bid)
admin.site.register(Watchlist)

