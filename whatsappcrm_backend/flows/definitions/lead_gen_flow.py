# whatsappcrm_backend/flows/definitions/lead_gen_flow.py

LEAD_GENERATION_FLOW = {
    "name": "lead_generation",
    "friendly_name": "Lead Generation",
    "description": "A default flow to capture basic lead information like name, company, and email for new contacts.",
    "trigger_keywords": ['info', 'quote', 'details', 'pricing', 'demo'],
    "is_active": True,
    "steps": [
        {
            "name": "initial_greeting",
            "is_entry_point": True,
            "type": "question",
            "config": {
                "message_config": {
                    "message_type": "text",
                    "text": {"body": "Welcome to Havano! To get started, what is your full name?"}
                },
                "reply_config": {
                    "expected_type": "text",
                    "save_to_variable": "user_full_name",
                    "validation_regex": "^.{3,}"
                },
                "fallback_config": {
                    "action": "re_prompt",
                    "max_retries": 2,
                    "re_prompt_message_text": "Please enter a valid name."
                }
            },
            "transitions": [
                {"to_step": "process_name", "priority": 0, "condition_config": {"type": "variable_exists", "variable_name": "user_full_name"}}
            ]
        },
        {
            "name": "process_name",
            "type": "action",
            "config": {
                "actions_to_run": [{
                    "action_type": "update_customer_profile",
                    "fields_to_update": {
                        "first_name": "{{ user_full_name.split(' ')[0] }}",
                        "last_name": "{{ ' '.join(user_full_name.split(' ')[1:]) }}"
                    }
                }]
            },
            "transitions": [
                {"to_step": "ask_company", "priority": 0, "condition_config": {"type": "always_true"}}
            ]
        },
        {
            "name": "ask_company",
            "type": "question",
            "config": {
                "message_config": {
                    "message_type": "text",
                    "text": {"body": "Thanks, {{ customer_profile.first_name }}! What is the name of your company?"}
                },
                "reply_config": {
                    "expected_type": "text",
                    "save_to_variable": "company_name"
                }
            },
            "transitions": [
                {"to_step": "process_company", "priority": 0, "condition_config": {"type": "variable_exists", "variable_name": "company_name"}}
            ]
        },
        {
            "name": "process_company",
            "type": "action",
            "config": {
                "actions_to_run": [{
                    "action_type": "update_customer_profile",
                    "fields_to_update": {"company": "{{ company_name }}"}
                }]
            },
            "transitions": [
                {"to_step": "ask_email", "priority": 0, "condition_config": {"type": "always_true"}}
            ]
        },
        {
            "name": "ask_email",
            "type": "question",
            "config": {
                "message_config": {
                    "message_type": "text",
                    "text": {"body": "Great. And what is your business email address?"}
                },
                "reply_config": {
                    "expected_type": "email",
                    "save_to_variable": "user_email"
                },
                "fallback_config": {
                    "action": "re_prompt",
                    "max_retries": 2,
                    "re_prompt_message_text": "That doesn't seem to be a valid email address. Please try again (e.g., name@example.com)."
                }
            },
            "transitions": [
                {"to_step": "process_email", "priority": 0, "condition_config": {"type": "variable_exists", "variable_name": "user_email"}}
            ]
        },
        {
            "name": "process_email",
            "type": "action",
            "config": {
                "actions_to_run": [{
                    "action_type": "update_customer_profile",
                    "fields_to_update": {"email": "{{ user_email }}"}
                }]
            },
            "transitions": [
                {"to_step": "ask_interest", "priority": 0, "condition_config": {"type": "always_true"}}
            ]
        },
        {
            "name": "ask_interest",
            "type": "question",
            "config": {
                "message_config": {
                    "message_type": "text",
                    "text": {"body": "Thank you. To help us prepare, what specific products or services are you interested in?"}
                },
                "reply_config": {
                    "expected_type": "text",
                    "save_to_variable": "user_interest"
                }
            },
            "transitions": [
                {"to_step": "process_interest", "priority": 0, "condition_config": {"type": "variable_exists", "variable_name": "user_interest"}}
            ]
        },
        {
            "name": "process_interest",
            "type": "action",
            "config": {
                "actions_to_run": [{
                    "action_type": "update_customer_profile",
                    "fields_to_update": {"notes": "{{ (customer_profile.notes + '\n') if customer_profile.notes else '' }}Initial interest: {{ user_interest }}"}
                }]
            },
            "transitions": [
                {"to_step": "send_summary_and_end", "priority": 0, "condition_config": {"type": "always_true"}}
            ]
        },
        {
            "name": "send_summary_and_end",
            "type": "action",
            "config": {
                "actions_to_run": [{
                    "action_type": "send_admin_notification",
                    "message_template": (
                        "New Lead from {{ contact.name or contact.whatsapp_id }}:\n\n"
                        "Name: {{ customer_profile.first_name }} {{ customer_profile.last_name }}\n"
                        "Company: {{ customer_profile.company }}\n"
                        "Email: {{ customer_profile.email }}\n"
                        "Interest: {{ user_interest }}")
                }]
            },
            "transitions": [
                {"to_step": "end_flow_final", "priority": 1, "condition_config": {"type": "always_true"}}
            ]
        },
        {
            "name": "end_flow_final",
            "type": "end_flow",
            "config": {"message_config": {"message_type": "text", "text": {"body": "Thank you! We have collected your information. Our team will contact you soon."}}},
            "transitions": []
        }
    ]
}
