def lists_equal(left, right, sort_by=None):
    return sorted(left, key=sort_by) == sorted(right, key=sort_by)
