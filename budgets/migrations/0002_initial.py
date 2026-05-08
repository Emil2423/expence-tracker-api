import django.db.models.deletion
from django.db import migrations, models
class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('budgets', '0001_initial'),
        ('transactions', '0001_initial'),
    ]
    operations = [
        migrations.AddField(
            model_name='budget',
            name='category',
            field=models.ForeignKey(help_text='Category to track spending for.', on_delete=django.db.models.deletion.CASCADE, related_name='budgets', to='transactions.category', verbose_name='category'),
        ),
    ]
