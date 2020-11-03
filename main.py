from urllib import request, parse
import time
import re
import json
import os
import datetime
import logging
import traceback
import threading

import teleBot
import db
import var

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

process = []


def payload(payload):
    dataDict = {}
    pairData = str(payload).split('&')
    for _data in pairData:
        _data = _data.split('=')
        dataDict[_data[0]] = _data[1]
    return dataDict


def req(url, payload):
    dataReq = ''
    for param in payload:
        dataReq += f'&{param}={payload[param]}'
    fullUrl = f'{url}?{dataReq}'
    while True:
        try:
            logger.debug(fullUrl)
            res = request.urlopen(fullUrl)
            time.sleep(1)
            content = str(res.read())
            if re.search('Kirim tanggapan lain', content):
                return (True, '')
            return (False, content)
        except Exception as e:
            logger.error('Error Saat menghubungi Server')
            logger.error('Error : ', exc_info=e.__str__())
            logger.warn('Mencoba kembali dalam 5 detik ', end='', flush=True)


def getGMT7():
    gmt0 = datetime.datetime.utcnow()
    offset = datetime.timedelta(hours=7)
    gmt7 = gmt0 + offset
    return gmt7


def pauseUntil(time, gmt, long):
    # print(day)
    nextDay = datetime.timedelta(days=long)

    _gmt = gmt + nextDay
    _gmt = _gmt.replace(hour=time[0], minute=time[1], second=0, microsecond=0)
    return _gmt


def nextTime(time, gmt):
    nextDay = datetime.timedelta(days=1)

    _gmt = gmt + nextDay
    _gmt = _gmt.replace(hour=time[0], minute=time[1], second=0, microsecond=0)
    return _gmt.isoformat()


def updatePayload(payload: dict, gmt: datetime.datetime):
    year = gmt.year
    month = gmt.month
    day = gmt.day

    for key in payload:
        if re.search('_year', key):
            payload[key] = year
        elif re.search('_month', key):
            payload[key] = month
        elif re.search('_day', key):
            payload[key] = day

    return payload


def workerMain(id):
    logger.info(msg="Working for user " + id.__str__())
    process.append(id)
    date = getGMT7()
    curDate = date.strftime(
        " %H:%M:%S %a, %d/%m/%Y")
    day = date.strftime(
        "%a")

    data = db.getData(id)
    time = [int(x) for x in data['waktu'].split('.')]
    libur = data['libur'].split(',')

    bot.sendMsg(data['chatId'], var.temMsg['log'])
    bot.sendMsg(data['chatId'], f'Hari ini : {curDate}')

    logger.debug(data)
    if data['pause'] != '' and data['pause'] != None:
        skip = datetime.datetime.fromisoformat(data['pause'])
        if skip >= date:
            skipStr = skip.strftime('%H:%M:%S %a, %d/%m/%Y')
            bot.sendMsg(data['chatId'], 'Skip Sampai %s' % skipStr)
            trig = nextTime(time, date)

            db.addConfig(id, 'trigger', trig)
            return
        else:
            db.addConfig(id, 'trigger', '')

    if libur.__contains__(day):
        bot.sendMsg(data['chatId'], 'Hari ini libur,')
        trig = nextTime(time, date)
        db.addConfig(id, 'trigger', trig)
        return

    bot.sendMsg(data['chatId'], 'Mencoba Absen ..')
    reqData = payload(data['payload'])
    reqData = updatePayload(reqData, date)

    login, url = req(data['url'], reqData)
    if login:
        bot.sendMsg(data['chatId'], 'Absen Berhasil !')
        trig = nextTime(time, date)
        db.addConfig(id, 'trigger', trig)
    else:
        bot.sendMsg(data['chatId'], 'Absen Gagal :')
        bot.sendMsg(data['chatId'], 'Full URL : ' + url)
        bot.sendMsg(data['chatId'], 'Layanan dihentikan !')
        db.addConfig(id, 'trigger', '')
    process.remove(id)


def workerPause(id, long: int):
    date = getGMT7()
    data = db.getData(id)
    time = [int(x) for x in data['waktu']]
    pause = pauseUntil(time, date, long)
    pauseIsoFormat = pause.isoformat()

    pauseStr = pause.strftime(
        " %H:%M:%S %a, %d/%m/%Y")
    db.addConfig(id, 'pause', pauseIsoFormat)
    bot.sendMsg(data['chatId'], 'Skip Sampai ' + pauseStr)


def workerLoop():
    """
    docstring
    """
    while True:
        date = getGMT7()
        triggers = db.checkTrig()

        for trigger in triggers:
            trigDate = datetime.datetime.fromisoformat(trigger)
            if trigDate <= date and not process.__contains__(triggers[trigger]):
                # print('here : ', triggers[trigger])
                threading.Thread(
                    target=workerMain, args=[triggers[trigger]]).start()
        time.sleep(3)


if __name__ == "__main__":
    threading.Thread(target=workerLoop).start()
    # threading.Thread(target=workerThread).start()
    bot = teleBot.TeleBot(
        '1047213602:AAG_J7z8vV-TSzObzKiRhHQEBVUSA3Uc3Gw', workerMain, workerPause)

    bot.run()
