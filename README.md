# Station météo e-ink

Affichage météo + agenda pour un écran **Inky Impression 7.3" (6 couleurs, `inky.inky_e673`)** branché sur un Raspberry Pi.
Résolution 800 × 480, rafraîchissement d'environ 30 secondes.

Contenu de l'écran :

- **En-tête** : date, lever/coucher du soleil, phase de lune, saint du jour, météo actuelle (température et ressenti)
- **Prochaines heures** : 18 heures (2 lignes de 9) avec icône, température et probabilité de pluie
- **4 jours** : icône, barre de températures colorée, min/max, pluie et vent (km/h)
- **Agenda** : événements Google Calendar groupés par jour (optionnel)

![aperçu](preview.png)

> L'aperçu s'obtient avec `python3 weather_display.py --preview` (voir plus bas).

---

## 1. Prérequis

| Élément | Détail |
|---|---|
| Matériel | Raspberry Pi + Inky Impression 7.3" (e673), SPI activé |
| Python | 3.9 ou plus |
| Police | DejaVu (`sudo apt install fonts-dejavu-core`) |
| Locale | `fr_FR.UTF-8` pour les jours et mois en français |
| API météo | Clé OpenWeather avec accès **One Call API 3.0** (abonnement gratuit jusqu'à un quota, mais il faut l'activer sur le compte) |
| Icônes | PNG 128 px nommés `01d.png`, `01n.png`, …, `50n.png` (codes OpenWeather) |

### Activer le SPI et la locale

```bash
sudo raspi-config nonint do_spi 0        # active le SPI
sudo dpkg-reconfigure locales            # cocher fr_FR.UTF-8
```

## 2. Installation

```bash
cd ~
git clone <ton-depot> weather-display     # ou dézipper l'archive ici
cd weather-display

python3 -m venv venv --system-site-packages
. venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
nano .env                                  # renseigner la clé API et la position
chmod +x run.sh
```

### Arborescence attendue

```
weather-display/
├── weather_display.py      # point d'entrée
├── config.py  palette.py  icons.py  data.py  canvas.py  sections.py
├── run.sh  .env  .env.example  requirements.txt
├── saints.json             # optionnel (saint du jour)
├── token.json              # optionnel (Google Calendar)
└── modernicon/weather_icons_dovora_interactive/PNG/128/*.png
```

## 3. Configuration (`.env`)

| Variable | Défaut | Rôle |
|---|---|---|
| `OPENWEATHER_API_KEY` | *(obligatoire)* | Clé OpenWeather |
| `WEATHER_LAT` / `WEATHER_LON` | 48.8566 / 2.3522 | Coordonnées (Paris par défaut) |
| `LOCATION_NAME` | `Paris` | Nom affiché en bas à droite |
| `GCAL_ENABLED` | `false` | `true` pour afficher l'agenda |
| `GCAL_CALENDAR_ID` | `primary` | Agenda à lire |
| `GCAL_DAYS_AHEAD` | `1` | Nombre de jours affichés après aujourd'hui |
| `GCAL_TOKEN_PATH` | `~/weather-display/token.json` | Jeton OAuth Google |

Le fichier `.env` contient une clé secrète : il ne doit pas être versionné (déjà exclu par `.gitignore`).

## 4. Lancer

```bash
./run.sh                       # affiche sur l'écran
./run.sh --preview             # écrit preview.png, sans toucher l'écran
./run.sh --preview /tmp/t.png  # aperçu vers un autre fichier
```

`run.sh` se place dans le bon dossier, charge `.env` et le venv, puis lance `weather_display.py`. Il peut donc être appelé de n'importe où, y compris depuis cron.

### Mise à jour automatique (cron)

```bash
crontab -e
```

```cron
# toutes les 30 minutes
*/30 * * * * /home/pi/weather-display/run.sh >> /home/pi/weather-display/weather.log 2>&1
```

Adapte le chemin à ton utilisateur. Un e-ink n'a pas besoin d'être rafraîchi plus souvent : 30 minutes est un bon compromis, et ménage l'écran.

## 5. Données optionnelles

### Saint du jour : `saints.json`

Fichier JSON dont les clés sont les mois en anglais (`january` … `december`). Chaque mois est une liste d'un élément par jour, et chaque élément est `[nom, préfixe]` (préfixe vide possible). Le texte affiché est `préfixe nom`. Sans ce fichier, rien n'est affiché, sans erreur.

### Google Calendar : `token.json`

- Activer `GCAL_ENABLED=true`.
- Le jeton OAuth doit exister dans `GCAL_TOKEN_PATH` avec le scope `https://www.googleapis.com/auth/calendar.readonly`. Il est rafraîchi automatiquement s'il expire.
- Bibliothèques : `google-api-python-client`, `google-auth`, `google-auth-oauthlib` (déjà dans `requirements.txt`).
- En cas de problème de jeton, l'agenda affiche simplement « Aucun événement ».

## 6. Organisation du code

| Fichier | Rôle |
|---|---|
| `weather_display.py` | Point d'entrée : récupère les données, compose l'image, l'envoie à l'écran ou en PNG |
| `config.py` | Variables d'environnement, dimensions, chemins |
| `palette.py` | Couleurs Inky et palette PIL alignée sur leurs indices |
| `icons.py` | Chargement des icônes et conversion en aplats 6 couleurs (mis en cache) |
| `data.py` | OpenWeather, Google Calendar, saint du jour |
| `canvas.py` | Primitives de dessin : texte, lignes, icônes, lune |
| `sections.py` | Les zones de l'écran (en-tête, heures, jours, agenda, pied de page) |

Le flux : `data` → `weather_display.build_image()` → `sections` (qui dessinent via `canvas`) → image palettisée → écran ou PNG.

## 7. Personnaliser

- **Nombre d'heures / colonnes** : `HOURS_COUNT` et `HOURS_PER_ROW` en haut de `sections.py`.
- **Agenda** : `AGENDA_X`, `AGENDA_MAX_EVENTS`, `AGENDA_TITLE_MAX`, même fichier.
- **Tailles de police** : dictionnaire `fonts` dans `canvas.py`.
- **Rendu des icônes** : seuils en haut de `icons.py`.
  - `VAL_DARK` : plus il est haut, plus les gris deviennent noirs.
  - `SAT_COLOR` : plus il est bas, plus de pixels deviennent colorés (utile si les flocons ou gouttes disparaissent).
  - `ALPHA_MIN` : seuil de transparence.
- **Changer de jeu d'icônes** : modifier `ICON_DIR` dans `config.py`, en gardant les noms `01d.png` … `50n.png`.

Après chaque réglage, `./run.sh --preview` permet de voir le résultat sans attendre l'écran.

## 8. Pourquoi les icônes sont retraitées

L'écran n'affiche que 6 couleurs : noir, blanc, jaune, rouge, bleu, vert. Les icônes d'origine sont en dégradés et en gris pâles, qu'il rend mal. Le script les convertit donc pixel par pixel :

- jaune pour le soleil et la lune ;
- bleu pour la pluie ;
- contour noir et intérieur blanc pour les nuages ;
- fond transparent conservé.

L'image finale est en mode `P` (palettisé) avec les indices exacts de l'Inky, pour éviter toute requantification ou dithering.

## 9. Dépannage

| Symptôme | Piste |
|---|---|
| `ERREUR: Configure .env avec OPENWEATHER_API_KEY` | `.env` absent, ou script lancé sans passer par `run.sh` |
| « Erreur météo » à l'écran | Clé invalide, One Call 3.0 non activée sur le compte, ou pas de réseau. Le détail est dans la console ou le log. |
| Jours en anglais | Locale `fr_FR.UTF-8` non générée |
| Carrés vides à la place de caractères | Police DejaVu absente (`fonts-dejavu-core`) |
| Icônes remplacées par un carré avec `?` | Dossier `ICON_DIR` introuvable ou nom de fichier incorrect |
| Icône invisible ou grise | Ajuster les seuils de `icons.py` |
| Erreur SPI / GPIO | SPI désactivé, ou utilisateur hors des groupes `spi` et `gpio` |
| Rien ne change via cron | Regarder `weather.log` ; vérifier le chemin absolu dans la crontab |
| Agenda vide | `GCAL_ENABLED` à `false`, jeton absent ou expiré |

## 10. Historique

| Version | Changements |
|---|---|
| 0.15 | Découpage en modules, option `--preview`, chemins relatifs au script, correction de chevauchements (température / icône, pluie / vent) |
| 0.14 | Image palettisée Inky, icônes recolorisées en aplats, lune dessinée à la place de l'emoji, fenêtre de l'agenda corrigée (fuseau horaire), agenda en noir |
| 0.13 | Icônes PNG, agenda groupé par date |

## 11. Crédits et licences

- **Icônes météo** : © Dovora Interactive, pack « Modern », sous licence
  [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
  Elles sont recolorisées au chargement pour l'e-ink (voir `ATTRIBUTION.md`).
- **Code** : voir le fichier `LICENSE`.

## 11. Crédits et licences

- **Icônes météo** : © Dovora Interactive, pack « Modern », sous licence
  [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
  Elles sont recolorisées au chargement pour l'e-ink (voir `ATTRIBUTION.md`).
- **Code** : voir le fichier `LICENSE`.
