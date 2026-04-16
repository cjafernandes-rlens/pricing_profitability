export type ProductType = "termLoan" | "revolver" | "letterOfCredit";

export type ProductInput = {
  id: string;
  name: string;
  type: ProductType;
  commitment: number;
  utilizationPct: number;
  spreadBps: number;
  transferRatePct: number;
  feeBps: number;
  feeAmount: number;
  feeInputMode: "bps" | "dollar";
  upfrontFeeBps: number;
  upfrontFeeAmount: number;
  upfrontFeeInputMode: "bps" | "dollar";
  upfrontFeeYears: number;
  pdPct?: number;
  lgdPct?: number;
  expectedLossBps: number;
  capitalBps: number;
  servicingCost: number;
};

export type RelationshipInput = {
  company: string;
  industry: string;
  sponsor: string;
  relationshipManager: string;
  riskRating: string;
  taxRatePct: number;
  capitalHurdlePct: number;
  depositsBalance: number;
  depositsSpreadBps: number;
  treasuryFees: number;
  cardsAndPaymentsFees: number;
  onboardingCost: number;
  portfolioOverhead: number;
  products: ProductInput[];
};

export type ProductResult = ProductInput & {
  averageBalance: number;
  netInterestIncome: number;
  recurringFees: number;
  annualizedUpfrontFees: number;
  totalRevenue: number;
  expectedLoss: number;
  capitalAllocated: number;
  pretaxProfit: number;
  afterTaxProfit: number;
  rarocPct: number;
  hurdleProfit: number;
  pricingGapBps: number;
};

export type RelationshipResult = {
  products: ProductResult[];
  loanRevenue: number;
  depositContribution: number;
  treasuryContribution: number;
  nonInterestIncome: number;
  totalRevenue: number;
  totalExpectedLoss: number;
  totalOperatingExpense: number;
  totalCapital: number;
  pretaxProfit: number;
  afterTaxProfit: number;
  rarocPct: number;
  hurdleProfit: number;
  profitAboveHurdle: number;
  averageExposure: number;
};

const toDecimal = (value: number) => value / 100;
const toRate = (bps: number) => bps / 10000;

export const initialRelationship: RelationshipInput = {
  company: "Summit Industrial Distribution",
  industry: "Industrial supply / logistics",
  sponsor: "Family-owned",
  relationshipManager: "A. Monroe",
  riskRating: "6 / Pass",
  taxRatePct: 26,
  capitalHurdlePct: 14,
  depositsBalance: 12_500_000,
  depositsSpreadBps: 185,
  treasuryFees: 185_000,
  cardsAndPaymentsFees: 72_000,
  onboardingCost: 95_000,
  portfolioOverhead: 140_000,
  products: [
    {
      id: "term-loan",
      name: "Term Loan A",
      type: "termLoan",
      commitment: 25_000_000,
      utilizationPct: 100,
      spreadBps: 290,
      transferRatePct: 4.35,
      feeBps: 18,
      feeAmount: 45_000,
      feeInputMode: "bps",
      upfrontFeeBps: 65,
      upfrontFeeAmount: 162_500,
      upfrontFeeInputMode: "bps",
      upfrontFeeYears: 5,
      pdPct: 1.4,
      lgdPct: 30,
      expectedLossBps: 42,
      capitalBps: 850,
      servicingCost: 110_000,
    },
    {
      id: "revolver",
      name: "Senior Revolver",
      type: "revolver",
      commitment: 18_000_000,
      utilizationPct: 48,
      spreadBps: 255,
      transferRatePct: 4.1,
      feeBps: 35,
      feeAmount: 63_000,
      feeInputMode: "bps",
      upfrontFeeBps: 40,
      upfrontFeeAmount: 72_000,
      upfrontFeeInputMode: "bps",
      upfrontFeeYears: 3,
      pdPct: 2.1,
      lgdPct: 27.62,
      expectedLossBps: 58,
      capitalBps: 950,
      servicingCost: 90_000,
    },
    {
      id: "loc",
      name: "Trade Letters of Credit",
      type: "letterOfCredit",
      commitment: 7_500_000,
      utilizationPct: 62,
      spreadBps: 0,
      transferRatePct: 0,
      feeBps: 145,
      feeAmount: 108_750,
      feeInputMode: "bps",
      upfrontFeeBps: 20,
      upfrontFeeAmount: 15_000,
      upfrontFeeInputMode: "bps",
      upfrontFeeYears: 1,
      pdPct: 1.2,
      lgdPct: 23.33,
      expectedLossBps: 28,
      capitalBps: 575,
      servicingCost: 40_000,
    },
  ],
};

export function calculateRelationship(
  input: RelationshipInput,
): RelationshipResult {
  const products = input.products.map((product) => {
    const averageBalance = product.commitment * toDecimal(product.utilizationPct);
    const recurringFees =
      product.feeInputMode === "dollar"
        ? product.feeAmount
        : averageBalance * toRate(product.feeBps) +
          (product.type === "revolver"
            ? (product.commitment - averageBalance) * toRate(product.feeBps)
            : 0);
    const annualizedUpfrontFees =
      product.upfrontFeeInputMode === "dollar"
        ? product.upfrontFeeAmount / Math.max(product.upfrontFeeYears, 1)
        : product.commitment *
          toRate(product.upfrontFeeBps) /
          Math.max(product.upfrontFeeYears, 1);
    const netInterestIncome =
      averageBalance *
      (product.type === "letterOfCredit" ? 0 : toRate(product.spreadBps));
    const totalRevenue =
      netInterestIncome + recurringFees + annualizedUpfrontFees;
    const expectedLoss = averageBalance * toRate(product.expectedLossBps);
    const capitalAllocated = averageBalance * toRate(product.capitalBps);
    const pretaxProfit =
      totalRevenue - expectedLoss - product.servicingCost;
    const afterTaxProfit = pretaxProfit * (1 - toDecimal(input.taxRatePct));
    const hurdleProfit =
      capitalAllocated * toDecimal(input.capitalHurdlePct);
    const pricingGapBps =
      averageBalance > 0
        ? Math.max(hurdleProfit - pretaxProfit, 0) / averageBalance * 10000
        : 0;

    return {
      ...product,
      averageBalance,
      netInterestIncome,
      recurringFees,
      annualizedUpfrontFees,
      totalRevenue,
      expectedLoss,
      capitalAllocated,
      pretaxProfit,
      afterTaxProfit,
      rarocPct: capitalAllocated > 0 ? (pretaxProfit / capitalAllocated) * 100 : 0,
      hurdleProfit,
      pricingGapBps,
    };
  });

  const loanRevenue = products.reduce((sum, product) => sum + product.totalRevenue, 0);
  const totalExpectedLoss = products.reduce(
    (sum, product) => sum + product.expectedLoss,
    0,
  );
  const productServicingExpense = products.reduce(
    (sum, product) => sum + product.servicingCost,
    0,
  );
  const totalCapital = products.reduce(
    (sum, product) => sum + product.capitalAllocated,
    0,
  );
  const averageExposure = products.reduce(
    (sum, product) => sum + product.averageBalance,
    0,
  );
  const depositContribution =
    input.depositsBalance * toRate(input.depositsSpreadBps);
  const treasuryContribution = input.treasuryFees + input.cardsAndPaymentsFees;
  const nonInterestIncome =
    treasuryContribution +
    products.reduce(
      (sum, product) => sum + product.recurringFees + product.annualizedUpfrontFees,
      0,
    );
  const totalRevenue = loanRevenue + depositContribution + treasuryContribution;
  const totalOperatingExpense =
    productServicingExpense + input.onboardingCost + input.portfolioOverhead;
  const pretaxProfit =
    totalRevenue -
    totalExpectedLoss -
    totalOperatingExpense;
  const afterTaxProfit = pretaxProfit * (1 - toDecimal(input.taxRatePct));
  const hurdleProfit = totalCapital * toDecimal(input.capitalHurdlePct);

  return {
    products,
    loanRevenue,
    depositContribution,
    treasuryContribution,
    nonInterestIncome,
    totalRevenue,
    totalExpectedLoss,
    totalOperatingExpense,
    totalCapital,
    pretaxProfit,
    afterTaxProfit,
    rarocPct: totalCapital > 0 ? (pretaxProfit / totalCapital) * 100 : 0,
    hurdleProfit,
    profitAboveHurdle: pretaxProfit - hurdleProfit,
    averageExposure,
  };
}
