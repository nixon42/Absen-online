from urllib import request, parse
import time
import re
import json
import os
import datetime


def payload(payload):
    dataDict = {}
    pairData = str(payload).split('&')
    for data in pairData:
        data = data.split('=')
        dataDict[data[0]] = data[1]
    return dataDict


def req(url, payload):
    data = ''
    for param in payload:
        data += f'&{param}={payload[param]}'
    fullUrl = f'{url}?{data}'
    while True:
        try:
            res = request.urlopen(fullUrl)
            if re.search('Tanggapan Anda telah direkam.', str(res.read())):
                return (True, '')
            return (False, fullUrl)
        except Exception as e:
            print('Terjadi Error Saat menghubungi Server')
            print('Error : ', e.__str__())
            print('')
            print('Mencoba kembali dalam 5 detik ', end='', flush=True)
            for _ in range(5):
                print('.', flush=True, end='')
            print('')


def countdown(sec):
    print('')
    while sec >= 0:
        # print(sec)
        minute, second = divmod(sec, 60)
        hour, minute = divmod(minute, 60)

        count = f"Next {hour}:{minute}:{second}"
        print(count, end='\r', flush=True)
        sec -= 1
        time.sleep(1)
    print('')


def getGMT7():
    gmt0 = datetime.datetime.utcnow()
    offset = datetime.timedelta(hours=7)
    gmt7 = gmt0 + offset
    return gmt7


def nextTime(time, gmt=datetime.datetime.now()):
    nextDay = datetime.timedelta(days=1)

    _gmt = gmt + nextDay
    _gmt = _gmt.replace(hour=time[0], minute=time[1], second=0, microsecond=0)
    different = _gmt - gmt
    # print('Next Time : ', _gmt)
    # print('Cur time : ', gmt)
    # print('Diff : ', different)
    countdown(different.seconds)


if __name__ == "__main__":
    print('Script Auto Login ..')
    print('')
    while True:
        date = getGMT7()
        timeTup = date.timetuple()
        curDate = time.strftime(
            " %H:%M:%S %a, %d/%m/%Y", timeTup)
        day = time.strftime('%a', timeTup)

        print(f'Hari ini : {curDate}')
        path = os.path.join(os.path.abspath('.'), 'data.json')
        dataDict = json.load(open(path))

        if dataDict['libur'].__contains__(day):
            print('Hari ini libur,')
            nextTime(dataDict['time'], date)
            continue

        if dataDict['lastLogin'] != '':
            lastDate = datetime.datetime.fromisoformat(dataDict['lastLogin'])
            if lastDate <= curDate:
                print('Hari ini sudah Login')
                nextTime(dataDict['time'], date)

        print('Mencoba Login ..')
        data = payload(dataDict['payload'])
        date = time.localtime()[:3]
        data['entry.1587417115_year'], data['entry.1587417115_month'], data['entry.1587417115_day'] = date

        login, url = req(dataDict['url'], data)
        if login:
            print('Login Berhasil !')
            dataDict['lastLogin'] = getGMT7().isoformat()
            json.dump(dataDict, open(path, 'w'))
            nextTime(dataDict['time'], date)
        else:
            print('Login Gagal :')
            print('Full URL : ' + url)
            time.sleep(3600)
