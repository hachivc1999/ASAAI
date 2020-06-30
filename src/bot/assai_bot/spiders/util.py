from urllib.parse import urljoin
import os


def create_project_dir(file_dir):
    if not os.path.exists(file_dir):
        print("Creating project's directory: " + file_dir)
        os.makedirs(file_dir)


def create_data_file(file):
    if not os.path.isfile(file):
        write_file(file, '')


def write_file(path, data):
    f = open(path, 'w')
    f.write(data)
    f.close()


def append_to_file(path, data):
    with open(path, 'a') as file:
        file.write(data + '\n')


def delete_file_contents(path):
    with open(path, 'w') as file:
        pass


def file_to_set(file_name):
    results = set()
    with open(file_name, 'rt') as f:
        for line in f:
            results.add(line.replace('\n', ''))
    return results


def set_to_file(links, file):
    delete_file_contents(file)
    for link in sorted(links):
        append_to_file(file, link)






