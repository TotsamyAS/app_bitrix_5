from django.urls import reverse

def url_with_message_parameters(redirect_url_string="index_after", status="success", content=""):
    return f'{reverse(f"{redirect_url_string}")}?message_type={status}&message_content={content}'
