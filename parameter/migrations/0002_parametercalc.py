# Generated by Django 4.1.7 on 2023-04-12 15:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('parameter', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParameterCalc',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.JSONField()),
                ('is_active', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('furnace_setting', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='furnace_setting', to='parameter.furnacesetting')),
                ('parameter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parameter', to='parameter.parameter')),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
    ]