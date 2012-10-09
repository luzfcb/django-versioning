from __future__ import absolute_import, unicode_literals
_registry = {}


class AlreadyRegistered(Exception):
    pass


def register(model, fields=None):
    """
    """
    from django.db import models
    from django.db.models import signals as model_signals
    from versioning.signals import pre_save, post_save

    opts = model._meta

    if fields is None:
        raise TypeError("You must give at least one field.")
    else:
        for field in fields:
            f = opts.get_field(field)
            if not isinstance(f, models.TextField) and False:
                raise TypeError("""
                    versioning cannot handle anything other
                    than a TextField. {0} is of type {1}
                    """.format(field, type(f))
                )

    if model in _registry:
        raise AlreadyRegistered
    _registry[model] = fields

    model_signals.pre_save.connect(pre_save, sender=model)
    model_signals.post_save.connect(post_save, sender=model)
