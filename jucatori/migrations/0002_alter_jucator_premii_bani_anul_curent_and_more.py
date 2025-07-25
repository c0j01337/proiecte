# Generated by Django 5.1.7 on 2025-04-23 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jucatori', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jucator',
            name='premii_bani_anul_curent',
            field=models.IntegerField(default=0, help_text='Premii în bani anul curent ($)'),
        ),
        migrations.AlterField(
            model_name='jucator',
            name='premii_bani_total',
            field=models.IntegerField(default=0, help_text='Total premii în bani ($)'),
        ),
    ]
