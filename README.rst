==================
Django-Versioning
==================

Django-versioning allows you to version the data stored in django models, and stores only diff, not content copy.

Supports all field types excepts ManyToMany (currently).

Django-versioning as small as possible, and follows the `KISS principle <http://en.wikipedia.org/wiki/KISS_principle>`_.

Usage
======

settings.py::

    MIDDLEWARE_CLASSES = [
        # ...
        "versioning.middleware.VersioningMiddleware",
        # ...
    ]
    # ...
    INSTALLED_APPS = [
        # ...
       'versioning',  # Should be after apps with versioned models
        # ...
    ]

wiki/models.py::

    from django.db import models
    from django.contrib.auth.models import User
    import versioning

    class Article(models.Model):
        title = models.CharField()
        body = models.TextField()
        is_active = models.BooleanField()
        weight = models.IntegerField(blank=True, null=True)
        creator = models.ForeignKey(User, blank=True, null=True)
        
        class Meta:
            permissions = (
                ("wiki.browse_revision_article", "Can browse revisions"),
                ("wiki.reapply_revision_article", "Can repply revision"),
            )

    versioning.register(
        Article,
        ['title', 'body', 'is_active', 'weight', 'creator', ]
    )

wiki/templates/wiki/article_detail.html::

    ...
    <a href="{% url versioning_revision_list content_type=contenttype_id object_id=article.pk %}">View the list of revisions.</a>
    ...

If you have already existent content, to create a first revision, simple run::

    ./manage.py versioning_setup wiki.Article -f

You can also view revisions in admin, by clicking "History" button on change object page.

Forked from https://github.com/brosner/django-versioning , Thanks to Brian Rosner.
