import cgi
import logging
import random
import webapp2
from google.appengine.api import users
from google.appengine.ext import db
from webapp2_extras.appengine.users import login_required
from lib import templates
from lib.models import Category
from lib.models import Item

class CategoryHandler(webapp2.RequestHandler):
  @login_required
  def new(self):
    template = templates.get('category.html')
    user = users.get_current_user()
    template_values = {
        'user' : user.nickname(),
        'logout_url': users.create_logout_url("/")
    }
    self.response.write(template.render(template_values))

  # Cannot use login_required decorator for POST
  def save(self):
    user = users.get_current_user()
    if user:
      category = None
      cat_name = self.request.POST['catName']
      category = Category(name=cat_name, owner=user)
      category.put()

      for param in self.request.POST.items():
        if param[0] != 'catName':
          if category:
            item = Item(name=cgi.escape(param[1]), category=category,
                wins=0, losses=0)
            item.put()
      self._show_home_page({'success': 'Saved category "%s" successfully' % cat_name})
    else:
      self.redirect(users.create_login_url("/"))


  @login_required
  def mine(self):
    user = users.get_current_user()
    categories = db.GqlQuery('SELECT * from Category where owner=:1', user)
    template = templates.get('user_category.html')
    user = users.get_current_user()
    category_list = []
    for category in categories:
      cat = {'name': category.name, 'date': str(category.date),
          'items': category.items.count(), 'id': category.key().id()}
      category_list.append(cat)
    template_values = {
        'user' : user.nickname(),
        'logout_url': users.create_logout_url("/"),
        'categories': category_list
    }
    self.response.write(template.render(template_values))

  @login_required
  def all(self):
    categories = db.GqlQuery('SELECT * from Category')
    template = templates.get('all_category.html')
    user = users.get_current_user()
    category_list = []
    for category in categories:
      cat = {'name': category.name, 'date': str(category.date),
          'items': category.items.count(), 'id': category.key().id(),
          'owner': category.owner.nickname()}
      category_list.append(cat)
    template_values = {
        'user' : user.nickname(),
        'logout_url': users.create_logout_url("/"),
        'categories': category_list
    }
    self.response.out.write(template.render(template_values))


  @login_required
  def vote(self, cat_id):
    user = users.get_current_user()
    template = templates.get('vote.html')
    category = Category.get_by_id(int(cat_id))
    items = category.items
    selected_items = list(random.sample(set(items), 2))
    template_values = {
        'user' : user.nickname(),
        'logout_url': users.create_logout_url("/"),
        'category': category.name,
        'item1': {'name': selected_items[0].name, 'id': selected_items[0].key().id()},
        'item2': {'name': selected_items[1].name, 'id': selected_items[1].key().id()}
    }
    self.response.out.write(template.render(template_values))

  def submit_vote(self):
    user = users.get_current_user()
    if user:
      item1_id = int(self.request.POST['item1'])
      item2_id = int(self.request.POST['item2'])
      selected_id = int(self.request.POST['optionsRadios'])
      item1 = Item.get_by_id(item1_id)
      item2 = Item.get_by_id(item2_id)
      if selected_id == item1_id:
        item1.wins += 1
        item1.put()
        item2.losses += 1
        item2.put()
      else:
        item2.wins += 1
        item2.put()
        item1.losses += 1
        item1.put()

      self._show_home_page({'success': 'Saved vote for successfully'})
    else:
      self.redirect(users.create_login_url("/"))

  def _show_home_page(self, msg_dict):
    template = templates.get('index.html')
    user = users.get_current_user()
    template_values = {
        'user' : user.nickname(),
        'logout_url': users.create_logout_url("/"),
        'message': msg_dict
    }
    self.response.write(template.render(template_values))
