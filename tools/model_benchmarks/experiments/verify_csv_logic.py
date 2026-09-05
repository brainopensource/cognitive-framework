def parse_csv(content: str) -> list[list[str]]:
    if not content:
        return []
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
            elif content[i:i+2] == '\r\n':
                current_record.append(current_field)
                records.append(current_record)
                current_record = []
                current_field = ""
                i += 2
            elif content[i] == '\n':
                current_record.append(current_field)
                records.append(current_record)
                current_record = []
                current_field = ""
                i += 1
            else:
                current_field += content[i]
                i += 1
    current_record.append(current_field)
    records.append(current_record)
    return records

res1 = parse_csv("a,b,c\n1,2,3")
assert res1 == [["a", "b", "c"], ["1", "2", "3"]], f"Failed Test 1: got {res1}"

res2 = parse_csv('"nome, completo",idade\n"Silva, Joao",30')
assert res2 == [["nome, completo", "idade"], ["Silva, Joao", "30"]], f"Failed Test 2: got {res2}"

res3 = parse_csv('id,descricao\n1,"linha 1\nlinha 2"\n2,fim')
assert res3 == [["id", "descricao"], ["1", "linha 1\nlinha 2"], ["2", "fim"]], f"Failed Test 3: got {res3}"

res4 = parse_csv('tag,"ele disse ""ola"""\n1,ok')
assert res4 == [["tag", 'ele disse "ola"'], ["1", "ok"]], f"Failed Test 4: got {res4}"

res5 = parse_csv('a,"",c\n,,')
assert res5 == [["a", "", "c"], ["", "", ""]], f"Failed Test 5: got {res5}"

print("ALL 5 TESTS PASS 100% PERFECTLY!")
