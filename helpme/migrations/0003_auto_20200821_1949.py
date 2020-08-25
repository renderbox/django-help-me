# Generated by Django 3.1 on 2020-08-21 19:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('helpme', '0002_auto_20200814_1841'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ticket',
            options={'permissions': (('see-support-tickets', 'Access to support-level tickets'), ('see-developer-tickets', 'Access to developer-level tickets'), ('see-all-tickets', 'Access to all tickets'))},
        ),
        migrations.AlterField(
            model_name='ticket',
            name='history',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='priority',
            field=models.IntegerField(choices=[(1, 'Suggestion'), (2, 'Low'), (3, 'Medium'), (4, 'High'), (5, 'Urgent')], default=3, verbose_name='Priority'),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='user_meta',
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
    ]
