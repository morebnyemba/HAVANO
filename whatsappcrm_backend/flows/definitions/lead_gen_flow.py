# whatsappcrm_backend/flows/definitions/lead_gen_flow.py

LEAD_GENERATION_FLOW = {
    "name": "lead_generation",
    "friendly_name": "Lead Generation",
     "description": "A comprehensive flow to qualify new leads by capturing contact details, business needs, and product interest.",
    "trigger_keywords": ['info', 'quote', 'details', 'pricing', 'demo', 'point of sale', 'pos'],
    "is_active": True,
    "steps": [
        {
            "name": "ask_name",
            "is_entry_point": True,
            "type": "question",
            "config": {
                "message_config": {
                    "message_type": "text",
                    "text": {"body": "Welcome to Havano! To get started, could I please have your full name?"}
                },
                "reply_config": {
                    "expected_type": "text",
                    "save_to_variable": "user_full_name",
                    "validation_regex": r"^.{3,}" # Require at least 3 characters
                },
                "fallback_config": {
                    "action": "re_prompt",
                    "max_retries": 2,
                    "re_prompt_message_text": "Please enter a valid full name."
                }
            },
            "transitions": [
                {"to_step": "process_name", "priority": 0, "condition_config": {"type": "variable_exists", "variable_name": "user_full_name"}},
            ]
        },
        {
            "name": "process_name",
            "type": "action",
            "config": {
                "actions_to_run": [
                    {"action_type": "update_contact_field", "field_path": "name", "value_template": "{{ user_full_name }}"},
                    {"action_type": "update_customer_profile", "fields_to_update": {
                        "first_name": "{{ user_full_name.split(' ')[0] }}",
                        "last_name": "{{ ' '.join(user_full_name.split(' ')[1:]) if ' ' in user_full_name else '' }}"
                    }}
                ]
            },
            "transitions": [
                {"to_step": "ask_company", "priority": 0, "condition_config": {"type": "always_true"}},
            ]
        },
        {
            "name": "ask_company",
            "type": "question",
            "config": {
                "message_config": {
                    "message_type": "text",
                    "text": {"body": "Thanks, {{ contact.customer_profile.first_name }}! What is the name of your company?"}
                },
                "reply_config": {
                    "expected_type": "text",
                    "save_to_variable": "company_name"
                }
            },
            "transitions": [
                {"to_step": "process_company", "priority": 0, "condition_config": {"type": "variable_exists", "variable_name": "company_name"}},
            ]
        },
        {
            "name": "process_company",
            "type": "action",
            "config": {
                "actions_to_run": [{"action_type": "update_customer_profile", "fields_to_update": {"company": "{{ company_name }}"}}]
            },
            "transitions": [
                {"to_step": "ask_email", "priority": 0, "condition_config": {"type": "always_true"}},
            ]
        },
        {
            "name": "ask_email",
            "type": "question",
            "config": {
                "message_config": {
                    "message_type": "text",
                    "text": {"body": "Great. And what is your business email address?"},
                },
                "reply_config": {"expected_type": "email", "save_to_variable": "user_email"},
                "fallback_config": {
                    "action": "re_prompt",
                    "max_retries": 2,
                    "re_prompt_message_text": "That doesn't seem to be a valid email address. Please try again (e.g., name@example.com).",
                }
            },
            "transitions": [
                {"to_step": "process_email", "priority": 0, "condition_config": {"type": "variable_exists", "variable_name": "user_email"}},
            ]
        },
        {
            "name": "process_email",
            "type": "action",
            "config": {
                "actions_to_run": [{"action_type": "update_customer_profile", "fields_to_update": {"email": "{{ user_email }}"}}]
            },
            "transitions": [
                {"to_step": "ask_business_type", "priority": 0, "condition_config": {"type": "always_true"}},
            ]
        },
        {
            "name": "ask_business_type",
            "type": "question",
            "config": {
                "message_config": {
                    "message_type": "text",
                    "text": {"body": "Perfect, thank you. What type of business are you into? (e.g., Retail, Restaurant, Salon)"}
                },
                "reply_config": {
                    "expected_type": "text",
                    "save_to_variable": "business_type"
                }
            },
            "transitions": [
                {"to_step": "process_business_type", "priority": 0, "condition_config": {"type": "variable_exists", "variable_name": "business_type"}}
            ]
        },
        {
            "name": "process_business_type",
            "type": "action",
            "config": {
                "actions_to_run": [{"action_type": "update_customer_profile", "fields_to_update": {"notes": "Business Type: {{ business_type }}"}}]
            },
            "transitions": [
                {"to_step": "ask_reason_for_new_system", "priority": 0, "condition_config": {"type": "always_true"}}
            ]
        },
        {
            "name": "ask_reason_for_new_system",
            "type": "question",
            "config": {
                "message_config": {
                    "message_type": "interactive",
                    "interactive": {
                        "type": "button",
                        "body": {"text": "Got it. What prompted you to look for a new system?"},
                        "action": {
                            "buttons": [
                                {"type": "reply", "reply": {"id": "reason_broken", "title": "System is Broken"}},
                                {"type": "reply", "reply": {"id": "reason_slow", "title": "System is Slow"}},
                                {"type": "reply", "reply": {"id": "reason_new_biz", "title": "New Business"}}
                            ]
                        }
                    }
                },
                "reply_config": {"save_to_variable": "reason_for_new_system", "expected_type": "interactive_id"}
            },
            "transitions": [
                {"to_step": "process_reason", "priority": 0, "condition_config": {"type": "always_true"}}
            ]
        },
        {
            "name": "process_reason",
            "type": "action",
            "config": {
                "actions_to_run": [{"action_type": "update_customer_profile", "fields_to_update": {"notes": "{{ customer_profile.notes }}\nReason for new system: {{ reason_for_new_system }}"}}]
            },
            "transitions": [
                {"to_step": "ask_location", "priority": 0, "condition_config": {"type": "always_true"}}
            ]
        },
        {
            "name": "ask_location",
            "type": "question",
            "config": {
                "message_config": {"message_type": "text", "text": {"body": "Understood. Where are you located?"}},
                "reply_config": {"save_to_variable": "customer_location", "expected_type": "text"}
            },
            "transitions": [
                {"to_step": "process_location", "priority": 0, "condition_config": {"type": "variable_exists", "variable_name": "customer_location"}}
            ]
        },
        {
            "name": "process_location",
            "type": "action",
            "config": {
                "actions_to_run": [{"action_type": "update_customer_profile", "fields_to_update": {"city": "{{ customer_location }}"}}]
            },
            "transitions": [
                {"to_step": "query_product_options", "priority": 0, "condition_config": {"type": "always_true"}}
            ]
        },
        {
            "name": "query_product_options",
            "type": "action",
            "config": {
                "actions_to_run": [{"action_type": "query_model", "app_label": "products_and_services", "model_name": "SoftwareProduct", "variable_name": "product_options", "filters_template": {"is_active": True, "category__name__icontains": "HAVANOERP"}, "order_by": ["name"], "limit": 5}]
            },
            "transitions": [
                {"to_step": "present_product_options", "priority": 10, "condition_config": {"type": "variable_exists", "variable_name": "product_options.0"}},
                {"to_step": "handle_no_products_found", "priority": 100, "condition_config": {"type": "always_true"}}
            ]
        },
        {
            "name": "present_product_options",
            "type": "question",
            "config": {
                "message_config": {
                    "message_type": "interactive",
                    "interactive": {
                        "type": "list", "header": {"type": "text", "text": "Available Options"},
                        "body": {"text": "Here are some options available. Which one did you like most?"},
                        "action": {"button": "View Products", "sections": [{"title": "Point of Sale Systems", "rows": "{{ product_options | to_interactive_rows }}"}]}
                    }
                },
                "reply_config": {"save_to_variable": "chosen_product_sku", "expected_type": "interactive_id"},
                "fallback_config": {"action": "re_prompt", "max_retries": 1, "re_prompt_message_text": "Please select a product from the list."}
            },
            "transitions": [
                {"to_step": "process_product_choice", "priority": 0, "condition_config": {"type": "variable_exists", "variable_name": "chosen_product_sku"}}
            ]
        },
        {
            "name": "handle_no_products_found",
            "type": "send_message",
            "config": {"message_type": "text", "text": {"body": "Apologies, I couldn't find specific product options right now. A team member will get in touch with a customized quote."}},
            "transitions": [
                {"to_step": "ask_when_to_follow_up", "priority": 1, "condition_config": {"type": "always_true"}}
            ]
        },
        {
            "name": "process_product_choice",
            "type": "action",
            "config": {
                "actions_to_run": [{"action_type": "update_customer_profile", "fields_to_update": {"notes": "{{ customer_profile.notes }}\nProduct Interest: {{ chosen_product_sku }}"}}]
            },
            "transitions": [
                {"to_step": "ask_when_to_follow_up", "priority": 0, "condition_config": {"type": "always_true"}}
            ]
        },
        {
            "name": "ask_when_to_follow_up",
            "type": "question",
            "config": {
                "message_config": {"message_type": "text", "text": {"body": "Thank you for your selection. When would be a good time for our team to follow up with you for a detailed discussion?"}},
                "reply_config": {"save_to_variable": "follow_up_time", "expected_type": "text"}
            },
            "transitions": [
                {"to_step": "send_summary_and_end", "priority": 0, "condition_config": {"type": "variable_exists", "variable_name": "follow_up_time"}}
            ]
        },
        {
            "name": "send_summary_and_end",
            "type": "action",
            "config": {
                "actions_to_run": [
                    {"action_type": "update_customer_profile", "fields_to_update": {"notes": "{{ customer_profile.notes }}\nFollow-up Time: {{ follow_up_time }}"}},
                    {"action_type": "send_admin_notification", "message_template": (
                        "New Lead from {{ contact.name or contact.whatsapp_id }}:\n\n"
                        "Name: {{ customer_profile.first_name }} {{ customer_profile.last_name }}\n"
                        "Company: {{ customer_profile.company }}\n"
                        "Email: {{ customer_profile.email }}\n"
                        "Business Type: {{ business_type }}\n"
                        "Reason: {{ reason_for_new_system }}\n"
                        "Location: {{ customer_location }}\n"
                        "Product SKU: {{ chosen_product_sku or 'N/A' }}\n"
                        "Follow-up: {{ follow_up_time }}"
                    )}
                ]
            },
            "transitions": [
                {"to_step": "end_flow_final", "priority": 1, "condition_config": {"type": "always_true"}},
            ]
        },
        {
            "name": "end_flow_final",
            "type": "end_flow",
            "config": {"message_config": {"message_type": "text", "text": {"body": "Perfect! We have all the details. A representative will contact you around {{ follow_up_time }}. Thank you for your interest in Havano!"}}},
            "transitions": []
        }
    ]
}
