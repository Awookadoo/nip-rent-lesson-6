from src.models import Apartment, Bill, Parameters, Tenant, TenantSettlement, Transfer, ApartmentSettlement
from typing import List, Tuple

class Manager:
    def __init__(self, parameters: Parameters):
        self.parameters = parameters 

        self.apartments = {}
        self.tenants = {}
        self.transfers = []
        self.bills = []
       
        self.load_data()

    def load_data(self):
        self.apartments = Apartment.from_json_file(self.parameters.apartments_json_path)
        self.tenants = Tenant.from_json_file(self.parameters.tenants_json_path)
        self.transfers = Transfer.from_json_file(self.parameters.transfers_json_path)
        self.bills = Bill.from_json_file(self.parameters.bills_json_path)

    def check_tenants_apartment_keys(self) -> bool:
        for tenant in self.tenants.values():
            if tenant.apartment not in self.apartments:
                return False
        return True

    def get_apartment_costs(self, apartment_key: str, year: int = None, month: int = None) -> float | None:
        if month is not None and (month < 1 or month > 12):
            raise ValueError("Month must be between 1 and 12")
        if apartment_key not in self.apartments:
            return None
        total_cost = 0.0
        for bill in self.bills:
            if bill.apartment == apartment_key and (year is None or bill.settlement_year == year) and (month is None or bill.settlement_month == month):
                total_cost += bill.amount_pln
        return total_cost

    def get_settlement(self, apartment_key: str, year: int, month: int) -> ApartmentSettlement | None:
        if month < 1 or month > 12:
            raise ValueError("Month must be between 1 and 12")
        if apartment_key not in self.apartments:
            return None
        total_cost = self.get_apartment_costs(apartment_key, year, month)
        if total_cost is None:
            return None
        
        return ApartmentSettlement(
            key=f"{apartment_key}-{year}-{month}",
            apartment=apartment_key,
            year=year,
            month=month,
            total_due_pln=total_cost
        )
    
    def create_tenants_settlements(self, apartment_settlement: ApartmentSettlement) -> List[TenantSettlement] | None:
        if apartment_settlement.month < 1 or apartment_settlement.month > 12:
            raise ValueError("Month must be between 1 and 12")
        if apartment_settlement.apartment not in self.apartments:
            return None
        tenants_in_apartment = [tenant for tenant in self.tenants.values() if tenant.apartment == apartment_settlement.apartment]
        if not tenants_in_apartment:
            return []
        
        return [
            TenantSettlement(
                tenant=tenant.name,
                apartment_settlement=apartment_settlement.key,
                month=apartment_settlement.month,
                year=apartment_settlement.year,
                total_due_pln=apartment_settlement.total_due_pln / len(tenants_in_apartment)
            )
        for tenant in tenants_in_apartment ]

    def get_debtors(self, apartment_key: str, month: int, year: int) -> List[str]:
        """
        Zwraca listę lokatorów, których suma przelewów w danym miesiącu jest mniejsza niż ich czynsz.
        """
        if month < 1 or month > 12:
            raise ValueError("Month must be between 1 and 12")
        if apartment_key not in self.apartments:
            return []
        
        debtors = []
        tenants_in_apartment = [tenant for tenant in self.tenants.values() if tenant.apartment == apartment_key]
        
        for tenant in tenants_in_apartment:
            # Znajdź klucz tenanta (np. "tenant-1")
            tenant_key = None
            for key, t in self.tenants.items():
                if t == tenant:
                    tenant_key = key
                    break
            
            if tenant_key is None:
                continue
            
            # Suma przelewów dla tego lokatora w danym miesiącu/roku
            total_transfers = sum(
                transfer.amount_pln for transfer in self.transfers
                if transfer.tenant == tenant_key and 
                   transfer.settlement_year == year and 
                   transfer.settlement_month == month
            )
            
            # Jeśli suma przelewów < czynsz, to dłużnik
            if total_transfers < tenant.rent_pln:
                debtors.append(tenant.name)
        
        return debtors

    def get_tax(self, year: int, month: int, tax_rate: float) -> float:
        """
        Zwraca sumę przychodów wymnożoną przez stawkę podatku i zaokrągloną do pełnych złotych.
        Każdy przelew jest opodatkowany.
        """
        if month < 1 or month > 12:
            raise ValueError("Month must be between 1 and 12")
        
        # Suma wszystkich przelewów w danym miesiącu/roku
        total_income = sum(
            transfer.amount_pln for transfer in self.transfers
            if transfer.settlement_year == year and transfer.settlement_month == month
        )
        
        # Oblicz podatek i zaokrąglij do pełnych złotych
        tax_amount = total_income * tax_rate
        return round(tax_amount) 
    
    