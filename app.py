from cProfile import label
import markdown
from flask import session, redirect, request
from flask import Flask, render_template, request
from flask import send_file
import io
import pandas as pd


from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
from ai_insights import generate_ai_insights

import mysql.connector

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root123",
    database="businessdb"
)

query = "SELECT * FROM train"

df = pd.read_sql(query, connection)
print(df.columns)



app = Flask(__name__)
app.secret_key = "secretkey"

# Read dataset

def generate_chart():

    plt.style.use('ggplot')

    region_sales = df.groupby("Region")["Sales"].sum()

    plt.figure(figsize=(14,7))

    region_sales.plot(
    kind="bar",
    color=["#1f77b4", "#2ca02c", "#ff7f0e", "#d62728"]
)

    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)

    plt.title(
    "Region Wise Sales",
    fontsize=18,
    fontweight='bold'
)

    plt.xlabel("Region", fontsize=12)
    plt.ylabel("Sales", fontsize=12)

    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    plt.savefig("static/charts/sales_chart.png", bbox_inches="tight")

    plt.close()

# PIE CHART

category_sales = df.groupby("Category")["Sales"].sum()

plt.figure(figsize=(8,8))

category_sales.plot(
    kind="pie",
    autopct='%1.1f%%',
    startangle=90,
    textprops={'fontsize':14},
    pctdistance=0.7
)

plt.ylabel("")

plt.title(
    "Category Wise Sales",
    fontsize=12,
    fontweight='bold'
)

plt.axis('equal')

plt.tight_layout()

plt.savefig("static/charts/pie_chart.png", bbox_inches="tight")

plt.close()

# LINE CHART

top_products = df.groupby("Sub-Category")["Sales"].sum().sort_values(ascending=False).head(10)

plt.figure(figsize=(14,7))

top_products.plot(
    kind="line",
    marker="o",
    color="#1f4e79",
    linewidth=3
)

plt.title(
    "Top Sub-Category Sales Trend",
    fontsize=16,
    fontweight='bold'
)
plt.xlabel(
    "Sub-Category",
    fontsize=12,
    fontweight='bold'
)

plt.ylabel(
    "Sales",
    fontsize=12,
    fontweight='bold'
)


plt.grid(
    linestyle="--",
    alpha=0.6
)

plt.xticks(
    rotation=30,
    ha='right',
    fontsize=11
)

plt.yticks(fontsize=11)

plt.tight_layout()

plt.savefig("static/charts/line_chart.png", bbox_inches="tight")

plt.close()

generate_chart()

@app.route("/login-page")
def login_page():
    return render_template("login.html")

@app.route("/signup-page")
def signup_page():
    return render_template("signup.html")

@app.route("/signup", methods=["POST"])
def signup():

    username = request.form["username"]
    password = request.form["password"]

    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username=%s",
        (username,)
    )

    user = cursor.fetchone()

    if user:
        cursor.close()
        return "Username already exists. Please login."

    cursor.execute(
        "INSERT INTO users(username,password) VALUES(%s,%s)",
        (username,password)
    )

    connection.commit()

    cursor.close()

    return redirect("/login-page")

@app.route("/login", methods=["POST"])
def login():

    username = request.form["username"]
    password = request.form["password"]

    cursor = connection.cursor()

    sql = """
    SELECT * FROM users
    WHERE username=%s AND password=%s
    """

    cursor.execute(sql, (username, password))

    user = cursor.fetchone()

    cursor.close()

    if user:
        session["user"] = username
        return redirect("/")
    else:
        return "Invalid Username or Password"
    

    
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login-page")

# -------------------------
# HOME PAGE
# -------------------------
@app.route("/")
def home():

    if "user" not in session:
        return redirect("/login-page")

    total_sales = round(df["Sales"].sum(),2)

    total_customers = df["Customer ID"].nunique()

    total_products = df["Product Name"].nunique()

    total_orders = df["Order ID"].nunique()
    total_profit = round(df["Sales"].sum() * 0.18, 2)

    total_quantity = len(df)

    avg_order_value = round(
        df["Sales"].sum() / total_orders,
        2
    )

    sales_growth = 12.5

    return render_template(
        "index.html",
        total_sales=total_sales,
        total_customers=total_customers,
        total_products=total_products,
        total_orders=total_orders,
        total_profit=total_profit,
        total_quantity=total_quantity,
        avg_order_value=avg_order_value,
        sales_growth=sales_growth
    )
# -------------------------
# TOTAL SALES API
# -------------------------
@app.route("/sales")
def sales():

    total_sales = df["Sales"].sum()

    region_sales = df.groupby("Region")["Sales"].sum()

    html = f"""

    <html>

    <head>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    </head>

    <body style="
    font-family:Arial;
    background:#f4f6f9;
    padding:40px;
    ">

    <div style="
    background:white;
    padding:30px;
    border-radius:15px;
    box-shadow:0px 4px 10px rgba(0,0,0,0.2);
    ">
    <a href="/"
style="
background:#1f4e79;
color:white;
padding:10px 18px;
text-decoration:none;
border-radius:8px;
display:inline-block;
margin-bottom:20px;
">
⬅ Back to Dashboard
</a>

    <h1 style="color:#1f4e79;">
    💰 Sales Performance Dashboard
    </h1>

    <h2>
    Total Sales: ${total_sales:,.2f}
    </h2>

    <canvas id="salesChart" height="100"></canvas>

    </div>

    <script>

    const ctx = document.getElementById('salesChart').getContext('2d');
    console.log(document.getElementById('salesChart'));
    new Chart(ctx, {{
    type: 'bar',
    data: {{
        labels: {list(region_sales.index)},
        datasets: [{{
            label: 'Region Sales',
            data: {[float(x) for x in region_sales.values]},
            backgroundColor: [
                '#1f77b4',
                '#2ca02c',
                '#ff7f0e',
                '#d62728'
            ],
            borderRadius: 8,
            borderWidth: 1
        }}]
    }},
    options: {{

    responsive: true,

    plugins: {{

        title: {{
            display: true,
            text: 'Region Wise Sales Performance'
        }},

        legend: {{
            display: true
        }}
    }},

    scales: {{
        y: {{
            beginAtZero: true
        }}
    }}
}}
}});

    </script>

    </body>

    </html>
    """

    return html

# -------------------------
# REGION SALES API
# -------------------------
@app.route("/region-sales")
def region_sales():

    region_data = df.groupby("Region")["Sales"].sum()

    html = """

    <html>

    <body style="
    font-family:Arial;
    background:#f4f6f9;
    padding:40px;
    ">

    <div style="
    background:white;
    padding:30px;
    border-radius:15px;
    box-shadow:0px 4px 10px rgba(0,0,0,0.1);
    ">
    <a href="/"
style="
background:#1f4e79;
color:white;
padding:10px 18px;
text-decoration:none;
border-radius:8px;
display:inline-block;
margin-bottom:20px;
">
⬅ Back to Dashboard
</a>

    <h1 style="color:#1f4e79;">
    Region Sales Analysis
    </h1>

    """

    for region, sales in region_data.items():

        html += f"""

        <div style="
        padding:15px;
        margin-top:15px;
        border-radius:10px;
        background:#eef3f8;
        ">

        <h2>{region}</h2>

        <p style="font-size:18px;">
        Total Sales: ${sales:,.2f}
        </p>

        </div>
        """

    html += "</div></body></html>"

    return html

# -------------------------
# TOP PRODUCTS API
# -------------------------
@app.route("/top-products")
def top_products():

    search = request.args.get("search")

    products = df.groupby("Product Name")["Sales"].sum()
    total_products = df["Product Name"].nunique()

    if search:

        products = products[
            products.index.str.contains(search, case=False)
        ]

    products = products.sort_values(
        ascending=False
    ).head(10)

    html = f"""

    <html>

    <body style="
    font-family:Arial;
    background:#f4f6f9;
    padding:40px;
    ">

    <div style="
    background:white;
    padding:30px;
    border-radius:15px;
    box-shadow:0px 4px 10px rgba(0,0,0,0.1);
    ">
    <a href="/"
style="
background:#1f4e79;
color:white;
padding:10px 18px;
text-decoration:none;
border-radius:8px;
display:inline-block;
margin-bottom:20px;
">
⬅ Back to Dashboard
</a>

    <h1 style="color:#1f4e79;">
    Product Search
    </h1>
    <h3 style="color:#555;">
    📦 Total Products: {total_products}
    </h3>

    <form method="GET">

    <input type="text"
    name="search"
    placeholder="Search product..."
    style="
    padding:12px;
    width:300px;
    border-radius:8px;
    border:1px solid gray;
    ">

    <button type="submit"
    style="
    padding:12px 20px;
    background:#1f4e79;
    color:white;
    border:none;
    border-radius:8px;
    ">
    Search
    </button>

    </form>

    <br><br>

    """

    for product, sales in products.items():

        html += f"""

        <div style="
        padding:15px;
        margin-top:15px;
        border-radius:10px;
        background:#eef3f8;
        ">

        <h3>{product}</h3>

        <p style="font-size:18px;">
        Sales: ${sales:,.2f}
        </p>

        </div>

        """

    html += """

    </div>

    </body>

    </html>

    """

    return html

# -------------------------
# TOP CUSTOMERS API
# -------------------------
@app.route("/top-customers")
def top_customers():

    customers = df.groupby("Customer Name")["Sales"].sum() \
        .sort_values(ascending=False).head(10)
    total_customers = df["Customer Name"].nunique()

    html = f"""

    <html>

    <body style="
    font-family:Arial;
    background:#f4f6f9;
    padding:40px;
    ">

    <div style="
    background:white;
    padding:30px;
    border-radius:15px;
    box-shadow:0px 4px 10px rgba(0,0,0,0.1);
    ">
    <a href="/"
    style="
    background:#1f4e79;
    color:white;
    padding:10px 18px;
    text-decoration:none;
    border-radius:8px;
    display:inline-block;
    margin-bottom:20px;
    ">
    ⬅ Back to Dashboard
    </a>

    <h1 style="color:#1f4e79;">
    Top Customers
    </h1>
    <h3 style="color:#555;">
    👥 Total Customers: {total_customers}
    </h3>

    """

    for rank, (customer, sales) in enumerate(customers.items(), start=1):

        html += f"""

        <div style="
        padding:15px;
        margin-top:15px;
        border-radius:10px;
        background:#eef3f8;
        ">

        <h3>🏆 #{rank} - {customer}</h3>

        <p style="font-size:18px;">
        Total Sales: ${sales:,.2f}
        </p>

        </div>
        """

    html += "</div></body></html>"

    return html

# -------------------------
# RUN SERVER
# -------------------------

@app.route("/ai-insights")
def ai_insights():

    insights = generate_ai_insights()

    html_style = """

    <style>

    li{
        margin-bottom:12px;
    }

    h1,h2,h3{
        margin-top:25px;
        margin-bottom:15px;
    }

    </style>

    """

    return f"""

    {html_style}

<html>

<head>

<style>

body{{
    font-family:Arial;
    background:#f4f6f9;
    padding:40px;
}}

.container{{
    background:white;
    padding:40px;
    border-radius:20px;
    box-shadow:0px 6px 18px rgba(0,0,0,0.15);
    max-width:1000px;
    margin:auto;
}}

h1{{
    color:#1f4e79;
    margin-bottom:30px;
}}

</style>

</head>

<body>

<div class="container">

<a href="/"
style="
background:#1f4e79;
color:white;
padding:10px 18px;
text-decoration:none;
border-radius:8px;
display:inline-block;
margin-bottom:20px;
">
⬅ Back to Dashboard
</a>
<h1>AI Business Insights</h1>

<hr style="
margin-bottom:30px;
border:1px solid #ddd;
">

<div style="
font-size:15px;
line-height:1.8;
color:#333;
text-align:left;
background:#eef3f8;
padding:25px;
border-radius:15px;
">

{
insights
.replace("### ", "<h3 style='color:#1f4e79;margin-top:25px;margin-bottom:15px;'>")
.replace("## ", "<h2 style='color:#1f4e79;margin-top:25px;margin-bottom:15px;'>")
.replace("# ", "<h1 style='color:#1f4e79;margin-top:25px;margin-bottom:15px;'>")
.replace("**", "")
.replace("- ", "<li>")
.replace("\n", "</li>")
}

</div>

</div>

</body>

</html>

"""

@app.route("/ask-ai", methods=["POST"])
def ask_ai():

    question = request.form["question"]

    data_summary = f"""
    Total Sales: {df['Sales'].sum()}

    Top Region:
    {df.groupby('Region')['Sales'].sum().idxmax()}

    Top Category:
    {df.groupby('Category')['Sales'].sum().idxmax()}
    """

    prompt = f"""
    You are a business analyst AI.

    Business Data:
    {data_summary}

    User Question:
    {question}

    Give professional business answer.
    """

    from ai_insights import client
    import markdown

    try:

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        answer = markdown.markdown(
            response.choices[0].message.content
        )

    except Exception as e:

        answer = f"""
        <div style="
        color:red;
        font-size:18px;
        ">
        AI service is temporarily unavailable.<br><br>

        Error: {str(e)}
        </div>
        """

    return f"""

    <html>

    <body style="
    font-family:Arial;
    background:#f4f6f9;
    padding:40px;
    ">

    <div style="
    background:white;
    padding:30px;
    border-radius:15px;
    box-shadow:0px 4px 10px rgba(0,0,0,0.2);
    max-width:1000px;
    margin:auto;
    ">

    <h1 style="
    color:#1f4e79;
    ">
    AI Business Answer
    </h1>

    <div style="
    font-size:18px;
    line-height:1.8;
    ">
    {answer}
    </div>

    <br><br>

    <a href="/"
    style="
    background:#1f4e79;
    color:white;
    padding:10px 18px;
    text-decoration:none;
    border-radius:8px;
    ">
    ⬅ Back to Dashboard
    </a>

    </div>

    </body>

    </html>
    """

@app.route("/data")
def data_table():

    search = request.args.get("search", "")
    region = request.args.get("region", "")
    category = request.args.get("category", "")
    start_date = request.args.get("start_date", "")
    end_date = request.args.get("end_date", "")

    filtered_df = df

    filtered_df["Order Date"] = pd.to_datetime(
    filtered_df["Order Date"],
    dayfirst=True
)

    if region:
        filtered_df = filtered_df[
            filtered_df["Region"] == region
        ]

    if category:
        filtered_df = filtered_df[
            filtered_df["Category"] == category
        ]

    if start_date:
        filtered_df = filtered_df[
            filtered_df["Order Date"] >= start_date
        ]

    if end_date:
        filtered_df = filtered_df[
            filtered_df["Order Date"] <= end_date
        ]

    if search:
        filtered_df = filtered_df[
            filtered_df.astype(str)
            .apply(lambda row:
            row.str.contains(search, case=False).any(), axis=1)
        ]

    total_records = len(filtered_df)

    total_sales_filtered = round(
        filtered_df["Sales"].sum(), 2
    )

    selected_region = region if region else "All"

    selected_category = category if category else "All"
    unique_customers = filtered_df["Customer Name"].nunique()

    table = filtered_df.to_html(
    classes='table',
    index=False
)

    return f"""

    <html>

    <head>

    <style>

    body{{
        font-family:Arial;
        background:#f4f6f9;
        padding:40px;
    }}

    .table{{
        width:100%;
        border-collapse:collapse;
        background:white;
        box-shadow:0px 4px 10px rgba(0,0,0,0.1);
    }}

    .table th{{
        background:#1f4e79;
        color:white;
        padding:12px;
    }}

    .table td{{
        padding:10px;
        border:1px solid #ddd;
    }}

    h1{{
        color:#1f4e79;
    }}

    input{{
    padding:12px;
    width:300px;
    border-radius:8px;
    border:1px solid gray;
    margin-bottom:0;
}}

    button{{
        padding:12px 18px;
        background:#1f4e79;
        color:white;
        border:none;
        border-radius:8px;
        cursor:pointer;
    }}

    </style>

    </head>


<body>

<div style="
max-width:1200px;
margin:0 auto;
">

<a href="/"
style="
background:#1f4e79;
color:white;
padding:10px 18px;
text-decoration:none;
border-radius:8px;
display:inline-block;
margin-bottom:20px;
">
⬅ Back to Dashboard
</a>

<h1>📊 Business Data Explorer</h1>

    <form method="GET"
style="
display:flex;
flex-wrap:wrap;
gap:15px;
align-items:flex-start;
margin-bottom:20px;
">

<input type="text"
name="search"
placeholder="Search customer, city, region, product..."
value="{search}"
style="
padding:12px;
width:180px;
height:50px;
box-sizing:border-box;
border-radius:8px;
border:1px solid gray;
">

<select name="region"
style="
padding:12px;
width:180px;
height:50px;
box-sizing:border-box;
border-radius:8px;
border:1px solid gray;
">
<option value="" {"selected" if region == "" else ""}>All Regions</option>
<option value="East" {"selected" if region == "East" else ""}>East</option>
<option value="West" {"selected" if region == "West" else ""}>West</option>
<option value="South" {"selected" if region == "South" else ""}>South</option>
<option value="Central" {"selected" if region == "Central" else ""}>Central</option>
</select>

<select name="category"
style="
padding:12px;
width:180px;
height:50px;
box-sizing:border-box;
border-radius:8px;
border:1px solid gray;
">
<option value="" {"selected" if category == "" else ""}>All Categories</option>
<option value="Furniture" {"selected" if category == "Furniture" else ""}>Furniture</option>
<option value="Office Supplies" {"selected" if category == "Office Supplies" else ""}>Office Supplies</option>
<option value="Technology" {"selected" if category == "Technology" else ""}>Technology</option>
</select>

<input type="date"
name="start_date"
value="{start_date}"
style="
padding:12px;
width:180px;
height:50px;
box-sizing:border-box;
border-radius:8px;
border:1px solid gray;
">

<input type="date"
name="end_date"
value="{end_date}"
style="
padding:12px;
width:180px;
height:50px;
box-sizing:border-box;
border-radius:8px;
border:1px solid gray;
">

<button type="submit"
style="
height:50px;
background:#1f4e79;
color:white;
border:none;
border-radius:8px;
cursor:pointer;
width:180px;
">
Search
</button>

</form>

<div style="
display:grid;
grid-template-columns:repeat(5,1fr);
gap:20px;
margin-top:15px;
margin-bottom:25px;
">

<div style="
background:white;
padding:15px;
border-radius:12px;
box-shadow:0px 4px 12px rgba(0,0,0,0.08);
width:180px;
line-height:1.4;
">
📄 <b>Total Records</b><br>
{total_records}
</div>

<div style="
background:white;
padding:15px;
border-radius:12px;
box-shadow:0px 4px 12px rgba(0,0,0,0.08);
width:180px;
line-height:1.4;
">
💰 <b>Total Sales</b><br>
${total_sales_filtered:,.2f}
</div>

<div style="
background:white;
padding:15px;
border-radius:12px;
box-shadow:0px 4px 12px rgba(0,0,0,0.08);
width:180px;
line-height:1.4;
">
👥 <b>Customers</b><br>
{unique_customers}
</div>

<div style="
background:white;
padding:15px;
border-radius:12px;
box-shadow:0px 4px 12px rgba(0,0,0,0.08);
width:180px;
line-height:1.4;
">
📍 <b>Region</b><br>
{selected_region}
</div>

<div style="
background:white;
padding:15px;
border-radius:12px;
box-shadow:0px 4px 12px rgba(0,0,0,0.08);
width:180px;
line-height:1.4;
">
📦 <b>Category</b><br>
{selected_category}
</div>

</div>

{table}

</div>

    </body>

    </html>
    """
@app.route("/download-excel")
def download_excel():

    output = io.BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Business Data')

    output.seek(0)

    return send_file(
        output,
        download_name="business_data.xlsx",
        as_attachment=True
    )

@app.route("/download-report")
def download_report():

    report_path = "business_report.pdf"

    doc = SimpleDocTemplate(report_path)

    styles = getSampleStyleSheet()

    elements = []

    title = Paragraph(
        "AI Business Report",
        styles['Title']
    )

    elements.append(title)

    elements.append(Spacer(1, 20))

    total_sales = round(df["Sales"].sum(), 2)

    top_region = df.groupby("Region")["Sales"].sum().idxmax()

    top_category = df.groupby("Category")["Sales"].sum().idxmax()

    top_products = df.groupby("Product Name")["Sales"].sum() \
        .sort_values(ascending=False).head(5)

    products_text = "<br/>".join(
        [f"{i+1}. {name}" for i, name in enumerate(top_products.index)]
    )

    total_customers = df["Customer ID"].nunique()

    total_orders = df["Order ID"].nunique()

    avg_sale = round(
    df["Sales"].mean(), 2
)
    
    top_subcategory = (
    df.groupby("Sub-Category")["Sales"]
    .sum()
    .idxmax()
)

    report_text = f"""

    <b>Total Sales:</b> ${total_sales}

    <br/><br/>

    <b>Total Customers:</b> {total_customers}

    <br/><br/>

    <b>Total Orders:</b> {total_orders}

    <br/><br/>

    <b>Best Region:</b> {top_region}

    <br/><br/>

    <b>Best Category:</b> {top_category}

    <br/><br/>

    <b>Top 5 Products:</b>

    <br/><br/>

    {products_text}

    <br/><br/>

    <b>Average Sale:</b> ${avg_sale}

    <br/><br/>

    <b>Top Sub-Category:</b> {top_subcategory}

    <br/><br/>

    <b>AI Recommendation:</b>

    <br/><br/>

    Focus investments in the {top_region} region
and strengthen inventory planning for the
{top_category} category. Monitor customer
purchase trends and promote top-selling
products to improve revenue growth.

    """

    report = Paragraph(
        report_text,
        styles['BodyText']
    )

    elements.append(report)

    doc.build(elements)

    return send_file(
        report_path,
        as_attachment=True
    )

@app.route("/analytics")
def analytics():

    total_sales = round(
        df["Sales"].sum(), 2
    )

    total_customers = (
        df["Customer Name"].nunique()
    )

    total_orders = len(df)

    top_region = (
        df.groupby("Region")["Sales"]
        .sum()
        .idxmax()
    )

    top_category = (
        df.groupby("Category")["Sales"]
        .sum()
        .idxmax()
    )

    top_subcategory = (
        df.groupby("Sub-Category")["Sales"]
        .sum()
        .idxmax()
    )

    avg_sale = round(
        df["Sales"].mean(), 2
    )

    return render_template(
        "analytics.html",
        total_sales=total_sales,
        total_customers=total_customers,
        total_orders=total_orders,
        top_region=top_region,
        top_category=top_category,
        top_subcategory=top_subcategory,
        avg_sale=avg_sale
    )

if __name__ == "__main__":
    app.run(debug=True)
