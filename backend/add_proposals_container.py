"""Add proposals container to database.py."""
import re

with open('src/database.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add proposals container to the list
old_containers = '''            container_definitions = [
                ("meetings", "/id"),
                ("tasks", "/id"),
                ("agents", "/id"),
                ("decisions", "/id"),
                ("resources", "/id"),
                ("tech_radar_items", "/id"),
                ("code_patterns", "/id"),
            ]'''

new_containers = '''            container_definitions = [
                ("meetings", "/id"),
                ("tasks", "/id"),
                ("agents", "/id"),
                ("proposals", "/id"),
                ("decisions", "/id"),
                ("resources", "/id"),
                ("tech_radar_items", "/id"),
                ("code_patterns", "/id"),
            ]'''

content = content.replace(old_containers, new_containers)

with open('src/database.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Added proposals container to database.py")
