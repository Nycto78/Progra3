import pydantic
import sys

if not hasattr(pydantic, 'v1'):
    sys.modules['pydantic.v1'] = pydantic