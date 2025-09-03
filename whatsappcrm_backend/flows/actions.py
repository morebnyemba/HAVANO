# whatsappcrm_backend/flows/actions.py

import logging
from typing import Dict, Any, List
from .services import flow_action_registry
from conversations.models import Contact
from customer_data.models import CustomerProfile

logger = logging.getLogger(__name__)

def update_lead_score(contact: Contact, context: Dict[str, Any], params: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    A custom flow action to update a lead's score on their CustomerProfile.

    Params expected from flow config:
    - score_to_add (int): The number of points to add (can be negative).
    - reason (str): The reason for the score change, for logging.
    """
    score_to_add = params.get('score_to_add', 0)
    reason = params.get('reason', 'Score updated by flow')

    if not isinstance(score_to_add, int):
        logger.warning(f"Lead scoring for contact {contact.id} skipped: 'score_to_add' was not an integer.")
        return []

    profile, created = CustomerProfile.objects.get_or_create(contact=contact)
    if created:
        logger.info(f"Created CustomerProfile for contact {contact.id} during lead scoring.")
    
    # Ensure lead_score is an integer before performing arithmetic
    current_score = getattr(profile, 'lead_score', 0)
    if not isinstance(current_score, int):
        current_score = 0

    profile.lead_score = current_score + score_to_add
    profile.save(update_fields=['lead_score'])

    logger.info(f"Updated lead score for contact {contact.id} by {score_to_add}. New score: {profile.lead_score}. Reason: {reason}")
    
    return [] # This action does not return any messages to the user

# --- Register all custom actions here ---
flow_action_registry.register('update_lead_score', update_lead_score)

