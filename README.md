# Usage

### Hud
- Windows 11/10
- Afficher la barre des pods
- Connexion au choix de personnage
- Anticrénélage: aucun
- Limite de passage en mode créature: aucun
- Ne pas cocher afficher les personnages en transparence
- Afficher les coordonnées de la carte
- Mode tactique
- Ne pas cocher utiliser le mode tactique coloré
- Ne pas cocher afficher les cartes adjacentes
- Ne pas cocher afficher tous les monstres d'un groupe
- Mise à l'echelle 100% paramètre affichage pc
- Résolution 1920x1080
- Ne pas avoir d'écran dupliquer, ca fout la merde apparemment
- Cacher la barre de tâche si windows 10

### Game
- Ne pas être dans le tutoriel
- Etre abonné de préférence
- Avoir le zaap de bonta

# Development

## Setup

### Example of .env:
```
BACKEND_URL=145.239.198.180
USERNAME="temp@example.com"
PASSWORD="lepassword"
```
### Install dependencies:
- `pip install poetry`
- `bash scripts/init.sh`

## Production:

### Generate obfucasted .exe
`pyi-makespec --noconsole --hidden-import "pkg_resources.extern" --add-data "./resources":"./resources" --add-data ".env":"." main.py && mkdir -p dist/ && pyarmor gen --pack main.spec -r main.py dist/`

## Profiling:

### Profile in RealTime:
`python -m cProfile -o scripts/helper/output/benchmark.pstats main.py`

### Display stat results
We need dot command :

- Install graphviz & put bin on path variable
  https://graphviz.org/download/

`gprof2dot -f pstats scripts/helper/output/benchmark.pstats | dot -Tpng -o scripts/helper/output/benchmark_output.png`

### Memory profiler
`mprof run main.py`
`mprof plot`