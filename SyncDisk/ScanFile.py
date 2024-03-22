import os
import datetime

import CalcHash


def scan_file(file_path, no_sync):

    text_all = ''

    for root, dirs, files in os.walk(file_path):
        for file in files:

            flag = False
            full_path = os.path.join(root, file)

            for word in no_sync:
                if word in full_path:
                    flag = True
            if flag:
                continue

            file_stat = os.stat(full_path)
            file_modified_time = datetime.datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y%m%d%H%M%S')

            relative_path = full_path.replace(file_path, "\\root")
            text_current = f'{relative_path}@{file_stat.st_size}@{file_modified_time}#{CalcHash.calc_hash(full_path)}\n'
            text_all += text_current

    return text_all
