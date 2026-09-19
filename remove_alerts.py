import glob, re

files = [
    'frontend-dashboard/src/components/InspectionForm.jsx',
    'frontend-dashboard/src/components/ReviewInterface.jsx',
    'frontend-dashboard/src/pages/CasesPage.jsx',
    'frontend-dashboard/src/pages/InvestigatorManagementPage.jsx',
    'frontend-dashboard/src/pages/ProjectDetailPage.jsx'
]

for p in files:
    with open(p, 'r', encoding='utf-8') as f:
        c = f.read()
    
    # 1. Add import
    if 'useToast' not in c:
        if 'components/' in p:
            c = "import { useToast } from '../contexts/ToastContext';\n" + c
        else:
            c = "import { useToast } from '../contexts/ToastContext';\n" + c

    # 2. Add hook
    if 'const { showToast } = useToast();' not in c:
        c = re.sub(r'(export default function \w+\(.*\) \{)', r'\1\n  const { showToast } = useToast();', c)
    
    # 3. Replace alert
    c = re.sub(r'alert\((.*?)\);', r'showToast(\1);', c)
    
    with open(p, 'w', encoding='utf-8') as f:
        f.write(c)
print('Done!')
