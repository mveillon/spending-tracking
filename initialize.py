import shutil
from os.path import exists, join
from os import makedirs
from datetime import date, timedelta

from src.utilities.paths import config_path, sheet_dir, untracked_path
from src.utilities.parse_args import parse_args


def check_overwrite(dest: str) -> bool:
    """
    Checks with the user on the CLI before overwriting files,
    unless the --force option is enabled.

    Paramters:
        dest (str): the destination path

    Returns:
        allowed (bool): whether the overwrite is approved
    """
    return (
        parse_args().force
        or not exists(dest)
        or (
            input(
                f"This will overwrite existing the data at {dest}. "
                + "Do you want to continue? (y/N)"
            )
            .lower()
            .strip()
            in ("y", "yes")
        )
    )


def init_config():
    """
    Initialize the config_overwrite.yml file.

    Parameters:
        None

    Returns:
        None
    """
    dest = config_path()

    if check_overwrite(dest):
        with open(dest, "w") as out:
            out.write(
                "\n\n".join(
                    (
                        "globals: {}",
                        "plots: {}",
                        "aggregations: {}",
                    )
                )
            )


def add_spending_dir():
    """
    Creates the base of the spending directory.

    Parameters:
        None

    Returns:
        None
    """
    dest = sheet_dir()
    makedirs(dest, exist_ok=True)

    untracked = untracked_path()
    if check_overwrite(untracked):
        shutil.copy("base_sheet.xlsx", untracked)

    current = date(parse_args().year, 1, 1)
    end = min(date.today(), date(current.year, 12, 31))
    while current <= end:
        this_month = join(dest, current.strftime("%B") + ".xlsx")

        if check_overwrite(this_month):
            shutil.copy("base_sheet.xlsx", this_month)
            next_month = current + timedelta(days=31)
            current = date(next_month.year, next_month.month, 1)

        else:
            current = date.max


if __name__ == "__main__":
    init_config()
    add_spending_dir()
