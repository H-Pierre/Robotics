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
    <img src="./demo_tracking.gif" alt="206" width="600">
</p>


## Installation

## Utilisation

## Ressources

1. [Tello SDK 1.3.0.0](https://dl-cdn.ryzerobotics.com/downloads/tello/20180910/Tello%20SDK%20Documentation%20EN_1.3.pdf)
2. [Tello SDK 2.0](https://dl-cdn.ryzerobotics.com/downloads/Tello/Tello%20SDK%202.0%20User%20Guide.pdf)
3. [OpenCV](https://github.com/opencv/opencv)
4. [Modèles préentraînés](https://github.com/opencv/opencv/tree/master/samples/dnn/face_detector)
