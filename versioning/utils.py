from __future__ import absolute_import, unicode_literals
import sys
import base64

try:
    import cPickle as pickle
except ImportError:
    import pickle

from difflib import SequenceMatcher
from django.db import models
from django.utils.encoding import force_unicode
from django.core.exceptions import ObjectDoesNotExist

#from django.utils.encoding import smart_unicode
# Google Diff Match Patch library
# http://code.google.com/p/google-diff-match-patch
if sys.version_info > (3, ):
    from .vendor.diff_match_patch.python3.diff_match_patch import diff_match_patch
else:
    from .vendor.diff_match_patch.python2.diff_match_patch import diff_match_patch

from versioning import _registry

try:
    str = unicode  # Python 2.* compatible
    string_types = (basestring,)
    integer_types = (int, long)
except NameError:
    string_types = (str,)
    integer_types = (int,)

PICKLED_MARKER = 'pickled:'
STR_MARKER = 'str:'

dmp = diff_match_patch()


def encode(val):
    if not isinstance(val, string_types):
        return PICKLED_MARKER + base64.standard_b64encode(
            pickle.dumps(val, protocol=pickle.HIGHEST_PROTOCOL)
        ).decode('ascii')
    return STR_MARKER + force_unicode(val)  # prevent to user to falsify PICKLED_MARKER


def decode(val):
    if val.startswith(PICKLED_MARKER):
        try:
            return pickle.loads(base64.standard_b64decode(val[len(PICKLED_MARKER):].encode('ascii')))
        except Exception:
            pass
    elif val.startswith(STR_MARKER):
        return val[len(STR_MARKER):]
    return val


def revisions_for_object(instance):
    from .models import Revision
    return Revision.objects.get_for_object(instance)


def diff(txt1, txt2):
    """Create a 'diff' from txt1 to txt2."""
    patch = dmp.patch_make(txt1, txt2)
    return dmp.patch_toText(patch)


def set_field_data(obj, field, data):
    field_inst = obj._meta.get_field(field)
    # data = decode(data)
    if field_inst.null and data == 'None':
        data = None
    else:
        data = field_inst.to_python(data)
    setattr(obj, field_inst.attname, data)


def get_field_data(obj, field):
    """Returns field's data"""
    # return encode(obj._meta.get_field(field)._get_val_from_obj(obj))
    return obj._meta.get_field(field).value_to_string(obj)


def obj_diff(obj1, obj2):
    """Create a 'diff' from obj1 to obj2."""
    model = obj1.__class__
    fields = _registry[model]
    lines = []
    for field in fields:
        original_data = get_field_data(obj2, field)
        new_data = get_field_data(obj1, field)
        #data_diff = unified_diff(original_data.splitlines(),
        #                         new_data.splitlines(), context=3)
        data_diff = diff(new_data, original_data)
        lines.extend(["--- {0}.{1}".format(model.__name__, field),
                     "+++ {0}.{1}".format(model.__name__, field)])
        #for line in data_diff:
        #lines.append(force_unicode(data_diff.strip()))
        lines.append(data_diff.strip())

    return "\n".join(lines)


def obj_is_changed(obj1, obj2):
    """Returns True, if watched attributes of obj1 deffer from obj2."""
    model = obj1.__class__
    fields = _registry[model]
    for field in fields:
        original_data = get_field_data(obj2, field)
        new_data = get_field_data(obj1, field)
        if original_data != new_data:
            return True
    return False


def diff_split_by_fields(txt):
    """Returns dictionary object, key is fieldname, value is it's diff"""
    result = {}
    current = None
    lines = txt.split("\n")
    for line in lines:
        if line[:4] == "--- ":
            continue
        if line[:4] == "+++ ":
            line = line[4:].strip()
            result[line] = current = []
            continue
        if current is not None:
            current.append(line)
    for k, v in result.items():
        result[k] = "\n".join(v)
    return result


def unified_diff(fromlines, tolines, context=None):
    """
    Generator for unified diffs. Slightly modified version from Trac 0.11.
    """
    matcher = SequenceMatcher(None, fromlines, tolines)
    for group in matcher.get_grouped_opcodes(context):
        i1, i2, j1, j2 = group[0][1], group[-1][2], group[0][3], group[-1][4]
        if i1 == 0 and i2 == 0:
            i1, i2 = -1, -1  # add support
        yield '@@ -{0:d},{1:d} +{2:d},{3:d} @@'.format(i1 + 1, i2 - i1, j1 + 1, j2 - j1)
        for tag, i1, i2, j1, j2 in group:
            if tag == 'equal':
                for line in fromlines[i1:i2]:
                    yield ' ' + line
            else:
                if tag in ('replace', 'delete'):
                    for line in fromlines[i1:i2]:
                        yield '-' + line
                if tag in ('replace', 'insert'):
                    for line in tolines[j1:j2]:
                        yield '+' + line
