import sys

file_path = r'd:\NEW-ERP\storeflow-erp\backend\api\models.py'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if "class Client(models.Model):" in line:
        new_lines.append(line)
    elif "id = models.CharField(max_length=50, primary_key=True, default=generate_client_id)" in line:
        new_lines.append(line.replace("default=generate_client_id)", "default=generate_client_id, editable=False)"))
    elif "id = models.CharField(max_length=50, primary_key=True, default=generate_device_id)" in line:
        new_lines.append(line.replace("default=generate_device_id)", "default=generate_device_id, editable=False)"))
    elif "id = models.CharField(max_length=50, primary_key=True, default=generate_feature_id)" in line:
        new_lines.append(line.replace("default=generate_feature_id)", "default=generate_feature_id, editable=False)"))
    elif "id = models.CharField(max_length=50, primary_key=True, default=generate_clientfeat_id)" in line:
        new_lines.append(line.replace("default=generate_clientfeat_id)", "default=generate_clientfeat_id, editable=False)"))
    else:
        new_lines.append(line)

# Add the seeding function at the end
seed_func = """
def seed_ai_features():
    \"\"\"
    Helper function to seed the specific AI features requested by the user.
    \"\"\"
    ai_features = [
        ("Business Analyst", "Chat with your ERP data for insights."),
        ("Inventory Forecast", "Predicts stockouts based on sales velocity."),
        ("Invoice OCR", "Automatically scans and populates purchase orders from receipt images."),
        ("Reorder Optimization", "Recommends optimal minStock and reorder quantities."),
        ("HR & Performance AI", "Analyzes attendance patterns, employee risk, and shift scheduling."),
        ("Recruitment AI", "Parses and scores resumes automatically."),
        ("HR Assistant", "A dedicated policy-aware chatbot for staff."),
    ]
    
    from api.models import Feature
    for name, desc in ai_features:
        Feature.objects.get_or_create(name=name, defaults={'description': desc})
    print(f"Successfully seeded {len(ai_features)} AI features.")
"""

if not any("def seed_ai_features()" in line for line in new_lines):
    new_lines.append(seed_func)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Modifications applied successfully.")
