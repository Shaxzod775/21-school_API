AUTH_URL = "https://auth.sberclass.ru/auth/realms/EduPowerKeycloak/protocol/openid-connect/token"
BASE_URL = "https://edu-api.21-school.ru/services/21-school/api/v1{}"


HEADERS =  {
    'Authorization': 'Bearer {}'
}

INTENSIVE = {
    # FIRST WEEK
    'T01D01': (19153, '1_week'),
    'T02D02': (19154, '1_week'),
    'T03D03': (19155, '1_week'),
    'T04D04': (19156, '1_week'),
    'E01D05': (19157, '1_week'),
    'P01D06': (19160, '1_week'),
    # SECOND WEEK
    'T05D08': (19161, '2_week'),
    'T06D09': (19162, '2_week'),
    'T07D10': (19163, '2_week'),
    'T08D11': (62331, '2_week'),
    'E02D12': (19368, '2_week'),
    'P02D13': (19165, '2_week'),
    # THIRD WEEK
    'T09D15': (19166, '3_week'),
    'T10D16': (19168, '3_week'),
    'T11D17': (19169, '3_week'),
    'T12D18': (19170, '3_week'),
    'E03D19': (19369, '3_week'),
    'P03D20': (19171, '3_week'),
    #FOURTH WEEK
    'T13D22': (19172, '4_week'),
    'T14D23': (19173, '4_week'),
    'T15D24': (19174, '4_week'),
    'E04D26': (19459, '4_week'),
}

EXAMS = ["E01D05", "E02D12", "E03D19", "E04D26"]
NO_STYLE_TASKS = ["T01D01", "T02D02", "E01D05", "E02D12", "E03D19", "E04D26"]
INTENSIVE_MONTHS = ["september_november", "february", "march"]
intensive_month_selected = "march"

