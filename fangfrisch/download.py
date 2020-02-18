"""
Copyright © 2020 Ralph Seichter

This file is part of "Fangfrisch".

Fangfrisch is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Fangfrisch is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Fangfrisch. If not, see <https://www.gnu.org/licenses/>.
"""
import requests
from requests import Response

from fangfrisch import __version__
from fangfrisch.logging import log
from fangfrisch.util import StatusDataPair

CONTENT_LENGTH = 'Content-Length'

_session = requests.Session()
_session.headers['User-Agent'] = f'fangfrisch/{__version__}'


class ClamavItem:
    def __init__(self, section, option, url, check, path, interval, max_size) -> None:
        self.check = check
        self.interval = interval
        self.max_size = max_size
        self.option = option
        self.path = path
        self.section = section
        self.url = url


def _has_valid_length(response: Response, max_length: int) -> StatusDataPair:
    """Check if content length in response is below a given limit.

    :param response: Response object.
    :param max_length: Maximum permitted content length.
    :return: True if length is permitted, False otherwise.
    """
    if CONTENT_LENGTH not in response.headers:  # pragma: no cover
        log.warning(f'Response is missing {CONTENT_LENGTH} header')
        return StatusDataPair(True, -1)
    length = int(response.headers[CONTENT_LENGTH])
    if length > max_length:
        log.error(f'{response.url} size exceeds defined limit ({length}/{max_length})')
        return StatusDataPair(False, length)
    return StatusDataPair(True, length)


def _download(url, max_length: int) -> StatusDataPair:
    """Download from specified URL if content length is below a given limit.

    :param url: Source URL.
    :param max_length: Maximum permitted content length.
    :return: True/Data for successfull downloads, False/None otherwise.
    """
    response = _session.get(url, stream=True, timeout=30)
    if response.status_code != requests.codes.ok:
        log.error(f'{url} download failed: {response.status_code} {response.reason}')
        return StatusDataPair(False)
    check = _has_valid_length(response, max_length)
    if not check.ok:
        return StatusDataPair(False)
    return StatusDataPair(True, response)


def get_digest(ci: ClamavItem, max_size: int = 1024) -> StatusDataPair:
    if not ci.check:
        return StatusDataPair(True)
    download = _download(f'{ci.url}.{ci.check}', max_size)
    if not download.ok:
        return StatusDataPair(False)
    digest = download.data.text.split(' ')[0]  # Returns original text if no space is found
    return StatusDataPair(True, digest)


def get_payload(ci: ClamavItem) -> StatusDataPair:
    download = _download(ci.url, ci.max_size)
    if not download.ok:
        return StatusDataPair(False)
    return StatusDataPair(True, download.data.content)
