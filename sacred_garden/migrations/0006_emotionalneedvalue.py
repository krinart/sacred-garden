# Generated by Django 4.1.7 on 2023-03-31 02:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sacred_garden', '0005_emotionalneed'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmotionalNeedValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.IntegerField()),
                ('is_current', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('emotional_need', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sacred_garden.emotionalneed')),
                ('partner_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
