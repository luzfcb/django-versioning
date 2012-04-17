from .middleware import get_request
from .models import Revision
from .utils import obj_diff


def pre_save(instance, **kwargs):
    """Pre-save signal handler
    """
    model = kwargs["sender"]
    try:
        original = model._default_manager.get(pk=instance.pk)
    except model.DoesNotExist:
        original = model()
    delta = obj_diff(instance, original)
    info = getattr(instance, 'revision_info', {})
    request = get_request()
    if request:
        if not info.get('editor'):
            info['editor'] = request.user
        if not info.get('editor_ip'):
            info['editor_ip'] = request.META.get("REMOTE_ADDR")
    if not hasattr(info, 'editor') or not getattr(info['editor'], 'pk', None):
        info['editor'] = None
    rev = Revision(delta=delta, **info)
    rev.content_object = instance
    rev.save()
