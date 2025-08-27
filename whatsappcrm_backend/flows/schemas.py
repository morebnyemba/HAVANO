# whatsappcrm_backend/flows/schemas.py
from __future__ import annotations
from pydantic import BaseModel, Field, model_validator
from typing import List, Dict, Any, Optional, Union, Literal

# --- Common Reusable Schemas ---

class MediaMessageContent(BaseModel):
    """
    Configuration for media messages (image, document, audio, video, sticker).
    Can use either a local MediaAsset primary key or a direct WhatsApp media ID/link.
    """
    asset_pk: Optional[int] = Field(None, description="Primary key of a MediaAsset from the media library.")
    id: Optional[str] = Field(None, description="Direct WhatsApp Media ID.")
    link: Optional[str] = Field(None, description="Direct public URL to the media.")
    caption: Optional[str] = Field(None, description="Caption for the media.")
    filename: Optional[str] = Field(None, description="Filename for documents.")

    @model_validator(mode='after')
    def check_one_source(self) -> 'MediaMessageContent':
        # This validator is for basic structural checks. The service layer performs
        # the definitive check after template resolution, as any of these fields
        # could be a template string.
        return self

class TextMessageContent(BaseModel):
    body: str
    preview_url: bool = False

class LocationPayload(BaseModel):
    latitude: float
    longitude: float
    name: Optional[str] = None
    address: Optional[str] = None

# Schemas for Interactive Messages
class InteractiveReplyButton(BaseModel):
    id: str = Field(..., max_length=256)
    title: str = Field(..., max_length=20)

class InteractiveButton(BaseModel):
    type: Literal["reply"] = "reply"
    reply: InteractiveReplyButton

class InteractiveAction(BaseModel):
    buttons: List[InteractiveButton] = Field(..., max_length=3)

class InteractiveBody(BaseModel):
    text: str

class InteractiveHeader(BaseModel):
    type: Literal["text", "video", "image", "document"]
    text: Optional[str] = Field(None, max_length=60)
    video: Optional[MediaMessageContent] = None
    image: Optional[MediaMessageContent] = None
    document: Optional[MediaMessageContent] = None

class InteractiveFooter(BaseModel):
    text: str = Field(..., max_length=60)

class InteractiveMessagePayload(BaseModel):
    type: Literal["button", "list"] # "product", "product_list" are other options
    body: InteractiveBody
    action: InteractiveAction
    header: Optional[InteractiveHeader] = None
    footer: Optional[InteractiveFooter] = None

# Schemas for Template Messages
class TemplateParameterMediaObject(BaseModel):
    link: str

class TemplateParameterCurrency(BaseModel):
    fallback_value: str
    code: str
    amount_1000: int

class TemplateParameterDateTime(BaseModel):
    fallback_value: str

class TemplateParameter(BaseModel):
    type: Literal['text', 'currency', 'date_time', 'image', 'video', 'document', 'payload']
    text: Optional[str] = None
    currency: Optional[TemplateParameterCurrency] = None
    date_time: Optional[TemplateParameterDateTime] = None
    image: Optional[TemplateParameterMediaObject] = None
    video: Optional[TemplateParameterMediaObject] = None
    document: Optional[TemplateParameterMediaObject] = None
    payload: Optional[str] = None

class TemplateComponent(BaseModel):
    type: Literal['header', 'body', 'button']
    parameters: Optional[List[TemplateParameter]] = None
    sub_type: Optional[Literal['quick_reply', 'url']] = None
    index: Optional[int] = None

class TemplateLanguage(BaseModel):
    code: str

class TemplateMessagePayload(BaseModel):
    name: str
    language: TemplateLanguage
    components: Optional[List[TemplateComponent]] = None

# Schemas for Contact Messages
class ContactName(BaseModel):
    formatted_name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    prefix: Optional[str] = None
    suffix: Optional[str] = None

class ContactPhone(BaseModel):
    phone: Optional[str] = None
    type: Optional[str] = None
    wa_id: Optional[str] = None

class ContactEmail(BaseModel):
    email: Optional[str] = None
    type: Optional[str] = None

class ContactURL(BaseModel):
    url: Optional[str] = None
    type: Optional[str] = None

class ContactAddress(BaseModel):
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    country: Optional[str] = None
    country_code: Optional[str] = None
    type: Optional[str] = None

class ContactOrg(BaseModel):
    company: Optional[str] = None
    department: Optional[str] = None
    title: Optional[str] = None

class ContactObject(BaseModel):
    name: ContactName
    birthday: Optional[str] = None
    phones: Optional[List[ContactPhone]] = None
    emails: Optional[List[ContactEmail]] = None
    urls: Optional[List[ContactURL]] = None
    addresses: Optional[List[ContactAddress]] = None
    org: Optional[ContactOrg] = None


# --- Step-specific Config Schemas ---

class StepConfigSendMessage(BaseModel):
    """
    Configuration for the content of a 'send_message' step.
    This model represents the value of the `message_config` key in the step's config.
    """
    message_type: Literal['text', 'image', 'document', 'audio', 'video', 'sticker', 'interactive', 'template', 'contacts', 'location']
    text: Optional[TextMessageContent] = None
    image: Optional[MediaMessageContent] = None
    document: Optional[MediaMessageContent] = None
    audio: Optional[MediaMessageContent] = None
    video: Optional[MediaMessageContent] = None
    sticker: Optional[MediaMessageContent] = None
    interactive: Optional[InteractiveMessagePayload] = None
    template: Optional[TemplateMessagePayload] = None
    contacts: Optional[List[ContactObject]] = None
    location: Optional[LocationPayload] = None

class FallbackConfig(BaseModel):
    action: Literal['re_prompt', 'switch_flow', 'end_flow'] = 're_prompt'
    max_retries: int = 2
    re_prompt_message_text: Optional[str] = None
    target_flow_name: Optional[str] = Field(None, description="The name of the flow to switch to on fallback.")

class ReplyConfig(BaseModel):
    save_to_variable: str
    expected_type: Literal['text', 'email', 'number', 'interactive_id', 'image'] = 'text'
    validation_regex: Optional[str] = None

class StepConfigQuestion(BaseModel):
    message_config: Dict[str, Any] # This will be validated as StepConfigSendMessage in services
    reply_config: ReplyConfig
    fallback_config: Optional[FallbackConfig] = None

class ActionItem(BaseModel):
    action_type: str
    variable_name: Optional[str] = None
    value_template: Optional[Any] = None
    field_path: Optional[str] = None
    fields_to_update: Optional[Dict[str, Any]] = None
    message_template: Optional[str] = None
    app_label: Optional[str] = None
    model_name: Optional[str] = None
    filters_template: Optional[Dict[str, Any]] = None
    order_by: Optional[List[str]] = None
    limit: Optional[int] = None
    params_template: Optional[Dict[str, Any]] = None

class StepConfigAction(BaseModel):
    actions_to_run: List[ActionItem]

class StepConfigHumanHandover(BaseModel):
    pre_handover_message_text: Optional[str] = None
    notification_details: Optional[str] = None

class StepConfigEndFlow(BaseModel):
    message_config: Optional[Dict[str, Any]] = None

class StepConfigSwitchFlow(BaseModel):
    target_flow_name: str
    initial_context_template: Optional[Dict[str, Any]] = None
    trigger_keyword_to_pass: Optional[str] = None