from django import forms
from django.utils.safestring import mark_safe

from .models import Revision


class RevisionReadonlyForm(forms.ModelForm):

    fields = ("delta",)

    def __init__(self, *a, **kw):
        """Instance constructor"""
        r = super(RevisionReadonlyForm, self).__init__(*a, **kw)
        if self.instance:
            self.instance.delta = mark_safe(
                self.instance.display_diff()
                #self.instance.delta.replace("\n", "<br />")
            )
        return r

    class Meta:
        model = Revision

    def save(self, *a, **kw):
        """Don't save"""
        pass
