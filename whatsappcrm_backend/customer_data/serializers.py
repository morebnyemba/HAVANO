# whatsappcrm_backend/customer_data/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import CustomerProfile, Interaction
from conversations.models import Contact

User = get_user_model()

# A simple serializer for providing context on related models
class SimpleContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'whatsapp_id', 'name']

class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']

class CustomerProfileSerializer(serializers.ModelSerializer):
    # The primary key of CustomerProfile is 'contact', which is a OneToOneField.
    # DRF handles this, 'pk' in the URL will map to 'contact_id'.
    contact = SimpleContactSerializer(read_only=True)
    
    # To make choices human-readable in API responses
    lead_status_display = serializers.CharField(source='get_lead_status_display', read_only=True)
    
    # Nested serializer for the assigned agent
    assigned_agent = SimpleUserSerializer(read_only=True)
    # Writable field for assigning an agent by their ID
    assigned_agent_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='assigned_agent', write_only=True, allow_null=True, required=False
    )

    class Meta:
        model = CustomerProfile
        # The 'contact' field is the PK, so it's implicitly read-only here.
        fields = [
            'contact', 'first_name', 'last_name', 'email', 'company', 'role',
            'address_line_1', 'address_line_2', 'city', 'state_province', 'postal_code', 'country',
            'lead_status', 'lead_status_display', 'potential_value', 'acquisition_source',
            'assigned_agent', 'assigned_agent_id', 'tags', 'notes', 'custom_attributes',
            'created_at', 'updated_at', 'last_interaction_date'
        ]
        read_only_fields = ('created_at', 'updated_at', 'last_interaction_date')

class InteractionSerializer(serializers.ModelSerializer):
    # Display human-readable choice values
    interaction_type_display = serializers.CharField(source='get_interaction_type_display', read_only=True)
    
    # Provide context on the customer and agent
    customer = CustomerProfileSerializer(read_only=True)
    agent = SimpleUserSerializer(read_only=True)

    # Writable fields for creating an interaction
    customer_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomerProfile.objects.all(), source='customer', write_only=True
    )
    agent_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='agent', write_only=True, allow_null=True, required=False
    )

    class Meta:
        model = Interaction
        fields = [
            'id', 'customer', 'customer_id', 'agent', 'agent_id', 'interaction_type',
            'interaction_type_display', 'notes', 'created_at'
        ]
        read_only_fields = ('id', 'created_at')

    def create(self, validated_data):
        # If agent is not provided in the request, but there's a user in the context (e.g., logged-in user),
        # we can automatically assign them.
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            if 'agent' not in validated_data:
                validated_data['agent'] = request.user
        
        return super().create(validated_data)