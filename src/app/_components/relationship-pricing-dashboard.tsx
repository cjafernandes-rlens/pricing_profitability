"use client";

import { useState } from "react";
import styles from "../page.module.css";
import {
  calculateRelationship,
  initialRelationship,
  type ProductInput,
  type RelationshipInput,
} from "../_lib/relationship-model";

const currency = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

const compactCurrency = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  notation: "compact",
  maximumFractionDigits: 1,
});

const percent = new Intl.NumberFormat("en-US", {
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
});

const integer = new Intl.NumberFormat("en-US", {
  maximumFractionDigits: 0,
});

function updateProduct(
  products: ProductInput[],
  productId: string,
  field: keyof ProductInput,
  value: number,
) {
  return products.map((product) =>
    product.id === productId ? { ...product, [field]: value } : product,
  );
}

export default function RelationshipPricingDashboard() {
  const [relationship, setRelationship] =
    useState<RelationshipInput>(initialRelationship);

  const result = calculateRelationship(relationship);

  return (
    <main className={styles.page}>
      <section className={styles.overviewCard}>
        <div className={styles.hero}>
          <div className={styles.heroCopy}>
            <p className={styles.eyebrow}>Relationship Pricing and Profitability</p>
            <h1>
              Full relationship economics across term debt, revolvers, letters of
              credit, deposits, and treasury services.
            </h1>
            <p className={styles.heroText}>
              This model mirrors the way relationship-pricing platforms look past
              single-deal spread and into total wallet return, capital usage, fee
              support, and pricing gaps to hurdle.
            </p>
          </div>

          <div className={styles.heroPanel}>
            <div>
              <span className={styles.panelLabel}>Client</span>
              <strong>{relationship.company}</strong>
            </div>
            <div>
              <span className={styles.panelLabel}>Industry</span>
              <strong>{relationship.industry}</strong>
            </div>
            <div>
              <span className={styles.panelLabel}>Risk</span>
              <strong>{relationship.riskRating}</strong>
            </div>
            <div>
              <span className={styles.panelLabel}>RM</span>
              <strong>{relationship.relationshipManager}</strong>
            </div>
          </div>
        </div>

        <section className={styles.metricsGrid}>
          <MetricCard
            label="Relationship Revenue"
            value={compactCurrency.format(result.totalRevenue)}
            detail="Annual net interest, fees, deposits, and treasury"
          />
          <MetricCard
            label="Pre-Tax Profit"
            value={compactCurrency.format(result.pretaxProfit)}
            detail="After expected loss and operating cost"
          />
          <MetricCard
            label="Relationship RAROC"
            value={`${percent.format(result.rarocPct)}%`}
            detail={`Hurdle ${percent.format(relationship.capitalHurdlePct)}%`}
          />
          <MetricCard
            label="Profit Above Hurdle"
            value={compactCurrency.format(result.profitAboveHurdle)}
            detail={`${compactCurrency.format(result.totalCapital)} allocated capital`}
          />
        </section>
      </section>

      <section className={styles.workspace}>
        <div className={styles.column}>
          <div className={styles.sectionCard}>
            <div className={styles.sectionHeading}>
              <div>
                <p className={styles.sectionEyebrow}>Relationship Drivers</p>
                <h2>Core assumptions</h2>
              </div>
            </div>

            <div className={styles.formGrid}>
              <Field
                label="Deposits Balance"
                value={relationship.depositsBalance}
                suffix="$"
                onChange={(value) =>
                  setRelationship((current) => ({
                    ...current,
                    depositsBalance: value,
                  }))
                }
              />
              <Field
                label="Deposit Spread"
                value={relationship.depositsSpreadBps}
                suffix="bps"
                onChange={(value) =>
                  setRelationship((current) => ({
                    ...current,
                    depositsSpreadBps: value,
                  }))
                }
              />
              <Field
                label="Treasury Fees"
                value={relationship.treasuryFees}
                suffix="$"
                onChange={(value) =>
                  setRelationship((current) => ({
                    ...current,
                    treasuryFees: value,
                  }))
                }
              />
              <Field
                label="Cards / Payments Fees"
                value={relationship.cardsAndPaymentsFees}
                suffix="$"
                onChange={(value) =>
                  setRelationship((current) => ({
                    ...current,
                    cardsAndPaymentsFees: value,
                  }))
                }
              />
              <Field
                label="Onboarding Cost"
                value={relationship.onboardingCost}
                suffix="$"
                onChange={(value) =>
                  setRelationship((current) => ({
                    ...current,
                    onboardingCost: value,
                  }))
                }
              />
              <Field
                label="Portfolio Overhead"
                value={relationship.portfolioOverhead}
                suffix="$"
                onChange={(value) =>
                  setRelationship((current) => ({
                    ...current,
                    portfolioOverhead: value,
                  }))
                }
              />
              <Field
                label="Tax Rate"
                value={relationship.taxRatePct}
                suffix="%"
                onChange={(value) =>
                  setRelationship((current) => ({
                    ...current,
                    taxRatePct: value,
                  }))
                }
              />
              <Field
                label="Capital Hurdle"
                value={relationship.capitalHurdlePct}
                suffix="%"
                onChange={(value) =>
                  setRelationship((current) => ({
                    ...current,
                    capitalHurdlePct: value,
                  }))
                }
              />
            </div>
          </div>

          <div className={styles.sectionCard}>
            <div className={styles.sectionHeading}>
              <div>
                <p className={styles.sectionEyebrow}>Product Stack</p>
                <h2>Deal-level inputs with relationship roll-up</h2>
              </div>
            </div>

            <div className={styles.productList}>
              {relationship.products.map((product) => {
                const productResult = result.products.find(
                  (candidate) => candidate.id === product.id,
                );

                if (!productResult) {
                  return null;
                }

                return (
                  <article key={product.id} className={styles.productCard}>
                    <div className={styles.productHeader}>
                      <div>
                        <p className={styles.productType}>{product.type}</p>
                        <h3>{product.name}</h3>
                      </div>
                      <div className={styles.productScore}>
                        <span>RAROC</span>
                        <strong>{percent.format(productResult.rarocPct)}%</strong>
                      </div>
                    </div>

                    <div className={styles.formGrid}>
                      <Field
                        label="Commitment"
                        value={product.commitment}
                        suffix="$"
                        onChange={(value) =>
                          setRelationship((current) => ({
                            ...current,
                            products: updateProduct(
                              current.products,
                              product.id,
                              "commitment",
                              value,
                            ),
                          }))
                        }
                      />
                      <Field
                        label="Utilization"
                        value={product.utilizationPct}
                        suffix="%"
                        onChange={(value) =>
                          setRelationship((current) => ({
                            ...current,
                            products: updateProduct(
                              current.products,
                              product.id,
                              "utilizationPct",
                              value,
                            ),
                          }))
                        }
                      />
                      <Field
                        label="Spread"
                        value={product.spreadBps}
                        suffix="bps"
                        onChange={(value) =>
                          setRelationship((current) => ({
                            ...current,
                            products: updateProduct(
                              current.products,
                              product.id,
                              "spreadBps",
                              value,
                            ),
                          }))
                        }
                      />
                      <Field
                        label="Transfer Rate"
                        value={product.transferRatePct}
                        suffix="%"
                        step="0.01"
                        onChange={(value) =>
                          setRelationship((current) => ({
                            ...current,
                            products: updateProduct(
                              current.products,
                              product.id,
                              "transferRatePct",
                              value,
                            ),
                          }))
                        }
                      />
                      <Field
                        label="Recurring Fee"
                        value={product.feeBps}
                        suffix="bps"
                        onChange={(value) =>
                          setRelationship((current) => ({
                            ...current,
                            products: updateProduct(
                              current.products,
                              product.id,
                              "feeBps",
                              value,
                            ),
                          }))
                        }
                      />
                      <Field
                        label="Upfront Fee"
                        value={product.upfrontFeeBps}
                        suffix="bps"
                        onChange={(value) =>
                          setRelationship((current) => ({
                            ...current,
                            products: updateProduct(
                              current.products,
                              product.id,
                              "upfrontFeeBps",
                              value,
                            ),
                          }))
                        }
                      />
                      <Field
                        label="Fee Amortization"
                        value={product.upfrontFeeYears}
                        suffix="yrs"
                        onChange={(value) =>
                          setRelationship((current) => ({
                            ...current,
                            products: updateProduct(
                              current.products,
                              product.id,
                              "upfrontFeeYears",
                              value,
                            ),
                          }))
                        }
                      />
                      <Field
                        label="Expected Loss"
                        value={product.expectedLossBps}
                        suffix="bps"
                        onChange={(value) =>
                          setRelationship((current) => ({
                            ...current,
                            products: updateProduct(
                              current.products,
                              product.id,
                              "expectedLossBps",
                              value,
                            ),
                          }))
                        }
                      />
                      <Field
                        label="Capital"
                        value={product.capitalBps}
                        suffix="bps"
                        onChange={(value) =>
                          setRelationship((current) => ({
                            ...current,
                            products: updateProduct(
                              current.products,
                              product.id,
                              "capitalBps",
                              value,
                            ),
                          }))
                        }
                      />
                      <Field
                        label="Servicing Cost"
                        value={product.servicingCost}
                        suffix="$"
                        onChange={(value) =>
                          setRelationship((current) => ({
                            ...current,
                            products: updateProduct(
                              current.products,
                              product.id,
                              "servicingCost",
                              value,
                            ),
                          }))
                        }
                      />
                    </div>

                    <div className={styles.productMetrics}>
                      <ProductMetric
                        label="Average Balance"
                        value={currency.format(productResult.averageBalance)}
                      />
                      <ProductMetric
                        label="Revenue"
                        value={currency.format(productResult.totalRevenue)}
                      />
                      <ProductMetric
                        label="Pre-Tax Profit"
                        value={currency.format(productResult.pretaxProfit)}
                      />
                      <ProductMetric
                        label="Gap to Hurdle"
                        value={`${integer.format(productResult.pricingGapBps)} bps`}
                      />
                    </div>
                  </article>
                );
              })}
            </div>
          </div>
        </div>

        <div className={styles.column}>
          <div className={styles.sectionCard}>
            <div className={styles.sectionHeading}>
              <div>
                <p className={styles.sectionEyebrow}>Relationship View</p>
                <h2>Profitability bridge</h2>
              </div>
            </div>

            <div className={styles.statement}>
              <StatementRow
                label="Loan and trade finance revenue"
                value={result.loanRevenue}
              />
              <StatementRow
                label="Deposit contribution"
                value={result.depositContribution}
              />
              <StatementRow
                label="Treasury and payment fees"
                value={result.treasuryContribution}
              />
              <StatementRow
                label="Expected loss"
                value={-result.totalExpectedLoss}
                muted
              />
              <StatementRow
                label="Operating expense"
                value={-result.totalOperatingExpense}
                muted
              />
              <StatementRow
                label="Pre-tax relationship profit"
                value={result.pretaxProfit}
                strong
              />
              <StatementRow
                label="After-tax relationship profit"
                value={result.afterTaxProfit}
                strong
              />
            </div>
          </div>

          <div className={styles.sectionCard}>
            <div className={styles.sectionHeading}>
              <div>
                <p className={styles.sectionEyebrow}>Pricing Guidance</p>
                <h2>Where the relationship is carrying the deal stack</h2>
              </div>
            </div>

            <div className={styles.guidanceList}>
              {result.products.map((product) => (
                <div key={product.id} className={styles.guidanceItem}>
                  <div>
                    <strong>{product.name}</strong>
                    <p>
                      {product.pricingGapBps > 0
                        ? `Standalone economics miss hurdle by ${integer.format(product.pricingGapBps)} bps.`
                        : "Standalone economics clear the hurdle on their own."}
                    </p>
                  </div>
                  <span
                    className={
                      product.pricingGapBps > 0
                        ? styles.badgeWarn
                        : styles.badgeGood
                    }
                  >
                    {product.pricingGapBps > 0 ? "Needs support" : "Clears hurdle"}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className={styles.sectionCard}>
            <div className={styles.sectionHeading}>
              <div>
                <p className={styles.sectionEyebrow}>Portfolio Lens</p>
                <h2>Relationship balance sheet snapshot</h2>
              </div>
            </div>

            <div className={styles.snapshotGrid}>
              <Snapshot label="Average credit exposure" value={currency.format(result.averageExposure)} />
              <Snapshot label="Allocated capital" value={currency.format(result.totalCapital)} />
              <Snapshot label="Non-interest income" value={currency.format(result.nonInterestIncome)} />
              <Snapshot
                label="Deposit support rate"
                value={`${percent.format(
                  relationship.depositsBalance > 0
                    ? (result.depositContribution / relationship.depositsBalance) * 100
                    : 0,
                )}%`}
              />
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}

function MetricCard({
  label,
  value,
  detail,
}: {
  label: string;
  value: string;
  detail: string;
}) {
  return (
    <article className={styles.metricCard}>
      <span>{label}</span>
      <strong>{value}</strong>
      <p>{detail}</p>
    </article>
  );
}

function ProductMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className={styles.productMetric}>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function StatementRow({
  label,
  value,
  strong = false,
  muted = false,
}: {
  label: string;
  value: number;
  strong?: boolean;
  muted?: boolean;
}) {
  return (
    <div
      className={[
        styles.statementRow,
        strong ? styles.statementStrong : "",
        muted ? styles.statementMuted : "",
      ].join(" ")}
    >
      <span>{label}</span>
      <strong>{currency.format(value)}</strong>
    </div>
  );
}

function Snapshot({ label, value }: { label: string; value: string }) {
  return (
    <div className={styles.snapshotCard}>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function Field({
  label,
  value,
  suffix,
  onChange,
  step = "1",
}: {
  label: string;
  value: number;
  suffix: string;
  onChange: (value: number) => void;
  step?: string;
}) {
  return (
    <label className={styles.field}>
      <span>
        {label}
        <small>{suffix}</small>
      </span>
      <input
        type="number"
        step={step}
        value={Number.isFinite(value) ? value : 0}
        onChange={(event) => onChange(Number(event.target.value))}
      />
    </label>
  );
}
