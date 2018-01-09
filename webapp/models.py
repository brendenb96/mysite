# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django  import forms


class Miner(models.Model):

    miner_choices = (
    ('antd3','Antminer D3'),
    ('antl3', 'Antminer L3'),
)

    name = models.CharField(max_length=30)
    ip = models.GenericIPAddressField()
    type = models.CharField(max_length=20, choices=miner_choices, default='antd3')
    username = models.CharField(max_length=20, default='root')
    password = models.CharField(max_length=20, default='root')
    sshpassword = models.CharField(max_length=20, default='admin')

    pool_one = models.CharField(max_length=100, default='')
    pool_one_worker = models.CharField(max_length=70, default='')
    pool_one_password = models.CharField(max_length=30, default='')

    pool_two = models.CharField(max_length=100, default='')
    pool_two_worker = models.CharField(max_length=70, default='')
    pool_two_password = models.CharField(max_length=30, default='')

    pool_three = models.CharField(max_length=100, default='')
    pool_three_worker = models.CharField(max_length=70, default='')
    pool_three_password = models.CharField(max_length=30, default='')

    hash_rate = models.FloatField()
    chain_1_temp = models.IntegerField(default=0)
    chain_2_temp = models.IntegerField(default=0)
    chain_3_temp = models.IntegerField(default=0)
    uptime = models.CharField(max_length=20, default='XX:XX')
    asic1 = models.CharField(max_length=70, default='NONE')
    asic2 = models.CharField(max_length=70, default='NONE')
    asic3 = models.CharField(max_length=70, default='NONE')
    bitmain_vil = models.CharField(max_length=10, default='true')
    bitmain_freq = models.CharField(max_length=10, default='0')

    def __unicode__(self):
        return self.name


# Create your models here.
