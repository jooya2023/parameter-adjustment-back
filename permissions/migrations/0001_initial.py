# Generated by Django 4.1.7 on 2023-03-25 07:53

import django.contrib.auth.models
from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='PermissionProxy',
            fields=[
            ],
            options={
                'proxy': True,
                'default_permissions': (),
                'indexes': [],
                'constraints': [],
            },
            bases=('auth.permission',),
            managers=[
                ('objects', django.contrib.auth.models.PermissionManager()),
            ],
        ),
    ]
