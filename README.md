# IA712 - Projet Robotique Mobile
**Harfouche Peter** - **Aillaud Arnaud**

## Présentation du projet
Pour ce projet, nous avons décidé de travailler sur 2 modules principaux :
* Un module de reconnaissance vocal, permettant de contrôler un drone Tello par la voix
* Un module de tracking, permettant de détecter et suivre une personne via la caméra principale du drone, lorsque le mode tracking est activé

L'implémentation de ces 2 modules nous a permis de mettre en pratique nos cours de:
* Dialogue multimodal via l'utilisation d'un modèle Speech-to-text
* NLP via l'utilisation d'un modèle de traduction français $\rightarrow$ anglais
* Computer Vision via l'utilisation d'un modèle de détection d'objets
* Robotique mobile via l'utilisation d'un filtre de Kalman pour le suivi de position

Les détails relatifs à chacune de ces applications sont exposés ci-après.

### Speech-to-text

Pour cette partie, nous avons opté pour l'utilisation de l'[API Vosk](https://alphacephei.com/vosk/). Cette librairie offre les avantages d'être bien documentée, d'être facilement installable et utilisable (API Python), d'être suffisamment légère pour être utilisée sur des appareils mobiles (le code tourne sur un ordinateur portable, mais cela reste appréciable) et d'avoir des performances suffisantes pour notre objectif (le drone n'a finalement besoin de reconnaître qu'un nombre limité de commandes). <br>
Nous souhaitions pouvoir nous adresser au drone en français, tant par commodité que pour faciliter la tâche au modèle (l'accent français peut être compliqué à transcrire pour certains mots). Nous avons donc décidé d'utiliser le modèle [vosk-model-fr-0.22](https://alphacephei.com/vosk/models/vosk-model-fr-0.22.zip)

Au niveau du fonctionnement, Vosk s'appuie en fait sur 3 modules différents pour réaliser la conversion voix $\rightarrow$ texte :
* Un modèle acoustique
* Un modèle de langue
* Un dictionnaire phonétique

### Traduction français $\rightarrow$ anglais

Helsinki https://huggingface.co/Helsinki-NLP/opus-mt-fr-en
, MarianMT => transformer https://huggingface.co/docs/transformers/model_doc/marian

### Détection d'objets
### Suivi de position

<p align="center"> 
    <img src="Demos/Demo_tracking.gif" alt="206" width="600">
</p>


## Installation
⚠️ Il est fortement conseillé d'installer le projet dans un environnement virtuel dédié ! ⚠️ <br>
Exemple de création et activation d'environnement virtuel :
```bash
python -m venv IA712_Robotique_mobile
source IA712_Robotique_mobile/bin/activate
```

1. Clonage du repository
```bash
git clone https://github.com/H-Pierre/Robotics.git
```
2. Installation des dépendances
```bash
cd Robotics/
pip install -r requirements.txt
```
3. Téléchargement du modèle de traduction depuis HuggingFace
```bash
python3 download_translation_weights.py
```
4. Téléchargement du modèle Speech-to-text <br>
Télécharger l'archive [vosk-model-fr-0.22](https://alphacephei.com/vosk/models/vosk-model-fr-0.22.zip) et la dézipper dans le dossier data, ou modifier le path à la ligne 19 dans `tello_object_tracking.py`
```python
Speech2Text = Model("PATH-A-MODIFIER/vosk-model-fr-0.22")
```

## Utilisation
⚠️ Avant toute utilisation, s'assurer que la salle de test est suffisamment grande. Le mode tracking est activé par défaut, et le drone cherche à détecter une personne dans son ensemble pour effectuer le tracking : après décollage, il va se reculer jusqu'à pouvoir obsever la personne des pieds à la tête. Il y a un fort risque de collision avec tout objet/personne présent(e) derrière le drone au décollage (mais le mode tracking peut être désactivé avant le décollage). ⚠️ <br>
1. Allumer un drone Tello et se connecter à son réseau WiFi depuis l'ordinateur où le projet est installé. 
2. Lancer le programme avec l'une des commandes suivantes
Utilisatin classique :
```bash
python3 tello_object_tracking.py -proto ./data/ssd_mobilenet_v1_coco_2017_11_17.pbtxt -model ./data/frozen_inference_graph.pb -obj Person -dconf 0.4
```
En mode DEBUG :
```bash
python3 tello_object_tracking.py -proto ./data/ssd_mobilenet_v1_coco_2017_11_17.pbtxt -model ./data/frozen_inference_graph.pb -obj Person -debug True -video ./data/<your video.avi> -dconf 0.4
```

Liste des commandes vocales reconnues par le drone (plusieurs mots sont autorisés pour certaines actions, pour laisser plus de marge aux erreurs de transcription/traduction). Les paramètres entre chevrons en italique sont optionnels :
* <ins>Tracking</ins> : permet de changer le mode de tracking du drone, i.e. désactive le mode tracking si le drone est en mode tracking, ou l'active s'il n'est pas en mode tracking
* <ins>Décolle / décollage / décoller</ins>: Fait décoller le drone
* <ins>Atterit / atterrissage / atterir</ins>: Fait atterir le drone
* <ins>Gauche <*chiffre*></ins> : Effectue une déplacement latéral gauche de *chiffre* centimètres. En l'absence de paramètre optionnel, le drone se déplace de 20 cm
* <ins>Droit / droite</ins>  : Effectue une déplacement latéral droit de *chiffre* centimètres. En l'absence de paramètre optionnel, le drone se déplace de 20 cm
* <ins>Monte / monter <*chiffre*></ins> : Monte de *chiffre* centimètres. En l'absence de paramètre optionnel, le drone monte de 30 cm
* <ins>Descend / descendre <*chiffre*></ins> : Descend de *chiffre* centimètres. En l'absence de paramètre optionnel, le drone descend de 30 cm
* <ins>Tourne / tourner <*chiffre*></ins> : Effectue une rotation de *chiffre* degrés dans le sens horaire. En l'absence de paramètre optionnel, le drone tourne de 20°
* <ins>Avance / avancer <*chiffre*></ins> : Avance de *chiffre* centimètres. En l'absence de paramètre optionnel, le drone avance de 20 cm
* <ins>Recule / reculer <*chiffre*></ins> : Recule de *chiffre* centimètres. En l'absence de paramètre optionnel, le drone recule de 20 cm
* <ins>Flip / Philippe</ins> : Effectue une flip vers la droite

En cas de problème, la touche `l` (pour land) peut être utilisée pour provoquer un atterrissage d'urgence.

Le programme affiche en continu les phrases perçues, et affiche un message s'il ne comprend pas les commandes qui lui sont adressées.


## Ressources

1. [Tello SDK 1.3.0.0](https://dl-cdn.ryzerobotics.com/downloads/tello/20180910/Tello%20SDK%20Documentation%20EN_1.3.pdf)
2. [Tello SDK 2.0](https://dl-cdn.ryzerobotics.com/downloads/Tello/Tello%20SDK%202.0%20User%20Guide.pdf)
3. [OpenCV](https://github.com/opencv/opencv)
4. [Modèles préentraînés](https://github.com/opencv/opencv/tree/master/samples/dnn/face_detector)
