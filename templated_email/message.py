from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import Context
from django.template.loader import get_template

from templated_email.utils import _get_node, BlockNotFound


class EmailRenderException(Exception):
    pass


class TemplatedEmailMessage(EmailMultiAlternatives):
    def __init__(self, template_name, context, template_prefix=None,
                 template_suffix=None, **kwargs):
        template_prefix = template_prefix or getattr(settings,'TEMPLATED_EMAIL_TEMPLATE_DIR', 'templated_email/')
        template_suffix = template_suffix or getattr(settings,'TEMPLATED_EMAIL_FILE_EXTENSION', 'email')
        full_template_name = '%s%s.%s' % (template_prefix, template_name,
                template_suffix)

        self._render_email(context, full_template_name)

    def _render_email(self, template_name, context):
        parts = {}
        errors = {}
        render_context = Context(context, autoescape=False)

        multi_part = get_template(template_name)

        if not self.subject:
            try:
                self.subject = _get_node(multi_part, render_context, name='subject')
            except BlockNotFound, error:
                raise EmailRenderException("No subject found in template: %s" %
                        error)

        for part in ('html','plain'):
            try:
                parts[part] = _get_node(multi_part, render_context, name=part)
            except BlockNotFound, error:
                errors[part] = error

        if 'plain' in parts:
            self.body = parts['plain']
            if 'html'  in parts:
                self.attach_alternative(parts['html'], 'text/html')
        elif 'html' in parts:
            self.body = parts['html']
            self.content_subtype = 'html'
        else:
            raise EmailRenderException("Couldn't render email parts. Errors: %s"
                                       % errors)
