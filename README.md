# ReadMe : Test technique - Alternance - Junior Data Manager

## 1.Intoduction: 
Le test consiste a réalisé un traitement sur un dump d'une base de donnée PosteGresSql dans le cadre d'un projet intitulé de **Goodwill**. Il est composé en trois taches essentiel qui sont:
- Récupèrer la base de donnée a partir du fichier dump et extraire des informations sur des fichiers CSV et JSON.
- Réaliser un petit rapport ( ReadMe File ) sur lequel j'explique ce que j'ai fais.
- Mettre tout ce que j'ai fais dans un repertoire privé et le partager avec monsieur Florian BRUNIAUX.

Pour la réalisation de ce test on aura besoin des outils suivants: 
- SGBD PostgreSQL avec la version 9.6 ou une version plus récente, pour ce qui ne l'ont pas, vous pouvez suivre le [lien suivant.](https://www.postgresql.org/download/linux/ubuntu/ "lien suivant.")
- Le langage python3.
- Les modules  [psycopg2](https://pypi.org/project/psycopg2/ "psycopg2") pour la manupulation de PostegreSQL avec python.

## 2. La recupération de la base de donnée: 
En s'appuiyant sur le fichier dump nommé de "test-JDM-dump_db_impacters" et disponible sur ce [bucket](https://www.google.com/url?sa=D&q=https://test-technique-alternant-junior-data-manager.s3.eu-west-3.amazonaws.com/test-JDM-dump_db_impacters&ust=1597353480000000&usg=AOvVaw0lq_Z6sOs4h3jbpttWcCWb&hl=en-GB&source=gmail "bucket"). on essaye de recupérer la base de donnée avec ses informations, pour cela j'ai suivi ces étapes:

### 2.1. Connexion au SGBD en tant que super user:
La première étape pour pouvoir manipuler les bases des données en PostegreSQL c'est bien sur la connexion, a l'instalation de ma base de donnée, un utilisateur par défaut nommé **postgres** a été crée. pour la connexion a cette utilisateur, j'ai utilisé la commande : 

```shell
su postegres
```

###### Attention: 
A l'instalation de postegreSQL, postgres sera sans mot de passe, pour faire une première connexion,  vous devrez vous connecter en terminal en tant que super user et donner un mot de passe a postgres, vous pouvez suivre les commandes suivantes:

```shell
sudo su # Vous serez amener a une authentification de votre utilisateur
passwd postgres # la vous aurez la main pour mettre votre nouveau mot de passe

```
Une fois vous etes connecté en tant que postgres user, vous pouvez taper la commande psql pour en profiter des fonctionnalité de la SGBD PostegreSQL, un petit guide pour les commandes est [ici.](https://www.postgresqltutorial.com/postgresql-cheat-sheet/ "ici")

### 2.2. Création d'une base de donnée:
Dans le but d'avoir une base de donnée ou je serai capable de stocker le résultat, j'ai crée une base donnée nommé "impacters" sur laquelle j'étais capable de récupèrer les informations de stocké dans le fichier dump. Pour le faire il suffit d'éxcuter la commande suivante : 
```sql
CREATE DATABASE impacters;
```

### 2.3. La première tentative de recupération:
Une fois notre base de donnée est crée, on appuie sur les bouton CNTRL + D pour revenir au utilisateur postgres, et on exécute la commande : 

```shell
psql --set ON_ERROR_STOP=on -d impacters -f /var/lib/postgresql/test-JDM-dump_db_impacters 


```
En exécutant cette commande, l'opération de récupération des informations commence, et grace a la commande **--set ON_ERROR_STOP=on** l'opération s'arrète a la première occurence d'erreur. Dans mon cas, l'erreur été l'absence d'un role nommé **"florianbruniaux"** Pour cela, j'étais amené a crée ce role en exécutant les commandes: 

```shell
psql 
CREATE ROLE role_name;
```
###2.4. La récupération de la base de donnée: 
Après la création du role, j'ai relancé la meme commande avec l'utilisateur postgres, et ma récupération est terminé sans erreur. pour une verification de contenu, je me suis connecté a ma base de donnée, et j'ai vérifié les tables et certains informations avec les commandes suivantes: 

```shell
psql 
\c impacters 
\dt # cette commande liste les tables de la base de donnée
\d+ impacter # cette commande affiche les informations sur la table impacter
```

## 3. L'extraction des informations dans des fichiers CSV: 

Une fois la base de donnée en main, j'étais amené a extraire certains informations de la base de donnée avec des commande SQL en me connectant a la base de donnée impacters, et les stockers dans des fichiers CSV. 

###3.1. Liste des associations (ID / Nom): 

Pour récupèrer la liste des associations ( qui sont stocké dans la table legal_entity ), j'étais obligé de récupèrer les identifier a partir de l'id impacters, donc j'étais amené a extraire tout les id des entités de type **"Associtations"**, et avec ces id, extraire l'id d'impacters a partir de la table **impacter_entity_type**; qui seront a la fin utulisé dans la table **legal_entity** pour récupèrer l'id et le nom des associations. Cela est fais grace a la requete suivante : 

```sql
SELECT id,name from legal_entity where impacter_id in (SELECT impacter_id from impacter_entity_type where entity_type_id in (SELECT id from entity_type where entity_label = 'Association'))
```

Pour extraire l'id et le nom dans un fichier CSV, j'ai crée un fichier CSV nommé **MELLAL-Houdaifa_associations-extract.csv** et j'ai lui donné les accès, et puis j'ai utilisé la commande **\copy** pour l'extraction avec la manière suivante: 

```sql
\copy ( SELECT id,name from legal_entity where impacter_id in (SELECT impacter_id from impacter_entity_type where entity_type_id in (SELECT id from entity_type where entity_label = 'Association'))) to '/home/gogle591/Usefull files/Autonome/Technical tests/MELLAL-Huudaifa_associations-extract.csv' DELIMITER ',' CSV HEADER ENCODING 'UTF8'
```
##### Remarque: 
L'encodage été mis dans le but de la reconnaisance des lettres avec les caractères spécieux commes les accents.

### 3.2. roles des mandats d'élus: 
Pour cette tache, c'est impossible d'identifier uniquement les roles de mandants d'élus, parce que la seul moyen de savoir si c'est un role d'elus ou pas c'est a partir de l'id physical_person_id, et une personne pourra avoir plusieurs role a la fois, ou meme durant son parcours, donc, tout les roles qui a eux durant son parcours vont etre identifier a partir de son physical_person_id. Ce que j'ai fais est de faire une petite demonstration sur ce que je viens dire avec la requete suivante: 

```sql
SELECT DISTINCT role from position where physical_person_id in ( SELECT id from physical_person where impacter_id in ( Select impacter_id from impacter_entity_type where entity_type_id = ( SELECT id from entity_type where entity_label = 'Elected'))); 
```
En effet, j'ai pris tout les roles qui ont été occupés par une personne qui est un impacter de type elus ( entity_label = Elected de la table entity_type), le soucis c'est que la personne élus pourra avoir le role Senior official.

## 4. La liste des impacters avec encore au moins 1 mandat actif avec Python dans des fichiers Json:

Cette tache a été réalisé a l'aide du langage python et le langage SQL avec les étapes suivants:

### 4.1. Connexion PostgreSQL: 
Pendant cette tache, j'ai utilisé le module psycopg2 pour etablir une connexion a l'utilisateur postgres et a la table impacters avec les lignes de codes suivantes : 

```python
import psycopg2
import traceback

dbname= input(" Saisir le nom de votre base de donnée:\n")
username = input(" Saisir le nom de votre utilistauer (username):\n")
password = input("Saisir votre mot de passe:\n ")

try:
    connect_str = "dbname='{}' user='{}' host='localhost' password='{}'".format(dbname,username,password)
    # use our connection values to establish a connection
    conn = psycopg2.connect(connect_str)
    # create a psycopg2 cursor that can execute queries
    cursor = conn.cursor()
except Exception as e:
    print(e)
    print(traceback.format_exc())
```
Le choix du nom de la base de donnée, l'utilisateur et le password est laissé ouvert, pour que le script marche avec tout les noms des utilisateurs et des bases des données de la meme structure.

le cursor va etre utiliser dans ce qui suit, il sert a effectuer des requetes.

### 4.2. La récupuration des personnes qui respectent la contrainte:
Une fois la connexion est établis, une requete a été faite pour recupèrer les id des personnes physiques qui ont au moins un mendant en cours, la requete est la suivante : 
```python
cursor.execute("""SELECT DISTINCT physical_person_id from position where NOW()::timestamp::date < end_date;""")
conn.commit() 
person_ids = cursor.fetchall()
```
Une fois les id des personnes concernés par la contraintes ( ils sont 80 personnes), une autre étape commence.

###4.3. La création d'un dictionnaire suivant la strecture donnée:
Dans le script python, plusieurs fonctions ont été implimenté pour faire la création d'un dictionnaire de la meme strecture d'un fichier Json demandé dans l'énoncé, les fonctions sont les suivants: 
- **def make_position(role,territory_code,territory_name,start_date,end_date): ** Cette fonction prends en paramètres les informations role, code terettoire, nom du terettoire, la date de début et la date de fin, et elle retourne un dictionnaire qui associe chaque information a sa case. Dans le cas ou la date de fin n'est pas indiqué, ceci sera ignoré. 

- **def make_positions(id_physical_person, cursor):** Cette fonction utilise la fonction précedentes pour créer une liste des positions, en effet, elle prends en entré l'identifiant d'une personne physique, et elle excute avec le cursor la requete suivante : 

```python
cursor.execute("SELECT role, start_date, end_date, legal_entity_id from position where 
physical_person_id = '{}' ORDER BY start_date;".format(id_physical_person))
    rows = cursor.fetchall()
```
Elle recupère donc dans rows tout les positions prise par une personne, et donc, pour chaque position, elle crée une position, et elle l'ajoute a un tableau défini au début de la fonction.  
A la fin, cette fonction retourne la liste des dictionnaires qui décrit les positons occupés par une personne donnée.

- **def make_impacter(id,name,positions):*** C'est le meme principe pour la fonction make_position, elle prends en entré les informations id, nom et les positions occupées, et elle retourne un dictionnaire associe chaque case a sa clé.

- ** def make_impacters(person_ids, cursor):** Cette fonction utilise les deux fonctions make positions et make_impacter et make_positions. elle prends en paramètre tout les id des personnes concernés par la containte, et puis a l'aide d'une boucle for, elle parcours chaque personne, pour qu'elle crée un dictionnaire pour chaque personne avec les informations associés au clés, elle utilise aussi le cursor pour obtenir les informations necessaires. pour la récupèration de l'id de la table surnom, et le nom et le prénom de la table physical person elle utilise les lignes suivantes : 

```python
cursor.execute("SELECT firstname, lastname, impacter_id from physical_person where id = '{}';".format(id_physical_person[0]))
impacter = cursor.fetchall()[0]
name = impacter[0] + " "+ impacter[1]
cursor.execute("SELECT surname_text from surname where impacter_id = '{}'".format(impacter[2]))
id = cursor.fetchall()[0][0]
```
cette fonction retourne un tableau d'impacters.


###4.3. La création de dictionnaire finale et la transformation en Json:

Après la requete de recupération des id des peronnes physiques concerné par la contrainte, on passe la liste person_ids en paramètre avec le cursor a la fonction make_impacters, et on recupère le tableau des impacters.
Une fois le tableau est retourné, on crée le dernier dectionnaire avec la strecture décrite, ensuite on applique les lignes de code suivants pour transofrmer le dictionnaire en fichier.

```python
impacters = make_impacters(person_ids,cursor)
    jsonfile = {
        "impacters": impacters
    }
    with open("test.json", "w", encoding="utf-16") as outfile: 
		json.dump(jsonfile, outfile, indent=4, ensure_ascii=False) 
```

Les options :
- **encoding="utf-16"** et **ensure_ascii=False** : sont important pour faire appraitre les accents dans les fichiers Json. 
- **indent=4**: Sert a indenter et strecturer les lignes de fichier Json.

## 5.Conclusion: 
Les fichiers rendus sont :
- ReadMe.md : C'est ce fichier écrit dans le cadre de la tache numéro deux.
- MELLAL_Houdaifa_impacters-json-extraction.py : Le script python qui réalise la quatrième partie de la tache une. 
- mendat_encours.json : Le fichier json généré par le script python.
- MELLAL-Houdaifa_roles-extract.csv: Les roles extraires dans le cadre de la troisième partie de la tache une.
- MELLAL-Houdaifa_associations-extract.csv: Les associations (ID/Nom) extraires dans le cadre de la deuxième partie de la tache une.

Ce travail a été réalisé dans le cadre d'un test technique pour le poste de Data Manager Junior en alternance, je me suis bien amusé en le faisant, et je l'ai trouvé très interessant comme projet, dans l'espère d'avoir une chance pour faire partie de son équipe de travail.














