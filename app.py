import streamlit as st
from datetime import datetime, timedelta
from streamlit_nej_datepicker import datepicker_component, Config

# Funkcja do bezpiecznego parsowania dat z różnych formatów
def parse_dates(dates_input):
    if dates_input is None:
        return []
    if isinstance(dates_input, str):
        return [datetime.strptime(dates_input, "%Y-%m-%d").date()]
    if isinstance(dates_input, list):
        return [datetime.strptime(d, "%Y-%m-%d").date() for d in dates_input]
    return []

# Funkcja do znalezienia wspólnego zakresu dat dla wszystkich użytkowników
def find_common_date_range(date_lists):
    if not date_lists:
        return None, None

    # Znajdujemy przecięcie zakresów
    max_start = max(dates[0] for dates in date_lists if dates)
    min_end = min(dates[-1] for dates in date_lists if dates)

    if max_start <= min_end:
        return max_start, min_end
    else:
        return None, None

st.title("Jakubator - wybierz najlepsze daty na Jakubalia")

# Przechowujemy dane użytkowników w stanie sesji
if "users" not in st.session_state:
    st.session_state.users = {}

# Dodawanie nowego użytkownika
with st.form("add_user_form"):
    new_user = st.text_input("Nazwa użytkownika")
    submitted = st.form_submit_button("Dodaj użytkownika")
    if submitted:
        if new_user.strip() == "":
            st.error("Podaj nazwę użytkownika")
        elif new_user in st.session_state.users:
            st.error("Taki użytkownik już istnieje")
        else:
            st.session_state.users[new_user] = []
            st.success(f"Dodano użytkownika {new_user}")

st.write("---")

# Wybór użytkownika do dodania dat
user_to_edit = st.selectbox("Wybierz użytkownika do zaznaczenia dat", options=list(st.session_state.users.keys()))

if user_to_edit:
    current_dates = st.session_state.users[user_to_edit]

    # Przygotowanie domyślnej wartości dla kalendarza w formacie stringów
    default_val = [d.strftime("%Y-%m-%d") for d in current_dates] if current_dates else None

    # Konfiguracja datepicker (unikalny klucz na użytkownika, by uniknąć błędów duplikacji)
    cfg = Config(
        selection_mode="multiple",
        default_value=default_val,
        placeholder=f"Wybierz daty dla {user_to_edit}"
    )

    picked_str = datepicker_component(key=f"datepicker_{user_to_edit}", config=cfg)
    picked_dates = parse_dates(picked_str)

    if picked_dates:
        st.session_state.users[user_to_edit] = sorted(picked_dates)
        st.write(f"Wybrane daty dla {user_to_edit}: ", st.session_state.users[user_to_edit])
    else:
        st.write(f"Brak zaznaczonych dat dla {user_to_edit}")

st.write("---")

# Pokazujemy wynik - wspólne daty wszystkich użytkowników
all_date_ranges = []
for dates in st.session_state.users.values():
    if dates:
        all_date_ranges.append(dates)

if all_date_ranges:
    start, end = find_common_date_range(all_date_ranges)
    if start and end:
        st.success(f"Wspólny zakres dat dla wszystkich użytkowników: od {start.strftime('%Y-%m-%d')} do {end.strftime('%Y-%m-%d')}")
    else:
        st.error("Brak wspólnego zakresu dat dla wszystkich użytkowników.")
else:
    st.info("Dodaj daty dla użytkowników, aby zobaczyć wspólny zakres.")

