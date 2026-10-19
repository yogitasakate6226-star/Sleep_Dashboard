
import streamlit as st
import pandas as pd
from datetime import datetime, date, time, timedelta
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Sleep Monitoring Dashboard",
    page_icon="🌙",
    layout="wide"
)

FILE = Path(__file__).with_name("sleep_records.csv")

# Custom CSS
st.markdown("""
<style>
.stApp {
    background-color: #f1f4fb;
}
h1, h2, h3 {
    color: #26386a;
}
[data-testid="stMetric"] {
    background-color: white;
    padding: 15px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# Load saved records
def load_data():
    columns = [
        "Date", "Bedtime", "Wake Up",
        "Sleep Hours", "Sleep Quality", "Notes"
    ]

    if FILE.exists():
        data = pd.read_csv(FILE)
        for column in columns:
            if column not in data.columns:
                data[column] = ""
        return data[columns]

    return pd.DataFrame(columns=columns)

if "records" not in st.session_state:
    st.session_state.records = load_data()

# Sidebar
st.sidebar.title("🌙 Sleep Tracker")
page = st.sidebar.radio(
    "Choose a page",
    ["Dashboard", "Add Sleep Record", "Sleep History", "Sleep Tips"]
)

# Header
st.title("🌙 Sleep Schedule & Quality Monitoring")
st.write("Track your sleep schedule and monitor sleep quality.")

df = st.session_state.records.copy()

# Dashboard
if page == "Dashboard":
    st.header("📊 Sleep Overview")

    if df.empty:
        st.info("No records found. Add your first sleep record.")
    else:
        df["Sleep Hours"] = pd.to_numeric(
            df["Sleep Hours"], errors="coerce"
        )
        df["Sleep Quality"] = pd.to_numeric(
            df["Sleep Quality"], errors="coerce"
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Average Sleep",
            f"{df['Sleep Hours'].mean():.1f} hours"
        )
        c2.metric(
            "Average Quality",
            f"{df['Sleep Quality'].mean():.1f}/5"
        )
        c3.metric("Total Records", len(df))

        st.subheader("Sleep Duration Trend")
        chart = df.copy()
        chart["Date"] = pd.to_datetime(chart["Date"])
        chart = chart.sort_values("Date").set_index("Date")
        st.line_chart(chart["Sleep Hours"])

        st.subheader("Sleep Quality Trend")
        st.bar_chart(chart["Sleep Quality"])

        st.subheader("Recent Sleep Records")
        st.dataframe(df.tail(7), use_container_width=True)

        if df["Sleep Hours"].mean() < 7:
            st.warning(
                "Your average sleep is below 7 hours. "
                "Review your sleep routine and age-specific sleep needs."
            )
        else:
            st.success(
                "Your average sleep is at least 7 hours. "
                "Try to maintain a regular sleep routine."
            )

# Add record
elif page == "Add Sleep Record":
    st.header("➕ Add Sleep Record")

    with st.form("sleep_form"):
        sleep_date = st.date_input("Sleep date", value=date.today())

        col1, col2 = st.columns(2)

        with col1:
            bedtime = st.time_input(
                "Bedtime", value=time(22, 30)
            )

        with col2:
            wakeup = st.time_input(
                "Wake-up time", value=time(6, 30)
            )

        quality = st.slider(
            "Sleep quality (1 = Poor, 5 = Excellent)",
            1, 5, 3
        )

        notes = st.text_area("Notes (optional)")

        submitted = st.form_submit_button("Save Sleep Record")

        if submitted:
            start = datetime.combine(sleep_date, bedtime)
            end = datetime.combine(sleep_date, wakeup)

            if end <= start:
                end += timedelta(days=1)

            hours = (end - start).total_seconds() / 3600

            if hours <= 0 or hours > 24:
                st.error("Please enter a valid sleep duration.")
            else:
                new_record = {
                    "Date": str(sleep_date),
                    "Bedtime": bedtime.strftime("%H:%M"),
                    "Wake Up": wakeup.strftime("%H:%M"),
                    "Sleep Hours": round(hours, 2),
                    "Sleep Quality": quality,
                    "Notes": notes
                }

                records = st.session_state.records.copy()

                records = records[
                    records["Date"].astype(str) != str(sleep_date)
                ]

                records = pd.concat(
                    [records, pd.DataFrame([new_record])],
                    ignore_index=True
                )

                records = records.sort_values("Date")
                records.to_csv(FILE, index=False)

                st.session_state.records = records
                st.success(
                    f"Record saved successfully! "
                    f"Sleep duration: {hours:.2f} hours."
                )

# History
elif page == "Sleep History":
    st.header("📅 Sleep History")

    if df.empty:
        st.info("No sleep records available.")
    else:
        st.dataframe(df, use_container_width=True)

        st.download_button(
            "Download Sleep History as CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="sleep_records.csv",
            mime="text/csv"
        )

        if st.button("Delete All Records"):
            st.session_state.records = pd.DataFrame(
                columns=[
                    "Date", "Bedtime", "Wake Up",
                    "Sleep Hours", "Sleep Quality", "Notes"
                ]
            )
            FILE.unlink(missing_ok=True)
            st.rerun()

# Sleep tips
elif page == "Sleep Tips":
    st.header("🌿 Healthy Sleep Tips")

    st.markdown("""
    1. Maintain a regular bedtime and wake-up time.
    2. Keep your bedroom quiet, dark, and comfortable.
    3. Reduce screen use before bedtime.
    4. Avoid caffeine late in the day.
    5. Follow a relaxing bedtime routine.
    6. Seek professional advice if sleep problems persist.
    """)

    st.info(
        "This application tracks self-reported sleep data. "
        "It does not diagnose sleep disorders."
    )

st.markdown("---")
st.caption("Sleep Monitoring Dashboard | Python Project")
