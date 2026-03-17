"""
run.py — Interactive CLI Command Center
========================================
Main entry point for the JOBS_AUTOMATION system.

Usage:
    python run.py          # Interactive menu
    python run.py --demo   # Test AI without scraping
"""

import os
import sys
import asyncio
import argparse
import logging
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)

BANNER = """
╔══════════════════════════════════════════════════════════╗
  🤖  AUTONOMOUS JOB HUNTING & B2B LEAD GEN CRM
      by Parameswar Swain | parameswar.dev
╠══════════════════════════════════════════════════════════╣
  [1] 🏙  Hunt LOCAL  — Odisha Companies (cold email)
  [2] 🌍  Hunt GLOBAL — YC/HN React Startups (Remote)
  [3] 📊  View Stats & Top Leads
  [4] 📤  Export Leads to CSV
  [5] 📬  Send Approved Emails (Gmail SMTP)
  [6] 🌐  Launch Web Dashboard (FastAPI + Next.js)
  [7] 🔒  Run GDPR Data Shield (dry-run)
  [8] 🧪  Demo Mode (test AI, no scraping)
  [9] 🎯  REAL Odisha Jobs — Naukri + Internshala
  [J] 🔍  HIDDEN BBSR Jobs — Beats Naukri/Indeed ← BEST
  [0] ❌  Exit
╚══════════════════════════════════════════════════════════╝"""

LOCAL_MENU = """
  Local Hunt — Odisha Jobs
  ────────────────────────
  [1] Direct Scrape (30 Odisha/Indian IT companies) ← NO API needed
  [2] ATS Dorks — Greenhouse + Lever (needs search API)
  [3] ATS Dorks — Workable + generic careers (needs search API)
  [4] All ATS dorks combined (needs search API)
  [0] Back"""

GLOBAL_MENU = """
  Global Hunt — Remote React Startups
  ──────────────────────────────────
  [1] Known Startups (Linear, Vercel, Resend…)
  [2] Hacker News Who's Hiring
  [3] YC Companies (needs SERPAPI_KEY)
  [4] Wellfound (needs SERPAPI_KEY)
  [0] Back"""


async def menu_local(orch):
    print(LOCAL_MENU)
    choice = input("  Choose: ").strip()
    preset_map = {
        "1": "odisha_direct",   # No API needed — direct URL scraping
        "2": "odisha_ats_1",    # Greenhouse + Lever dorks
        "3": "odisha_ats_3",    # Workable + generic
        "4": "odisha_ats_all",  # All dorks
    }
    if choice in preset_map:
        await orch.run_preset(preset_map[choice], mode="local")
    elif choice == "0":
        return
    else:
        print("  Invalid choice.")


async def menu_global(orch):
    print(GLOBAL_MENU)
    choice = input("  Choose: ").strip()
    preset_map = {
        "1": "known_startups",
        "2": "hn_hiring",
        "3": "yc_react",
        "4": "wellfound",
    }
    if choice in preset_map:
        await orch.run_preset(preset_map[choice], mode="global")
    elif choice == "0":
        return
    else:
        print("  Invalid choice.")


def show_stats(orch):
    s = orch.db.get_stats()
    print(f"""
╔══════════════════════════════════════════════════════╗
  📊 CRM STATS
  Companies    : {s['companies']}
  Leads        : {s['leads']}
  Email Drafts : {s['drafts']}
  Sent         : {s['sent']}
  Replied      : {s['replied']}""")
    if s["top"]:
        import json as _json
        print("  ──────────────────────────────────────────────────")
        print(f"  {'Company':<22} {'Sc':>3}  {'Mode':<8} {'Stack':<25} Contact")
        print(f"  {'─'*22} {'─'*3}  {'─'*8} {'─'*25} {'─'*15}")
        for row in s["top"]:
            try:
                tech = _json.loads(row[2]) if row[2] else []
            except Exception:
                tech = []
            ts = ", ".join(tech[:2])
            print(f"  {str(row[0]):<22} {str(row[1]):>3}  {str(row[3]):<8} {ts:<25} {row[4] or '?'}")
    print("╚══════════════════════════════════════════════════════╝")


async def demo_mode(orch):
    print("\n[DEMO — AI pipeline test, no scraping]\n")
    import random
    from backend.orchestrator import score_lead

    company = {
        "name":"Linear","domain":"linear.app",
        "tech_stack":["React","TypeScript","GraphQL","Electron","Next.js"],
        "description":"Issue tracking for high-performance software teams.",
        "pain_points":["real-time sync latency","React re-render at scale"],
        "funding_stage":"Series B","funding_amount":"$35M","mode":"global",
    }
    contact = {"full_name":"Tuomas Artman","job_title":"CTO"}
    score   = score_lead(company, contact, {})
    draft   = await orch.ai.generate_email(company, contact, {})
    orch._print_result(company, contact, draft, score)


def launch_dashboard():
    import subprocess
    print("\n  Starting FastAPI backend…")
    print("  Dashboard will be at: http://localhost:3000")
    print("  API at:               http://localhost:8000/docs")
    print("  Press Ctrl+C to stop\n")

    api_proc = subprocess.Popen(
        [sys.executable, "api_server.py"],
        cwd=str(Path(__file__).parent),
    )
    frontend_dir = Path(__file__).parent / "frontend"
    fe_proc = None
    if frontend_dir.exists():
        fe_proc = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=str(frontend_dir),
            shell=sys.platform == "win32",
        )
    try:
        api_proc.wait()
    except KeyboardInterrupt:
        api_proc.terminate()
        if fe_proc:
            fe_proc.terminate()
        print("\n  Dashboard stopped.")


async def main():
    parser = argparse.ArgumentParser(description="Jobs Automation CLI")
    parser.add_argument("--demo",  action="store_true")
    parser.add_argument("--stats", action="store_true")
    args = parser.parse_args()

    # Lazy import to avoid startup cost
    from backend.orchestrator import Orchestrator
    orch = Orchestrator()

    if args.demo:
        await demo_mode(orch)
        return
    if args.stats:
        show_stats(orch)
        return

    while True:
        print(BANNER)
        choice = input("  Enter choice: ").strip()

        if choice == "0":
            print("\n  Goodbye! 👋\n")
            break
        elif choice == "1":
            await menu_local(orch)
        elif choice == "2":
            await menu_global(orch)
        elif choice == "3":
            show_stats(orch)
        elif choice == "4":
            from backend.exporter import export_csv
            path = export_csv()
            if path:
                print(f"\n  ✅ Exported → {path}\n")
        elif choice == "5":
            from backend.smtp_sender import send_approved_drafts
            confirm = input("  Send all approved emails? (y/n): ").strip().lower()
            if confirm == "y":
                send_approved_drafts()
        elif choice == "6":
            launch_dashboard()
        elif choice == "7":
            from backend.data_shield import DataShield
            shield = DataShield()
            report = shield.run_purge(dry_run=True)
            print(f"\n  [DRY-RUN] Would purge {report['purged']} leads older than {report['retention_days']} days\n")
        elif choice == "8":
            await demo_mode(orch)
        elif choice == "9":
            from backend.naukri_scraper import scrape_all_odisha_jobs, print_jobs
            print("\n  🎯 Scraping REAL Odisha jobs from Naukri + Internshala...")
            print("  ⏳ This takes 2-3 minutes. Sit back.\n")
            real_jobs = await scrape_all_odisha_jobs(max_total=50)
            print_jobs(real_jobs)
        elif choice.lower() == "j":
            import os
            from backend.bbsr_jobs import hunt_bbsr_jobs, print_jobs_terminal
            serper_key = os.getenv("SERPER_API_KEY","")
            print("\n  🌍 WORLD-WIDE BHUBANESWAR JOB HUNTER")
            print("  ─────────────────────────────────────────────────")
            print("  Hits 60+ sources: Naukri, Indeed, Internshala, Shine,")
            print("  TimesJobs, Glassdoor, Wellfound, Reddit, Twitter,")
            print("  20 Bhubaneswar company career pages, ATS portals,")
            print("  Google Jobs, Google dorks for hidden jobs")
            print("  Skills: React, Java, SQL, HTML/CSS/JS, Full Stack")
            print("  Target: 2024/2025/2026 passout, 0-1 year")
            if not serper_key:
                print("  ⚠  Tip: Add SERPER_API_KEY to .env for more hidden jobs")
                print("     Get 2500 free searches → serper.dev")
            print("  ⏳ Takes 8-12 minutes (60+ sources). Running…\n")
            bbsr_jobs = await hunt_bbsr_jobs(
                serper_key=serper_key,
                max_total=150,
            )
            print_jobs_terminal(bbsr_jobs)
            # Save to JSON for dashboard
            import json
            with open("bbsr_jobs_latest.json","w",encoding="utf-8") as f:
                json.dump([j.to_dict() for j in bbsr_jobs], f, indent=2, ensure_ascii=False)
            print(f"  💾 Saved to bbsr_jobs_latest.json ({len(bbsr_jobs)} jobs)\n")
        else:
            print("  Invalid choice — try again.")


if __name__ == "__main__":
    asyncio.run(main())