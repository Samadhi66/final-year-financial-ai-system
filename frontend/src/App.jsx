import { useState } from "react";
import "./App.css";

/* =========================================================
   REUSABLE INPUT FIELD
   ========================================================= */

function InputField({
  label,
  name,
  value,
  onChange,
  error,
  type = "number",
  step,
  min,
  max,
}) {
  return (
    <label>
      {label}

      <input
        type={type}
        name={name}
        value={value}
        onChange={onChange}
        step={step}
        min={min}
        max={max}
        style={
          error
            ? {
                borderColor: "#dc2626",
                boxShadow:
                  "0 0 0 3px rgba(220, 38, 38, 0.08)",
              }
            : undefined
        }
      />

      {error && (
        <span
          style={{
            color: "#dc2626",
            fontSize: "11px",
            fontWeight: "600",
            marginTop: "2px",
          }}
        >
          {error}
        </span>
      )}
    </label>
  );
}

/* =========================================================
   MAIN APPLICATION
   ========================================================= */

function App() {
  const [activePage, setActivePage] =
    useState("dashboard");

  /* =======================================================
     BUDGET STATE
     Keep inputs as strings so empty fields remain empty
     ======================================================= */

  const [budgetForm, setBudgetForm] = useState({
    week_sin: "0.5",
    week_cos: "0.866",

    current_week_spending: "175000",

    spending_1_week_ago: "172000",
    spending_2_weeks_ago: "170000",
    spending_3_weeks_ago: "168000",
    spending_4_weeks_ago: "171000",

    previous_2_week_avg: "171000",
    previous_4_week_avg: "170250",
    previous_8_week_avg: "169500",

    current_transaction_count: "35",
    current_avg_transaction_amount: "5000",
    current_fraud_count: "1",

    previous_transaction_count: "34",
    previous_avg_transaction_amount: "5058.82",

    spending_change: "2000",
    spending_change_percentage: "1.1765",
  });

  const [budgetResult, setBudgetResult] =
    useState(null);

  const [budgetLoading, setBudgetLoading] =
    useState(false);

  const [budgetError, setBudgetError] =
    useState("");

  const [budgetValidation, setBudgetValidation] =
    useState({});

  /* =======================================================
     FRAUD STATE
     ======================================================= */

  const [fraudForm, setFraudForm] = useState({
    amount: "4500",
    category: "1",
    merchant: "5",
    payment_method: "1",
    location: "2",
  });

  const [fraudResult, setFraudResult] =
    useState(null);

  const [fraudLoading, setFraudLoading] =
    useState(false);

  const [fraudError, setFraudError] =
    useState("");

  const [fraudValidation, setFraudValidation] =
    useState({});

  /* =======================================================
     AMOUNT PREDICTION STATE
     ======================================================= */

  const [amountForm, setAmountForm] = useState({
    category: "2",
    merchant: "10",
    payment_method: "1",
    location: "3",
    month: "8",
    day: "20",
    is_weekend: "0",
    category_avg_amount: "5500",
    merchant_frequency: "12",
    payment_impact: "1.1",
  });

  const [amountResult, setAmountResult] =
    useState(null);

  const [amountLoading, setAmountLoading] =
    useState(false);

  const [amountError, setAmountError] =
    useState("");

  const [amountValidation, setAmountValidation] =
    useState({});

  /* =======================================================
     INPUT CHANGE HANDLERS
     IMPORTANT: Do not convert to Number here
     ======================================================= */

  const handleBudgetChange = (event) => {
    const { name, value } = event.target;

    setBudgetForm((previous) => ({
      ...previous,
      [name]: value,
    }));

    setBudgetValidation((previous) => ({
      ...previous,
      [name]: "",
    }));
  };

  const handleFraudChange = (event) => {
    const { name, value } = event.target;

    setFraudForm((previous) => ({
      ...previous,
      [name]: value,
    }));

    setFraudValidation((previous) => ({
      ...previous,
      [name]: "",
    }));
  };

  const handleAmountChange = (event) => {
    const { name, value } = event.target;

    setAmountForm((previous) => ({
      ...previous,
      [name]: value,
    }));

    setAmountValidation((previous) => ({
      ...previous,
      [name]: "",
    }));
  };

  /* =======================================================
     NUMBER HELPERS
     ======================================================= */

  const isEmpty = (value) =>
    value === "" ||
    value === null ||
    value === undefined;

  const isValidNumber = (value) =>
    !isEmpty(value) &&
    Number.isFinite(Number(value));

  /* =======================================================
     BUDGET VALIDATION
     ======================================================= */

  const validateBudgetForm = () => {
    const errors = {};

    const requiredFields = [
      "week_sin",
      "week_cos",
      "current_week_spending",
      "spending_1_week_ago",
      "spending_2_weeks_ago",
      "spending_3_weeks_ago",
      "spending_4_weeks_ago",
      "previous_2_week_avg",
      "previous_4_week_avg",
      "previous_8_week_avg",
      "current_transaction_count",
      "current_avg_transaction_amount",
      "current_fraud_count",
      "previous_transaction_count",
      "previous_avg_transaction_amount",
      "spending_change",
      "spending_change_percentage",
    ];

    requiredFields.forEach((field) => {
      if (!isValidNumber(budgetForm[field])) {
        errors[field] =
          "This field is required and must be a valid number.";
      }
    });

    if (
      isValidNumber(
        budgetForm.current_week_spending
      ) &&
      Number(
        budgetForm.current_week_spending
      ) <= 0
    ) {
      errors.current_week_spending =
        "Current week spending must be greater than 0.";
    }

    const nonNegativeFields = [
      "spending_1_week_ago",
      "spending_2_weeks_ago",
      "spending_3_weeks_ago",
      "spending_4_weeks_ago",
      "previous_2_week_avg",
      "previous_4_week_avg",
      "previous_8_week_avg",
      "current_transaction_count",
      "current_avg_transaction_amount",
      "current_fraud_count",
      "previous_transaction_count",
      "previous_avg_transaction_amount",
    ];

    nonNegativeFields.forEach((field) => {
      if (
        isValidNumber(budgetForm[field]) &&
        Number(budgetForm[field]) < 0
      ) {
        errors[field] =
          "Negative values are not allowed.";
      }
    });

    if (
      isValidNumber(
        budgetForm.current_avg_transaction_amount
      ) &&
      Number(
        budgetForm.current_avg_transaction_amount
      ) <= 0
    ) {
      errors.current_avg_transaction_amount =
        "Average transaction amount must be greater than 0.";
    }

    if (
      isValidNumber(
        budgetForm.previous_avg_transaction_amount
      ) &&
      Number(
        budgetForm.previous_avg_transaction_amount
      ) <= 0
    ) {
      errors.previous_avg_transaction_amount =
        "Previous average transaction amount must be greater than 0.";
    }

    if (
      isValidNumber(
        budgetForm.current_transaction_count
      ) &&
      !Number.isInteger(
        Number(
          budgetForm.current_transaction_count
        )
      )
    ) {
      errors.current_transaction_count =
        "Transaction count must be a whole number.";
    }

    if (
      isValidNumber(
        budgetForm.previous_transaction_count
      ) &&
      !Number.isInteger(
        Number(
          budgetForm.previous_transaction_count
        )
      )
    ) {
      errors.previous_transaction_count =
        "Transaction count must be a whole number.";
    }

    if (
      isValidNumber(
        budgetForm.current_fraud_count
      ) &&
      !Number.isInteger(
        Number(
          budgetForm.current_fraud_count
        )
      )
    ) {
      errors.current_fraud_count =
        "Fraud count must be a whole number.";
    }

    if (
      isValidNumber(
        budgetForm.current_fraud_count
      ) &&
      isValidNumber(
        budgetForm.current_transaction_count
      ) &&
      Number(
        budgetForm.current_fraud_count
      ) >
        Number(
          budgetForm.current_transaction_count
        )
    ) {
      errors.current_fraud_count =
        "Fraud count cannot exceed transaction count.";
    }

    if (
      isValidNumber(budgetForm.week_sin) &&
      (
        Number(budgetForm.week_sin) < -1 ||
        Number(budgetForm.week_sin) > 1
      )
    ) {
      errors.week_sin =
        "Week Sin must be between -1 and 1.";
    }

    if (
      isValidNumber(budgetForm.week_cos) &&
      (
        Number(budgetForm.week_cos) < -1 ||
        Number(budgetForm.week_cos) > 1
      )
    ) {
      errors.week_cos =
        "Week Cos must be between -1 and 1.";
    }

    setBudgetValidation(errors);

    return Object.keys(errors).length === 0;
  };

  /* =======================================================
     FRAUD VALIDATION
     ======================================================= */

  const validateFraudForm = () => {
    const errors = {};

    Object.entries(fraudForm).forEach(
      ([field, value]) => {
        if (!isValidNumber(value)) {
          errors[field] =
            "This field is required.";
        }
      }
    );

    if (
      isValidNumber(fraudForm.amount) &&
      Number(fraudForm.amount) <= 0
    ) {
      errors.amount =
        "Transaction amount must be greater than 0.";
    }

    const codeFields = [
      "category",
      "merchant",
      "payment_method",
      "location",
    ];

    codeFields.forEach((field) => {
      if (
        isValidNumber(fraudForm[field]) &&
        Number(fraudForm[field]) < 0
      ) {
        errors[field] =
          "Code cannot be negative.";
      }

      if (
        isValidNumber(fraudForm[field]) &&
        !Number.isInteger(
          Number(fraudForm[field])
        )
      ) {
        errors[field] =
          "Code must be a whole number.";
      }
    });

    setFraudValidation(errors);

    return Object.keys(errors).length === 0;
  };

  /* =======================================================
     AMOUNT VALIDATION
     ======================================================= */

  const validateAmountForm = () => {
    const errors = {};

    Object.entries(amountForm).forEach(
      ([field, value]) => {
        if (!isValidNumber(value)) {
          errors[field] =
            "This field is required.";
        }
      }
    );

    const codeFields = [
      "category",
      "merchant",
      "payment_method",
      "location",
    ];

    codeFields.forEach((field) => {
      if (
        isValidNumber(amountForm[field]) &&
        Number(amountForm[field]) < 0
      ) {
        errors[field] =
          "Code cannot be negative.";
      }

      if (
        isValidNumber(amountForm[field]) &&
        !Number.isInteger(
          Number(amountForm[field])
        )
      ) {
        errors[field] =
          "Code must be a whole number.";
      }
    });

    if (
      isValidNumber(amountForm.month) &&
      (
        Number(amountForm.month) < 1 ||
        Number(amountForm.month) > 12
      )
    ) {
      errors.month =
        "Month must be between 1 and 12.";
    }

    if (
      isValidNumber(amountForm.day) &&
      (
        Number(amountForm.day) < 1 ||
        Number(amountForm.day) > 31
      )
    ) {
      errors.day =
        "Day must be between 1 and 31.";
    }

    if (
      isValidNumber(
        amountForm.category_avg_amount
      ) &&
      Number(
        amountForm.category_avg_amount
      ) <= 0
    ) {
      errors.category_avg_amount =
        "Category average amount must be greater than 0.";
    }

    if (
      isValidNumber(
        amountForm.merchant_frequency
      ) &&
      Number(
        amountForm.merchant_frequency
      ) < 0
    ) {
      errors.merchant_frequency =
        "Merchant frequency cannot be negative.";
    }

    if (
      isValidNumber(
        amountForm.merchant_frequency
      ) &&
      !Number.isInteger(
        Number(
          amountForm.merchant_frequency
        )
      )
    ) {
      errors.merchant_frequency =
        "Merchant frequency must be a whole number.";
    }

    if (
      isValidNumber(
        amountForm.payment_impact
      ) &&
      Number(
        amountForm.payment_impact
      ) <= 0
    ) {
      errors.payment_impact =
        "Payment impact must be greater than 0.";
    }

    setAmountValidation(errors);

    return Object.keys(errors).length === 0;
  };

  /* =======================================================
     BUDGET API
     ======================================================= */

  const handleBudgetPrediction = async (
    event
  ) => {
    event.preventDefault();

    setBudgetError("");

    if (!validateBudgetForm()) {
      setBudgetResult(null);

      setBudgetError(
        "Please correct the highlighted input values before generating a prediction."
      );

      return;
    }

    const payload = Object.fromEntries(
      Object.entries(budgetForm).map(
        ([key, value]) => [
          key,
          Number(value),
        ]
      )
    );

    setBudgetLoading(true);
    setBudgetResult(null);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/predict_budget",
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",
          },

          body: JSON.stringify(payload),
        }
      );

      if (!response.ok) {
        throw new Error(
          `Server returned ${response.status}`
        );
      }

      const result =
        await response.json();

      if (
        result.status === "Error" ||
        result.status === "Unavailable"
      ) {
        throw new Error(
          result.message ||
            result.error ||
            "Budget prediction failed"
        );
      }

      setBudgetResult(result);
    } catch (error) {
      console.error(error);

      setBudgetError(
        "Budget prediction could not be completed. Please check that the FastAPI server is running."
      );
    } finally {
      setBudgetLoading(false);
    }
  };

  /* =======================================================
     FRAUD API
     ======================================================= */

  const handleFraudDetection = async (
    event
  ) => {
    event.preventDefault();

    setFraudError("");

    if (!validateFraudForm()) {
      setFraudResult(null);

      setFraudError(
        "Please correct the highlighted transaction values before analysing fraud risk."
      );

      return;
    }

    const payload = Object.fromEntries(
      Object.entries(fraudForm).map(
        ([key, value]) => [
          key,
          Number(value),
        ]
      )
    );

    setFraudLoading(true);
    setFraudResult(null);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/detect_fraud",
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",
          },

          body: JSON.stringify(payload),
        }
      );

      if (!response.ok) {
        throw new Error(
          `Server returned ${response.status}`
        );
      }

      const result =
        await response.json();

      if (
        result.status === "Error" ||
        result.status === "Unavailable"
      ) {
        throw new Error(
          result.error ||
            result.message ||
            "Fraud detection failed"
        );
      }

      setFraudResult(result);
    } catch (error) {
      console.error(error);

      setFraudError(
        "Fraud detection could not be completed. Please check that the FastAPI server is running."
      );
    } finally {
      setFraudLoading(false);
    }
  };

  /* =======================================================
     AMOUNT API
     ======================================================= */

  const handleAmountPrediction = async (
    event
  ) => {
    event.preventDefault();

    setAmountError("");

    if (!validateAmountForm()) {
      setAmountResult(null);

      setAmountError(
        "Please correct the highlighted input values before generating an amount prediction."
      );

      return;
    }

    const payload = Object.fromEntries(
      Object.entries(amountForm).map(
        ([key, value]) => [
          key,
          Number(value),
        ]
      )
    );

    setAmountLoading(true);
    setAmountResult(null);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/predict_amount",
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",
          },

          body: JSON.stringify(payload),
        }
      );

      if (!response.ok) {
        throw new Error(
          `Server returned ${response.status}`
        );
      }

      const result =
        await response.json();

      if (
        result.status === "Unavailable" ||
        result.status === "Error"
      ) {
        throw new Error(
          result.error ||
            result.message ||
            "Amount prediction failed"
        );
      }

      setAmountResult(result);
    } catch (error) {
      console.error(error);

      setAmountError(
        "Amount prediction could not be completed. Please check that the FastAPI server is running."
      );
    } finally {
      setAmountLoading(false);
    }
  };

  /* =======================================================
     DASHBOARD
     ======================================================= */

  const renderDashboard = () => {
    const latestBudget =
      budgetResult
        ?.predicted_next_week_spending ??
      null;

    const latestFraudProbability =
      fraudResult?.fraud_probability ??
      null;

    const latestFraudStatus =
      fraudResult?.fraud_status ??
      "Not Analysed";

    const latestAmount =
      amountResult?.predicted_amount ??
      null;

    return (
      <>
        <header>
          <div>
            <p className="eyebrow">
              AI-POWERED FINANCE
            </p>

            <h1>
              Financial Intelligence Dashboard
            </h1>

            <p className="subtitle">
              Unified view of smart budget
              forecasts, transaction estimates
              and behavioral fraud risk.
            </p>
          </div>

          <div className="system-status">
            <span className="status-dot"></span>
            All AI Models Active
          </div>
        </header>

        <section className="dashboard-kpis">
          <div
            className="kpi-card"
            onClick={() =>
              setActivePage("budget")
            }
          >
            <div className="kpi-top">
              <span className="kpi-icon">
                ◈
              </span>

              <span className="kpi-label">
                Next Week Forecast
              </span>
            </div>

            <h3>
              {latestBudget !== null
                ? `Rs. ${Number(
                    latestBudget
                  ).toLocaleString()}`
                : "No prediction"}
            </h3>

            <p>
              {budgetResult
                ? budgetResult.trend
                : "Run budget prediction"}
            </p>
          </div>

          <div
            className="kpi-card"
            onClick={() =>
              setActivePage("fraud")
            }
          >
            <div className="kpi-top">
              <span className="kpi-icon">
                ◎
              </span>

              <span className="kpi-label">
                Fraud Risk
              </span>
            </div>

            <h3>
              {latestFraudProbability !==
              null
                ? `${(
                    Number(
                      latestFraudProbability
                    ) * 100
                  ).toFixed(1)}%`
                : "No analysis"}
            </h3>

            <p>
              {latestFraudStatus}
            </p>
          </div>

          <div
            className="kpi-card"
            onClick={() =>
              setActivePage("amount")
            }
          >
            <div className="kpi-top">
              <span className="kpi-icon">
                ↗
              </span>

              <span className="kpi-label">
                Predicted Amount
              </span>
            </div>

            <h3>
              {latestAmount !== null
                ? `Rs. ${Number(
                    latestAmount
                  ).toLocaleString()}`
                : "No estimate"}
            </h3>

            <p>
              Smart transaction estimate
            </p>
          </div>

          <div className="kpi-card model-health-card">
            <div className="kpi-top">
              <span className="kpi-icon">
                AI
              </span>

              <span className="kpi-label">
                Model Health
              </span>
            </div>

            <h3>
              3 / 3 Active
            </h3>

            <p>
              All prediction services available
            </p>
          </div>
        </section>

        <section className="dashboard-grid">
          <div className="dashboard-panel">
            <div className="panel-heading">
              <p className="eyebrow">
                RECENT AI INSIGHTS
              </p>

              <h2>
                Decision Support Summary
              </h2>
            </div>

            <div className="insight-list">
              <div className="insight-item">
                <span className="insight-dot blue"></span>

                <div>
                  <strong>
                    Budget Forecast
                  </strong>

                  <p>
                    {budgetResult
                      ? budgetResult.explanation
                      : "Generate a budget forecast to view AI spending insights."}
                  </p>
                </div>
              </div>

              <div className="insight-item">
                <span
                  className={`insight-dot ${
                    fraudResult
                      ?.fraud_status ===
                    "Fraud Detected"
                      ? "red"
                      : "green"
                  }`}
                ></span>

                <div>
                  <strong>
                    Fraud Intelligence
                  </strong>

                  <p>
                    {fraudResult
                      ? `${fraudResult.fraud_status} with ${(
                          Number(
                            fraudResult.fraud_probability
                          ) * 100
                        ).toFixed(
                          1
                        )}% fraud probability.`
                      : "Analyse a transaction to receive behavioral fraud intelligence."}
                  </p>
                </div>
              </div>

              <div className="insight-item">
                <span className="insight-dot purple"></span>

                <div>
                  <strong>
                    Transaction Estimate
                  </strong>

                  <p>
                    {amountResult
                      ? `Expected transaction amount is approximately Rs. ${Number(
                          amountResult.predicted_amount
                        ).toLocaleString()}.`
                      : "Run amount prediction to generate a smart transaction estimate."}
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="dashboard-panel system-panel">
            <p className="eyebrow">
              SYSTEM OVERVIEW
            </p>

            <h2>
              AI Model Status
            </h2>

            <div className="model-status-list">
              <div>
                <span>
                  Gradient Boosting
                </span>

                <strong className="online-text">
                  Online
                </strong>
              </div>

              <div>
                <span>
                  Random Forest Fraud Model
                </span>

                <strong className="online-text">
                  Online
                </strong>
              </div>

              <div>
                <span>
                  Amount Prediction Model
                </span>

                <strong className="online-text">
                  Online
                </strong>
              </div>
            </div>

            <div className="system-score">
              <span>
                Integrated AI Services
              </span>

              <strong>
                100%
              </strong>
            </div>
          </div>
        </section>
      </>
    );
  };

  /* =======================================================
     BUDGET PAGE
     ======================================================= */

  const renderBudgetPrediction = () => {
    return (
      <>
        <header>
          <div>
            <p className="eyebrow">
              SMART BUDGET FORECASTING
            </p>

            <h1>
              Budget Prediction
            </h1>

            <p className="subtitle">
              Predict next week's spending using
              the trained Gradient Boosting model.
            </p>
          </div>

          <div className="system-status">
            <span className="status-dot"></span>
            Model Ready
          </div>
        </header>

        <div className="prediction-layout">
          <section className="prediction-form-card">
            <div className="section-heading">
              <div>
                <p className="eyebrow">
                  INPUT DATA
                </p>

                <h2>
                  Financial Behaviour
                </h2>
              </div>

              <span className="model-chip">
                Gradient Boosting
              </span>
            </div>

            <form
              className="prediction-form"
              onSubmit={
                handleBudgetPrediction
              }
            >
              <div className="form-section">
                <h3>
                  Current Spending
                </h3>

                <div className="form-grid">
                  <InputField
                    label="Current Week Spending"
                    name="current_week_spending"
                    value={
                      budgetForm.current_week_spending
                    }
                    onChange={
                      handleBudgetChange
                    }
                    error={
                      budgetValidation.current_week_spending
                    }
                  />

                  <InputField
                    label="Current Transaction Count"
                    name="current_transaction_count"
                    value={
                      budgetForm.current_transaction_count
                    }
                    onChange={
                      handleBudgetChange
                    }
                    error={
                      budgetValidation.current_transaction_count
                    }
                    min="0"
                  />

                  <InputField
                    label="Average Transaction Amount"
                    name="current_avg_transaction_amount"
                    value={
                      budgetForm.current_avg_transaction_amount
                    }
                    onChange={
                      handleBudgetChange
                    }
                    error={
                      budgetValidation.current_avg_transaction_amount
                    }
                  />

                  <InputField
                    label="Current Fraud Count"
                    name="current_fraud_count"
                    value={
                      budgetForm.current_fraud_count
                    }
                    onChange={
                      handleBudgetChange
                    }
                    error={
                      budgetValidation.current_fraud_count
                    }
                    min="0"
                  />
                </div>
              </div>

              <div className="form-section">
                <h3>
                  Historical Spending
                </h3>

                <div className="form-grid">
                  <InputField
                    label="1 Week Ago"
                    name="spending_1_week_ago"
                    value={
                      budgetForm.spending_1_week_ago
                    }
                    onChange={
                      handleBudgetChange
                    }
                    error={
                      budgetValidation.spending_1_week_ago
                    }
                  />

                  <InputField
                    label="2 Weeks Ago"
                    name="spending_2_weeks_ago"
                    value={
                      budgetForm.spending_2_weeks_ago
                    }
                    onChange={
                      handleBudgetChange
                    }
                    error={
                      budgetValidation.spending_2_weeks_ago
                    }
                  />

                  <InputField
                    label="3 Weeks Ago"
                    name="spending_3_weeks_ago"
                    value={
                      budgetForm.spending_3_weeks_ago
                    }
                    onChange={
                      handleBudgetChange
                    }
                    error={
                      budgetValidation.spending_3_weeks_ago
                    }
                  />

                  <InputField
                    label="4 Weeks Ago"
                    name="spending_4_weeks_ago"
                    value={
                      budgetForm.spending_4_weeks_ago
                    }
                    onChange={
                      handleBudgetChange
                    }
                    error={
                      budgetValidation.spending_4_weeks_ago
                    }
                  />
                </div>
              </div>

              <div className="form-section">
                <h3>
                  Rolling Behaviour
                </h3>

                <div className="form-grid">
                  <InputField
                    label="Previous 2 Week Average"
                    name="previous_2_week_avg"
                    value={
                      budgetForm.previous_2_week_avg
                    }
                    onChange={
                      handleBudgetChange
                    }
                    error={
                      budgetValidation.previous_2_week_avg
                    }
                  />

                  <InputField
                    label="Previous 4 Week Average"
                    name="previous_4_week_avg"
                    value={
                      budgetForm.previous_4_week_avg
                    }
                    onChange={
                      handleBudgetChange
                    }
                    error={
                      budgetValidation.previous_4_week_avg
                    }
                  />

                  <InputField
                    label="Previous 8 Week Average"
                    name="previous_8_week_avg"
                    value={
                      budgetForm.previous_8_week_avg
                    }
                    onChange={
                      handleBudgetChange
                    }
                    error={
                      budgetValidation.previous_8_week_avg
                    }
                  />

                  <InputField
                    label="Previous Transaction Count"
                    name="previous_transaction_count"
                    value={
                      budgetForm.previous_transaction_count
                    }
                    onChange={
                      handleBudgetChange
                    }
                    error={
                      budgetValidation.previous_transaction_count
                    }
                  />

                  <InputField
                    label="Previous Avg Transaction"
                    name="previous_avg_transaction_amount"
                    value={
                      budgetForm.previous_avg_transaction_amount
                    }
                    onChange={
                      handleBudgetChange
                    }
                    error={
                      budgetValidation.previous_avg_transaction_amount
                    }
                    step="0.01"
                  />
                </div>
              </div>

              <div className="form-section">
                <h3>
                  Trend & Seasonality
                </h3>

                <div className="form-grid">
                  <InputField
                    label="Spending Change"
                    name="spending_change"
                    value={
                      budgetForm.spending_change
                    }
                    onChange={
                      handleBudgetChange
                    }
                    error={
                      budgetValidation.spending_change
                    }
                  />

                  <InputField
                    label="Spending Change %"
                    name="spending_change_percentage"
                    value={
                      budgetForm.spending_change_percentage
                    }
                    onChange={
                      handleBudgetChange
                    }
                    error={
                      budgetValidation.spending_change_percentage
                    }
                    step="0.0001"
                  />

                  <InputField
                    label="Week Sin"
                    name="week_sin"
                    value={
                      budgetForm.week_sin
                    }
                    onChange={
                      handleBudgetChange
                    }
                    error={
                      budgetValidation.week_sin
                    }
                    step="0.001"
                    min="-1"
                    max="1"
                  />

                  <InputField
                    label="Week Cos"
                    name="week_cos"
                    value={
                      budgetForm.week_cos
                    }
                    onChange={
                      handleBudgetChange
                    }
                    error={
                      budgetValidation.week_cos
                    }
                    step="0.001"
                    min="-1"
                    max="1"
                  />
                </div>
              </div>

              {budgetError && (
                <div className="error-box">
                  {budgetError}
                </div>
              )}

              <button
                type="submit"
                className="primary-button"
                disabled={budgetLoading}
              >
                {budgetLoading
                  ? "Generating Prediction..."
                  : "Generate Budget Prediction"}
              </button>
            </form>
          </section>

          <section className="prediction-result-card">
            <p className="eyebrow">
              AI RESULT
            </p>

            <h2>
              Forecast Summary
            </h2>

            {!budgetResult && (
              <div className="result-placeholder">
                <div className="result-icon">
                  AI
                </div>

                <h3>
                  Ready to Predict
                </h3>

                <p>
                  Enter valid financial behaviour
                  information to generate an
                  AI-powered budget forecast.
                </p>
              </div>
            )}

            {budgetResult && (
              <div className="result-content">
                <div className="result-highlight">
                  <p>
                    Predicted Next Week
                  </p>

                  <h3>
                    Rs.{" "}
                    {Number(
                      budgetResult.predicted_next_week_spending
                    ).toLocaleString()}
                  </h3>
                </div>

                <div className="result-stat-grid">
                  <div>
                    <span>
                      Current Spending
                    </span>

                    <strong>
                      Rs.{" "}
                      {Number(
                        budgetResult.current_week_spending
                      ).toLocaleString()}
                    </strong>
                  </div>

                  <div>
                    <span>
                      Difference
                    </span>

                    <strong>
                      Rs.{" "}
                      {Number(
                        budgetResult.predicted_difference
                      ).toLocaleString()}
                    </strong>
                  </div>

                  <div>
                    <span>
                      Change
                    </span>

                    <strong>
                      {budgetResult.percentage_change}%
                    </strong>
                  </div>

                  <div>
                    <span>
                      Model R²
                    </span>

                    <strong>
                      {budgetResult.model_r2}
                    </strong>
                  </div>
                </div>

                <div
                  className={`trend-badge ${
                    budgetResult.trend ===
                    "Expected Increase"
                      ? "increase"
                      : budgetResult.trend ===
                        "Expected Decrease"
                      ? "decrease"
                      : "stable"
                  }`}
                >
                  {budgetResult.trend}
                </div>

                <div className="explanation-box">
                  <span>
                    AI Explanation
                  </span>

                  <p>
                    {budgetResult.explanation}
                  </p>
                </div>
              </div>
            )}
          </section>
        </div>
      </>
    );
  };

  /* =======================================================
     FRAUD PAGE
     ======================================================= */

  const renderFraudDetection = () => {
    return (
      <>
        <header>
          <div>
            <p className="eyebrow">
              BEHAVIORAL FRAUD INTELLIGENCE
            </p>

            <h1>
              Fraud Detection
            </h1>

            <p className="subtitle">
              Analyse transaction behaviour
              using the trained Random Forest
              fraud detection model.
            </p>
          </div>

          <div className="system-status">
            <span className="status-dot"></span>
            Fraud Model Ready
          </div>
        </header>

        <div className="prediction-layout">
          <section className="prediction-form-card">
            <div className="section-heading">
              <div>
                <p className="eyebrow">
                  TRANSACTION INPUT
                </p>

                <h2>
                  Transaction Details
                </h2>
              </div>

              <span className="model-chip">
                Random Forest
              </span>
            </div>

            <form
              onSubmit={
                handleFraudDetection
              }
            >
              <div className="form-section">
                <h3>
                  Financial Transaction
                </h3>

                <div className="form-grid">
                  <InputField
                    label="Transaction Amount"
                    name="amount"
                    value={
                      fraudForm.amount
                    }
                    onChange={
                      handleFraudChange
                    }
                    error={
                      fraudValidation.amount
                    }
                  />

                  <InputField
                    label="Category Code"
                    name="category"
                    value={
                      fraudForm.category
                    }
                    onChange={
                      handleFraudChange
                    }
                    error={
                      fraudValidation.category
                    }
                  />

                  <InputField
                    label="Merchant Code"
                    name="merchant"
                    value={
                      fraudForm.merchant
                    }
                    onChange={
                      handleFraudChange
                    }
                    error={
                      fraudValidation.merchant
                    }
                  />

                  <InputField
                    label="Payment Method Code"
                    name="payment_method"
                    value={
                      fraudForm.payment_method
                    }
                    onChange={
                      handleFraudChange
                    }
                    error={
                      fraudValidation.payment_method
                    }
                  />

                  <InputField
                    label="Location Code"
                    name="location"
                    value={
                      fraudForm.location
                    }
                    onChange={
                      handleFraudChange
                    }
                    error={
                      fraudValidation.location
                    }
                  />
                </div>
              </div>

              <div className="fraud-info-box">
                <span>
                  Optimized Fraud Threshold
                </span>

                <strong>
                  0.45
                </strong>

                <p>
                  Transactions with an AI fraud
                  probability equal to or above
                  45% are classified as suspicious.
                </p>
              </div>

              {fraudError && (
                <div className="error-box">
                  {fraudError}
                </div>
              )}

              <button
                type="submit"
                className="primary-button"
                disabled={fraudLoading}
              >
                {fraudLoading
                  ? "Analysing Transaction..."
                  : "Analyse Fraud Risk"}
              </button>
            </form>
          </section>

          <section className="prediction-result-card">
            <p className="eyebrow">
              AI RISK ANALYSIS
            </p>

            <h2>
              Fraud Assessment
            </h2>

            {!fraudResult && (
              <div className="result-placeholder">
                <div className="result-icon">
                  AI
                </div>

                <h3>
                  Ready to Analyse
                </h3>

                <p>
                  Enter valid transaction
                  details to receive an
                  AI-powered fraud assessment.
                </p>
              </div>
            )}

            {fraudResult && (
              <div className="result-content">
                <div
                  className={`fraud-result-banner ${
                    fraudResult.fraud_status ===
                    "Fraud Detected"
                      ? "fraud"
                      : "normal"
                  }`}
                >
                  <span>
                    AI Decision
                  </span>

                  <h3>
                    {fraudResult.fraud_status}
                  </h3>

                  <p>
                    {fraudResult.risk_level} Risk
                  </p>
                </div>

                <div className="result-stat-grid">
                  <div>
                    <span>
                      Fraud Probability
                    </span>

                    <strong>
                      {(
                        Number(
                          fraudResult.fraud_probability
                        ) * 100
                      ).toFixed(2)}
                      %
                    </strong>
                  </div>

                  <div>
                    <span>
                      Decision Threshold
                    </span>

                    <strong>
                      {(
                        Number(
                          fraudResult.threshold
                        ) * 100
                      ).toFixed(0)}
                      %
                    </strong>
                  </div>

                  <div>
                    <span>
                      Risk Level
                    </span>

                    <strong>
                      {fraudResult.risk_level}
                    </strong>
                  </div>

                  <div>
                    <span>
                      Model
                    </span>

                    <strong>
                      Random Forest
                    </strong>
                  </div>
                </div>

                <div
                  className={`risk-badge ${
                    fraudResult.risk_level?.toLowerCase()
                  }`}
                >
                  {fraudResult.risk_level} Risk
                </div>

                <div className="explanation-box">
                  <span>
                    Why was this decision made?
                  </span>

                  <ul className="risk-reason-list">
                    {fraudResult.risk_reasons?.map(
                      (
                        reason,
                        index
                      ) => (
                        <li key={index}>
                          {reason}
                        </li>
                      )
                    )}
                  </ul>
                </div>

                <div className="probability-panel">
                  <div className="probability-heading">
                    <span>
                      Fraud Probability
                    </span>

                    <strong>
                      {(
                        Number(
                          fraudResult.fraud_probability
                        ) * 100
                      ).toFixed(1)}
                      %
                    </strong>
                  </div>

                  <div className="probability-track">
                    <div
                      className={`probability-fill ${
                        fraudResult.fraud_status ===
                        "Fraud Detected"
                          ? "danger"
                          : "safe"
                      }`}
                      style={{
                        width: `${Math.min(
                          Number(
                            fraudResult.fraud_probability
                          ) * 100,
                          100
                        )}%`,
                      }}
                    />

                    <div
                      className="threshold-marker"
                      style={{
                        left: `${
                          Number(
                            fraudResult.threshold
                          ) * 100
                        }%`,
                      }}
                    />
                  </div>

                  <div className="probability-labels">
                    <span>
                      0%
                    </span>

                    <span>
                      Threshold 45%
                    </span>

                    <span>
                      100%
                    </span>
                  </div>
                </div>
              </div>
            )}
          </section>
        </div>
      </>
    );
  };

  /* =======================================================
     AMOUNT PAGE
     ======================================================= */

  const renderAmountPrediction = () => {
    return (
      <>
        <header>
          <div>
            <p className="eyebrow">
              SMART TRANSACTION ESTIMATION
            </p>

            <h1>
              Amount Prediction
            </h1>

            <p className="subtitle">
              Estimate a transaction amount
              using historical financial
              behaviour and machine learning.
            </p>
          </div>

          <div className="system-status">
            <span className="status-dot"></span>
            Prediction Model Ready
          </div>
        </header>

        <div className="prediction-layout">
          <section className="prediction-form-card">
            <div className="section-heading">
              <div>
                <p className="eyebrow">
                  TRANSACTION FEATURES
                </p>

                <h2>
                  Prediction Inputs
                </h2>
              </div>

              <span className="model-chip">
                Random Forest
              </span>
            </div>

            <form
              onSubmit={
                handleAmountPrediction
              }
            >
              <div className="form-section">
                <h3>
                  Transaction Information
                </h3>

                <div className="form-grid">
                  <InputField
                    label="Category Code"
                    name="category"
                    value={
                      amountForm.category
                    }
                    onChange={
                      handleAmountChange
                    }
                    error={
                      amountValidation.category
                    }
                  />

                  <InputField
                    label="Merchant Code"
                    name="merchant"
                    value={
                      amountForm.merchant
                    }
                    onChange={
                      handleAmountChange
                    }
                    error={
                      amountValidation.merchant
                    }
                  />

                  <InputField
                    label="Payment Method Code"
                    name="payment_method"
                    value={
                      amountForm.payment_method
                    }
                    onChange={
                      handleAmountChange
                    }
                    error={
                      amountValidation.payment_method
                    }
                  />

                  <InputField
                    label="Location Code"
                    name="location"
                    value={
                      amountForm.location
                    }
                    onChange={
                      handleAmountChange
                    }
                    error={
                      amountValidation.location
                    }
                  />
                </div>
              </div>

              <div className="form-section">
                <h3>
                  Time Behaviour
                </h3>

                <div className="form-grid">
                  <InputField
                    label="Month"
                    name="month"
                    value={
                      amountForm.month
                    }
                    onChange={
                      handleAmountChange
                    }
                    error={
                      amountValidation.month
                    }
                    min="1"
                    max="12"
                  />

                  <InputField
                    label="Day"
                    name="day"
                    value={
                      amountForm.day
                    }
                    onChange={
                      handleAmountChange
                    }
                    error={
                      amountValidation.day
                    }
                    min="1"
                    max="31"
                  />

                  <label>
                    Is Weekend

                    <select
                      name="is_weekend"
                      value={
                        amountForm.is_weekend
                      }
                      onChange={
                        handleAmountChange
                      }
                    >
                      <option value="0">
                        No
                      </option>

                      <option value="1">
                        Yes
                      </option>
                    </select>
                  </label>
                </div>
              </div>

              <div className="form-section">
                <h3>
                  Behavioral Features
                </h3>

                <div className="form-grid">
                  <InputField
                    label="Category Average Amount"
                    name="category_avg_amount"
                    value={
                      amountForm.category_avg_amount
                    }
                    onChange={
                      handleAmountChange
                    }
                    error={
                      amountValidation.category_avg_amount
                    }
                    step="0.01"
                  />

                  <InputField
                    label="Merchant Frequency"
                    name="merchant_frequency"
                    value={
                      amountForm.merchant_frequency
                    }
                    onChange={
                      handleAmountChange
                    }
                    error={
                      amountValidation.merchant_frequency
                    }
                  />

                  <InputField
                    label="Payment Impact"
                    name="payment_impact"
                    value={
                      amountForm.payment_impact
                    }
                    onChange={
                      handleAmountChange
                    }
                    error={
                      amountValidation.payment_impact
                    }
                    step="0.01"
                  />
                </div>
              </div>

              {amountError && (
                <div className="error-box">
                  {amountError}
                </div>
              )}

              <button
                type="submit"
                className="primary-button"
                disabled={amountLoading}
              >
                {amountLoading
                  ? "Generating Estimate..."
                  : "Predict Transaction Amount"}
              </button>
            </form>
          </section>

          <section className="prediction-result-card">
            <p className="eyebrow">
              AI ESTIMATE
            </p>

            <h2>
              Amount Prediction
            </h2>

            {!amountResult && (
              <div className="result-placeholder">
                <div className="result-icon">
                  AI
                </div>

                <h3>
                  Ready to Estimate
                </h3>

                <p>
                  Enter valid transaction
                  behaviour information to
                  generate an AI-powered estimate.
                </p>
              </div>
            )}

            {amountResult && (
              <div className="result-content">
                <div className="result-highlight">
                  <p>
                    Predicted Transaction Amount
                  </p>

                  <h3>
                    Rs.{" "}
                    {Number(
                      amountResult.predicted_amount
                    ).toLocaleString()}
                  </h3>
                </div>

                <div className="amount-summary">
                  <div>
                    <span>
                      Category
                    </span>

                    <strong>
                      {amountForm.category}
                    </strong>
                  </div>

                  <div>
                    <span>
                      Merchant
                    </span>

                    <strong>
                      {amountForm.merchant}
                    </strong>
                  </div>

                  <div>
                    <span>
                      Payment Method
                    </span>

                    <strong>
                      {
                        amountForm.payment_method
                      }
                    </strong>
                  </div>

                  <div>
                    <span>
                      Location
                    </span>

                    <strong>
                      {amountForm.location}
                    </strong>
                  </div>
                </div>

                <div className="explanation-box">
                  <span>
                    AI Estimate
                  </span>

                  <p>
                    Based on the supplied
                    transaction and behavioural
                    features, the model predicts
                    an expected transaction
                    amount of{" "}
                    <strong>
                      Rs.{" "}
                      {Number(
                        amountResult.predicted_amount
                      ).toLocaleString()}
                    </strong>
                    .
                  </p>
                </div>
              </div>
            )}
          </section>
        </div>
      </>
    );
  };

  /* =======================================================
     PAGE ROUTING
     ======================================================= */

  const renderPage = () => {
    if (activePage === "budget") {
      return renderBudgetPrediction();
    }

    if (activePage === "fraud") {
      return renderFraudDetection();
    }

    if (activePage === "amount") {
      return renderAmountPrediction();
    }

    return renderDashboard();
  };

  /* =======================================================
     MAIN UI
     ======================================================= */

  return (
    <div className="app">
      <aside className="sidebar">
        <div>
          <h2 className="logo">
            FinAI
          </h2>

          <p className="logo-subtitle">
            Financial Intelligence
          </p>

          <nav>
            <button
              className={`nav-item ${
                activePage === "dashboard"
                  ? "active"
                  : ""
              }`}
              onClick={() =>
                setActivePage("dashboard")
              }
            >
              Dashboard
            </button>

            <button
              className={`nav-item ${
                activePage === "budget"
                  ? "active"
                  : ""
              }`}
              onClick={() =>
                setActivePage("budget")
              }
            >
              Budget Prediction
            </button>

            <button
              className={`nav-item ${
                activePage === "fraud"
                  ? "active"
                  : ""
              }`}
              onClick={() =>
                setActivePage("fraud")
              }
            >
              Fraud Detection
            </button>

            <button
              className={`nav-item ${
                activePage === "amount"
                  ? "active"
                  : ""
              }`}
              onClick={() =>
                setActivePage("amount")
              }
            >
              Amount Prediction
            </button>
          </nav>
        </div>

        <div className="sidebar-footer">
          <span className="status-dot"></span>
          AI System Online
        </div>
      </aside>

      <main className="main-content">
        {renderPage()}
      </main>
    </div>
  );
}

export default App;