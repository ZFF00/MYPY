def subprocess_popen(command, work_dir = None, se_PIPE = True, so_PIPE = True):
    # 执行系统命令
    import os
    import re
    import subprocess
    code = 'gbk' if os.name == 'nt' else 'utf-8'
    so = subprocess.PIPE if so_PIPE else None   # 指定标准输出到哪
    se = subprocess.PIPE if se_PIPE else None   # 指定标准错误输出到哪
    p = subprocess.Popen(command, shell=True, stdout=so,stderr=se, cwd = work_dir)
    data , error = p.communicate()    # communicate()等待子进程结束，从stdout和stderr读数据返回元组
    data, error = ('' if i is None else i.decode(code) for i in (data, error))
    result = re.split(r'[\r\n]+', data.strip('\r\n'))
    error_info = re.split(r'[\r\n]+', error.strip('\r\n'))
    return result, error_info, p.returncode

def set_style(words, style):
    '''
    style = [显示方式, 前景色, 背景色]
    颜色默认设置为0或空

    前景色 背景色 颜色
    ---------------------------------------
    30  40  黑色
    31  41  红色
    32  42  绿色
    33  43  黃色
    34  44  蓝色
    35  45  洋红
    36  46  青色
    37  47  白色

    显示方式    意义
    ---------------------------------------
    0   终端默认设置
    1   高亮显示
    22  非高亮显示
    4   使用下划线
    24  去下划线
    5   闪烁
    25  去闪烁
    7   反白显示
    27  非反显
    8   不可见
    28  可见
    '''
    # display = [0, 1, 4, 5, 7, 8, 22, 24, 25, 27, 28]
    # Fcolor = list(range(30, 38))
    # Bcolor = list(range(40, 48))

    try:
        if len(style) != 3:
            raise Exception('样式格式应为：[显示方式, 前景色, 背景色]')
        # style = tuple(style)
    except:
        raise Exception('样式格式应为：[显示方式, 前景色, 背景色]')

    style = [str(i) if i else '' for i in style]
    style = ';'.join(style).strip(';')
    words = '\033[%sm%s\033[0m'%(style, words)
    return words

def log(info: 'Exception|str|int|list', file: str = None, prompt: str = 'i', exit_code: int = 1, color: str = None):
    # 输出提示信息（info）
    # 1:输出到日志（file）
    # 2:输出到屏幕
    # 3:输出到日志和屏幕
    # exit_code不为0时，输出信息后，退出程序
    import sys

    info_list = []
    if isinstance(info, Exception):
        info_list = list(info.args)
    if type(info) in (str, int):
        info_list = [str(info)] if info else []
    elif type(info) == list:
        info_list = [i.rstrip("\r\n") if type(i) is str else str(i) for i in info if i]

    if not info_list:
        return
    # style
    # type
    prompt_info = {
        'i' : ['', [0,0,0]],
        'e' : ['[ERROR] ', [1,31,0]],
        'w' : ['[WARNING] ', [1,33,0]],
        'c' : ['[Completed] ', [1,32,0]],
        'f' : ['[Failure] ', [1,31,0]]
    }

    # 生成颜色对应的code字典
    colors = ['black', 'red', 'green','yellow', 'blue', 'magenta', 'cyan', 'white']
    color_code = range(30,38)
    color_dict = dict(zip(colors,color_code))
    # print(color_dict)
    for i in colors:
        # 原词及首字母大写原词
        color_dict[i.upper()] = color_dict[i]
        color_dict[i[0].upper() + i[:]] = color_dict[i]
        if i[0] not in color_dict:
            k = ''
        else:
            k = 2
            while i[0] + str(k) in color_dict:
                k += 1
        # 首字母大小写加序号
        color_dict[i[0] + str(k)] = color_dict[i]
        color_dict[i[0].upper() + str(k)] = color_dict[i]

    # 在info前面加上提示prompt
    if prompt not in prompt_info:
        prompt_info[prompt] = [prompt + ' ', [1, 0, 0]]
    for k, v in list(prompt_info.items())[1:]:
        if v[0] in info_list[0]:
            p = ''
            break
    else:
        p = prompt_info[prompt][0]
    info_list = [p + i for i in info_list if i]
    write_info = "\n".join(info_list)

    # 设置打印的style
    style = prompt_info[prompt][1][:]
    if color in color_dict:
        style[0] = 1  # 一旦设置颜色就高亮显示
        style[1] = color_dict[color]
    print_info = '\n'.join([set_style(i, style) for i in info_list])

    if prompt in ('e', 'w', 'f'):
        out = sys.stderr
    else:
        out = sys.stdout

    if file:
        with open(file, 'a') as f:
            f.write(write_info + "\n")
    else:
        print(print_info, file = out)
    
    # 大多数情况下如果prompt为e，程序会退出，个别情况不想退出的话可以指定exit_code为0
    # 可以使用指定的错误代码退出
    if prompt == 'e' and exit_code != 0:
        exit(exit_code)
        

def file_type(file):
    #返回文件类型
    return file.rsplit(".",1)[-1]

def file_check(file, ftype = None):
    #检查文件是否合法
    # -1:文件不存在；0:文件不合法；1:文件存在、合法
    import os
    if ftype:
        if os.path.isfile(file):
            if type(ftype) == str:
                if file_type(file) == ftype:
                    return 1
                else:
                    return 0
            elif type(ftype) == tuple:
                if file_type(file) in ftype:
                    return 1
                else:
                    return 0
        else:
            return -1
    else:
        if os.path.isfile(file):
            return 1
        else:
            return -1

def dir_check(Dir):
    import os
    return os.path.isdir(Dir)


def db_check(db, dbtype):
    # 检查数据库
    # 0:数据库不存在或不合法
    # 1:数据库合法
    import os
    if db[-1] == "/":  # 不能是一个目录
        return 0
    else:
        if dbtype == "prot":
            dbs = ("pin", "phr", "psq")
        elif dbtype == "nucl":
            dbs = ("nin", "nhr", "nsq")
        db_dir = os.path.dirname(db)
        db_title = os.path.split(db)[1]
        if dir_check(db_dir):
            files = os.listdir(db_dir)
            flag = 0
            for file in files:
                # file0 = os.path.join(db_dir, file)
                # if file_check(file0) == 1:
                if db_title in file.rsplit(".", 1)[0] and file_type(file) in dbs:
                    # if file.rsplit(".",1)[0] == db_title and file_type(file) in dbs:
                    flag += 1
            if flag >= 3:
                return 1
            else:
                return 0
        else:
            return 0

def zip_file(filedir, new_file):
    import os
    import zipfile
    z = zipfile.ZipFile(new_file,'w',zipfile.ZIP_DEFLATED) #参数一：文件夹名
    for dirpath, dirnames, filenames in os.walk(filedir):
        fpath = dirpath.replace(filedir,'')     #这一句很重要，不replace的话，就从根目录开始复制
        fpath = fpath and fpath + os.sep or ''  #实现当前文件夹以及包含的所有文件的压缩
        for filename in filenames:
            z.write(os.path.join(dirpath, filename),fpath+filename)
    z.close()

def unzip_file(file, new_dir):
    import zipfile
    zip_file = zipfile.ZipFile(file)
    zip_file.extractall(new_dir)  # 解压全部
    zip_file.close()

def read_fasta(file):
    # 生成器， 每次返回一条fasta序列的字典
    fasta = {}
    seq = []
    with open(file, newline='') as f:  # newline 不把\r\n自动转换为\n
        while True:
            line = f.readline()
            if (line.startswith('>') or not line) and seq:
                fasta['id'] = id
                fasta['description'] = description  # 描述
                fasta['title'] = title  # 标题长度
                fasta['seq'] = ''.join(seq)  # 序列
                fasta['length'] = len(fasta['seq'])  # 序列长度
                fasta['line_base'] = len(seq[0])  # 每行碱基数
                fasta['line_end'] = line_end  # 换行符字符数
                yield fasta
            if line.startswith('>'):
                title = line.strip('>\r\n')
                title_list = title.split(' ', 1)
                id = title_list[0]
                description = '' if len(title_list) == 1 else title_list[1]
                seq = []
            else:
                line_end = 2 if line.endswith('\r\n') else 1
                seq.append(line.strip(' \r\n'))
            if not line:
                break
    return fasta

