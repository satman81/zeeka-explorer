from django.shortcuts import render
from django.http import HttpResponse
import requests

NODE = "127.0.0.1:8765"


def get_blocks(since, max_len=16):
    blocks = []
    while True:
        resp = requests.get(
            "http://{}/explorer/blocks?since={}&count={}".format(NODE, since + len(blocks), 16),
            headers={"X-ZEEKA-NETWORK-NAME": "debug"},
            timeout=2,
        ).json()['blocks']
        if len(resp) == 0 or len(blocks) >= max_len:
            break
        blocks.extend(resp)
    return blocks


def get_balance(acc):
    return requests.get(
        "http://{}/account?address={}".format(NODE, acc),
        headers={"X-ZEEKA-NETWORK-NAME": "debug"},
        timeout=2,
    ).json()['balance']


def get_mpn_accounts():
    return sorted([(int(k), v) for (k,v) in requests.get(
        "http://{}/explorer/mpn/accounts?page=0&page_size=10000".format(NODE),
        headers={"X-ZEEKA-NETWORK-NAME": "debug"},
        timeout=2,
    ).json()['accounts'].items()])


def index(request):
    blocks = get_blocks(0, 10000)
    miners = {}
    for b in blocks:
        if 'RegularSend' in b['body'][0]['data']:
            r = b['body'][0]['data']['RegularSend']
            if r['dst'] not in miners:
                miners[r['dst']]=0
            miners[r['dst']]+=r['amount']
    miners = {k: v/1000000000 for k, v in sorted(miners.items(), key=lambda item: -item[1])}
    return render(request, 'index.html', {'blocks': blocks[-10:], 'miners':miners, 'mpn': get_mpn_accounts()})
