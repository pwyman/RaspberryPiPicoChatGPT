import json
import network
import time
import urequests
import constants

def chat_gpt(ssid, password, endpoint, api_key, model, prompt, max_tokens):
        # Just making our internet connection
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(ssid, password)

        # Wait for connect or fail
        max_wait = 10
        while max_wait > 0:
            if wlan.status() < 0 or wlan.status() >= 3:
                break
            max_wait -= 1
            print('waiting for connection...')
            time.sleep(1)
        # Handle connection error
        if wlan.status() != 3:
            print(wlan.status())
            raise RuntimeError('network connection failed')
        else:
            print('connected')
            print(wlan.status())
            status = wlan.ifconfig()

        # Begin formatting request
        headers = {'Content-Type': 'application/json',
                   "Authorization": "Bearer " + api_key}
        data = {"model": model,
                "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
                "max_tokens": max_tokens}

        print("Attempting to send Prompt")
        r = urequests.post("https://api.openai.com/v1/{}".format(endpoint),
                           json=data,
                           headers=headers)

        if r.status_code >= 300 or r.status_code <= 200:
            print("There was an error with your request \n" +
                  "Response Status: " + str(r.text))
        else:
            print("Success")
            response_data = json.loads(r.text)
            completion = response_data["choices"][0]["message"]["content"]
            print(completion)
        r.close()

chat_gpt(constants.INTERNET_NAME,
             constants.INTERNET_PASSWORD,
             "chat/completions",
             constants.CHAT_GPT_API_KEY,
             "gpt-4o-mini",
             "What is a Raspberry Pi Pico?",
             100)
