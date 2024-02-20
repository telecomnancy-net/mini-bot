### Bot de Citation Discord

Ce bot Discord est conçu pour gérer et poster des citations dans un serveur Discord, en permettant aux utilisateurs de soumettre des citations et de les afficher dans un canal spécifique. Voici un aperçu des fonctionnalités et des instructions pour configurer et utiliser le bot.

---

### Instructions

1. **Configuration initiale**
   - Avant d'utiliser le bot, assurez-vous d'avoir défini les éléments suivants :
     - Un fichier `secrettoken.txt` contenant le jeton d'authentification de votre bot Discord.
     - Définissez les IDs des canaux appropriés dans le code (`channelCitationsID`) ou via la commande `setchannel`.

2. **Exécution du bot**
   - Exécutez le script pour lancer le bot Discord.
   - Assurez-vous que le bot est correctement ajouté à votre serveur Discord.

3. **Utilisation des commandes**
   - Le bot répond à deux commandes principales :
     - `/setchannel` : Définit le salon où envoyer les citations.
     - `/post` : Poster une citation dans le salon défini.

4. **Interactions utilisateur**
   - Les utilisateurs peuvent poster des citations via des commandes ou directement dans les messages privés du bot.

5. **Réactions et traitement**
   - Les réactions sur les messages sont surveillées pour permettre des actions supplémentaires, comme le changement de couleur de citation.

6. **Personnalisation**
   - Vous pouvez personnaliser les réactions et les comportements du bot en modifiant le code Python selon vos besoins.

---

### Dépendances
- Ce bot utilise la bibliothèque `discord.py` pour interagir avec l'API Discord.
- Assurez-vous d'installer la version appropriée de cette bibliothèque avant d'exécuter le bot.

### Configuration requise
- Python 3.x
- Un compte Discord pour créer un bot et gérer les autorisations nécessaires.

### Auteur
Ce bot a été créé par Boufty

Pour toute question ou assistance, veuillez me contacter à @boufty.

--- 

### Avertissement
Assurez-vous de ne pas partager votre jeton d'authentification (`secrettoken.txt`) avec quiconque, car cela pourrait compromettre la sécurité de votre bot Discord.

---

**Remarque :** Ce fichier README est fourni à titre informatif uniquement. Assurez-vous de comprendre le code que vous exécutez et de prendre des mesures pour sécuriser votre bot Discord conformément aux meilleures pratiques de sécurité.
