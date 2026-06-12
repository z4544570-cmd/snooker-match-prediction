import re
import pandas as pd

def get_decade(date_str):
    """
    输入: "2005-12-13" 或 "2005-12-12 - 12-13"
    输出: '00年代', '10年代', '90年代', '20年代' 等
    """
    if pd.isna(date_str) or not isinstance(date_str, str):
        return None

    # 提取第一个出现的四位年份（兼容范围如 "2005-12-12 - 12-13"）
    match = re.search(r'(\d{4})', date_str)
    if not match:
        return None

    year = int(match.group(1))

    # 计算年代
    decade = (year // 10) * 10

    if decade == 1990:
        return "90s"
    elif decade == 2000:
        return "00s"
    elif decade == 2010:
        return "10s"
    elif decade == 2020:
        return "20s"
    elif decade == 2030:
        return "30s"
    else:
        return f"{decade}s"

def parse_frame_score_keep_break(frame):
    """
    支持左右两边都有括号的情况
    输入示例:
        '110(75)-124(64, 60)'   → 左右都有
        '8-124(64, 60)'         → 只有右边
        '110(75)-44'            → 只有左边
        '100-30'                → 都没有

    返回: (main_score, p1_break, p2_break)
    """
    if not isinstance(frame, str):
        return None, None, None

    frame = frame.strip()

    # 提取所有括号内容
    break_matches = re.findall(r'\(([\d\s,]+)\)', frame)

    p1_break = None
    p2_break = None

    # 判断括号位置
    if break_matches:
        # 找到左边和右边的括号
        left_part = frame.split('-')[0]
        right_part = frame.split('-')[-1]

        if re.search(r'\(', left_part):  # 左边有括号 → Player1
            numbers = [int(x) for x in re.findall(r'\d+', break_matches[0])]
            p1_break = tuple(numbers)

        if re.search(r'\(', right_part):  # 右边有括号 → Player2
            # 如果左右都有，取最后一个括号内容
            idx = 1 if len(break_matches) > 1 else 0
            numbers = [int(x) for x in re.findall(r'\d+', break_matches[idx])]
            p2_break = tuple(numbers)

    # 清理所有括号内容后提取主比分
    frame_clean = re.sub(r'\(.*?\)', '', frame)
    match = re.search(r'(\d+)\s*-\s*(\d+)', frame_clean)

    if match:
        s1 = int(match.group(1))
        s2 = int(match.group(2))
        main_score = (s1, s2)
        return main_score, p1_break, p2_break

    return None, None, None

def get_date_period(date_str):
    """
    输入: "23-11 - 01-12" （日-月 格式）
    输出: 所属时间区间
    """
    if pd.isna(date_str) or not isinstance(date_str, str):
        return None

    # 提取第一个日期（日-月格式）
    match = re.search(r'(\d{1,2})-(\d{1,2})', date_str)
    if not match:
        return None

    day = int(match.group(1))  # 日
    month = int(match.group(2))  # 月   ← 注意这里顺序和之前相反

    # 判断区间
    if (month == 1 and day >= 2) or (month == 2) or (month == 3 and day <= 1):
        return "赛季中期"

    elif (month == 3 and day >= 2) or (month == 4) or (month == 5) or (month == 6) or (month == 7 and day <= 1):
        return "临世锦赛及世锦赛时期"

    elif (month == 7 and day >= 2) or (month == 8) or (month == 9) or (month == 10) or (month == 11 and day <= 1):
        return "赛季前期"

    else:  # 11月2日 以后 到 次年1月1日
        return "赛季中期"


# ==================== 用于 DataFrame 的向量化函数 ====================
def add_period_column(df, date_column='date'):
    df = df.copy()
    df['period'] = df[date_column].apply(get_date_period)
    return df

def valid_scores(scores_str):
    if pd.isna(scores_str):
        return False
    scores_str = str(scores_str).strip()
    if scores_str in ['None', 'none', 'null', 'nan', 'NaN', 'NAN', '', ' ']:
        return False
    frames = scores_str.split(';')
    for frame in frames:
        frame = frame.strip()
        result = parse_frame_score(frame)
        if result is None:
            return False
    return True

def valid_scores_num(scores_str):
    frames = scores_str.split(';')
    return len(frames)

def parse_frame_score(frame):
    """
    输入:
        '110(75)-44'
        '78-56'
        'Robertson docked 1 frame'
        'late at the table'

    输出:
        (110, 44)
        (78, 56)
        None
        None
    """

    if not isinstance(frame, str):
        return None

    # 去掉括号内容
    frame = re.sub(r'\(.*?\)', '', frame)

    # 提取数字-数字
    match = re.search(r'(\d+)\s*-\s*(\d+)', frame)

    if match:
        s1 = int(match.group(1))
        s2 = int(match.group(2))
        return s1, s2

    return None

def missing_value_report(df):
    """
    生成详细的缺失值报告（包含 NaN 和各种字符串缺失情况）
    """
    report = []

    for col in df.columns:
        # 基础信息
        total = len(df)
        dtype = df[col].dtype

        # 1. 真正的 NaN / None
        null_count = df[col].isna().sum()

        # 2. 字符串形式的缺失值
        str_missing = ['None', 'none', 'null', 'nan', 'NaN', 'NAN', '', ' ']
        str_missing_count = df[col].astype(str).str.strip().isin(str_missing).sum()

        # 3. 空字符串（去空格后）
        empty_str_count = (df[col].astype(str).str.strip() == '').sum()

        # 4. 总"缺失"数量（去重计算）
        total_missing = null_count + str_missing_count

        # 5. 缺失率
        missing_rate = total_missing / total * 100

        report.append({
            'column': col,
            'dtype': dtype,
            'total_rows': total,
            'null_count': null_count,
            'str_missing_count': str_missing_count,
            'empty_str_count': empty_str_count,
            'total_missing': total_missing,
            'missing_rate_%': round(missing_rate, 2)
        })

    # 转为 DataFrame 并排序
    report_df = pd.DataFrame(report)
    report_df = report_df.sort_values(by='missing_rate_%', ascending=False)

    # 输出概览
    print(f"数据集总行数: {len(df)} 行")
    print(f"match_id数: {df['match_id'].nunique()}")
    print(f"共有 {len(df.columns)} 列")
    print(f"有缺失值的列数量: {len(report_df[report_df['total_missing'] > 0])} 列\n")

    return report_df

def turn_df_agg_into_single(df):
    df = (
        df.sort_values("match_id")
        .drop_duplicates(subset="match_id")
    )
    return df

def clean_scores(df):
    df["scores"] = df["scores"].astype(str).str.split(";")
    df = df.explode("scores")
    df["scores"] = df["scores"].apply(parse_frame_score)


from contextlib import redirect_stdout
import sys


def run_and_save_output(func, output_file=r"C:\Users\赵梓健\PyCharmMiscProject\snooker predict\模式识别输出.txt"):
    """运行函数并把所有输出保存到文件"""
    with open(output_file, "w", encoding="utf-8") as f:
        with redirect_stdout(f):
            try:
                func()  # 执行你的主函数
            except Exception as e:
                print(f"运行出错: {e}", file=sys.stderr)  # 错误信息也保存

    print(f"✅ 所有输出已保存到: {output_file}")


def switch_score(score: str):
    """
    将比分字符串左右对调
    示例: "10-8; 9-11; 12-7" → "8-10; 11-9; 7-12"
    """
    if not isinstance(score, str) or not score.strip():
        return None

    # 按分号分割每一局比分
    frames = [f.strip() for f in score.strip().split(';') if f.strip()]

    switched = []
    for frame in frames:
        if '-' not in frame:
            switched.append(frame)  # 没有 '-' 的保持原样
            continue

        # 左右对调
        left, right = frame.split('-', 1)  # 只按第一个 '-' 分割
        switched.append(f"{right.strip()}-{left.strip()}")

    # 重新拼接
    result = "; ".join(switched)
    return result