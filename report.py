import os
import json
import webbrowser
from jinja2 import Environment, FileSystemLoader

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, 'data')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')

def render_report():
    with open(os.path.join(DATA_DIR, 'pulse.json')) as f:
        pulse = json.load(f)

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

    md_template = env.get_template('pulse.md.j2')
    md_output = md_template.render(pulse=pulse)
    md_path = os.path.join(OUTPUT_DIR, 'weekly_pulse.md')
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_output)

    html_template = env.get_template('pulse.html.j2')
    html_output = html_template.render(pulse=pulse)
    html_path = os.path.join(OUTPUT_DIR, 'weekly_pulse.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_output)

    print(f"Report saved: output/weekly_pulse.md")
    print(f"Report saved: output/weekly_pulse.html")
    webbrowser.open(f'file:///{html_path}')

if __name__ == '__main__':
    render_report()
