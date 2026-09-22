"""Veil's Streamlit interface.

The statistical engine stays in ``veil/`` so this page can later be replaced
by another presentation without changing the draw itself.
"""
from datetime import date
import secrets

import streamlit as st

from veil.__main__ import create_story


st.set_page_config(page_title="Veil", page_icon="◌", layout="centered", initial_sidebar_state="collapsed")

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600&family=Inter:wght@400;500;600&display=swap');

:root { --ink: #0b0d16; --paper: #e9e1ce; --muted: #9f9bab; --ember: #d6a86a; --line: rgba(233,225,206,.16); }
.stApp { background: radial-gradient(circle at 50% 8%, #202039 0%, var(--ink) 42%, #06070c 100%); color: var(--paper); }
.block-container { max-width: 760px; padding: 4.5rem 1.4rem 4rem; }
h1, h2, h3 { font-family: 'Cormorant Garamond', Georgia, serif !important; font-weight: 500 !important; letter-spacing: .035em; }
p, label, button, input, small, .stCaption { font-family: 'Inter', sans-serif !important; }
.veil-mark { color: var(--paper); font-family: 'Cormorant Garamond', Georgia, serif; font-size: 1rem; letter-spacing: .52em; text-align: center; margin: 0 0 1.8rem .52em; }
.veil-intro { color: var(--muted); font-family: 'Cormorant Garamond', Georgia, serif; font-size: 1.35rem; line-height: 1.35; text-align: center; margin: 0 auto 2.5rem; max-width: 34rem; }
.draw-card { border: 1px solid var(--line); border-radius: 2px; padding: 1.4rem 1.5rem; background: rgba(17,18,31,.62); box-shadow: 0 20px 70px rgba(0,0,0,.18); }
.eyebrow { color: var(--ember); font: 600 .67rem/1.4 'Inter', sans-serif; letter-spacing: .18em; text-transform: uppercase; margin-bottom: .35rem; }
.reveal-title { color: var(--paper); font: 500 2.4rem/1.05 'Cormorant Garamond', Georgia, serif; margin: 0 0 .7rem; }
.reveal-copy { color: var(--muted); font: .82rem/1.6 'Inter', sans-serif; }
.fact { border-top: 1px solid var(--line); padding: .8rem 0 .35rem; }
.fact-label { color: var(--muted); font: 600 .64rem/1.4 'Inter', sans-serif; letter-spacing: .14em; text-transform: uppercase; }
.fact-value { color: var(--paper); font: 1.3rem/1.2 'Cormorant Garamond', Georgia, serif; margin-top: .16rem; }
.fact-note { color: var(--muted); font: .72rem/1.5 'Inter', sans-serif; margin-top: .18rem; }
div[data-testid="stForm"] { border: 1px solid var(--line); background: rgba(17,18,31,.6); padding: 1.2rem 1.2rem .75rem; }
div[data-testid="stForm"] label { color: var(--muted) !important; }
.stButton > button, div[data-testid="stFormSubmitButton"] button { background: var(--ember); border: 0; border-radius: 1px; color: #181018; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; }
.stButton > button:hover, div[data-testid="stFormSubmitButton"] button:hover { background: #edc181; color: #181018; }
.source-note { color: var(--muted); font: .68rem/1.55 'Inter', sans-serif; }
section[data-testid="stSidebar"] { background: #0b0d16; }
</style>
""",
    unsafe_allow_html=True,
)


def fact(label, value, note=""):
    note_html = f'<div class="fact-note">{note}</div>' if note else ''
    st.markdown(f'<div class="fact"><div class="fact-label">{label}</div><div class="fact-value">{value}</div>{note_html}</div>', unsafe_allow_html=True)


def render_result(story):
    country = story['country']
    place = story['settlement']
    early = story['early_life']
    culture = story['culture']
    outcomes = story['outcomes']
    st.markdown('<div class="draw-card">', unsafe_allow_html=True)
    st.markdown('<div class="eyebrow">Your beginning</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="reveal-title">{country["name"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="reveal-copy">{country["births"]:,} estimated births in {story["birth_year"]} · {country["probability"]:.2%} of the draw</div>', unsafe_allow_html=True)
    fact('Place', place['name'], place.get('detail') or '')
    fact('Circumstances', story['socioeconomic']['name'])
    fact('Birth-year life expectancy', f'{early["life_expectancy_at_birth"]:.1f} years' if early['life_expectancy_at_birth'] is not None else 'Unavailable', f'{early["year"]}')
    if early['infant_death_probability'] is not None:
        fact('Before age one', f'{early["infant_death_probability"]:.1%} risk', f'Before age five: {early["under_five_death_probability"]:.1%}')
    outcome_labels = {
        'died_in_infancy': 'This life ends before its first birthday.',
        'died_in_early_childhood': 'This life ends between its first and fifth birthdays.',
        'survived_to_five': 'You survive to your fifth birthday.',
        'unavailable': 'Childhood outcome unavailable.',
    }
    fact('Early life', outcome_labels[early['outcome']])
    st.markdown('<div class="eyebrow" style="margin-top:1.1rem">The life around this birthplace</div>', unsafe_allow_html=True)
    for key, label in [('language', 'Language'), ('religion', 'Religion'), ('food', 'Food'), ('music', 'Music')]:
        value = culture.get(key)
        if value:
            fact(label, value['text'])
    if place['kind'] in ('rural', 'urban') and culture.get('terrain'):
        fact('Landscape', culture['terrain'])
    if early['outcome'] not in ('died_in_infancy', 'died_in_early_childhood'):
        st.markdown('<div class="eyebrow" style="margin-top:1.1rem">The world today</div>', unsafe_allow_html=True)
        if outcomes.get('income'):
            income = outcomes['income']
            fact('Income context', f'{income["value"]:,.0f} international dollars / person / year', str(income['year']))
        if outcomes.get('life_expectancy'):
            life = outcomes['life_expectancy']
            fact('Today’s newborn life expectancy', f'{life["value"]:.1f} years', str(life['year']))
        death = outcomes.get('leading_death_cause') or outcomes.get('leading_death_category')
        if death:
            fact('Leading cause context', death['label'], str(death['year']))
        fact('Age this year', str(story['age_this_year']), str(story['as_of_year']))
    st.markdown('</div>', unsafe_allow_html=True)
    with st.expander('Sources'):
        st.markdown(f'<div class="source-note">Births: {country["url"]}<br>Settlement: {place["source"]}<br>Culture and food sources are included in the structured result.<br>Repeat seed: {story["seed"]}</div>', unsafe_allow_html=True)


st.markdown('<div class="veil-mark">V E I L</div>', unsafe_allow_html=True)
st.markdown('<div class="veil-intro">Behind Rawls’s veil of ignorance, you do not know where you will begin. Veil draws one beginning from the world’s births.</div>', unsafe_allow_html=True)

with st.form('birth_form'):
    birth_year = st.number_input('Year of birth', min_value=1950, max_value=2023, value=1985, step=1)
    seed = st.text_input('Seed', placeholder='Leave empty for a new life')
    submitted = st.form_submit_button('Draw a beginning', use_container_width=True)

if submitted:
    chosen_seed = seed.strip() or secrets.token_hex(6)
    st.session_state['veil_story'] = create_story(int(birth_year), chosen_seed, date.today().year)

if 'veil_story' in st.session_state:
    render_result(st.session_state['veil_story'])
else:
    st.markdown('<p style="color:#9f9bab;text-align:center;font:.76rem Inter,sans-serif;margin-top:2rem">Enter a year. Step through the veil.</p>', unsafe_allow_html=True)
