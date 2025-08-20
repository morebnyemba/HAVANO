# whatsappcrm_backend/customer_data/models.py

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone
from conversations.models import Contact
import uuid

class CustomerProfile(models.Model):
    """
    Stores aggregated and specific data about a customer, linked to their Contact record.
    This profile is enriched over time through conversations, forms, and manual entry.
    """
    contact = models.OneToOneField(
        Contact,
        on_delete=models.CASCADE,
        related_name='customer_profile',
        primary_key=True,
        help_text=_("The contact this customer profile belongs to.")
    )
    
    # Basic Info (can be synced or enriched)
    first_name = models.CharField(_("First Name"), max_length=100, blank=True, null=True)
    last_name = models.CharField(_("Last Name"), max_length=100, blank=True, null=True)
    email = models.EmailField(_("Email Address"), max_length=254, blank=True, null=True)
    company = models.CharField(_("Company"), max_length=150, blank=True, null=True)
    role = models.CharField(_("Role/Title"), max_length=100, blank=True, null=True)
    
    # Location Details
    address_line_1 = models.CharField(_("Address Line 1"), max_length=255, blank=True, null=True)
    address_line_2 = models.CharField(_("Address Line 2"), max_length=255, blank=True, null=True)
    city = models.CharField(_("City"), max_length=100, blank=True, null=True)
    state_province = models.CharField(_("State/Province"), max_length=100, blank=True, null=True)
    postal_code = models.CharField(_("Postal Code"), max_length=20, blank=True, null=True)
    country = models.CharField(_("Country"), max_length=100, blank=True, null=True)
    
    # Sales & Lead Information
    LEAD_STATUS_CHOICES = [
        ('new', _('New')),
        ('contacted', _('Contacted')),
        ('qualified', _('Qualified')),
        ('proposal_sent', _('Proposal Sent')),
        ('negotiation', _('Negotiation')),
        ('won', _('Won')),
        ('lost', _('Lost')),
        ('on_hold', _('On Hold')),
    ]
    lead_status = models.CharField(
        _("Lead Status"),
        max_length=50,
        choices=LEAD_STATUS_CHOICES,
        default='new',
        db_index=True,
        help_text=_("The current stage of the customer in the sales pipeline.")
    )
    potential_value = models.DecimalField(
        _("Potential Value"),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Estimated value of the deal or lifetime value of the customer.")
    )
    acquisition_source = models.CharField(
        _("Acquisition Source"),
        max_length=150, 
        blank=True, 
        null=True, 
        help_text=_("How this customer was acquired, e.g., 'Website Form', 'Cold Call', 'Referral'")
    )
    
    # Agent Assignment & Segmentation
    assigned_agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_index=True,
        related_name='assigned_customers',
        help_text=_("The sales or support agent assigned to this customer.")
    )
    tags = models.JSONField(
        _("Tags"),
        default=list, 
        blank=True, 
        help_text=_("Descriptive tags for segmentation, e.g., ['high-priority', 'tech-industry', 'follow-up']")
    )
    
    # Notes & Custom Data
    notes = models.TextField(
        _("Notes"), 
        blank=True, 
        null=True,
        help_text=_("General notes about the customer, their needs, or past interactions.")
    )
    custom_attributes = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Flexible field for storing custom data collected via forms or integrations.")
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_interaction_date = models.DateTimeField(
        _("Last Interaction Date"),
        null=True,
        blank=True,
        db_index=True,
        help_text=_("Timestamp of the last recorded interaction with this customer.")
    )

    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        return None

    def __str__(self):
        full_name = self.get_full_name()
        if full_name:
            return f"Customer: {full_name} ({self.contact.whatsapp_id})"
        return f"Customer: {self.contact.name or self.contact.whatsapp_id}"

    class Meta:
        verbose_name = _("Customer Profile")
        verbose_name_plural = _("Customer Profiles")
        ordering = ['-last_interaction_date', '-updated_at']


class Interaction(models.Model):
    """
    Represents a single interaction with a customer, such as a call, email, or meeting.
    This creates a historical log of all communications.
    """
    INTERACTION_TYPE_CHOICES = [
        ('call', _('Call')),
        ('email', 'Email'),
        ('whatsapp', _('WhatsApp Message')),
        ('meeting', _('Meeting')),
        ('note', _('Internal Note')),
        ('other', _('Other')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(
        CustomerProfile,
        on_delete=models.CASCADE,
        related_name='interactions',
        help_text=_("The customer this interaction is associated with.")
    )
    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='interactions',
        help_text=_("The agent who had the interaction.")
    )
    interaction_type = models.CharField(
        _("Interaction Type"),
        max_length=50,
        choices=INTERACTION_TYPE_CHOICES,
        default='note'
    )
    notes = models.TextField(
        _("Notes / Summary"),
        help_text=_("A summary of the interaction, key points, and next steps.")
    )
    created_at = models.DateTimeField(
        _("Interaction Time"),
        default=timezone.now,
        help_text=_("When the interaction occurred.")
    )

    def __str__(self):
        return f"{self.get_interaction_type_display()} with {self.customer} on {self.created_at.strftime('%Y-%m-%d')}"

    def save(self, *args, **kwargs):
        """
        Overrides save to update the customer's last_interaction_date.
        """
        # Save the interaction first
        super().save(*args, **kwargs)
        # Then, update the related customer profile
        # Use self.created_at as the source of truth for the interaction time
        if self.customer:
            self.customer.last_interaction_date = self.created_at
            self.customer.save(update_fields=['last_interaction_date'])

    class Meta:
        verbose_name = _("Interaction")
        verbose_name_plural = _("Interactions")
        ordering = ['-created_at']
