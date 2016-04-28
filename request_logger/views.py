from pprint import pformat

from flask import request
from flask import render_template

from werkzeug.routing import BaseConverter

from request_logger import app


class RegexConverter(BaseConverter):
  def __init__(self, url_map, *items):
    super(RegexConverter, self).__init__(url_map)
    self.regex = items[0]


app.url_map.converters['regex'] = RegexConverter

stored_requests = []


@app.route('/<regex(".+"):url>', methods=['GET', 'POST'])
def index(url):
  stored_requests.append({
    'url': '{} {}'.format(request.method, request.url),
    'data': pformat(vars(request), indent=2),
  })
  return render_template(
    'index.html',
    stored_requests=stored_requests,
  )


@app.route('/', methods=['GET'])
def display_calls():
  return render_template(
    'index.html',
    stored_requests=stored_requests,
  )
