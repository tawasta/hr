{
    "name": "HR Autofill Employee Job Title",
    "summary": "Automatically autofills employee job title upon creation via portal",
    "version": "17.0.1.0.1",
    "category": "Human Resources",
    "website": "https://github.com/tawasta/hr",
    "author": "Futural",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["hr", "hr_expense"],
    "data": [
        "views/res_config_settings_views.xml",
    ],
}
