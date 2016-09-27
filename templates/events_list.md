*Live events:*
{% for event in events %}
{{ loop.index }}. {{ event.name }}
    *{{ event.days_remaining }} days remaining*
    *{{ event.quantity_sold }}/{{ event.capacity }}* tickets sold
{% endfor %}
Manage events at https://www.eventbrite.co.uk/myevents/
