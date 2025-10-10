import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from services.api.app.services.financial.service import FinancialService


class StubSupabaseService:
    def __init__(self):
        self.tables = {
            'api_costs': [
                {
                    'id': 1,
                    'provider': 'OpenAI',
                    'operation': 'chat',
                    'cost': 120.0,
                    'timestamp': '2025-01-01T10:00:00Z',
                    'metadata': {'category': 'AI'}
                },
                {
                    'id': 2,
                    'provider': 'Meta',
                    'operation': 'ads',
                    'cost': 80.0,
                    'timestamp': '2025-01-02T10:00:00Z',
                    'metadata': {'category': 'Marketing'}
                },
            ],
            'revenues': [
                {
                    'id': 1,
                    'source': 'ClientA',
                    'amount': 500.0,
                    'timestamp': '2025-01-01T15:00:00Z',
                    'metadata': {'category': 'Legal Services'}
                },
                {
                    'id': 2,
                    'source': 'ClientB',
                    'amount': 450.0,
                    'timestamp': '2025-01-02T16:00:00Z',
                    'metadata': {'category': 'Legal Services'}
                },
            ],
            'cost_categories': [],
            'invoices': [
                {
                    'id': 'inv-1',
                    'number': 'INV-1',
                    'client_name': 'Test Client',
                    'client_email': 'client@example.com',
                    'client_address': 'Str. Exemplu 1',
                    'due_date': '2025-02-01',
                    'tax_rate': 0.19,
                    'subtotal': 1000.0,
                    'tax_amount': 190.0,
                    'total': 1190.0,
                    'items': [{'description': 'Serviciu', 'quantity': 1, 'total': 1000.0}],
                    'notes': None,
                    'created_at': '2025-01-01T12:00:00Z'
                }
            ]
        }

    def _table_select(self, table: str, *_cols, filters=None, order=None, limit=None):
        data = list(self.tables.get(table, []))
        if filters:
            for op, field, value in filters:
                if op == 'eq':
                    data = [row for row in data if row.get(field) == value]
        if order:
            key, desc = order
            data.sort(key=lambda row: row.get(key), reverse=desc)
        if limit:
            data = data[:limit]
        return data

    def _table_insert(self, table: str, payload: dict):
        self.tables.setdefault(table, []).append(payload)
        return payload

    def _table_update_eq(self, table: str, field: str, value, payload: dict):
        updated = []
        for row in self.tables.get(table, []):
            if row.get(field) == value:
                row.update(payload)
                updated.append(row)
        return updated

    def _table_delete_eq(self, table: str, field: str, value):
        rows = self.tables.get(table, [])
        before = len(rows)
        self.tables[table] = [row for row in rows if row.get(field) != value]
        return {"success": True, "deleted": before - len(self.tables[table])}


@pytest.fixture
def financial_service():
    return FinancialService(StubSupabaseService())


def test_financial_breakdown(financial_service):
    breakdown = financial_service.financial_breakdown(period='7d')
    assert breakdown['costs']['total'] == 200.0
    assert breakdown['revenue']['total'] == 950.0
    assert breakdown['profitability']['net_profit'] == 750.0
    assert len(breakdown['timeline']) == 2


def test_financial_forecast(financial_service):
    forecast = financial_service.financial_forecast(period='7d')
    assert 'averages' in forecast
    assert 'forecasts' in forecast
    assert forecast['forecasts']['7d']['revenue'] >= 0


def test_profit_loss_report(financial_service):
    report = financial_service.profit_loss_report(period='7d')
    assert report['total_revenue'] == 950.0
    assert report['total_costs'] == 200.0
    assert report['avg_daily_profit'] >= 0
    assert isinstance(report['daily_metrics'], list)


def test_cost_category_management(financial_service):
    defaults = financial_service.list_cost_categories()
    assert defaults, "Default categories should be returned when table empty"
    created = financial_service.create_cost_category({
        'name': 'Test Category',
        'budget_cap': 1000,
        'color': '#ffffff'
    })
    assert created['name'] == 'Test Category'
    financial_service.assign_cost_category(1, created['slug'])
    financial_service.delete_cost_category(created['slug'])


def test_generate_invoice_pdf(financial_service):
    pdf_bytes, invoice = financial_service.generate_invoice_pdf('inv-1')
    assert invoice['id'] == 'inv-1'
    assert pdf_bytes.startswith(b'%PDF')
