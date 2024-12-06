"""Custom Job for Data Population Lab to import Locations into Nautobot."""

import csv
from io import StringIO

from nautobot.dcim.models import Location, LocationType
from nautobot.extras.models import Status
from nautobot.apps.jobs import FileVar, Job

US_STATE_ABBR_MAP = {
    'AL': 'Alabama',
    'AK': 'Alaska',
    'AZ': 'Arizona',
    'AR': 'Arkansas',
    'CA': 'California',
    'CO': 'Colorado',
    'CT': 'Connecticut',
    'DE': 'Delaware',
    'FL': 'Florida',
    'GA': 'Georgia',
    'HI': 'Hawaii',
    'ID': 'Idaho',
    'IL': 'Illinois',
    'IN': 'Indiana',
    'IA': 'Iowa',
    'KS': 'Kansas',
    'KY': 'Kentucky',
    'LA': 'Louisiana',
    'ME': 'Maine',
    'MD': 'Maryland',
    'MA': 'Massachusetts',
    'MI': 'Michigan',
    'MN': 'Minnesota',
    'MS': 'Mississippi',
    'MO': 'Missouri',
    'MT': 'Montana',
    'NE': 'Nebraska',
    'NV': 'Nevada',
    'NH': 'New Hampshire',
    'NJ': 'New Jersey',
    'NM': 'New Mexico',
    'NY': 'New York',
    'NC': 'North Carolina',
    'ND': 'North Dakota',
    'OH': 'Ohio',
    'OK': 'Oklahoma',
    'OR': 'Oregon',
    'PA': 'Pennsylvania',
    'RI': 'Rhode Island',
    'SC': 'South Carolina',
    'SD': 'South Dakota',
    'TN': 'Tennessee',
    'TX': 'Texas',
    'UT': 'Utah',
    'VT': 'Vermont',
    'VA': 'Virginia',
    'WA': 'Washington',
    'WV': 'West Virginia',
    'WI': 'Wisconsin',
    'WY': 'Wyoming',
    'DC': 'District of Columbia',
}

LOCATION_NAME_MAP = {
    "Den": "Denver",
    "SanDiego": "San Diego",
}

class ImportLocationsCSV(Job):
    """Import Locations from CSV file.

    Args:
        Job (Job): Nautobot Job.
    """

    csv_file = FileVar(
        label="Locations CSV File",
        required=True
    )

    class Meta:  # pylint: disable=too-few-public-methods
        """Meta object boilerplate for onboarding."""

        name = "Import Locations from CSV"
        description = "Create Locations from CSV file."
        has_sensitive_variables = False

    def run(self, *args, **kwargs):
        """Process Locations CSV."""

        self.csv_file = kwargs["csv_file"]

        active_status = Status.objects.get(name="Active")
        state_loctype = LocationType.objects.get(name="State")
        city_loctype = LocationType.objects.get(name="City")

        decoded_csv = self.csv_file.read().decode("utf-8")

        csv_file = csv.DictReader(StringIO(decoded_csv))
        for line in csv_file:
            location_name = line["name"].replace("-BR", "").replace("-DC", "")
            if location_name in LOCATION_NAME_MAP:
                location_name = LOCATION_NAME_MAP[location_name]
            location_type_name = "Branch" if line["name"].endswith("BR") else "Data Center"
            location_type = LocationType.objects.get(name=location_type_name)
            city = line["city"]
            state = line["state"]
            if state in US_STATE_ABBR_MAP:
                state = US_STATE_ABBR_MAP[state]

            state_loc, _ = Location.objects.get_or_create(name=state, location_type=state_loctype, defaults={"status": active_status})
            city_loc, _ = Location.objects.get_or_create(name=city, location_type=city_loctype, parent=state_loc, defaults={"status": active_status})
            Location.objects.get_or_create(name=location_name, parent=city_loc, defaults={"location_type": location_type, "status": active_status})
