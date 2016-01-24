# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0006_auto_20160108_2132'),
    ]

    operations = [
        migrations.AddField(
            model_name='productclass',
            name='digital_goods',
            field=models.NullBooleanField(help_text="Indicates that products in this class are Digital Goods per EU VAT regulations, meaning the customer's location determines the applicable VAT rate.", verbose_name='Digital Goods?'),
        ),
    ]
