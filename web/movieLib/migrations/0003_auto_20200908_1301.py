# Generated by Django 3.1.1 on 2020-09-08 05:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movieLib', '0002_auto_20200908_1115'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actor',
            name='birthday',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='actor',
            name='birthplace',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='actor',
            name='constellation',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='actor',
            name='description',
            field=models.CharField(max_length=10000, null=True),
        ),
        migrations.AlterField(
            model_name='actor',
            name='gender',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='actor',
            name='profession',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='movie',
            name='description',
            field=models.CharField(max_length=20000, null=True),
        ),
        migrations.AlterField(
            model_name='movie',
            name='rating',
            field=models.FloatField(default=0, null=True),
        ),
    ]
