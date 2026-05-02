PAGE_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>denari</title>
  <style>
    :root {
      --ink: #17211f;
      --muted: #66736f;
      --line: #d7e1dd;
      --panel: #ffffff;
      --page: #f5f7f3;
      --primary: #176b5c;
      --primary-dark: #105044;
      --accent: #e7f2ee;
      --warning: #9a5b18;
      --warning-bg: #fff4df;
      --success-bg: #e7f5ed;
      --success-line: #add8bd;
      --error-bg: #fff0f0;
      --error-line: #e3b3b3;
    }
    body {
      font-family: Arial, sans-serif;
      margin: 0;
      padding: 32px;
      max-width: 1180px;
      color: var(--ink);
      background: var(--page);
    }
    h1 {
      margin: 0 0 26px;
      color: var(--primary-dark);
      font-family: "Snell Roundhand", "Brush Script MT", "Segoe Script", cursive;
      font-size: 52px;
      font-weight: 600;
    }
    .expense-entry {
      display: grid;
      grid-template-columns: minmax(360px, 520px) minmax(280px, 1fr);
      gap: 28px;
      align-items: start;
    }
    .hero-image {
      display: block;
      width: 100%;
      height: 360px;
      object-fit: contain;
      border-radius: 10px;
      border: 1px solid var(--line);
      background: var(--panel);
    }
    h2 {
      margin-top: 28px;
      margin-bottom: 12px;
      font-size: 20px;
      color: var(--ink);
    }
    label {
      display: block;
      margin-top: 16px;
      font-weight: bold;
      color: var(--muted);
      font-size: 14px;
    }
    .expense-form,
    .group-form {
      max-width: 520px;
    }
    .expense-form input,
    .expense-form select,
    .expense-form button,
    .group-form input,
    .group-form select,
    .group-form button {
      box-sizing: border-box;
      width: 100%;
      margin-top: 6px;
      padding: 10px;
      font-size: 16px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
      color: var(--ink);
    }
    .expense-form button,
    .group-form button {
      margin-top: 20px;
      cursor: pointer;
      border: 0;
      background: var(--primary);
      color: #fff;
      font-weight: bold;
    }
    .expense-form button:hover,
    .group-form button:hover {
      background: var(--primary-dark);
    }
    .expense-form button:disabled,
    .group-form button:disabled,
    input:disabled,
    select:disabled {
      cursor: not-allowed;
      opacity: 0.65;
    }
    .group-tools {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 20px;
      align-items: end;
      padding: 18px;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
    }
    .group-status {
      color: var(--muted);
    }
    .group-action {
      margin-top: 12px;
    }
    .inline-form {
      margin: 0;
    }
    .inline-form input {
      display: none;
    }
    .small-button {
      width: auto;
      margin: 0;
      padding: 6px 8px;
      font-size: 14px;
      line-height: 1.2;
      white-space: nowrap;
      cursor: pointer;
      border: 0;
      border-radius: 5px;
      background: var(--primary);
      color: #fff;
      font-weight: bold;
    }
    .small-button:hover {
      background: var(--primary-dark);
    }
    .secondary-button {
      background: var(--warning);
    }
    .secondary-button:hover {
      background: #754512;
    }
    .settle-button {
      background: #2f6f9f;
    }
    .settle-button:hover {
      background: #24577d;
    }
    .result {
      margin-top: 24px;
      padding: 12px;
      background: var(--success-bg);
      border: 1px solid var(--success-line);
      border-radius: 6px;
    }
    .error {
      margin-top: 24px;
      padding: 12px;
      background: var(--error-bg);
      border: 1px solid var(--error-line);
      border-radius: 6px;
    }
    .balance {
      margin-top: 28px;
      padding: 16px;
      background: var(--accent);
      border: 1px solid #b8d4cb;
      border-left: 5px solid var(--primary);
      border-radius: 8px;
      font-weight: bold;
      font-size: 18px;
    }
    .table-wrap {
      overflow-x: auto;
      padding-bottom: 8px;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      min-width: 680px;
      font-size: 14px;
    }
    th,
    td {
      border-bottom: 1px solid var(--line);
      padding: 10px;
      text-align: left;
      vertical-align: middle;
    }
    th {
      background: var(--accent);
      color: var(--primary-dark);
    }
    .number-cell,
    .status-cell,
    .action-cell,
    .date-cell {
      white-space: nowrap;
    }
    .action-cell {
      min-width: 120px;
    }
    .settled-row {
      color: var(--muted);
      background: #f8faf8;
    }
    .empty {
      color: var(--muted);
    }
    @media (max-width: 640px) {
      body {
        padding: 20px;
      }
      .expense-entry {
        grid-template-columns: 1fr;
      }
      .hero-image {
        height: auto;
        max-height: 420px;
      }
    }
  </style>
</head>
<body>
  <h1>Denari</h1>

  <h2>Expense group</h2>
  <div class="group-tools">
    <form class="group-form" method="get">
      <label for="group_id">Viewing</label>
      <select id="group_id" name="group_id">
        $group_options_html
      </select>
      <button type="submit">View group</button>
    </form>

    <form class="group-form" method="post">
      <input type="hidden" name="action" value="create_group">
      <label for="group_name">New group</label>
      <input id="group_name" name="group_name" type="text" placeholder="Alaska">
      <button type="submit">Create group</button>
    </form>
  </div>
  $close_group_html

  <div class="expense-entry">
    <div>
      <h2>Add expense to $selected_group_name</h2>
      <form class="expense-form" method="post">
        <input type="hidden" name="action" value="add_expense">
        <input type="hidden" name="group_id" value="$selected_group_id">

        <label for="expense_name">Expense name</label>
        <input id="expense_name" name="expense_name" type="text" value="$expense_name" $form_disabled required>

        <label for="amount">Amount</label>
        <input id="amount" name="amount" type="number" min="0.01" step="0.01" value="$amount" $form_disabled required>

        <label for="paid_by">Paid by</label>
        <select id="paid_by" name="paid_by" $form_disabled required>
          <option value="">Choose one</option>
          <option value="Neha" $neha_selected>Neha</option>
          <option value="Stephen" $stephen_selected>Stephen</option>
        </select>

        <button type="submit" $form_disabled>Submit expense</button>
      </form>
      $result_html
    </div>

    <img class="hero-image" src="/home-image" alt="Neha and Stephen riding camels in the desert">
  </div>

  <h2>Current balance for $selected_group_name</h2>
  $balance_html

  <h2>Expenses for $selected_group_name</h2>
  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>Expense</th>
          <th>Amount</th>
          <th>Paid by</th>
          <th>Owed by</th>
          <th>Owed amount</th>
          <th>Status</th>
          <th>Action</th>
          <th>Date</th>
        </tr>
      </thead>
      <tbody>
        $expenses_html
      </tbody>
    </table>
  </div>
</body>
</html>
"""
