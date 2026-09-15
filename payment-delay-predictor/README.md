# Construction Payment Risk Prediction

An operational machine-learning system for prioritizing construction payment-protection workflows before delay or escalation becomes harder to manage.

The project combines a governed AWS data and serving architecture with an interpretable Logistic Regression champion. A separate DataRobot AutoML study tests whether a broader model search produces a meaningful reason to replace that production choice.

> **Responsible-use boundary:** all development and evaluation data is synthetic. Predictions support operational prioritization and human review; they are not legal advice, legal conclusions, or automated legal decisions.

## Project objective

Construction payment protection depends on acting while notices, documentation, payment-chain records, and escalation options are still useful. The system ranks workflows by modeled escalation risk so operations teams can decide what to review first. It does not decide whether a legal right exists or what action a person should take.

The design priorities are:

- surface higher-risk workflows early enough for human intervention;
- keep model outputs traceable to a frozen feature and explanation contract;
- preserve a clear boundary between prediction, operational review, and legal judgment;
- monitor service health and data drift without silently retraining or changing thresholds.

## Production architecture

```text
Synthetic workflow data
        │
        ▼
Amazon S3 ──► AWS Glue ──► Amazon Athena
        │                         │
        │                         └──► Operations dashboard and review queue
        ▼
Amazon SageMaker
training, temporal evaluation, artifact promotion
        │
        ▼
Versioned Logistic Regression v1 artifact
        │
        ▼
FastAPI service on Amazon ECS ──► human-reviewed prioritization
        │
        └──► Amazon CloudWatch logs, metrics, alarms, and drift signals

IAM applies least-privilege access across storage, training, query, and serving boundaries.
```

The repository contains the serving API, operational dashboard, model and feature contracts, experiment records, explanation artifacts, monitoring policy, incident runbook, and container build definitions.

## Production champion

**Logistic Regression v1 remains the approved production champion.** Its operational threshold is frozen at **0.20**, chosen to support a review-oriented workflow where missing a developing payment risk carries a meaningful operational cost.

The champion is retained because it is already integrated with the production feature contract and AWS serving path, its behavior is directly inspectable, and its monitoring and explanation contracts are established. Replacing it requires more than a small leaderboard improvement: a challenger must demonstrate material, repeatable benefit under comparable validation while preserving operational clarity and governance.

## DataRobot AutoML benchmark

DataRobot was used as a benchmark and challenger search, not as the deployed runtime. The strongest DataRobot result was **Elastic-Net with α=0.5**.

| DataRobot model | Holdout ROC-AUC |
|---|---:|
| Elastic-Net, α=0.5 | **0.6840** |
| LightGBM | 0.6806 |
| XGBoost | 0.6765 |
| GAM | 0.6748 |
| Random Forest | 0.6714 |
| Elastic-Net L2 | 0.6702 |
| RuleFit | 0.6625 |

For Elastic-Net α=0.5, the additional verified results are:

| Evaluation measure | Result |
|---|---:|
| Backtest ROC-AUC | **0.6733** |
| Holdout PR-AUC | **0.4136** |
| Holdout LogLoss | **0.5274** |

### How to read the comparison

The AutoML results are **not an identical head-to-head comparison** with the manually engineered Logistic Regression experiment. The two studies use different temporal partitions. The DataRobot leaderboard supports challenger discovery within its own evaluation design; it does not, by itself, establish that a model will outperform the AWS champion in the production pipeline.

The benchmark therefore answers a narrower question: *does a wider automated search reveal a sufficiently strong challenger to justify a controlled, partition-aligned evaluation?* On the verified evidence available, it does not justify replacing the simpler production champion. No DataRobot model is deployed.

## Temporal validation

Random splits can leak future workflow patterns into training and overstate performance. The production experiment uses ordered development, validation, and untouched out-of-time test periods. The decision threshold is selected before final testing and remains frozen during final evaluation.

DataRobot also used backtesting and a holdout, but with different temporal partitions. Results are reported under their original evaluation labels and are not merged into the production experiment table.

## Explainability and model governance

The production model exposes human-readable drivers derived from its coefficients, supported by a versioned explanation contract and SHAP as a secondary analysis method. Explanations describe statistical associations in synthetic data; they are not causal findings.

The verified DataRobot feature-effect and SHAP review supports these qualitative directions:

- a higher prior escalation rate increases modeled risk;
- more complete payment-chain information decreases modeled risk;
- critical missing fields increase modeled risk;
- conflicting project information increases modeled risk.

No unverified SHAP magnitude, feature rank, or local explanation value is published. Predictions remain subject to human review, and monitoring signals cannot automatically change the approved threshold or trigger model promotion.

## Production engineering

- **Versioned contracts:** feature schema, model manifest, API response, explainability behavior, dashboard behavior, and monitoring policy are committed as inspectable artifacts.
- **Serving:** FastAPI exposes health, model metadata, and prediction endpoints backed by the approved serialized pipeline.
- **Operations:** the dashboard reads candidate workflows from Athena, applies the frozen threshold, and records human-review activity in S3.
- **Observability:** CloudWatch receives structured logs and service metrics, with documented alarms and an incident runbook.
- **Containers:** separate hardened images support the API and dashboard deployment paths.
- **Change control:** model promotion, threshold changes, and retraining require explicit review rather than automatic action.

## Repository guide

| Path | Purpose |
|---|---|
| `app/` | Prediction API, inference, explanations, schemas, and observability |
| `dashboard/` | Athena-backed risk queue, analytics, and human-review workflow |
| `artifacts/` | Versioned experiment, model, API, explainability, dashboard, and monitoring evidence |
| `notebooks/` | Exploratory analysis and the controlled Logistic Regression experiment |
| `tests/` | API contract and integration coverage |
| `data_dictionary.md` | Synthetic workflow field definitions and use constraints |

## Local validation

```bash
cd payment-delay-predictor
python -m pytest tests
```

The API and dashboard use separate dependency manifests and container definitions so each runtime can be built and reviewed independently.

## Current status

- **Production champion:** Logistic Regression v1
- **Operational threshold:** 0.20
- **Serving path:** FastAPI on Amazon ECS
- **Monitoring:** CloudWatch contracts and incident response defined
- **Operational interface:** Athena-backed dashboard with human review
- **AutoML benchmark:** complete; DataRobot Elastic-Net α=0.5 led the verified holdout leaderboard
- **DataRobot deployment:** none
- **Data:** synthetic only

The next valid model-selection step would be a controlled challenger evaluation using the same frozen temporal partitions, feature availability rules, and operational acceptance criteria as the production champion.
