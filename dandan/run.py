import csv
import sys
import time
import json
import random
from match import Match

table = []
keys = []

WEIGHT_JSON = 'weight.json'
MAX_DIFF_JSON = 'max_diff.json'


def save_result(matched_data):
    file_name = time.strftime("%Y%m%d-%H%M%S", time.localtime()) + '.csv'
    with open(file_name, 'w', newline='') as f_csv:
        writer = csv.writer(f_csv, dialect='excel')
        writer.writerow(keys)
        for item in matched_data:
            writer.writerow(item)


def get_matched_data(matched_list, raw_data):
    matched_table = []
    for item in matched_list:
        for line in raw_data:
            if item[0] == line['ID'] or item[1] == line['ID']:
                new_line = []
                for key in keys:
                    new_line.append(line[key])
                matched_table.append(new_line)
        matched_table.append([''])
    return matched_table


def load_json(file_name):
    with open(file_name) as f_json:
        j_obj = json.load(f_json)
    return j_obj


def load_raw_data(file_name):
    with open(file_name) as f:
        f_csv = csv.reader(f)
        first_line = True
        raw_data = []
        for row in f_csv:
            if first_line:
                first_line = False

                # 保存列名
                global keys
                keys = row[0].upper().split('\t')
            else:
                item = {}
                value = row[0].upper().split('\t')
                num_data = len(value)
                i = 0
                while i < num_data:
                    item[keys[i]] = value[i]
                    i += 1

                # 一条数据匹配一次
                item['matched'] = False
                raw_data.append(item)

        return raw_data


if __name__ == "__main__":
    if len(sys.argv) > 1:
        raw_data_file = sys.argv[1]
    else:
        raw_data_file = 'abc.csv'

    # load data
    raw_data = load_raw_data(raw_data_file)

    # 打乱列表顺序
    random.shuffle(raw_data)

    weight = load_json(WEIGHT_JSON)
    max_diff = load_json(MAX_DIFF_JSON)

    # 匹配数据
    match = Match(raw_data, weight, max_diff)
    match.match_all()
    matched_list = match.get_matched_list()
    matched_table = get_matched_data(matched_list, raw_data)

    # 保存数据
    save_result(matched_table)
