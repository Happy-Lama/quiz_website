# Generated by Django 4.2.10 on 2024-02-20 23:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz_system', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='image',
            field=models.ImageField(blank=True, default=None, null=True, upload_to='images/'),
        ),
    ]
