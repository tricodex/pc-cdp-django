"""
Add owner field to Agent model
"""
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def get_default_user(apps, schema_editor):
    User = apps.get_model(settings.AUTH_USER_MODEL)
    return User.objects.first().id if User.objects.exists() else 1


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('agents', '0003_remove_agent_owner_agentwallet'),
    ]

    operations = [
        migrations.AddField(
            model_name='agent',
            name='owner',
            field=models.ForeignKey(
                to=settings.AUTH_USER_MODEL,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='agents',
                null=True
            ),
        ),
        migrations.AlterField(
            model_name='agent',
            name='owner',
            field=models.ForeignKey(
                to=settings.AUTH_USER_MODEL,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='agents'
            ),
        ),
    ]