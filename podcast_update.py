# Add podcast style to all analysis functions
with open('app.py', 'r') as f:
    content = f.read()

# Add to analyze_evolution
content = content.replace(
    'style_prompts = {\n        \'roasting\': "Be brutally honest',
    'style_prompts = {\n        \'podcast\': "Create a podcast discussion between Alex and Jordan analyzing how this person\'s music taste evolved. Script format.",\n        \'roasting\': "Be brutally honest'
)

# Add to analyze_battle  
content = content.replace(
    'style_prompts = {\n        \'roasting\': "Roast both',
    'style_prompts = {\n        \'podcast\': "Create a podcast where Alex and Jordan compare these two tastes head-to-head. Script format.",\n        \'roasting\': "Roast both'
)

# Add to analyze_manual_input
content = content.replace(
    'style_prompts = {\n        \'roasting\': "Roast their taste',
    'style_prompts = {\n        \'podcast\': "Create a podcast where Alex and Jordan discuss these preferences. Script format.",\n        \'roasting\': "Roast their taste'
)

with open('app.py', 'w') as f:
    f.write(content)

print("✅ Done")
