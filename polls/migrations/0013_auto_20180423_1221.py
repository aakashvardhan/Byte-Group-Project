# Generated by Django 2.0.4 on 2018-04-23 12:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0012_surveyanswer_surveytitle'),
    ]

    operations = [
        migrations.AlterField(
            model_name='surveyquestion',
            name='title',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='polls.Surveytitle'),
        ),
    ]