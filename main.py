import re
import sqlite3


def format_numero(numero):

    def add_point_on_every_two_digits(numero):
        return ".".join(numero[i:i+2] for i in range(0, len(numero), 2))

    formated_numero = ""
    if len(numero) == 10:
        formated_numero = add_point_on_every_two_digits(numero)
    elif numero.startswith("33"):
        formated_numero = "33." + numero[3] + "." + add_point_on_every_two_digits(numero[3:])

    return formated_numero


def get_conn_database():
    return sqlite3.connect("database.db")


def exec_query_select(*query):
    conn = get_conn_database()
    c = conn.cursor()
    c.execute(*query)
    all_result = c.fetchall()
    conn.commit()
    conn.close()
    return all_result


def exec_query(*query):
    """
    Fonction pour modifier la structure ou les données d'une base
    """
    conn = get_conn_database()
    c = conn.cursor()
    try:
        c.execute(*query)
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.close()


class Person:

    def __init__(self, name="", mail="", numero=""):
        self.data = {"name": name, "mail": mail, "numero": numero}

    def save_in_database(self):
        exec_query("INSERT INTO persons VALUES (:name, :mail, :numero)", self.data)


class Persons:

    def __init__(self):
        self._persons = []

    def get_persons(self):
        return self._persons

    def add_person(self, person):
        self._persons.append(person)

    def init_from_text(self, text):
        self.__init__()
        texts_by_persons = re.split(r'M\.|Mme|monsieur|Mlle|Dr|Madame|mademoiselle', text)
        del texts_by_persons[0]

        for text_by_person in texts_by_persons:
            words_by_person = text_by_person.split()
            person = Person()
            person.data["name"] = (words_by_person[0] + " " + words_by_person[1]).strip(".,")

            numero = ""
            for word in words_by_person:
                word = word.strip(".,+")
                if "@" in word and "." in word:
                    person.data["mail"] = word
                else:
                    word = word.replace(".", "")
                    if word.isdigit():
                        numero += word
            if len(formated_numero := format_numero(numero)) > 0:
                person.data["numero"] = formated_numero

            self.add_person(person)

    def save_in_database(self):
        exec_query("""
            CREATE TABLE IF NOT EXISTS persons(
                name text,
                mail text PRIMARY KEY NOT NULL,
                numero text
            )""")

        for person in self.get_persons():
            person.save_in_database()

    def init_from_database(self):
        self.__init__()
        all_result = exec_query_select("SELECT * FROM persons")
        for result in all_result:
            self.add_person(Person(result[0], result[1], result[2]))

    def show_in_command_line(self):
        text = ""
        line_separator = ""
        padding_x = 1
        column_infos = {"name": "Nom & Prénom", "mail": "Mail", "numero": "Numéro"}
        column_infos = {code: {
            "wording": wording,
            "col_width": padding_x * 2 + max([len(wording),
                                              max(len(person.data[code]) for person in self.get_persons())])
        } for code, wording in column_infos.items()}

        for infos in column_infos.values():
            text += f"|{infos["wording"]:^{infos["col_width"]}}"
            line_separator += f"|{'-' * infos["col_width"]}"

        line_separator += "|\n"
        text += f"|\n{line_separator}"

        for person in self.get_persons():
            for code, infos in column_infos.items():
                text += f"|{' ' * padding_x + person.data[code]:{infos["col_width"]}}"
            text += "|\n"

        text += line_separator
        print(text)


if __name__ == '__main__':

    text = """
Récemment, j'ai eu l'opportunité de rencontrer des entrepreneurs exceptionnels lors d'une conférence. Par exemple, j'ai
 été inspiré par l'histoire de M. Thomas Bernard, qui a démarré sa propre entreprise dans la Silicon Valley. Vous pouvez
  le contacter à l'adresse email thomas.b@alphamail.com ou au numéro suivant +33 1 12 34 56 78. Une autre personne
   fascinante était Mme Claire Martin, la fondatrice d'une startup technologique innovante. Elle est joignable à 
   cmartin@betainbox.org, son numéro de téléphone est le 09 01 23 45 67. Ensuite, il y avait monsieur Lucas Petit, un 
   innovateur dans le domaine de la construction durable, contactable à lp@experimentalpost.net, son téléphone est le 
   0890 12 34 56.

En parcourant mon ancien annuaire, je suis tombé sur quelques contacts intéressants. Par exemple, j'ai redécouvert le 
contact de Mlle Sophie Martin. Son numéro de téléphone est 07 89 01 23 45, et elle est facilement joignable à l'adresse
 sophie@prototypemail.com. Un autre contact noté était celui du Dr Lucas Dupont. Je me souviens avoir eu plusieurs 
 discussions avec lui. Son numéro est 06 78 90 12 34 et son mail est drdupont@randominbox.org. C'est fascinant de voir
  comment certains contacts peuvent rapidement nous rappeler des souvenirs passés.

Lors de notre dernière réunion, Madame Jennifer Laroche, joignable au 05.67.890.123 ou par e-mail à 
laroche@trialmail.net, a exprimé sa satisfaction concernant les avancées du projet. Elle a insisté sur la pertinence du 
 feedback fourni par M. Sébastien Girard, qui peut être contacté au 0456789012 ou par email à sebastieng@demomail.org. 
 De plus, notre consultante externe, mademoiselle Chloé Lefebvre, dont le numéro est le 03.45.67.89.01 et l'e-mail est 
 lefebvre_chloe@testinbox.net, a fourni un rapport détaillé qui a été bien reçu par l'équipe.
"""

    persons = Persons()
    persons.init_from_text(text)
    persons.save_in_database()
    persons.init_from_database()
    persons.show_in_command_line()