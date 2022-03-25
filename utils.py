from sympy import pi

# Gets a string and return True if all chars are digits
def is_number(string):
    if string and string[0] == '-': string = string[1:]
    for i in string:
        if not i.isdigit():
            return False
    return True


def deg_to_rad(deg):
    return str((2*pi)*(float(deg)/360))
