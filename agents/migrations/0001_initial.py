"""
Initial migration for agents app
"""
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Agent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('description', models.TextField()),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive'), ('pending', 'Pending'), ('error', 'Error'), ('completed', 'Completed')], default='inactive', max_length=20)),
                ('configuration', models.JSONField(default=dict)),
                ('wallet_address', models.CharField(blank=True, max_length=255)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='AgentAction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('action_type', models.CharField(max_length=100)),
                ('parameters', models.JSONField(default=dict)),
                ('result', models.JSONField(blank=True, null=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive'), ('pending', 'Pending'), ('error', 'Error'), ('completed', 'Completed')], default='pending', max_length=20)),
                ('error_message', models.TextField(blank=True)),
                ('agent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='actions', to='agents.agent')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]