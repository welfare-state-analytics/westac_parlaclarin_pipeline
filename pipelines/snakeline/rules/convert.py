import xmltodict

# def lookup(dic, key, *keys):
#     if keys:
#         return lookup(dic.get(key, {}), *keys)
#     return dic.get(key)

def lookup(dic, *keys):
    for key in keys or []:
        dic = dic.get(key, {})
    return dic

def parla_clarin_to_u_csv(source_file: str, target_file: str) -> None:

    with open(source_file, mode="r") as fp:
        teiCorpus = xmltodict.parse(fp.read())
    

