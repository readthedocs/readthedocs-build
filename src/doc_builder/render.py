from jinja2 import Environment, FileSystemLoader
from doc_builder.constants import TEMPLATE_DIR

env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))


def render_context(template, context):
    template = env.get_template(template)
    return template.render(**context)


def render_to_string(template, **context):
    template = env.get_template(template)
    return template.render(**context)
