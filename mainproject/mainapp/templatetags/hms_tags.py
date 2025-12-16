from django import template
from django.utils.safestring import mark_safe
from ..models import Notification

register = template.Library()

@register.filter
def notification_badge(count):
    """Display notification badge if count > 0"""
    if count > 0:
        return mark_safe(f'<span class="badge bg-danger">{count}</span>')
    return ''

@register.filter
def status_badge(status):
    """Display colored badge for appointment status"""
    badges = {
        'PENDING': 'warning',
        'CONFIRMED': 'info', 
        'COMPLETED': 'success',
        'CANCELLED': 'danger'
    }
    color = badges.get(status, 'secondary')
    return mark_safe(f'<span class="badge bg-{color}">{status}</span>')

@register.filter
def priority_badge(priority):
    """Display colored badge for triage priority"""
    badges = {
        'LOW': 'success',
        'MEDIUM': 'warning',
        'HIGH': 'danger',
        'URGENT': 'dark'
    }
    color = badges.get(priority, 'secondary')
    return mark_safe(f'<span class="badge bg-{color}">{priority}</span>')

@register.inclusion_tag('partials/notification_dropdown.html')
def notification_dropdown(user):
    """Render notification dropdown"""
    notifications = Notification.objects.filter(user=user, is_read=False)[:5]
    return {'notifications': notifications}