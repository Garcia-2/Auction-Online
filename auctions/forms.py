from django import forms
from .models import Listings, Category, Comment

class CreateListingForm(forms.ModelForm):
    class Meta:
        model = Listings
        fields = ['title', 'description', 'starting_bid', 'category', 'images', 'image_urls']

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'starting_bid': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.CheckboxSelectMultiple(), 
            #'images': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'image_urls': forms.URLInput(attrs={'class': 'form-control'}),
        }

class BidForm(forms.Form):
    amount = forms.DecimalField(
        label='Bid Amount',
        max_digits=10,
        decimal_places=2,
        min_value=0.01  # Adjust the minimum bid amount as needed
    )

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']