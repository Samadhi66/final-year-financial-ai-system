import { useEffect, useState } from "react";
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
     LIVE TRANSACTION DASHBOARD STATE
     ======================================================= */

  const [transactionSummary, setTransactionSummary] =
    useState({
      transaction_count: 0,
      total_spending: 0,
      average_amount: 0,
    });

  const [recentTransactions, setRecentTransactions] =
    useState([]);

  const [latestSavedTransaction, setLatestSavedTransaction] =
    useState(null);

  const [transactionDashboardLoading, setTransactionDashboardLoading] =
    useState(false);

  const [transactionDashboardError, setTransactionDashboardError] =
    useState("");

  const [autoFraudResult, setAutoFraudResult] =
    useState(null);

  const [autoFraudLoading, setAutoFraudLoading] =
    useState(false);

  const [autoFraudError, setAutoFraudError] =
    useState("");

  const [deletingTransactionId, setDeletingTransactionId] =
    useState(null);

  const [transactionDeleteMessage, setTransactionDeleteMessage] =
    useState("");

  const [transactionDeleteError, setTransactionDeleteError] =
    useState("");

  const [editingTransaction, setEditingTransaction] =
    useState(null);

  const [editTransactionForm, setEditTransactionForm] =
    useState({
      merchant: "",
      amount: "",
      transaction_date: "",
      category: "",
    });

  const [transactionEditLoading, setTransactionEditLoading] =
    useState(false);

  const [transactionEditMessage, setTransactionEditMessage] =
    useState("");

  const [transactionEditError, setTransactionEditError] =
    useState("");

  /* =======================================================
     RECEIPT OCR STATE
     ======================================================= */

  const [ocrFile, setOcrFile] = useState(null);
  const [ocrPreview, setOcrPreview] = useState("");
  const [ocrResult, setOcrResult] = useState(null);
  const [ocrLoading, setOcrLoading] = useState(false);
  const [ocrError, setOcrError] = useState("");
  const [ocrConfirmed, setOcrConfirmed] = useState(false);
  const [transactionSaving, setTransactionSaving] = useState(false);
  const [savedTransaction, setSavedTransaction] = useState(null);

  const [ocrForm, setOcrForm] = useState({
    merchant: "",
    amount: "",
    date: "",
    suggested_category: "",
  });

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
     LIVE TRANSACTION DASHBOARD API
     ======================================================= */

  const loadTransactionDashboard = async () => {
    setTransactionDashboardLoading(true);
    setTransactionDashboardError("");

    try {
      const [
        summaryResponse,
        transactionsResponse,
        latestResponse,
        latestFraudResponse,
      ] = await Promise.all([
        fetch(
          "http://127.0.0.1:8000/transactions/summary"
        ),
        fetch(
          "http://127.0.0.1:8000/transactions"
        ),
        fetch(
          "http://127.0.0.1:8000/transactions/latest"
        ),
        fetch(
          "http://127.0.0.1:8000/transactions/latest/fraud"
        ),
      ]);

      if (
        !summaryResponse.ok ||
        !transactionsResponse.ok ||
        !latestResponse.ok ||
        !latestFraudResponse.ok
      ) {
        throw new Error(
          "Transaction dashboard data could not be loaded."
        );
      }

      const summaryData =
        await summaryResponse.json();

      const transactionsData =
        await transactionsResponse.json();

      const latestData =
        await latestResponse.json();

      const latestFraudData =
        await latestFraudResponse.json();

      if (
        summaryData.status !== "Success" ||
        transactionsData.status !== "Success" ||
        latestData.status !== "Success" ||
        latestFraudData.status !== "Success"
      ) {
        throw new Error(
          "Transaction dashboard data is unavailable."
        );
      }

      setTransactionSummary({
        transaction_count:
          Number(
            summaryData.transaction_count
          ) || 0,

        total_spending:
          Number(
            summaryData.total_spending
          ) || 0,

        average_amount:
          Number(
            summaryData.average_amount
          ) || 0,
      });

      setRecentTransactions(
        Array.isArray(
          transactionsData.transactions
        )
          ? transactionsData.transactions
          : []
      );

      setLatestSavedTransaction(
        latestData.transaction || null
      );

      if (
        latestFraudData.has_transaction &&
        latestFraudData.fraud_analysis
      ) {
        setAutoFraudResult(
          latestFraudData.fraud_analysis
        );
        setAutoFraudError("");
      } else {
        setAutoFraudResult(null);
      }
    } catch (error) {
      console.error(error);

      setTransactionDashboardError(
        "Saved transaction data could not be loaded. Please check that the FastAPI server is running."
      );
    } finally {
      setTransactionDashboardLoading(false);
    }
  };

  useEffect(() => {
    loadTransactionDashboard();
  }, []);

  useEffect(() => {
    if (activePage === "dashboard") {
      loadTransactionDashboard();
    }
  }, [activePage]);

  /* =======================================================
     EDIT / UPDATE SAVED TRANSACTION
     ======================================================= */

  const openTransactionEditor = (transaction) => {
    setEditingTransaction(transaction);

    setEditTransactionForm({
      merchant: transaction.merchant || "",
      amount:
        transaction.amount !== null &&
        transaction.amount !== undefined
          ? String(transaction.amount)
          : "",
      transaction_date:
        transaction.transaction_date || "",
      category: transaction.category || "",
    });

    setTransactionEditMessage("");
    setTransactionEditError("");
  };

  const closeTransactionEditor = () => {
    if (transactionEditLoading) {
      return;
    }

    setEditingTransaction(null);
    setEditTransactionForm({
      merchant: "",
      amount: "",
      transaction_date: "",
      category: "",
    });
    setTransactionEditError("");
  };

  const handleEditTransactionChange = (event) => {
    const { name, value } = event.target;

    setEditTransactionForm((previous) => ({
      ...previous,
      [name]: value,
    }));

    setTransactionEditError("");
  };

  const handleUpdateTransaction = async (event) => {
    event.preventDefault();

    if (!editingTransaction) {
      return;
    }

    const merchant =
      editTransactionForm.merchant.trim();

    const transactionDate =
      editTransactionForm.transaction_date.trim();

    const category =
      editTransactionForm.category.trim();

    const amount =
      Number(editTransactionForm.amount);

    if (
      !merchant ||
      !transactionDate ||
      !category ||
      !Number.isFinite(amount) ||
      amount <= 0
    ) {
      setTransactionEditError(
        "Please enter a merchant, valid amount greater than 0, transaction date and category."
      );
      return;
    }

    setTransactionEditLoading(true);
    setTransactionEditMessage("");
    setTransactionEditError("");
    setTransactionDeleteMessage("");
    setTransactionDeleteError("");

    const payload = {
      merchant,
      amount,
      transaction_date: transactionDate,
      category,
      source:
        editingTransaction.source || "Manual",
      raw_ocr_text:
        editingTransaction.raw_ocr_text ?? null,
    };

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/transactions/${editingTransaction.id}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        }
      );

      const result = await response.json();

      if (!response.ok) {
        throw new Error(
          result.detail ||
            result.message ||
            `Server returned ${response.status}`
        );
      }

      if (result.status === "Duplicate") {
        throw new Error(
          result.message ||
            "Another identical transaction already exists."
        );
      }

      if (result.status !== "Success") {
        throw new Error(
          result.message ||
            "Transaction could not be updated."
        );
      }

      setTransactionEditMessage(
        `Transaction #${editingTransaction.id} updated successfully.`
      );

      if (
        savedTransaction?.transaction_id ===
        editingTransaction.id
      ) {
        setSavedTransaction((previous) =>
          previous
            ? {
                ...previous,
                ...payload,
              }
            : previous
        );
      }

      setEditingTransaction(null);
      setEditTransactionForm({
        merchant: "",
        amount: "",
        transaction_date: "",
        category: "",
      });

      await loadTransactionDashboard();
    } catch (error) {
      console.error(error);

      setTransactionEditError(
        error.message ||
          "Transaction could not be updated. Please check that the FastAPI server is running."
      );
    } finally {
      setTransactionEditLoading(false);
    }
  };

  /* =======================================================
     DELETE SAVED TRANSACTION
     ======================================================= */

  const handleDeleteTransaction = async (transaction) => {
    const confirmed = window.confirm(
      `Delete transaction #${transaction.id} from ${transaction.merchant} for Rs. ${Number(
        transaction.amount
      ).toLocaleString()}?`
    );

    if (!confirmed) {
      return;
    }

    setDeletingTransactionId(transaction.id);
    setTransactionDeleteMessage("");
    setTransactionDeleteError("");

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/transactions/${transaction.id}`,
        {
          method: "DELETE",
        }
      );

      const result = await response.json();

      if (!response.ok) {
        throw new Error(
          result.detail ||
            result.message ||
            `Server returned ${response.status}`
        );
      }

      if (result.status !== "Success") {
        throw new Error(
          result.message ||
            "Transaction could not be deleted."
        );
      }

      setTransactionDeleteMessage(
        `Transaction #${transaction.id} deleted successfully.`
      );

      if (
        savedTransaction?.transaction_id === transaction.id
      ) {
        setSavedTransaction(null);
        setOcrConfirmed(false);
      }

      await loadTransactionDashboard();
    } catch (error) {
      console.error(error);

      setTransactionDeleteError(
        error.message ||
          "Transaction could not be deleted. Please check that the FastAPI server is running."
      );
    } finally {
      setDeletingTransactionId(null);
    }
  };

  /* =======================================================
     AUTO FRAUD ANALYSIS FOR SAVED OCR TRANSACTIONS
     ======================================================= */

  const runAutoFraudAnalysis = async ({
    amount,
    category,
    merchant,
  }) => {
    setAutoFraudLoading(true);
    setAutoFraudError("");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/auto_detect_fraud",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            amount: Number(amount),
            category,
            merchant,
            payment_method: 0,
            location: 0,
          }),
        }
      );

      const result = await response.json();

      if (!response.ok) {
        throw new Error(
          result.detail ||
            result.message ||
            `Server returned ${response.status}`
        );
      }

      if (result.status !== "Success") {
        throw new Error(
          result.message ||
            "Automatic fraud analysis could not be completed."
        );
      }

      setAutoFraudResult(
        result.fraud_analysis || null
      );

      return result;
    } catch (error) {
      console.error(error);

      setAutoFraudError(
        error.message ||
          "Automatic fraud analysis could not be completed."
      );

      return null;
    } finally {
      setAutoFraudLoading(false);
    }
  };

  /* =======================================================
     RECEIPT OCR API
     ======================================================= */

  const handleOcrFileChange = (event) => {
    const file = event.target.files?.[0] || null;
    setOcrFile(file);
    setOcrResult(null);
    setOcrError("");
    setOcrConfirmed(false);
    setSavedTransaction(null);
    setAutoFraudResult(null);
    setAutoFraudError("");

    if (ocrPreview) URL.revokeObjectURL(ocrPreview);
    setOcrPreview(file ? URL.createObjectURL(file) : "");
  };

  const handleOcrFieldChange = (event) => {
    const { name, value } = event.target;
    setOcrForm((previous) => ({ ...previous, [name]: value }));
    setOcrConfirmed(false);
    setSavedTransaction(null);
  };

  const handleReceiptScan = async (event) => {
    event.preventDefault();
    setOcrError("");
    setOcrConfirmed(false);

    if (!ocrFile) {
      setOcrError("Please select a receipt image before scanning.");
      return;
    }

    const allowedTypes = ["image/jpeg", "image/png", "image/webp"];
    if (!allowedTypes.includes(ocrFile.type)) {
      setOcrError("Please upload a JPG, PNG or WEBP image.");
      return;
    }

    if (ocrFile.size > 10 * 1024 * 1024) {
      setOcrError("Receipt image must be 10 MB or smaller.");
      return;
    }

    const formData = new FormData();
    formData.append("file", ocrFile);

    setOcrLoading(true);
    setOcrResult(null);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/ocr_receipt",
        { method: "POST", body: formData }
      );

      const result = await response.json();

      if (!response.ok) {
        throw new Error(
          result.detail || result.message || `Server returned ${response.status}`
        );
      }

      if (result.status === "Error" || result.status === "Unavailable") {
        throw new Error(
          result.error || result.message || "Receipt OCR failed"
        );
      }

      setOcrResult(result);
      setOcrForm({
        merchant: result.merchant ?? "",
        amount:
          result.amount !== null && result.amount !== undefined
            ? String(result.amount)
            : "",
        date: result.date ?? "",
        suggested_category: result.suggested_category ?? "",
      });
    } catch (error) {
      console.error(error);
      setOcrError(
        error.message ||
          "Receipt scanning could not be completed. Please check that the FastAPI server is running."
      );
    } finally {
      setOcrLoading(false);
    }
  };

  const handleConfirmReceipt = async () => {
    if (
      !ocrForm.merchant.trim() ||
      !ocrForm.amount ||
      !ocrForm.date.trim() ||
      !ocrForm.suggested_category.trim()
    ) {
      setOcrError(
        "Please review and complete the extracted receipt details before confirming."
      );
      return;
    }

    if (
      !Number.isFinite(Number(ocrForm.amount)) ||
      Number(ocrForm.amount) <= 0
    ) {
      setOcrError(
        "Receipt amount must be a valid value greater than 0."
      );
      return;
    }

    const payload = {
      merchant: ocrForm.merchant.trim(),
      amount: Number(ocrForm.amount),
      transaction_date: ocrForm.date.trim(),
      category: ocrForm.suggested_category.trim(),
      source: "OCR",
      raw_ocr_text: ocrResult?.raw_text || "",
    };

    setOcrError("");
    setOcrConfirmed(false);
    setSavedTransaction(null);
    setTransactionSaving(true);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/transactions",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        }
      );

      const result = await response.json();

      if (!response.ok) {
        throw new Error(
          result.detail ||
            result.message ||
            `Server returned ${response.status}`
        );
      }

      if (result.status !== "Success") {
        throw new Error(
          result.message ||
            "Transaction could not be saved."
        );
      }

      setSavedTransaction({
        ...payload,
        transaction_id: result.transaction_id,
      });

      setOcrConfirmed(true);

      await runAutoFraudAnalysis({
        amount: payload.amount,
        category: payload.category,
        merchant: payload.merchant,
      });

      await loadTransactionDashboard();
    } catch (error) {
      console.error(error);

      setOcrError(
        error.message ||
          "Transaction could not be saved. Please check that the FastAPI server is running."
      );
    } finally {
      setTransactionSaving(false);
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

    const effectiveFraudResult =
      autoFraudResult || fraudResult;

    const latestFraudProbability =
      effectiveFraudResult
        ?.fraud_probability ??
      null;

    const latestFraudStatus =
      effectiveFraudResult
        ?.fraud_status ??
      "Not Analysed";

    const latestFraudRiskLevel =
      effectiveFraudResult
        ?.risk_level ??
      "Not Analysed";

    const latestAmount =
      amountResult?.predicted_amount ??
      null;

    const categoryTotals =
      recentTransactions.reduce(
        (totals, transaction) => {
          const category =
            transaction.category ||
            "Other";

          totals[category] =
            (totals[category] || 0) +
            Number(
              transaction.amount || 0
            );

          return totals;
        },
        {}
      );

    const topCategoryEntry =
      Object.entries(categoryTotals).sort(
        (a, b) => b[1] - a[1]
      )[0] || null;

    const topCategory =
      topCategoryEntry
        ? topCategoryEntry[0]
        : "No data";

    const topCategoryAmount =
      topCategoryEntry
        ? topCategoryEntry[1]
        : 0;

    const dashboardTransactions =
      recentTransactions.slice(0, 5);

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
              Unified view of AI predictions and
              live saved transaction intelligence.
            </p>
          </div>

          <div className="system-status">
            <span className="status-dot"></span>
            AI & Transaction System Active
          </div>
        </header>

        <section className="dashboard-kpis">
          <div
            className="kpi-card"
            onClick={() =>
              setActivePage("ocr")
            }
          >
            <div className="kpi-top">
              <span className="kpi-icon">
                Rs
              </span>

              <span className="kpi-label">
                Total Saved Spending
              </span>
            </div>

            <h3>
              Rs.{" "}
              {Number(
                transactionSummary.total_spending
              ).toLocaleString()}
            </h3>

            <p>
              {transactionSummary.transaction_count}
              {" "}
              saved transaction
              {transactionSummary.transaction_count === 1
                ? ""
                : "s"}
            </p>
          </div>

          <div className="kpi-card">
            <div className="kpi-top">
              <span className="kpi-icon">
                #
              </span>

              <span className="kpi-label">
                Average Expense
              </span>
            </div>

            <h3>
              Rs.{" "}
              {Number(
                transactionSummary.average_amount
              ).toLocaleString()}
            </h3>

            <p>
              Average saved transaction amount
            </p>
          </div>

          <div className="kpi-card">
            <div className="kpi-top">
              <span className="kpi-icon">
                ↗
              </span>

              <span className="kpi-label">
                Latest Expense
              </span>
            </div>

            <h3>
              {latestSavedTransaction
                ? `Rs. ${Number(
                    latestSavedTransaction.amount
                  ).toLocaleString()}`
                : "No expense"}
            </h3>

            <p>
              {latestSavedTransaction
                ? latestSavedTransaction.merchant
                : "Save a receipt transaction"}
            </p>
          </div>

          <div className="kpi-card model-health-card">
            <div className="kpi-top">
              <span className="kpi-icon">
                AI
              </span>

              <span className="kpi-label">
                Top Category
              </span>
            </div>

            <h3>
              {topCategory}
            </h3>

            <p>
              {topCategoryEntry
                ? `Rs. ${Number(
                    topCategoryAmount
                  ).toLocaleString()} recorded`
                : "No saved category data"}
            </p>
          </div>
        </section>

        {transactionDashboardError && (
          <div
            className="error-box"
            style={{
              marginBottom: "20px",
            }}
          >
            {transactionDashboardError}
          </div>
        )}

        {transactionDeleteError && (
          <div
            className="error-box"
            style={{
              marginBottom: "20px",
            }}
          >
            {transactionDeleteError}
          </div>
        )}

        {transactionDeleteMessage && (
          <div
            className="explanation-box"
            style={{
              marginBottom: "20px",
            }}
          >
            <span>Transaction Updated</span>
            <p>{transactionDeleteMessage}</p>
          </div>
        )}

        {transactionEditError && !editingTransaction && (
          <div
            className="error-box"
            style={{
              marginBottom: "20px",
            }}
          >
            {transactionEditError}
          </div>
        )}

        {transactionEditMessage && (
          <div
            className="explanation-box"
            style={{
              marginBottom: "20px",
            }}
          >
            <span>Transaction Updated</span>
            <p>{transactionEditMessage}</p>
          </div>
        )}

        {editingTransaction && (
          <div
            style={{
              position: "fixed",
              inset: 0,
              background: "rgba(15, 23, 42, 0.48)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              padding: "20px",
              zIndex: 9999,
            }}
            onMouseDown={(event) => {
              if (
                event.target === event.currentTarget &&
                !transactionEditLoading
              ) {
                closeTransactionEditor();
              }
            }}
          >
            <form
              onSubmit={handleUpdateTransaction}
              style={{
                width: "min(560px, 100%)",
                background: "#ffffff",
                borderRadius: "18px",
                padding: "24px",
                boxShadow:
                  "0 24px 70px rgba(15, 23, 42, 0.22)",
                border: "1px solid #e2e8f0",
              }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "flex-start",
                  gap: "14px",
                  marginBottom: "20px",
                }}
              >
                <div>
                  <p
                    className="eyebrow"
                    style={{
                      marginBottom: "6px",
                    }}
                  >
                    TRANSACTION MANAGEMENT
                  </p>

                  <h2
                    style={{
                      margin: 0,
                    }}
                  >
                    Edit Transaction #{editingTransaction.id}
                  </h2>
                </div>

                <button
                  type="button"
                  onClick={closeTransactionEditor}
                  disabled={transactionEditLoading}
                  style={{
                    border: "1px solid #e2e8f0",
                    background: "#f8fafc",
                    color: "#0f172a",
                    borderRadius: "9px",
                    padding: "7px 11px",
                    cursor:
                      transactionEditLoading
                        ? "not-allowed"
                        : "pointer",
                    fontWeight: "700",
                  }}
                >
                  Close
                </button>
              </div>

              <div
                style={{
                  display: "grid",
                  gridTemplateColumns:
                    "repeat(2, minmax(0, 1fr))",
                  gap: "14px",
                }}
              >
                <label
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: "7px",
                    fontWeight: "700",
                    fontSize: "12px",
                  }}
                >
                  Merchant
                  <input
                    type="text"
                    name="merchant"
                    value={editTransactionForm.merchant}
                    onChange={handleEditTransactionChange}
                    disabled={transactionEditLoading}
                    style={{
                      width: "100%",
                      border: "1px solid #dbe3ef",
                      borderRadius: "9px",
                      padding: "11px 12px",
                      font: "inherit",
                    }}
                  />
                </label>

                <label
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: "7px",
                    fontWeight: "700",
                    fontSize: "12px",
                  }}
                >
                  Amount
                  <input
                    type="number"
                    name="amount"
                    min="0.01"
                    step="0.01"
                    value={editTransactionForm.amount}
                    onChange={handleEditTransactionChange}
                    disabled={transactionEditLoading}
                    style={{
                      width: "100%",
                      border: "1px solid #dbe3ef",
                      borderRadius: "9px",
                      padding: "11px 12px",
                      font: "inherit",
                    }}
                  />
                </label>

                <label
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: "7px",
                    fontWeight: "700",
                    fontSize: "12px",
                  }}
                >
                  Transaction Date
                  <input
                    type="text"
                    name="transaction_date"
                    placeholder="DD/MM/YYYY"
                    value={
                      editTransactionForm.transaction_date
                    }
                    onChange={handleEditTransactionChange}
                    disabled={transactionEditLoading}
                    style={{
                      width: "100%",
                      border: "1px solid #dbe3ef",
                      borderRadius: "9px",
                      padding: "11px 12px",
                      font: "inherit",
                    }}
                  />
                </label>

                <label
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: "7px",
                    fontWeight: "700",
                    fontSize: "12px",
                  }}
                >
                  Category
                  <select
                    name="category"
                    value={editTransactionForm.category}
                    onChange={handleEditTransactionChange}
                    disabled={transactionEditLoading}
                    style={{
                      width: "100%",
                      border: "1px solid #dbe3ef",
                      borderRadius: "9px",
                      padding: "11px 12px",
                      font: "inherit",
                      background: "#ffffff",
                      color: "#0f172a",
                    }}
                  >
                    <option value="">
                      Select category
                    </option>
                    <option value="Food & Dining">
                      Food & Dining
                    </option>
                    <option value="Groceries">
                      Groceries
                    </option>
                    <option value="Transport">
                      Transport
                    </option>
                    <option value="Shopping">
                      Shopping
                    </option>
                    <option value="Utilities">
                      Utilities
                    </option>
                    <option value="Entertainment">
                      Entertainment
                    </option>
                    <option value="Healthcare">
                      Healthcare
                    </option>
                    <option value="Education">
                      Education
                    </option>
                    <option value="Travel">
                      Travel
                    </option>
                    <option value="Other">
                      Other
                    </option>
                  </select>
                </label>
              </div>

              {transactionEditError && (
                <div
                  className="error-box"
                  style={{
                    marginTop: "16px",
                  }}
                >
                  {transactionEditError}
                </div>
              )}

              <div
                style={{
                  display: "flex",
                  justifyContent: "flex-end",
                  gap: "10px",
                  marginTop: "22px",
                }}
              >
                <button
                  type="button"
                  onClick={closeTransactionEditor}
                  disabled={transactionEditLoading}
                  style={{
                    border: "1px solid #dbe3ef",
                    background: "#ffffff",
                    color: "#0f172a",
                    borderRadius: "9px",
                    padding: "10px 15px",
                    cursor:
                      transactionEditLoading
                        ? "not-allowed"
                        : "pointer",
                    fontWeight: "700",
                  }}
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  disabled={transactionEditLoading}
                  style={{
                    border: "none",
                    background: "#2563eb",
                    color: "#ffffff",
                    borderRadius: "9px",
                    padding: "10px 17px",
                    cursor:
                      transactionEditLoading
                        ? "not-allowed"
                        : "pointer",
                    fontWeight: "700",
                    opacity:
                      transactionEditLoading
                        ? 0.7
                        : 1,
                  }}
                >
                  {transactionEditLoading
                    ? "Saving..."
                    : "Save Changes"}
                </button>
              </div>
            </form>
          </div>
        )}

        <section className="dashboard-grid">
          <div className="dashboard-panel">
            <div className="panel-heading">
              <p className="eyebrow">
                LIVE TRANSACTION DATA
              </p>

              <h2>
                Recent Saved Expenses
              </h2>
            </div>

            {transactionDashboardLoading ? (
              <div
                className="explanation-box"
              >
                <span>
                  Loading
                </span>

                <p>
                  Loading transaction data...
                </p>
              </div>
            ) : dashboardTransactions.length ===
              0 ? (
              <div
                className="explanation-box"
              >
                <span>
                  No Transactions
                </span>

                <p>
                  Scan and save a receipt to
                  populate the live dashboard.
                </p>
              </div>
            ) : (
              <div className="model-status-list">
                {dashboardTransactions.map(
                  (transaction) => (
                    <div
                      key={transaction.id}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                        gap: "12px",
                      }}
                    >
                      <span
                        style={{
                          flex: 1,
                          minWidth: 0,
                        }}
                      >
                        <strong>
                          {transaction.merchant}
                        </strong>
                        {" · "}
                        {transaction.category}
                        {" · "}
                        {transaction.transaction_date}
                      </span>

                      <div
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: "10px",
                          flexShrink: 0,
                        }}
                      >
                        <strong>
                          Rs.{" "}
                          {Number(
                            transaction.amount
                          ).toLocaleString()}
                        </strong>

                        <button
                          type="button"
                          onClick={() =>
                            openTransactionEditor(
                              transaction
                            )
                          }
                          disabled={
                            deletingTransactionId ===
                            transaction.id
                          }
                          style={{
                            border: "1px solid #bfdbfe",
                            background: "#eff6ff",
                            color: "#2563eb",
                            borderRadius: "8px",
                            padding: "6px 10px",
                            fontSize: "11px",
                            fontWeight: "700",
                            cursor:
                              deletingTransactionId ===
                              transaction.id
                                ? "not-allowed"
                                : "pointer",
                            opacity:
                              deletingTransactionId ===
                              transaction.id
                                ? 0.6
                                : 1,
                          }}
                        >
                          Edit
                        </button>

                        <button
                          type="button"
                          onClick={() =>
                            handleDeleteTransaction(
                              transaction
                            )
                          }
                          disabled={
                            deletingTransactionId ===
                            transaction.id
                          }
                          style={{
                            border: "1px solid #fecaca",
                            background: "#fff7f7",
                            color: "#dc2626",
                            borderRadius: "8px",
                            padding: "6px 10px",
                            fontSize: "11px",
                            fontWeight: "700",
                            cursor:
                              deletingTransactionId ===
                              transaction.id
                                ? "not-allowed"
                                : "pointer",
                            opacity:
                              deletingTransactionId ===
                              transaction.id
                                ? 0.6
                                : 1,
                          }}
                        >
                          {deletingTransactionId ===
                          transaction.id
                            ? "Deleting..."
                            : "Delete"}
                        </button>
                      </div>
                    </div>
                  )
                )}
              </div>
            )}

            <div
              className="system-score"
              style={{
                marginTop: "20px",
              }}
            >
              <span>
                Transactions Stored
              </span>

              <strong>
                {
                  transactionSummary.transaction_count
                }
              </strong>
            </div>
          </div>

          <div className="dashboard-panel system-panel">
            <p className="eyebrow">
              AI DECISION SUPPORT
            </p>

            <h2>
              Current AI Insights
            </h2>

            <div className="model-status-list">
              <div>
                <span>
                  Budget Forecast
                </span>

                <strong>
                  {latestBudget !== null
                    ? `Rs. ${Number(
                        latestBudget
                      ).toLocaleString()}`
                    : "Not run"}
                </strong>
              </div>

              <div>
                <span>
                  Fraud Risk
                </span>

                <strong>
                  {latestFraudRiskLevel}
                </strong>
              </div>

              <div>
                <span>
                  Fraud Decision
                </span>

                <strong>
                  {latestFraudStatus}
                </strong>
              </div>

              <div>
                <span>
                  Fraud Probability
                </span>

                <strong>
                  {latestFraudProbability !==
                  null
                    ? `${(
                        Number(
                          latestFraudProbability
                        ) * 100
                      ).toFixed(2)}%`
                    : "Not run"}
                </strong>
              </div>

              <div>
                <span>
                  Predicted Amount
                </span>

                <strong>
                  {latestAmount !== null
                    ? `Rs. ${Number(
                        latestAmount
                      ).toLocaleString()}`
                    : "Not run"}
                </strong>
              </div>
            </div>

            <div className="system-score">
              <span>
                Integrated Services
              </span>

              <strong>
                4 / 4
              </strong>
            </div>
          </div>
        </section>

        <section
          className="dashboard-grid"
          style={{
            marginTop: "20px",
          }}
        >
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
                    effectiveFraudResult
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
                    {effectiveFraudResult
                      ? `${effectiveFraudResult.fraud_status} · ${effectiveFraudResult.risk_level} risk · ${(
                          Number(
                            effectiveFraudResult.fraud_probability
                          ) * 100
                        ).toFixed(
                          2
                        )}% fraud probability.`
                      : "Analyse a transaction or save an OCR expense to receive behavioral fraud intelligence."}
                  </p>
                </div>
              </div>

              <div className="insight-item">
                <span className="insight-dot purple"></span>

                <div>
                  <strong>
                    Latest Saved Expense
                  </strong>

                  <p>
                    {latestSavedTransaction
                      ? `${latestSavedTransaction.merchant}: Rs. ${Number(
                          latestSavedTransaction.amount
                        ).toLocaleString()} in ${latestSavedTransaction.category}.`
                      : "No saved expense is currently available."}
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
              Integrated Services
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

              <div>
                <span>
                  EasyOCR + SQLite
                </span>

                <strong className="online-text">
                  Online
                </strong>
              </div>
            </div>

            <div className="system-score">
              <span>
                Live Transaction Integration
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
     RECEIPT OCR PAGE
     ======================================================= */

  const renderReceiptOcr = () => {
    return (
      <>
        <header>
          <div>
            <p className="eyebrow">AI-POWERED RECEIPT PROCESSING</p>
            <h1>Receipt OCR</h1>
            <p className="subtitle">
              Upload a receipt image, extract transaction information with
              EasyOCR, review the detected values and confirm the expense.
            </p>
          </div>

          <div className="system-status">
            <span className="status-dot"></span>
            EasyOCR Ready
          </div>
        </header>

        <div className="prediction-layout">
          <section className="prediction-form-card">
            <div className="section-heading">
              <div>
                <p className="eyebrow">RECEIPT INPUT</p>
                <h2>Scan Receipt</h2>
              </div>
              <span className="model-chip">EasyOCR</span>
            </div>

            <form onSubmit={handleReceiptScan}>
              <div className="form-section">
                <h3>Receipt Image</h3>

                <label>
                  Choose Receipt
                  <input
                    type="file"
                    accept=".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp"
                    onChange={handleOcrFileChange}
                  />
                </label>

                {ocrFile && (
                  <div className="fraud-info-box">
                    <span>Selected File</span>
                    <strong>{ocrFile.name}</strong>
                    <p>{(ocrFile.size / 1024 / 1024).toFixed(2)} MB</p>
                  </div>
                )}

                {ocrPreview && (
                  <div style={{
                    marginTop: "18px",
                    padding: "14px",
                    border: "1px solid #e5e7eb",
                    borderRadius: "14px",
                    textAlign: "center",
                  }}>
                    <img
                      src={ocrPreview}
                      alt="Receipt preview"
                      style={{
                        width: "100%",
                        maxWidth: "360px",
                        maxHeight: "480px",
                        objectFit: "contain",
                        borderRadius: "10px",
                      }}
                    />
                  </div>
                )}
              </div>

              {ocrError && <div className="error-box">{ocrError}</div>}

              <button
                type="submit"
                className="primary-button"
                disabled={ocrLoading || !ocrFile}
              >
                {ocrLoading ? "Scanning Receipt..." : "Scan Receipt with AI"}
              </button>
            </form>
          </section>

          <section className="prediction-result-card">
            <p className="eyebrow">OCR RESULT</p>
            <h2>Extracted Information</h2>

            {!ocrResult && (
              <div className="result-placeholder">
                <div className="result-icon">OCR</div>
                <h3>Ready to Scan</h3>
                <p>
                  Upload a clear receipt image and run EasyOCR to extract
                  merchant, amount, date and category information.
                </p>
              </div>
            )}

            {ocrResult && (
              <div className="result-content">
                <div className="result-highlight">
                  <p>Detected Amount</p>
                  <h3>Rs. {Number(ocrForm.amount || 0).toLocaleString()}</h3>
                </div>

                <div className="form-section">
                  <h3>Review & Edit Extracted Data</h3>
                  <div className="form-grid">
                    <InputField
                      label="Merchant"
                      name="merchant"
                      type="text"
                      value={ocrForm.merchant}
                      onChange={handleOcrFieldChange}
                    />
                    <InputField
                      label="Amount"
                      name="amount"
                      type="number"
                      step="0.01"
                      min="0"
                      value={ocrForm.amount}
                      onChange={handleOcrFieldChange}
                    />
                    <InputField
                      label="Date"
                      name="date"
                      type="text"
                      value={ocrForm.date}
                      onChange={handleOcrFieldChange}
                    />
                    <InputField
                      label="Suggested Category"
                      name="suggested_category"
                      type="text"
                      value={ocrForm.suggested_category}
                      onChange={handleOcrFieldChange}
                    />
                  </div>
                </div>

                <div className="explanation-box">
                  <span>OCR Confirmation</span>
                  <p>
                    {ocrResult.message ||
                      "Receipt scanned successfully. Please confirm or edit the extracted information."}
                  </p>
                </div>

                <div className="fraud-info-box" style={{ marginTop: "16px" }}>
                  <span>Raw OCR Text</span>
                  <p style={{ whiteSpace: "pre-wrap", wordBreak: "break-word" }}>
                    {ocrResult.raw_text || "No raw text returned."}
                  </p>
                </div>

                <button
                  type="button"
                  className="primary-button"
                  onClick={handleConfirmReceipt}
                  disabled={transactionSaving}
                  style={{ marginTop: "18px" }}
                >
                  {transactionSaving
                    ? "Saving Transaction..."
                    : "Confirm & Save Expense"}
                </button>

                {ocrConfirmed && savedTransaction && (
                  <div
                    className="explanation-box"
                    style={{ marginTop: "16px" }}
                  >
                    <span>Saved Successfully</span>
                    <p>
                      Receipt expense has been confirmed and saved to the
                      transaction database.
                    </p>
                    <p>
                      Transaction ID:{" "}
                      <strong>
                        {savedTransaction.transaction_id}
                      </strong>
                    </p>
                  </div>
                )}


                {autoFraudLoading && (
                  <div
                    className="explanation-box"
                    style={{ marginTop: "16px" }}
                  >
                    <span>Fraud Analysis</span>
                    <p>
                      Analysing the saved transaction with the Random Forest fraud model...
                    </p>
                  </div>
                )}

                {autoFraudError && (
                  <div
                    className="error-box"
                    style={{ marginTop: "16px" }}
                  >
                    {autoFraudError}
                  </div>
                )}

                {autoFraudResult && (
                  <div
                    className="explanation-box"
                    style={{ marginTop: "16px" }}
                  >
                    <span>Automatic Fraud Analysis</span>
                    <p>
                      Decision:{" "}
                      <strong>
                        {autoFraudResult.fraud_status}
                      </strong>
                    </p>
                    <p>
                      Risk Level:{" "}
                      <strong>
                        {autoFraudResult.risk_level}
                      </strong>
                    </p>
                    <p>
                      Fraud Probability:{" "}
                      <strong>
                        {(
                          Number(
                            autoFraudResult.fraud_probability
                          ) * 100
                        ).toFixed(2)}
                        %
                      </strong>
                    </p>
                  </div>
                )}
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

    if (activePage === "ocr") {
      return renderReceiptOcr();
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

            <button
              className={`nav-item ${
                activePage === "ocr" ? "active" : ""
              }`}
              onClick={() => setActivePage("ocr")}
            >
              Receipt OCR
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