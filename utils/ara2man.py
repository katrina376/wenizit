import re

digit = {
    'one': lambda x: ones[x],
    'ten': lambda x: tens[x] if x in tens else ones[x] + '十',
    'hundred': lambda x: hundreds[x]
}

ones = {
    '0' : '零',
    '1' : '一',
    '2' : '二',
    '3' : '三',
    '4' : '四',
    '5' : '五',
    '6' : '六',
    '7' : '七',
    '8' : '八',
    '9' : '九',
}

tens = {
    '0': '零',
    '2': '廿',
    '3': '卅',
}

hundreds = {
    '1': '一百'
}

def ara2man(ara):
    '''
    Convert Hindu-Arabic numerals into Mandarin
    '''
    
    man = ''

    if ara == '':
        return '.*'

    if len(ara) == 1:
        man = digit['one'](ara[0])
    elif len(ara) == 2:
        man = digit['ten'](ara[0]) + digit['one'](ara[1])
    elif len(ara) == 3:
        man = digit['hundred'](ara[0]) + digit['ten'](ara[1]) + digit['one'](ara[2])

    if man[-1] == '零':
        man = man[:-1]

    if man[0] == '一' and len(ara) == 2:
        man = man[1:]

    return man
