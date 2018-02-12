from django.conf import settings
import requests


def push(message, *channels):
    for channel in channels:
        response = requests.post(
            'http://ws:%s/api/1.0.0/%s/channels/%s/' % (
                settings.THUNDERPUSH_PORT,
                settings.THUNDERPUSH_PUBLIC_KEY,
                channel
            ),
            headers={
                'X-Thunder-Secret-Key': settings.THUNDERPUSH_PRIVATE_KEY
            },
            json=message
        )

        response.raise_for_status()
