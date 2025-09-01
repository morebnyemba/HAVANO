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
            "step_type": "send_message",
            "config": {
                "message_config": {
                    "message_type": "text",
                    "text": {"body": "Welcome! To best assist you, I need a little more information."}
                }
            },
            "transitions": [
                {"next_step": "ask_business_type", "priority": 1, "condition_config": {"type": "always_true"}}
            ]
        },
        {
            "name": "ask_business_type",
            "step_type": "question",
            "config": {
                "message_config": {
                    "message_type": "interactive",
                    "interactive": {
                        "type": "button",
                        "body": {"text": "What type of business do you run?"},
                        "action": {
                            "buttons": [
                                {"type": "reply", "reply": {"id": "retail", "title": "Retail"}},
                                {"type": "reply", "reply": {"id": "restaurant", "title": "Restaurant"}},
                                {"type": "reply", "reply": {"id": "other", "title": "Other"}}
                            ]
                        }
                    }
                },
                "reply_config": {"save_to_variable": "business_type", "expected_type": "interactive_id"},
                "fallback_config": {"action": "re_prompt", "max_retries": 1, "re_prompt_message_text": "Please select a business type from the buttons."}
            },
            "transitions": [
                {
                    "next_step": "ask_other_business_type",
                    "priority": 10,
                    "condition_config": {"type": "variable_equals", "variable_name": "business_type", "value": "other"}
                },
                {
                    "next_step": "ask_reason_for_new_system",
                    "priority": 100,
                    "condition_config": {"type": "always_true"}
                }
            ]
        },
        {
            "name": "ask_other_business_type",
            "step_type": "question",
            "config": {
                "message_config": {
                    "message_type": "text",
                    "text": {"body": "Could you please specify your business type?"}
                },
                "reply_config": {"save_to_variable": "other_business_type_details", "expected_type": "text"}
            },
            "transitions": [
                {
                    "next_step": "ask_reason_for_new_system", "priority": 1, "condition_config": {"type": "always_true"}
                }
            ]
        },
        {
            "name": "ask_reason_for_new_system",
            "step_type": "question",
            "config": {
                "message_config": {
                    "message_type": "text",
                    "text": {"body": "What is the main reason you are looking for a new system?"}
                },
                "reply_config": {"save_to_variable": "reason_for_new_system", "expected_type": "text"},
                "fallback_config": {"action": "re_prompt", "max_retries": 1, "re_prompt_message_text": "Please tell me the main reason you're looking for a new system."}
            },
            "transitions": [
                {
                    "next_step": "handle_urgent_case",
                    "priority": 10,
                    "condition_config": {"type": "user_reply_contains_keyword", "keyword": "broken", "case_sensitive": False}
                },
                {
                    "next_step": "handle_urgent_case",
                    "priority": 11, # Slightly lower priority than 'broken'
                    "condition_config": {"type": "user_reply_contains_keyword", "keyword": "slow", "case_sensitive": False}
                },
                {
                    "next_step": "ask_location",
                    "priority": 100,
                    "condition_config": {"type": "always_true"}
                }
            ]
        },
        {
            "name": "handle_urgent_case",
            "step_type": "send_message",
            "config": {"message_config": {"message_type": "text", "text": {"body": "I see. It sounds like this is urgent. Let me get your location so we can proceed."}}},
            "transitions": [
                {"next_step": "ask_location", "priority": 1, "condition_config": {"type": "always_true"}}
            ]
        },
        {
            "name": "ask_location",
            "step_type": "question",
            "config": {
                "message_config": {
                    "message_type": "text",
            "transitions": [
                {"next_step": "query_product_options", "priority": 1, "condition_config": {"type": "always_true"}}
            ]
        },
        {
            "name": "query_product_options",
            "step_type": "action",
            "config": {
                "actions_to_run": [{
                    "action_type": "query_model",
                    "app_label": "products_and_services",
                    "model_name": "SoftwareProduct",
                    "variable_name": "product_options",
                    "filters_template": {"is_active": True, "product__sku": "HAVANO-ERP"},
                    "order_by": ["name"],
                    "limit": 5
                }]
            },
            "transitions": [
                {
                    "next_step": "present_and_record_product_choice",
                    "priority": 10,
                    "condition_config": {"type": "variable_exists", "variable_name": "product_options.0"}
                },
                {
                    "next_step": "handle_no_products_found",
                    "priority": 100,
                    "condition_config": {"type": "always_true"}
                }
            ]
        },
        {
            "name": "handle_no_products_found",
            "step_type": "send_message",
            "config": {
                "message_config": {
                    "message_type": "text",
                    "text": {"body": "Apologies, but we couldn't find any specific products for your location at this moment. We've noted your interest, however."}
                }
            },
            "transitions": [
                {"next_step": "ask_when_to_follow_up", "priority": 1, "condition_config": {"type": "always_true"}}
            ]
        },
        {
            "name": "present_and_record_product_choice",
            "step_type": "question",
            "config": {
                "message_config": {
                    "message_type": "interactive",
                    "interactive": {
                        "type": "list",
                        "header": {"type": "text", "text": "Product Options"},
                        "body": {"text": "Here are some options. Which one did you like most?"},
                        "action": {
                            "button": "View Products",
                            "sections": [{
                                "title": "Available Products",
                                "rows": "{{ product_options | to_interactive_rows }}"
                            }]
                        }
                    }
                },
                "reply_config": {"save_to_variable": "chosen_product_sku", "expected_type": "interactive_id"},
                "fallback_config": {"action": "re_prompt", "max_retries": 1, "re_prompt_message_text": "Please select a product from the provided options by tapping the button and choosing from the list."}
            },
            "transitions": [
                {"next_step": "ask_when_to_follow_up", "priority": 1, "condition_config": {"type": "always_true"}}
            ]
        },
        {
            "name": "ask_when_to_follow_up",
            "step_type": "question",
            "config": {
                "message_config": {"message_type": "text", "text": {"body": "Great! When would be a good time for our team to follow up with you?"}},
                "reply_config": {"save_to_variable": "follow_up_time", "expected_type": "text"},
                "fallback_config": {"action": "re_prompt", "max_retries": 1, "re_prompt_message_text": "Please let us know when we should follow up."}
            },
            "transitions": [
                {"next_step": "send_summary_and_end", "priority": 1, "condition_config": {"type": "always_true"}}
            ]
        },
        {
            "name": "send_summary_and_end",
            "step_type": "action",
            "config": {
                "actions_to_run": [{
                    "action_type": "send_admin_notification",
                    "message_template": "New Lead from {{ contact.name or contact.whatsapp_id }}:\n- Business Type: {{ business_type }}{% if other_business_type_details %}\n- Other Details: {{ other_business_type_details }}{% endif %}\n- Reason: {{ reason_for_new_system }}\n- Location: {{ customer_location }}{% if chosen_product_sku %}\n- Chosen Product SKU: {{ chosen_product_sku }}{% endif %}\n- Follow-up Time: {{ follow_up_time }}"
                }]
            },
            "transitions": [
                {"next_step": "end_flow_final", "priority": 1, "condition_config": {"type": "always_true"}}
            ]
        },
        {
            "name": "end_flow_final",
            "step_type": "end_flow",
            "config": {"message_config": {"message_type": "text", "text": {"body": "Thank you! We have collected your information. Our team will contact you soon."}}},
            "transitions": []
        }
    ]
}
                    "text": {"body": "Where are you located?"}
                },
                "reply_config": {"save_to_variable": "customer_location", "expected_type": "text"},
                "fallback_config": {"action": "re_prompt", "max_retries": 1, "re_prompt_message_text": "Please enter your location."}
            },
            "transitions": [{"to_step": "query_product_options", "priority": 1, "condition_config": {"type": "always_true"}}]
        },
        {
            "name": "query_product_options",
            "type": "action",
            "config": {
                "actions_to_run": [{
                    "action_type": "query_model",
                    "app_label": "products",
                    "model_name": "Product",
                    "variable_name": "product_options",
                    "filters_template": {"is_active": True, "available_in__icontains": "{{ customer_location }}"},
                    "order_by": ["-created_at"],
                    "limit": 3
                }]
            },
            "transitions": [
                {
                    "to_step": "handle_no_products_found",
                    "priority": 10,
                    "condition_config": {"type": "variable_equals", "variable_name": "product_options", "value": "[]"}
                },
                {
                    "to_step": "present_and_record_product_choice",
                    "priority": 100,
                    "condition_config": {"type": "always_true"}
                }
            ]
        },
        {
            "name": "handle_no_products_found",
            "type": "send_message",
            "config": {
                "message_config": {
                    "message_type": "text",
                    "text": {"body": "Apologies, but we couldn't find any specific products for your location at this moment. We've noted your interest, however."}
                }
            },
            "transitions": [{"to_step": "ask_when_to_follow_up", "priority": 1, "condition_config": {"type": "always_true"}}]
        },
        {
            "name": "present_and_record_product_choice",
            "type": "question",
            "config": {
                "message_config": {
                    "message_type": "interactive",
                    "interactive": {
                        "type": "list",
                        "header": {"type": "text", "text": "Product Options"},
                        "body": {"text": "Here are some options. Which one did you like most?"},
                        "action": {
                            "button": "View Products",
                            "sections": [{
                                "title": "Available Products",
                                "rows": "{{ product_options | to_interactive_rows }}"
                            }]
                        }
                    }
                },
                "reply_config": {"save_to_variable": "chosen_product_sku", "expected_type": "interactive_id"},
                "fallback_config": {"action": "re_prompt", "max_retries": 1, "re_prompt_message_text": "Please select a product from the provided options by tapping the button and choosing from the list."}
            },
            "transitions": [{"to_step": "ask_when_to_follow_up", "priority": 1, "condition_config": {"type": "always_true"}}]
        },
        {
            "name": "ask_when_to_follow_up",
            "type": "question",
            "config": {
                "message_config": {"message_type": "text", "text": {"body": "Great! When would be a good time for our team to follow up with you?"}},
                "reply_config": {"save_to_variable": "follow_up_time", "expected_type": "text"},
                "fallback_config": {"action": "re_prompt", "max_retries": 1, "re_prompt_message_text": "Please let us know when we should follow up."}
            },
            "transitions": [{"to_step": "send_summary_and_end", "priority": 1, "condition_config": {"type": "always_true"}}]
        },
        {
            "name": "send_summary_and_end",
            "type": "action",
            "config": {
                "actions_to_run": [{
                    "action_type": "send_admin_notification",
                    "message_template": "New Lead from {{ contact.name or contact.whatsapp_id }}:\n- Business Type: {{ business_type }}{% if other_business_type_details %}\n- Other Details: {{ other_business_type_details }}{% endif %}\n- Reason: {{ reason_for_new_system }}\n- Location: {{ customer_location }}{% if chosen_product_sku %}\n- Chosen Product SKU: {{ chosen_product_sku }}{% endif %}\n- Follow-up Time: {{ follow_up_time }}"
                }]
            },
            "transitions": [{"to_step": "end_flow_final", "priority": 1, "condition_config": {"type": "always_true"}}]
        },
        {
            "name": "end_flow_final",
            "type": "end_flow",
            "config": {"message_config": {"message_type": "text", "text": {"body": "Thank you! We have collected your information. Our team will contact you soon."}}},
            "transitions": []
        }
    ]
}
# Note: This flow captures lead information, handles urgent cases, queries product options based on location,
# and sends a summary notification to admins. It uses buttons and lists for better user interaction.
