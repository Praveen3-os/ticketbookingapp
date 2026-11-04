from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name='FAQ',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=500)),
                ('answer', models.TextField()),
                ('category', models.CharField(choices=[('booking','Booking'),('payment','Payment'),('account','Account'),('events','Events'),('errors','Error Codes'),('general','General')], default='general', max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('order', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ['category', 'order', 'id'], 'verbose_name': 'FAQ', 'verbose_name_plural': 'FAQs'},
        ),
    ]

