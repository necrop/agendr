#======================================================
#
# Tasks
#
# Wrapper for processes to be run through Celery
#
#======================================================

from celery import task

from .lib.imports.analyse.analyse import analyse
from .lib.imports.insert.addtodb import AddToDB
from .lib.imports.insert.rollback import Rollback


@task()
def import_analyse_zip(job):
    analyse(job)


@task()
def import_add_to_db(job):
    AddToDB(job).process()


@task()
def import_rollback(job):
    Rollback(job).process()
