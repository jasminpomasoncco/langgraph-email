from .email_categorizer import *
from .email_listener import *
from .email_writer import *
from .email_sender import *

NODES = {
    "email_listener": listen_for_emails_node,
    "email_categorizer": email_categorizer_node,
    "query_or_email": query_or_email_node,
    "email_writer_with_context": email_writer_with_context_node,
    "email_sender": email_sender_node,
}