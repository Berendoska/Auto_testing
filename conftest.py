import pytest
from check import checkout, getout
import random, string
import yaml
from datetime import datetime

with open('config.yaml') as f:
    # читаем документ YAML
    data = yaml.safe_load(f)

@pytest.fixture()
def make_folders():
    return checkout("mkdir {} {} {} {}".format(data["folder_in"], data["folder_in"], data["folder_ext"], data["folder_ext2"]), "")

@pytest.fixture()
def clear_folders():
    return checkout("rm -rf {}/* {}/* {}/* {}/*".format(data["folder_in"], data["folder_in"], data["folder_ext"], data["folder_ext2"]), "")
@pytest.fixture()
def make_files():
    list_of_files = []
    for i in range(data["count"]):
        filename = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        if checkout("cd {}; dd if=/dev/urandom of={} bs={} count=1 iflag=fullblock".format(data["folder_in"], filename, data["bs"]), ""):
            list_of_files.append(filename)
    return list_of_files

@pytest.fixture()
def make_subfolder():
    testfilename = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    subfoldername = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    if not checkout("cd {}; mkdir {}".format(data["folder_in"], subfoldername), ""):
        return None, None
    if not checkout("cd {}/{}; dd if=/dev/urandom of={} bs=1M count=1 iflag=fullblock".format(data["folder_in"], subfoldername, testfilename), ""):
        return subfoldername, None
    else:
        return subfoldername, testfilename

@pytest.fixture(autouse=True)
def print_time():
    print("Start: {}".format(datetime.now().strftime("%H:%M:%S.%f")))
    yield
    print("Finish: {}".format(datetime.now().strftime("%H:%M:%S.%f")))

@pytest.fixture()
def create_bad_archive():
    checkout(f'cd {data["folder_in"]}; 7z a -t{data["arc_type"]} {data["folder_out"]}/arx2', "Everything is Ok")
    checkout(f'cp {data["folder_out"]}/arx2.{data["arc_type"]} {data["folder_bad"]}', '')
    checkout(f'truncate -s 1 {data["folder_bad"]}/arx2.{data["arc_type"]}', '')  # сделали битым



@pytest.fixture(autouse=True)
def stat_fixture():
    pass
    yield
    time_stamp = datetime.now().strftime("%H:%M:%S.%f")
    files_count = data["count"]
    file_size = data["bs"]
    cpu_stat = getout("cat /proc/loadavg")
    checkout(f'cd {data["stat_file_dir"]}; echo "time = {time_stamp}, files_count = {files_count}, file_size = {file_size}, cpu_stat = {cpu_stat}" >> stat.txt','')
