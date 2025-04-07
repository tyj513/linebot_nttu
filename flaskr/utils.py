import opencc

def traditional_to_simplified(traditional_text):
    cc = opencc.OpenCC('t2s')  # 建立繁體字到簡體字的轉換器
    simplified_text = cc.convert(traditional_text)  # 將繁體字轉換成簡體字
    return simplified_text

def simplified_to_traditional(simplified_text):
    cc = opencc.OpenCC('s2t')  # 建立簡體字到繁體字的轉換器
    traditional_text = cc.convert(simplified_text)  # 將簡體字轉換成繁體字
    return traditional_text