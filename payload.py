import json
import random

import requests
from lorem.text import TextLorem

CREATE_COUNT = 10000
URL = '/notes/'
TAG = 'Normal_Requests'
 # GET||/url||case_tag||body(optional)
TEMPL_POST = '{}||{}||{}||{}\n'
TEMPL_GET = '{}||{}||{}\n'

if __name__ == '__main__':
    # create note
    lorem = TextLorem(srange=(3, 50))
    with open('./data.txt', 'wt', encoding='utf-8') as f:

        for n, i in enumerate(range(CREATE_COUNT)):
            # res = requests.post(
            #         url=URL,
            #         json={'text': lorem.sentence()}
            # )
            body = json.dumps({'text': lorem.sentence()})
            line = TEMPL_POST.format('POST', URL, TAG, body)
            f.write(line)

        # update note
        for i in range(CREATE_COUNT):
            # idx = random.randint(0, CREATE_COUNT)
            # url = f'{URL}{idx}/'
            # print(idx, url, end=': ')
            # resp = requests.patch(
            #         url=url,
            #         json={'completed': True}
            # )
            line = TEMPL_GET.format('GET', URL, TAG)
            f.write(line)
