from sympy import pi

# Gets a string and return True if all chars are digits
def is_number(string):
    for i in string:
        if not i.isdigit():
            return False
    return True


def deg_to_rad(deg):
    return (2*pi)*(float(deg)/360)
