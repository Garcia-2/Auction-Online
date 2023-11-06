# Generated by Django 4.2.6 on 2023-10-18 07:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0004_rename_price_listings_starting_bid_listings_images'),
    ]

    operations = [
        migrations.RenameField(
            model_name='listings',
            old_name='categories',
            new_name='category',
        ),
        migrations.RenameField(
            model_name='listings',
            old_name='discription',
            new_name='description',
        ),
        migrations.AlterField(
            model_name='listings',
            name='image_urls',
            field=models.URLField(blank=True, default='', max_length=500),
        ),
    ]