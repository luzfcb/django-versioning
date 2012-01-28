
from django.contrib import admin
from django import forms
from django.contrib.contenttypes import generic
from django.utils.safestring import mark_safe

from . import _registry
from .models import Revision
from .forms import RevisionReadonlyForm


class DeltaWidget(forms.HiddenInput):
    """
    Render a delta in a form.
    TODO: this needs some more work.
    """
    def render(self, name, data, attrs):
        r = super(DeltaWidget, self).render(name, data, attrs)
        data = data or ''
        r += data.replace("\n", "<br />")
        return mark_safe(r)


class RevisionInline(generic.GenericTabularInline):
    form = RevisionReadonlyForm
    model = Revision
    ct_field = "content_type"
    ct_fk_field = "object_id"
    extra = 0
    can_delete = False
    fields = ("delta",)

    def get_readonly_fields(self, request, obj=None):
        return ("delta",)

    def formfield_for_dbfield2(self, db_field, **kwargs):
        print dir(self)
        if db_field.name == "delta":
            del kwargs['request']
            kwargs["widget"] = DeltaWidget
            return db_field.formfield(**kwargs)
        return super(RevisionInline, self).formfield_for_dbfield(db_field, **kwargs)


class RevisionAdmin(admin.ModelAdmin):
    list_display = ("sha1", "content_type", "object_id", "created_at")
    list_filter = ("created_at", "content_type",)

    def formfield_for_dbfield2(self, db_field, **kwargs):
        if db_field.name == "delta":
            del kwargs['request']
            kwargs["widget"] = DeltaWidget
            return db_field.formfield(**kwargs)
        return super(RevisionAdmin, self).formfield_for_dbfield(db_field, **kwargs)

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
