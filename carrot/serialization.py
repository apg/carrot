"""

Support for encoding/decoding.  Requires a json library. 
Optionally installs support for HessianPy and YAML.

.. function:: serialize(obj)

    Serialize the object to JSON.

.. function:: deserialize(obj)

    Deserialize JSON-encoded object to a Python object.

"""

import codecs
from cStringIO import StringIO

class DecoderNotInstalled(StandardError):
    """Support for the requested serialization type is not installed"""
    

class SerializerRegistry(object):
    
    def __new__(type):
        """
        Make the registry a singleton.
        """
        if not '_sr_instance' in type.__dict__:
            type._sr_instance = object.__new__(type)
        return type._sr_instance

    def __init__(self):
        self._encoders = {}
        self._decoders = {}
        self._default_encode = None
        self._default_content_type = None
        self._default_content_encoding = None
        
    def register(self, name, encoder, decoder, content_type, 
                 content_encoding='utf-8'):

        if encoder: 
            self._encoders[name] = (content_type, content_encoding, encoder)
        if decoder:
            self._decoders[content_type] = decoder

    def set_default_serializer(self, name):
        try:
            (self._default_content_type, self._default_content_encoding, 
             self._default_encode) = self._encoders[name]
        except KeyError: 
            raise DecoderNotInstalled(
                "No decoder installed for %s" % name)

    def encode(self, message, serializer=None):

        # If a raw string was sent, assume binary encoding 
        # (it's likely either ASCII or a raw binary file, but 'binary' 
        # charset will encompass both, even if not ideal.
        if isinstance(message, str) and not serializer:
            # In Python 3+, this would be "bytes"; allow binary data to be 
            # sent as a message without getting encoder errors
            content_type = 'application/data'
            content_encoding = 'binary'
            payload = message

        # For unicode objects, force it into a string
        elif isinstance(message, unicode) and not serializer: 
            content_type = 'text/plain'
            content_encoding = 'utf-8'
            payload = message.encode(content_encoding)

        # Special case serializer
        elif serializer == 'raw': 
            content_type = 'application/data'
            payload = message
            if isinstance(payload, unicode): 
                content_encoding = 'utf-8'
                payload = payload.encode(content_encoding)
            else:
                content_encoding = 'binary'
                
        else:
            if serializer: 
                (content_type, content_encoding, 
                 encoder) = self._encoders[serializer]
            else:
                encoder = self._default_encode
                content_type = self._default_content_type
                content_encoding = self._default_content_encoding
            payload = encoder(message)

        return (content_type, content_encoding, payload)

    def decode(self, message, content_type, content_encoding):
        content_type = content_type or 'application/data'
        content_encoding = (content_encoding or 'utf-8').lower()

        # Don't decode 8-bit strings
        if content_encoding not in ('binary','ascii-8bit'):
            message = codecs.decode(message, content_encoding)

        try:
            decoder = self._decoders[content_type]
        except KeyError: 
            return message
            
        return decoder(message)


registry = SerializerRegistry()


def register_json():
    # Try to import a module that provides json parsing and emitting, starting
    # with the fastest alternative and falling back to the slower ones.
    try:
        # cjson is the fastest
        import cjson
        json_serialize = cjson.encode
        json_deserialize = cjson.decode
    except ImportError:
        try:
            # Then try to find simplejson. Later versions has C speedups which
            # makes it pretty fast.
            import simplejson
            json_serialize = simplejson.dumps
            json_deserialize = simplejson.loads
        except ImportError:
            try:
                # Then try to find the python 2.6 stdlib json module.
                import json
                json_serialize = json.dumps
                json_deserialize = json.loads
            except ImportError:
                # If all of the above fails, fallback to the simplejson
                # embedded in Django.
                from django.utils import simplejson
                json_serialize = simplejson.dumps
                json_deserialize = simplejson.loads

    registry.register('json', json_serialize, json_deserialize, 
                      content_type='application/json', 
                      content_encoding='utf-8')


# def register_hessian():
#     from hessian import hessian
#     
#     def h_encode(body):
#         sio = StringIO()
#         hessian.Reply().write(
#                       hessian.WriteContext(sio),
#                       ({}, '', body))
#         return sio.getvalue()
#         
#     def h_decode(body):
#         payload = StringIO(body)
#         ctx = hessian.ParseContext(payload)
#         (method, headers, params) = hessian.Call().read(ctx, ctx.read(1))
#         print (method, headers, params)
#         return params
# 
#     registry.register('hessian', h_encode, h_decode, 
#                       content_type='application/x-hessian', 
#                       content_encoding='binary')
# 

def register_yaml():
    import yaml
    registry.register('yaml', yaml.safe_dump, yaml.safe_load, 
                      content_type='application/x-yaml', 
                      content_encoding='utf-8')

def register_pickle():
    import cPickle
    registry.register('pickle', cPickle.dumps, cPickle.loads, 
                      content_type='application/x-python-serialize', 
                      content_encoding='binary')


# For backwards compatability
register_json()
registry.set_default_serializer('json')

# Register optional encoders, if possible
for optional in (register_yaml, register_pickle): #register_hessian): 
    try:
        optional()
    except ImportError: 
        pass


