"""Turn text rows into named amounts."""


def parse_rows(lines):
    rows = []
    for line in lines:
        name, raw = line.split(":")
        rows.append((name, int(raw)))
    return rows
