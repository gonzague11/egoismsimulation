import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# Simulation : monde continu + vaches (chaque vache = 10, 2 hommes requis, 5 chacun)
# ============================================================
np.random.seed(3)

# Paramètres
L = 1.0
r_homme = 0.02
r_carotte = 0.01
r_vache = 0.03
carottes_par_jour = 1000
nb_vaches = 15
sigma_step = 0.02
n_steps_par_jour = 500
jours = 100
remplacement_delay = 40  # pas avant qu'une nouvelle vache apparaisse

# Fonctions
def positions_aleatoires(n, L):
    return np.random.rand(n, 2) * L

def rebondir_bords(pos, L):
    return np.clip(pos, 0, L)

def distance_matrix(a, b):
    diff = a[:, None, :] - b[None, :, :]
    return np.linalg.norm(diff, axis=2)

# Initialisation
pos_hommes = positions_aleatoires(1, L)
nb_hommes_par_jour = [len(pos_hommes)]

# Initialisation vaches
pos_vaches = positions_aleatoires(nb_vaches, L)
vaches_vivantes = np.ones(nb_vaches, dtype=bool)
remplacement_compteur = np.zeros(nb_vaches, dtype=int)  # compteur de pas avant nouvelle vache

# Boucle principale
for jour in range(jours):
    pos_carottes = positions_aleatoires(carottes_par_jour, L)
    carottes_restantes = np.ones(carottes_par_jour, dtype=bool)
    carottes_ramassees = np.zeros(len(pos_hommes), dtype=int)

    for step in range(n_steps_par_jour):
        if len(pos_hommes) == 0:
            break

        pos_hommes += np.random.normal(0, sigma_step, pos_hommes.shape)
        pos_hommes = rebondir_bords(pos_hommes, L)

        # Interaction carottes
        if carottes_restantes.any():
            carottes_indices = np.where(carottes_restantes)[0]
            dist = distance_matrix(pos_hommes, pos_carottes[carottes_restantes])
            proche = dist < (r_homme + r_carotte)
            if np.any(proche):
                indices_hommes, indices_carottes_locales = np.where(proche)
                for h, c_local in zip(indices_hommes, indices_carottes_locales):
                    c_global = carottes_indices[c_local]
                    if carottes_restantes[c_global]:
                        carottes_ramassees[h] += 1
                        carottes_restantes[c_global] = False

        # Interaction vaches (à partir du jour 20)
        if jour >= 20 and np.any(vaches_vivantes) and len(pos_hommes) > 0:
            vaches_indices = np.where(vaches_vivantes)[0]
            dist_v = distance_matrix(pos_hommes, pos_vaches[vaches_vivantes])
            proche_v = dist_v < (r_homme + r_vache)

            for idx_local, v_global in enumerate(vaches_indices):
                hommes_proches = np.where(proche_v[:, idx_local])[0]
                if hommes_proches.size >= 2:
                    dists_pour_vache = dist_v[hommes_proches, idx_local]
                    tri = np.argsort(dists_pour_vache)
                    deux = hommes_proches[tri[:2]]
                    for h in deux:
                        carottes_ramassees[h] += 5
                    # Vache consommée
                    vaches_vivantes[v_global] = False
                    remplacement_compteur[v_global] = remplacement_delay

        # Remplacement des vaches mortes après le délai
        for i in range(nb_vaches):
            if not vaches_vivantes[i] and remplacement_compteur[i] > 0:
                remplacement_compteur[i] -= 1
                if remplacement_compteur[i] == 0:
                    pos_vaches[i] = positions_aleatoires(1, L)
                    vaches_vivantes[i] = True

    # Sélection
    if len(pos_hommes) == 0:
        nb_hommes_par_jour.append(0)
        continue

    survivants = carottes_ramassees >= 5
    pos_hommes = pos_hommes[survivants]

    # Reproduction
    nb_survivants = len(pos_hommes)
    if nb_survivants > 0:
        enfants = []
        for i, nb in enumerate(carottes_ramassees[survivants]):
            nb_enfants = int((nb - 5) // 5)
            if nb_enfants > 0:
                enfants.append(pos_hommes[i] + np.random.normal(0, 0.02, (nb_enfants, 2)))
        if enfants:
            enfants = np.vstack(enfants)
            enfants = np.clip(enfants, 0, L)
            pos_hommes = np.vstack((pos_hommes, enfants))

    nb_hommes_par_jour.append(len(pos_hommes))

# Affichage
plt.figure(figsize=(7,4))
plt.plot(nb_hommes_par_jour, lw=2)
plt.axvline(20, color='orange', linestyle='--', label='Jour 20 : vaches')
plt.xlabel("Jour")
plt.ylabel("Nombre d'hommes")
plt.title("Population avec vaches (remplacement différé)")
plt.legend()
plt.grid(True)
plt.show()

print("Population finale :", nb_hommes_par_jour[-1])
