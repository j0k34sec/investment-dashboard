import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import numpy as np
from dateutil.relativedelta import relativedelta
 
# ======================================================
# 🎨 Page Configuration & Custom CSS
# ======================================================
st.set_page_config(
    page_title="💼 Investment Management Dashboard", 
    layout="wide",
    page_icon="💼"
)
 
# Enhanced CSS with better visual hierarchy and responsive design
st.markdown("""
<style>
:root {
    --primary-color: #003366;
    --secondary-color: #28a745;
    --background-color: #f8f9fa;
    --text-color: #212529;
    --border-radius: 8px;
}
 
body {
    background-color: var(--background-color);
    color: var(--text-color);
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
}
 
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 1.5rem;
}
 
.sidebar .sidebar-content {
    background-color: var(--primary-color);
    color: white;
}
 
.stButton>button, .stDownloadButton>button {
    background-color: var(--secondary-color);
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: var(--border-radius);
    margin-top: 5px;
    cursor: pointer;
    transition: all 0.3s ease;
}
 
.stButton>button:hover, .stDownloadButton>button:hover {
    opacity: 0.9;
    transform: translateY(-1px);
}
 
.stSelectbox>div>div {
    padding: 0.5rem;
}
 
.stAlert {
    padding: 0.75rem;
    border-radius: var(--border-radius);
    margin-bottom: 1rem;
}
 
.stSuccess {
    background-color: #d4edda;
    color: #155724;
}
 
.stWarning {
    background-color: #fff3cd;
    color: #856404;
}
 
.stError {
    background-color: #f8d7da;
    color: #721c24;
}
 
.stInfo {
    background-color: #d1ecf1;
    color: #0c5460;
}
 
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    color: var(--primary-color);
    margin-bottom: 0.75rem;
}
 
.stDataFrame {
    border-radius: var(--border-radius);
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
 
.stTextInput>div>div>input, .stNumberInput>div>div>input, 
.stTextArea>div>div>textarea, .stDateInput>div>div>input {
    border-radius: var(--border-radius);
    padding: 0.5rem;
}
 
.metric-card {
    background-color: white;
    border-radius: var(--border-radius);
    padding: 1rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    margin-bottom: 1rem;
}
 
.metric-value {
    font-size: 1.5rem;
    font-weight: bold;
    color: var(--primary-color);
}
 
.metric-label {
    font-size: 0.9rem;
    color: #6c757d;
}
 
@media (max-width: 768px) {
    .block-container {
        padding: 1rem;
    }
    
    .stButton>button, .stDownloadButton>button {
        width: 100%;
    }
}
</style>
""", unsafe_allow_html=True)
 
# ======================================================
# 📂 Data Initialization with Error Handling
# ======================================================
data_dir = "investment_data"
os.makedirs(data_dir, exist_ok=True)
 
investor_file = os.path.join(data_dir, "investors.csv")
payment_file = os.path.join(data_dir, "payments.csv")
backup_dir = os.path.join(data_dir, "backups")
os.makedirs(backup_dir, exist_ok=True)
 
def load_data():
    """Load data with proper error handling and data validation"""
    global investors_df, payments_df
    
    # Load investors data
    try:
        if os.path.exists(investor_file):
            investors_df = pd.read_csv(investor_file)
            if not investors_df.empty:
                # Convert dates with error handling
                investors_df['DOB'] = pd.to_datetime(investors_df['DOB'], errors='coerce').dt.date
                investors_df['InvestmentDate'] = pd.to_datetime(investors_df['InvestmentDate'], errors='coerce').dt.date
                # Ensure required columns exist
                required_cols = ['InvestorID', 'Name', 'InvestedAmount', 'InterestRate', 'GoldPlan']
                for col in required_cols:
                    if col not in investors_df.columns:
                        st.error(f"Missing required column in investors data: {col}")
                        return False
        else:
            investors_df = pd.DataFrame(columns=[
                'InvestorID', 'Name', 'DOB', 'FatherName', 'Address', 'MobileNumber', 'EmailID',
                'PANNumber', 'AadharNumber', 'InvestedAmount', 'InterestRate', 'GoldPlan', 
                'ChequeNumber', 'InvestmentDate'
            ])
        
        # Load payments data
        if os.path.exists(payment_file):
            payments_df = pd.read_csv(payment_file)
            if not payments_df.empty:
                payments_df['PaidDate'] = pd.to_datetime(payments_df['PaidDate'], errors='coerce')
                # Ensure required columns exist
                required_cols = ['InvestorID', 'Month', 'Year', 'PaymentType', 'Paid']
                for col in required_cols:
                    if col not in payments_df.columns:
                        st.error(f"Missing required column in payments data: {col}")
                        return False
        else:
            payments_df = pd.DataFrame(columns=[
                'InvestorID', 'Month', 'Year', 'PaymentType', 'Paid', 'PaidDate'
            ])
        
        return True
    
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return False
 
def create_backup():
    """Create timestamped backup of data files"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_investor = os.path.join(backup_dir, f"investors_backup_{timestamp}.csv")
        backup_payment = os.path.join(backup_dir, f"payments_backup_{timestamp}.csv")
        
        investors_df.to_csv(backup_investor, index=False)
        payments_df.to_csv(backup_payment, index=False)
        return True
    except Exception as e:
        st.error(f"Backup failed: {str(e)}")
        return False
 
def save_data():
    """Save data with backup and error handling"""
    if create_backup():
        try:
            investors_df.to_csv(investor_file, index=False)
            payments_df.to_csv(payment_file, index=False)
            return True
        except Exception as e:
            st.error(f"Error saving data: {str(e)}")
            return False
    return False
 
# Initialize data
if not load_data():
    st.error("Critical error loading data. The application may not function properly.")
 
# ======================================================
# 🔧 Enhanced Utility Functions
# ======================================================
def validate_investor_data(data):
    """Validate investor data before saving"""
    errors = []
    
    if not data.get('Name') or len(data['Name'].strip()) < 3:
        errors.append("Name must be at least 3 characters")
    
    if data.get('InvestedAmount', 0) <= 0:
        errors.append("Invested amount must be positive")
    
    if data.get('MobileNumber') and not str(data['MobileNumber']).isdigit():
        errors.append("Mobile number must contain only digits")
    
    if data.get('PANNumber') and len(str(data['PANNumber'])) != 10:
        errors.append("PAN number must be 10 characters")
    
    if data.get('AadharNumber') and (not str(data['AadharNumber']).isdigit() or len(str(data['AadharNumber'])) != 12):
        errors.append("Aadhar number must be 12 digits")
    
    return errors
 
def calculate_gold_plan(amount):
    """Calculate gold plan details with validation"""
    if amount <= 0:
        return 0, 0
    grams_per_month = amount / 100000
    total_grams = grams_per_month * 25
    return round(grams_per_month, 4), round(total_grams, 4)
 
def calculate_outstanding():
    """Calculate outstanding payments with improved accuracy"""
    cash_summary = []
    gold_summary = []
 
    for _, investor in investors_df.iterrows():
        investor_id = investor['InvestorID']
        investment_date = pd.to_datetime(investor['InvestmentDate'])
        
        if investor['GoldPlan']:
            # Gold plan calculations
            grams_per_month, total_grams = calculate_gold_plan(investor['InvestedAmount'])
            
            # Calculate delivered and pending gold
            today = datetime.today().date()
            if today < investment_date.date():
                months_elapsed = 0
            else:
                months_elapsed = (today.year - investment_date.year) * 12 + (today.month - investment_date.month)
                months_elapsed = min(months_elapsed, 25)  # Cap at 25 months
                
            delivered_gold = grams_per_month * months_elapsed
            pending_gold = total_grams - delivered_gold
            
            gold_summary.append({
                'InvestorID': investor_id,
                'Name': investor['Name'],
                'Monthly Gold (gm)': grams_per_month,
                'Total Gold (gm)': total_grams,
                'Delivered Gold (gm)': delivered_gold,
                'Pending Gold (gm)': pending_gold,
                'Last Delivery Month': (investment_date + relativedelta(months=+months_elapsed)).strftime('%b %Y') if months_elapsed > 0 else 'Not started'
            })
        else:
            # Cash plan calculations
            today = datetime.today().date()
            if today < investment_date.date():
                months_due = 0
            else:
                months_due = (today.year - investment_date.year) * 12 + (today.month - investment_date.month)
            
            total_due = months_due * investor['InvestedAmount'] * (investor['InterestRate'] / 100)
            
            # Get all payments for this investor
            paid_records = payments_df[
                (payments_df['InvestorID'] == investor_id) & 
                (payments_df['Paid'] == True)
            ]
            
            total_paid = sum([
                investor['InvestedAmount'] * (investor['InterestRate'] / 100)
                for _, _ in paid_records.iterrows()
            ])
            
            outstanding = total_due - total_paid
            
            cash_summary.append({
                'InvestorID': investor_id,
                'Name': investor['Name'],
                'Monthly Payment (₹)': investor['InvestedAmount'] * (investor['InterestRate'] / 100),
                'Total Due (₹)': total_due,
                'Total Paid (₹)': total_paid,
                'Outstanding (₹)': outstanding,
                'Months Due': months_due,
                'Months Paid': len(paid_records)
            })
 
    return pd.DataFrame(cash_summary), pd.DataFrame(gold_summary)
 
def monthly_pending_summary(year=None):
    """Generate monthly pending summary with optional year filter"""
    today = datetime.today()
    year = year if year else today.year
    
    # Generate all months for the year
    month_year_list = pd.date_range(start=f"{year}-01-01", end=f"{year}-12-31", freq='MS')
    records = []
 
    for date in month_year_list:
        month_name = date.strftime('%B')
        current_year = date.year
 
        for _, investor in investors_df.iterrows():
            investor_id = investor['InvestorID']
            investment_date = pd.to_datetime(investor['InvestmentDate'])
            
            if investor['GoldPlan']:
                # Gold plan pending calculation
                first_gold_date = investment_date + relativedelta(months=1)
                
                if date >= first_gold_date and date <= first_gold_date + relativedelta(months=24):
                    # Check if this month's gold has been delivered
                    payment_exists = not payments_df[
                        (payments_df['InvestorID'] == investor_id) &
                        (payments_df['Month'] == month_name) &
                        (payments_df['Year'] == current_year) &
                        (payments_df['Paid'] == True)
                    ].empty
                    
                    if not payment_exists:
                        grams_per_month, _ = calculate_gold_plan(investor['InvestedAmount'])
                        records.append({
                            'Month': month_name,
                            'Year': current_year,
                            'InvestorID': investor_id,
                            'Name': investor['Name'],
                            'Plan': 'Gold',
                            'Pending Amount': f"{grams_per_month:.4f} gm Gold",
                            'Status': 'Pending'
                        })
            else:
                # Cash plan pending calculation
                if date >= investment_date and date <= pd.Timestamp(today):
                    # Check if this month's payment has been made
                    payment_exists = not payments_df[
                        (payments_df['InvestorID'] == investor_id) &
                        (payments_df['Month'] == month_name) &
                        (payments_df['Year'] == current_year) &
                        (payments_df['Paid'] == True)
                    ].empty
                    
                    if not payment_exists:
                        amount_due = investor['InvestedAmount'] * (investor['InterestRate'] / 100)
                        records.append({
                            'Month': month_name,
                            'Year': current_year,
                            'InvestorID': investor_id,
                            'Name': investor['Name'],
                            'Plan': 'Cash',
                            'Pending Amount': f"₹ {amount_due:,.2f}",
                            'Status': 'Pending'
                        })
 
    return pd.DataFrame(records)
 
# ======================================================
# 📊 Enhanced Dashboard Summary
# ======================================================
def dashboard_summary():
    st.header("📊 Dashboard Overview")
    
    # Calculate metrics
    total_invested = investors_df['InvestedAmount'].sum()
    total_investors = investors_df.shape[0]
    cash_investors = investors_df[~investors_df['GoldPlan']].shape[0]
    gold_investors = investors_df[investors_df['GoldPlan']].shape[0]
    
    # Display metrics in cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class='metric-card'>
            <div class='metric-label'>Total Investors</div>
            <div class='metric-value'>{}</div>
        </div>
        """.format(total_investors), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='metric-card'>
            <div class='metric-label'>Total Invested</div>
            <div class='metric-value'>₹ {:,.2f}</div>
        </div>
        """.format(total_invested), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='metric-card'>
            <div class='metric-label'>Cash Investors</div>
            <div class='metric-value'>{}</div>
        </div>
        """.format(cash_investors), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class='metric-card'>
            <div class='metric-label'>Gold Investors</div>
            <div class='metric-value'>{}</div>
        </div>
        """.format(gold_investors), unsafe_allow_html=True)
    
    # Cash Plan Summary
    st.subheader("💰 Cash Plan Summary")
    cash_df, gold_df = calculate_outstanding()
    
    if not cash_df.empty:
        # Add summary row
        summary_row = pd.DataFrame({
            'InvestorID': ['TOTAL'],
            'Name': [''],
            'Monthly Payment (₹)': [cash_df['Monthly Payment (₹)'].sum()],
            'Total Due (₹)': [cash_df['Total Due (₹)'].sum()],
            'Total Paid (₹)': [cash_df['Total Paid (₹)'].sum()],
            'Outstanding (₹)': [cash_df['Outstanding (₹)'].sum()],
            'Months Due': [cash_df['Months Due'].sum()],
            'Months Paid': [cash_df['Months Paid'].sum()]
        })
        
        display_df = pd.concat([cash_df, summary_row], ignore_index=True)
        st.dataframe(
            display_df.style.format({
                'Monthly Payment (₹)': '{:,.2f}',
                'Total Due (₹)': '{:,.2f}',
                'Total Paid (₹)': '{:,.2f}',
                'Outstanding (₹)': '{:,.2f}'
            }),
            use_container_width=True
        )
        
        # Add download button
        csv = cash_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download Cash Outstanding Summary",
            data=csv,
            file_name='Cash_Outstanding_Summary.csv',
            mime='text/csv'
        )
    else:
        st.success("No outstanding cash payments!")
    
    # Gold Plan Summary
    st.subheader("🏅 Gold Plan Summary")
    if not gold_df.empty:
        # Add summary row
        summary_row = pd.DataFrame({
            'InvestorID': ['TOTAL'],
            'Name': [''],
            'Monthly Gold (gm)': [gold_df['Monthly Gold (gm)'].sum()],
            'Total Gold (gm)': [gold_df['Total Gold (gm)'].sum()],
            'Delivered Gold (gm)': [gold_df['Delivered Gold (gm)'].sum()],
            'Pending Gold (gm)': [gold_df['Pending Gold (gm)'].sum()],
            'Last Delivery Month': ['']
        })
        
        display_df = pd.concat([gold_df, summary_row], ignore_index=True)
        st.dataframe(
            display_df.style.format({
                'Monthly Gold (gm)': '{:.4f}',
                'Total Gold (gm)': '{:.4f}',
                'Delivered Gold (gm)': '{:.4f}',
                'Pending Gold (gm)': '{:.4f}'
            }),
            use_container_width=True
        )
        
        # Add download button
        csv = gold_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download Gold Plan Summary",
            data=csv,
            file_name='Gold_Plan_Summary.csv',
            mime='text/csv'
        )
    else:
        st.success("No gold plan investors!")
    
    # Monthly Pending Summary
    st.subheader("📅 Monthly Pending Summary")
    year = st.selectbox(
        "Select Year for Pending Summary",
        options=range(2020, datetime.today().year + 1),
        index=datetime.today().year - 2020
    )
    
    monthly_df = monthly_pending_summary(year)
    if not monthly_df.empty:
        st.dataframe(monthly_df, use_container_width=True)
        
        # Add download button
        csv = monthly_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download Monthly Pending Summary",
            data=csv,
            file_name=f'Monthly_Pending_Summary_{year}.csv',
            mime='text/csv'
        )
    else:
        st.success(f"No pending payments for {year}!")
 
# ======================================================
# 📝 Enhanced Register Investor with Validation
# ======================================================
def register_investor():
    global investors_df
 
    st.header("📝 Register New Investor")
    
    with st.form("register_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name*", help="Required field")
            dob = st.date_input(
                "Date of Birth*", 
                value=datetime.today().date() - timedelta(days=365*25),
                max_value=datetime.today().date(),
                help="Required field"
            )
            father_name = st.text_input("Father's Name")
            mobile = st.text_input(
                "Mobile Number*", 
                max_chars=10,
                help="10 digit mobile number (required)"
            )
            email = st.text_input("Email ID")
            pan = st.text_input(
                "PAN Number", 
                max_chars=10,
                help="10 character PAN number"
            )
        
        with col2:
            aadhar = st.text_input(
                "Aadhar Number", 
                max_chars=12,
                help="12 digit Aadhar number"
            )
            address = st.text_area("Address")
            invested_amount = st.number_input(
                "Invested Amount (₹)*", 
                min_value=1000.0, 
                step=1000.0,
                value=100000.0,
                help="Minimum ₹1000 (required)"
            )
            interest_rate = st.selectbox(
                "Interest Rate (%)*", 
                options=[1, 2, 3, 4, 5],
                index=2,
                help="Required field"
            )
            gold_plan = st.checkbox(
                "Gold Plan (1 gm per ₹100,000/month for 25 months)",
                help="1 gram per ₹100,000 invested each month for 25 months"
            )
            cheque_number = st.text_input("Cheque Number (if any)")
            investment_date = st.date_input(
                "Investment Date*", 
                value=datetime.today().date(),
                max_value=datetime.today().date(),
                help="Required field"
            )
        
        # Show gold plan details if selected
        if gold_plan and invested_amount > 0:
            grams_per_month, total_grams = calculate_gold_plan(invested_amount)
            st.info(f"""
            **Gold Plan Details:**
            - Monthly Gold: {grams_per_month:.4f} grams
            - Total Gold over 25 months: {total_grams:.4f} grams
            - Value at ₹5,000/gm: ₹{total_grams*5000:,.2f}
            """)
        
        submitted = st.form_submit_button("Register Investor")
        
        if submitted:
            # Validate inputs
            validation_errors = validate_investor_data({
                'Name': name,
                'InvestedAmount': invested_amount,
                'MobileNumber': mobile,
                'PANNumber': pan,
                'AadharNumber': aadhar
            })
            
            if validation_errors:
                for error in validation_errors:
                    st.error(error)
            else:
                # Generate investor ID
                investor_id = f"INV{len(investors_df)+1:05d}"
                
                # Create new record
                new_data = {
                    'InvestorID': investor_id,
                    'Name': name.strip(),
                    'DOB': dob,
                    'FatherName': father_name.strip() if father_name else '',
                    'Address': address.strip() if address else '',
                    'MobileNumber': mobile.strip() if mobile else '',
                    'EmailID': email.strip() if email else '',
                    'PANNumber': pan.strip().upper() if pan else '',
                    'AadharNumber': aadhar.strip() if aadhar else '',
                    'InvestedAmount': invested_amount,
                    'InterestRate': interest_rate,
                    'GoldPlan': gold_plan,
                    'ChequeNumber': cheque_number.strip() if cheque_number else '',
                    'InvestmentDate': investment_date
                }
                
                # Add to DataFrame
                investors_df = pd.concat([investors_df, pd.DataFrame([new_data])], ignore_index=True)
                
                # Save data
                if save_data():
                    st.success(f"""
                    Investor **{name}** registered successfully!
                    - Investor ID: **{investor_id}**
                    - Investment Amount: **₹{invested_amount:,.2f}**
                    - Plan: **{'Gold' if gold_plan else 'Cash'}**
                    """)
                    
                    # Generate initial payment records for cash plans
                    if not gold_plan:
                        today = datetime.today()
                        investment_date_dt = datetime.combine(investment_date, datetime.min.time())
                        
                        if investment_date_dt <= today:
                            months_due = (today.year - investment_date.year) * 12 + (today.month - investment_date.month)
                            
                            for i in range(months_due + 1):
                                payment_date = investment_date_dt + relativedelta(months=+i)
                                month_name = payment_date.strftime('%B')
                                year = payment_date.year
                                
                                # Check if payment record already exists
                                existing = payments_df[
                                    (payments_df['InvestorID'] == investor_id) &
                                    (payments_df['Month'] == month_name) &
                                    (payments_df['Year'] == year)
                                ]
                                
                                if existing.empty:
                                    new_payment = {
                                        'InvestorID': investor_id,
                                        'Month': month_name,
                                        'Year': year,
                                        'PaymentType': 'Interest',
                                        'Paid': False,
                                        'PaidDate': pd.NaT
                                    }
                                    payments_df = pd.concat([payments_df, pd.DataFrame([new_payment])], ignore_index=True)
                            
                            save_data()
                else:
                    st.error("Failed to save investor data. Please try again.")
 
# ======================================================
# 👥 Enhanced View Investors with Search and Filters
# ======================================================
def view_investors():
    st.header("👥 Investor Directory")
    
    if investors_df.empty:
        st.info("No investors found.")
        return
    
    # Search and filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_query = st.text_input("Search by Name or ID")
    
    with col2:
        plan_filter = st.selectbox(
            "Filter by Plan",
            options=["All", "Cash", "Gold"],
            index=0
        )
    
    with col3:
        sort_by = st.selectbox(
            "Sort By",
            options=["Name (A-Z)", "Name (Z-A)", "Investment Date (Newest)", "Investment Date (Oldest)", "Amount (High-Low)", "Amount (Low-High)"],
            index=0
        )
    
    # Apply filters
    filtered_df = investors_df.copy()
    
    if search_query:
        mask = (
            filtered_df['Name'].str.contains(search_query, case=False) |
            filtered_df['InvestorID'].str.contains(search_query, case=False)
        )
        filtered_df = filtered_df[mask]
    
    if plan_filter != "All":
        gold_filter = plan_filter == "Gold"
        filtered_df = filtered_df[filtered_df['GoldPlan'] == gold_filter]
    
    # Apply sorting
    if sort_by == "Name (A-Z)":
        filtered_df = filtered_df.sort_values('Name', ascending=True)
    elif sort_by == "Name (Z-A)":
        filtered_df = filtered_df.sort_values('Name', ascending=False)
    elif sort_by == "Investment Date (Newest)":
        filtered_df = filtered_df.sort_values('InvestmentDate', ascending=False)
    elif sort_by == "Investment Date (Oldest)":
        filtered_df = filtered_df.sort_values('InvestmentDate', ascending=True)
    elif sort_by == "Amount (High-Low)":
        filtered_df = filtered_df.sort_values('InvestedAmount', ascending=False)
    elif sort_by == "Amount (Low-High)":
        filtered_df = filtered_df.sort_values('InvestedAmount', ascending=True)
    
    # Display results
    st.write(f"Showing {len(filtered_df)} of {len(investors_df)} investors")
    
    # Pagination
    page_size = 10
    total_pages = (len(filtered_df) // page_size + (1 if len(filtered_df) % page_size > 0 else 0))

    if total_pages > 1:
        page = st.number_input("Page", min_value=1, max_value=total_pages, value=1)
        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, len(filtered_df))
        display_df = filtered_df.iloc[start_idx:end_idx]
    else:
        display_df = filtered_df
    
    st.dataframe(
        display_df.style.format({
            'InvestedAmount': '₹{:,}',
            'DOB': lambda x: x.strftime('%d-%b-%Y') if not pd.isna(x) else '',
            'InvestmentDate': lambda x: x.strftime('%d-%b-%Y') if not pd.isna(x) else ''
        }),
        use_container_width=True,
        height=min(400, (len(display_df) + 1) * 35 + 3)
    )
    
    # Download button
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Download Investor List",
        data=csv,
        file_name='Investor_List.csv',
        mime='text/csv'
    )
 
# ======================================================
# 🗑️ Enhanced Delete Investor with Confirmation
# ======================================================
def delete_investor():
    global investors_df, payments_df
 
    st.header("🗑️ Delete Investor")
    
    if investors_df.empty:
        st.info("No investors to delete.")
        return
    
    # Select investor
    selected_investor = st.selectbox(
        "Select Investor to Delete",
        options=investors_df['InvestorID'],
        format_func=lambda x: f"{x} - {investors_df[investors_df['InvestorID'] == x].iloc[0]['Name']}"
    )
    
    investor = investors_df[investors_df['InvestorID'] == selected_investor].iloc[0]
    
    # Show confirmation
    st.warning(f"""
    ### Are you sure you want to delete this investor?
    - **Name:** {investor['Name']}
    - **Investor ID:** {investor['InvestorID']}
    - **Invested Amount:** ₹{investor['InvestedAmount']:,.2f}
    - **Plan:** {'Gold' if investor['GoldPlan'] else 'Cash'}
    """)
    
    # Additional confirmation
    confirm = st.checkbox("I understand this action cannot be undone")
    
    if st.button("Delete Investor", disabled=not confirm):
        # Create backup before deletion
        if create_backup():
            # Remove investor and related payments
            investors_df = investors_df[investors_df['InvestorID'] != selected_investor]
            payments_df = payments_df[payments_df['InvestorID'] != selected_investor]
            
            # Save data
            if save_data():
                st.success(f"Investor {investor['Name']} ({investor['InvestorID']}) deleted successfully!")
                st.experimental_rerun()
            else:
                st.error("Failed to save changes after deletion.")
        else:
            st.error("Deletion aborted because backup failed.")
 
# ======================================================
# 💸 Enhanced Payment Management System
# ======================================================
def payment_management():
    st.header("💸 Payment Management")
    
    tab1, tab2, tab3 = st.tabs(["Pending Payments", "Record Payment", "Payment History"])
    
    with tab1:
        st.subheader("⏳ Pending Payments")
        
        # Filter unpaid and cash plans only
        pending_df = payments_df[(payments_df['Paid'] == False)]
        pending_df = pending_df.merge(
            investors_df[['InvestorID', 'Name', 'GoldPlan', 'InvestedAmount', 'InterestRate']], 
            on='InvestorID', 
            how='left'
        )
        pending_df = pending_df[pending_df['GoldPlan'] == False]
        
        if pending_df.empty:
            st.success("No pending cash payments!")
            return
        
        # Group by year and month
        grouped = pending_df.groupby(['Year', 'Month']).size().reset_index(name='Count')
        grouped = grouped.sort_values(['Year', 'Month'], ascending=[False, True])
        
        # Select year and month
        col1, col2 = st.columns(2)
        
        with col1:
            selected_year = st.selectbox(
                "Select Year",
                options=sorted(pending_df['Year'].unique(), reverse=True)
        )
        
        with col2:
            months_in_year = pending_df[pending_df['Year'] == selected_year]['Month'].unique()
            selected_month = st.selectbox(
                "Select Month",
                options=sorted(months_in_year, key=lambda x: datetime.strptime(x, "%B").month)
            )
        
        # Filter payments
        filtered = pending_df[
            (pending_df['Year'] == selected_year) & 
            (pending_df['Month'] == selected_month)
        ]
        
        if filtered.empty:
            st.info(f"No pending payments for {selected_month} {selected_year}")
            return
        
        st.write(f"Showing {len(filtered)} pending payments for **{selected_month} {selected_year}**")
        
        # Display payments with action buttons
        for _, row in filtered.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([4, 3, 2])
                
                with col1:
                    st.markdown(f"""
                    **{row['Name']}**  
                    Investor ID: {row['InvestorID']}  
                    Amount: ₹{row['InvestedAmount'] * (row['InterestRate'] / 100):,.2f}
                    """)
                
                with col2:
                    st.markdown(f"""
                    Due for: **{row['Month']} {row['Year']}**  
                    Payment Type: {row['PaymentType']}
                    """)
                
                with col3:
                    if st.button("Mark as Paid", key=f"pay_{row.name}"):
                        payments_df.loc[row.name, 'Paid'] = True
                        payments_df.loc[row.name, 'PaidDate'] = pd.Timestamp.now()
                        
                        if save_data():
                            st.success(f"Payment marked as paid for {row['Name']}")
                            st.experimental_rerun()
                        else:
                            st.error("Failed to save payment status.")
        
        # Download button
        csv = filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download Pending Payments",
            data=csv,
            file_name=f'Pending_Payments_{selected_month}_{selected_year}.csv',
            mime='text/csv'
        )
    
    with tab2:
        st.subheader("➕ Record New Payment")
        
        # Select investor
        cash_investors = investors_df[~investors_df['GoldPlan']]
        
        if cash_investors.empty:
            st.info("No cash investors available for payment recording.")
            return
        
        selected_investor = st.selectbox(
            "Select Investor",
            options=cash_investors['InvestorID'],
            format_func=lambda x: f"{x} - {cash_investors[cash_investors['InvestorID'] == x].iloc[0]['Name']}"
        )
        
        investor = cash_investors[cash_investors['InvestorID'] == selected_investor].iloc[0]
        
        # Payment details
        col1, col2 = st.columns(2)
        
        with col1:
            payment_month = st.selectbox(
                "Month",
                options=[
                    'January', 'February', 'March', 'April', 'May', 'June',
                    'July', 'August', 'September', 'October', 'November', 'December'
                ]
            )
        
        with col2:
            payment_year = st.number_input(
                "Year",
                min_value=2020,
                max_value=datetime.today().year,
                value=datetime.today().year
            )
        
        payment_amount = investor['InvestedAmount'] * (investor['InterestRate'] / 100)
        payment_date = st.date_input(
            "Payment Date",
            value=datetime.today().date()
        )
        
        payment_reference = st.text_input("Payment Reference (Cheque No./UTR/etc.)")
        
        # Check if payment already exists
        existing_payment = payments_df[
            (payments_df['InvestorID'] == selected_investor) &
            (payments_df['Month'] == payment_month) &
            (payments_df['Year'] == payment_year)
        ]
        
        if not existing_payment.empty:
            st.warning(f"""
            A payment record already exists for **{payment_month} {payment_year}** for this investor.
            
            If you meant to update it, use **Payment History** (or delete the record and re-add it).
            """)