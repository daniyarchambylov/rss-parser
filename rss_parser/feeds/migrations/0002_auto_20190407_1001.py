# Generated by Django 2.1.7 on 2019-04-07 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feeds', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feed',
            name='link',
            field=models.URLField(unique=True),
        ),
        migrations.AlterField(
            model_name='feed',
            name='rss_link',
            field=models.URLField(unique=True),
        ),
        migrations.AlterField(
            model_name='feedarticle',
            name='link',
            field=models.URLField(unique=True),
        ),
    ]
