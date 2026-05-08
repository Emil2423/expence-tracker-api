from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_default_categories(sender, instance, created, **kwargs):
    if created:
        from transactions.models import Category
        default_categories = [
            {'name': 'Salary', 'type': 'INCOME'},
            {'name': 'Freelance', 'type': 'INCOME'},
            {'name': 'Investments', 'type': 'INCOME'},
            {'name': 'Other Income', 'type': 'INCOME'},
            {'name': 'Food & Dining', 'type': 'EXPENSE'},
            {'name': 'Transportation', 'type': 'EXPENSE'},
            {'name': 'Shopping', 'type': 'EXPENSE'},
            {'name': 'Entertainment', 'type': 'EXPENSE'},
            {'name': 'Bills & Utilities', 'type': 'EXPENSE'},
            {'name': 'Healthcare', 'type': 'EXPENSE'},
            {'name': 'Housing', 'type': 'EXPENSE'},
            {'name': 'Other Expenses', 'type': 'EXPENSE'},
        ]
        categories_to_create = [
            Category(
                name=cat['name'],
                type=cat['type'],
                user=instance,
            )
            for cat in default_categories
        ]
        Category.objects.bulk_create(categories_to_create)
