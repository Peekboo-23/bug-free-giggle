import re


def reg_search(text: str, regex_list: list) -> list:

    BUILTIN_RULES = {
        '标的证券': (
            r'股票代码[：:]\s*(\d{6}\.\w+)',
            lambda g: g[0]
        ),
        '换股期限': (
            r'(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日.*?至.*?'
            r'(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日',
            lambda g: [
                f"{g[0]}-{int(g[1]):02d}-{int(g[2]):02d}",
                f"{g[3]}-{int(g[4]):02d}-{int(g[5]):02d}",
            ]
        ),
    }

    result = []
    for rule_dict in regex_list:
        res_dict = {}
        for key in rule_dict:
            rule = BUILTIN_RULES.get(key)
            if not rule:
                res_dict[key] = None
                continue

            pattern, handler = rule
            match = re.search(pattern, text, re.S)
            if match:
                res_dict[key] = handler(match.groups())
            else:
                res_dict[key] = None
        result.append(res_dict)

    return result


if __name__ == "__main__":
    text = '''
标的证券：本期发行的证券为可交换为发行人所持中国长江电力股份
有限公司股票（股票代码：600900.SH，股票简称：长江电力）的可交换公司债
券。
换股期限：本期可交换公司债券换股期限自可交换公司债券发行结束
之日满 12 个月后的第一个交易日起至可交换债券到期日止，即 2023 年 6 月 2
日至 2027 年 6 月 1 日止。
'''

    regex_list = [{"标的证券": "*自定义*", "换股期限": "*自定义*"}]
    print(reg_search(text, regex_list))
