import numpy as np


# ─────────────────────────────────────────────────────────
# 辅助：单局单球员的单杆统计
# ─────────────────────────────────────────────────────────

def _break_stats(breaks):
    """
    breaks: tuple of ints 或 None
    return: (max, mean, count, sum, has_century, has_fifty)
    """
    if breaks is None or len(breaks) == 0:
        return 0.0, 0.0, 0, 0.0, 0, 0
    arr = np.array(breaks, dtype=float)
    return (
        float(arr.max()),
        float(arr.mean()),
        int(len(arr)),
        float(arr.sum()),
        int((arr >= 100).any()),   # 本局是否有世纪杆
        int((arr >= 50).any()),    # 本局是否有50+
    )


# ─────────────────────────────────────────────────────────
# 特征提取（主函数）
# ─────────────────────────────────────────────────────────

def extract_features(frames_data):
    n = len(frames_data)

    # 自动判断格式
    # 新格式: ((a, b), breaks_p1, breaks_p2)
    # 旧格式: (a, b)
    if isinstance(frames_data[0][0], (tuple, list)):
        # 新格式
        a    = np.array([float(d[0][0]) for d in frames_data])
        b    = np.array([float(d[0][1]) for d in frames_data])
        brk1 = np.array([_break_stats(d[1]) for d in frames_data], dtype=float)
        brk2 = np.array([_break_stats(d[2]) for d in frames_data], dtype=float)
    else:
        # 旧格式，无单杆数据
        a    = np.array([float(d[0]) for d in frames_data])
        b    = np.array([float(d[1]) for d in frames_data])
        brk1 = np.zeros((n, 6), dtype=float)
        brk2 = np.zeros((n, 6), dtype=float)


    # 方便按名称取列
    MAX, MEAN, CNT, SUM, CENT, FIFTY = 0, 1, 2, 3, 4, 5

    # ── 原有的轨迹特征 ────────────────────────
    theta     = np.arctan2(b, a)
    pace      = (a + b) / np.sqrt(2)
    domin     = (a - b) / np.sqrt(2)
    cum_domin = np.cumsum(domin)

    feat = {}

    # 比赛进度
    feat["n_frames"] = n

    # 多窗口轨迹均值
    for w in [3, 5, 10]:
        ew = min(w, n)
        feat[f"theta_mean_w{w}"] = theta[-ew:].mean()
        feat[f"domin_mean_w{w}"] = domin[-ew:].mean()
        feat[f"pace_mean_w{w}"]  = pace[-ew:].mean()

    # 全局轨迹统计
    feat["theta_mean_all"] = theta.mean()
    feat["theta_std"]      = theta.std()  if n > 1 else 0.0
    feat["domin_mean_all"] = domin.mean()
    feat["domin_std"]      = domin.std()  if n > 1 else 0.0
    feat["domin_cumsum"]   = float(cum_domin[-1])
    feat["pace_mean_all"]  = pace.mean()
    feat["pace_std"]       = pace.std()   if n > 1 else 0.0

    # 漂移
    recent = max(1, n // 3)
    feat["theta_drift"] = theta[-recent:].mean() - theta.mean()
    feat["domin_drift"] = domin[-recent:].mean() - domin.mean()
    feat["pace_drift"]  = pace[-recent:].mean()  - pace.mean()

    # 线性趋势
    if n >= 2:
        x = np.arange(n, dtype=float)
        feat["domin_trend"] = float(np.polyfit(x, domin, 1)[0])
        feat["theta_trend"] = float(np.polyfit(x, theta, 1)[0])
        feat["pace_trend"]  = float(np.polyfit(x, pace,  1)[0])
    else:
        feat["domin_trend"] = feat["theta_trend"] = feat["pace_trend"] = 0.0

    # 曲率
    if n >= 2:
        angles    = np.angle(a + 1j * b)
        curvature = np.diff(angles)
        feat["curvature_std"]  = float(curvature.std())
        feat["curvature_mean"] = float(curvature.mean())
        feat["curvature_last"] = float(curvature[-1])
        feat["curvature_sum"]  = float(curvature.sum())
    else:
        feat["curvature_std"] = feat["curvature_mean"] = \
        feat["curvature_last"] = feat["curvature_sum"] = 0.0

    # 连胜/连败
    direction = 1 if domin[-1] > 0 else -1
    streak    = 1
    for i in range(n - 2, -1, -1):
        if (domin[i] > 0) == (direction > 0):
            streak += 1
        else:
            break
    feat["streak"] = streak * direction

    # EWMA 主导
    alpha = 0.3
    ewma  = float(domin[0])
    for d in domin[1:]:
        ewma = alpha * float(d) + (1 - alpha) * ewma
    feat["domin_ewma"] = ewma

    # 最后一局原始分差
    feat["last_a"]     = float(a[-1])
    feat["last_b"]     = float(b[-1])
    feat["last_domin"] = float(domin[-1])
    feat["last_pace"]  = float(pace[-1])

    # ── 新增：单杆特征 ────────────────────────

    # 辅助：安全除法（避免分母为0）
    def safe_ratio(x, y, default=0.5):
        return float(x / y) if y > 1e-6 else default

    # 全局单杆均值 & 最大杆
    p1_max_all  = brk1[:, MAX].max()
    p2_max_all  = brk2[:, MAX].max()
    p1_mean_all = brk1[:, MEAN]
    p2_mean_all = brk2[:, MEAN]
    p1_avg = p1_mean_all[p1_mean_all > 0].mean() if (p1_mean_all > 0).any() else 0.0
    p2_avg = p2_mean_all[p2_mean_all > 0].mean() if (p2_mean_all > 0).any() else 0.0

    feat["p1_max_break_all"]  = float(p1_max_all)
    feat["p2_max_break_all"]  = float(p2_max_all)
    feat["p1_avg_break_all"]  = p1_avg
    feat["p2_avg_break_all"]  = p2_avg

    # 单杆主导比：p1 / (p1+p2)，越大表示p1单杆越强
    feat["break_domin_all"] = safe_ratio(
        p1_max_all, p1_max_all + p2_max_all
    )
    feat["break_avg_domin_all"] = safe_ratio(p1_avg, p1_avg + p2_avg)

    # 多窗口单杆统计
    for w in [3, 5]:
        ew = min(w, n)
        b1w = brk1[-ew:]
        b2w = brk2[-ew:]

        p1_max_w = float(b1w[:, MAX].max())
        p2_max_w = float(b2w[:, MAX].max())
        p1_avg_w = float(b1w[:, MEAN][b1w[:, MEAN] > 0].mean()) \
                   if (b1w[:, MEAN] > 0).any() else 0.0
        p2_avg_w = float(b2w[:, MEAN][b2w[:, MEAN] > 0].mean()) \
                   if (b2w[:, MEAN] > 0).any() else 0.0

        feat[f"break_domin_max_w{w}"] = safe_ratio(
            p1_max_w, p1_max_w + p2_max_w
        )
        feat[f"break_domin_avg_w{w}"] = safe_ratio(p1_avg_w, p1_avg_w + p2_avg_w)
        feat[f"p1_max_break_w{w}"]    = p1_max_w
        feat[f"p2_max_break_w{w}"]    = p2_max_w

    # 单杆主导漂移：近期 vs 全局（动量切换信号）
    ew3 = min(3, n)
    p1_max_recent = float(brk1[-ew3:, MAX].max())
    p2_max_recent = float(brk2[-ew3:, MAX].max())
    break_domin_recent = safe_ratio(p1_max_recent, p1_max_recent + p2_max_recent)
    feat["break_domin_drift"] = break_domin_recent - feat["break_domin_all"]

    # 世纪杆 & 50+ 累计
    feat["p1_centuries"] = int(brk1[:, CENT].sum())
    feat["p2_centuries"] = int(brk2[:, CENT].sum())
    feat["p1_fifty_plus"] = int(brk1[:, FIFTY].sum())
    feat["p2_fifty_plus"] = int(brk2[:, FIFTY].sum())
    feat["century_diff"]  = feat["p1_centuries"] - feat["p2_centuries"]
    feat["fifty_diff"]    = feat["p1_fifty_plus"] - feat["p2_fifty_plus"]

    # 最后一局单杆信号
    feat["last_p1_max_break"] = float(brk1[-1, MAX])
    feat["last_p2_max_break"] = float(brk2[-1, MAX])
    feat["last_break_domin"]  = safe_ratio(
        brk1[-1, MAX], brk1[-1, MAX] + brk2[-1, MAX]
    )

    # 单杆EWMA（近期单杆状态的平滑估计）
    alpha = 0.3
    e1, e2 = float(brk1[0, MAX]), float(brk2[0, MAX])
    for i in range(1, n):
        e1 = alpha * float(brk1[i, MAX]) + (1 - alpha) * e1
        e2 = alpha * float(brk2[i, MAX]) + (1 - alpha) * e2
    feat["p1_break_ewma"] = e1
    feat["p2_break_ewma"] = e2
    feat["break_ewma_domin"] = safe_ratio(e1, e1 + e2)

    return list(feat.values())


# ─────────────────────────────────────────────────────────
# 累积样本生成
# ─────────────────────────────────────────────────────────

def extract_match_samples(frames_data, min_frames=2):
    """
    frames_data: list of ((a,b), breaks_p1, breaks_p2)
    return: (samples, indices)
    """
    samples, indices = [], []
    for i in range(min_frames, len(frames_data) + 1):
        history  = frames_data[:i]
        features = extract_features(history)
        samples.append(features)
        indices.append(i)
    return samples, indices

if __name__ == "__main__":
    frames_data = [((80, 54), (77,), None), ((90, 41), (51,), None), ((101, 1), (97,), None)]
    samples, indices = extract_match_samples(frames_data)
    print(samples)
    print(indices)

