# ML Experiment Tracking - Model Card Template
# Demonstrates documentation practices for ML lifecycle management

## Model Overview

| Field              | Value                            |
|--------------------|----------------------------------|
| **Model Name**     | Order Demand Forecaster v2.1     |
| **Model Type**     | Gradient Boosted Decision Tree   |
| **Framework**      | scikit-learn 1.4.0               |
| **Task**           | Regression (demand forecasting)  |
| **Owner**          | Data Science Team                |
| **Last Updated**   | 2026-01-20                       |
| **Status**         | Production                       |

## Intended Use

- **Primary Use**: Predict next-week order volume per product category
- **Users**: Demand planning team, inventory management
- **Out of Scope**: Real-time pricing decisions, individual customer predictions

## Training Data

| Property            | Value                          |
|---------------------|--------------------------------|
| **Source**          | fact_orders warehouse table     |
| **Date Range**     | 2024-01-01 to 2025-12-31       |
| **Records**        | 1,247,832                       |
| **Features**       | 14 numeric, 6 categorical      |
| **Target**         | weekly_order_count              |
| **Train/Val/Test** | 70% / 15% / 15%                |

### Feature Importance (Top 5)

| Rank | Feature                | Importance |
|------|------------------------|------------|
| 1    | rolling_avg_4w         | 0.312      |
| 2    | day_of_week            | 0.187      |
| 3    | category_encoded       | 0.143      |
| 4    | promotional_flag       | 0.098      |
| 5    | seasonal_component     | 0.076      |

## Evaluation Metrics

| Metric   | Validation Set | Test Set | Production (30d) |
|----------|---------------|----------|-------------------|
| MAE      | 12.4          | 13.1     | 14.8              |
| RMSE     | 18.7          | 19.2     | 21.3              |
| MAPE     | 8.2%          | 8.9%     | 10.1%             |
| R-squared| 0.91          | 0.89     | 0.87              |

## Known Limitations

- Accuracy degrades for new product categories with less than 8 weeks of history
- Holiday periods (Black Friday, end-of-year) have higher error rates (MAPE > 15%)
- Model assumes stable pricing - accuracy drops after significant price changes

## Ethical Considerations

- No personally identifiable information (PII) used as features
- Model does not make decisions about individual customers
- Regional bias tested - performance consistent across all geographic regions

## Monitoring and Alerts

- **Data drift**: Kolmogorov-Smirnov test on feature distributions (weekly)
- **Performance drift**: MAPE monitored daily, alert if > 12% for 3 consecutive days
- **Retraining trigger**: Automatic retraining when monthly MAPE exceeds 11%
