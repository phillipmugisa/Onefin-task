# Generated by Django 4.1.1 on 2022-09-17 20:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("movies", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="collection",
            name="uuid",
            field=models.CharField(
                blank=True, max_length=50, null=True, verbose_name="uuid"
            ),
        ),
        migrations.AlterField(
            model_name="collectionmovie",
            name="uuid",
            field=models.CharField(
                blank=True, max_length=50, null=True, verbose_name="uuid"
            ),
        ),
        migrations.AlterField(
            model_name="moviegenre",
            name="uuid",
            field=models.CharField(
                blank=True, max_length=50, null=True, verbose_name="uuid"
            ),
        ),
    ]