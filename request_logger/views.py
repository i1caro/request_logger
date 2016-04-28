from datetime import datetime
from pprint import pformat

from flask import request
from flask import render_template

from werkzeug.routing import BaseConverter

from request_logger import app


class RegexConverter(BaseConverter):
  def __init__(self, url_map, *items):
    super(RegexConverter, self).__init__(url_map)
    self.regex = items[0]


class WSGICopyBody(object):
  def __init__(self, application):
    self.application = application

  def __call__(self, environ, start_response):

    from cStringIO import StringIO
    length = environ.get('CONTENT_LENGTH', '0')
    length = 0 if length == '' else int(length)

    body = environ['wsgi.input'].read(length)
    environ['body_copy'] = body
    environ['wsgi.input'] = StringIO(body)

    # Call the wrapped application
    app_iter = self.application(environ,
                                self._sr_callback(start_response))

    # Return modified response
    return app_iter

  def _sr_callback(self, start_response):
    def callback(status, headers, exc_info=None):

      # Call upstream start_response
      start_response(status, headers, exc_info)
    return callback

app.wsgi_app = WSGICopyBody(app.wsgi_app)


app.url_map.converters['regex'] = RegexConverter

stored_requests = []


@app.route('/<regex(".+"):url>', methods=['GET', 'POST'])
def index(url):
  if url != 'favicon.ico':
    stored_requests.append({
      'timestamp': datetime.now(),
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
    stored_requests=sorted(stored_requests, key=lambda x: x['timestamp']),
  )
