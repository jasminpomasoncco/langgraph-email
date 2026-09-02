from .email_categorizer import *

AGENT_REGISTRY = {
    "email_categorizer": categorize_email(),
}