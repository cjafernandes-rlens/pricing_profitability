from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Literal

import streamlit as st

ProductType = Literal["termLoan", "revolver", "letterOfCredit"]


@dataclass(frozen=True)
class ProductInput:
    id: str
    name: str
    type: ProductType
    commitment: float
    utilization_pct: float
    spread_bps: float
    transfer_rate_pct: float
    fee_bps: float
    upfront_fee_bps: float
    upfront_fee_years: float
    expected_loss_bps: float
    capital_bps: float
    servicing_cost: float


@dataclass(frozen=True)
class RelationshipInput:
    company: str
    industry: str
    sponsor: str
    relationship_manager: str
    probability_of_default_pct: float
    risk_rating: str
    tax_rate_pct: float
    capital_hurdle_pct: float
    deposits_balance: float
    deposits_spread_bps: float
    deposit_ftp_credit_bps: float
    deposit_stability_pct: float
    treasury_fees: float
    cards_and_payments_fees: float
    onboarding_cost: float
    portfolio_overhead: float
    products: list[ProductInput]


@dataclass(frozen=True)
class ProductResult:
    input: ProductInput
    average_balance: float
    net_interest_income: float
    recurring_fees: float
    annualized_upfront_fees: float
    total_revenue: float
    expected_loss: float
    capital_allocated: float
    pretax_profit: float
    after_tax_profit: float
    raroc_pct: float
    hurdle_profit: float
    pricing_gap_bps: float


@dataclass(frozen=True)
class RelationshipResult:
    products: list[ProductResult]
    loan_revenue: float
    deposit_contribution: float
    deposit_spread_contribution: float
    deposit_ftp_contribution: float
    stable_deposit_balance: float
    treasury_contribution: float
    non_interest_income: float
    total_revenue: float
    total_expected_loss: float
    total_operating_expense: float
    total_capital: float
    pretax_profit: float
    after_tax_profit: float
    raroc_pct: float
    hurdle_profit: float
    profit_above_hurdle: float
    average_exposure: float


INITIAL_RELATIONSHIP = RelationshipInput(
    company="Summit Industrial Distribution",
    industry="Industrial supply / logistics",
    sponsor="Family-owned",
    relationship_manager="A. Monroe",
    probability_of_default_pct=0.42,
    risk_rating="6 / Pass",
    tax_rate_pct=26.0,
    capital_hurdle_pct=14.0,
    deposits_balance=12_500_000,
    deposits_spread_bps=185.0,
    deposit_ftp_credit_bps=110.0,
    deposit_stability_pct=72.0,
    treasury_fees=185_000,
    cards_and_payments_fees=72_000,
    onboarding_cost=95_000,
    portfolio_overhead=140_000,
    products=[
        ProductInput(
            id="term-loan",
            name="Term Loan A",
            type="termLoan",
            commitment=25_000_000,
            utilization_pct=100.0,
            spread_bps=290.0,
            transfer_rate_pct=4.35,
            fee_bps=18.0,
            upfront_fee_bps=65.0,
            upfront_fee_years=5.0,
            expected_loss_bps=42.0,
            capital_bps=850.0,
            servicing_cost=110_000,
        ),
        ProductInput(
            id="revolver",
            name="Senior Revolver",
            type="revolver",
            commitment=18_000_000,
            utilization_pct=48.0,
            spread_bps=255.0,
            transfer_rate_pct=4.10,
            fee_bps=35.0,
            upfront_fee_bps=40.0,
            upfront_fee_years=3.0,
            expected_loss_bps=58.0,
            capital_bps=950.0,
            servicing_cost=90_000,
        ),
        ProductInput(
            id="loc",
            name="Trade Letters of Credit",
            type="letterOfCredit",
            commitment=7_500_000,
            utilization_pct=62.0,
            spread_bps=0.0,
            transfer_rate_pct=0.0,
            fee_bps=145.0,
            upfront_fee_bps=20.0,
            upfront_fee_years=1.0,
            expected_loss_bps=28.0,
            capital_bps=575.0,
            servicing_cost=40_000,
        ),
    ],
)


def pct_to_decimal(value: float) -> float:
    return value / 100


def bps_to_decimal(value: float) -> float:
    return value / 10_000


def as_float(value: float | None) -> float:
    return float(value) if value is not None else 0.0


def map_pd_to_internal_rating(probability_of_default_pct: float) -> str:
    rating_scale = [
        (0.03, "1 / Exceptional"),
        (0.05, "2 / Minimal"),
        (0.09, "3 / Very Strong"),
        (0.18, "4 / Strong"),
        (0.35, "5 / Good"),
        (0.65, "6 / Pass"),
        (1.20, "7 / Acceptable"),
        (2.50, "8 / Watch"),
        (5.00, "9 / Special Mention"),
        (10.00, "10 / Substandard"),
        (20.00, "11 / Doubtful"),
    ]

    for upper_bound, label in rating_scale:
        if probability_of_default_pct <= upper_bound:
            return label

    return "12 / Loss"


def calculate_relationship(input_data: RelationshipInput) -> RelationshipResult:
    product_results: list[ProductResult] = []

    for product in input_data.products:
        average_balance = product.commitment * pct_to_decimal(product.utilization_pct)
        recurring_fees = average_balance * bps_to_decimal(product.fee_bps)
        if product.type == "revolver":
            recurring_fees += (
                product.commitment - average_balance
            ) * bps_to_decimal(product.fee_bps)

        annualized_upfront_fees = (
            product.commitment
            * bps_to_decimal(product.upfront_fee_bps)
            / max(product.upfront_fee_years, 1)
        )
        net_interest_income = (
            0.0
            if product.type == "letterOfCredit"
            else average_balance * bps_to_decimal(product.spread_bps)
        )
        total_revenue = net_interest_income + recurring_fees + annualized_upfront_fees
        expected_loss = average_balance * bps_to_decimal(product.expected_loss_bps)
        capital_allocated = average_balance * bps_to_decimal(product.capital_bps)
        pretax_profit = total_revenue - expected_loss - product.servicing_cost
        after_tax_profit = pretax_profit * (1 - pct_to_decimal(input_data.tax_rate_pct))
        hurdle_profit = capital_allocated * pct_to_decimal(input_data.capital_hurdle_pct)
        pricing_gap_bps = (
            max(hurdle_profit - pretax_profit, 0) / average_balance * 10_000
            if average_balance > 0
            else 0.0
        )

        product_results.append(
            ProductResult(
                input=product,
                average_balance=average_balance,
                net_interest_income=net_interest_income,
                recurring_fees=recurring_fees,
                annualized_upfront_fees=annualized_upfront_fees,
                total_revenue=total_revenue,
                expected_loss=expected_loss,
                capital_allocated=capital_allocated,
                pretax_profit=pretax_profit,
                after_tax_profit=after_tax_profit,
                raroc_pct=(pretax_profit / capital_allocated) * 100
                if capital_allocated > 0
                else 0.0,
                hurdle_profit=hurdle_profit,
                pricing_gap_bps=pricing_gap_bps,
            )
        )

    loan_revenue = sum(product.total_revenue for product in product_results)
    total_expected_loss = sum(product.expected_loss for product in product_results)
    product_servicing_expense = sum(
        product.input.servicing_cost for product in product_results
    )
    total_capital = sum(product.capital_allocated for product in product_results)
    average_exposure = sum(product.average_balance for product in product_results)
    deposit_spread_contribution = (
        input_data.deposits_balance * bps_to_decimal(input_data.deposits_spread_bps)
    )
    stable_deposit_balance = (
        input_data.deposits_balance * pct_to_decimal(input_data.deposit_stability_pct)
    )
    deposit_ftp_contribution = (
        stable_deposit_balance * bps_to_decimal(input_data.deposit_ftp_credit_bps)
    )
    deposit_contribution = deposit_spread_contribution + deposit_ftp_contribution
    treasury_contribution = (
        input_data.treasury_fees + input_data.cards_and_payments_fees
    )
    non_interest_income = treasury_contribution + sum(
        product.recurring_fees + product.annualized_upfront_fees
        for product in product_results
    )
    total_revenue = loan_revenue + deposit_contribution + treasury_contribution
    total_operating_expense = (
        product_servicing_expense
        + input_data.onboarding_cost
        + input_data.portfolio_overhead
    )
    pretax_profit = total_revenue - total_expected_loss - total_operating_expense
    after_tax_profit = pretax_profit * (1 - pct_to_decimal(input_data.tax_rate_pct))
    hurdle_profit = total_capital * pct_to_decimal(input_data.capital_hurdle_pct)

    return RelationshipResult(
        products=product_results,
        loan_revenue=loan_revenue,
        deposit_contribution=deposit_contribution,
        deposit_spread_contribution=deposit_spread_contribution,
        deposit_ftp_contribution=deposit_ftp_contribution,
        stable_deposit_balance=stable_deposit_balance,
        treasury_contribution=treasury_contribution,
        non_interest_income=non_interest_income,
        total_revenue=total_revenue,
        total_expected_loss=total_expected_loss,
        total_operating_expense=total_operating_expense,
        total_capital=total_capital,
        pretax_profit=pretax_profit,
        after_tax_profit=after_tax_profit,
        raroc_pct=(pretax_profit / total_capital) * 100 if total_capital > 0 else 0.0,
        hurdle_profit=hurdle_profit,
        profit_above_hurdle=pretax_profit - hurdle_profit,
        average_exposure=average_exposure,
    )


def format_currency(value: float) -> str:
    return f"${value:,.0f}"


def format_compact(value: float) -> str:
    abs_value = abs(value)
    if abs_value >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    if abs_value >= 1_000:
        return f"${value / 1_000:.1f}K"
    return f"${value:,.0f}"


def render_metric_card(label: str, value: str, detail: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
          <div class="metric-label">{label}</div>
          <div class="metric-value">{value}</div>
          <div class="metric-detail">{detail}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp {
          background: linear-gradient(180deg, #eef2f6 0%, #e5ecf3 100%);
        }
        .block-container {
          padding-top: 1.4rem;
          padding-bottom: 2rem;
          max-width: 1380px;
        }
        .overview-shell,
        .panel-card,
        .product-card,
        .metric-card {
          border: 1px solid #d8e1e8;
          border-radius: 22px;
          background: #ffffff;
          box-shadow: 0 10px 28px rgba(18, 33, 47, 0.06);
        }
        .overview-shell {
          padding: 1.2rem 1.2rem 0.7rem;
          margin-bottom: 1rem;
        }
        .eyebrow {
          color: #7b5b2a;
          text-transform: uppercase;
          letter-spacing: 0.16em;
          font-size: 0.68rem;
          font-weight: 700;
          margin-bottom: 0.45rem;
        }
        .hero-title {
          color: #1a2a37;
          font-size: 2.25rem;
          line-height: 1.02;
          letter-spacing: -0.05em;
          font-weight: 700;
          margin-bottom: 0.7rem;
          max-width: 11ch;
        }
        .hero-copy {
          color: #586976;
          font-size: 0.93rem;
          line-height: 1.55;
          max-width: 70ch;
          margin-bottom: 0;
        }
        .hero-info {
          display: grid;
          grid-template-columns: repeat(2, minmax(0, 1fr));
          gap: 0.75rem;
        }
        .hero-info-item {
          background: #f7fafc;
          border: 1px solid #e4ecf2;
          border-radius: 16px;
          padding: 0.85rem;
        }
        .hero-info-label {
          color: #728492;
          font-size: 0.68rem;
          text-transform: uppercase;
          letter-spacing: 0.12em;
          margin-bottom: 0.3rem;
        }
        .hero-info-value {
          color: #1f303d;
          font-size: 0.95rem;
          font-weight: 600;
        }
        .metric-card {
          padding: 1rem;
          min-height: 132px;
        }
        .metric-label {
          color: #6a7b87;
          font-size: 0.78rem;
        }
        .metric-value {
          color: #1c2b38;
          font-size: 1.55rem;
          line-height: 1.05;
          letter-spacing: -0.04em;
          font-weight: 700;
          margin: 0.45rem 0;
        }
        .metric-detail {
          color: #6b7d89;
          font-size: 0.82rem;
          line-height: 1.45;
        }
        .panel-card {
          padding: 1rem 1rem 0.4rem;
          margin-bottom: 1rem;
        }
        .panel-title {
          color: #1c2b38;
          font-size: 1.1rem;
          font-weight: 700;
          margin-bottom: 0.8rem;
        }
        .statement-row {
          display: flex;
          justify-content: space-between;
          gap: 1rem;
          padding: 0.72rem 0;
          border-bottom: 1px solid #e7edf2;
          color: #475b68;
          font-size: 0.88rem;
        }
        .statement-row strong {
          color: #1e3241;
          font-size: 0.9rem;
        }
        .product-card {
          padding: 1rem;
          margin-bottom: 0.9rem;
        }
        .product-head {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          gap: 1rem;
          margin-bottom: 0.9rem;
        }
        .product-type {
          color: #7b5b2a;
          text-transform: uppercase;
          letter-spacing: 0.14em;
          font-size: 0.66rem;
          font-weight: 700;
          margin-bottom: 0.25rem;
        }
        .product-name {
          color: #1b2c38;
          font-size: 1.05rem;
          font-weight: 700;
        }
        .raroc-pill {
          padding: 0.7rem 0.85rem;
          border-radius: 14px;
          background: #eff5f9;
          border: 1px solid #dde7ef;
          min-width: 112px;
        }
        .raroc-label {
          color: #667885;
          font-size: 0.65rem;
          text-transform: uppercase;
          letter-spacing: 0.12em;
        }
        .raroc-value {
          color: #193041;
          margin-top: 0.25rem;
          font-size: 1.18rem;
          font-weight: 700;
        }
        .guidance-item {
          border: 1px solid #e5edf3;
          border-radius: 16px;
          background: #f8fbfd;
          padding: 0.9rem;
          margin-bottom: 0.7rem;
        }
        .guidance-title {
          color: #1d2f3d;
          font-size: 0.93rem;
          font-weight: 700;
          margin-bottom: 0.25rem;
        }
        .guidance-copy {
          color: #60717d;
          font-size: 0.84rem;
          line-height: 1.45;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def build_sidebar(defaults: RelationshipInput) -> RelationshipInput:
    st.sidebar.header("Relationship Inputs")
    relationship = defaults

    probability_of_default_pct = st.sidebar.number_input(
        "Probability of Default (%)",
        min_value=0.0,
        max_value=100.0,
        value=as_float(relationship.probability_of_default_pct),
        step=0.01,
    )
    derived_risk_rating = map_pd_to_internal_rating(probability_of_default_pct)
    st.sidebar.caption(f"Mapped Internal Rating: {derived_risk_rating}")

    deposits_balance = st.sidebar.number_input(
        "Deposits Balance",
        min_value=0.0,
        value=as_float(relationship.deposits_balance),
        step=500_000.0,
    )
    deposits_spread_bps = st.sidebar.number_input(
        "Deposit Spread (bps)",
        min_value=0.0,
        value=as_float(relationship.deposits_spread_bps),
        step=5.0,
    )
    deposit_ftp_credit_bps = st.sidebar.number_input(
        "Deposit FTP Credit (bps)",
        min_value=0.0,
        value=as_float(relationship.deposit_ftp_credit_bps),
        step=5.0,
    )
    deposit_stability_pct = st.sidebar.number_input(
        "NMD Stability Weight (%)",
        min_value=0.0,
        max_value=100.0,
        value=as_float(relationship.deposit_stability_pct),
        step=1.0,
    )
    treasury_fees = st.sidebar.number_input(
        "Treasury Fees",
        min_value=0.0,
        value=as_float(relationship.treasury_fees),
        step=10_000.0,
    )
    cards_and_payments_fees = st.sidebar.number_input(
        "Cards / Payments Fees",
        min_value=0.0,
        value=as_float(relationship.cards_and_payments_fees),
        step=5_000.0,
    )
    onboarding_cost = st.sidebar.number_input(
        "Onboarding Cost",
        min_value=0.0,
        value=as_float(relationship.onboarding_cost),
        step=5_000.0,
    )
    portfolio_overhead = st.sidebar.number_input(
        "Portfolio Overhead",
        min_value=0.0,
        value=as_float(relationship.portfolio_overhead),
        step=5_000.0,
    )
    tax_rate_pct = st.sidebar.number_input(
        "Tax Rate (%)",
        min_value=0.0,
        value=as_float(relationship.tax_rate_pct),
        step=0.5,
    )
    capital_hurdle_pct = st.sidebar.number_input(
        "Capital Hurdle (%)",
        min_value=0.0,
        value=as_float(relationship.capital_hurdle_pct),
        step=0.5,
    )

    st.sidebar.header("Product Inputs")
    products: list[ProductInput] = []
    for product in relationship.products:
        with st.sidebar.expander(product.name, expanded=False):
            products.append(
                replace(
                    product,
                    commitment=st.number_input(
                        f"{product.name} Commitment",
                        min_value=0.0,
                        value=as_float(product.commitment),
                        step=500_000.0,
                        key=f"{product.id}-commitment",
                    ),
                    utilization_pct=st.number_input(
                        f"{product.name} Utilization (%)",
                        min_value=0.0,
                        max_value=100.0,
                        value=as_float(product.utilization_pct),
                        step=1.0,
                        key=f"{product.id}-utilization",
                    ),
                    spread_bps=st.number_input(
                        f"{product.name} Spread (bps)",
                        min_value=0.0,
                        value=as_float(product.spread_bps),
                        step=5.0,
                        key=f"{product.id}-spread",
                    ),
                    transfer_rate_pct=st.number_input(
                        f"{product.name} Transfer Rate (%)",
                        min_value=0.0,
                        value=as_float(product.transfer_rate_pct),
                        step=0.05,
                        key=f"{product.id}-transfer-rate",
                    ),
                    fee_bps=st.number_input(
                        f"{product.name} Recurring Fee (bps)",
                        min_value=0.0,
                        value=as_float(product.fee_bps),
                        step=5.0,
                        key=f"{product.id}-fee",
                    ),
                    upfront_fee_bps=st.number_input(
                        f"{product.name} Upfront Fee (bps)",
                        min_value=0.0,
                        value=as_float(product.upfront_fee_bps),
                        step=5.0,
                        key=f"{product.id}-upfront-fee",
                    ),
                    upfront_fee_years=st.number_input(
                        f"{product.name} Fee Amortization (years)",
                        min_value=1.0,
                        value=max(as_float(product.upfront_fee_years), 1.0),
                        step=1.0,
                        key=f"{product.id}-upfront-years",
                    ),
                    expected_loss_bps=st.number_input(
                        f"{product.name} Expected Loss (bps)",
                        min_value=0.0,
                        value=as_float(product.expected_loss_bps),
                        step=5.0,
                        key=f"{product.id}-expected-loss",
                    ),
                    capital_bps=st.number_input(
                        f"{product.name} Capital (bps)",
                        min_value=0.0,
                        value=as_float(product.capital_bps),
                        step=5.0,
                        key=f"{product.id}-capital",
                    ),
                    servicing_cost=st.number_input(
                        f"{product.name} Servicing Cost",
                        min_value=0.0,
                        value=as_float(product.servicing_cost),
                        step=5_000.0,
                        key=f"{product.id}-servicing",
                    ),
                )
            )

    return replace(
        relationship,
        probability_of_default_pct=probability_of_default_pct,
        risk_rating=derived_risk_rating,
        deposits_balance=deposits_balance,
        deposits_spread_bps=deposits_spread_bps,
        deposit_ftp_credit_bps=deposit_ftp_credit_bps,
        deposit_stability_pct=deposit_stability_pct,
        treasury_fees=treasury_fees,
        cards_and_payments_fees=cards_and_payments_fees,
        onboarding_cost=onboarding_cost,
        portfolio_overhead=portfolio_overhead,
        tax_rate_pct=tax_rate_pct,
        capital_hurdle_pct=capital_hurdle_pct,
        products=products,
    )


def main() -> None:
    st.set_page_config(
        page_title="Pricing and Profitability",
        page_icon=":bar_chart:",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_styles()

    relationship = build_sidebar(INITIAL_RELATIONSHIP)
    result = calculate_relationship(relationship)

    st.markdown('<div class="overview-shell">', unsafe_allow_html=True)
    hero_left, hero_right = st.columns([1.7, 1], gap="large")

    with hero_left:
        st.markdown('<div class="eyebrow">Relationship Pricing and Profitability</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="hero-title">Full relationship economics across loans, revolvers, and letters of credit.</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p class="hero-copy">Use this Streamlit workbench to evaluate relationship revenue, expected loss, capital consumption, fee support, and pricing shortfall to hurdle across the entire client wallet instead of only the lead deal.</p>',
            unsafe_allow_html=True,
        )

    with hero_right:
        st.markdown(
            f"""
            <div class="hero-info">
              <div class="hero-info-item">
                <div class="hero-info-label">Client</div>
                <div class="hero-info-value">{relationship.company}</div>
              </div>
              <div class="hero-info-item">
                <div class="hero-info-label">Industry</div>
                <div class="hero-info-value">{relationship.industry}</div>
              </div>
              <div class="hero-info-item">
                <div class="hero-info-label">Risk</div>
                <div class="hero-info-value">{relationship.risk_rating}</div>
              </div>
              <div class="hero-info-item">
                <div class="hero-info-label">PD</div>
                <div class="hero-info-value">{relationship.probability_of_default_pct:.2f}%</div>
              </div>
              <div class="hero-info-item">
                <div class="hero-info-label">RM</div>
                <div class="hero-info-value">{relationship.relationship_manager}</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

    metric_cols = st.columns(4, gap="medium")
    with metric_cols[0]:
        render_metric_card(
            "Relationship Revenue",
            format_compact(result.total_revenue),
            "Annual net interest, fees, deposit spread, FTP credit, and treasury contribution.",
        )
    with metric_cols[1]:
        render_metric_card(
            "Pre-Tax Profit",
            format_compact(result.pretax_profit),
            "After expected loss and operating expense.",
        )
    with metric_cols[2]:
        render_metric_card(
            "Relationship RAROC",
            f"{result.raroc_pct:.1f}%",
            f"Hurdle {relationship.capital_hurdle_pct:.1f}%.",
        )
    with metric_cols[3]:
        render_metric_card(
            "Profit Above Hurdle",
            format_compact(result.profit_above_hurdle),
            f"{format_compact(result.total_capital)} allocated capital.",
        )

    left_col, right_col = st.columns([1.35, 0.95], gap="large")

    with left_col:
        st.markdown('<div class="panel-card"><div class="panel-title">Product Stack</div>', unsafe_allow_html=True)
        for product in result.products:
            guidance = (
                f"Standalone economics miss hurdle by {product.pricing_gap_bps:,.0f} bps."
                if product.pricing_gap_bps > 0
                else "Standalone economics clear the hurdle."
            )
            st.markdown(
                f"""
                <div class="product-card">
                  <div class="product-head">
                    <div>
                      <div class="product-type">{product.input.type}</div>
                      <div class="product-name">{product.input.name}</div>
                    </div>
                    <div class="raroc-pill">
                      <div class="raroc-label">RAROC</div>
                      <div class="raroc-value">{product.raroc_pct:.1f}%</div>
                    </div>
                  </div>
                """,
                unsafe_allow_html=True,
            )

            product_metrics = st.columns(4, gap="small")
            with product_metrics[0]:
                st.metric("Average Balance", format_currency(product.average_balance))
            with product_metrics[1]:
                st.metric("Revenue", format_currency(product.total_revenue))
            with product_metrics[2]:
                st.metric("Pre-Tax Profit", format_currency(product.pretax_profit))
            with product_metrics[3]:
                st.metric("Gap to Hurdle", f"{product.pricing_gap_bps:,.0f} bps")

            st.caption(guidance)
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with right_col:
        st.markdown('<div class="panel-card"><div class="panel-title">Profitability Bridge</div>', unsafe_allow_html=True)
        for label, value in [
            ("Loan and trade finance revenue", result.loan_revenue),
            ("Deposit spread contribution", result.deposit_spread_contribution),
            ("Deposit FTP credit", result.deposit_ftp_contribution),
            ("Total deposit contribution", result.deposit_contribution),
            ("Treasury and payment fees", result.treasury_contribution),
            ("Expected loss", -result.total_expected_loss),
            ("Operating expense", -result.total_operating_expense),
            ("Pre-tax relationship profit", result.pretax_profit),
            ("After-tax relationship profit", result.after_tax_profit),
        ]:
            st.markdown(
                f'<div class="statement-row"><span>{label}</span><strong>{format_currency(value)}</strong></div>',
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="panel-card"><div class="panel-title">Pricing Guidance</div>', unsafe_allow_html=True)
        for product in result.products:
            status = (
                f"Needs relationship support. Shortfall to hurdle is {product.pricing_gap_bps:,.0f} bps."
                if product.pricing_gap_bps > 0
                else "Clears hurdle on standalone economics."
            )
            st.markdown(
                f"""
                <div class="guidance-item">
                  <div class="guidance-title">{product.input.name}</div>
                  <div class="guidance-copy">{status}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="panel-card"><div class="panel-title">Relationship Snapshot</div>', unsafe_allow_html=True)
        snap_cols = st.columns(2, gap="small")
        with snap_cols[0]:
            st.metric("Average Credit Exposure", format_currency(result.average_exposure))
            st.metric("Non-Interest Income", format_currency(result.non_interest_income))
        with snap_cols[1]:
            st.metric("Allocated Capital", format_currency(result.total_capital))
            st.metric("Stable NMD Balance", format_currency(result.stable_deposit_balance))
            deposit_support_rate = (
                (result.deposit_contribution / relationship.deposits_balance) * 100
                if relationship.deposits_balance > 0
                else 0.0
            )
            st.metric("Deposit Support Rate", f"{deposit_support_rate:.2f}%")
        st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
