import requests
import logging
import threading


log = logging.getLogger(__name__)


def post_api(url, device, total: int, total_down: int, total_up: int, delta: int):
    log.info(f"API - total: {total}, total_down: {total_down}, total_up: {total_up}, delta: {delta} ")
    post_body = {'apparaat': device, 'binnen': total_down, 'buiten': total_up, 'delta': delta, 'totaal': total}
    # Creating a thread to execute the post_request function
    post_thread = threading.Thread(target=post_request, args=(url, post_body))
    # Starting the thread
    post_thread.start()


def post_request(url, post_body):
    resp = requests.post(url, json=post_body)
    log.info(resp.text)
    return resp


