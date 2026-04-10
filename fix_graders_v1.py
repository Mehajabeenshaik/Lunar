import re

# Read the file
with open('content_moderation_env/graders_v1.py', 'r') as f:
    content = f.read()

# Replace all instances
content = re.sub(r'return\s+1\.0(?!\d)', 'return 0.99', content)
content = re.sub(r'return\s+0\.0(?!\d)', 'return 0.01', content)

lines = content.split('\n')
new_lines = []
for line in lines:
    if not line.strip().startswith('#'):
        line = re.sub(r'=\s+1\.0(?!\d)(?!\s*#)', '= 0.99', line)
        line = re.sub(r'=\s+0\.0(?!\d)(?!\s*#)', '= 0.01', line)
    new_lines.append(line)

new_content = '\n'.join(new_lines)

# Write back
with open('content_moderation_env/graders_v1.py', 'w') as f:
    f.write(new_content)

print("✅ Fixed graders_v1.py: All 1.0->0.99, 0.0->0.01")
