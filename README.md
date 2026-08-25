# FinAI – AI-Powered Financial Intelligence System

## Project Overview

FinAI is an AI-powered financial intelligence system developed to support intelligent expense management, spending prediction, fraud detection, transaction analysis, receipt processing, and voice-based expense entry.

The system combines machine learning, OCR, voice input, transaction management, and real-time dashboard analytics within a unified platform.

The main objective of the project is to provide users with data-driven financial insights using historical transaction behaviour and trained machine learning models.

---

## Key Features

- Financial Intelligence Dashboard
- Smart Budget Prediction
- Behavioral Fraud Detection
- Transaction Amount Prediction
- Voice Expense Entry
- Receipt OCR Processing
- Transaction CRUD Operations
- Duplicate Transaction Detection
- Input Validation
- SQLite Transaction Storage
- Automatic AI Feature Encoding
- Live AI Insights
- Model Evaluation and Comparison

---

## Machine Learning Components

### 1. Smart Budget Prediction

The Smart Budget Prediction module forecasts the expected spending for the next week using historical transaction behaviour.

The production system uses a Gradient Boosting regression model.

Main input features include:

- Current week spending
- Previous weekly spending
- Previous 2-week average
- Previous 4-week average
- Previous 8-week average
- Transaction count
- Average transaction amount
- Fraud count
- Spending change
- Spending change percentage
- Seasonal week features

Model evaluation included:

- Linear Regression
- Ridge Regression
- Random Forest
- Extra Trees
- Gradient Boosting
- Hist Gradient Boosting
- Naive Forecast Baseline

### Budget Prediction Results

| Model | Test R² |
|---|---:|
| Current Gradient Boosting | 0.5997 |
| Linear Regression | 0.5885 |
| Naive Forecast | 0.5804 |
| Feature-Engineered Candidate | 0.6386 |

The feature-engineered candidate achieved the highest holdout R² score of approximately 0.6386.

However, the existing production Gradient Boosting model was retained because the candidate did not demonstrate sufficiently stable time-series cross-validation performance.

This decision prioritised model generalisation and reliability instead of selecting a model only using the highest holdout score.

---

## 2. Behavioral Fraud Detection

The fraud detection module analyses the latest transaction using a trained Random Forest classification model.

The system automatically encodes transaction information such as:

- Merchant
- Category
- Transaction amount
- Transaction behaviour

The fraud model generates:

- Fraud probability
- Fraud decision
- Risk level
- Decision explanation

The optimised fraud threshold used by the system is:

`0.45`

Transactions with a fraud probability equal to or greater than 45% are classified as suspicious.

---

## 3. Transaction Amount Prediction

The Amount Prediction module estimates the expected value of the next financial transaction.

The system uses a Random Forest regression model.

Prediction features include:

- Latest transaction amount
- Category
- Merchant
- Month
- Day
- Weekend indicator
- Merchant frequency
- Category average amount
- Payment-related feature values

The module uses the latest saved transaction together with historical transaction behaviour to generate the predicted amount.

---

## Receipt OCR

The Receipt OCR module allows users to upload receipt images.

The system uses EasyOCR to extract receipt information and converts it into structured transaction data.

Extracted fields include:

- Merchant
- Amount
- Date
- Category
- Raw OCR text

Users can review and edit OCR results before saving the transaction.

After confirmation, the transaction is stored in SQLite and becomes available to the financial intelligence and machine learning modules.

---

## Voice Expense Entry

The Voice Expense feature allows users to record or type a natural-language expense statement.

Example:

`I spent 1800 rupees at Dialog for utilities today`

The system extracts:

- Merchant
- Amount
- Transaction date
- Category

Users can review the extracted information before saving.

Saved voice transactions are automatically integrated with:

- Dashboard analytics
- Budget prediction
- Fraud detection
- Amount prediction

---

## End-to-End AI Integration

The system supports the following integrated pipelines:

### Receipt Pipeline

Receipt Image  
→ EasyOCR  
→ Extract Transaction Details  
→ User Confirmation  
→ SQLite Database  
→ Dashboard  
→ Budget Prediction  
→ Fraud Detection  
→ Amount Prediction

### Voice Pipeline

Voice Input  
→ Speech Transcript  
→ Expense Parsing  
→ User Confirmation  
→ SQLite Database  
→ Dashboard  
→ Budget Prediction  
→ Fraud Detection  
→ Amount Prediction

---

## Transaction Management

FinAI supports full CRUD operations:

- Create transaction
- Read transactions
- Update transaction
- Delete transaction

The system also includes:

- Duplicate transaction prevention
- Date validation
- Amount validation
- Merchant validation
- Category validation

Example validation responses include:

- Transaction amount must be greater than 0
- Merchant is required
- Category is required
- Transaction date must use DD/MM/YYYY format and must be a valid calendar date

---

## Dashboard

The Financial Intelligence Dashboard provides a unified view of saved transactions and AI-generated insights.

Dashboard information includes:

- Total saved spending
- Average expense
- Latest expense
- Top spending category
- Recent saved expenses
- Budget forecast
- Fraud risk
- Fraud decision
- Fraud probability
- Predicted transaction amount
- Integrated service status

---

## Model Evaluation Visualisations

Budget model evaluation includes:

- Actual vs Predicted Weekly Spending
- Feature Importance
- Residual Analysis
- Model Comparison

Generated graphs are stored in:

```text
backend/graphs/budget_model/