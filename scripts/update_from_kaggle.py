#!/usr/bin/env python3
"""
Update competition data from Kaggle (requires user's machine with API egress).

USAGE (on your machine with Kaggle API access):
    python scripts/update_from_kaggle.py

This script:
1. Pulls current leaderboard state (mu, sigma, episodes)
2. Downloads latest episode replays/logs
3. Analyzes meta composition
4. Updates ladder tracking
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path

def run_cmd(cmd, desc=""):
    """Run shell command and return output."""
    if desc:
        print(f"\n🔄 {desc}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print(f"✅ Done")
            return result.stdout
        else:
            print(f"❌ Error: {result.stderr}")
            return None
    except subprocess.TimeoutExpired:
        print(f"⏱️ Timeout")
        return None

def main():
    """Main update workflow."""

    base_dir = Path(__file__).parent.parent
    os.chdir(base_dir)

    print("=" * 60)
    print("KAGGLE API UPDATE SCRIPT")
    print(f"Timestamp: {datetime.utcnow().isoformat()}Z")
    print("=" * 60)

    # 1. Pull leaderboard
    print("\n📊 STEP 1: Fetch Leaderboard")
    leaderboard_cmd = (
        "python3 << 'EOPY'\n"
        "from kaggle.api.kaggle_api_extended import KaggleApi\n"
        "import json\n"
        "from datetime import datetime\n"
        "\n"
        "api = KaggleApi()\n"
        "api.authenticate()\n"
        "\n"
        "# Get competition leaderboard\n"
        "leaderboard = api.competition_leaderboard('pokemon-tcg-ai-battle')\n"
        "\n"
        "# Save snapshot\n"
        "lb_data = []\n"
        "for entry in leaderboard:\n"
        "    lb_data.append({\n"
        "        'TeamId': entry.get('TeamId'),\n"
        "        'TeamName': entry.get('TeamName'),\n"
        "        'SubmissionDate': str(entry.get('SubmissionDate', '')),\n"
        "        'Score': entry.get('Score'),\n"
        "    })\n"
        "\n"
        "snap_file = f\"report/leaderboard_snap_{datetime.utcnow().strftime('%Y%m%d_%H%M')}.json\"\n"
        "with open(snap_file, 'w') as f:\n"
        "    json.dump(lb_data, f, indent=2)\n"
        "\n"
        "print(f'✅ Leaderboard: {len(lb_data)} teams')\n"
        "print(f'📁 Saved to: {snap_file}')\n"
        "EOPY"
    )
    leaderboard_result = run_cmd(leaderboard_cmd, "Fetching current leaderboard state")
    if leaderboard_result:
        print(leaderboard_result)

    # 2. Download episode data
    print("\n📥 STEP 2: Download Episode Dataset")
    episodes_cmd = (
        "kaggle datasets download -d kaggle/pokemon-tcg-ai-battle-episodes-index "
        "-p data/episodes/raw --unzip -q && "
        "echo '✅ Episodes downloaded to data/episodes/raw/'"
    )
    episodes_result = run_cmd(episodes_cmd, "Downloading episode replays (may be large)")

    # 3. Analyze episodes
    print("\n🔍 STEP 3: Analyze Episode Meta")
    analyze_cmd = (
        "python3 scripts/analyze_daily_episodes.py && "
        "echo '✅ Episode analysis complete'"
    )
    analyze_result = run_cmd(analyze_cmd, "Analyzing yesterday's battles")

    # 4. Update competition data
    print("\n📋 STEP 4: Fetch Competition Data")
    data_cmd = (
        "kaggle competitions download pokemon-tcg-ai-battle "
        "-p data/competition_data --unzip -q 2>/dev/null && "
        "echo '✅ Competition data updated' || "
        "echo '⚠️  Competition data not available (may have ended)'"
    )
    data_result = run_cmd(data_cmd, "Downloading competition metadata")

    # 5. Update our submission status
    print("\n📈 STEP 5: Track Our Submissions")
    track_cmd = (
        "python3 << 'EOPY'\n"
        "from kaggle.api.kaggle_api_extended import KaggleApi\n"
        "import json\n"
        "\n"
        "api = KaggleApi()\n"
        "api.authenticate()\n"
        "\n"
        "# Get our submissions\n"
        "submissions = api.competition_submissions('pokemon-tcg-ai-battle')\n"
        "\n"
        "# Save to file\n"
        "sub_data = []\n"
        "for sub in submissions[:20]:  # Last 20\n"
        "    sub_data.append({\n"
        "        'Id': sub.get('Id'),\n"
        "        'Ref': sub.get('Ref'),\n"
        "        'SubmissionDate': str(sub.get('SubmissionDate', '')),\n"
        "        'Score': sub.get('Score'),\n"
        "        'PublicScore': sub.get('PublicScore'),\n"
        "    })\n"
        "\n"
        "with open('report/our_submissions.json', 'w') as f:\n"
        "    json.dump(sub_data, f, indent=2)\n"
        "\n"
        "print(f'✅ Our submissions: {len(sub_data)} retrieved')\n"
        "EOPY"
    )
    track_result = run_cmd(track_cmd, "Tracking our submission history")
    if track_result:
        print(track_result)

    print("\n" + "=" * 60)
    print("✅ UPDATE COMPLETE")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Review report/leaderboard_snap_*.json for current standings")
    print("  2. Run: python scripts/analyze_daily_episodes.py")
    print("  3. Run: git add report/ && git commit -m 'Daily Kaggle update'")
    print("=" * 60)

if __name__ == "__main__":
    main()
