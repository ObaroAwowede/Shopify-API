# myproject/utils/short_swagger.py
from typing import Iterable, Optional
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema

def auto_operation_summaries(methods: Optional[Iterable[str]] = None,
                             use_full_doc_as_description: bool = False):
    """
    Very small class decorator:
      - first line of a method docstring -> operation_summary
      - if use_full_doc_as_description, whole docstring -> operation_description
    Pass `methods` to restrict which method names are processed.
    """
    methods = set(methods) if methods is not None else None

    def cls_decorator(cls):
        for name, fn in cls.__dict__.items():
            if name.startswith('_') or not callable(fn):
                continue
            if methods is not None and name not in methods:
                continue

            doc = (fn.__doc__ or '').strip()
            if not doc:
                continue
            first = next((line.strip() for line in doc.splitlines() if line.strip()), None)
            if not first:
                continue

            kwargs = {'operation_summary': first}
            if use_full_doc_as_description:
                kwargs['operation_description'] = doc

            cls = method_decorator(swagger_auto_schema(**kwargs), name=name)(cls)
        return cls
    return cls_decorator
