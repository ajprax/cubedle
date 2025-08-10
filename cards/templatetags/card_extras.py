from django import template

register = template.Library()

@register.filter
def get_image_uri(card, face=0):
    """Get image URI for a specific card face"""
    return card.get_image_uri(face)

@register.simple_tag
def card_back_image(card):
    """Get back image URI if card has multiple faces"""
    if card.has_multiple_faces():
        return card.get_image_uri(1)
    return ""