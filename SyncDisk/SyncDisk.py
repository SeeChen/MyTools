import os
import json
import shutil

import CalcHash
import ScanFile

if __name__ == '__main__':

    # 读取配置文件
    with open("Property.json", encoding='UTF-8') as property_file:

        property_json = json.load(property_file)
        property_file.close()

    path_root = property_json['ROOT']
    path_sync = property_json['SYNC']

    # 判断程序是否是第一次打开
    sync_system_folder = path_root + '\\.sync'

    sync_source_folder = sync_system_folder + "\\source"
    sync_target_folder = sync_system_folder + "\\target"

    path_status_source = f"{sync_source_folder}\\status.json"
    path_status_target = f"{sync_target_folder}\\status.json"
    if not os.path.exists(sync_system_folder):

        # 不存在，创建文件夹
        os.makedirs(sync_system_folder, exist_ok=False)

        os.makedirs(sync_source_folder, exist_ok=False)
        os.makedirs(sync_target_folder, exist_ok=False)

        # 初始化文件夹内容
        with (open(path_status_source, mode='w', encoding='UTF-8') as source_status_file,
              open(path_status_target, mode='w', encoding='UTF-8') as target_status_file):

            property_hash = CalcHash.calc_hash('Property.json')
            source_status_list = [{"FILE": "Property.json", "HASH": property_hash}]
            target_status_list = [{"FILE": "Property.json", "HASH": property_hash}]

            for single_file in path_sync:
                source_file_name = str(single_file['SOURCE']).replace(':\\', '-').replace('\\', '-') + '.txt'
                target_file_name = str(single_file['TARGET']).replace(':\\', '-').replace('\\', '-') + '.txt'

                source_file_full_path = f"{sync_source_folder}\\{source_file_name}"
                target_file_full_path = f"{sync_target_folder}\\{target_file_name}"

                with (open(source_file_full_path, mode='w', encoding='UTF-8') as f1,
                      open(target_file_full_path, mode='w', encoding='UTF-8') as f2):
                    f1.write(ScanFile.scan_file(single_file['SOURCE'], single_file['NO_SYNC']))
                    f2.write(ScanFile.scan_file(single_file['TARGET'], single_file['NO_SYNC']))

                    f1.close()
                    f2.close()

                source_status_list.append({"FILE": f"{single_file['SOURCE']}",
                                           "HASH": f"{CalcHash.calc_hash(source_file_full_path)}"})
                target_status_list.append({"FILE": f"{single_file['TARGET']}",
                                           "HASH": f"{CalcHash.calc_hash(target_file_full_path)}"})

            json.dump(source_status_list, source_status_file, indent=4)
            json.dump(target_status_list, target_status_file, indent=4)

    new_status_source = []

    # 不是第一次打开或初始化之后
    sync_list = property_json['SYNC']
    with (open(path_status_source, mode='r+', encoding='UTF-8') as file_source):

        status_source = json.load(file_source)
        status_source_new = [status_source[0]]

        for sync_folder in sync_list:
            sync_source, sync_target, no_sync = sync_folder['SOURCE'], sync_folder['TARGET'], sync_folder['NO_SYNC']
            source_record_file = str(sync_source_folder) + "\\" + str(sync_source).replace(":\\", '-').replace("\\", '-') + ".txt"

            with open(source_record_file, mode='w', encoding='UTF-8') as f:

                f.write(ScanFile.scan_file(sync_source, no_sync))
                f.close()

            status_source_new.append({"FILE": f"{sync_source}",
                                      "HASH": f"{CalcHash.calc_hash(source_record_file)}"})

        new_status_source = status_source_new

        file_source.seek(0)
        file_source.truncate()

        json.dump(status_source_new, file_source, indent=4)
        file_source.close()

    with open(path_status_target, mode='r+', encoding='UTF-8') as file_target:

        status_target = json.load(file_target)
        status_target_new = [status_target[0]]

        for sync_folder in sync_list:
            sync_source, sync_target, no_sync = sync_folder['SOURCE'], sync_folder['TARGET'], sync_folder['NO_SYNC']
            source_record_file = str(sync_source_folder) + "\\" + str(sync_source).replace(":\\", '-').replace("\\", '-') + ".txt"
            target_record_file = str(sync_target_folder) + "\\" + str(sync_target).replace(":\\", '-').replace("\\", '-') + ".txt"

            flag = False
            for source_item, target_item in zip(new_status_source, status_target):
                if source_item['FILE'] == sync_source and target_item['FILE'] == sync_target:
                    if source_item['HASH'] == target_item['HASH']:
                        flag = True

                        status_target_new.append(target_item)

            if flag:
                continue

            with (open(source_record_file, mode='r', encoding='UTF-8') as file1,
                  open(target_record_file, mode='r', encoding='UTF-8') as file2):

                set_source = set(file1.readlines())
                set_target = set(file2.readlines())

                list_add = set_source - set_target
                list_del = set_target - set_source

                file1.close()
                file2.close()

            for item in list_del:

                file_del = item.split('@')[0].replace('\\root', sync_target)
                os.remove(file_del)

            for item in list_add:

                file_add = item.split('@')[0].replace('\\root', sync_source)
                des_path = os.path.dirname(file_add.replace(sync_source, sync_target))

                os.makedirs(des_path, exist_ok=True)
                shutil.copy2(file_add, des_path)

            with open(target_record_file, 'w', encoding='UTF-8') as file:

                file.write(ScanFile.scan_file(sync_target, no_sync))
                file.close()

            status_target_new.append({'FILE': f'{sync_target}', 'HASH': CalcHash.calc_hash(target_record_file)})

        file_target.seek(0)
        file_target.truncate()
        json.dump(status_target_new, file_target, indent=4)

    for i in path_sync:

        for root, dirs, file in os.walk(i['TARGET'], topdown=False):

            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)

                if not os.listdir(dir_path):

                    os.rmdir(dir_path)
