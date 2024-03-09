import re
import json

input_string = """
            select
                s.StudentId,
                firstName,
                s.lastName,
                deptName
            from student as s join department as d on s.dept_id = d.id;
                
"""


def extract_select_columns(sql_string):
    match = re.search(r'select\s+(.*?)\s+from', sql_string, re.DOTALL | re.IGNORECASE)
    if not match:
        return []
    selected_columns = match.group(1).strip()
    selected_columns_list = [col.strip() for col in selected_columns.split(',')]
    return selected_columns_list


def join_conditions(sql_string):
    match_join_condition = re.search(r'on\s+(.*?)\s*;', sql_string, re.DOTALL | re.IGNORECASE)
    if match_join_condition:
        join_condition = match_join_condition.group(1).strip()
        return [item.strip() for item in join_condition.split('=')]
    return []


def extract_tables(sql_string):
    main_table_name, main_table_alias, join_table_name, join_table_alias = None, None, None, None
    match_table = re.search(r'from\s+(\w+)\s+as\s+(\w+)\s+join', sql_string, re.IGNORECASE)
    if match_table:
        main_table_name, main_table_alias = match_table.group(1).strip(), match_table.group(2).strip()
    join_table = re.search(r'join\s+(\w+)\s+as\s+(\w+)\s+on', sql_string, re.IGNORECASE)
    if join_table:
        join_table_name, join_table_alias = join_table.group(1).strip(), join_table.group(2).strip()
    return main_table_name, main_table_alias, join_table_name, join_table_alias


def columns_from_alias(alias, columns_list):
    possible_columns = []
    columns = []
    for column in columns_list:
        alias_name = f'{alias}.'
        if column.startswith(alias_name):
            columns.append(column[len(alias_name):])
        elif '.' not in column:
            possible_columns.append(column)
    return columns, possible_columns


def main(sql_string):
    output = []
    selected_columns_list = extract_select_columns(sql_string)
    main_table_name, main_table_alias, join_table_name, join_table_alias = extract_tables(sql_string)
    join_condition = join_conditions(sql_string)
    if main_table_name and main_table_alias:
        columns, possible_columns = columns_from_alias(main_table_alias, selected_columns_list)
        join_columns, _ = columns_from_alias(main_table_alias, join_condition)
        columns.extend(join_columns)
        output.append({
            'name': main_table_name,
            'columns': columns,
            'possible_columns': possible_columns
        })

    if join_table_name and join_table_alias:
        columns, possible_columns = columns_from_alias(join_table_alias, selected_columns_list)
        join_columns, _ = columns_from_alias(join_table_alias, join_condition)
        columns.extend(join_columns)
        output.append({
            'name': join_table_name,
            'columns': columns,
            'possible_columns': possible_columns
        })
    return output


if __name__ == '__main__':
    result = main(sql_string=input_string)
    with open('result.json', 'w') as file:
        json.dump(result, file)