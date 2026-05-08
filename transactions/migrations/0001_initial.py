import django.core.validators
from decimal import Decimal
from django.db import migrations, models
class Migration(migrations.Migration):
    initial = True
    dependencies = [
    ]
    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of the category (max 50 characters).', max_length=50, verbose_name='category name')),
                ('type', models.CharField(choices=[('INCOME', 'Income'), ('EXPENSE', 'Expense')], help_text='Type of category: INCOME or EXPENSE.', max_length=7, verbose_name='category type')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
            ],
            options={
                'verbose_name': 'category',
                'verbose_name_plural': 'categories',
                'ordering': ['type', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, help_text='Transaction amount (must be positive).', max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))], verbose_name='amount')),
                ('note', models.TextField(blank=True, default='', help_text='Optional description or note for the transaction.', verbose_name='note')),
                ('date', models.DateTimeField(help_text='Date and time of the transaction.', verbose_name='transaction date')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
            ],
            options={
                'verbose_name': 'transaction',
                'verbose_name_plural': 'transactions',
                'ordering': ['-date', '-created_at'],
            },
        ),
    ]
