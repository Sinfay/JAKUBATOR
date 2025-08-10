import streamlit as st
from streamlit_nej_datepicker import datepicker_component, Config
from datetime import datetime, timedelta

def parse_dates(dates_str_list):
    # konwersja listy stringów 'YYYY-MM-DD' na listę datetime.date
    return [datetime.strptime(d, "%Y-%m-%d").date() for d in dates_str_list]

def intersect_date_ranges(lists_of_dates):
    if not lists_of_dates:
        return []
    # dla uproszczenia: bierzemy minimalną i maksymalną datę każdego użytkownika jako zakres,
    # następnie znajdujemy zakres wspólny (przecięcie) wszystkich zakresów
    
    min_dates = [min(dates) for dates in lists_of_dates if dates]
    max_dates = [max(dates) for dates in lists_of_dates if dates]

    if not min_dates or not max_dates:
        return []

    start = max(min_dates)
    end = min(max_dates)
    if start > end:
        return []  # brak wspólnych dat

    # zwracamy wszystkie dni z zakresu od start do end
    delta = (end - start).days
    return [start + timedelta(days=i) for i in range(delta + 1)]

# Inicjalizacja stanu sesji
if 'participants' not in st.session_state:
    st.session_state.participants = {}

st.title("Jakubator - Wybór dat na Jakubalia")

# Dodawanie nowego użytkownika
with st.form("add_user_form"):
    new_user = st.text_input("Dodaj nazwę użytkownika:")
    submitted = st.form_submit_button("Dodaj użytkownika")
    if submitted and new_user:
        if new_user in st.session_state.participants:
            st.warning(f"Użytkownik {new_user} już istnieje.")
        else:
            st.session_state.participants[new_user] = []
            st.success(f"Dodano użytkownika {new_user}.")

# Edycja dat dla każdego użytkownika
for name in list(st.session_state.participants.keys()):
    with st.expander(f"Daty dla: {name}", expanded=True):
        current_dates = st.session_state.participants.get(name, [])
        # konwersja datetime.date do stringów, jeśli są daty
        default_val = [d.strftime("%Y-%m-%d") for d in current_dates] if current_dates else []

        cfg = Config(
            selection_mode="multiple",
            default_value=default_val,
            placeholder=f"Wybierz daty dla {name}"
        )
        # klucz musi być unikalny
        picked_str = datepicker_component(config=cfg, key=f"calendar_{name}")

        if picked_str is not None:
            picked_dates = parse_dates(picked_str)
            st.session_state.participants[name] = picked_dates

# Wyświetlenie wspólnego zakresu dat (przecięcia)
all_dates_lists = list(st.session_state.participants.values())
common_dates = intersect_date_ranges(all_dates_lists)

st.markdown("---")
st.header("Wspólne dostępne daty dla wszystkich użytkowników:")

if common_dates:
    # wypisz zakres dat
    st.write(f"Od {common_dates[0].strftime('%Y-%m-%d')} do {common_dates[-1].strftime('%Y-%m-%d')}")
else:
    st.write("Brak wspólnych dostępnych dat.")
