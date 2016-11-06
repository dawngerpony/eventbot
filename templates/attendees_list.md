Attendees for '{{ event.name }}':
{% for attendee in attendees %}
{{ loop.index }}. {{ attendee.name }} - {{ attendee.ticket_class_name }} ({{ attendee.email }})
{% endfor %}
