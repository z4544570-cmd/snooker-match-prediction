import numpy as np
import pandas as pd
import xgboost as xgb
from p_pattern import *
from sklearn.model_selection import (
    train_test_split,
    StratifiedKFold,
    cross_val_score
)

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
    log_loss,
    brier_score_loss
)

from sklearn.calibration import CalibratedClassifierCV

# ─────────────────────────────────────────────
# 训练
# ─────────────────────────────────────────────

def train_pattern_model(dataset_training, dataset_label):
    print("=" * 60)
    print("Loading Pattern Dataset...")
    print("=" * 60)

    X = np.array(dataset_training)
    y = np.array(dataset_label)

    print(f"样本数       : {len(X)}")
    print(f"特征维度     : {X.shape[1]}")

    # ── 划分 ──────────────────────────────────
    # 70% train | 15% val（early stopping）| 15% test
    X_train, X_tmp, y_train, y_tmp = train_test_split(
        X, y, test_size=0.30, random_state=42, stratify=y
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_tmp, y_tmp, test_size=0.50, random_state=42, stratify=y_tmp
    )

    # ── P_base ────────────────────────────────
    p_base = float(y_train.mean())
    print(f"\nP_base       : {p_base:.4f}")

    num_c0 = int((y_train == 0).sum())
    num_c1 = int((y_train == 1).sum())
    spw    = num_c0 / num_c1
    print(f"class 0 / 1  : {num_c0} / {num_c1}")
    print(f"scale_pos_weight = {spw:.4f}")

    # ── 模型 ──────────────────────────────────
    print("\n" + "=" * 60)
    print("Training...")
    print("=" * 60)

    model = xgb.XGBClassifier(
        objective          = "binary:logistic",
        eval_metric        = ["auc", "logloss"],
        scale_pos_weight   = spw,

        n_estimators       = 2000,
        learning_rate      = 0.02,
        max_depth          = 4,
        min_child_weight   = 10,
        gamma              = 0.2,
        subsample          = 0.75,
        colsample_bytree   = 0.75,
        reg_alpha          = 0.1,
        reg_lambda         = 1.0,

        early_stopping_rounds = 80,
        random_state       = 42,
        n_jobs             = -1,
    )

    model.fit(
        X_train, y_train,
        eval_set  = [(X_val, y_val)],
        verbose   = False,
    )

    best_iter = model.best_iteration
    print(f"Best iteration : {best_iter}")

    # ── 测试集评估 ────────────────────────────
    print("\n" + "=" * 60)
    print("Test Result")
    print("=" * 60)

    y_pred  = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    acc   = accuracy_score(y_test, y_pred)
    auc   = roc_auc_score(y_test, y_proba)
    ll    = log_loss(y_test, y_proba)
    brier = brier_score_loss(y_test, y_proba)

    print(f"Accuracy   = {acc:.4f}")
    print(f"AUC        = {auc:.4f}")
    print(f"LogLoss    = {ll:.4f}  (baseline 0.6931)")
    print(f"BrierScore = {brier:.4f}")
    print()
    print(classification_report(y_test, y_pred))
    print(confusion_matrix(y_test, y_pred))

    # ── 可靠性（无校准，直接检查原始概率）────
    print("\n" + "=" * 60)
    print("Reliability (raw, no calibration)")
    print("=" * 60)
    ece = _ece(y_test, y_proba)
    print(f"ECE = {ece:.4f}")
    _print_reliability_curve(y_test, y_proba)

    # ── 5-Fold CV ─────────────────────────────
    print("\n" + "=" * 60)
    print("5-Fold CV  (AUC)")
    print("=" * 60)

    cv_model = xgb.XGBClassifier(
        objective        = "binary:logistic",
        eval_metric      = "auc",
        scale_pos_weight = spw,
        n_estimators     = best_iter,
        learning_rate    = 0.02,
        max_depth        = 4,
        min_child_weight = 10,
        gamma            = 0.2,
        subsample        = 0.75,
        colsample_bytree = 0.75,
        reg_alpha        = 0.1,
        reg_lambda       = 1.0,
        random_state     = 42,
        n_jobs           = -1,
    )

    cv       = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_aucs  = cross_val_score(cv_model, X, y, cv=cv, scoring="roc_auc", n_jobs=1)
    print(f"Fold AUC  : {cv_aucs}")
    print(f"Mean AUC  = {cv_aucs.mean():.4f} ± {cv_aucs.std():.4f}")

    # ── 特征重要性 ────────────────────────────
    print("\n" + "=" * 60)
    print("Feature Importance")
    print("=" * 60)

    feat_names = list(extract_features([(1, 1)].__class__([
        (60, 40), (70, 30)
    ]).__class__([
        (60, 40), (70, 30)
    ])) )  # 仅用于占位，实际用 feature_names 参数更优
    # 直接用 index 显示
    imp_df = pd.DataFrame({
        "feature_id" : range(X.shape[1]),
        "importance" : model.feature_importances_
    }).sort_values("importance", ascending=False)
    print(imp_df.head(20).to_string(index=False))

    return model, imp_df, p_base


# ─────────────────────────────────────────────
# 辅助
# ─────────────────────────────────────────────

def _ece(y_true, y_proba, n_bins=10):
    bins = np.linspace(0, 1, n_bins + 1)
    ece  = 0.0
    for i in range(n_bins):
        m = (y_proba >= bins[i]) & (y_proba < bins[i + 1])
        if m.sum() == 0:
            continue
        ece += m.sum() * abs(y_true[m].mean() - y_proba[m].mean())
    return ece / len(y_true)


def _print_reliability_curve(y_true, y_proba, n_bins=10):
    bins = np.linspace(0, 1, n_bins + 1)
    print(f"{'pred':>6}  {'actual':>6}  bar")
    for i in range(n_bins):
        m = (y_proba >= bins[i]) & (y_proba < bins[i + 1])
        if m.sum() == 0:
            continue
        pred   = y_proba[m].mean()
        actual = y_true[m].mean()
        bar    = "█" * int(actual * 20)
        print(f"{pred:6.2f}  {actual:6.2f}  {bar}")


# ── ECE 辅助函数 ──────────────────────────────────────────────
def _compute_ece(y_true, y_proba, n_bins=10):
    """Expected Calibration Error"""
    bins = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    for i in range(n_bins):
        mask = (y_proba >= bins[i]) & (y_proba < bins[i + 1])
        if mask.sum() == 0:
            continue
        acc  = y_true[mask].mean()
        conf = y_proba[mask].mean()
        ece += mask.sum() * abs(acc - conf)
    return ece / len(y_true)
