# Generated by Django 4.1.7 on 2023-03-30 00:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sacred_garden', '0002_alter_user_managers_user_partner_invite_code_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='partner_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]