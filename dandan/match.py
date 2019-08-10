class Match:
    def __init__(self, table, weight, max_diff):
        self.table = table
        self.WEIGHT = weight
        self.MAX_DIFF = max_diff
        self.matched_list = []

    def get_matched_list(self):
        return self.matched_list

    def find_match_item(self, row):
        if row['matched']:
            return -1
        else:
            matched_id = -1
            min_diff_values = -1

            for match_row in self.table:

                # 匹配到原数据时跳过
                if row['ID'] == match_row['ID']:
                    continue

                # 差值最小的数据就是最匹配的那一条
                diff_value = self.diff_value(row, match_row)
                if -1 != diff_value \
                        and (-1 == min_diff_values or diff_value < min_diff_values):
                    min_diff_values = diff_value
                    matched_id = match_row['ID']

            if -1 != min_diff_values:
                return matched_id
            else:
                return -1

    def matched_flag(self, id):
        for row in self.table:
            if id == row['ID']:
                row['matched'] = True

    def match_all(self):
        for row in self.table:
            id = self.find_match_item(row)
            if -1 != id:
                self.matched_list.append([row['ID'], id])
                self.matched_flag(row['ID'])
                self.matched_flag(id)

    def diff_value(self, left, right):
        try:
            diff_value = -1
            for key in self.WEIGHT.keys():
                abs_diff = abs(float(left[key]) - float(right[key]))

                # 单个数据差别太大就放弃
                if abs_diff < self.MAX_DIFF[key]:
                    diff_value += abs_diff * self.WEIGHT[key]
        except ValueError:
            diff_value = -1
            pass

        return diff_value
