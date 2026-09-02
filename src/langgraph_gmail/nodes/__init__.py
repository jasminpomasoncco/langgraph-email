from .email_categorizer import *
from .email_listener import *

NODES = {
    "email_listener": listen_for_emails_node,
    "email_categorizer": email_categorizer_node
}