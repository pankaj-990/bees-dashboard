# BeES Weekly Dashboard

Streamlit app that downloads weekly data from Yahoo Finance using `yfinance`, and plots close price with a 30-week SMA for:

- Nifty BeES
- Bank BeES
- Gold BeES
- Silver BeES
- Hang Seng BeES
- MON 100

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Notes

- If any symbol doesn't return data in your region/account, edit it in the sidebar.
- Weekly data uses `interval="1wk"` and `auto_adjust=True`.
