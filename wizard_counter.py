import streamlit as st
import pandas as pd
import altair as alt
import json
import os
import requests
from datetime import datetime
from pathlib import Path

st.set_page_config(page_title="The Grand Fardini", page_icon="🧙", layout="wide")

# Touchscreen-optimized CSS
st.markdown("""
<style>
    /* ===== BUTTONS - Larger touch targets ===== */
    .stButton > button {
        min-height: 54px !important;
        font-size: 1.1rem !important;
        padding: 0.75rem 1.5rem !important;
        border-radius: 12px !important;
        margin: 6px 0 !important;
        font-weight: 500 !important;
    }
    
    /* Primary buttons even more prominent */
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="baseButton-primary"] {
        min-height: 60px !important;
        font-size: 1.25rem !important;
        font-weight: 600 !important;
    }
    
    /* ===== NUMBER INPUTS - Larger steppers ===== */
    .stNumberInput > div > div > input {
        font-size: 1.5rem !important;
        height: 54px !important;
        text-align: center !important;
        font-weight: 600 !important;
    }
    
    /* Make +/- stepper buttons properly sized and centered */
    .stNumberInput button {
        min-width: 48px !important;
        min-height: 48px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 0 !important;
    }
    
    .stNumberInput button svg {
        width: 18px !important;
        height: 18px !important;
        position: relative !important;
        top: -5px !important;
    }
    
    .stNumberInput [data-testid="stNumberInputStepUp"],
    .stNumberInput [data-testid="stNumberInputStepDown"] {
        width: 48px !important;
        height: 48px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    /* ===== RADIO BUTTONS - Tab navigation ===== */
    .stRadio > div {
        gap: 8px !important;
    }
    
    .stRadio > div > label {
        padding: 14px 24px !important;
        font-size: 1.15rem !important;
        border-radius: 12px !important;
        min-height: 52px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        background: #f0f2f6 !important;
        border: 2px solid transparent !important;
        transition: all 0.15s ease !important;
        font-weight: 500 !important;
    }
    
    .stRadio > div > label:hover {
        background: #e0e2e6 !important;
        transform: scale(1.02) !important;
    }
    
    .stRadio > div > label[data-checked="true"],
    .stRadio > div > label:has(input:checked) {
        background: #ff4b4b !important;
        color: white !important;
        border-color: #ff4b4b !important;
    }
    
    /* ===== SELECT BOXES ===== */
    .stSelectbox > div > div {
        min-height: 52px !important;
        font-size: 1.1rem !important;
    }
    
    .stSelectbox [data-baseweb="select"] {
        min-height: 52px !important;
    }
    
    /* ===== TEXT INPUTS ===== */
    .stTextInput > div > div > input {
        min-height: 52px !important;
        font-size: 1.1rem !important;
        padding: 12px !important;
    }
    
    /* ===== CHECKBOXES - Larger tap targets ===== */
    .stCheckbox > label {
        padding: 10px 0 !important;
        min-height: 48px !important;
        display: flex !important;
        align-items: center !important;
    }
    
    .stCheckbox > label > span {
        font-size: 1.1rem !important;
    }
    
    .stCheckbox > label > div[data-testid="stCheckbox"] {
        width: 26px !important;
        height: 26px !important;
    }
    
    /* ===== EXPANDERS ===== */
    .streamlit-expanderHeader {
        font-size: 1.15rem !important;
        min-height: 52px !important;
        padding: 12px !important;
    }
    
    /* ===== SPACING & LAYOUT ===== */
    [data-testid="column"] {
        padding: 0 10px !important;
    }
    
    /* More space between form elements */
    .stForm > div > div {
        margin-bottom: 1rem !important;
    }
    
    /* ===== SUBHEADERS & TEXT ===== */
    h2, .stSubheader {
        font-size: 1.6rem !important;
        margin-top: 1.5rem !important;
    }
    
    h3 {
        font-size: 1.3rem !important;
    }
    
    /* Player name labels larger */
    .stNumberInput label, .stTextInput label {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
    }
    
    /* ===== TOUCH FEEDBACK ===== */
    button:active, .stButton > button:active {
        transform: scale(0.97) !important;
        transition: transform 0.1s !important;
    }
    
    /* ===== DATA TABLES ===== */
    .stDataFrame td, .stDataFrame th {
        font-size: 1rem !important;
        padding: 12px 8px !important;
    }
    
    /* ===== ALERTS & INFO BOXES ===== */
    .stAlert, .stInfo, .stWarning, .stSuccess, .stError {
        padding: 16px !important;
        font-size: 1.05rem !important;
        border-radius: 10px !important;
    }
    
    /* ===== DIALOG/MODAL BUTTONS ===== */
    [data-testid="stModal"] button {
        min-height: 50px !important;
        min-width: 50px !important;
    }
    
    /* ===== COLOR PICKER ===== */
    .stColorPicker > div {
        min-height: 48px !important;
    }
    
    /* ===== SLIDER ===== */
    .stSlider > div {
        padding: 10px 0 !important;
    }
    
    .stSlider [data-testid="stThumbValue"] {
        font-size: 1.1rem !important;
    }
    
    /* ===== TABS CONTAINER PADDING ===== */
    .block-container {
        padding: 1rem 2rem 3rem 2rem !important;
    }
    
    /* ===== DOWNLOAD BUTTON ===== */
    .stDownloadButton > button {
        min-height: 54px !important;
        font-size: 1.1rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Save directory for game files
SAVE_DIR = Path(__file__).parent / "saved_games"
SAVE_DIR.mkdir(exist_ok=True)

# API key config file
API_KEY_FILE = Path(__file__).parent / ".api_key"

def load_saved_api_key():
    """Load the API key from the config file if it exists."""
    if API_KEY_FILE.exists():
        try:
            with open(API_KEY_FILE, 'r') as f:
                return f.read().strip()
        except Exception:
            pass
    return ""

def save_api_key(api_key):
    """Save the API key to a config file."""
    try:
        with open(API_KEY_FILE, 'w') as f:
            f.write(api_key)
    except Exception:
        pass

# NVIDIA API Configuration
NVIDIA_API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
NVIDIA_MODELS = {
    "DeepSeek-R1 (Slower, More Creative)": "deepseek-ai/deepseek-r1",
    "Llama 3.1 70B (Fast)": "meta/llama-3.1-70b-instruct",
    "Llama 3.1 8B (Fastest)": "meta/llama-3.1-8b-instruct",
}
DEFAULT_MODEL = "meta/llama-3.1-70b-instruct"  # Faster default

# Default colors for new players
DEFAULT_COLORS = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7", "#DDA0DD", "#98D8C8", "#F7DC6F"]

# Initialize session state
if 'players' not in st.session_state:
    st.session_state.players = []
if 'current_round' not in st.session_state:
    st.session_state.current_round = 1
if 'game_data' not in st.session_state:
    st.session_state.game_data = {}  # {round: {player: {'bid': x, 'tricks': y}}}
if 'game_started' not in st.session_state:
    st.session_state.game_started = False
if 'max_rounds' not in st.session_state:
    st.session_state.max_rounds = 0
if 'current_save_file' not in st.session_state:
    st.session_state.current_save_file = None
if 'player_colors' not in st.session_state:
    st.session_state.player_colors = {}  # {player_name: hex_color}
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 0  # 0=Bids, 1=Tricks, 2=Scoreboard
if 'starting_dealer_index' not in st.session_state:
    st.session_state.starting_dealer_index = 0  # Index of dealer for round 1
if 'shot_players' not in st.session_state:
    st.session_state.shot_players = []  # Players who need to take a shot
if 'round_roasts' not in st.session_state:
    st.session_state.round_roasts = {}  # {round_num: roast_text}
if 'nvidia_api_key' not in st.session_state:
    st.session_state.nvidia_api_key = load_saved_api_key()
if 'enable_roasts' not in st.session_state:
    st.session_state.enable_roasts = False
if 'api_verified' not in st.session_state:
    st.session_state.api_verified = False
if 'selected_model' not in st.session_state:
    st.session_state.selected_model = DEFAULT_MODEL
if 'game_finished' not in st.session_state:
    st.session_state.game_finished = False
if 'show_celebration' not in st.session_state:
    st.session_state.show_celebration = False
if 'manual_roast' not in st.session_state:
    st.session_state.manual_roast = {}  # For on-demand roasts {player: roast}
if 'game_summary' not in st.session_state:
    st.session_state.game_summary = None  # LLM-generated end-game summary
if 'game_stats' not in st.session_state:
    st.session_state.game_stats = None  # Analyzed game statistics

def calculate_score(bid, tricks):
    """Calculate score for a round based on bid and tricks won."""
    if bid == tricks:
        return 20 + (10 * tricks)
    else:
        return -10 * abs(bid - tricks)

def get_total_scores():
    """Calculate total scores for all players (only completed rounds, not current round unless game is finished)."""
    totals = {player: 0 for player in st.session_state.players}
    current_round = st.session_state.get('current_round', 1)
    game_finished = st.session_state.get('game_finished', False)
    
    for round_num, round_data in st.session_state.game_data.items():
        # Count rounds before the current round, OR all rounds if game is finished
        if round_num < current_round or game_finished:
            for player, data in round_data.items():
                if data['bid'] is not None and data['tricks'] is not None:
                    totals[player] += calculate_score(data['bid'], data['tricks'])
    return totals

def analyze_game_stats():
    """Analyze the full game and return comprehensive statistics."""
    max_rounds = st.session_state.max_rounds
    players = st.session_state.players
    
    # Build running totals per round for each player
    running_totals = {p: [0] for p in players}  # Start at 0
    round_scores = {p: [] for p in players}
    round_standings = []  # List of standings after each round
    
    for r in range(1, max_rounds + 1):
        if r in st.session_state.game_data:
            round_standing = {}
            for p in players:
                data = st.session_state.game_data[r].get(p, {'bid': None, 'tricks': None})
                bid = data['bid']
                tricks = data['tricks']
                if bid is not None and tricks is not None:
                    score = calculate_score(bid, tricks)
                    round_scores[p].append(score)
                    running_totals[p].append(running_totals[p][-1] + score)
                else:
                    round_scores[p].append(0)
                    running_totals[p].append(running_totals[p][-1])
                round_standing[p] = running_totals[p][-1]
            round_standings.append(sorted(round_standing.items(), key=lambda x: x[1], reverse=True))
    
    stats = {
        'running_totals': running_totals,
        'round_scores': round_scores,
        'round_standings': round_standings,
        'analysis': {}
    }
    
    # Calculate interesting statistics for each player
    for p in players:
        scores = round_scores[p]
        totals = running_totals[p]
        
        # Best and worst rounds
        if scores:
            best_round_score = max(scores)
            worst_round_score = min(scores)
            best_round = scores.index(best_round_score) + 1
            worst_round = scores.index(worst_round_score) + 1
        else:
            best_round_score = worst_round_score = best_round = worst_round = 0
        
        # Correct bids count
        correct_bids = sum(1 for s in scores if s > 0)
        
        # Biggest 3-round jump and drop
        max_3round_jump = 0
        max_3round_drop = 0
        jump_rounds = (0, 0)
        drop_rounds = (0, 0)
        
        if len(totals) >= 4:
            for i in range(len(totals) - 3):
                change = totals[i+3] - totals[i]
                if change > max_3round_jump:
                    max_3round_jump = change
                    jump_rounds = (i+1, i+3)
                if change < max_3round_drop:
                    max_3round_drop = change
                    drop_rounds = (i+1, i+3)
        
        # Lead changes - how many times they took/lost the lead
        times_in_lead = 0
        lead_changes_involving = 0
        was_leading = False
        
        for i, standing in enumerate(round_standings):
            currently_leading = standing[0][0] == p if standing else False
            if currently_leading:
                times_in_lead += 1
            if currently_leading != was_leading:
                lead_changes_involving += 1
            was_leading = currently_leading
        
        # Comeback or choke stats
        if len(round_standings) >= 2:
            first_standing = [x[0] for x in round_standings[0]]
            last_standing = [x[0] for x in round_standings[-1]]
            start_rank = first_standing.index(p) + 1 if p in first_standing else len(players)
            end_rank = last_standing.index(p) + 1 if p in last_standing else len(players)
            rank_change = start_rank - end_rank  # Positive = improved
        else:
            start_rank = end_rank = rank_change = 0
        
        # Hot and cold streaks
        current_streak = 0
        max_hot_streak = 0
        max_cold_streak = 0
        for s in scores:
            if s > 0:
                if current_streak >= 0:
                    current_streak += 1
                else:
                    current_streak = 1
                max_hot_streak = max(max_hot_streak, current_streak)
            else:
                if current_streak <= 0:
                    current_streak -= 1
                else:
                    current_streak = -1
                max_cold_streak = max(max_cold_streak, abs(current_streak))
        
        stats['analysis'][p] = {
            'final_score': totals[-1] if totals else 0,
            'best_round': best_round,
            'best_round_score': best_round_score,
            'worst_round': worst_round,
            'worst_round_score': worst_round_score,
            'correct_bids': correct_bids,
            'total_rounds': len(scores),
            'accuracy': round(correct_bids / len(scores) * 100, 1) if scores else 0,
            'max_3round_jump': max_3round_jump,
            'jump_rounds': jump_rounds,
            'max_3round_drop': max_3round_drop,
            'drop_rounds': drop_rounds,
            'times_in_lead': times_in_lead,
            'lead_changes': lead_changes_involving,
            'start_rank': start_rank,
            'end_rank': end_rank,
            'rank_change': rank_change,
            'max_hot_streak': max_hot_streak,
            'max_cold_streak': max_cold_streak,
        }
    
    return stats

def generate_game_summary(stats):
    """Use LLM to generate an engaging end-game summary."""
    if not st.session_state.nvidia_api_key or not st.session_state.api_verified:
        return None
    
    players = st.session_state.players
    analysis = stats['analysis']
    
    # Build comprehensive stats summary for LLM
    player_summaries = []
    for p in players:
        a = analysis[p]
        summary = f"""{p}:
- Final: #{a['end_rank']} with {a['final_score']} pts
- Accuracy: {a['correct_bids']}/{a['total_rounds']} correct ({a['accuracy']}%)
- Best round: R{a['best_round']} (+{a['best_round_score']} pts), Worst: R{a['worst_round']} ({a['worst_round_score']} pts)
- Biggest 3-round jump: +{a['max_3round_jump']} (R{a['jump_rounds'][0]}-R{a['jump_rounds'][1]})
- Biggest 3-round drop: {a['max_3round_drop']} (R{a['drop_rounds'][0]}-R{a['drop_rounds'][1]})
- Times leading: {a['times_in_lead']} rounds, Lead changes: {a['lead_changes']}
- Started #{a['start_rank']}, Finished #{a['end_rank']} (moved {'+' if a['rank_change'] > 0 else ''}{a['rank_change']} spots)
- Hot streak: {a['max_hot_streak']} correct in a row, Cold streak: {a['max_cold_streak']} misses in a row"""
        player_summaries.append(summary)
    
    # Find superlatives
    superlatives = []
    
    # Best accuracy
    best_accuracy = max(players, key=lambda p: analysis[p]['accuracy'])
    superlatives.append(f"Most Accurate: {best_accuracy} ({analysis[best_accuracy]['accuracy']}%)")
    
    # Worst accuracy
    worst_accuracy = min(players, key=lambda p: analysis[p]['accuracy'])
    superlatives.append(f"Least Accurate: {worst_accuracy} ({analysis[worst_accuracy]['accuracy']}%)")
    
    # Biggest comeback
    biggest_comeback = max(players, key=lambda p: analysis[p]['rank_change'])
    if analysis[biggest_comeback]['rank_change'] > 0:
        superlatives.append(f"Biggest Comeback: {biggest_comeback} (climbed {analysis[biggest_comeback]['rank_change']} spots)")
    
    # Biggest choke
    biggest_choke = min(players, key=lambda p: analysis[p]['rank_change'])
    if analysis[biggest_choke]['rank_change'] < 0:
        superlatives.append(f"Biggest Choke: {biggest_choke} (dropped {abs(analysis[biggest_choke]['rank_change'])} spots)")
    
    # Hottest streak
    hottest = max(players, key=lambda p: analysis[p]['max_hot_streak'])
    superlatives.append(f"Hottest Streak: {hottest} ({analysis[hottest]['max_hot_streak']} correct in a row)")
    
    # Coldest streak
    coldest = max(players, key=lambda p: analysis[p]['max_cold_streak'])
    superlatives.append(f"Coldest Streak: {coldest} ({analysis[coldest]['max_cold_streak']} misses in a row)")
    
    # Best 3-round jump
    best_jumper = max(players, key=lambda p: analysis[p]['max_3round_jump'])
    superlatives.append(f"Best 3-Round Run: {best_jumper} (+{analysis[best_jumper]['max_3round_jump']} pts)")
    
    # Worst 3-round drop
    worst_dropper = min(players, key=lambda p: analysis[p]['max_3round_drop'])
    superlatives.append(f"Worst 3-Round Collapse: {worst_dropper} ({analysis[worst_dropper]['max_3round_drop']} pts)")
    
    prompt = f"""You are a sports commentator giving an exciting end-game summary for a Wizard card game tournament.

FINAL STANDINGS AND PLAYER STATS:
{chr(10).join(player_summaries)}

NOTABLE ACHIEVEMENTS:
{chr(10).join(superlatives)}

Write an exciting, dramatic game summary (3-4 paragraphs) that:
1. Celebrates the winner and their journey to victory
2. Highlights the most dramatic moments (comebacks, chokes, close battles)
3. Gives funny "awards" to each player based on their unique stats
4. Ends with a memorable final statement

Be entertaining, use their names, reference specific stats. Make it feel like a sports broadcast recap!"""

    try:
        response = requests.post(
            NVIDIA_API_URL,
            headers={
                "Authorization": f"Bearer {st.session_state.nvidia_api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            json={
                "model": st.session_state.selected_model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 800,
                "temperature": 0.9,
                "stream": False
            },
            timeout=120  # Game summary needs more time for detailed analysis
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            return None
    except Exception as e:
        return None

def verify_nvidia_api(api_key):
    """Verify that the NVIDIA API key is working."""
    try:
        response = requests.post(
            NVIDIA_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            json={
                "model": st.session_state.selected_model,
                "messages": [{"role": "user", "content": "Say 'API working' in exactly 2 words."}],
                "max_tokens": 50,
                "temperature": 0.5,
                "stream": False
            },
            timeout=60  # Reduced timeout for verification
        )
        
        if response.status_code == 200:
            return True, "API key verified successfully!"
        elif response.status_code == 401:
            return False, "Invalid API key. Please check your key."
        elif response.status_code == 403:
            return False, "Access denied. Check your API key permissions."
        elif response.status_code == 404:
            return False, f"Model not found. Check model name: {st.session_state.selected_model}"
        else:
            return False, f"API error: {response.status_code} - {response.text[:200]}"
    except requests.exceptions.Timeout:
        return False, "Request timed out. Please try again."
    except Exception as e:
        return False, f"Connection error: {str(e)[:100]}"

def generate_roasts(round_num):
    """Generate roasts for players based on their full game history using NVIDIA API."""
    if not st.session_state.nvidia_api_key or not st.session_state.enable_roasts or not st.session_state.api_verified:
        return None
    
    # Build comprehensive game history for each player
    player_histories = []
    totals = get_total_scores()
    sorted_by_score = sorted(totals.items(), key=lambda x: x[1], reverse=True)
    
    for player in st.session_state.players:
        # Current standing
        rank = [i+1 for i, (p, s) in enumerate(sorted_by_score) if p == player][0]
        total_score = totals[player]
        
        # Round-by-round history
        round_details = []
        total_correct = 0
        total_over = 0
        total_under = 0
        biggest_fail = 0
        
        for r in range(1, round_num + 1):
            if r in st.session_state.game_data and player in st.session_state.game_data[r]:
                data = st.session_state.game_data[r].get(player, {'bid': None, 'tricks': None})
                bid = data['bid']
                tricks = data['tricks']
                if bid is not None and tricks is not None:
                    diff = tricks - bid
                    score = calculate_score(bid, tricks)
                    round_details.append(f"R{r}: bid {bid}, got {tricks}, {'✓' if diff == 0 else f'off by {abs(diff)}'} ({score:+d} pts)")
                    
                    if diff == 0:
                        total_correct += 1
                    elif diff > 0:
                        total_over += 1
                    else:
                        total_under += 1
                    
                    if abs(diff) > biggest_fail:
                        biggest_fail = abs(diff)
        
        # Build player summary
        history = f"""{player} (Rank #{rank}, {total_score} pts total):
  - Correct bids: {total_correct}/{round_num} rounds
  - Overbid: {total_under}x, Underbid: {total_over}x
  - Biggest miss: {biggest_fail} tricks off
  - Round history: {'; '.join(round_details[-5:])}"""  # Last 5 rounds for context
        
        player_histories.append(history)
    
    # Current round performance
    current_performances = []
    for player in st.session_state.players:
        data = st.session_state.game_data[round_num].get(player, {'bid': None, 'tricks': None})
        bid = data['bid'] or 0
        tricks = data['tricks'] or 0
        diff = tricks - bid
        
        if diff == 0:
            status = f"{player} nailed their bid of {bid} (smug success)"
        elif diff > 0:
            status = f"{player} bid {bid} but got {tricks} (overachiever by {diff})"
        else:
            status = f"{player} bid {bid} but only got {tricks} (failed by {abs(diff)})"
        current_performances.append(status)
    
    # Standings summary
    standings = ", ".join([f"#{i+1} {p} ({s} pts)" for i, (p, s) in enumerate(sorted_by_score)])
    
    prompt = f"""You are a witty, sarcastic commentator for a Wizard card game. Round {round_num} of {st.session_state.max_rounds} just ended.

CURRENT STANDINGS: {standings}

FULL PLAYER HISTORIES:
{chr(10).join(player_histories)}

THIS ROUND'S PERFORMANCES:
{chr(10).join(current_performances)}

Write a brief, savage roast for EACH player individually (1-2 sentences each). Use their FULL GAME HISTORY to make it personal - reference their patterns, streaks, choking moments, or consistent failures. Format as:
PLAYER_NAME: [roast]

Be savage but friendly. Reference specific stats, patterns, or memorable moments from their history. Keep each roast short and punchy."""

    try:
        response = requests.post(
            NVIDIA_API_URL,
            headers={
                "Authorization": f"Bearer {st.session_state.nvidia_api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            json={
                "model": st.session_state.selected_model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 500,
                "temperature": 0.9,
                "stream": False
            },
            timeout=60  # Timeout for roast generation
        )
        
        if response.status_code == 200:
            result = response.json()
            message = result.get("choices", [{}])[0].get("message", {})
            
            # DeepSeek-R1 may return reasoning in 'reasoning_content' and final answer in 'content'
            raw_content = message.get("content") or message.get("reasoning_content") or ""
            
            # If still empty, try to get any text from the response
            if not raw_content and result.get("choices"):
                # Try alternative response structures
                raw_content = str(result.get("choices", [{}])[0])
            
            # Check if we got valid content
            if not raw_content:
                return {p: f"The AI was speechless... (debug: {str(result)[:100]})" for p in st.session_state.players}
            
            # Parse individual roasts from response
            roasts = {}
            for player in st.session_state.players:
                # Look for "PLAYER_NAME:" pattern
                import re
                pattern = rf"{re.escape(player)}[:\s]+(.+?)(?=\n[A-Z]|$)"
                match = re.search(pattern, raw_content, re.IGNORECASE | re.DOTALL)
                if match:
                    roast_text = match.group(1).strip()
                    # Clean up the roast text
                    roast_text = roast_text.strip('"').strip()
                    roasts[player] = roast_text
                else:
                    roasts[player] = "Even the AI couldn't find words for this performance..."
            
            return roasts
        else:
            # Return error for all players with more detail
            try:
                error_detail = response.json().get("error", {}).get("message", response.text[:100])
            except:
                error_detail = response.text[:100]
            return {p: f"[API Error {response.status_code}]: {error_detail}" for p in st.session_state.players}
    except requests.exceptions.Timeout:
        return {p: "[Timeout]: API took too long to respond" for p in st.session_state.players}
    except Exception as e:
        return {p: f"[Error]: {str(e)[:80]}" for p in st.session_state.players}

def save_game(title=None, filename=None):
    """Save the current game state to a text file."""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        players_str = "_".join(st.session_state.players[:3])
        filename = f"wizard_game_{players_str}_{timestamp}.txt"
    
    if title is None:
        title = f"Game: {', '.join(st.session_state.players)}"
    
    game_data_serializable = {
        str(k): v for k, v in st.session_state.game_data.items()
    }
    
    save_data = {
        "title": title,
        "players": st.session_state.players,
        "player_colors": st.session_state.player_colors,
        "starting_dealer_index": st.session_state.starting_dealer_index,
        "current_round": st.session_state.current_round,
        "game_data": game_data_serializable,
        "max_rounds": st.session_state.max_rounds,
        "game_started": st.session_state.game_started,
        "saved_at": datetime.now().isoformat(),
        "total_scores": get_total_scores()
    }
    
    filepath = SAVE_DIR / filename
    with open(filepath, 'w') as f:
        f.write("=== WIZARD CARD GAME SAVE FILE ===\n")
        f.write(f"Title: {title}\n")
        f.write(f"Saved: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Players: {', '.join(st.session_state.players)}\n")
        f.write(f"Round: {st.session_state.current_round} / {st.session_state.max_rounds}\n")
        f.write(f"Scores: {get_total_scores()}\n")
        f.write("=" * 35 + "\n\n")
        f.write("--- JSON DATA (DO NOT EDIT BELOW) ---\n")
        f.write(json.dumps(save_data, indent=2))
    
    st.session_state.current_save_file = filename
    return filename

def load_game(filename):
    """Load a game state from a text file."""
    filepath = SAVE_DIR / filename
    with open(filepath, 'r') as f:
        content = f.read()
    
    json_marker = "--- JSON DATA (DO NOT EDIT BELOW) ---\n"
    json_start = content.find(json_marker) + len(json_marker)
    json_data = content[json_start:]
    
    save_data = json.loads(json_data)
    
    st.session_state.players = save_data["players"]
    st.session_state.player_colors = save_data.get("player_colors", {})
    st.session_state.starting_dealer_index = save_data.get("starting_dealer_index", 0)
    st.session_state.current_round = save_data["current_round"]
    st.session_state.game_data = {
        int(k): v for k, v in save_data["game_data"].items()
    }
    st.session_state.max_rounds = save_data["max_rounds"]
    st.session_state.game_started = save_data["game_started"]
    st.session_state.current_save_file = filename

def get_saved_games():
    """Get list of saved game files."""
    saved_games = []
    for filepath in SAVE_DIR.glob("wizard_game_*.txt"):
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Parse JSON data for title
            json_marker = "--- JSON DATA (DO NOT EDIT BELOW) ---\n"
            json_start = content.find(json_marker) + len(json_marker)
            json_data = content[json_start:]
            save_data = json.loads(json_data)
            title = save_data.get("title", "Untitled Game")
            
            # Parse header lines
            lines = content.split("\n")
            saved_at = lines[2].replace("Saved: ", "").strip() if len(lines) > 2 else "Unknown"
            players = lines[3].replace("Players: ", "").strip() if len(lines) > 3 else "Unknown"
            round_info = lines[4].replace("Round: ", "").strip() if len(lines) > 4 else "Unknown"
            
            saved_games.append({
                "filename": filepath.name,
                "title": title,
                "saved_at": saved_at,
                "players": players,
                "round": round_info
            })
        except Exception:
            pass
    saved_games.sort(key=lambda x: x["saved_at"], reverse=True)
    return saved_games

def update_save_title(filename, new_title):
    """Update the title of a saved game."""
    filepath = SAVE_DIR / filename
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Extract JSON data
    json_marker = "--- JSON DATA (DO NOT EDIT BELOW) ---\n"
    json_start = content.find(json_marker) + len(json_marker)
    json_data = content[json_start:]
    save_data = json.loads(json_data)
    
    # Update title
    save_data["title"] = new_title
    
    # Rewrite file with new title
    with open(filepath, 'w') as f:
        f.write("=== WIZARD CARD GAME SAVE FILE ===\n")
        f.write(f"Title: {new_title}\n")
        f.write(f"Saved: {save_data['saved_at'].replace('T', ' ')[:19]}\n")
        f.write(f"Players: {', '.join(save_data['players'])}\n")
        f.write(f"Round: {save_data['current_round']} / {save_data['max_rounds']}\n")
        f.write(f"Scores: {save_data['total_scores']}\n")
        f.write("=" * 35 + "\n\n")
        f.write("--- JSON DATA (DO NOT EDIT BELOW) ---\n")
        f.write(json.dumps(save_data, indent=2))

def delete_save(filename):
    """Delete a save file."""
    filepath = SAVE_DIR / filename
    if filepath.exists():
        filepath.unlink()

def reset_game():
    """Reset the game to initial state."""
    st.session_state.players = []
    st.session_state.player_colors = {}
    st.session_state.starting_dealer_index = 0
    st.session_state.current_round = 1
    st.session_state.game_data = {}
    st.session_state.game_started = False
    st.session_state.max_rounds = 0
    st.session_state.current_save_file = None
    st.session_state.game_finished = False
    st.session_state.shot_players = []
    st.session_state.round_roasts = {}
    st.session_state.manual_roast = {}
    st.session_state.game_summary = None
    st.session_state.game_stats = None

# Title and header
st.title("🎩 The Grand Fardini")
st.markdown("---")

# Sidebar for game setup
with st.sidebar:
    st.header("⚙️ Game Setup")
    st.caption("Version 0.2")
    
    if not st.session_state.game_started:
        st.subheader("Add Players")
        
        # Use a form so Enter key submits
        with st.form(key="add_player_form", clear_on_submit=True):
            new_player = st.text_input("Player Name")
            submit = st.form_submit_button("Add Player", type="primary")
            if submit and new_player:
                if new_player not in st.session_state.players:
                    st.session_state.players.append(new_player)
                    st.rerun()
                else:
                    st.warning("Player already exists!")
        
        if st.session_state.players:
            st.write("**Current Players:**")
            for i, player in enumerate(st.session_state.players):
                # Assign default color if not set
                if player not in st.session_state.player_colors:
                    st.session_state.player_colors[player] = DEFAULT_COLORS[i % len(DEFAULT_COLORS)]
                
                col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
                col1.write(f"{i+1}. {player}")
                # Color picker
                new_color = col2.color_picker("", st.session_state.player_colors[player], key=f"color_{player}")
                if new_color != st.session_state.player_colors[player]:
                    st.session_state.player_colors[player] = new_color
                # Move up button
                if i > 0:
                    if col3.button("⬆️", key=f"up_{player}"):
                        st.session_state.players[i], st.session_state.players[i-1] = \
                            st.session_state.players[i-1], st.session_state.players[i]
                        st.rerun()
                # Move down button
                if i < len(st.session_state.players) - 1:
                    if col4.button("⬇️", key=f"down_{player}"):
                        st.session_state.players[i], st.session_state.players[i+1] = \
                            st.session_state.players[i+1], st.session_state.players[i]
                        st.rerun()
                # Remove button
                if col5.button("❌", key=f"remove_{player}"):
                    st.session_state.players.remove(player)
                    if player in st.session_state.player_colors:
                        del st.session_state.player_colors[player]
                    st.rerun()
        
        st.markdown("---")
        
        if len(st.session_state.players) >= 3:
            # Calculate max rounds based on number of players
            num_players = len(st.session_state.players)
            calculated_max_rounds = 60 // num_players
            st.info(f"With {num_players} players, max rounds = {calculated_max_rounds}")
            
            # Select starting dealer
            st.markdown("**Select First Dealer:**")
            dealer_options = st.session_state.players
            selected_dealer = st.selectbox(
                "First dealer", 
                dealer_options, 
                index=st.session_state.starting_dealer_index,
                label_visibility="collapsed"
            )
            st.session_state.starting_dealer_index = dealer_options.index(selected_dealer)
            
            if st.button("🎮 Start Game", type="primary"):
                st.session_state.game_started = True
                st.session_state.current_round = 1  # Reset to round 1
                st.session_state.max_rounds = calculated_max_rounds
                st.session_state.game_data = {}  # Clear any old game data
                st.session_state.game_finished = False  # Reset game finished flag
                st.session_state.shot_players = []  # Clear shot players
                st.session_state.round_roasts = {}  # Clear roasts
                # Initialize game data for round 1
                st.session_state.game_data[1] = {
                    player: {'bid': None, 'tricks': None} 
                    for player in st.session_state.players
                }
                st.rerun()
        else:
            st.warning("Need at least 3 players to start!")
    
    else:
        st.success(f"Game in progress!")
        st.write(f"**Players:** {len(st.session_state.players)}")
        st.write(f"**Current Round:** {st.session_state.current_round} / {st.session_state.max_rounds}")
        
        st.markdown("---")
        st.subheader("💾 Save Game")
        
        # Get current title from existing save or use default
        default_title = f"Game: {', '.join(st.session_state.players)}"
        if st.session_state.current_save_file:
            # Try to get existing title from save file
            try:
                saved_games = get_saved_games()
                for game in saved_games:
                    if game['filename'] == st.session_state.current_save_file:
                        default_title = game.get('title', default_title)
                        break
            except:
                pass
        
        save_title = st.text_input("Game Title", value=default_title, key="save_title_input")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save", type="primary"):
                # Use existing filename if available, otherwise create new
                filename = st.session_state.current_save_file if st.session_state.current_save_file else None
                save_game(title=save_title, filename=filename)
                st.success(f"Game saved!")
        
        with col2:
            if st.button("📄 Save as New"):
                # Always create a new file
                save_game(title=save_title, filename=None)
                st.success(f"Saved as new file!")
        
        if st.session_state.current_save_file:
            st.caption(f"Current file: {st.session_state.current_save_file}")
        
        st.markdown("---")
        if st.button("🔄 New Game", type="secondary"):
            reset_game()
            st.rerun()
        
        # Roast settings
        st.markdown("---")
        st.subheader("🔥 AI Roasts")
        st.session_state.enable_roasts = st.toggle("Enable roasts", value=st.session_state.enable_roasts)
        if st.session_state.enable_roasts:
            api_key = st.text_input(
                "NVIDIA API Key", 
                value=st.session_state.nvidia_api_key, 
                type="password",
                help="Get your API key from build.nvidia.com"
            )
            
            # Only update and reset verification if key changed
            if api_key != st.session_state.nvidia_api_key:
                st.session_state.nvidia_api_key = api_key
                st.session_state.api_verified = False
                save_api_key(api_key)  # Persist API key
            
            if api_key:
                col1, col2 = st.columns([2, 1])
                with col1:
                    if st.button("🔌 Verify API Key"):
                        with st.spinner("Verifying..."):
                            success, message = verify_nvidia_api(api_key)
                            if success:
                                st.session_state.api_verified = True
                                st.success(message)
                            else:
                                st.session_state.api_verified = False
                                st.error(message)
                with col2:
                    if st.session_state.api_verified:
                        st.markdown("✅ Verified")
                    else:
                        st.markdown("❌ Not verified")
                
                # Model selector
                model_names = list(NVIDIA_MODELS.keys())
                current_model_name = [k for k, v in NVIDIA_MODELS.items() if v == st.session_state.selected_model]
                current_index = model_names.index(current_model_name[0]) if current_model_name else 1
                
                selected_name = st.selectbox(
                    "AI Model",
                    model_names,
                    index=current_index,
                    help="Llama models are faster, DeepSeek-R1 is more creative but slower"
                )
                if NVIDIA_MODELS[selected_name] != st.session_state.selected_model:
                    st.session_state.selected_model = NVIDIA_MODELS[selected_name]
                    st.session_state.api_verified = False  # Re-verify with new model
                    st.rerun()
            else:
                st.caption("⚠️ Enter your NVIDIA API key")
                st.caption("Get one at: build.nvidia.com")
    
    # Load game section (always visible in sidebar)
    st.markdown("---")
    st.subheader("📂 Load Game")
    saved_games = get_saved_games()
    if saved_games:
        for game in saved_games[:5]:  # Show last 5 saves
            with st.expander(f"📁 {game.get('title', 'Untitled')[:25]}"):
                st.write(f"**Title:** {game.get('title', 'Untitled')}")
                st.write(f"**Saved:** {game['saved_at']}")
                st.write(f"**Players:** {game['players']}")
                st.write(f"**Round:** {game['round']}")
                
                # Edit title
                new_title = st.text_input("Edit Title", value=game.get('title', ''), key=f"edit_title_{game['filename']}")
                if new_title != game.get('title', ''):
                    if st.button("💾 Save Title", key=f"save_title_{game['filename']}"):
                        update_save_title(game['filename'], new_title)
                        st.rerun()
                
                col1, col2 = st.columns(2)
                if col1.button("Load", key=f"load_{game['filename']}"):
                    load_game(game['filename'])
                    st.rerun()
                if col2.button("🗑️", key=f"del_{game['filename']}"):
                    delete_save(game['filename'])
                    st.rerun()
    else:
        st.caption("No saved games found.")

# Main game area
if not st.session_state.game_started:
    st.info("👈 Add players and start the game using the sidebar!")
    
    # Show game rules
    with st.expander("📜 Wizard Game Rules & Scoring"):
        st.markdown("""
        ### Scoring System
        - **Correct Bid:** 20 points + 10 points per trick won
        - **Incorrect Bid:** -10 points per trick over or under
        
        ### Example Scores
        | Bid | Tricks | Score |
        |-----|--------|-------|
        | 0   | 0      | +20   |
        | 3   | 3      | +50   |
        | 2   | 4      | -20   |
        | 3   | 1      | -20   |
        
        ### Cards per Round
        - Round 1: 1 card each
        - Round 2: 2 cards each
        - ... and so on
        
        ### Number of Rounds
        - 60 cards ÷ number of players = max rounds
        """)

else:
    # Current round input
    st.header(f"📍 Round {st.session_state.current_round}")
    
    # Calculate current dealer (rotates each round)
    num_players = len(st.session_state.players)
    current_dealer_index = (st.session_state.starting_dealer_index + st.session_state.current_round - 1) % num_players
    current_dealer = st.session_state.players[current_dealer_index]
    dealer_color = st.session_state.player_colors.get(current_dealer, "#808080")
    
    st.markdown(f"*Each player has {st.session_state.current_round} card(s)* &nbsp;&nbsp;|&nbsp;&nbsp; "
                f"🃏 **Dealer:** <span style='color:{dealer_color}; font-weight:bold;'>{current_dealer}</span>", 
                unsafe_allow_html=True)
    
    # Prominent Roast Display and Button
    if st.session_state.enable_roasts and st.session_state.api_verified:
        roast_col1, roast_col2 = st.columns([3, 1])
        with roast_col2:
            if st.button("🔥 ROAST! 🔥", type="primary", use_container_width=True):
                with st.spinner("Generating roasts..."):
                    roasts = generate_roasts(st.session_state.current_round)
                    if roasts:
                        st.session_state.manual_roast = roasts
                    else:
                        st.session_state.manual_roast = {p: "The AI is speechless..." for p in st.session_state.players}
                st.rerun()
        
        # Always show the roast box if there are roasts to display
        if st.session_state.manual_roast:
            st.markdown(
                """
                <div style='background: linear-gradient(135deg, #8B0000 0%, #FF4500 50%, #FFD700 100%); 
                            padding: 20px; border-radius: 20px; 
                            border: 4px solid #FFD700; 
                            margin: 15px 0; 
                            box-shadow: 0 0 30px #FF4500, 0 0 60px #8B000040;'>
                    <h2 style='color: #FFFFFF; text-align: center; margin: 0 0 15px 0; text-shadow: 2px 2px 4px #000;'>
                        🔥🎤 THE ROASTS 🎤🔥
                    </h2>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Display individual roasts in columns
            roast_cols = st.columns(len(st.session_state.players))
            for i, player in enumerate(st.session_state.players):
                player_color = st.session_state.player_colors.get(player, "#FF6B6B")
                roast_text = st.session_state.manual_roast.get(player, "No roast available")
                with roast_cols[i]:
                    st.markdown(
                        f"""
                        <div style='background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%); 
                                    padding: 15px; border-radius: 15px; 
                                    border: 3px solid {player_color}; 
                                    margin: 5px 0; 
                                    box-shadow: 0 0 15px {player_color}40;
                                    min-height: 150px;'>
                            <h3 style='color: {player_color}; text-align: center; margin: 0 0 10px 0;'>
                                🔥 {player} 🔥
                            </h3>
                            <p style='color: #FFFFFF; text-align: center; font-size: 1.1em; font-style: italic; 
                                      margin: 0; line-height: 1.4;'>
                                "{roast_text}"
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            
            # Button to clear the roast
            if st.button("❌ Clear Roasts", type="secondary"):
                st.session_state.manual_roast = {}
                st.rerun()
    
    # Always show current standings at top
    st.markdown("---")
    totals = get_total_scores()
    sorted_players = sorted(totals.items(), key=lambda x: x[1], reverse=True)
    
    cols = st.columns(len(sorted_players))
    medals = ["🥇", "🥈", "🥉"] + [""] * 10
    
    for i, (player, score) in enumerate(sorted_players):
        player_color = st.session_state.player_colors.get(player, "#808080")
        with cols[i]:
            st.markdown(f"<div style='text-align:center; padding:5px; border-radius:5px; border: 2px solid {player_color};'>"
                       f"<b>{medals[i]} {player}</b><br><span style='font-size:1.2em;'>{score} pts</span></div>", 
                       unsafe_allow_html=True)
    st.markdown("---")
    
    # Tab selection using radio buttons
    tab_options = ["🎯 Bids", "🃏 Tricks Won", "📊 Scoreboard"]
    
    # Check for pending tab change (set before rerun)
    if "pending_tab" in st.session_state:
        st.session_state.active_tab = st.session_state.pending_tab
        del st.session_state.pending_tab
    
    # Use a unique key based on current active_tab to force widget recreation
    selected = st.radio(
        "Navigate", 
        tab_options, 
        index=st.session_state.active_tab, 
        horizontal=True, 
        label_visibility="collapsed"
    )
    
    # Update active_tab based on selection
    new_tab = tab_options.index(selected)
    if new_tab != st.session_state.active_tab:
        st.session_state.active_tab = new_tab
        st.rerun()
    
    if st.session_state.active_tab == 0:  # Bids tab
        st.subheader("Enter Bids")
        current_round = st.session_state.current_round
        
        # Ensure current round exists in game data
        if current_round not in st.session_state.game_data:
            st.session_state.game_data[current_round] = {
                player: {'bid': None, 'tricks': None} 
                for player in st.session_state.players
            }
        
        cols = st.columns(len(st.session_state.players))
        for i, player in enumerate(st.session_state.players):
            with cols[i]:
                current_bid = st.session_state.game_data[current_round][player]['bid']
                bid = st.number_input(
                    f"**{player}**",
                    min_value=0,
                    max_value=current_round,
                    value=current_bid if current_bid is not None else 0,
                    step=1,
                    key=f"bid_{player}_{current_round}"
                )
                st.session_state.game_data[current_round][player]['bid'] = bid
        
        # Show total bids
        total_bids = sum(
            st.session_state.game_data[current_round][p]['bid'] or 0 
            for p in st.session_state.players
        )
        
        # Calculate what the dealer can't say
        cant_say = current_round - total_bids
        num_players = len(st.session_state.players)
        current_dealer_index = (st.session_state.starting_dealer_index + current_round - 1) % num_players
        current_dealer = st.session_state.players[current_dealer_index]
        dealer_color = st.session_state.player_colors.get(current_dealer, "#808080")
        
        if total_bids == current_round:
            st.warning(f"⚠️ Total bids ({total_bids}) = tricks available ({current_round}). Someone must be wrong!")
        else:
            st.info(f"Total bids: {total_bids} / {current_round} tricks available")
        
        # Show dealer restriction
        if 0 <= cant_say <= current_round:
            st.markdown(f"🚫 <b><span style='color:{dealer_color};'>{current_dealer}</span> (dealer) can't say {cant_say}</b>", 
                       unsafe_allow_html=True)
        
        # Button to go to Tricks tab
        st.markdown("---")
        if st.button("Go to Tricks 🃏 ➡️", type="primary"):
            st.session_state.pending_tab = 1
            st.rerun()
    
    elif st.session_state.active_tab == 1:  # Tricks tab
        st.subheader("Enter Tricks Won")
        current_round = st.session_state.current_round
        
        cols = st.columns(len(st.session_state.players))
        for i, player in enumerate(st.session_state.players):
            with cols[i]:
                # Show player's bid next to their name
                player_bid = st.session_state.game_data[current_round][player]['bid'] or 0
                player_color = st.session_state.player_colors.get(player, "#808080")
                st.markdown(f"**{player}** <span style='color:{player_color}; font-size:0.9em;'>(Bid: {player_bid})</span>", 
                           unsafe_allow_html=True)
                
                current_tricks = st.session_state.game_data[current_round][player]['tricks']
                tricks = st.number_input(
                    f"Tricks for {player}",
                    min_value=0,
                    max_value=current_round,
                    label_visibility="collapsed",
                    value=current_tricks if current_tricks is not None else 0,
                    step=1,
                    key=f"tricks_{player}_{current_round}"
                )
                st.session_state.game_data[current_round][player]['tricks'] = tricks
        
        # Show total tricks
        total_tricks = sum(
            st.session_state.game_data[current_round][p]['tricks'] or 0 
            for p in st.session_state.players
        )
        if total_tricks != current_round:
            st.error(f"❌ Total tricks ({total_tricks}) ≠ tricks available ({current_round})")
        else:
            st.success(f"✅ Total tricks: {total_tricks} / {current_round}")
        
        st.markdown("---")
        
        # Round navigation
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.session_state.current_round > 1:
                if st.button("⬅️ Previous Round"):
                    st.session_state.current_round -= 1
                    st.rerun()
        
        with col3:
            if st.session_state.current_round < st.session_state.max_rounds:
                if st.button("Next Round ➡️", type="primary"):
                    # Check for players who need to take a shot (off by 2+ tricks)
                    shot_players = []
                    current_round = st.session_state.current_round
                    for player in st.session_state.players:
                        bid = st.session_state.game_data[current_round][player]['bid'] or 0
                        tricks = st.session_state.game_data[current_round][player]['tricks'] or 0
                        if abs(bid - tricks) >= 2:
                            shot_players.append(player)
                    
                    st.session_state.shot_players = shot_players
                    
                    # Generate roast for this round before moving on
                    if st.session_state.enable_roasts and st.session_state.nvidia_api_key and st.session_state.api_verified:
                        with st.spinner("🔥 Generating roasts... (this may take up to 90 seconds)"):
                            roast = generate_roasts(current_round)
                            st.session_state.round_roasts[current_round] = roast if roast else "[No roast generated - API may have failed]"
                    elif st.session_state.enable_roasts and not st.session_state.api_verified:
                        st.session_state.round_roasts[current_round] = "[API not verified - please verify your API key]"
                    
                    st.session_state.current_round += 1
                    st.session_state.pending_tab = 0  # Switch to Bids tab on rerun
                    # Initialize next round if needed
                    if st.session_state.current_round not in st.session_state.game_data:
                        st.session_state.game_data[st.session_state.current_round] = {
                            player: {'bid': None, 'tricks': None} 
                            for player in st.session_state.players
                        }
                    
                    # Auto-save game after each round
                    if st.session_state.current_save_file:
                        save_game(filename=st.session_state.current_save_file)
                    else:
                        save_game()
                    
                    st.rerun()
            else:
                # Final round - add Finish Game button
                all_tricks_entered = all(
                    st.session_state.game_data[st.session_state.current_round][p]['tricks'] is not None
                    for p in st.session_state.players
                )
                all_bids_entered = all(
                    st.session_state.game_data[st.session_state.current_round][p]['bid'] is not None
                    for p in st.session_state.players
                )
                
                if all_tricks_entered and all_bids_entered and not st.session_state.get('game_finished', False):
                    if st.button("🏆 Finish Game", type="primary"):
                        # Check for players who need to take a shot (off by 2+ tricks)
                        shot_players = []
                        current_round = st.session_state.current_round
                        for player in st.session_state.players:
                            bid = st.session_state.game_data[current_round][player]['bid'] or 0
                            tricks = st.session_state.game_data[current_round][player]['tricks'] or 0
                            if abs(bid - tricks) >= 2:
                                shot_players.append(player)
                        
                        st.session_state.shot_players = shot_players
                        
                        # Generate roast for final round
                        if st.session_state.enable_roasts and st.session_state.nvidia_api_key and st.session_state.api_verified:
                            with st.spinner("🔥 Generating final roasts... (this may take up to 90 seconds)"):
                                roast = generate_roasts(current_round)
                                st.session_state.round_roasts[current_round] = roast if roast else "[No roast generated - API may have failed]"
                        elif st.session_state.enable_roasts and not st.session_state.api_verified:
                            st.session_state.round_roasts[current_round] = "[API not verified - please verify your API key]"
                        
                        st.session_state.game_finished = True
                        st.session_state.show_celebration = True  # Trigger confetti
                        st.session_state.pending_tab = 2  # Switch to Scoreboard on rerun
                        st.rerun()
                elif st.session_state.get('game_finished', False):
                    st.success("🏆 Game Complete! View results in Scoreboard tab.")
                else:
                    st.info("Final Round! Enter all bids and tricks, then click Finish Game.")
    
    # Show shot popup if there are players who need to take a shot
    if st.session_state.shot_players:
        # Show roast first if available
        prev_round = st.session_state.current_round - 1
        if prev_round in st.session_state.round_roasts:
            roast_text = st.session_state.round_roasts[prev_round]
            st.markdown(
                f"""<div style='background: linear-gradient(135deg, #2d1b69 0%, #11998e 100%); 
                             padding: 20px; border-radius: 15px; border: 2px solid #f39c12; 
                             margin: 10px 0; box-shadow: 0 0 15px #f39c12;'>
                    <h3 style='color: #f39c12; text-align: center; margin-bottom: 10px;'>🔥 Round {prev_round} Roast 🔥</h3>
                    <p style='color: #FFFFFF; text-align: center; font-size: 1.1em; font-style: italic;'>"{roast_text}"</p>
                    </div>""",
                unsafe_allow_html=True
            )
        
        shot_html = ""
        for player in st.session_state.shot_players:
            player_color = st.session_state.player_colors.get(player, "#FF0000")
            shot_html += f"<h2 style='color:{player_color}; text-align:center;'>🍺 {player.upper()} NEEDS TO TAKE A SHOT! 🍺</h2>"
        
        st.markdown(
            f"""<div style='background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); 
                         padding: 30px; border-radius: 15px; border: 3px solid #e94560; 
                         margin: 20px 0; box-shadow: 0 0 20px #e94560;'>
                {shot_html}
                </div>""",
            unsafe_allow_html=True
        )
        
        if st.button("✅ Acknowledged - Shots Taken!", type="primary"):
            st.session_state.shot_players = []
            # Clear the roast for previous round
            prev_round = st.session_state.current_round - 1
            if prev_round in st.session_state.round_roasts:
                del st.session_state.round_roasts[prev_round]
            st.rerun()
    
    # Show roast popup even if no shot players (when there's a pending roast)
    elif not st.session_state.shot_players:
        prev_round = st.session_state.current_round - 1
        if prev_round in st.session_state.round_roasts:
            roast_text = st.session_state.round_roasts[prev_round]
            st.markdown(
                f"""<div style='background: linear-gradient(135deg, #2d1b69 0%, #11998e 100%); 
                             padding: 20px; border-radius: 15px; border: 2px solid #f39c12; 
                             margin: 10px 0; box-shadow: 0 0 15px #f39c12;'>
                    <h3 style='color: #f39c12; text-align: center; margin-bottom: 10px;'>🔥 Round {prev_round} Roast 🔥</h3>
                    <p style='color: #FFFFFF; text-align: center; font-size: 1.1em; font-style: italic;'>"{roast_text}"</p>
                    </div>""",
                unsafe_allow_html=True
            )
            if st.button("😂 Nice one! Continue", type="primary"):
                del st.session_state.round_roasts[prev_round]
                st.rerun()

    if st.session_state.active_tab == 2:  # Scoreboard tab
        st.subheader("📊 Full Scoreboard")
        
        # Build scoreboard dataframe
        scoreboard_data = []
        running_totals = {player: 0 for player in st.session_state.players}
        
        # Only show completed rounds (not current round unless game is finished)
        game_finished = st.session_state.get('game_finished', False)
        max_round_to_show = st.session_state.current_round if game_finished else st.session_state.current_round - 1
        
        for round_num in range(1, max_round_to_show + 1):
            if round_num in st.session_state.game_data:
                row = {'Round': round_num}
                for player in st.session_state.players:
                    data = st.session_state.game_data[round_num].get(player, {'bid': None, 'tricks': None})
                    bid = data['bid']
                    tricks = data['tricks']
                    
                    if bid is not None and tricks is not None:
                        score = calculate_score(bid, tricks)
                        running_totals[player] += score
                        hit = "✓" if bid == tricks else "✗"
                        row[f"{player} Bid"] = bid
                        row[f"{player} Tricks"] = tricks
                        row[f"{player} Score"] = f"{score:+d} {hit}"
                        row[f"{player} Total"] = running_totals[player]
                    else:
                        row[f"{player} Bid"] = "-"
                        row[f"{player} Tricks"] = "-"
                        row[f"{player} Score"] = "-"
                        row[f"{player} Total"] = running_totals[player]
                
                scoreboard_data.append(row)
        
        if scoreboard_data:
            df = pd.DataFrame(scoreboard_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Score progression chart
        st.markdown("---")
        st.subheader("📈 Score Progression")
        
        # Build chart data - cumulative scores per round
        chart_data = {"Round": [0]}  # Start at round 0 with 0 points
        for player in st.session_state.players:
            chart_data[player] = [0]
        
        running_totals_chart = {player: 0 for player in st.session_state.players}
        for round_num in range(1, max_round_to_show + 1):
            if round_num in st.session_state.game_data:
                # Check if this round is complete (all players have bid and tricks)
                round_complete = all(
                    st.session_state.game_data[round_num].get(player, {}).get('bid') is not None and
                    st.session_state.game_data[round_num].get(player, {}).get('tricks') is not None
                    for player in st.session_state.players
                )
                
                if not round_complete:
                    continue  # Skip incomplete rounds
                
                chart_data["Round"].append(round_num)
                for player in st.session_state.players:
                    data = st.session_state.game_data[round_num].get(player, {'bid': None, 'tricks': None})
                    bid = data['bid']
                    tricks = data['tricks']
                    if bid is not None and tricks is not None:
                        running_totals_chart[player] += calculate_score(bid, tricks)
                    chart_data[player].append(running_totals_chart[player])
        
        if len(chart_data["Round"]) > 1:
            chart_df = pd.DataFrame(chart_data)
            # Melt the dataframe for Altair
            chart_melted = chart_df.melt(id_vars=["Round"], var_name="Player", value_name="Score")
            
            # Get colors for each player
            color_scale = alt.Scale(
                domain=st.session_state.players,
                range=[st.session_state.player_colors.get(p, DEFAULT_COLORS[i % len(DEFAULT_COLORS)]) 
                       for i, p in enumerate(st.session_state.players)]
            )
            
            # Create Altair chart with custom colors
            chart = alt.Chart(chart_melted).mark_line(point=True, strokeWidth=3).encode(
                x=alt.X("Round:Q", title="Round", axis=alt.Axis(tickMinStep=1)),
                y=alt.Y("Score:Q", title="Total Score"),
                color=alt.Color("Player:N", scale=color_scale, legend=alt.Legend(title="Players")),
                tooltip=["Round", "Player", "Score"]
            ).properties(
                height=400
            ).interactive()
            
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("Complete at least one round to see the score progression chart.")
        
        # Final results - only show when game is properly finished
        if st.session_state.get('game_finished', False):
            # Show celebration effects only once (when flag is set)
            if st.session_state.get('show_celebration', False):
                st.balloons()
                st.snow()
            
            # Analyze game stats if not already done
            if st.session_state.game_stats is None:
                st.session_state.game_stats = analyze_game_stats()
                # Only set celebration to False after stats are analyzed (first load)
                st.session_state.show_celebration = False
            
            stats = st.session_state.game_stats
            analysis = stats['analysis']
            
            # Build results HTML
            winner = sorted_players[0][0]
            winner_color = st.session_state.player_colors.get(winner, "#FFD700")
            
            results_html = ""
            medals = ["🥇", "🥈", "🥉"] + [""] * 10
            for i, (player, score) in enumerate(sorted_players):
                player_color = st.session_state.player_colors.get(player, "#FFFFFF")
                if i == 0:
                    results_html += f"<h1 style='color:{player_color}; text-align:center; margin:10px 0;'>{medals[i]} {player} - {score} pts 👑</h1>"
                else:
                    results_html += f"<h3 style='color:{player_color}; text-align:center; margin:5px 0;'>{medals[i]} {player} - {score} pts</h3>"
            
            # Celebration popup
            st.markdown(
                f"""
                <div style='background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); 
                            padding: 40px; border-radius: 20px; 
                            border: 4px solid {winner_color}; 
                            margin: 30px 0; 
                            box-shadow: 0 0 30px {winner_color}, 0 0 60px {winner_color}40;
                            text-align: center;'>
                    <h1 style='color: #FFD700; font-size: 3em; margin-bottom: 20px;'>
                        🎉🏆 GAME OVER! 🏆🎉
                    </h1>
                    <h2 style='color: #FFFFFF; margin-bottom: 30px;'>
                        🧙 The Wizard Tournament Has Concluded! 🧙
                    </h2>
                    <div style='background: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px; margin: 20px 0;'>
                        {results_html}
                    </div>
                    <p style='color: #98D8C8; font-size: 1.2em; margin-top: 20px;'>
                        🎊 Congratulations to all players! 🎊
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Game Statistics Section
            st.markdown("---")
            st.subheader("📊 Game Statistics & Awards")
            
            # Player stat cards
            stat_cols = st.columns(len(st.session_state.players))
            for i, (player, score) in enumerate(sorted_players):
                player_color = st.session_state.player_colors.get(player, "#808080")
                a = analysis[player]
                with stat_cols[i]:
                    st.markdown(
                        f"""
                        <div style='background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%); 
                                    padding: 15px; border-radius: 15px; 
                                    border: 3px solid {player_color}; 
                                    margin: 5px 0;'>
                            <h3 style='color: {player_color}; text-align: center; margin: 0 0 10px 0;'>
                                {medals[i]} {player}
                            </h3>
                            <p style='color: #FFFFFF; text-align: center; font-size: 1.5em; margin: 5px 0;'>
                                {score} pts
                            </p>
                            <hr style='border-color: {player_color}40;'>
                            <p style='color: #98D8C8; font-size: 0.9em; margin: 5px 0;'>
                                🎯 Accuracy: <b>{a['accuracy']}%</b> ({a['correct_bids']}/{a['total_rounds']})
                            </p>
                            <p style='color: #98D8C8; font-size: 0.9em; margin: 5px 0;'>
                                🔥 Best Round: R{a['best_round']} (+{a['best_round_score']})
                            </p>
                            <p style='color: #98D8C8; font-size: 0.9em; margin: 5px 0;'>
                                💀 Worst Round: R{a['worst_round']} ({a['worst_round_score']})
                            </p>
                            <p style='color: #98D8C8; font-size: 0.9em; margin: 5px 0;'>
                                📈 Best 3-Round: +{a['max_3round_jump']}
                            </p>
                            <p style='color: #98D8C8; font-size: 0.9em; margin: 5px 0;'>
                                📉 Worst 3-Round: {a['max_3round_drop']}
                            </p>
                            <p style='color: #98D8C8; font-size: 0.9em; margin: 5px 0;'>
                                🏆 Led {a['times_in_lead']} rounds
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            
            # Superlative Awards
            st.markdown("---")
            st.subheader("🏅 Game Awards")
            
            award_cols = st.columns(4)
            
            # Calculate awards
            best_accuracy = max(st.session_state.players, key=lambda p: analysis[p]['accuracy'])
            worst_accuracy = min(st.session_state.players, key=lambda p: analysis[p]['accuracy'])
            biggest_comeback = max(st.session_state.players, key=lambda p: analysis[p]['rank_change'])
            biggest_choke = min(st.session_state.players, key=lambda p: analysis[p]['rank_change'])
            hottest_streak = max(st.session_state.players, key=lambda p: analysis[p]['max_hot_streak'])
            coldest_streak = max(st.session_state.players, key=lambda p: analysis[p]['max_cold_streak'])
            best_jumper = max(st.session_state.players, key=lambda p: analysis[p]['max_3round_jump'])
            worst_dropper = min(st.session_state.players, key=lambda p: analysis[p]['max_3round_drop'])
            
            awards = [
                ("🎯 Sharpshooter", best_accuracy, f"{analysis[best_accuracy]['accuracy']}% accuracy"),
                ("🙈 Blind Bidder", worst_accuracy, f"{analysis[worst_accuracy]['accuracy']}% accuracy"),
                ("🚀 Rocket", best_jumper, f"+{analysis[best_jumper]['max_3round_jump']} pts in 3 rounds"),
                ("📉 Freefall", worst_dropper, f"{analysis[worst_dropper]['max_3round_drop']} pts in 3 rounds"),
                ("🔥 On Fire", hottest_streak, f"{analysis[hottest_streak]['max_hot_streak']} correct in a row"),
                ("❄️ Ice Cold", coldest_streak, f"{analysis[coldest_streak]['max_cold_streak']} misses in a row"),
                ("🦸 Comeback King", biggest_comeback, f"Climbed {analysis[biggest_comeback]['rank_change']} spots") if analysis[biggest_comeback]['rank_change'] > 0 else None,
                ("😱 Choke Artist", biggest_choke, f"Dropped {abs(analysis[biggest_choke]['rank_change'])} spots") if analysis[biggest_choke]['rank_change'] < 0 else None,
            ]
            
            # Filter out None awards and display
            awards = [a for a in awards if a is not None]
            for i, (title, player, stat) in enumerate(awards):
                player_color = st.session_state.player_colors.get(player, "#FFD700")
                with award_cols[i % 4]:
                    st.markdown(
                        f"""
                        <div style='background: linear-gradient(135deg, #2d1b69 0%, #11998e 100%); 
                                    padding: 15px; border-radius: 10px; 
                                    border: 2px solid {player_color}; 
                                    margin: 5px 0; text-align: center;'>
                            <h4 style='color: #FFD700; margin: 0;'>{title}</h4>
                            <p style='color: {player_color}; font-size: 1.2em; margin: 5px 0; font-weight: bold;'>{player}</p>
                            <p style='color: #FFFFFF; font-size: 0.9em; margin: 0;'>{stat}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            
            # LLM Game Summary
            if st.session_state.enable_roasts and st.session_state.api_verified:
                st.markdown("---")
                st.subheader("🎙️ The Commentator's Recap")
                
                if st.session_state.game_summary is None:
                    if st.button("🎤 Generate Game Summary", type="primary", use_container_width=True):
                        with st.spinner("The commentator is reviewing the footage..."):
                            summary = generate_game_summary(stats)
                            if summary:
                                st.session_state.game_summary = summary
                            else:
                                st.session_state.game_summary = "The commentator lost their notes... but what a game that was!"
                        st.rerun()
                else:
                    st.info("🎙️ **The Commentator Says:**")
                    st.write(st.session_state.game_summary)
                    if st.button("🔄 Regenerate Summary"):
                        st.session_state.game_summary = None
                        st.rerun()

# Footer
st.markdown("---")
st.markdown("*Made with ❤️ for Wizard card game enthusiasts*")
