# Generated by Django 3.0.3 on 2020-04-17 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nckh', '0002_delete_submit2'),
    ]

    operations = [
        migrations.DeleteModel(
            name='File',
        ),
        migrations.AlterField(
            model_name='submit',
            name='comment',
            field=models.CharField(default='', max_length=1024),
        ),
    ]