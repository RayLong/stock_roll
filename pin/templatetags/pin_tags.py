import datetime
from urlparse import urlparse

from django import template
from django.contrib.auth.models import User
from django.template import Library,Node
from django.template.base import TemplateSyntaxError
from django.template.defaultfilters import stringfilter
from django.utils.text import normalize_newlines
from django.utils.safestring import mark_safe

from pin.models import Likes as pin_likes, Notify, StockTrend
from user_profile.models import Profile
import os
import dpin

register = Library()

def user_item_like(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, item = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires exactly two arguments" % token.contents.split()[0])
    
    return UserItemLike(item)

class UserItemLike(template.Node):
    def __init__(self, item):
        self.item = template.Variable(item)

    def render(self, context):
        try:
            item = int(self.item.resolve(context))
            user=context['user']
            liked = Likes.objects.filter(user=user, item=item).count()
            if liked :
                return 'btn-danger'
            else:
                return ''
        except template.VariableDoesNotExist:
            return ''

register.tag('user_item_like', user_item_like)

def user_post_like(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, item = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires exactly two arguments" % token.contents.split()[0])
    
    return UserPostLike(item)

class UserPostLike(template.Node):
    def __init__(self, item):
        self.item = template.Variable(item)

    def render(self, context):
        try:
            item = int(self.item.resolve(context))
            user=context['user']
            liked = pin_likes.objects.filter(user=user, post=item).count()
            if liked :
                return 'btn-danger'
            else:
                return ''
        except template.VariableDoesNotExist:
            return ''

register.tag('user_post_like', user_post_like)

@register.filter
def get_user_notify(userid):
    notify = Notify.objects.all().filter(user_id=userid, seen=False).count()
    return notify

@register.filter
def get_username(user):
    try:
        profile=Profile.objects.get(user_id=user.id)
        username=profile.name
    except Profile.DoesNotExist:
        username=user.username
    return username

@register.filter
def get_host(value):
    o = urlparse(value)
    if hasattr(o, 'netloc'):
        return o.netloc
    else:
        return ''

@register.filter
def get_svg(stock_code, modify_date):
    svg_file_string="stock_pics/"+str(stock_code)+"-"+modify_date.strftime("%Y-%m-%d")+".svg"
    if not os.path.isfile(dpin.settings.MEDIA_ROOT+"/"+svg_file_string):
        import daemon.stocks_db as DB
        import daemon.drawing_svg as drawing
        db=DB.ORM_Stock()
        data=db.get_stock_data(stock_code,['high_price','open_price','close_price','low_price'])
        if data.exists():
            data=map((lambda m : [m['high_price'],m['open_price'],m['close_price'],m['low_price']]), list(data)[-20:])
            t=StockTrend.objects.filter(stock_code=stock_code)[0]
            svg_content_string=drawing.to_image(dpin.settings.MEDIA_ROOT+"/"+svg_file_string, data, t.a, t.b, t.k)
        else:
            svg_content_string='<svg></svg>'
    else:
        f=open(dpin.settings.MEDIA_ROOT+"/"+svg_file_string,'r')
        svg_content_string=f.read()
        f.close()
    return mark_safe(svg_content_string)

@register.filter
def date_from_timestamp(value):
    return datetime.datetime.fromtimestamp(int(value)).strftime('%Y-%m-%d %H:%M:%S')

def remove_newlines(text):
    """
    Removes all newline characters from a block of text.
    """
    # First normalize the newlines using Django's nifty utility
    normalized_text = normalize_newlines(text)
    # Then simply remove the newlines like so.
    return mark_safe(normalized_text.replace('\n', ' '))

remove_newlines.is_safe = True
remove_newlines = stringfilter(remove_newlines)
register.filter(remove_newlines)
