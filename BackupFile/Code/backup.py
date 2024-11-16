
import os
import sys
import json
import time
import shutil
import hashlib
import argparse
import platform


# 获取文件的类型
def get_file_type(file_name):
    _, ext = os.path.splitext(file_name)

    if file_name.startswith('.') and not ext or not ext:
        return "UNKNOWN"

    return ext.lstrip('.').lower()


# 计算文件哈希值
def get_hash_kay(file_path, hash_algorithm='sha256'):
    hash_func = hashlib.new(hash_algorithm)

    with open(file_path, 'rb') as file:
        while chunk := file.read(8192):
            hash_func.update(chunk)

    return hash_func.hexdigest()


def option():

    parser = argparse.ArgumentParser(description='Hi, Here is SeeChen Backup.')

    # 配置基础设置
    parser.add_argument('--set', required=False, help='Set the backup source path and target path.', action='store_true')
    parser.add_argument('-source', required=False, type=str, help='File Path you want to backup.')
    parser.add_argument('-target', required=False, type=str, help='The path to which the files are backed up')

    parser.add_argument('--init', required=False, help='Start the first backup.', action='store_true')

    return parser


# 进行基础配置
def config(path_source, path_target):

    confirm_source = input(f'Please confirm your Source Path: "{path_source}":[y / n]')
    if confirm_source not in ['y', 'Y']:
        sys.exit()

    # 判断给定的源文件路径是否存在
    if not os.path.exists(path_source):
        print(f'"{path_source}" does not exist. Please make sure the path is correct and absolute.')
        sys.exit()

    confirm_target = input(f'Please confirm your Target Path: "{path_target}":[y / n]')
    if confirm_target not in ['y', 'Y']:
        sys.exit()

    # 判断给定的目标路径是否存在
    if not os.path.exists(path_target):
        confirm_create = input(f'"{path_target}" does not exist. Do you want to create it?:[y / n]')
        if confirm_target not in ['y', 'Y']:
            sys.exit()

        # 创建相关文件夹
        os.mkdir(path_target)
        path_target = os.path.abspath(path_target)
        print(f'The target is create on {path_target}')

    # # 创建记录文件夹
    os.makedirs(os.path.join(path_target, '.tree'), exist_ok=True)     # 用于保存文件树结构
    os.makedirs(os.path.join(path_target, '.log'), exist_ok=True)      # 用于保存日志文件
    os.makedirs(os.path.join(path_target, '.file'), exist_ok=True)     # 用于保存真实文件
    os.makedirs(os.path.join(path_target, '.mapping'), exist_ok=True)  # 用于记录文件与哈希值的映射

    # 创建一个记录基础信息的文件
    with open(os.path.join(path_target, 'SeeChen-Backup.json'), 'w') as file:

        backup_record = {
            "source": path_source,
            "target": path_target,
            "skip": "",
            "INIT": False
        }

        json.dump(backup_record, file, indent=4, ensure_ascii=False)
        pass
    pass


# 获得文件树
def get_tree(path_root):

    # 记录格式
    file_tree = {
        "name": path_root,
        "type": "FOLDER",
        "hash-value": "",
        "timestamp": int(round(time.time() * 1000)),
        "size": 0,
        "DELETE": {
            "status": False,
            "at": None
        },
        "children": []
    }

    # 临时映射文件
    mapping = {}

    # 哈希 : [文件] 映射文件
    mapping_hash_file = {}

    for root, dirs, files in os.walk(path_root):

        relative_path = os.path.relpath(root, path_root)
        parent = file_tree

        if relative_path != ".":
            for part in relative_path.split(os.sep):
                for child in parent['children']:
                    if child['name'] == part:
                        parent = child
                        break

        parent['children'].extend([{
            "name": d,
            "type": "FOLDER",
            "hash-value": "",
            "timestamp": int(round(time.time() * 1000)),
            "size": 0,
            "DELETE": {
                "status": False,
                "at": None
            },
            "children": []
        } for d in dirs])

        list_file_info = []
        for f in files:
            file_path = os.path.join(root, f)
            file_type = get_file_type(f)
            file_hash = get_hash_kay(file_path)
            file_size = os.path.getsize(file_path)

            rel_path = os.path.join('root\\', os.path.relpath(file_path, path_root))
            if file_type not in mapping:
                _temp = {
                    file_type: {
                        file_hash: file_path
                    }
                }
                _temp_hash_file = {
                    file_type: {
                        file_hash: [rel_path]
                    }
                }

                mapping.update(**_temp)
                mapping_hash_file.update(**_temp_hash_file)
            elif file_hash not in mapping[file_type]:
                mapping[file_type][file_hash] = file_path
                mapping_hash_file[file_type][file_hash] = [rel_path]

            elif file_hash in mapping[file_type]:
                mapping_hash_file[file_type][file_hash].append(rel_path)

            file_info = {
                "name": f,
                "type": file_type,
                "hash-value": file_hash,
                "timestamp": int(round(time.time() * 1000)),
                "size": file_size,
                "DELETE": {
                    "status": False,
                    "at": None
                },
                "children": []
            }

            list_file_info.append(file_info)

        parent['children'].extend(list_file_info)

    return file_tree, mapping, mapping_hash_file


# 复制文件
def copy_file(path_target, mapping):

    system = platform.system()

    for file_type in mapping:
        for hash_key in mapping[file_type]:
            list_sub_dir = [hash_key[i:i + 4] for i in range(0, len(hash_key), 4)]
            sub_dir = '\\'.join(list_sub_dir[:-1])
            target_dir = os.path.join(path_target, f'.file\\{file_type}', sub_dir)
            target_path = os.path.join(target_dir, f'{list_sub_dir[-1]}.{file_type}')

            os.makedirs(target_dir, exist_ok=True)
            shutil.copy2(mapping[file_type][hash_key], target_path)
            print(f'Copy {target_path} -> {mapping[file_type][hash_key]}')

    # Windows 平台
    if system == 'Windows':
        pass

    # Linux 平台
    if system == 'Linux':
        import xattr

    # No macOS Platform because I don't have MacBook.
    if system == 'Darwin':
        pass

    pass


# 初始化
def init_backup():

    # 读取记录文件
    with open('../Test/Target/SeeChen-Backup.json', 'r') as file:
        backup_data = json.load(file)
        file.close()

    init_tree, init_mapping, init_mapping_hash_file = get_tree(backup_data['source'])
    # copy_file(backup_data['target'], init_mapping)
    #
    # # 写入 Mapping 数据
    # with open(os.path.join(backup_data['target'], '.mapping', 'hash2file.json'), 'w', encoding='UTF-8') as file_mapping:
    #     json.dump(init_mapping_hash_file, file_mapping, ensure_ascii=False, indent=4)
    #     file_mapping.close()
    #
    # # 写入当前文件树
    # with open(os.path.join(backup_data['target'], '.tree', f'{int(round(time.time() * 1000))}.json'), 'w', encoding='UTF-8') as file_tree:
    #     json.dump(init_tree, file_tree, ensure_ascii=False, indent=4)
    #     file_tree.close()
    #
    # # 更新数据
    # with open(os.path.join(backup_data['target'], 'SeeChen-Backup.json'), 'w') as file_backup_main:
    #     backup_data['INIT'] = True
    #     json.dump(backup_data, file_backup_main, ensure_ascii=False, indent=4)
    #     file_backup_main.close()

    pass


if __name__ == '__main__':

    option_parser = option()
    args = option_parser.parse_args()

    if args.set:
        if args.source and args.target:
            config(args.source, args.target)

        else:
            print(f'"{"source" if not args.source else "target"}" path is required in --set optional.')
            sys.exit()

    if args.init:
        init_backup()

