# whatsappcrm_backend/flows/definitions/fiscalisation_flow.py

FISCALISATION_FLOW = {
    "name": "fiscalisation_service",
    "friendly_name": "Fiscalisation Service Inquiry",
    "description": "A flow to handle inquiries about fiscalisation services, gather requirements, and create a lead.",
    "trigger_keywords": ['fiscalisation', 'zimra', 'fiscalised', 'fiscalization'],
    "is_active": True,
    "steps": [
        {
            "name": "ask_vat_registered",
            "is_entry_point": True,
            "type": "question",
            "config": {
                "message_config": {
                    "message_type": "interactive",
                    "interactive": {
                        "type": "button",
                        "body": {"text": "Welcome! I can help with your fiscalisation inquiry. First, are you VAT registered?"},
                        "action": {
                            "buttons": [
                                {"type": "reply", "reply": {"id": "vat_yes", "title": "Yes"}},
                                {"type": "reply", "reply": {"id": "vat_no", "title": "No"}}
                            ]
                        }
                    }
                },
                "reply_config": {"expected_type": "interactive_id", "save_to_variable": "is_vat_registered"}
            },
            "transitions": [
                {"to_step": "inform_cost_and_time", "priority": 0, "condition_config": {"type": "always_true"}}
            ]
        },
        {
            "name": "inform_cost_and_time",
            "type": "send_message",
            "config": {
                "message_type": "text",
                "text": {"body": "Okay, thank you. We can assist you with the fiscalisation process. It costs $150 and takes approximately 2 days to complete."}
            },
            "transitions": [
                {"to_step": "ask_reason", "priority": 0, "condition_config": {"type": "always_true"}}
            ]
        },
        {
            "name": "ask_reason",
            "type": "question",
            "config": {
                "message_config": {
                    "message_type": "interactive",
                    "interactive": {
                        "type": "list",
                        "header": {"type": "text", "text": "Reason for Fiscalising"},
                        "body": {"text": "What is the main reason you are looking to get fiscalised?"},
                        "action": {
                            "button": "Select Reason",
                            "sections": [{
                                "title": "Choose one",
                                "rows": [
                                    {"id": "reason_zimra", "title": "ZIMRA Recommended"},
                                    {"id": "reason_customers", "title": "My Customers Require It"},
                                    {"id": "reason_voluntary", "title": "I Want to Do It Voluntarily"}
                                ]
                            }]
                        }
                    }
                },
                "reply_config": {"expected_type": "interactive_id", "save_to_variable": "fiscalisation_reason"}
            },
            "transitions": [
                {"to_step": "acknowledge_reason", "priority": 0, "condition_config": {"type": "always_true"}}
            ]
        },
        {
            "name": "acknowledge_reason",
            "type": "send_message",
            "config": {"message_type": "text", "text": {"body": "Ok, understood."}},
            "transitions": [
                {"to_step": "ask_business_type", "priority": 0, "condition_config": {"type": "always_true"}}
            ]
        },
        {
            "name": "ask_business_type",
            "type": "question",
            "config": {
                "message_config": {"message_type": "text", "text": {"body": "What type of business are you into? (e.g., Retail Shop, Hardware, Consulting)"}},
                "reply_config": {"expected_type": "text", "save_to_variable": "business_type"}
            },
            "transitions": [
                {"to_step": "ask_urgency", "priority": 0, "condition_config": {"type": "variable_exists", "variable_name": "business_type"}}
            ]
        },
        {
            "name": "ask_urgency",
            "type": "question",
            "config": {
                "message_config": {
                    "message_type": "interactive",
                    "interactive": {
                        "type": "list",
                        "header": {"type": "text", "text": "Urgency"},
                        "body": {"text": "How urgently do you need the fiscalisation to be done?"},
                        "action": {
                            "button": "Select Urgency",
                            "sections": [{"title": "Timeline", "rows": [
                                {"id": "urgent_very", "title": "Very Urgent"},
                                {"id": "urgent_this_week", "title": "This Week"},
                                {"id": "urgent_next_week", "title": "Next Week"},
                                {"id": "urgent_will_update", "title": "I will update you later"}
                            ]}]
                        }
                    }
                },
                "reply_config": {"expected_type": "interactive_id", "save_to_variable": "urgency_level"}
            },
            "transitions": [
                {"to_step": "inform_urgent_requirements", "priority": 0, "condition_config": {"type": "interactive_reply_id_equals", "value": "urgent_very"}},
                {"to_step": "handle_not_urgent", "priority": 1, "condition_config": {"type": "always_true"}}
            ]
        },
        {
            "name": "inform_urgent_requirements",
            "type": "question",
            "config": {
                "message_config": {
                    "message_type": "interactive",
                    "interactive": {
                        "type": "button",
                        "body": {"text": "For urgent processing, the cost is $150. We will need your Company Name, TIN, VAT number, Phone, Address, and Email.\n\nWould you like to start the process now?"},
                        "action": {"buttons": [
                            {"type": "reply", "reply": {"id": "start_today", "title": "Yes, Start Now"}},
                            {"type": "reply", "reply": {"id": "start_later", "title": "I'll provide details later"}}
                        ]}
                    }
                },
                "reply_config": {"expected_type": "interactive_id", "save_to_variable": "start_process_decision"}
            },
            "transitions": [
                {"to_step": "ask_company_name", "priority": 0, "condition_config": {"type": "interactive_reply_id_equals", "value": "start_today"}},
                {"to_step": "handle_will_update", "priority": 1, "condition_config": {"type": "always_true"}}
            ]
        },
        {
            "name": "ask_company_name",
            "type": "question",
            "config": {
                "message_config": {"message_type": "text", "text": {"body": "Great. Let's get started. What is your company's full registered name?"}},
                "reply_config": {"expected_type": "text", "save_to_variable": "fiscalisation_company_name"}
            },
            "transitions": [{"to_step": "ask_tin", "priority": 0, "condition_config": {"type": "always_true"}}]
        },
        {
            "name": "ask_tin",
            "type": "question",
            "config": {
                "message_config": {"message_type": "text", "text": {"body": "Thank you. What is the company's TIN (Taxpayer Identification Number)?"}},
                "reply_config": {"expected_type": "text", "save_to_variable": "fiscalisation_tin"}
            },
            "transitions": [{"to_step": "ask_vat_number", "priority": 0, "condition_config": {"type": "always_true"}}]
        },
        {
            "name": "ask_vat_number",
            "type": "question",
            "config": {
                "message_config": {"message_type": "text", "text": {"body": "What is the VAT number? (If not applicable, please type 'N/A')"}},
                "reply_config": {"expected_type": "text", "save_to_variable": "fiscalisation_vat"}
            },
            "transitions": [{"to_step": "ask_phone", "priority": 0, "condition_config": {"type": "always_true"}}]
        },
        {
            "name": "ask_phone",
            "type": "question",
            "config": {
                "message_config": {"message_type": "text", "text": {"body": "What is the best contact phone number for the business?"}},
                "reply_config": {"expected_type": "text", "save_to_variable": "fiscalisation_phone"}
            },
            "transitions": [{"to_step": "ask_email", "priority": 0, "condition_config": {"type": "always_true"}}]
        },
        {
            "name": "ask_email",
            "type": "question",
            "config": {
                "message_config": {"message_type": "text", "text": {"body": "And the best business email address?"}},
                "reply_config": {"expected_type": "email", "save_to_variable": "fiscalisation_email"}
            },
            "transitions": [{"to_step": "ask_address", "priority": 0, "condition_config": {"type": "always_true"}}]
        },
        {
            "name": "ask_address",
            "type": "question",
            "config": {
                "message_config": {"message_type": "text", "text": {"body": "Finally, what is the physical address of the business?"}},
                "reply_config": {"expected_type": "text", "save_to_variable": "fiscalisation_address"}
            },
            "transitions": [{"to_step": "compile_and_end_urgent", "priority": 0, "condition_config": {"type": "always_true"}}]
        },
        {
            "name": "compile_and_end_urgent",
            "type": "action",
            "config": {
                "actions_to_run": [
                    {
                        "action_type": "set_context_variable",
                        "variable_name": "final_notes",
                        "value_template": (
                            "New Fiscalisation Lead (Urgent):\n\n"
                            "Company: {{ fiscalisation_company_name }}\n"
                            "TIN: {{ fiscalisation_tin }}\n"
                            "VAT: {{ fiscalisation_vat }}\n"
                            "Phone: {{ fiscalisation_phone }}\n"
                            "Email: {{ fiscalisation_email }}\n"
                            "Address: {{ fiscalisation_address }}\n"
                            "---\n"
                            "Business Type: {{ business_type }}\n"
                            "Reason: {{ fiscalisation_reason }}\n"
                            "VAT Registered: {{ is_vat_registered }}"
                        )
                    },
                    {
                        "action_type": "update_customer_profile",
                        "fields_to_update": {"notes": "{{ final_notes }}\n---\n{{ customer_profile.notes or '' }}"}
                    },
                    {
                        "action_type": "send_admin_notification",
                        "message_template": "URGENT Fiscalisation Lead for {{ contact.name or contact.whatsapp_id }}:\n\n{{ final_notes }}"
                    }
                ]
            },
            "transitions": [
                {"to_step": "end_flow_final_message", "priority": 0, "condition_config": {"type": "always_true"}}
            ]
        },
        {
            "name": "end_flow_final_message",
            "type": "end_flow",
            "config": {
                "message_config": {
                    "message_type": "text",
                    "text": {"body": "Thank you for providing all the details. We will start the process immediately. Payment of $150 can be made once the process has been finished. We will keep you updated."}
                }
            },
            "transitions": []
        },
        {
            "name": "handle_not_urgent",
            "type": "action",
            "config": {
                "actions_to_run": [{
                    "action_type": "set_context_variable",
                    "variable_name": "final_notes",
                    "value_template": (
                        "New Fiscalisation Lead (Not Urgent):\n\n"
                        "Business Type: {{ business_type }}\n"
                        "Reason: {{ fiscalisation_reason }}\n"
                        "Urgency: {{ urgency_level }}\n"
                        "VAT Registered: {{ is_vat_registered }}"
                    )
                }]
            },
            "transitions": [
                {"to_step": "compile_and_end_not_urgent", "priority": 0, "condition_config": {"type": "always_true"}}
            ]
        },
        {
            "name": "handle_will_update",
            "type": "action",
            "config": {
                "actions_to_run": [{
                    "action_type": "set_context_variable",
                    "variable_name": "final_notes",
                    "value_template": (
                        "New Fiscalisation Lead (Will Update):\n\n"
                        "Business Type: {{ business_type }}\n"
                        "Reason: {{ fiscalisation_reason }}\n"
                        "VAT Registered: {{ is_vat_registered }}\n"
                        "Note: Client chose to provide details later."
                    )
                }]
            },
            "transitions": [
                {"to_step": "compile_and_end_not_urgent", "priority": 0, "condition_config": {"type": "always_true"}}
            ]
        },
        {
            "name": "compile_and_end_not_urgent",
            "type": "action",
            "config": {
                "actions_to_run": [
                    {
                        "action_type": "update_customer_profile",
                        "fields_to_update": {"notes": "{{ final_notes }}\n---\n{{ customer_profile.notes or '' }}"}
                    },
                    {
                        "action_type": "send_admin_notification",
                        "message_template": "New Fiscalisation Lead for {{ contact.name or contact.whatsapp_id }}:\n\n{{ final_notes }}"
                    }
                ]
            },
            "transitions": [
                {"to_step": "end_flow_generic", "priority": 0, "condition_config": {"type": "always_true"}}
            ]
        },
        {
            "name": "end_flow_generic",
            "type": "end_flow",
            "config": {
                "message_config": {
                    "message_type": "text",
                    "text": {"body": "Thank you for your interest in our fiscalisation service. A specialist will be in touch shortly to discuss the next steps based on your selection. We look forward to assisting you!"}
                }
            },
            "transitions": []
        }
    ]
}