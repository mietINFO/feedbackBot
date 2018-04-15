# -*- coding: utf-8 -*-

def headline_wrapper(headline):
    """
    Формируем и возвращаем обработанный заголовок сообщения
    """
    return '<b>' + headline + '</b>\r\n\r\n'


def message_wrapper(message):
    """
    Формируем и возвращаем готовое сообщение
    """
    if "headline" in message:
        return headline_wrapper(str(message["headline"])) + str(message["text"])
    else:
        return message["text"]