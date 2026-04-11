"use client";

import { useMemo, useState } from "react";
import styles from "./page.module.css";

type Mode = "dark" | "light";

type MarketTile = {
  symbol: string;
  last: string;
  change: string;
  trend: "up" | "down";
};

const marketTape: MarketTile[] = [
  { symbol: "UST 10Y", last: "4.18%", change: "+0.04", trend: "up" },
  { symbol: "SOFR", last: "5.08%", change: "+0.01", trend: "up" },
  { symbol: "DXY", last: "103.44", change: "-0.22", trend: "down" },
  { symbol: "CDX IG", last: "57.1", change: "-1.8", trend: "down" },
];

const metrics = [
  { label: "Relationship RAROC", value: "14.2%", footnote: "Target 12.0%" },
  { label: "Pre-tax Profit", value: "$42.6M", footnote: "YTD Run Rate" },
  { label: "Economic Capital", value: "$79.3M", footnote: "Basel View" },
  { label: "Pricing Gap", value: "+18 bps", footnote: "vs hurdle" },
];

export default function Home() {
  const [mode, setMode] = useState<Mode>("dark");

  const modeCopy = useMemo(
    () => (mode === "dark" ? "Switch to Light" : "Switch to Dark"),
    [mode],
  );

  return (
    <div className={styles.terminal} data-theme={mode}>
      <header className={styles.topbar}>
        <div>
          <p className={styles.kicker}>PRICING & PROFITABILITY MONITOR</p>
          <h1>Relationship Analytics Terminal</h1>
        </div>
        <button
          type="button"
          className={styles.modeButton}
          onClick={() => setMode((prev) => (prev === "dark" ? "light" : "dark"))}
        >
          {modeCopy}
        </button>
      </header>

      <section className={styles.ticker} aria-label="Market tape">
        {marketTape.map((tile) => (
          <article key={tile.symbol} className={styles.tickerTile}>
            <span>{tile.symbol}</span>
            <strong>{tile.last}</strong>
            <em data-trend={tile.trend}>{tile.change}</em>
          </article>
        ))}
      </section>

      <section className={styles.grid} aria-label="Relationship metrics">
        {metrics.map((metric) => (
          <article key={metric.label} className={styles.metricCard}>
            <span>{metric.label}</span>
            <strong>{metric.value}</strong>
            <p>{metric.footnote}</p>
          </article>
        ))}
      </section>
    </div>
  );
}
