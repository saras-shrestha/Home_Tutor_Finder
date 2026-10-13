
import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import Region, District, City


DATA_DIR = Path(__file__).resolve().parents[2] / "data"

TYPE_MAPPING = {
    "metropolitan city": "METROPOLITAN",
    "sub-metropolitan city": "SUB_METROPOLITAN",
    "municipality": "MUNICIPALITY",
    "rural municipality": "RURAL_MUNICIPALITY",
}


def read_json(filename):
    path = DATA_DIR / filename

    if not path.exists():
        raise CommandError(f"File not found: {path}")

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise CommandError(f"Invalid JSON in {filename}: {exc}")

    if not isinstance(data, list):
        raise CommandError(f"{filename} must contain a JSON list.")

    return data


class Command(BaseCommand):
    help = "Import Nepal provinces, districts and local levels"

    def handle(self, *args, **options):
        # Read and validate files before changing the database.
        provinces = read_json("provinces.json")
        districts = read_json("districts.json")
        local_levels = read_json("local_levels.json")

        if len(provinces) != 7:
            raise CommandError(
                f"Expected 7 provinces; found {len(provinces)}."
            )

        if len(districts) != 77:
            raise CommandError(
                f"Expected 77 districts; found {len(districts)}."
            )

        if len(local_levels) != 753:
            raise CommandError(
                f"Expected 753 local levels; found {len(local_levels)}."
            )

        # Validate local-level types before starting the transaction.
        for item in local_levels:
            type_name = item["type_en"].strip().lower()

            if type_name not in TYPE_MAPPING:
                raise CommandError(
                    f"Unknown local-level type: {item['type_en']}"
                )

        with transaction.atomic():
            regions_by_code = {}
            districts_by_code = {}

            # 1. Import provinces.
            for item in provinces:
                region, _ = Region.objects.get_or_create(
                    name=item["name_en"].strip()
                )

                regions_by_code[str(item["code"])] = region

            # 2. Import districts and connect them to provinces.
            for item in districts:
                province_code = str(item["province_code"])

                if province_code not in regions_by_code:
                    raise CommandError(
                        f"Unknown province code: {province_code}"
                    )

                district, _ = District.objects.get_or_create(
                    name=item["name_en"].strip(),
                    region=regions_by_code[province_code],
                )

                districts_by_code[str(item["code"])] = district

            # 3. Import all local levels into City.
            for item in local_levels:
                district_code = str(item["district_code"])

                if district_code not in districts_by_code:
                    raise CommandError(
                        f"Unknown district code: {district_code}"
                    )

                type_name = item["type_en"].strip().lower()

                City.objects.update_or_create(
                    name=item["name_en"].strip(),
                    district=districts_by_code[district_code],
                    defaults={
                        "local_level_type": TYPE_MAPPING[type_name],
                    },
                )

        self.stdout.write(
            self.style.SUCCESS(
                "Nepal administrative locations imported successfully!"
            )
        )
        self.stdout.write(f"Dataset provinces: {len(provinces)}")
        self.stdout.write(f"Dataset districts: {len(districts)}")
        self.stdout.write(f"Dataset local levels: {len(local_levels)}")