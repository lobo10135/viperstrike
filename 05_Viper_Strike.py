import streamlit as st
import yfinance as yf
import pandas as pd
import os
from datetime import timedelta

# Seiten-Konfiguration
st.set_page_config(page_title="Viper Strike", layout="wide")

_, col_center, _ = st.columns([1, 2, 1])

with col_center:
    if os.path.exists("bulle.jpg"):
        st.image("bulle.jpg", use_container_width=True)

    st.markdown("### 🐍 Viper Strike")

    def get_market_data(ticker, name, rb_threshold_pct, stop_buy_offset_pct, stop_points, tp_points, hold_weeks, filter_months):
        try:
            data = yf.Ticker(ticker).history(period="3mo", interval="1wk")
            if data.empty or len(data) < 2: return None
            
            w0 = data.iloc[-1]
            if filter_months and w0.name.month in filter_months: return None
            
            rb = abs(w0['Close'] - w0['Open'])
            rng = abs(w0['High'] - w0['Low'])
            rb_pct = ((rb / rng) * 100) if rng != 0 else 0.0
            is_met = rb_pct < rb_threshold_pct
            
            # Stop Buy: Schlusskurs + (Range * Prozent-Offset)
            stop_buy = w0['Close'] + (rng * stop_buy_offset_pct)
            
            # Absolute Punktberechnung
            stop_calc = stop_buy - stop_points
            tp_calc = stop_buy + tp_points
            
            hold_days = (hold_weeks * 7) if hold_weeks > 0 else 7
            end_date = (w0.name + timedelta(days=hold_days)).strftime("%d.%m.%Y") if is_met else "-"
            
            def fmt(v): return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            
            return {
                "Markt": name,
                "Real Body %": f"{rb_pct:.2f}%".replace(".", ","),
                "Stop Buy": fmt(stop_buy) if is_met else "-",
                "Stop": fmt(stop_calc) if is_met else "-",
                "TP": fmt(tp_calc) if is_met else "-",
                "Haltedauer": end_date
            }
        except: return None

    if st.button("Analyse starten"):
        # Liste: (Ticker, Name, RB_Limit, StopBuy_Offset, Stop_Punkte, TP_Punkte, Hold_Weeks, Filter)
        markets = [
            ("ES=F", "S&P 500", 20, 0.10, 420, 420, 4, None),
            ("^GDAXI", "FDAX", 60, 0.50, 2000, 2000, 5, None),
            ("NQ=F", "Nasdaq", 70, 0.10, 2250, 2750, 10, [9]),
            ("YM=F", "Dow Jones", 50, 0.10, 6600, 6600, 2, None),
            ("^STOXX50E", "EuroStoxx 50", 50, 0.10, 1000, 1000, 4, [1, 6]),
            ("RTY=F", "Russell 2000", 50, 0.20, 400, 240, 4, None),
            ("ZB=F", "T-Bond", 30, 0.20, 10, 10, 2, [1, 10]),
            ("ZN=F", "10yr T-Notes", 60, 0.10, 8, 8, 3, [3, 4]),
            ("DE10Y-F", "Bund Future", 70, 0.40, 11, 7, 5, [5, 11]),
            ("GC=F", "Gold", 60, 0.20, 140, 170, 0, None),
            ("SI=F", "Silber", 70, 0.50, 1.4, 4.6, 0, [6]),
            ("PL=F", "Platin", 40, 0.90, 280, 700, 5, [2, 6, 11]),
            ("PA=F", "Palladium", 70, 0.60, 250, 500, 1, [8]),
            ("HG=F", "Copper", 70, 0.40, 0.48, 0.40, 0, [8])
        ]
        
        results = [get_market_data(*m) for m in markets]
        results = [r for r in results if r]
        
        if results:
            st.dataframe(pd.DataFrame(results), use_container_width=True, hide_index=True)
        else:
            st.error("Datenabruf für einige Märkte fehlgeschlagen.")
