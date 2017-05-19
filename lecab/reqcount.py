#!/usr/bin/env python

import gzip


#dir = '/home/voxtur/files/log_archive/'
checker = True
path_to_log = '/home/mikhail/PycharmProjects/haulmont/lecab/new_44.txt'

while checker:
    try:
        #path_web = raw_input('Enter the web directory -->')
        #file_name = raw_input('Enter file name --> ')
        #dir_name = file_name.lstrip('sherbook.log.').rstrip('.gz')
        #path_to_log = dir + path_web + '/' + dir_name + '/' + file_name
        #f = gzip.open(path_to_log, "r", "utf-8")
        f = open(path_to_log, "r")
        fh = open(path_to_log + '_result.csv', 'w')
        for line in f:
            if '[received] /calculate/price' in line:
                if '"promoCode":"MiniCabTest"' in line:
                    id = line[31:63]
                    time = line[0:23]
                    fh.write('{0} - {1}\n'.format(id, time))
        if f is not None:
            f.close()
        elif fh is not None:
            fh.close()
        checker = False
    except (NameError, IOError, ValueError):
        print('Oops, something wrong! \nMake sure that your path ({0}) is correct'.format(path_to_log))
        if f is not None:
            f.close()
        elif fh is not None:
            fh.close()
        checker = False
