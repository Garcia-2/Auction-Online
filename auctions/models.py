from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

    def __str__(self) -> str:
        return f"Username:{self.username}. Email:{self.email}. User Id:{self.id}"

class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self) -> str:
        return f"{self.name}"
    

class Listings(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=500)
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField()
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    image_urls = models.URLField(max_length=500, blank=True, default="")
    category = models.ManyToManyField(Category)
    images = models.ImageField(upload_to='listings/images/', blank=True, null=True)
    closed = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.title} {self.description} {self.starting_bid} {self.date} {self.user} {self.category} {self.images} {self.image_urls} {self.closed}"

class Bid(models.Model):
    listing = models.ForeignKey('Listings', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listings = models.ManyToManyField(Listings, blank=True)

    def __str__(self):
        return f"{self.user.username}"