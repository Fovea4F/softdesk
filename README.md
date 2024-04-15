# Scénario

SoftDesk, une société d'édition de logiciels de collaboration, a décidé de publier une application permettant de remonter et suivre des problèmes techniques. Cette solution, SoftDesk Support, s’adresse à des entreprises en B2B (Business to Business).

SoftDesk a mis en place une nouvelle équipe chargée de ce projet et vous avez été embauché comme ingénieur logiciel pour créer un back-end performant et sécurisé, devant servir des applications front-end sur différentes plateformes. Il faut alors trouver un moyen standard de traiter les données, ce qui peut se faire en développant une API RESTful.

Le projet permet d'appréhender la mise en œuvre d'une API RESTFULL sécurisée basée sur DJANGO Rest.

# Installation

## 1. Prérequis

Il est nécessaire d'installer Poetry afin de déployer ce projet.
Allez sur le site de Poetry pour le téléchargement et l'installation de la dernière version

## 2. Déploiement du code

- Décompresser le zip téléchargé depuis Github sur une nouvelle arborescence locale.
- Le fichier **pyproject.toml** contient la liste des paquets de dépendance.
- Lancer la commande **Poetry install** : Les paquets correspondant au contenu du fichier **.toml** vont être téléchargés et installés.

## 3. Lancement du serveur

- La commande **python manage\.py runserver "xxxx"** permet de démarrer le serveur web en écoute sur le port **"xxxx"**
