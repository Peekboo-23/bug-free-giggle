import requests
import pandas as pd
import time
import os


API_URL = "https://www.chinamoney.com.cn/ags/ms/cm-u-bond-md/BondMarketInfoListEN"
BOND_TYPE = "100001"
ISSUE_YEAR = "2023"
PAGE_SIZE = 50
OUTPUT_FILE = "2023_treasury_bond_data.csv"


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://www.chinamoney.com.cn",
    "Referer": "https://www.chinamoney.com.cn/english/bdInfo/",
    "X-Requested-With": "XMLHttpRequest",
}

data = {
    "isin": "",
    "bondCode": "",
    "issueEnty": "",
    "bondType": BOND_TYPE,
    "couponType": "",
    "issueYear": ISSUE_YEAR,
    "rtngShrt": "",
    "bondSpclPrjctVrty": "",
}


def fetch_all_pages() -> list:

    all_records = []
    page_no = 1
    total = None

    while True:
        params = {**data, "pageNo": str(page_no), "pageSize": str(PAGE_SIZE)}
        print(f"[第 {page_no} 页] 请求中...", end=" ")

        try:
            resp = requests.post(API_URL, headers=headers, data=params, timeout=20)
            resp.raise_for_status()
            result = resp.json()
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            break
        except ValueError as e:
            print(f"JSON 解析失败: {e}")
            break

        data_block = result.get("data", {})
        if total is None:
            total = data_block.get("total", 0)
            print(f"共 {total} 条记录")
            if total == 0:
                print("未找到任何数据，请检查筛选条件。")
                break

        records = data_block.get("resultList", [])
        if not records:
            print("无更多数据。")
            break

        all_records.extend(records)
        print(f"累计获取 {len(all_records)}/{total} 条")

        if len(all_records) >= total:
            break

        page_no += 1
        time.sleep(0.3)

    return all_records


def parse_records(raw_records: list) -> pd.DataFrame:

    parsed = []
    for rec in raw_records:
        parsed.append({
            "ISIN":         rec.get("isin", ""),
            "Bond Code":     rec.get("bondCode", ""),
            "Issuer":        rec.get("entyFullName", ""),
            "Bond Type":     rec.get("bondType", ""),
            "Issue Date":    rec.get("issueStartDate", ""),
            "Latest Rating": rec.get("debtRtng", "N/A") if rec.get("debtRtng") != "---" else "N/A",
        })

    df = pd.DataFrame(parsed)

    df["Issue Date"] = pd.to_datetime(df["Issue Date"], errors="coerce")
    df = df.sort_values("Issue Date").reset_index(drop=True)
    df["Issue Date"] = df["Issue Date"].dt.strftime("%Y-%m-%d")

    return df

def save_csv(df: pd.DataFrame, filepath: str) -> None:
    df.to_csv(filepath, index=False, encoding="utf-8-sig")
    print(f"\n CSV 已保存: {filepath}")
    print(f"   记录数: {len(df)}")
    print(f"   文件大小: {os.path.getsize(filepath)} bytes")


def main():
    print("=" * 60)
    print("中国货币网 · 债券信息查询")
    print(f"  筛选: Bond Type = Treasury Bond, Issue Year = {ISSUE_YEAR}")
    print("=" * 60)

    raw_records = fetch_all_pages()
    if not raw_records:
        print("未获取到数据，程序退出。")
        return

    df = parse_records(raw_records)

    print("\n--- 数据预览（前 5 条）---")
    print(df.head(5).to_string(index=False))

    save_csv(df, OUTPUT_FILE)

    print("\n--- 字段说明 ---")
    print(df.dtypes.to_string())


if __name__ == "__main__":
    main()
