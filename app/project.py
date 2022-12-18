class Project(object):
    def __init__(
        self,
        offre: float = 638,
        agence: float = 18,
        notaire_tx: float = 7.5,
        apport: float = 240,
    ):
        self.offre = offre * 1000
        self.agence = agence * 1000
        self.notaire_tx = notaire_tx * 0.01
        self.apport = apport * 1000

    @property
    def notaire(self):
        return self.price * self.notaire_tx

    @property
    def price(self):
        return self.offre - self.agence

    @property
    def emprunt(self):
        return self.price + self.notaire + self.agence - self.apport


class Simulation(object):
    def __init__(
        self,
        p: Project,
        taux: float = 0.045,
        assurance: float = 24448,
        duree: int = 22,
        chargesloc_mensuel: float = 200 + 141,
        frais_dossier: float = 2445,
        garantielogement: float = 4896,
    ):
        self.montant_emprunt = p.emprunt
        self.taux_annuel = taux
        self.mensualite_assurance = assurance
        self.chargesloc = chargesloc_mensuel
        self.fraisfixesdepart = p.notaire + p.agence + frais_dossier + garantielogement
        self.duree = duree
        self.mensualite = int(
            (p.emprunt * taux / 12.0) / (1 - (1 + (taux / 12)) ** (-12 * duree))
        )

        self.reset()

    def reset(self):
        self.nb_mois = 0
        self.montant_rembourse = 0
        self.reste_a_rembourser = self.montant_emprunt
        self.total_interets = 0  # le coût total que l'on a dépensé en intérêts
        self.total_assurance = 0
        self.taux_mens = self.taux_annuel / 12.0
        self.charges = 0
        self.states = None

    def step(self):
        interets = self.taux_mens * self.reste_a_rembourser
        augmentation_capital = self.mensualite - interets
        self.montant_rembourse += augmentation_capital
        self.reste_a_rembourser -= augmentation_capital
        self.total_interets += interets
        self.total_assurance += self.mensualite_assurance
        self.charges += self.chargesloc
        self.nb_mois += 1
        if self.states is None:
            self.states = dict(
                augmentation_capital=[],
                interets=[],
                montant_rembourse=[],
                reste_a_rembourser=[],
                total_interets=[],
                total_assurance=[],
                charges=[],
                perdu=[],
                revente_penalty=[],
                mois=[],
                annee=[],
            )

        self.states["augmentation_capital"].append(augmentation_capital)
        self.states["interets"].append(int(interets))
        self.states["montant_rembourse"].append(int(self.montant_rembourse))
        self.states["reste_a_rembourser"].append(int(self.reste_a_rembourser))
        self.states["total_interets"].append(int(self.total_interets))
        self.states["total_assurance"].append(int(self.total_assurance))
        self.states["charges"].append(int(self.charges))
        self.states["perdu"].append(self.total_perdu)
        self.states["mois"].append(self.nb_mois)
        self.states["annee"].append(self.nb_mois // 12)
        penalty = min(0.03 * self.reste_a_rembourser, 6 * interets)
        self.states["revente_penalty"].append(penalty)

    def run(self):
        self.reset()
        for i in range(self.duree * 12):
            self.step()
        return self.states

    @property
    def total_perdu(self):
        return (
            self.fraisfixesdepart
            + self.total_interets
            + self.charges
            + self.total_assurance
        )
