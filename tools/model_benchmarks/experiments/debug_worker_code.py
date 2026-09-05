import subprocess
import re

code = '''
def parse_csv(content: str) -> list[list[str]]:
    records = []
    current_record = []
    current_field = ""
    in_quoted_field = False
    i = 0
    while i < len(content):
        if in_quoted_field:
            if i + 1 < len(content) and content[i] == '"' and content[i+1] == '"':
                current_field += '"'
                i += 2
            elif content[i] == '"':
                in_quoted_field = False
                i += 1
            else:
                current_field += content[i]
                i += 1
        else:
            if content[i] == ',':
                current_record.append(current_field)
                current_field = ""
                i += 1
            elif content[i] == '"':
                in_quoted_field = True
                i += 1
            elif content[i:i+2] == '\\r\\n':
                current_record.append(current_field)
                records.append(current_record)
                current_record = []
                current_field = ""
                i += 2
            elif content[i] == '\\n':
                current_record.append(current_field)
                records.append(current_record)
                current_record = []
                current_field = ""
                i += 1
            else:
                current_field += content[i]
                i += 1
    if current_field:
        current_record.append(current_field)
    if current_record:
        records.append(current_record)
    return records
'''

test_harness = '''
res5 = parse_csv('a,"",c\\n,,')
print("res5 result:", res5)
assert res5 == [["a", "", "c"], ["", "", ""]], f"Failed Test 5: got {res5}"
'''

res = subprocess.run(["python3", "-c", code + test_harness], capture_output=True, text=True)
print("STDOUT:", res.stdout)
print("STDERR:", res.stderr)
