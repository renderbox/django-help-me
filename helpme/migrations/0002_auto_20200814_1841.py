# Generated by Django 3.0 on 2020-08-14 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('helpme', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='category',
            field=models.IntegerField(choices=[(1, 'Comment'), (2, 'Sales'), (3, 'Help'), (4, 'Bug')], default=3, verbose_name='Category'),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='priority',
            field=models.IntegerField(choices=[(1, 'Low'), (2, 'Medium'), (3, 'High'), (4, 'Urgent')], default=2, verbose_name='Priority'),
        ),
    ]
