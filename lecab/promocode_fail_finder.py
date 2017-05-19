#!/usr/bin/env python

import gzip


dir = '/home/voxtur/files/log_archive/'
checker = True
#path_to_log = 'new_44.txt'
dic = dict()
id = str()

while checker:
    try:
        path_web = raw_input('Enter the web directory -->')
        file_name = raw_input('Enter file name --> ')
        dir_name = file_name.lstrip('sherbook.log.').rstrip('.gz')
        path_to_log = dir + path_web + '/' + dir_name + '/' + file_name
        f = gzip.open(path_to_log, "r", "utf-8")
        #f = open(path_to_log, "r")
        fh = open(path_to_log + '_result.csv', 'w')
        for line in f:
            id = line[31:63]
            time = line[0:23]
            if '[received] /calculate/price' in line:
                if '"promoCode":"MiniCabTest"' in line:
                    dic[id] = ['sent', time]
            elif '[send] /calculate/price' in line:
                if id in dic.keys():
                    if dic[id][0] == 'sent':
                        if '"appliedDiscounts":[{"promoCode":null' in line:
                            fh.write('{0}  {1}'.format(time, id))
                            dic[id][0] = 'rec'
                        else:
                            dic[id][0] = 'rec'
        if f:
            f.close()
        elif fh:
            fh.close()
        checker = False
    except IOError as err:
        print 'Oops, something wrong! \n{0}'.format(err)
        checker = False
    except (ValueError):
        print 'Oops, something wrong!'
        if f:
            f.close()
        elif fh:
            fh.close()
        checker = False
