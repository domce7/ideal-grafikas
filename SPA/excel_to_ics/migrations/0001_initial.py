# Generated by Django 4.0.4 on 2022-06-22 20:02

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Upload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('target_year', models.DateField()),
                ('target_month', models.DateField()),
                ('excel', models.FileField(upload_to='excel_files/')),
            ],
        ),
    ]
