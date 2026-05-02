from html import escape
from string import Template

from database import get_balance, get_group, list_expenses, list_groups
from templates import PAGE_TEMPLATE


def render_page(result=None, error=None, values=None, selected_group_id=None):
    values = values or {}
    selected_group_id = get_selected_group_id(selected_group_id)
    selected_group = get_group(selected_group_id) if selected_group_id else None
    expense_name = escape(values.get("expense_name", ""))
    amount = escape(values.get("amount", ""))
    paid_by = values.get("paid_by", "")

    result_html = render_message(result, error)
    neha_selected = "selected" if paid_by == "Neha" else ""
    stephen_selected = "selected" if paid_by == "Stephen" else ""
    group_closed = bool(selected_group and selected_group["closed"])
    form_disabled = "disabled" if group_closed or selected_group is None else ""
    selected_group_name = selected_group["name"] if selected_group else "No group"

    return Template(PAGE_TEMPLATE).substitute(
        expense_name=expense_name,
        amount=amount,
        selected_group_id=selected_group_id or "",
        selected_group_name=escape(selected_group_name),
        group_options_html=render_group_options(selected_group_id),
        close_group_html=render_close_group(selected_group),
        form_disabled=form_disabled,
        neha_selected=neha_selected,
        stephen_selected=stephen_selected,
        result_html=result_html,
        balance_html=render_balance(selected_group_id),
        expenses_html=render_expenses(selected_group_id),
    )


def get_selected_group_id(group_id):
    try:
        group_id = int(group_id)
    except (TypeError, ValueError):
        groups = list_groups()
        return groups[0]["id"] if groups else None

    return group_id if get_group(group_id) else None


def render_message(result, error):
    if result:
        return f'<p class="result">{escape(result)}</p>'
    if error:
        return f'<p class="error">{escape(error)}</p>'
    return ""


def render_group_options(selected_group_id):
    options = []
    for group in list_groups():
        selected = "selected" if group["id"] == selected_group_id else ""
        status = "closed" if group["closed"] else "open"
        label = f"{group['name']} ({status})"
        options.append(
            f'<option value="{group["id"]}" {selected}>{escape(label)}</option>'
        )

    if not options:
        return '<option value="">No groups yet</option>'

    return "\n".join(options)


def render_close_group(selected_group):
    if selected_group is None:
        return ""

    if selected_group["closed"]:
        return '<p class="group-status">This group is closed.</p>'

    return (
        '<form class="inline-form group-action" method="post">'
        '<input type="hidden" name="action" value="close_group">'
        f'<input type="hidden" name="group_id" value="{selected_group["id"]}">'
        '<button class="small-button secondary-button" type="submit">Close group</button>'
        "</form>"
    )


def render_balance(selected_group_id):
    if selected_group_id is None:
        return '<p class="balance">Create a group to start tracking expenses.</p>'

    balance = get_balance(selected_group_id)

    if balance > 0:
        text = f"Stephen owes Neha ${balance:.2f} for this group."
    elif balance < 0:
        text = f"Neha owes Stephen ${abs(balance):.2f} for this group."
    else:
        text = "Neha and Stephen are settled up for this group."

    return f'<p class="balance">{escape(text)}</p>'


def render_expenses(selected_group_id):
    if selected_group_id is None:
        return '<tr><td class="empty" colspan="8">No group selected.</td></tr>'

    expenses = list_expenses(selected_group_id)
    if not expenses:
        return '<tr><td class="empty" colspan="8">No expenses yet.</td></tr>'

    rows = []
    for expense in expenses:
        rows.append(render_expense_row(expense, selected_group_id))

    return "\n".join(rows)


def render_expense_row(expense, selected_group_id):
    is_settled = bool(expense["settled"])
    status = "Settled" if is_settled else "Unsettled"
    created_date = expense["created_at"].split(" ", 1)[0]
    action = "Done"
    row_class = "settled-row" if is_settled else ""

    if not is_settled:
        action = (
            '<form class="inline-form" method="post">'
            '<input type="hidden" name="action" value="settle_expense">'
            f'<input type="hidden" name="group_id" value="{selected_group_id}">'
            f'<input type="hidden" name="expense_id" value="{expense["id"]}">'
            '<button class="small-button settle-button" type="submit">Mark settled</button>'
            "</form>"
        )

    return (
        f'<tr class="{row_class}">'
        f"<td>{escape(expense['expense_name'])}</td>"
        f"<td class=\"number-cell\">${expense['amount']:.2f}</td>"
        f"<td class=\"status-cell\">{escape(expense['paid_by'])}</td>"
        f"<td class=\"status-cell\">{escape(expense['owed_by'])}</td>"
        f"<td class=\"number-cell\">${expense['owed_amount']:.2f}</td>"
        f"<td class=\"status-cell\">{status}</td>"
        f"<td class=\"action-cell\">{action}</td>"
        f"<td class=\"date-cell\">{escape(created_date)}</td>"
        "</tr>"
    )
