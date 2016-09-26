*Live events:*
{% for event in events %}
{{ loop.index }}. {{ event.name }} (*{{ event.days_remaining }} days remaining*)
{% endfor %}
Manage events at https://www.eventbrite.co.uk/myevents/
