import json, math
import numpy as np
import pandas as pd

RSI_LEN        = 14
PIVOT_STRENGTH = 3
MIN_BARS       = 5
MAX_BARS       = 60
FRESH_BARS     = 2
FRESH_LEFT     = 12
MIN_DRSI       = 3.0
MIN_DLOW_PCT   = 0.5
RSI_ZONE_REG   = 45.0
HISTORY        = "320d"
CHART_BARS     = 130

def rsi_wilder(close, length=RSI_LEN):
    delta = close.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    avg_gain = gain.ewm(alpha=1/length, min_periods=length).mean()
    avg_loss = loss.ewm(alpha=1/length, min_periods=length).mean()
    return 100 - 100/(1 + avg_gain/avg_loss)

def pivot_lows(low, strength=PIVOT_STRENGTH):
    vals = low.values; n = len(vals); out = []
    for i in range(strength, n - strength):
        win = vals[i-strength:i+strength+1]
        if vals[i] == win.min() and (win == vals[i]).sum() == 1:
            out.append(i)
    return out

def scan_symbol(df, ticker):
    df = df.dropna(subset=["Close", "Low"])
    if len(df) < 120: return []
    close, low = df["Close"], df["Low"]
    rsi = rsi_wilder(close); sma50 = close.rolling(50).mean(); n = len(df)
    pivots = [p for p in pivot_lows(low) if not math.isnan(rsi.iloc[p])]
    if not pivots: return []
    fresh = []; lv = low.values
    for p in range(n - FRESH_BARS, n):
        if p <= FRESH_LEFT or math.isnan(rsi.iloc[p]): continue
        if lv[p] == lv[p-FRESH_LEFT:n].min():
            fresh.append((p, "fruehsignal")); break
    fresh += [(p, "bestaetigt") for p in pivots if (p + PIVOT_STRENGTH) >= (n - FRESH_BARS)]
    hits = []
    for p2, status in fresh:
        for p1 in reversed([p for p in pivots if p < p2]):
            dist = p2 - p1
            if dist < MIN_BARS: continue
            if dist > MAX_BARS: break
            l1, l2 = low.iloc[p1], low.iloc[p2]
            r1, r2 = rsi.iloc[p1], rsi.iloc[p2]
            if abs(r2-r1) < MIN_DRSI or abs(l2/l1-1)*100 < MIN_DLOW_PCT: continue
            typ = None
            if l2 < l1 and r2 > r1 and min(r1, r2) < RSI_ZONE_REG: typ = "regulaer"
            elif l2 > l1 and r2 < r1 and close.iloc[-1] > sma50.iloc[-1]: typ = "versteckt"
            if typ is None: continue
            chart = df.iloc[-CHART_BARS:]; ci0 = n - len(chart)
            hits.append({
                "ticker": ticker, "typ": typ, "status": status,
                "tage_seit_tief": int(n-1-p2),
                "datum_p1": str(df.index[p1].date()), "datum_p2": str(df.index[p2].date()),
                "low_p1": round(float(l1),2), "low_p2": round(float(l2),2),
                "rsi_p1": round(float(r1),1), "rsi_p2": round(float(r2),1),
                "close": round(float(close.iloc[-1]),2),
                "rsi_aktuell": round(float(rsi.iloc[-1]),1),
                "abstand_bars": int(dist),
                "chart": {
                    "dates": [str(d.date()) for d in chart.index],
                    "close": [round(float(x),2) for x in chart["Close"]],
                    "low":   [round(float(x),2) for x in chart["Low"]],
                    "rsi":   [None if math.isnan(x) else round(float(x),1) for x in rsi.iloc[-CHART_BARS:]],
                    "p1": p1-ci0, "p2": p2-ci0,
                },
            })
            break
    return hits


def main():
    import sys
    from datetime import datetime, timezone
    import yfinance as yf
    tick_file = sys.argv[1] if len(sys.argv) > 1 else "sp500-ticker.txt"
    tickers = open(tick_file).read().split()
    yf_map = {t: t.replace(".", "-") for t in tickers}
    all_hits, failed = [], []
    syms = list(yf_map.values())
    BATCH = 100
    for i in range(0, len(syms), BATCH):
        batch = syms[i:i + BATCH]
        data = yf.download(batch, period=HISTORY, interval="1d",
                           group_by="ticker", auto_adjust=True,
                           progress=False, threads=True)
        for orig, ysym in yf_map.items():
            if ysym not in batch:
                continue
            try:
                df = data[ysym] if len(batch) > 1 else data
                if df["Close"].dropna().empty:
                    raise ValueError("keine Daten")
                all_hits.extend(scan_symbol(df, orig))
            except Exception:
                failed.append(orig)
        print(f"  {min(i+BATCH, len(syms))}/{len(syms)} gescannt, "
              f"Treffer: {len(all_hits)}", flush=True)
    result = {
        "scan_datum": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "anzahl_ticker": len(tickers),
        "fehlgeschlagen": failed,
        "treffer": all_hits,
    }
    with open("scan-ergebnis.json", "w") as f:
        json.dump(result, f, ensure_ascii=False)
    fru = sum(1 for h in all_hits if h["status"] == "fruehsignal")
    print(f"Fertig: {len(all_hits)} Treffer ({fru} Fruehsignale), "
          f"{len(failed)} ohne Daten: {failed}")


if __name__ == "__main__":
    main()
