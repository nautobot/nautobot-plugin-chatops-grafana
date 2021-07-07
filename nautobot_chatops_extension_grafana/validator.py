from termcolor import colored
from typing import List
from schema_enforcer import config
from schema_enforcer.schemas.manager import SchemaManager
from schema_enforcer.instances.file import InstanceFileManager
from schema_enforcer.exceptions import InvalidJSONSchema


def validate(strict: bool = False) -> List[str]:
    """Validates instance files against defined schema.

    Args:
        strict (bool): Forces a stricter schema check that warns about unexpected additional properties
    """

    config.load()

    try:
        smgr = SchemaManager(config=config.SETTINGS)
    except InvalidJSONSchema as exc:
        raise InvalidJSONSchema(str(exc))

    if not smgr.schemas:
        return []

    ifm = InstanceFileManager(config=config.SETTINGS)

    if not ifm.instances:
        return []

    if config.SETTINGS.data_file_automap:
        ifm.add_matches_by_property_automap(smgr)

    errors = []
    for instance in ifm.instances:
        for result in instance.validate(smgr, strict):

            result.instance_type = "FILE"
            result.instance_name = instance.filename
            result.instance_location = instance.path

            if not result.passed():
                msg = colored("FAIL", "red") + f" | [ERROR] {result.message}"
                if result.instance_type == "FILE":
                    msg += f" [{result.instance_type}] {result.instance_location}/{result.instance_name}"

                elif result.instance_type == "HOST":
                    msg += f" [{result.instance_type}] {result.instance_hostname}"

                msg += f" [PROPERTY] {':'.join(str(item) for item in result.absolute_path)}"
                errors.append(msg)

    return errors
