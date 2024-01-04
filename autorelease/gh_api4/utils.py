import datetime
def string_to_datetime(string):
    # TODO: move this elsewhere
    return datetime.datetime.strptime(string, "%Y-%m-%dT%H:%M:%SZ")

