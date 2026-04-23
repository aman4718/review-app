import subprocess
import sys
import os
import argparse

def run_phase(name, fn):
    print(f"\n{'='*50}")
    print(f"  {name}")
    print(f"{'='*50}")
    try:
        fn()
        print(f"  Done.")
    except Exception as e:
        print(f"  FAILED: {e}")
        sys.exit(1)

def phase_scrape():
    result = subprocess.run(['node', 'scraper.js'], capture_output=False)
    if result.returncode != 0:
        raise RuntimeError("Scraper failed")

def phase_cluster():
    import cluster
    cluster.run_clustering()

def phase_analyse():
    import analyse
    analyse.analyse()

def phase_report():
    import report
    report.render_report()

def phase_email():
    import emailer
    emailer.send_email()

PHASES = {
    'scrape': ('Phase 1 — Scraping Play Store Reviews', phase_scrape),
    'cluster': ('Phase 2 — BERTopic Clustering', phase_cluster),
    'analyse': ('Phase 3 — Groq LLM Analysis', phase_analyse),
    'report': ('Phase 4 — Report Generation', phase_report),
    'email': ('Phase 5 — Email Delivery', phase_email),
}

def main():
    parser = argparse.ArgumentParser(description='ChatGPT Review Analyser Pipeline')
    parser.add_argument('--phase', choices=PHASES.keys(), help='Run a single phase only')
    args = parser.parse_args()

    os.makedirs('data', exist_ok=True)
    os.makedirs('output', exist_ok=True)

    if args.phase:
        name, fn = PHASES[args.phase]
        run_phase(name, fn)
    else:
        for phase_key in ['scrape', 'cluster', 'analyse', 'report', 'email']:
            name, fn = PHASES[phase_key]
            run_phase(name, fn)

    print("\nPipeline complete.")

if __name__ == '__main__':
    main()
