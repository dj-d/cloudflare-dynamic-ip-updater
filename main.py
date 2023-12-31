"""
References: 
    - Make API calls: https://developers.cloudflare.com/fundamentals/api/how-to/make-api-calls/
    - Verify Token: https://developers.cloudflare.com/api/operations/user-api-tokens-verify-token
    - List DNS Records: https://developers.cloudflare.com/api/operations/dns-records-for-a-zone-list-dns-records
    - DNS Record Details: https://developers.cloudflare.com/api/operations/dns-records-for-a-zone-dns-record-details
    - Update DNS Record: https://developers.cloudflare.com/api/operations/dns-records-for-a-zone-update-dns-record
"""

import os
import requests
import subprocess
from time import sleep
import logging


# FIXME: fix running in local environment (by python3 main.py)


logging.basicConfig(
    filename='app.log',
    format='%(levelname)s - %(asctime)s - %(message)s',
    level=logging.INFO
)


def telegram_notification(api_key: str, chat_id: str, message: str) -> None:
    """
    Send a message to a Telegram chat using the Telegram API.

    :param message: The message to send.
    :param api_key: The API key of the bot.
    :param chat_id: The chat ID of the chat to send the message to.

    :return: None
    """
    _message = '%20'.join(message.split())

    cmd = f'curl -s "https://api.telegram.org/bot{api_key}/sendMessage?chat_id={chat_id}&text={_message}"'

    subprocess.call(cmd, shell=True)


def get_actual_ip() -> str:
    _r = requests.get('https://api.ipify.org/?format=json')

    if _r.status_code == 200:
        logging.info(f'Actual IP: {_r.json()["ip"]}')

        return _r.json()['ip']
    else:
        logging.error(f'Error while getting actual IP: {_r.json()}')

        telegram_notification(
            api_key=TL_API_KEY,
            chat_id=TL_CHAT_ID,
            message=f'Error while getting actual IP: {_r.json()}'
        )

        raise Exception(f'Error while getting actual IP: {_r.json()}')


def check_token(bearer_token: str) -> bool:
    _r = requests.get(
        'https://api.cloudflare.com/client/v4/user/tokens/verify',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {bearer_token}'
        }
    )

    if _r.status_code == 200:
        logging.info(f'Token is active: {_r.json()["result"]["status"]}')

        return _r.json()['result']['status'] == 'active'
    else:
        logging.error(f'Error while checking token: {_r.json()}')

        telegram_notification(
            api_key=TL_API_KEY,
            chat_id=TL_CHAT_ID,
            message=f'Error while checking token: {_r.json()}'
        )

        # raise Exception(f'Error while checking token: {_r.json()}')


def get_record_list(bearer_token: str, zone_id: str) -> list:
    _r = requests.get(
        f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {bearer_token}'
        }
    )

    if _r.status_code == 200:
        logging.info(f'Record list: {_r.json()["result"]}')

        return _r.json()['result']
    else:
        logging.error(f'Error while getting record list: {_r.json()}')

        telegram_notification(
            api_key=TL_API_KEY,
            chat_id=TL_CHAT_ID,
            message=f'Error while getting record list: {_r.json()}'
        )

        raise Exception(f'Error while getting record list: {_r.json()}')


def get_record_ip(bearer_token: str, dns_record_id: str, zone_id: str) -> str:
    _r = requests.get(
        f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{dns_record_id}',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {bearer_token}'
        }
    )

    if _r.status_code == 200:
        logging.info(f'Record IP: {_r.json()["result"]["content"]}')

        return _r.json()['result']['content']
    else:
        logging.error(f'Error while getting record: {_r.json()}')

        telegram_notification(
            api_key=TL_API_KEY,
            chat_id=TL_CHAT_ID,
            message=f'Error while getting record: {_r.json()}'
        )

        raise Exception(f'Error while getting record: {_r.json()}')


def update_record(bearer_token: str, dns_record_id: str, zone_id: str, dns_record_name: str, new_ip: str):
    _r = requests.put(
        f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{dns_record_id}',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {bearer_token}'
        },
        json={
            'content': new_ip,
            'name': dns_record_name,
            'proxied': False,
            'type': 'A',
            'comment': 'Domain record',
            'ttl': 1
        }
    )

    if _r.status_code == 200:
        logging.info(f'Updated record IP: {_r.json()["result"]["content"]}')

        return _r.json()['result']['content']
    else:
        logging.error(f'Error while updating record: {_r.json()}')

        telegram_notification(
            api_key=TL_API_KEY,
            chat_id=TL_CHAT_ID,
            message=f'Error while updating record: {_r.json()}'
        )

        raise Exception(f'Error while updating record: {_r.json()}')


if __name__ == '__main__':
    DNS_RECORD_ID = os.environ.get('DNS_RECORD_ID')
    DNS_RECORD_NAME = os.environ.get('DNS_RECORD_NAME')
    ZONE_ID = os.environ.get('ZONE_ID')
    BEARER_TOKEN = os.environ.get('BEARER_TOKEN')
    TL_API_KEY = os.environ.get('TL_API_KEY')
    TL_CHAT_ID = os.environ.get('TL_CHAT_ID')

    if not check_token(BEARER_TOKEN):
        logging.error('Token is not active')

        telegram_notification(
            api_key=TL_API_KEY,
            chat_id=TL_CHAT_ID,
            message=f'Token is not active'
        )

        raise Exception('Token is not active')

    while True:
        actual_ip = get_actual_ip()

        record_ip = get_record_ip(
            bearer_token=BEARER_TOKEN,
            dns_record_id=DNS_RECORD_ID,
            zone_id=ZONE_ID
        )

        if actual_ip != record_ip:
            res = update_record(
                bearer_token=BEARER_TOKEN,
                dns_record_id=DNS_RECORD_ID,
                zone_id=ZONE_ID,
                dns_record_name=DNS_RECORD_NAME,
                new_ip=actual_ip
            )

            logging.info(f'IP changed from {record_ip} to {actual_ip}')

            telegram_notification(
                api_key=TL_API_KEY,
                chat_id=TL_CHAT_ID,
                message=f'IP changed from {record_ip} to {actual_ip}'
            )
        else:
            logging.info(f'IP is actual {actual_ip}')
        
        sleep(5)
