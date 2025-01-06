def cal_sum(*args, **kwargs):
    result = sum(args)
    return result

def cal_difference(x, y, **kwargs):
    result = x - y
    return result

def cal_multiply(x, y, **kwargs):
    result = x * y
    return result

def cal_divide(x, y, **kwargs):
    result = x / y
    return result

def cal_median(*args, **kwargs):
    result = sum(args) / len(args)
    return result

def price_with_discount(price, discount, **kwargs):
    value_discount = price * (discount / 100)
    result = cal_difference(price, value_discount)
    return result

def price_with_tax(price, tax, **kwargs):
    result = price + price * (tax / 100)
    return result

def price_with_shipping(price, shipping, **kwargs):
    result = price + shipping
    return result

def price_total(price, discount, tax, shipping, **kwargs):
    result = price + price * (tax / 100) + shipping - price * (discount / 100)
    return result
