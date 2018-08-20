import jinja2


class UndefinedVariable(jinja2.Undefined):
    """Implements jinja2's Undefined interface to render placeholder content"""

    def __init__(self, *args, **kwargs):
        self._name = kwargs.get('name', 'placeholder')
        self._parent = kwargs.pop('parent', None)
        super().__init__(*args, **kwargs)

    def items(self):
        return [
            ('field0', self['field0']),
            ('field1', self['field1'])
        ]

    def keys(self):
        return [key for key, _ in self.items()]

    def values(self):
        return [value for _, value in self.items()]

    def __iter__(self):
        for item in (self[0], self[1]):
            yield item

    def __getattr__(self, name):
        return UndefinedVariable(name=name, parent=self)

    def __getitem__(self, key):
        return UndefinedVariable(name='[{}]'.format(repr(key)), parent=self)

    def __call__(self, *args, **kwargs):
        signature = ', '.join(str(a) for a in args)

        if kwargs:
            if signature:
                signature += ', '
            signature += ', '.join('{}={}'.format(k, v) for k, v in kwargs.items())

        signature = '(' + signature + ')'

        return UndefinedVariable(name=signature, parent=self)

    def __str__(self):
        return '{{ ' + self._get_name() + ' }}'

    def _get_name(self):
        if self._name.startswith('[') or self._name.startswith('('):
            separator = ''
        else:
            separator = '.'

        if self._parent is not None:
            parent_name = self._parent._get_name()
        else:
            parent_name = ''
            separator = ''

        return '{}{}{}'.format(parent_name, separator, self._name)


class JSONParamConsolidationMiddleware(object):
    """Middleware class to rejoin incorrectly-split request JSON parameters"""
    def process_resource(self, req, resp, resource, params):
        for key, value in req.params.items():
            if isinstance(value, list) and value[0].startswith(('{', '[')):
                req.params[key] = ','.join(value)
