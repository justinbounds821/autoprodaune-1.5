/**
 * Tax Calculator Manager - Business Logic Layer
 * Single Responsibility: Manage tax calculations and regulations
 * File Length: < 200 lines ✅
 */

export interface TaxCalculation {
  id: string;
  invoice_amount: number;
  tax_rate: number;
  tax_amount: number;
  net_amount: number;
  gross_amount: number;
  tax_type: 'vat' | 'income' | 'social' | 'health';
  period: string;
  created_at: string;
}

export interface TaxSettings {
  vat_rate: number;
  income_tax_rate: number;
  social_contributions_rate: number;
  health_insurance_rate: number;
  tax_year: number;
  currency: string;
}

export interface TaxReport {
  period: string;
  total_revenue: number;
  total_taxes: number;
  breakdown: {
    vat: number;
    income_tax: number;
    social_contributions: number;
    health_insurance: number;
  };
  net_profit: number;
}

export class TaxCalculatorManager {
  private settings: TaxSettings = {
    vat_rate: 0.19, // 19% VAT
    income_tax_rate: 0.10, // 10% Income Tax
    social_contributions_rate: 0.35, // 35% Social Contributions
    health_insurance_rate: 0.10, // 10% Health Insurance
    tax_year: 2025,
    currency: 'RON'
  };

  private calculations: TaxCalculation[] = [];

  getSettings(): TaxSettings {
    return { ...this.settings };
  }

  updateSettings(newSettings: Partial<TaxSettings>): void {
    this.settings = { ...this.settings, ...newSettings };
  }

  calculateVAT(amount: number, isIncludingVAT: boolean = false): TaxCalculation {
    const vatRate = this.settings.vat_rate;
    
    let netAmount: number;
    let taxAmount: number;
    let grossAmount: number;

    if (isIncludingVAT) {
      grossAmount = amount;
      netAmount = amount / (1 + vatRate);
      taxAmount = grossAmount - netAmount;
    } else {
      netAmount = amount;
      taxAmount = amount * vatRate;
      grossAmount = netAmount + taxAmount;
    }

    const calculation: TaxCalculation = {
      id: Date.now().toString(),
      invoice_amount: amount,
      tax_rate: vatRate,
      tax_amount: Math.round(taxAmount * 100) / 100,
      net_amount: Math.round(netAmount * 100) / 100,
      gross_amount: Math.round(grossAmount * 100) / 100,
      tax_type: 'vat',
      period: new Date().toISOString().slice(0, 7), // YYYY-MM
      created_at: new Date().toISOString()
    };

    this.calculations.push(calculation);
    return calculation;
  }

  calculateIncomeTax(grossIncome: number): TaxCalculation {
    const taxRate = this.settings.income_tax_rate;
    const taxAmount = grossIncome * taxRate;
    const netAmount = grossIncome - taxAmount;

    const calculation: TaxCalculation = {
      id: Date.now().toString(),
      invoice_amount: grossIncome,
      tax_rate: taxRate,
      tax_amount: Math.round(taxAmount * 100) / 100,
      net_amount: Math.round(netAmount * 100) / 100,
      gross_amount: grossIncome,
      tax_type: 'income',
      period: new Date().toISOString().slice(0, 7),
      created_at: new Date().toISOString()
    };

    this.calculations.push(calculation);
    return calculation;
  }

  calculateSocialContributions(grossIncome: number): TaxCalculation {
    const taxRate = this.settings.social_contributions_rate;
    const taxAmount = grossIncome * taxRate;
    const netAmount = grossIncome - taxAmount;

    const calculation: TaxCalculation = {
      id: Date.now().toString(),
      invoice_amount: grossIncome,
      tax_rate: taxRate,
      tax_amount: Math.round(taxAmount * 100) / 100,
      net_amount: Math.round(netAmount * 100) / 100,
      gross_amount: grossIncome,
      tax_type: 'social',
      period: new Date().toISOString().slice(0, 7),
      created_at: new Date().toISOString()
    };

    this.calculations.push(calculation);
    return calculation;
  }

  calculateHealthInsurance(grossIncome: number): TaxCalculation {
    const taxRate = this.settings.health_insurance_rate;
    const taxAmount = grossIncome * taxRate;
    const netAmount = grossIncome - taxAmount;

    const calculation: TaxCalculation = {
      id: Date.now().toString(),
      invoice_amount: grossIncome,
      tax_rate: taxRate,
      tax_amount: Math.round(taxAmount * 100) / 100,
      net_amount: Math.round(netAmount * 100) / 100,
      gross_amount: grossIncome,
      tax_type: 'health',
      period: new Date().toISOString().slice(0, 7),
      created_at: new Date().toISOString()
    };

    this.calculations.push(calculation);
    return calculation;
  }

  calculateAllTaxes(grossIncome: number): TaxReport {
    const incomeTax = this.calculateIncomeTax(grossIncome);
    const socialContributions = this.calculateSocialContributions(grossIncome);
    const healthInsurance = this.calculateHealthInsurance(grossIncome);

    const totalTaxes = incomeTax.tax_amount + socialContributions.tax_amount + healthInsurance.tax_amount;
    const netProfit = grossIncome - totalTaxes;

    return {
      period: new Date().toISOString().slice(0, 7),
      total_revenue: grossIncome,
      total_taxes: Math.round(totalTaxes * 100) / 100,
      breakdown: {
        vat: 0, // VAT calculated separately per invoice
        income_tax: Math.round(incomeTax.tax_amount * 100) / 100,
        social_contributions: Math.round(socialContributions.tax_amount * 100) / 100,
        health_insurance: Math.round(healthInsurance.tax_amount * 100) / 100
      },
      net_profit: Math.round(netProfit * 100) / 100
    };
  }

  getCalculationsByPeriod(period: string): TaxCalculation[] {
    return this.calculations.filter(calc => calc.period === period);
  }

  getCalculationsByType(taxType: TaxCalculation['tax_type']): TaxCalculation[] {
    return this.calculations.filter(calc => calc.tax_type === taxType);
  }

  getAllCalculations(): TaxCalculation[] {
    return [...this.calculations];
  }

  clearCalculations(): void {
    this.calculations = [];
  }
}
