from .models import Revision
from .utils import obj_diff


def pre_save(instance, **kwargs):
    """Pre-save signal handler
    """
    model = kwargs["sender"]
    original = model._default_manager.get(pk=instance.pk)
    delta = obj_diff(instance, original)
    info = getattr(instance, 'revision_info', {})
    rev = Revision(delta=delta, **info)
    rev.content_object = instance
    rev.save()
