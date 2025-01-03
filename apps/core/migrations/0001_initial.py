# Generated by Django 5.0.6 on 2025-01-02 19:32

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DashBoardPanel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game_title', models.CharField(max_length=127)),
                ('max_game_price', models.FloatField()),
                ('panel_type', models.CharField(choices=[('table', 'Table of Games Found in Search'), ('horizontal-bar chart', 'Bar-Chart of Discounts'), ('vertical-bar chart', 'Bar-Chart of Game Ratings')], max_length=127)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('panel_size', models.CharField(choices=[('small', 'Small'), ('medium', 'Medium'), ('large', 'Large')], default='medium', max_length=127)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='FavoriteGame',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, unique=True)),
                ('image', models.URLField()),
                ('release_date', models.DateTimeField()),
                ('sale_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('normal_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('steam_rating', models.IntegerField()),
                ('deal_rating', models.FloatField(default=0.0)),
                ('favorites', models.ManyToManyField(blank=True, related_name='favorite', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
