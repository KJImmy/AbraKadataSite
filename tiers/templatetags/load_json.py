from django import template

register = template.Library()

@register.simple_tag
def load_json(path):
	return json.loads(path)