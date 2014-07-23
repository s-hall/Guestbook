import cgi
import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

MAIN_PAGE_FOOTER_TEMPLATE = """\
    <form action="/sign?%s" method="post">
      <div><textarea name="content" rows="3" cols="60"></textarea></div>
      <div><input type="submit" value="Sign Guestbook"></div>
    </form>
    <hr>

    <form method = "post" action = "/test" > Checkboxes:
      {% set boxes = ['fun', 'happy', 'sad'] %}
      {% for box in boxes %}
       <input type = "checkbox" name = "{{box}}" > {{box}}

      {% endfor %}
      <input type = "submit" value = "Submit" > 
    
    </form>
    <a href="%s">%s</a>
  </body>
</html>
"""

boxes = ['fun', 'happy', 'sad'] 

DEFAULT_GUESTBOOK_NAME = 'default_guestbook'

# We set a parent key on the 'Greetings' to ensure that they are all in the same
# entity group. Queries across the single entity group will be consistent.
# However, the write rate should be limited to ~1/second.

def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
    """Constructs a Datastore key for a Guestbook entity with guestbook_name."""
    return ndb.Key('Guestbook', guestbook_name)

def checkbox_key(boxes):
    return ndb.Key('Checkbox', boxes)

class Checkbox(webapp2.RequestHandler):
    def post(self):
        self.response.headers ['Content-Type'] = 'text/html'

        for box in boxes:
          checked_box = self.request.get(box)
          #if checked_box:
	   #   checked_box.put()
          self.response.out.write('my checkbox is, %s' %(box))


class Greeting(ndb.Model):
    """Models an individual Guestbook entry."""
    author = ndb.UserProperty()
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)

class MainPage(webapp2.RequestHandler):
    def get(self):
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        greetings_query = Greeting.query(
            ancestor=guestbook_key(guestbook_name)).order(-Greeting.date)
        greetings = greetings_query.fetch(10)

        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'boxes' : boxes,
            'greetings': greetings,
            'guestbook_name': urllib.quote_plus(guestbook_name),
            'url': url,
            'url_linktext': url_linktext,
        }


        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

class Guestbook(webapp2.RequestHandler):
    def post(self):
        # We set the same parent key on the 'Greeting' to ensure each Greeting
        # is in the same entity group. Queries across the single entity group
        # will be consistent. However, the write rate to a single entity group
        # should be limited to ~1/second.
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        greeting = Greeting(parent=guestbook_key(guestbook_name))

        self.response.headers ['Content-Type'] = 'text/html'

        if users.get_current_user():
            greeting.author = users.get_current_user()


        for box in boxes:
          checked_box = self.request.get(box)
          #if checked_box:
           #   checked_box.put()
           #self.response.out.write('my checkbox is, %s' (box))


        greeting.content = self.request.get('content')
        greeting.content += "my checkbox is " + checked_box
        #greeting.content += self.response.out.write ('checkbox')


        greeting.put()

        query_params = {'guestbook_name': guestbook_name} 


        self.redirect('/?' + urllib.urlencode(query_params))

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/sign', Guestbook),
    ('/test', Checkbox),
], debug=True)
