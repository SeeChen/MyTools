import hashlib


def calc_hash(path_file, method='sha256'):

    hasher = hashlib.new(method)

    with open(path_file, mode='rb') as file:

        while True:

            chunk = file.read()
            if not chunk:
                break

            hasher.update(chunk)

    return hasher.hexdigest()
