# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-15 03:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0010_miner_sshpassword'),
    ]

    operations = [
        migrations.AddField(
            model_name='miner',
            name='has_error',
            field=models.BooleanField(default=True),
        ),
    ]
