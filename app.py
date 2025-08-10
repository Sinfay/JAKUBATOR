import streamlit as st
from streamlit_nej_datepicker import datepicker_component, Config
from datetime import datetime, timedelta

st.set_page_config(page_title="JAKUBATOR", page_icon="📅", layout="wide")
st.title("📅 JAKUBATOR — wybierz daty na Jakubalia")
st.write("Dodaj osoby po lewej, każda wybiera daty. Kliknij **Znajdź wspólne daty**, aby poznać zakresy dostępne dla wszystkich.")

if "participants" not in st.session_state:
    st.session_state.participants = {}
    st.session_state.next_id = 1

# --- Sidebar
with st.sidebar:
    st.header("Dodaj osobę")
    new_name = st.text_input("Imię / nick (opcjonalnie)")
    if st.button("Dodaj osobę"):
        name = new_name.strip() or f"Osoba {st.session_state.next_id}"
        if name in st.session_state.participants:
            st.warning("Taka osoba już istnieje.")
        else:
            st.session_state.participants[name] = []
            st.session_state.next_id += 1
            st.success(f"Dodano: {name}")
    st.markdown("---")
    if st.button("Usuń wszystkie osoby"):
        st.session_state.participants = {}
        st.session_state.next_id = 1
        st.experimental_rerun()

# --- Główna część
for idx, name in enumerate(list(st.session_state.participants.keys())):
    with st.expander(name, expanded=True):
        current = st.session_state.participants.get(name, [])
        default_val = [d.isoformat() for d in current] if current else None

        cfg = Config(
            selection_mode="multiple",
            default_value=default_val
        )

        picked = datepicker_component(config=cfg, key=f"calendar_{name}")

        if picked:
            st.write("Wybrane daty:", ", ".join(d.isoformat() for d in picked))
        else:
            st.write("Wybrane daty: brak")

        c1, c2, c3 = st.columns(3)
        if c1.button("Zapisz daty", key=f"save_{idx}"):
            st.session_state.participants[name] = picked or []
            st.success("Zapisano.")
        if c2.button("Wyczyść daty", key=f"clear_{idx}"):
            st.session_state.participants[name] = []
            st.success("Wyczyszczono.")
        if c3.button("Usuń osobę", key=f"del_{idx}"):
            del st.session_state.participants[name]
            st.experimental_rerun()

st.markdown("---")

def merge_dates_to_ranges(dates):
    """Przyjmuje posortowaną listę dat datetime.date i zwraca listę (start, end) przedziałów."""
    if not dates:
        return []
    ranges = []
    start = prev = dates[0]
    for current in dates[1:]:
        if (current - prev).days == 1:
            prev = current
        else:
            ranges.append((start, prev))
            start = prev = current
    ranges.append((start, prev))
    return ranges

if st.button("🔎 Znajdź wspólne daty"):
    if not st.session_state.participants:
        st.warning("Dodaj przynajmniej jedną osobę.")
    else:
        # Sprawdź, czy każdy ma zaznaczone daty
        if any(not dates for dates in st.session_state.participants.values()):
            st.warning("Każda osoba musi wybrać przynajmniej jedną datę.")
        else:
            # Przecięcie zbiorów dat
            sets = [set(st.session_state.participants[name]) for name in st.session_state.participants]
            common_dates = set.intersection(*sets) if sets else set()

            if not common_dates:
                st.error("Brak wspólnych dat — spróbuj wybrać inne terminy.")
            else:
                # Sortujemy wspólne daty
                common_sorted = sorted(common_dates)
                # Zamieniamy na przedziały
                ranges = merge_dates_to_ranges(common_sorted)
                st.success("Daty wspólne wszystkim uczestnikom (zakresy):")
                for start, end in ranges:
                    if start == end:
                        st.write(f"- {start.isoformat()}")
                    else:
                        st.write(f"- {start.isoformat()} – {end.isoformat()}")
