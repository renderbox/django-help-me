# Generated by Django 3.1 on 2020-11-06 22:38

import django.contrib.sites.managers
from django.db import migrations
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('helpme', '0010_auto_20201009_0000'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='ticket',
            managers=[
                ('objects', django.db.models.manager.Manager()),
                ('on_site', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
    ]
