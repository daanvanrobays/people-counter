import requests
import logging


log = logging.getLogger(__name__)


def post_api(url, device, total: int, total_down: int, total_up: int, delta: int):
    log.info(f"API - total: {total}, total_down: {total_down}, total_up: {total_up}, delta: {delta} ")
    post_body = {'apparaat': device, 'binnen': total_down, 'buiten': total_up, 'delta': delta, 'totaal': total}
    resp = requests.post(url, json=post_body)
    log.info(resp.text)
    return resp
