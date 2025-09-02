# whatsappcrm_backend/flows/definitions/lead_gen_flow.py

LEAD_GENERATION_FLOW = {
    "name": "lead_generation",
    "friendly_name": "Lead Generation",
     "description": "A comprehensive flow to qualify new leads by capturing contact details, business needs, and product interest.",
    "trigger_keywords": ['info', 'quote', 'details', 'pricing', 'demo', 'point of sale', 'pos'],
    "is_active": True,
    "steps": [
        {
            "name": "check_customer_status",
            "is_entry_point": True,
            "type": "action",
            "config": {
                "actions_to_run": [{
                    "action_type": "set_context_variable",
                    "variable_name": "is_returning_customer",
                    "value_template": "{{ 'yes' if customer_profile.first_name else 'no' }}"
                }]
            },
            "transitions": [
                {"to_step": "greet_returning_customer", "priority": 0, "condition_config": {"type": "variable_equals", "variable_name": "is_returning_customer", "value": "yes"}},
                {"to_step": "ask_name", "priority": 1, "condition_config": {"type": "always_true"}},
            ]
        },
        {
            "name": "greet_returning_customer",
            "type": "send_message",
            "config": {
                "message_config": {
                    "message_type": "text",
                    "text": {"body": "Welcome back, {{ customer_profile.first_name }}! Let's find what you're looking for."}
                }
            },
            "transitions": [
                {"to_step": "check_for_trigger_category", "priority": 0, "condition_config": {"type": "always_true"}}
            ]
        },
        {
            "name": "ask_name",
            "is_entry_point": False,
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
                    {"action_type": "update_contact_field", "field_path": "name", "value_template": "{{ user_full_name }}"}, # Updates Contact.name
                    {"action_type": "update_customer_profile", "fields_to_update": {
                        "first_name": "{{ user_full_name.split(' ')[0] if ' ' in user_full_name else user_full_name }}",
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
                    "text": {"body": "Thanks, {{ customer_profile.first_name }}! What is the name of your company?"}
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
                {"to_step": "ask_role", "priority": 0, "condition_config": {"type": "always_true"}},
            ]
        },
        {
            "name": "ask_role",
            "type": "question",
            "config": {
                "message_config": {"message_type": "text", "text": {"body": "And what is your role at {{ company_name }}?"}},
                "reply_config": {"expected_type": "text", "save_to_variable": "user_role"}
            },
            "transitions": [
                {"to_step": "process_role", "priority": 0, "condition_config": {"type": "variable_exists", "variable_name": "user_role"}}
            ]
        },
        {
            "name": "process_role",
            "type": "action",
            "config": {
                "actions_to_run": [{"action_type": "update_customer_profile", "fields_to_update": {"role": "{{ user_role }}"}}]
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
                {"to_step": "ask_phone_confirmation", "priority": 0, "condition_config": {"type": "always_true"}},
            ]
        },
        {
            "name": "ask_phone_confirmation",
            "type": "question",
            "config": {
                "message_config": {
                    "message_type": "interactive",
                    "interactive": {
                        "type": "button",
                        "body": {"text": "Perfect. Can our team use this number ({{ contact.whatsapp_id }}) to call you for a follow-up?"},
                        "action": {
                            "buttons": [
                                {"type": "reply", "reply": {"id": "confirm_phone_yes", "title": "Yes, that's fine"}},
                                {"type": "reply", "reply": {"id": "confirm_phone_no", "title": "Use another number"}}
                            ]
                        }
                    }
                },
                "reply_config": {"expected_type": "interactive_id", "save_to_variable": "phone_confirmation"}
            },
            "transitions": [
                {"to_step": "ask_business_type", "priority": 0, "condition_config": {"type": "interactive_reply_id_equals", "value": "confirm_phone_yes"}},
                {"to_step": "ask_alternative_phone", "priority": 1, "condition_config": {"type": "interactive_reply_id_equals", "value": "confirm_phone_no"}}
            ]
        },
        {
            "name": "ask_alternative_phone",
            "type": "question",
            "config": {
                "message_config": {"message_type": "text", "text": {"body": "No problem. What number should we use? Please include the country code (e.g., +14155552671)."}},
                "reply_config": {"expected_type": "text", "save_to_variable": "alternative_phone", "validation_regex": r"^\+?[1-9]\d{1,14}$"},
                "fallback_config": {"action": "re_prompt", "max_retries": 1, "re_prompt_message_text": "That doesn't look like a valid phone number. Please try again."}
            },
            "transitions": [
                {"to_step": "process_alternative_phone", "priority": 0, "condition_config": {"type": "variable_exists", "variable_name": "alternative_phone"}}
            ]
        },
        {
            "name": "process_alternative_phone",
            "type": "action",
            "config": {
                "actions_to_run": [{"action_type": "update_customer_profile", "fields_to_update": {"notes": "Alternative Phone: {{ alternative_phone }}\\n---\\n{{ customer_profile.notes }}"}}]
            },
            "transitions": [
                {"to_step": "ask_business_type", "priority": 0, "condition_config": {"type": "always_true"}}
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
                "actions_to_run": [{"action_type": "set_context_variable", "variable_name": "lead_notes", "value_template": "Business Type: {{ business_type }}"}]
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
                    "message_type": "text",
                    "text": {"body": "Got it. What prompted you to look for a new system?"}
                },
                "reply_config": {"save_to_variable": "reason_for_new_system", "expected_type": "text"}
            },
            "transitions": [
                {"to_step": "process_reason", "priority": 0, "condition_config": {"type": "always_true"}}
            ]
        },
        {
            "name": "process_reason",
            "type": "action",
            "config": {
                "actions_to_run": [{"action_type": "set_context_variable", "variable_name": "lead_notes", "value_template": "{{ lead_notes }}\nReason for new system: {{ reason_for_new_system }}"}]
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
                {"to_step": "check_for_trigger_category", "priority": 0, "condition_config": {"type": "always_true"}}
            ]
        },
        {
            "name": "check_for_trigger_category",
            "type": "action",
            "config": {"actions_to_run": []},
            "transitions": [
                {"to_step": "query_by_category", "priority": 0, "condition_config": {"type": "variable_exists", "variable_name": "product_category_from_trigger"}},
                {"to_step": "query_all_products", "priority": 1, "condition_config": {"type": "always_true"}}
            ]
        },
        {
            "name": "query_by_category",
            "type": "action",
            "config": {
                "actions_to_run": [{
                    "action_type": "query_model",
                    "app_label": "products_and_services",
                    "model_name": "SoftwareProduct",
                    "variable_name": "product_options",
                    "filters_template": {
                        "is_active": True,
                        "category__name__icontains": "{{ product_category_from_trigger }}"
                    },
                    "order_by": ["name"],
                    "limit": 3
                }]
            },
            "transitions": [
                {"to_step": "present_product_options", "priority": 0, "condition_config": {"type": "variable_exists", "variable_name": "product_options.0"}},
                {"to_step": "handle_no_products_found", "priority": 1, "condition_config": {"type": "always_true"}}
            ]
        },
        {
            "name": "query_all_products",
            "type": "action",
            "config": {
                "actions_to_run": [{"action_type": "query_model", "app_label": "products_and_services", "model_name": "SoftwareProduct", "variable_name": "product_options", "filters_template": {"is_active": True}, "order_by": ["name"], "limit": 3}]
            },
            "transitions": [
                {"to_step": "present_product_options", "priority": 0, "condition_config": {"type": "variable_exists", "variable_name": "product_options.0"}},
                {"to_step": "handle_no_products_found", "priority": 1, "condition_config": {"type": "always_true"}}
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
                {"to_step": "query_chosen_product", "priority": 0, "condition_config": {"type": "variable_exists", "variable_name": "chosen_product_sku"}}
            ]
        },
        {
            "name": "query_chosen_product",
            "type": "action",
            "config": {
                "actions_to_run": [{
                    "action_type": "query_model",
                    "app_label": "products_and_services",
                    "model_name": "SoftwareProduct",
                    "variable_name": "chosen_product_details",
                    "filters_template": {"sku": "{{ chosen_product_sku }}"},
                    "limit": 1
                }]
            },
            "transitions": [
                {"to_step": "show_product_details", "priority": 0, "condition_config": {"type": "variable_exists", "variable_name": "chosen_product_details.0"}},
                {"to_step": "ask_when_to_follow_up", "priority": 1, "condition_config": {"type": "always_true"}}
            ]
        },
        {
            "name": "show_product_details",
            "type": "send_message",
            "config": {
                "message_config": {
                    "message_type": "image",
                    "image": {
                        "link": "{{ chosen_product_details.0.image }}",
                        "caption": "Great choice! Here are the details for the *{{ chosen_product_details.0.name }}*:\n\n{{ chosen_product_details.0.description }}\n\n*Price*: ${{ chosen_product_details.0.price }} {{ chosen_product_details.0.currency }}\n*License*: {{ chosen_product_details.0.license_type }}"
                    }
                }
            },
            "transitions": [
                {"to_step": "ask_next_action", "priority": 0, "condition_config": {"type": "always_true"}}
            ]
        },
        {
            "name": "ask_next_action",
            "type": "question",
            "config": {
                "message_config": {
                    "message_type": "interactive",
                    "interactive": {
                        "type": "button",
                        "body": {"text": "What would you like to do next?"},
                        "action": { "buttons": [
                            {"type": "reply", "reply": {"id": "schedule_demo", "title": "Schedule a Demo"}},
                            {"type": "reply", "reply": {"id": "talk_to_sales", "title": "Talk to Sales"}},
                            {"type": "reply", "reply": {"id": "ask_question", "title": "Ask a Question"}}
                        ]}
                    }
                },
                "reply_config": {"expected_type": "interactive_id", "save_to_variable": "next_action_choice"}
            },
            "transitions": [
                {"to_step": "process_product_choice", "priority": 0, "condition_config": {"type": "variable_exists", "variable_name": "next_action_choice"}}
            ]
        },
        {
            "name": "handle_no_products_found",
            "type": "send_message",
            "config": {
                "message_config": {
                    "message_type": "text", 
                    "text": {"body": "Apologies, I couldn't find specific product options right now. A team member will get in touch with a customized quote."}
                }
            },
            "transitions": [
                {"to_step": "ask_when_to_follow_up", "priority": 1, "condition_config": {"type": "always_true"}}
            ]
        },
        {
            "name": "process_product_choice",
            "type": "action",
            "config": {
                "actions_to_run": [{"action_type": "set_context_variable", "variable_name": "lead_notes", "value_template": "{{ lead_notes }}\\nProduct Interest: {{ chosen_product_sku }}\\nNext Step: {{ next_action_choice | default('Follow-up') }}"}]
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
                    {"action_type": "set_context_variable", "variable_name": "lead_notes", "value_template": "{{ lead_notes }}\nFollow-up Time: {{ follow_up_time }}"},
                    {"action_type": "update_customer_profile", "fields_to_update": {"notes": "{{ lead_notes }}"}},
                    {"action_type": "send_admin_notification", "message_template": (
                        "New Lead from {{ contact.name or contact.whatsapp_id }}:\n\n"
                        "Name: {{ customer_profile.first_name }} {{ customer_profile.last_name or '' }}\n"
                        "Company: {{ customer_profile.company }}\n"
                        "Email: {{ customer_profile.email }}\n"
                        "Notes:\n{{ lead_notes }}"
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
