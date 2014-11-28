#!/usr/bin/python3

import bottle
import pygments
import pygments.formatters
import pygments.lexers
import identigen
import config
from pathlib import Path

pathbase = Path(config.pastedir)
pygment_formater = pygments.formatters.HtmlFormatter()

if not pathbase.exists():
    pathbase.mkdir(mode=0o700, parents=True)

@bottle.route('/')
def route_root():
    return bottle.template('root')

@bottle.route('/', method='POST')
def route_paste_post():
    content = bottle.request.forms.get('content')
    try:
        pid = identigen.generate(content)
    except AttributeError as e:
        print(e)
        bottle.abort(400)
    path = pathbase / pid
    with path.open(mode='wb') as fd:
        fd.write(content.encode('utf8'))
    bottle.redirect('/' + pid)

@bottle.route('/static/<path:path>')
def route_static(path):
    return bottle.static_file(path, root='static')

@bottle.route('/<pid>')
@bottle.route('/<pid>/<pformat>')
def route_paste_get(pid, pformat='colored'):
    if pformat != 'colored' and pformat != 'raw':
        return bottle.template('bad_format')
    path = pathbase / pid
    try:
        with path.open() as fd:
            content = fd.read()
    except IOError:
        # use this template for all file based exception
        bottle.abort(404)
    if pformat == 'colored':
        try:
            lexer = pygments.lexers.guess_lexer(content)
            content = pygments.highlight(content, lexer, pygment_formater)
        except pygments.util.ClassNotFound:
            pass
        return bottle.template('paste', content=content)
    return content

@bottle.error(404)
def error404(error):
    return bottle.template("not_found")

@bottle.error(400)
def error400(error):
    return bottle.template("bad_request")

if __name__ == '__main__':
    print('I: Starting application with development server')
    bottle.run(host='0.0.0.0', port=8080, debug=True, reloader=True)
else:
    print('I: Starting application as a wsgi application')
    application = bottle.default_app() # application used for wsgi mode
