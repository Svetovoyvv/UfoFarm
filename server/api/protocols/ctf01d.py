# params: SYSTEM_URL, SYSTEM_TOKEN, TIMEOUT_QUERY
import requests

from models import FlagSubmit, FlagStatus, Flag


def protocol_error(flags: list[Flag], error: str):
    for flag in flags:
        yield FlagSubmit(flag.flag, FlagStatus.QUEUED, error)


def submit_flags(flags: list[Flag], config):
    system_url = config.get('SYSTEM_URL', None)
    system_token = config.get('SYSTEM_TOKEN', None)
    timeout_query = config.get('TIMEOUT_QUERY', 5)

    if not system_url:
        return protocol_error(flags, '[Settings] System url not set')

    if not system_token:
        return protocol_error(flags, '[Settings] System token not set')

    system_url = system_url.strip()
    if 'http://' not in system_url and 'https://' not in system_url:
        system_url = 'http://' + system_url

    system_token = system_token.strip()

    for flag in flags:

        r = requests.get(
            system_url + '/flag',
            query={
                "teamid": system_token,
                "flag": flags
            },
            timeout=timeout_query,
        )
        status = {
            400: FlagStatus.QUEUED,
            403: FlagStatus.REJECTED,
            200: FlagStatus.ACCEPTED
        }
        yield FlagSubmit(flag, status.get(r.status_code, FlagStatus.QUEUED), r.text)
