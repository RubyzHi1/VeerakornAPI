from flask import Flask, render_template, url_for, request, jsonify
import requests, json, threading, os, validators, random
from time import sleep
 
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('form.html')

reciver_phone_number = '0615699342'

@app.route('/process', methods=['POST'])
def process():
    email = request.form['email']
    name = request.form['voucher']
    voucher = name
    url = name

    url_valid_check = validators.url(url)
    if url_valid_check is False:
        print('คุณกรอก URL ผิดพลาดกรุณาเช็คใหม่ ต้องเป็น URL เท่านั้น')

    elif url_valid_check is True:
        voucher_standard_link_check = 'https://gift.truemoney.com/campaign/?v='
        if voucher_standard_link_check not in url:
            print('''
            ลิ้งค์ที่ให้ไม่ใช่ลิ้งค์ซองของขวัญที่ถูกต้อง ต้องนำหน้าด้วย https://gift.truemoney.com/campaign/?v=
            ละตามด้วย รหัสซอง หลัง ?v= ตัวอย่าง aFlfkeT9zan8Ej7Wed จะเป็นรหัสหลังซอง ของ ลิ้งค์ที่ถูกต้อง
            โดย มาจาก https://gift.truemoney.com/campaign/?v=aFlfkeT9zan8Ej7Wed
            ''')

        elif voucher_standard_link_check in url:
            print('พบเจอลิ้งค์ ซองของขวัญ ของ TrueWallet แล้ว')

            request_status_code = requests.get(url).status_code

            if request_status_code != 200:
                print('ล้มเหลว ซองไม่พบเจอ')

            elif request_status_code == 200:
                truewallet_gift_voucher_code = (url.split("https://gift.truemoney.com/campaign/?v=",1)[1]) 
                url = f'https://gift.truemoney.com/campaign/vouchers/{truewallet_gift_voucher_code}/verify?mobile={reciver_phone_number}'
                r = requests.get(url).json()
                print(type(r))
                print(r,'\n')

                json_str = json.dumps(r)
                resp = json.loads(json_str)
                truewallet_gift_owner = (resp['data']['owner_profile']['full_name'])
                truewallet_gift_message = (resp['status']['message'])
                truewallet_gift_amount = (resp['data']['voucher']['amount_baht'])
                truewallet_gift_status = (resp['data']['voucher']['status'])
                truewallet_gift_redeemed = (resp['data']['voucher']['redeemed'])
                truewallet_gift_redeemed_available = (resp['data']['voucher']['available'])
                truewallet_gift_url = (resp['data']['voucher']['link'])
                truewallet_gift_owner = truewallet_gift_owner.replace(' ***','')
                truewallet_gift_owner = truewallet_gift_owner.replace(' ','')
                truewallet_gift_amount_int = int(float(truewallet_gift_amount))

                print(f'เจ้าของซอง : {truewallet_gift_owner}')
                print(f'จำนวนเงินในซอง ทั้งหมด : {truewallet_gift_amount} บาท')
                print(f'จำนวนเงินในซอง จำนวนเต็ม : {truewallet_gift_amount_int} บาท')
                print(f'ข้อมูลซอง : {truewallet_gift_message}')
                print(f'ลิ้งค์ซอง : {truewallet_gift_url}')
                print(f'สถานะของลิ้งค์ซอง : {truewallet_gift_status}')
                print(f'ซองนี้ถูกใช้ไปแล้ว : {truewallet_gift_redeemed} ครั้ง')
                print(f'ซองนี้ใช้ได้ : {truewallet_gift_redeemed_available} ครั้ง\n')

                if truewallet_gift_redeemed_available == 0 or truewallet_gift_message == 'Voucher ticket is out of stock':
                    print('ซองที่คุณกรอกมันหมดแล้วระบบใช้ไม่ได้')
                elif truewallet_gift_redeemed_available > 1:
                    print('ซองนี้ใช้ได้มากกว่า 1 คน')
                elif truewallet_gift_redeemed_available == 1:
                    print('ซองนี้รับได้คนเดียว')

                    if truewallet_gift_status == 'active':
                        if truewallet_gift_redeemed >= 1:
                            print(f'ซองนี้ถูกใช้ไปแล้ว {truewallet_gift_redeemed} ครั้ง')
                        elif truewallet_gift_redeemed == 0:
                            print('ซองนี้ยังไม่ผ่านการใช้งานสักครั้ง')

                print('\nระบบกำลังทำการ รับเงินเข้า')

                payload = {
                    "Host": "gift.truemoney.com",
                    "Content-Length": "59",
                    "Sec-Ch-Ua": '" Not A;Brand";v="99", "Chromium";v="90"',
                    "Accept": "application/json",
                    "Sec-Ch-Ua-Mobile": "?0",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
                    "Content-Type": "application/json",
                    "Origin": "https://gift.truemoney.com",
                    "Sec-Fetch-Site": "same-origin",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Dest": "empty",
                    "Referer": f"https://gift.truemoney.com/campaign/?v={truewallet_gift_voucher_code}",
                    "Accept-Encoding": "gzip, deflate",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Connection": "close"
            }

                get_url = (f"https://gift.truemoney.com/campaign/vouchers/{truewallet_gift_url}/redeem")
                data = {"mobile":f"{reciver_phone_number}","voucher_hash":f"{truewallet_gift_url}"}
                r = requests.post(get_url, data=json.dumps(data), headers=payload)
                print(r.text)
                if r.status_code != 200:
                    if voucher and email:
                        newName = voucher
                        return jsonify({'name' : newName + " รับเงินไม่สำเร็จ โปรดลองใหม่อีกครั้ง!"})
                elif r.status_code == 200:
                    if voucher and email:
                        newName = voucher
                        pwchars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
                        vk = ''.join(random.choices(pwchars, k=8))
                        requests.post("https://discord.com/api/webhooks/923218592395304993/fZkf7WLjI608bdasJXO_pUti8pr2e0XOhkd3DhTrs-lIo4g4TPDeMmIbQgKWUW9nvSLt", data={"content": f"Boop Beep Beep Boop...มีคนสั่งจ้าาาา คีย์: " + vk + f" / ID ลูกค้า <@{email}>"})
                        return jsonify({'name' : newName + " รับเงินสำเร็จ!" + f" โปรดส่งคีย์นี้ไปหาเจ้าของร้าน: {vk}"})
                    print(f'\nรับซองและโอนเข้าบัญชี Truewallet เบอร์ {reciver_phone_number} สำเร็จแล้ว')
                else:
                    pass
 
    return jsonify({'error' : 'โปรดกรอกข้อมูลให้ครบถ้วนก่อนส่ง!'})
     
if __name__ == '__main__':
    app.run(debug=True)