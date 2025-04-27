import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import pandas as pd
import streamlit as st
from faker import Faker

# ======================
# 1. Synthetic Data Generator
# ======================
class SyntheticDataGenerator:
    def __init__(self):
        self.fake = Faker()
        self.products = ["Product A", "Product B", "Product C"]
        self.stages = ["Prospecting", "Qualification", "Demo", "Proposal", "Negotiation", "Closed Won", "Closed Lost"]

    def generate_leads(self, count=100):
        return [{
            "id": f"L{1000 + i}",
            "name": self.fake.company(),
            "source": random.choice(["Web", "Referral", "Event", "Cold Call"]),
            "date": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d"),
            "status": random.choice(["New", "Contacted", "Qualified", "Disqualified"])
        } for i in range(count)]

    def generate_opportunities(self, count=50):
        return [{
            "id": f"O{2000 + i}",
            "lead_id": f"L{1000 + random.randint(0, 99)}",
            "amount": round(random.uniform(1000, 50000), 2),
            "product": random.choice(self.products),
            "stage": random.choice(self.stages),
            "owner": f"Sales-{random.randint(1, 5)}",
            "created_date": (datetime.now() - timedelta(days=random.randint(0, 90))).strftime("%Y-%m-%d"),
            "close_date": (datetime.now() + timedelta(days=random.randint(0, 60))).strftime("%Y-%m-%d")
        } for i in range(count)]

    def generate_closed_deals(self, count=30):
        return [{
            "id": f"D{3000 + i}",
            "opportunity_id": f"O{2000 + random.randint(0, 49)}",
            "amount": round(random.uniform(1000, 50000), 2),
            "close_date": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d"),
            "status": random.choices(["Closed Won", "Closed Lost"], weights=[0.7, 0.3])[0]
        } for i in range(count)]

# ======================
# 2. Agent Definitions
# ======================
class DataCollectorAgent:
    def __init__(self):
        self.generator = SyntheticDataGenerator()
        self.data = None

    def collect_data(self):
        self.data = {
            "leads": self.generator.generate_leads(),
            "opportunities": self.generator.generate_opportunities(),
            "closed_deals": self.generator.generate_closed_deals()
        }
        return self.data

class DataQualityAgent:
    def check_completeness(self, data: Dict[str, List[Dict]]):
        issues = []
        for dataset_name, records in data.items():
            for record in records:
                if any(v is None for v in record.values()):
                    issues.append(f"Missing data in {dataset_name} record {record.get('id')}")
        return issues

class KPICalculationAgent:
    def calculate(self, data: Dict[str, List[Dict]]):
        df_leads = pd.DataFrame(data["leads"])
        df_opps = pd.DataFrame(data["opportunities"])
        df_deals = pd.DataFrame(data["closed_deals"])

        won_deals = df_deals[df_deals["status"] == "Closed Won"]
        lost_deals = df_deals[df_deals["status"] == "Closed Lost"]
        total_deals = len(won_deals) + len(lost_deals)
        open_opps = df_opps[~df_opps["stage"].isin(["Closed Won", "Closed Lost"])]
        qualified_leads = df_leads[df_leads["status"] == "Qualified"]

        return {
            "monthly_revenue": won_deals["amount"].sum(),
            "average_deal_size": won_deals["amount"].mean() if not won_deals.empty else 0,
            "win_rate": (len(won_deals) / total_deals * 100) if total_deals > 0 else 0,
            "sales_cycle_days": random.uniform(14, 45),
            "quota_attainment": random.uniform(70, 120),
            "pipeline_value": open_opps["amount"].sum(),
            "pipeline_velocity": (open_opps["amount"].sum() * 0.7) / 30,
            "forecast_accuracy": random.uniform(80, 95),
            "stage_conversion": {stage: random.uniform(0.2, 0.8) for stage in ["Prospecting", "Qualification", "Demo"]},
            "coverage_ratio": (open_opps["amount"].sum() / 100000) if open_opps.shape[0] else 0,
            "lead_conversion_rate": (len(qualified_leads) / len(df_leads) * 100) if len(df_leads) > 0 else 0,
            "cost_per_lead": random.uniform(50, 200),
            "mql_to_sql": random.uniform(20, 50),
            "website_conversion": random.uniform(1, 5),
            "cac": random.uniform(500, 2000)
        }

class ForecastingAgent:
    def forecast(self, kpis: Dict[str, Any]):
        return {
            "next_30d_revenue": kpis["monthly_revenue"] * random.uniform(0.9, 1.2),
            "next_30d_leads": int(kpis.get("lead_conversion_rate", 0) * 2)
        }

# ======================
# 3. Sales Dashboard
# ======================
class SalesDashboard:
    def __init__(self, collector):
        self.collector = collector

    def _styled_metric(self, title, value, delta=None):
        delta_html = ""
        if delta is not None:
            color = "#2ecc71" if (isinstance(delta, str) or delta >= 0) else "#e74c3c"
            delta_html = f'<div style="color: {color}; font-size: 14px;">{delta}</div>'

        st.markdown(f"""
        <style>
        .metric-card {{
            background: linear-gradient(135deg, #e0f7fa 0%, #ffffff 100%);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        .metric-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
        }}
        </style>
        <div class="metric-card">
            <div style="color: #555; font-size: 14px; font-weight: 600;">{title}</div>
            <div style="color: #2c3e50; font-size: 28px; font-weight: 700; margin: 10px 0;">{value}</div>
            {delta_html}
        </div>
        """, unsafe_allow_html=True)

    def _section_header(self, text):
        st.markdown(f"<h2 style='color: #228B22; margin-top: 30px;'>{text}</h2>", unsafe_allow_html=True)

    def display(self, kpis, forecasts, alerts):
        st.set_page_config(layout="wide", page_title="Sales KPI Dashboard")

        # Header
        col1, col2 = st.columns([1, 5])
        with col1:
            st.image("https://via.placeholder.com/100x30?text=SALES+DASH", width=100)
        with col2:
            st.markdown("<h1 style='color: #008080;'>Sales Performance Dashboard</h1>", unsafe_allow_html=True)

        # Alerts
        if alerts:
            st.error("\n".join(alerts))

        self._section_header("Sales Performance")
        cols = st.columns(5)
        with cols[0]:
            self._styled_metric("Monthly Revenue", f"${kpis['monthly_revenue']:,.0f}")
        with cols[1]:
            self._styled_metric("Avg Deal Size", f"${kpis['average_deal_size']:,.0f}")
        with cols[2]:
            self._styled_metric("Win Rate", f"{kpis['win_rate']:.1f}%")
        with cols[3]:
            self._styled_metric("Sales Cycle", f"{kpis['sales_cycle_days']:.1f} days")
        with cols[4]:
            self._styled_metric("Quota Attainment", f"{kpis['quota_attainment']:.1f}%")

        self._section_header("Pipeline Health")
        cols = st.columns(4)
        with cols[0]:
            self._styled_metric("Pipeline Value", f"${kpis['pipeline_value']:,.0f}")
        with cols[1]:
            self._styled_metric("Pipeline Velocity", f"${kpis['pipeline_velocity']:,.0f}/day")
        with cols[2]:
            self._styled_metric("Forecast Accuracy", f"{kpis['forecast_accuracy']:.1f}%")
        with cols[3]:
            self._styled_metric("Coverage Ratio", f"{kpis['coverage_ratio']:.2f}x")

        self._section_header("Stage Conversion")
        st.bar_chart(pd.DataFrame(kpis["stage_conversion"].items(), columns=["Stage", "Rate"]).set_index("Stage"))

        self._section_header("Lead Generation")
        cols = st.columns(4)
        with cols[0]:
            self._styled_metric("Lead Conversion", f"{kpis['lead_conversion_rate']:.1f}%")
        with cols[1]:
            self._styled_metric("Cost Per Lead", f"${kpis['cost_per_lead']:,.0f}")
        with cols[2]:
            self._styled_metric("MQL to SQL", f"{kpis['mql_to_sql']:.1f}%")
        with cols[3]:
            self._styled_metric("Website Conv.", f"{kpis['website_conversion']:.1f}%")

        self._section_header("Financial Metrics")
        cols = st.columns(3)
        with cols[0]:
            self._styled_metric("Customer Acquisition Cost", f"${kpis['cac']:,.0f}")
        with cols[1]:
            self._styled_metric("LTV Estimate", f"${kpis['average_deal_size']*3:,.0f}")
        with cols[2]:
            ltv_cac = (kpis['average_deal_size']*3)/kpis['cac']
            self._styled_metric("LTV:CAC Ratio", f"{ltv_cac:.1f}x")

        with st.expander("Show Raw Data"):
            st.dataframe(pd.DataFrame(self.collector.data['leads']))
            st.dataframe(pd.DataFrame(self.collector.data['opportunities']))
            st.dataframe(pd.DataFrame(self.collector.data['closed_deals']))

# ======================
# 4. Orchestrator
# ======================
class Orchestrator:
    def __init__(self):
        self.collector = DataCollectorAgent()
        self.quality = DataQualityAgent()
        self.kpi = KPICalculationAgent()
        self.forecaster = ForecastingAgent()
        self.dashboard = SalesDashboard(self.collector)

    def run(self):
        data = self.collector.collect_data()
        quality_issues = self.quality.check_completeness(data)
        kpis = self.kpi.calculate(data)
        forecasts = self.forecaster.forecast(kpis)
        alerts = []  # No alert agent

        if quality_issues:
            st.warning(" ".join(quality_issues))

        self.dashboard.display(kpis, forecasts, alerts)

# ======================
# 5. Execution
# ======================
if __name__ == "__main__":
    orchestrator = Orchestrator()
    orchestrator.run()
