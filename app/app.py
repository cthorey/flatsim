import streamlit as st
from project import Project, Simulation
import pandas as pd

st.title("Flatsim (Guerin et al. 2022)")
project, simulation, revente = st.tabs(["project", "simulation", "revente"])

with project:
    col0, col1 = st.columns(2)
    with col0:
        offre = st.slider("Offre (M)", min_value=100, max_value=800, step=1, value=638)
        agence = st.slider(
            "Frais agence (M)", min_value=1, max_value=30, step=1, value=18
        )
        notaire_tx = st.slider(
            "Notaire tx (%)", min_value=1.0, max_value=10.0, value=7.5
        )
        apport = st.slider("Apport (M)", min_value=0, max_value=500, step=1, value=240)
        pjx = Project(offre=offre, agence=agence, notaire_tx=notaire_tx, apport=apport)

    with col1:
        df = pd.DataFrame(
            [["Price", pjx.price], ["Emprunt", pjx.emprunt], ["Notaire", pjx.notaire]],
            columns=["name", "price"],
        )
        st.bar_chart(df, x="name", y="price")

with simulation:
    col2, col3, col4 = st.columns(3)
    with col2:
        taux = st.number_input(
            "Taux annuel (%)", min_value=0.5, max_value=5.0, step=0.01, value=2.35
        )
        duree = st.number_input("Durée (annee)", min_value=0, max_value=25, value=22)
    with col4:
        frais_dossier = st.number_input("Frais dossier", value=2445)
        charges = st.number_input("Charges mensuel", value=341)
    with col3:
        assurance = st.number_input("Assurance mensuel", value=90)
        garanti = st.number_input("Garantie logement", value=4896)

    sim = Simulation(
        pjx,
        taux=taux / 100.0,
        assurance=assurance,
        frais_dossier=frais_dossier,
        duree=duree,
        chargesloc_mensuel=charges,
        garantielogement=garanti,
    )
    st.markdown(
        f"**Mensualité**: {sim.mensualite}, **Frais fixe**: {int(sim.fraisfixesdepart)}"
    )
    data = sim.run()
    data = pd.DataFrame(data)
    _keys = [
        "montant_rembourse",
        "reste_a_rembourser",
        "total_interets",
        "total_assurance",
        "charges",
    ]
    keys = st.multiselect(
        "Pick some data to plot",
        _keys,
        _keys,
    )
    st.bar_chart(data[_keys], use_container_width=True)

with revente:
    rc0, rc1 = st.columns(2)
    with rc0:
        market = st.number_input(
            "Evolution prix (%)", min_value=-30.0, max_value=30.0, step=1.0, value=0.0
        )
        revente = pjx.price * (1 + 0.01 * market)
        penalty_to_pay = st.radio("Paying penalty", ["Yes", "No"])
        penalty_to_pay = penalty_to_pay == "Yes"
    with rc1:
        tloyer = st.number_input(
            "Loyer aujourd'hui", min_value=500, max_value=2500, step=10, value=1650
        )
        tcharge = st.number_input(
            "Charge aujourd'hui", min_value=50, max_value=300, step=1, value=250
        )
    data["bilan"] = (
        revente
        - data.reste_a_rembourser
        - pjx.apport
        - data.revente_penalty * penalty_to_pay
    )
    break_even_annee = data.loc[data.bilan > 0, "annee"].min()
    break_even_month = data.loc[data.bilan > 0, "mois"].min()
    st.markdown(f"Revente à: **{int(revente)}**")
    st.markdown(
        f"**Break even**: Annee: **{break_even_annee}**, Month: **{break_even_month%12}**"
    )
    data["Achat"] = [int(r) for r in data["bilan"]]
    data["Location"] = [tloyer + tcharge for _ in range(len(data))]
    data["Location"] = -data["Location"].cumsum() + pjx.apport
    show_loc = st.radio("Show Location alternative", ["No", "Yes"], horizontal=True)
    keys = ["Achat", "Location"]
    if show_loc == "No":
        keys = ["Achat"]
    st.bar_chart(data[keys], use_container_width=True)
