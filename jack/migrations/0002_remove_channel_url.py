# Generated by Django 3.1 on 2020-08-29 10:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jack', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='channel',
            name='url',
        ),
    ]
