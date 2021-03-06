# Generated by Django 3.1 on 2020-08-31 23:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        ('helpme', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=120)),
                ('localization', models.JSONField(default=dict)),
                ('sites', models.ManyToManyField(to='sites.Site')),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=120)),
                ('answer', models.CharField(max_length=255)),
                ('localization', models.JSONField(default=dict)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='questions', to='helpme.category')),
                ('sites', models.ManyToManyField(blank=True, to='sites.Site')),
            ],
        ),
    ]
