from django import template
from django.db.models import Avg, IntegerField

register = template.Library()


@register.filter
def percentage(value):
    if value:
        return '{0:.2%}'.format(value / 100)
    else:
        return 'Not Avialable'


@register.filter
def overall_rating(value):
    x = value.listing_ratings.all(
    ).aggregate(Avg(('rating'), output_field=IntegerField()))
    if x['rating__avg']:
        return x['rating__avg']
    else:
        return 0

# @register.filter()
# @register.inclusion_tag('store/sell_details.html', takes_context=True)
# def own_store_filter(all_products):
#     if all_products:
#         request = context['request']
#         data = all_products.filter(store=request.user.user_store)
#         return data
#     return all_course
