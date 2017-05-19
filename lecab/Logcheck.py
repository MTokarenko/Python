#!/usr/bin/env python

import gzip

path_web = raw_input('Enter the web directory -->')
file_name = raw_input('Enter file name --> ')
dir_name = file_name.lstrip('sherbook.log.').rstrip('.gz')
path = file_name + '_result.txt'
dir = '/home/voxtur/files/log_archive/'
path_to_log = dir + path_web + '/' + dir_name + '/' + file_name
print(path_to_log)

dic = dict()
id = str()

try:
    f = gzip.open(path_to_log, "r", "utf-8")
    for line in f:
        if 'TRACE' in line:
            id = line[31:63]
            time = line[0:23]
            if '[received] /calculate/price' in line:
                if '"promoCode":"MiniCabTest"' in line:
                    if id not in dic.keys():
                        dic[id] = ['sent', 0, time]
                    else:
                        dic[id][0] = 'sent'
            elif '[received] /calculate/prebookLimit' in line:
                if id in dic.keys():
                    if dic[id][0] == 'sent':
                        dic[id][0] = 'rec'
            elif '[sent] /calculate/prebookLimit' in line:
                if id in dic.keys():
                    if '"status":"FULLY_BOOKED"' in line:
                        if dic[id][0] == 'rec':
                            dic[id][0] = 'FULLY!'
                            dic[id][1] += 1
                            dic[id][2] = time
                    else:
                        dic[id][0] = 'closed'
finally:
    f.close()
total = 0
with open(path, 'w') as fh:
    for item in dic.items():
        if item[1][1] > 0:
            total += int(item[1][1])
            fh.write('{0}. {1} - {2}\n'.format(item[1][2], item[0], item[1][1]))
    print('Total - ' + str(total))
