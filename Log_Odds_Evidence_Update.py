import numpy as np


def logit(p):
    """
    Probability -> Log Odds
    """
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


def sigmoid(x):
    """
    sigmoid function把实数轴映射到[0，1],将赔率转化为概率
    Log Odds -> Probability
    """
    return 1 / (1 + np.exp(-x))


def log_odds_update(
        p_prior,
        p_pattern,
        p_pattern_base=0.5,
        alpha=1.0,
        verbose=True
):
    """
    Log-Odds Bayesian Update

    Parameters
    ----------
    p_prior : float
        p_base模型输出的先验概率

    p_pattern : float
        pattern模型输出概率

    p_pattern_base : float
        pattern模型训练集标签均值
        平衡数据集一般为0.5

    alpha : float
        Pattern证据权重

        alpha = 0
            完全忽略Pattern

        alpha = 1
            完全采用Pattern

        alpha < 1
            部分采用Pattern

        alpha > 1
            强化Pattern

    verbose : bool
        是否打印更新过程

    Returns
    -------
    p_post : float
        更新后的后验概率
    """

    # prior
    prior_log_odds = logit(p_prior)

    # evidence increment
    pattern_increment = (
            logit(p_pattern)
            - logit(p_pattern_base)
    )

    # posterior
    posterior_log_odds = (
            prior_log_odds
            + alpha * pattern_increment
    )

    p_post = sigmoid(posterior_log_odds)

    if verbose:
        print("\n====================")
        print("LOG-ODDS UPDATE")
        print("====================")

        print(f"P_prior         = {p_prior:.4f}")
        print(f"P_pattern       = {p_pattern:.4f}")
        print(f"P_pattern_base  = {p_pattern_base:.4f}")
        print(f"alpha           = {alpha:.4f}")

        print()

        print(f"logit(prior)    = {prior_log_odds:.4f}")
        print(f"increment       = {pattern_increment:.4f}")

        print()

        print(f"logit(post)     = {posterior_log_odds:.4f}")
        print(f"P_post          = {p_post:.4f}")

    return p_post

