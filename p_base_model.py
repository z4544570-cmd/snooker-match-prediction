import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from tqdm import tqdm
import xgboost as xgb
from collections import Counter
from xgboost import XGBClassifier

from sklearn.model_selection import (
    train_test_split,
    StratifiedKFold,
    cross_val_score
)

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)


def train_xgb(dataset_training, dataset_label):
    print("=" * 50)
    print("Loading Data...")
    print("=" * 50)

    X = np.array(dataset_training)
    y = np.array(dataset_label)

    print(f"样本数: {len(X)}")
    print(f"特征维度: {X.shape[1]}")
    print()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    # 动态计算权重
    num_class0 = np.sum(y_train == 0)
    num_class1 = np.sum(y_train == 1)
    scale_pos_weight = num_class0 / num_class1
    print(f"类别0数量: {num_class0} | 类别1数量: {num_class1}")
    print(f"scale_pos_weight = {scale_pos_weight:.4f}")

    # 主模型（带 early stopping）
    model = xgb.XGBClassifier(
        scale_pos_weight=scale_pos_weight,  # 可尝试 0.4 ~ 0.6 区间
        eval_metric=['aucpr', 'logloss'],
        n_estimators=800,  # 增加
        learning_rate=0.03,  # 降低
        max_depth=7,  # 尝试 5~8
        subsample=0.75,
        colsample_bytree=0.75,
        gamma=0.1,  # 新增：防止过拟合
        min_child_weight=5,  # 新增
        random_state=42,
        early_stopping_rounds=60
    )
    print("=" * 50)
    print("Training...")
    print("=" * 50)

    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=False
    )

    print("Training completed.")

    # ====================== 测试集评估 ======================
    print("=" * 50)
    print("Test Result")
    print("=" * 50)

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_proba)

    print(f"Accuracy = {acc:.4f}")
    print(f"AUC      = {auc:.4f}\n")

    print("Classification Report")
    print(classification_report(y_test, y_pred))

    print("Confusion Matrix")
    print(confusion_matrix(y_test, y_pred))

    # ====================== 5-Fold CV ======================
    print("=" * 50)
    print("5-Fold Cross Validation")
    print("=" * 50)

    # CV 使用不带 early_stopping 的简化模型
    cv_model = xgb.XGBClassifier(
        scale_pos_weight=scale_pos_weight,
        eval_metric='aucpr',
        n_estimators=300,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        verbosity=0
    )

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(
        cv_model, X, y, cv=cv, scoring="accuracy", n_jobs=1
    )

    print("Fold Accuracy:")
    print(cv_scores)
    print()
    print(f"Mean Accuracy = {cv_scores.mean():.4f}")
    print(f"Std Accuracy  = {cv_scores.std():.4f}")

    # ====================== 特征重要性 ======================
    print("=" * 50)
    print("Feature Importance")
    print("=" * 50)

    importance_df = pd.DataFrame({
        "feature_id": range(X.shape[1]),
        "importance": model.feature_importances_
    }).sort_values(by="importance", ascending=False)

    print(importance_df.head(30))

    return model, importance_df