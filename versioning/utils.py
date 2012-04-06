from difflib import SequenceMatcher

#from django.utils.encoding import smart_unicode
# Google Diff Match Patch library
# http://code.google.com/p/google-diff-match-patch
from diff_match_patch import diff_match_patch

from versioning import _registry

dmp = diff_match_patch()


def revisions_for_object(instance):
    from models import Revision
    return Revision.objects.get_for_object(instance)


def diff(txt1, txt2):
    """Create a 'diff' from txt1 to txt2."""
    patch = dmp.patch_make(txt1, txt2)
    return dmp.patch_toText(patch)


def obj_diff(obj1, obj2):
    """Create a 'diff' from obj1 to obj2."""
    model = obj1.__class__
    fields = _registry[model]
    lines = []
    for field in fields:
        original_data = unicode(getattr(obj2, field))
        new_data = unicode(getattr(obj1, field))
        #data_diff = unified_diff(original_data.splitlines(),
        #                         new_data.splitlines(), context=3)
        data_diff = diff(new_data, original_data)
        lines.extend([u"--- %s.%s" % (model.__name__, field),
                     u"+++ %s.%s" % (model.__name__, field)])
        #for line in data_diff:
        #lines.append(smart_unicode(data_diff.strip()))
        lines.append(data_diff.strip())

    return "\n".join(lines)


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
    for k, v in result.iteritems():
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
        yield '@@ -%d,%d +%d,%d @@' % (i1 + 1, i2 - i1, j1 + 1, j2 - j1)
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
