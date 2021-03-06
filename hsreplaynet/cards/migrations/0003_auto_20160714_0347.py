# -*- coding: utf-8 -*-
# Generated by Django 1.10a1 on 2016-07-14 03:47
from __future__ import unicode_literals

from django.db import migrations
import hearthstone.enums
import hsreplaynet.utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0002_auto_20160618_1127'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CardCollectionAuditLog',
        ),
        migrations.AlterField(
            model_name='card',
            name='card_class',
            field=hsreplaynet.utils.fields.IntEnumField(choices=[(0, 'INVALID'), (1, 'DEATHKNIGHT'), (2, 'DRUID'), (3, 'HUNTER'), (4, 'MAGE'), (5, 'PALADIN'), (6, 'PRIEST'), (7, 'ROGUE'), (8, 'SHAMAN'), (9, 'WARLOCK'), (10, 'WARRIOR'), (11, 'DREAM'), (12, 'NEUTRAL')], default=0, validators=[hsreplaynet.utils.fields.IntEnumValidator(hearthstone.enums.CardClass)]),
        ),
    ]
