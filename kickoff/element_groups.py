
def get_element_group(el_num):
    if el_num == 1: return 1

    elif el_num == 2: return 18

    elif 2 < el_num < 19:
        if (el_num - 2) % 8 == 0: return 18
        elif (el_num - 2) % 8 <= 2: return (el_num - 2) % 8
        else: return 10 + (el_num - 2) % 8

    elif 18 < el_num < 55:
        if (el_num - 18) % 18 == 0: return 18
        else: return (el_num - 18) % 18

    if 56 < el_num < 72: return 3 # custom group for lanthanoids

    elif 88 < el_num < 104: return 3 # custom group for actinoids

    elif (el_num - 54) % 32 == 0: return 18

    elif (el_num - 54) % 32 >= 17: return (el_num - 54) % 32 - 14

    else: return (el_num - 54) % 32
