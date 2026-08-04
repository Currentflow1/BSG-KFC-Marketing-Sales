from django.shortcuts import render

def dashboard(request):
    dashboard_sections = [
        {
            "title": "Operations",
            "cards": [
                {
                    "title": "Orders",
                    "description": "Create and manage customer orders.",
                    "href": "/orders/",
                    "emoji": "🛒",
                },
                {
                    "title": "Transaction Logs",
                    "description": "View all user activities and audit history.",
                    "href": "/transaction_logs/",
                    "emoji": "📜",
                },
                {
                    "title": "Records",
                    "description": "View stock movement and export records.",
                    "href": "/records/",
                    "emoji": "📋",
                },
                {
                    "title": "Forecasting",
                    "description": "View Stock Data.",
                    "href": "/forecasting/",
                    "emoji": "📊",
                },
            ],
        },
        {
            "title": "Master Data",
            "cards": [
                {
                    "title": "Products",
                    "description": "Manage finished products.",
                    "href": "/products/",
                    "emoji": "📦",
                },
                {
                    "title": "Area Prices",
                    "description": "Manage area-based product pricing.",
                    "href": "/area_prices/",
                    "emoji": "💷",
                },
                {
                    "title": "Customers",
                    "description": "Manage customer information.",
                    "href": "/customers/",
                    "emoji": "👥",
                },
                {
                    "title": "Employees",
                    "description": "Manage employee records.",
                    "href": "/employees/",
                    "emoji": "👤",
                },
                {
                    "title": "Admin",
                    "description": "Manage app data in the admin panel.",
                    "href": "/admin/",
                    "emoji": "🔐",
                },
            ],
        },
    ]

    return render(request, "dashboard/dashboard.html", {
        "sections": dashboard_sections
    })