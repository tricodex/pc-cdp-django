"""Add TokenPrice model"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agents', '0004_agent_owner'),
    ]

    operations = [
        migrations.CreateModel(
            name='TokenPrice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token_id', models.CharField(max_length=100)),
                ('price_usd', models.DecimalField(decimal_places=12, max_digits=24)),
                ('price_eth', models.DecimalField(decimal_places=12, max_digits=24, null=True)),
                ('market_cap_usd', models.DecimalField(decimal_places=2, max_digits=24, null=True)),
                ('volume_24h_usd', models.DecimalField(decimal_places=2, max_digits=24, null=True)),
                ('change_24h', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('timestamp', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'indexes': [
                    models.Index(fields=['token_id'], name='token_id_idx'),
                    models.Index(fields=['timestamp'], name='timestamp_idx'),
                    models.Index(fields=['token_id', 'timestamp'], name='token_time_idx')
                ],
                'get_latest_by': 'timestamp',
            },
        ),
    ]
