# Snooker Bayesian Prediction System

## Project Overview

This project aims to predict the winner of the next frame in a professional snooker match.

Unlike traditional machine learning approaches that directly predict outcomes, this project separates the prediction process into two independent information sources:

1. Prior Information (Player Strength)
2. Match Pattern Information (Frame-by-frame dynamics)

The two probabilities are then combined through a Bayesian Log-Odds Update framework.

---

## Motivation

Most sports prediction systems mix all features into a single model.

This project attempts to answer a different question:

> How should prior knowledge and in-match evidence be combined mathematically?

The resulting architecture follows a Bayesian perspective:

Prior Probability + Match Evidence → Posterior Probability

---

## System Architecture

Raw Match Data

↓

Pre-Match Features

↓

P_base Model

↓

P_prior

----------------------------------

Frame-by-Frame Scores

↓

Pattern Feature Engineering

↓

P_pattern Model

↓

Match Evidence

----------------------------------

Bayesian Log-Odds Update

↓

P_post

---

## P_base Module

Purpose:

Estimate the probability of Player A winning the next frame based solely on pre-match information.

Features include:

- Historical performance metrics
- Player profile vectors
- Strength difference vectors

Model:

- XGBoost Classifier

Performance:

- AUC ≈ 0.57

---

## P_pattern Module

Purpose:

Extract match dynamics from frame-by-frame score trajectories.

Each frame score is represented as a 2D vector:

(frame_score_A, frame_score_B)

Feature engineering includes:

- Theta (direction)
- Dominance
- Pace
- Curvature
- Momentum
- EWMA trends
- Streak statistics

Model:

- XGBoost Classifier
- Probability Calibration

Performance:

- AUC ≈ 0.54

---

## Bayesian Update

Posterior probability is computed using:

logit(P_post)

=

logit(P_prior)

+

α ×

(

logit(P_pattern)

−

logit(P_pattern_base)

)

where:

- P_prior comes from P_base
- P_pattern comes from the pattern model
- P_pattern_base is the training-set baseline probability
- α controls evidence strength

---

## Key Findings

### Data Leakage Discovery

A major issue was discovered during development:

Including future match information accidentally produced unrealistically high performance.

After removing leakage, model performance dropped significantly but became reliable.

This became one of the most important lessons of the project.

---

### Match Dynamics Representation

An important insight was that frame scores can be viewed as a trajectory in 2D space.

This perspective motivated the pattern feature engineering framework and remains an active research direction.

---

## Current Status

Version: v1.0

Completed:

- Data pipeline
- Feature engineering
- P_base model
- P_pattern model
- Bayesian fusion framework
- Real-time prediction workflow

Future Work:

- Trajectory-based sequence models
- LSTM / Transformer experiments
- Improved pattern representation
- Online Bayesian updating
- Web deployment
