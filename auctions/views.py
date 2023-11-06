from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from .forms import CreateListingForm, BidForm, CommentForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import User, Listings, Watchlist, Bid, Comment, Category


def index(request):

    listings = Listings.objects.all()

    context = {
        "listings": listings
    }

    return render(request, "auctions/index.html", context)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        print("Login view accessed without POST request")
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required  
def create_listing(request):
    if request.method == "POST":
        form = CreateListingForm(request.POST, request.FILES)
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            starting_bid = form.cleaned_data["starting_bid"]
            image_urls = form.cleaned_data["image_urls"]
            images = form.cleaned_data["images"]
            category = list(form.cleaned_data["category"])
            date = timezone.now()
            user = request.user

            # Create a new listing object
            new_listing = Listings.objects.create(
                title=title,
                description=description,
                starting_bid=starting_bid,
                images=images,
                image_urls=image_urls,
                date=date,
                user=user
            )

            # Set the many-to-many relationship to the selected categories
            new_listing.category.set(category)

            return HttpResponseRedirect(reverse("index"))
    else:
        form = CreateListingForm()

    context = {
        "form": form,
    }

    return render(request, "auctions/create_listing.html", {"form": form}) # Pass the context dictionary to the render function

@login_required
def add_to_watchlist(request, listing_id):
    if request.user.is_authenticated:
        print("add_to_watchlist called")
        listing = get_object_or_404(Listings, pk=listing_id)
        watchlist, created = Watchlist.objects.get_or_create(user=request.user)
        watchlist.listings.add(listing)
        print(f"Added {listing.title} to watchlist for user {request.user.username}")
        return HttpResponseRedirect(reverse('listing_page', args=[listing_id]))  # Use 'args' here
    else:
        return HttpResponseRedirect(reverse('login'))

@login_required
def remove_from_watchlist(request, listing_id):
    if request.user.is_authenticated:
        print("remove_from_watchlist called")
        listing = get_object_or_404(Listings, pk=listing_id)

        # Get or create the user's watchlist
        watchlist, created = Watchlist.objects.get_or_create(user=request.user)
        if not created:
            watchlist.listings.remove(listing)
        return HttpResponseRedirect(reverse('listing_page', args=[listing_id]))
    else:
        return HttpResponseRedirect(reverse('login'))

@login_required  
def place_bid(request, listing_id):
    print("place_bid view called")
    listing = get_object_or_404(Listings, pk=listing_id)
    bid_form = BidForm(request.POST or None)

    if request.method == 'POST':
        if request.user.is_authenticated:
            if bid_form.is_valid():
                bid_amount = bid_form.cleaned_data['amount']
                current_bid = Bid.objects.filter(listing=listing).order_by('-amount').first()

                if (
                    bid_amount >= listing.starting_bid
                    and (not current_bid or bid_amount > current_bid.amount)
                ):
                    # Create a new bid
                    new_bid = Bid(listing=listing, user=request.user, amount=bid_amount)
                    new_bid.save()
                    current_bid = new_bid  # Update the current_bid

                    messages.success(request, 'Your bid has been placed successfully.')
                else:
                    messages.error(request, "Invalid bid amount. Bid amount can't be less than the current bid.")
                    return HttpResponseRedirect(reverse('listing_page', args=[listing_id]))  # Add this line to prevent the "Invalid bid form" message
            else:
                print(bid_form.errors)
                messages.error(request, 'Invalid bid form. Please try again.')
        else:
            return HttpResponseRedirect(reverse('login'))

    return HttpResponseRedirect(reverse('listing_page', args=[listing_id]))

@login_required
def close_auction(request, listing_id):
    listing = get_object_or_404(Listings, pk=listing_id)

    # Check if the user is the owner of the listing
    if request.user == listing.user and not listing.closed:
        # Close the auction
        listing.closed = True

        # Determine the winner (highest bidder)
        winning_bid = Bid.objects.filter(listing=listing).order_by('-amount').first()

        if winning_bid:
            winner = winning_bid.user
            listing.winner = winner
            listing.save()

            messages.success(request, f"The auction has been closed, and {winner.username} is the winner.")
        else:
             messages.info(request, "The auction has been closed, but there were no bids.")

    return HttpResponseRedirect(reverse('listing_page', args=[listing_id]))

@login_required
def listing_page(request, listing_id):
    listing = get_object_or_404(Listings, pk=listing_id)
    user_watchlist, created = Watchlist.objects.get_or_create(user=request.user)

    is_in_watchlist = False
    button_text = "Add to Watchlist"

    if listing in user_watchlist.listings.all():
        is_in_watchlist = True
        button_text = "Remove from Watchlist"

    current_bid = Bid.objects.filter(listing=listing).order_by('-amount').first()
    bid_form = BidForm(request.POST or None)

    # Comment handling
    comments = Comment.objects.filter(listing=listing)
    comment_form = CommentForm(request.POST or None)

    if request.method == 'POST':
        if request.user.is_authenticated:
            if bid_form.is_valid():
                bid_amount = bid_form.cleaned_data['amount']
                if (
                    bid_amount >= listing.starting_bid
                    and (not current_bid or bid_amount > current_bid.amount)
                ):
                    # Create a new bid
                    new_bid = Bid(listing=listing, user=request.user, amount=bid_amount)
                    new_bid.save()
                    return HttpResponseRedirect(reverse('listing_page', args=[listing_id]))
                else:
                    return render(request, "auctions/listing_page.html", {
                        "listing": listing,
                        "is_in_watchlist": is_in_watchlist,
                        "button_text": button_text,  # Added button_text
                        "current_bid": current_bid,
                        "bid_form": bid_form,
                        "error_message": "Invalid bid amount."
                    })
            elif comment_form.is_valid():
                new_comment = comment_form.save(commit=False)
                new_comment.user = request.user
                new_comment.listing = listing
                new_comment.save()
                return HttpResponseRedirect(reverse('listing_page', args=[listing_id]))
            else:
                return render(request, "auctions/listing_page.html", {
                    "listing": listing,
                    "is_in_watchlist": is_in_watchlist,
                    "button_text": button_text,  # Added button_text
                    "current_bid": current_bid,
                    "bid_form": bid_form,
                    "comments": comments,
                    "comment_form": comment_form,
                    "error_message": "Invalid bid or comment."
                })
        else:
            return HttpResponseRedirect(reverse('login'))

    return render(request, "auctions/listing_page.html", {
        "listing": listing,
        "is_in_watchlist": is_in_watchlist,
        "button_text": button_text,  # Added button_text
        "current_bid": current_bid,
        "bid_form": bid_form,
        "comments": comments,
        "comment_form": comment_form,
    })

@login_required
def add_comment(request, listing_id):
    if request.method == 'POST' and request.user.is_authenticated:
        form = CommentForm(request.POST)
        if form.is_valid():
            listing = Listings.objects.get(pk=listing_id)
            new_comment = form.save(commit=False)
            new_comment.user = request.user
            new_comment.listing = listing
            new_comment.save()
            messages.success(request, 'Comment added successfully.')
        else:
            messages.error(request, 'Invalid comment. Please try again.')

    return HttpResponseRedirect(reverse('listing_page', args=[listing_id]))

@login_required
def watchlist(request):
    user_watchlist, created = Watchlist.objects.get_or_create(user=request.user)
    listings = user_watchlist.listings.all()
    print(listings)
    return render(request, 'auctions/watchlist.html', {'listings': listings})

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'auctions/categories.html', {'categories': categories})

def category_listings(request, category_id):
    listings = Listings.objects.filter(category=category_id, closed=False)
    category = Category.objects.get(pk=category_id)
    return render(request, 'auctions/category_listings.html', {'listings': listings, 'category': category})