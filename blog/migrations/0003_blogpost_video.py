# Generated by Django 5.1.2 on 2024-11-04 13:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_blogpost_created_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogpost',
            name='video',
            field=models.FileField(null=True, upload_to='blog/videos/'),
        ),
    ]
