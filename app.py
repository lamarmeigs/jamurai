from wsgiref import simple_server

import falcon
from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import TemplateNotFound

from utils import UndefinedVariable


TEMPLATES_DIRECTORY = 'templates'


class RenderTemplateResponder:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.jinja_env = Environment(
            loader=FileSystemLoader(TEMPLATES_DIRECTORY),
            undefined=UndefinedVariable,
        )

    def on_get(self, req, resp, template_name):
        try:
            template = self.jinja_env.get_template(template_name)
        except TemplateNotFound:
            raise falcon.HTTPNotFound(
                title='Template not found',
                description='No such template: "{}"'.format(template_name)
            )
        # TODO: gather variables from req.params
        variables = {}
        resp.body = template.render(**variables)
        resp.status = falcon.HTTP_OK


app = falcon.API()
app.add_route('/{template_name}', RenderTemplateResponder())


if __name__ == '__main__':
    httpd = simple_server.make_server(host='localhost', port=8000, app=app)
    print('Running on http://localhost:8000')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Shutting down...')
        httpd.shutdown()
