from datetime import date, timedelta
import unittest
from unittest.mock import Mock, patch
from pydantic import ValidationError

from models import ExpenseCreate, ExpenseUpdate, CategoryEnum
from services import ExpenseService
from exceptions import NotFoundException  # Jeśli używasz własnego wyjątku

class TestExpenseServiceUnit(unittest.TestCase):

    def setUp(self):
        """Inicjalizacja świeżej instancji serwisu przed każdym testem."""
        self.service = ExpenseService()

    def test_create_expense_success(self):
        expense_data = ExpenseCreate(
            amount=45.50,
            category=CategoryEnum.FOOD,
            description="Lunch z klientem",
            spent_on=date.today()
        )
        
        result = self.service.create_expense(expense_data)

        self.assertEqual(result.id, 1)
        self.assertEqual(result.amount, 45.50)
        self.assertEqual(result.category, CategoryEnum.FOOD)
        self.assertEqual(len(self.service._storage), 1)

    def test_create_expense_invalid_amount(self):
        with self.assertRaises(ValidationError):
            ExpenseCreate(
                amount=0.0,
                category=CategoryEnum.FOOD,
                description="Kwota zerowa",
                spent_on=date.today()
            )

    def test_create_expense_invalid_category(self):
        with self.assertRaises(ValidationError):
            ExpenseCreate(
                amount=10.0,
                category="NieistniejacaKategoria",
                description="Test",
                spent_on=date.today()
            )

    def test_create_expense_future_date(self):
        future_date = date.today() + timedelta(days=1)
        with self.assertRaises(ValidationError):
            ExpenseCreate(
                amount=10.0,
                category=CategoryEnum.FOOD,
                description="Czasopodróżnik",
                spent_on=future_date
            )

    def test_get_expense_by_id(self):
        expense_data = ExpenseCreate(
            amount=20.0,
            category=CategoryEnum.TRANSPORT,
            description="Bilet autobusowy",
            spent_on=date.today()
        )
        created = self.service.create_expense(expense_data)

        fetched = self.service.get_expense_by_id(created.id)
        self.assertEqual(fetched.description, "Bilet autobusowy")

        with self.assertRaises((NotFoundException, KeyError)):
            self.service.get_expense_by_id(999)

    def test_list_expenses_with_filters(self):
        today = date.today()
        yesterday = today - timedelta(days=1)

        self.service.create_expense(ExpenseCreate(amount=10, category=CategoryEnum.FOOD, description="A", spent_on=yesterday))
        self.service.create_expense(ExpenseCreate(amount=20, category=CategoryEnum.UTILITIES, description="B", spent_on=today))

        food_expenses = self.service.list_expenses(category=CategoryEnum.FOOD)
        self.assertEqual(len(food_expenses), 1)
        self.assertEqual(food_expenses[0].description, "A")

        range_expenses = self.service.list_expenses(from_date=yesterday, to_date=yesterday)
        self.assertEqual(len(range_expenses), 1)
        self.assertEqual(range_expenses[0].description, "A")

    def test_update_expense(self):
        created = self.service.create_expense(ExpenseCreate(
            amount=100.0,
            category=CategoryEnum.ENTERTAINMENT,
            description="Bilety do kina",
            spent_on=date.today()
        ))

        update_data = ExpenseUpdate(amount=120.0, description="Bilety IMAX")
        updated = self.service.update_expense(created.id, update_data)

        self.assertEqual(updated.amount, 120.0)
        self.assertEqual(updated.description, "Bilety IMAX")
        self.assertEqual(updated.category, CategoryEnum.ENTERTAINMENT)

    def test_delete_expense(self):
        created = self.service.create_expense(ExpenseCreate(
            amount=5.0,
            category=CategoryEnum.OTHER,
            description="Guma do żucia",
            spent_on=date.today()
        ))

        self.service.delete_expense(created.id)

        with self.assertRaises((NotFoundException, KeyError)):
            self.service.get_expense_by_id(created.id)

    def test_expenses_summary(self):
        today = date.today()
        yesterday = today - timedelta(days=1)

        self.service.create_expense(ExpenseCreate(amount=50, category=CategoryEnum.FOOD, description="Obiad", spent_on=yesterday))
        self.service.create_expense(ExpenseCreate(amount=150, category=CategoryEnum.UTILITIES, description="Prąd", spent_on=today))

        summary = self.service.get_summary(from_date=yesterday, to_date=today)

        self.assertEqual(summary["total"], 200.0)
        self.assertEqual(summary["total_per_category"][CategoryEnum.FOOD], 50.0)
        self.assertEqual(summary["total_per_category"][CategoryEnum.UTILITIES], 150.0)
        self.assertEqual(summary["average_per_day"], 100.0)

    def test_update_nonexistent_expense(self):
        update_data = ExpenseUpdate(amount=50.0)
        with self.assertRaises((NotFoundException, KeyError)):
            self.service.update_expense(999, update_data)


if __name__ == "__main__":
    unittest.main()