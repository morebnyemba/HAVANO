from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid

class ProductCategory(models.Model):
    """
    A category for organizing products and services.
    Supports nested categories.
    """
    name = models.CharField(_("Category Name"), max_length=255, unique=True)
    description = models.TextField(_("Description"), blank=True, null=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        help_text=_("Parent category for creating a hierarchy.")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Product Category")
        verbose_name_plural = _("Product Categories")
        ordering = ['name']

class Product(models.Model):
    """
    Represents a physical or digital product that can be sold.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Product Name"), max_length=255)
    description = models.TextField(_("Description"), blank=True, null=True)
    sku = models.CharField(_("SKU (Stock Keeping Unit)"), max_length=100, unique=True, blank=True, null=True)
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
    )
    price = models.DecimalField(_("Price"), max_digits=12, decimal_places=2)
    currency = models.CharField(_("Currency"), max_length=3, default='USD')
    stock_quantity = models.PositiveIntegerField(_("Stock Quantity"), default=0, help_text=_("Available stock. 0 for unlimited or digital products."))
    is_active = models.BooleanField(
        _("Is Active"),
        default=True,
        help_text=_("Whether the product is available for sale.")
    )
    image = models.ImageField(_("Product Image"), upload_to='products/', blank=True, null=True, help_text=_("An image of the product. Requires the 'Pillow' library."))
    attributes = models.JSONField(
        _("Attributes"),
        default=dict,
        blank=True,
        help_text=_("Custom attributes like size, color, etc. E.g., {'color': 'Red', 'size': 'L'}")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.sku or 'No SKU'})"

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        ordering = ['name']

class Service(models.Model):
    """
    Represents a service that can be offered to customers.
    """
    class BillingCycle(models.TextChoices):
        ONE_TIME = 'one_time', _('One-Time')
        MONTHLY = 'monthly', _('Monthly')
        QUARTERLY = 'quarterly', _('Quarterly')
        YEARLY = 'yearly', _('Yearly')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Service Name"), max_length=255)
    description = models.TextField(_("Description"), blank=True, null=True)
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='services'
    )
    price = models.DecimalField(_("Price"), max_digits=12, decimal_places=2)
    currency = models.CharField(_("Currency"), max_length=3, default='USD')
    billing_cycle = models.CharField(
        _("Billing Cycle"),
        max_length=20,
        choices=BillingCycle.choices,
        default=BillingCycle.ONE_TIME
    )
    is_active = models.BooleanField(
        _("Is Active"),
        default=True,
        help_text=_("Whether the service is currently offered.")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_billing_cycle_display()})"

    class Meta:
        verbose_name = _("Service")
        verbose_name_plural = _("Services")
        ordering = ['name']
