# Generated by Django 4.1.7 on 2023-04-18 21:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sacred_garden', '0003_emotionalneed_is_sample_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='has_sample_data',
            field=models.BooleanField(default=False),
        ),
    ]
