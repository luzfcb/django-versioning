
from django.contrib import admin
from django import forms
from django.contrib.contenttypes import generic
from django.utils.safestring import mark_safe

from . import _registry
from .forms import RevisionReadonlyForm
from .models import Revision
from .utils import diff_split_by_fields


class RevisionInline(generic.GenericTabularInline):
    form = RevisionReadonlyForm
    model = Revision
    ct_field = "content_type"
    ct_fk_field = "object_id"
    extra = 0
    can_delete = False
    fields = ("reapply", "delta_repr", )

    def get_formset(self, request, obj=None):
        """Binds to object the editor's info"""
        obj.revision_info = {
            'editor_ip': request.META.get("REMOTE_ADDR"),
            'editor': request.user
        }
        return super(RevisionInline, self).get_formset(request, obj)


class RevisionAdmin(admin.ModelAdmin):
    form = RevisionReadonlyForm
    list_display = ("pk", "revision", "sha1", "content_type",\
                    "object_id", "created_at", "editor", )
    list_filter = ("created_at", "content_type", )
    fields = ("reapply", "delta_repr", )

    def has_delete_permission(self, request, obj=None):
        """Allows to delete only first or diff-empty revisions"""
        parent = super(RevisionAdmin, self)\
            .has_delete_permission(request, obj)
        if not parent or not obj:
            return False

        previouses = Revision.objects.get_for_object(obj.content_object)\
            .filter(revision__lt=obj.revision)
        if not previouses.count():
            return True

        diffs = diff_split_by_fields(obj.delta)
        if not u"".join(diffs.values()).strip():
            return True

        return False

admin.site.register(Revision, RevisionAdmin)


def patch_admin_models():
    """Adds RevisionInline for revisionable models."""
    for model in _registry:
        if model in admin.site._registry:
            model_admin = admin.site._registry[model]
            cls = model_admin.__class__
            if RevisionInline not in cls.inlines:
                cls.inlines = list(cls.inlines)  # tuple to list
                cls.inlines.append(RevisionInline)
                admin.site.unregister(model)
                admin.site.register(model, cls)

patch_admin_models()
