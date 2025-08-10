import streamlit as st
from streamlit_nej_datepicker import datepicker_component, Config
from collections import Counter
import csv, io

st.set_page_config(page_title="JAKUBATOR", page_icon="📅", layout="wide")
st.title("📅 JAKUBATOR — wybierz daty na Jakubalia")
st.write("Dodaj osoby w pasku bocznym, każda osoba wybiera dowolną liczbę dat w kalendarzu. Potem kliknij **Znajdź wspólne daty**.")

# inicjalizacja session_state
if "participants" not in st.session_state:
    st.session_state.participants = {}  # {name: [date,...]}
    st.session_state.next_id = 1

# --- sidebar: dodawanie osób
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

# --- główna część: listujemy osoby i pokazujemy kalendarz dla każdej
for idx, name in enumerate(list(st.session_state.participants.keys())):
    with st.expander(name, expanded=True):
        current = st.session_state.participants.get(name, [])
        cfg = Config(
            selection_mode="multiple",
            default_value=current if current else None,
            placeholder=f"Wybierz daty dla {name}",
            minimum_today=True
        )
        picked = datepicker_component(config=cfg)
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
if st.button("🔎 Znajdź wspólne daty"):
    lists = [set(v) for v in st.session_state.participants.values() if v]
    if not lists:
        st.warning("Brak dat do porównania — dodaj osoby i wybierz daty.")
    else:
        common = set.intersection(*lists) if lists else set()
        if common:
            common_sorted = sorted(common)
            st.success("Daty pasujące wszystkim:")
            st.write(", ".join(d.isoformat() for d in common_sorted))
            # CSV do pobrania
            buf = io.StringIO()
            w = csv.writer(buf)
            w.writerow(["date", "count"])
            for d in common_sorted:
                w.writerow([d.isoformat(), sum(1 for s in lists if d in s)])
            st.download_button("Pobierz wspólne daty (CSV)", data=buf.getvalue(),
                               file_name="jakubator_common_dates.csv", mime="text/csv")
        else:
            st.error("Brak dat pasujących wszystkim. Proponowane kompromisy (najpopularniejsze daty):")
            all_dates = [d for v in st.session_state.participants.values() for d in v]
            counts = Counter(all_dates)
            most = counts.most_common(10)
            if not most:
                st.info("Nikt nie wybrał żadnej daty.")
            else:
                for d, cnt in most:
                    st.write(f"{d.isoformat()} — {cnt} osób")
                # CSV z propozycjami
                buf = io.StringIO()
                w = csv.writer(buf)
                w.writerow(["date", "count"])
                for d, cnt in most:
                    w.write
