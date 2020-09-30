# Generated by Django 3.1 on 2020-09-08 22:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('helpme', '0004_auto_20200901_2323'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='comment_type',
            field=models.IntegerField(choices=[(0, 'Message'), (1, 'History')], default=0, verbose_name='Type'),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='description',
            field=models.TextField(verbose_name='Message'),
        ),
    ]