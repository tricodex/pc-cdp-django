"""
Migration to add ChatMessage model.
"""
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('agents', '0006_pricecache_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('message_type', models.CharField(choices=[('human', 'Human'), ('ai', 'AI'), ('tool', 'Tool'), ('system', 'System')], max_length=10)),
                ('content', models.TextField()),
                ('metadata', models.JSONField(default=dict, help_text='Additional message metadata like tool calls or system info')),
                ('conversation_id', models.UUIDField(default=uuid.uuid4, help_text='Groups messages in same conversation')),
                ('agent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat_messages', to='agents.agent')),
                ('parent_message', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='replies', to='agents.chatmessage')),
            ],
            options={
                'ordering': ['created_at'],
                'indexes': [
                    models.Index(fields=['agent', 'conversation_id'], name='agents_chat_agent_i_c8001c_idx'),
                    models.Index(fields=['conversation_id'], name='agents_chat_convers_f21274_idx'),
                    models.Index(fields=['created_at'], name='agents_chat_created_e0c1a5_idx')
                ],
            },
        ),
    ]
