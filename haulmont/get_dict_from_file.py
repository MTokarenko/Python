path_to_csv='C:/users.txt'
users_dic = dict()
def abc():
    f = open(path_to_csv)
    for lino, line in enumerate(f):
        if lino != 0:
            line = line.split(';')
            test_list = []
            for index, word in enumerate(line):
                test_list.append(word.strip())
            users_dic[test_list[0]] = test_list
    f.close()
    return users_dic

a = abc()
print(a)
