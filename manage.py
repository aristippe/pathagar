#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    # TODO: this tricks manage.py into thinking it is executed on the parent
    # directory. It should be removed once #13 is handled, and the project
    # tree follow a more standard django-project structure.
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                 os.pardir)))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pathagar.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
