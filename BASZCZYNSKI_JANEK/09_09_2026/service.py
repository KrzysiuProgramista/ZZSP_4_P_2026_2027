from datetime import date
from models import Expense, Category

def createExpense(expenses, id, expense):
    expenses[id] = expense
    return expense


def getExpenses(expenses, category=None, from_=None, to=None):
    result = []

    for id, expense in expenses.items():

        if category is not None and expense.category != category:
            continue

        if from_ is not None and expense.spent_on < from_:
            continue

        if to is not None and expense.spent_on > to:
            continue

        result.append({
            "id": id,
            **expense.model_dump()
        })

    return result


def getExpense(expenses, id):
    return expenses.get(id)


def updateExpense(expenses, id, expense):
    if id not in expenses:
        return None

    expenses[id] = expense
    return expense


def deleteExpense(expenses, id):
    if id not in expenses:
        return False

    del expenses[id]
    return True


def getSummary(expenses, category=None, from_=None, to=None):
    filtered = []

    for expense in expenses.values():

        if category is not None and expense.category != category:
            continue

        if from_ is not None and expense.spent_on < from_:
            continue

        if to is not None and expense.spent_on > to:
            continue

        filtered.append(expense)

    total = sum(expense.amount for expense in filtered)

    totalPerCategory = {}

    for categoryValue in Category:
        totalPerCategory[categoryValue.value] = sum(
            expense.amount
            for expense in filtered
            if expense.category == categoryValue
        )

    if from_ is not None and to is not None:
        days = (to - from_).days + 1
    elif filtered:
        firstDay = min(expense.spent_on for expense in filtered)
        lastDay = max(expense.spent_on for expense in filtered)
        days = (lastDay - firstDay).days + 1
    else:
        days = 0

    averagePerDay = total / days if days > 0 else 0

    return {
        "total": total,
        "total_per_category": totalPerCategory,
        "average_per_day": averagePerDay
    }
