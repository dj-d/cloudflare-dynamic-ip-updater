"""
References: 
    - python-cloudflare:
        - https://blog.cloudflare.com/python-cloudflare/
        - https://github.com/cloudflare/cloudflare-python/tree/main
    - DNS Record Details: https://developers.cloudflare.com/api/python/resources/dns/subresources/records/methods/get/
    - Update DNS Record: https://developers.cloudflare.com/api/python/resources/dns/subresources/records/methods/edit/
    - List Zones: https://developers.cloudflare.com/api/resources/zones/methods/list/
    - List DNS Records: https://developers.cloudflare.com/api/resources/dns/subresources/records/methods/list/
"""

import os
from time import sleep
from typing_extensions import Literal

import requests
import subprocess
from cloudflare import Cloudflare


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
        print(f'Actual IP: {_r.json()["ip"]}')

        return _r.json()['ip']
    else:
        print(f'Error while getting actual IP: {_r.json()}')

        telegram_notification(
            api_key=TL_API_KEY,
            chat_id=TL_CHAT_ID,
            message=f'Error while getting actual IP: {_r.json()}'
        )

        raise Exception(f'Error while getting actual IP: {_r.json()}')


def get_dns_record_ip(cf_client: Cloudflare, zone_id: str, dns_record_id: str) -> str:
    try:
        record = cf_client.dns.records.get(
            zone_id=zone_id,
            dns_record_id=dns_record_id
        )

        return record.content
    except Exception as e:
        print(f'Error while getting DNS record: {e}')

        telegram_notification(
            api_key=TL_API_KEY,
            chat_id=TL_CHAT_ID,
            message=f'Error while getting DNS record: {e}'
        )

        raise Exception(f'Error while getting DNS record: {e}')


def update_dns_record(cf_client: Cloudflare, zone_id: str, dns_record_id: str, dns_record_name: str, ip: str, record_type: Literal['A'] = 'A') -> bool:
    try:
        response = cf_client.dns.records.update(
            zone_id=zone_id,
            dns_record_id=dns_record_id,
            name=dns_record_name,
            content=ip,
            type=record_type
        )

        print(f'DNS record updated: {response}')
        return True
    except Exception as e:
        print(f'Error while updating DNS record: {e}')

        telegram_notification(
            api_key=TL_API_KEY,
            chat_id=TL_CHAT_ID,
            message=f'Error while updating DNS record: {e}'
        )

        raise Exception(f'Error while updating DNS record: {e}')


if __name__ == '__main__':
    BEARER_TOKEN = str(os.environ.get('BEARER_TOKEN'))
    DNS_RECORD_ID = str(os.environ.get('DNS_RECORD_ID'))
    DNS_RECORD_NAME = str(os.environ.get('DNS_RECORD_NAME'))
    ZONE_ID = str(os.environ.get('ZONE_ID'))
    TL_API_KEY = str(os.environ.get('TL_API_KEY'))
    TL_CHAT_ID = str(os.environ.get('TL_CHAT_ID'))

    cf = Cloudflare(
        api_token=BEARER_TOKEN
    )

    while True:
        current_ip = get_actual_ip()

        record_ip = get_dns_record_ip(
            cf_client=cf,
            zone_id=ZONE_ID,
            dns_record_id=DNS_RECORD_ID
        )

        if current_ip != record_ip:
            update_response = update_dns_record(
                cf_client=cf,
                zone_id=ZONE_ID,
                dns_record_id=DNS_RECORD_ID,
                dns_record_name=DNS_RECORD_NAME,
                ip=current_ip
            )

            if update_response:
                telegram_notification(
                    api_key=TL_API_KEY,
                    chat_id=TL_CHAT_ID,
                    message=f'IP updated to {current_ip}'
                )
        else:
            print(f'IP already updated to {current_ip}')

        sleep(300)