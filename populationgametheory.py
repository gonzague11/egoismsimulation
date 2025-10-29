import numpy as np
import matplotlib.pyplot as plt
import collections

np.random.seed(1234598)

# ============================================================
# Paramètres
# ============================================================
L = 1.0
r_homme = 0.02
r_carotte = 0.01
r_vache = 0.03
carottes_par_jour = 1000
nb_vaches = 15
sigma_step = 0.02
n_steps_par_jour = 500
jours = 1000
remplacement_delay = 40  # pas avant qu'une nouvelle vache apparaisse
ego_max = 9
nb_hommes_init = 441
nb_par_profil = nb_hommes_init // ego_max

# ============================================================
# Fonctions utiles
# ============================================================
def positions_aleatoires(n, L):
    return np.random.rand(n, 2) * L

def rebondir_bords(pos, L):
    return np.clip(pos, 0, L)

def distance_matrix(a, b):
    diff = a[:, None, :] - b[None, :, :]
    return np.linalg.norm(diff, axis=2)

def repartition_vache(obj1, obj2):
    """
    Répartit les 10 parts d'une vache entre deux hommes selon leurs objectifs.
    obj1, obj2 : objectifs de chaque homme (1 à 9)
    """
    total = obj1 + obj2

    # Cas total = 10 : chacun prend exactement son objectif
    if total == 10:
        return obj1, obj2

    # Cas total < 10 : chacun prend son objectif + répartition du reste
    elif total < 10:
        reste = 10 - total
        if reste % 2 == 0:
            return obj1 + reste//2, obj2 + reste//2
        else:
            # si reste impair, le plus égoïste prend la part supplémentaire
            if obj1 > obj2:
                return obj1 + reste//2 + 1, obj2 + reste//2
            elif obj2 > obj1:
                return obj1 + reste//2, obj2 + reste//2 + 1
            else:
                # profils égaux, partage équilibré
                return obj1 + reste//2, obj2 + reste//2

    # Cas total > 10 : chacun perd le surplus qu'il a demandé en trop + 1 part de pénalité
    else:
        surplus = total - 10
        a = max(obj1 - surplus - 1, 0)
        b = max(obj2 - surplus - 1, 0)
        return a, b

def reproduction_ego(parent_ego):
    r = np.random.rand()
    if r < 0.8:
        return parent_ego
    elif r < 0.9:
        return min(parent_ego + 1, ego_max)
    else:
        return max(parent_ego - 1, 1)

# ============================================================
# Initialisation
# ============================================================
pos_hommes = positions_aleatoires(nb_hommes_init, L)

# Profils : 27 de chaque
ego_hommes = np.array([])
for i in range(1, ego_max + 1):
    ego_hommes = np.concatenate((ego_hommes, np.array([i]*nb_par_profil)))
np.random.shuffle(ego_hommes)

nb_hommes_par_jour = [len(pos_hommes)]
profil_journalier = []

# Vaches
pos_vaches = positions_aleatoires(nb_vaches, L)
vaches_vivantes = np.ones(nb_vaches, dtype=bool)
remplacement_compteur = np.zeros(nb_vaches, dtype=int)

# ============================================================
# Boucle principale
# ============================================================
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

        # Interaction vaches
        if np.any(vaches_vivantes) and len(pos_hommes) > 0:
            vaches_indices = np.where(vaches_vivantes)[0]
            dist_v = distance_matrix(pos_hommes, pos_vaches[vaches_vivantes])
            proche_v = dist_v < (r_homme + r_vache)

            for idx_local, v_global in enumerate(vaches_indices):
                hommes_proches = np.where(proche_v[:, idx_local])[0]
                if hommes_proches.size >= 2:
                    dists_pour_vache = dist_v[hommes_proches, idx_local]
                    tri = np.argsort(dists_pour_vache)
                    h1, h2 = hommes_proches[tri[:2]]

                    parts1, parts2 = repartition_vache(ego_hommes[h1], ego_hommes[h2])
                    carottes_ramassees[h1] += parts1
                    carottes_ramassees[h2] += parts2

                    vaches_vivantes[v_global] = False
                    remplacement_compteur[v_global] = remplacement_delay

        # Remplacement différé
        for i in range(nb_vaches):
            if not vaches_vivantes[i] and remplacement_compteur[i] > 0:
                remplacement_compteur[i] -= 1
                if remplacement_compteur[i] == 0:
                    pos_vaches[i] = positions_aleatoires(1, L)
                    vaches_vivantes[i] = True

    # Sélection
    if len(pos_hommes) == 0:
        nb_hommes_par_jour.append(0)
        profil_journalier.append(np.zeros(ego_max))
        continue

    survivants = carottes_ramassees >= 5
    pos_hommes = pos_hommes[survivants]
    ego_hommes = ego_hommes[survivants]

    # Reproduction
    enfants = []
    enfants_ego = []
    for i, nb in enumerate(carottes_ramassees[survivants]):
        nb_enfants = int((nb - 5) // 5)
        for _ in range(nb_enfants):
            enfant_pos = pos_hommes[i] + np.random.normal(0, 0.02, (1,2))
            enfant_pos = np.clip(enfant_pos, 0, L)
            enfants.append(enfant_pos)
            enfants_ego.append(reproduction_ego(ego_hommes[i]))
    if enfants:
        enfants = np.vstack(enfants)
        pos_hommes = np.vstack((pos_hommes, enfants))
        ego_hommes = np.concatenate((ego_hommes, enfants_ego))

    nb_hommes_par_jour.append(len(pos_hommes))

    # Proportion des profils
    compte = collections.Counter(ego_hommes)
    proportion = np.array([compte.get(i,0)/len(pos_hommes) for i in range(1, ego_max+1)])
    profil_journalier.append(proportion)

# ============================================================
# Affichage population totale
# ============================================================
plt.figure(figsize=(8,4))
plt.plot(nb_hommes_par_jour, lw=2)
plt.xlabel("Jour")
plt.ylabel("Nombre d'hommes")
plt.title("Population totale")
plt.grid(True)
plt.show()

# ============================================================
# Affichage proportions profils
# ============================================================
profil_journalier = np.array(profil_journalier)
plt.figure(figsize=(10,5))
for i in range(ego_max):
    plt.plot(profil_journalier[:,i], label=f'Profil {i+1}')
plt.xlabel("Jour")
plt.ylabel("Proportion de la population")
plt.title("Proportion de chaque profil d'égoïsme")
plt.legend()
plt.grid(True)
plt.show()
# ============================================================
# Affichage des proportions finales
# ============================================================
derniere_proportion = profil_journalier[-1]
for i, p in enumerate(derniere_proportion, start=1):
    print(f"Profil {i} : {p*100:.2f}%")