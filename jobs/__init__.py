"""Initialize and register Job."""

from nautobot.apps.jobs import register_jobs
from .import_locations import ImportLocationsCSV

register_jobs(ImportLocationsCSV)