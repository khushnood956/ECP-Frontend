import os
import re

models_dir = 'app/models'
files = [os.path.join(models_dir, f) for f in os.listdir(models_dir) if f.endswith('.py') and f != '__init__.py']
files.append('app/db/base.py')

for filepath in files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'Mapped[' in content:
        # Add import Optional if not present
        if 'from typing import ' in content and 'Optional' not in content:
            content = re.sub(r'from typing import (.*)', r'from typing import Optional, \1', content, count=1)
        elif 'from typing import ' not in content and 'Optional' not in content:
            content = "from typing import Optional\n" + content
            
        # Replace str | None -> Optional[str], datetime | None -> Optional[datetime], etc.
        # Handle all type | None inside Mapped[]
        content = re.sub(r'Mapped\[([a-zA-Z0-9_]+)\s*\|\s*None\]', r'Mapped[Optional[\1]]', content)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filepath}")
