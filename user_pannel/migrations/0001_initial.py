# Generated by Django 5.0.6 on 2024-08-11 13:05

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
            name='UserAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('house_name', models.CharField(max_length=100)),
                ('street_name', models.CharField(max_length=100)),
                ('pin_number', models.IntegerField()),
                ('district', models.CharField(max_length=100)),
                ('state', models.CharField(max_length=100)),
                ('phone_number', models.CharField(max_length=50)),
                ('status', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User Address',
                'verbose_name_plural': 'User Addresses',
            },
        ),
    ]
