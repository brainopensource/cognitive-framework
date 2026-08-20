def includes(parent, child):
    return parent == child or str(child).startswith(str(parent))


def decide(parent, child):
    return includes(parent, child)
