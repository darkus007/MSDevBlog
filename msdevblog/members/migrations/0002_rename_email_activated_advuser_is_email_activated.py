# Generated by Django 4.2.1 on 2023-05-17 19:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='advuser',
            old_name='email_activated',
            new_name='is_email_activated',
        ),
    ]