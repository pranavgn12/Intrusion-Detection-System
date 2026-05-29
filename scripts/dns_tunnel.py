import random
import string
import socket

while True:

    subdomain = ''.join(
        random.choices(
            string.ascii_letters +
            string.digits,
            k=40
        )
    )

    domain = f"{subdomain}.example.com"

    try:
        socket.gethostbyname(domain)
    except:
        pass
