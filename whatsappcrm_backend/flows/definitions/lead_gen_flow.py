# flows/definitions/lead_gen_flow.py

"""
Collects information from new users and presents product options.
"""

LEAD_GENERATION_FLOW = {
    "name": "lead_generation",
    "friendly_name": "New Lead Information and Product Selection",
    "description": "Collects initial info from new users and presents product options based on ad source.",
    "trigger_keywords": [], # Triggered only on first incoming message
    "is_active": True,
    "steps": [
        {
            "name": "initial_greeting",
            "is_entry_point": True,
            "type": "send_message",
            "config": {
                "message_type": "text",
                "text": {"body": "{{ trigger_message.text_content }}\n\nWelcome! To best assist you, I need a little more information."}
            },
            "transitions": [{"to_step": "refine_initial_greeting", "condition_config": {"type": "always_true"}}]
        },
        {
            "name": "ask_business_type",
            "type": "question",
            "config": {
                "message_config": {
                    "message_type": "text",
                    "text": {"body": "What type of business are you into?"}
                },
                "reply_config": {"save_to_variable": "business_type", "expected_type": "text"},
                "fallback_config": {"action": "re_prompt", "max_retries": 1, "re_prompt_message_text": "Please enter the type of business."}
            },
            "transitions": [{"to_step": "ask_reason_for_new_system", "condition_config": {"type": "always_true"}}]
        },
        {
            "name": "ask_reason_for_new_system",
            "type": "question",
            "config": {
                "message_config": {
                    "message_type": "interactive",
                    "interactive": {
                        "type": "list",
                        "header": {"type": "text", "text": "New System Reason"},
                        "body": {"text": "What prompted you to look for a new system?"},
                        "action": {
                            "button": "Select Reason",
                            "sections": [
                                {
                                    "title": "Reasons",
                                    "rows": [
                                        {"id": "scalability", "title": "Scalability"},
                                        {"id": "cost", "title": "Reduce Costs"},
                                        {"id": "features", "title": "Need More Features"},
                                        {"id": "integration", "title": "Better Integration"},
                                        {"id": "support", "title": "Poor Support"}
                                    ]
                                }
                            ]
                        }
                    }
                },
                "reply_config": {"save_to_variable": "reason_for_new_system", "expected_type": "interactive_id"},
                "fallback_config": {"action": "re_prompt", "max_retries": 1, "re_prompt_message_text": "Please select a reason from the list."}
            },
            "transitions": [{"to_step": "ask_location", "condition_config": {"type": "always_true"}}]
        },
        {
            "name": "ask_location",
            "type": "question",
            "config": {
                "message_type": "text",
                "text": {"body": "Where are you located?"}
            },
            "reply_config": {"save_to_variable": "customer_location", "expected_type": "text"},
            "fallback_config": {"action": "re_prompt", "max_retries": 1, "re_prompt_message_text": "Please enter your location."}
            },
            "transitions": [{"to_step": "query_product_options", "condition_config": {"type": "always_true"}}]
        },
        {
            "name": "query_product_options",
            "type": "action",
            "config": {
                "actions_to_run": [{
                    "action_type": "query_model",
                    "app_label": "products_and_services",
                    "model_name": "SoftwareProduct",
                    "variable_name": "product_options",
                    "filters_template": {"is_active": True},
                    "order_by": ["name"]
                }]
            },
            "transitions": [{"to_step": "check_if_products_exist", "condition_config": {"type": "always_true"}}]
        },
        {
            "name": "check_if_products_exist",
            "type": "action",
            "config": {"actions_to_run": []},
            "transitions": [
                {"to_step": "present_and_record_product_choice", "priority": 10, "condition_config": {"type": "variable_exists", "variable_name": "product_options.0"}},
                {"to_step": "no_products_available_message", "priority": 20, "condition_config": {"type": "always_true"}}
            ]
        },
        {
            "name": "no_products_available_message",
            "type": "send_message",
            "config": {"message_type": "text", "text": {"body": "Apologies, it seems we don't have any active software products available right now. Please check back later or contact us directly."}},
            "transitions": [{"to_step": "end_flow", "condition_config": {"type": "always_true"}}]
        },
        {
            "name": "present_and_record_product_choice",
            "type": "send_message",
            "config": {
                "message_type": "interactive",
                "interactive": {
                    "type": "list",
                    "header": {"type": "text", "text": "Product Options"},
                    "body": {"text": "Here are some options. Which one did you like most?"},
                    "action": {
                        "button": "View Products",
                        "sections": [{
                            "title": "Available Products",
                            "rows": [
                                {"id": "{{ product.sku }}", "title": "{{ product.name }}", "description": "${{ product.price }}"}
                                for product in "{{ product_options }}"
                            ]
                        }]
                    }
                }
            },
                "reply_config": {"save_to_variable": "chosen_product_sku", "expected_type": "interactive_id"},
                "fallback_config": {"action": "re_prompt", "max_retries": 1, "re_prompt_message_text": "Please select a product from the provided options by tapping the button and choosing from the list."}
            },
            "transitions": [{"to_step": "ask_when_to_follow_up", "condition_config": {"type": "always_true"}}]
        },
        {
            "name": "refine_initial_greeting",
            "type": "send_message",
            "config": {"message_type": "text", "text": {"body": "Welcome! To best assist you, I need a little more information."}},
            "transitions": [{"to_step": "ask_business_type", "condition_config": {"type": "always_true"}}]
        },
        {
            "name": "ask_when_to_follow_up",
            "type": "question",
            "config": {
                "message_type": "text",
                "text": {"body": "When would be a good time for our team to follow up with you?"}
            },
            "reply_config": {"save_to_variable": "follow_up_time", "expected_type": "text"},
            "transitions": [{"to_step": "create_lead", "condition_config": {"type": "always_true"}}]
        },
        {
            "name": "create_lead",
            "type": "action",
            "config": {
                "actions_to_run": [
                    {
                        "action_type": "create_opportunity",
                        "params_template": {
                            "name": "New Lead - {{ business_type }}",
                            "stage": "prospecting",
                            "software_product_sku": "{{ chosen_product_sku }}",
                            "description": "Business Type: {{ business_type }}.\nReason: {{ reason_for_new_system }}.\nLocation: {{ customer_location }}.\nFollow-up: {{ follow_up_time }}",
                            "confirmation_text": "Thank you! We have collected your information. Our team will contact you soon."
                        }
                    }
                ]
            },
            "transitions": [{"to_step": "end_flow", "condition_config": {"type": "always_true"}}]
        },
        {
            "name": "end_flow",
            "type": "end_flow",
            "config": {"message_config": {"message_type": "text", "text": {"body": "Thank you for your interest!"}}},
            "transitions": []
        }
    ]                       "description": "Business Type: {{ business_type }}.\nReason: {{ reason_for_new_system }}.\nLocation: {{ customer_location }}.\nFollow-up: {{ follow_up_time }}",
                            "confirmation_text": "Thank you! We have collected your information. Our team will contact you soon."
                        }
                    }
                ]
            },
            "transitions": [{"to_step": "end_flow", "condition_config": {"type": "always_true"}}]
        },
        {
            "name": "end_flow",
            "type": "end_flow",
            "config": {"message_config": {"message_type": "text", "text": {"body": "Thank you for your interest!"}}},
            "transitions": []
        }
    ]
}