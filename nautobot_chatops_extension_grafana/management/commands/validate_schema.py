from django.core.management.base import BaseCommand
from nautobot_chatops_extension_grafana.validator import validate


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        schema_errors = validate(strict=kwargs["strict"])
        if schema_errors:
            print(",".join(schema_errors))
        else:
            print("ALL SCHEMA VALIDATION CHECKS PASSED √√")

    def add_arguments(self, parser):
        parser.add_argument(
            "--strict",
            action="store_true",
            help="Force a stricter schema check that warns about unexpected additional properties",
        )
