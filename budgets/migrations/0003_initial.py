import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('budgets', '0002_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.AddField(
            model_name='budget',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='budgets', to=settings.AUTH_USER_MODEL, verbose_name='user'),
        ),
        migrations.AddIndex(
            model_name='budget',
            index=models.Index(fields=['user', 'start_date', 'end_date'], name='budgets_bud_user_id_ea9bf3_idx'),
        ),
        migrations.AddIndex(
            model_name='budget',
            index=models.Index(fields=['user', 'category'], name='budgets_bud_user_id_72baec_idx'),
        ),
    ]
