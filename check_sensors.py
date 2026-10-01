"""Check which lab sensors are overdue for calibration."""

import json
from pathlib import Path

import pandas as pd
import yaml


def read_config(config_path: Path) -> dict:
    """Read settings from a YAML file and return them as a dictionary."""
    with open(config_path) as file:
        return yaml.safe_load(file)


def read_sensors(excel_path: Path) -> pd.DataFrame:
    """Read sensor locations and owners from an Excel file."""
    return pd.read_excel(excel_path)


def read_calibrations(csv_path: Path) -> pd.DataFrame:
    """Read calibration status from a CSV file."""
    return pd.read_csv(csv_path)


def join_data(sensors: pd.DataFrame, calibrations: pd.DataFrame) -> pd.DataFrame:
    """Match each sensor with its calibration status using sensor_id."""
    return sensors.merge(calibrations, on="sensor_id")


def find_overdue(data: pd.DataFrame, max_days: int) -> pd.DataFrame:
    """Keep only the sensors where days_since_calibration > max_days."""
    return data[data["days_since_calibration"] > max_days]


def write_json(overdue: pd.DataFrame, output_path: Path) -> None:
    """Save the overdue sensors as a formatted JSON array."""
    # Turn the table into a list of dictionaries, one per sensor
    records = overdue.to_dict(orient="records")
    with open(output_path, "w") as file:
        json.dump(records, file, indent=2)


def main() -> None:
    # Settings from config.yml
    config = read_config(Path("config.yml"))
    max_days = config["max_days_since_calibration"]
    output_file = config["output_file"]

    # Data from the Excel file and the CSV file
    sensors = read_sensors(Path("sensors.xlsx"))
    calibrations = read_calibrations(Path("calibrations.csv"))

    # Join the two tables, then keep only the overdue sensors
    joined = join_data(sensors, calibrations)
    overdue = find_overdue(joined, max_days)

    # Save the result to the file name given in config.yml
    write_json(overdue, Path(output_file))
    print(f"Saved {len(overdue)} overdue sensors to {output_file}")


if __name__ == "__main__":
    main()