import os
import re

print("Converting React/Vite project to a No-NPM standalone HTML file...")

BASE_DIR = r"c:\Users\USER\Desktop\SIH26102\frontend-dashboard\src"

# Order of files to concatenate (dependencies first)
files_in_order = [
    "services/apiClient.js",
    "components/InspectionForm.jsx",
    "components/ReviewInterface.jsx",
    "pages/DashboardPage.jsx",
    "pages/AuditTrailPage.jsx",
    "App.jsx"
]

combined_code = ""

for rel_path in files_in_order:
    full_path = os.path.join(BASE_DIR, rel_path.replace("/", os.sep))
    if not os.path.exists(full_path):
        print(f"Warning: {full_path} not found.")
        continue
        
    with open(full_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Remove imports
    content = re.sub(r"^import .*?;?\n", "", content, flags=re.MULTILINE)
    
    # Change 'export default function Name' to 'function Name'
    content = re.sub(r"^export default function (\w+)", r"function \1", content, flags=re.MULTILINE)
    # Change 'export default Name' to nothing (handled by just declaring it)
    content = re.sub(r"^export default .*?;?\n", "", content, flags=re.MULTILINE)
    
    combined_code += f"\n// --- {rel_path} ---\n{content}\n"

# Wrap in HTML
html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CivicShield AI MVP</title>
    
    <!-- CDNs for React, ReactDOM, Babel, Tailwind, Axios -->
    <script crossorigin src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
</head>
<body class="bg-gray-100 min-h-screen">
    <div id="root"></div>

    <script type="text/babel">
        // Make React hooks globally available so components don't need imports
        const {{ useState, useEffect }} = React;
        
        {combined_code}
        
        // Render the App
        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<App />);
    </script>
</body>
</html>
"""

out_path = r"c:\Users\USER\Desktop\SIH26102\index.html"
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html_content)
    
print(f"Successfully compiled frontend to {out_path}!")
print("You can now open this file directly in your browser or run:")
print("python -m http.server 3000")
