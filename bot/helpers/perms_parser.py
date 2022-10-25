from ..helpers.enums import NewUserFilter, Punishment


def stringify_dangerous_user(perm_num):
    return ", ".join([perm.name.title() for perm in Punishment if perm_num & perm])


def stringify_new_user_filter(perm_num):
    return ", ".join([perm.name.title() for perm in NewUserFilter if perm_num & perm])
