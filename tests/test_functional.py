import pytest

from src.manager import Manager
from src.models import Parameters, ApartmentSettlement, TenantSettlement
from src.models import Bill


def test_tenant_settlements_sum_equals_apartment_settlement():
    parameters = Parameters()
    manager = Manager(parameters)
    
    apartment_key = "apart-polanka"
    year = 2025
    month = 1
    
    apartment_settlement = manager.get_settlement(apartment_key, year, month)
    tenant_settlements = manager.create_tenants_settlements(apartment_settlement)
    
    assert apartment_settlement is not None, "Rozliczenie mieszkania powinno istnieć"
    assert tenant_settlements is not None, "Rozliczenia lokatorów powinny istnieć"
    assert len(tenant_settlements) > 0, "Powinni być lokatorzy w mieszkaniu"
    
    total_tenants_due = sum(tenant.total_due_pln for tenant in tenant_settlements)
    
    assert (
        abs(total_tenants_due - apartment_settlement.total_due_pln) < 0.01
    ), (
        f"Suma total_due_pln lokatorów ({total_tenants_due}) powinna równać się "
        f"total_due_pln mieszkania ({apartment_settlement.total_due_pln})"
    )


def test_get_debtors():

    parameters = Parameters()
    manager = Manager(parameters)
    
    apartment_key = "apart-polanka"
    year = 2025
    month = 1
    
    debtors = manager.get_debtors(apartment_key, month, year)

    assert isinstance(debtors, list), "Metoda powinna zwrócić listę"
    assert len(debtors) == 0, "W danych testowych nie powinno być dłużników"


def test_get_tax():

    parameters = Parameters()
    manager = Manager(parameters)
    
    year = 2025
    month = 1
    tax_rate = 0.085 
    
    tax_amount = manager.get_tax(year, month, tax_rate)

    expected_tax = round(7500 * 0.085)
    
    assert isinstance(tax_amount, (int, float)), "Metoda powinna zwrócić liczbę"
    assert tax_amount == expected_tax, f"Podatek powinien wynosić {expected_tax} PLN, a wynosi {tax_amount}"