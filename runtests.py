# -*- coding: utf-8 -*-
import os
import sys


def main():
    from django.conf import settings
    settings.configure(
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:'
            }
        },
        INSTALLED_APPS = [
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'versioning',
        ],
        MIDDLEWARE_CLASSES = [
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            'django.middleware.clickjacking.XFrameOptionsMiddleware',
            "versioning.middleware.VersioningMiddleware",
        ],
        STATIC_URL = '/static/',
        TEST_RUNNER = 'django.test.simple.DjangoTestSuiteRunner',
        TEMPLATE_DIRS = [],
        DEBUG = True,
        TEMPLATE_DEBUG = True,
        ROOT_URLCONF = 'runtests',
    )

    from django.conf.urls import patterns, include, url
    from django.contrib import admin
    global urlpatterns
    urlpatterns = patterns(
        '',
        url(r'^admin/', include(admin.site.urls)),
        url(r'^versioning/', include('versioning.urls')),
    )
    admin.autodiscover()

    # Run the test suite, including the extra validation tests.
    from django.test.utils import get_runner
    TestRunner = get_runner(settings)

    test_runner = TestRunner(verbosity=1, interactive=False, failfast=False)
    failures = test_runner.run_tests(['versioning'])
    sys.exit(failures)


if __name__ == "__main__":
    main()
