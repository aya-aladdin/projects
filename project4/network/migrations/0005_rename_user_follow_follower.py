# Generated by Django 5.1.4 on 2024-12-29 09:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0004_follow_reply_like'),
    ]

    operations = [
        migrations.RenameField(
            model_name='follow',
            old_name='user',
            new_name='follower',
        ),
    ]
