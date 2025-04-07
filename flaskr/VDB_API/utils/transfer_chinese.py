from opencc import OpenCC

def traditional_to_simplified(text):
    cc = OpenCC('t2s')
    return cc.convert(text)

def simplified_to_traditional(text):   
    cc = OpenCC('s2t')
    return cc.convert(text)