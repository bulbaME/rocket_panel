def remove_duplicates(data, dp_f='pk'):
    r = []
    c = []

    for v in data:
        if v[dp_f] not in c:
            r.append(v)
            c.append(v[dp_f])

    return r