

import sqlite3              # Eingebaute Python-Datenbank (SQLite), speichert Daten in einer .db Datei
import hashlib              # Macht Passwörter sicher (Hashing)

# Datenbank-Verbindung herstellen
def connect():
    """
    Stellt eine Verbindung zur SQLite-Datenbank her.
    Falls die Datei noch nicht existiert, wird sie automatisch erstellt.
    """
    return sqlite3.connect("todo.db")


# Tabellen erstellen
def create_tables():
    """
    Erstellt die benötigten Tabellen, falls sie noch nicht existieren.
    """
    conn = connect()
    cursor = conn.cursor()

    # Tabelle für Benutzer
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    # Tabelle für Aufgaben
    # Jede Aufgabe gehört zu einem bestimmten Benutzer
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT,
            completed INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


# Passwort hashen (Sicherheit)
def hash_password(password):
    """
    Wandelt ein Passwort in einen SHA256-Hash um. So speichern wir keine Klartext-Passwörter.
    """
    return hashlib.sha256(password.encode()).hexdigest()


# Registrierung eines neuen Users
def register():
    """
    Registriert einen neuen Benutzer und speichert ihn in der Datenbank.
    """
    conn = connect()
    cursor = conn.cursor()

    username = input("Username: ")
    password = input("Passwort: ")

    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hash_password(password))
        )
        conn.commit()
        print("Registrierung erfolgreich!")
    except sqlite3.IntegrityError:
        print("Dieser Username existiert bereits.")

    conn.close()


# Login Funktion
def login():
    """
    Prüft ob Username und Passwort korrekt sind. Gibt die User-ID zurück, wenn erfolgreich.
    """
    conn = connect()
    cursor = conn.cursor()

    username = input("Username: ")
    password = input("Passwort: ")

    cursor.execute(
        "SELECT id FROM users WHERE username=? AND password=?",
        (username, hash_password(password))
    )

    user = cursor.fetchone()
    conn.close()

    if user:
        print("Login erfolgreich!")
        return user[0]  # user_id zurückgeben
    else:
        print("Falsche Login-Daten.")
        return None


# Neue Aufgabe hinzufügen
def add_task(user_id):
    """
    Fügt eine neue Aufgabe für den eingeloggten Benutzer hinzu.
    """
    conn = connect()
    cursor = conn.cursor()

    title = input("Neue Aufgabe: ")

    cursor.execute(
        "INSERT INTO tasks (user_id, title) VALUES (?, ?)",
        (user_id, title)
    )

    conn.commit()
    conn.close()
    print("Aufgabe hinzugefügt.")


# Aufgaben anzeigen
def view_tasks(user_id):
    """
    Zeigt alle Aufgaben des aktuellen Benutzers an.
    """
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, title, completed FROM tasks WHERE user_id=?",
        (user_id,)
    )

    tasks = cursor.fetchall()

    if not tasks:
        print("Keine Aufgaben vorhanden.")
    else:
        for task in tasks:
            status = "DONE" if task[2] else "OPEN"
            print(f"{task[0]} - {task[1]} [{status}]")

    conn.close()


# Aufgabe als erledigt markieren
def complete_task(user_id):
    """
    Markiert eine Aufgabe als erledigt.
    """
    task_id = input("Task ID zum Abschließen: ")

    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE tasks SET completed=1 WHERE id=? AND user_id=?",
        (task_id, user_id)
    )

    conn.commit()
    conn.close()
    print("Aufgabe als erledigt markiert.")


# Aufgabe löschen
def delete_task(user_id):
    """
    Löscht eine Aufgabe des aktuellen Benutzers.
    """
    task_id = input("Task ID zum Löschen: ")

    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM tasks WHERE id=? AND user_id=?",
        (task_id, user_id)
    )

    conn.commit()
    conn.close()
    print("Aufgabe gelöscht.")


# Hauptprogramm
def main():
    """
    Startpunkt des Programms. Hier läuft das Hauptmenü.
    """
    create_tables()

    while True:
        print("\n--- To-Do App ---")
        print("1 - Registrieren")
        print("2 - Login")
        print("3 - Beenden")

        choice = input("Auswahl: ")

        if choice == "1":
            register()

        elif choice == "2":
            user_id = login()

            # Wenn Login erfolgreich -> User-Menü starten
            if user_id:
                while True:
                    print("\n--- Benutzer Menü ---")
                    print("1 - Aufgabe hinzufügen")
                    print("2 - Aufgaben anzeigen")
                    print("3 - Aufgabe abschließen")
                    print("4 - Aufgabe löschen")
                    print("5 - Logout")

                    action = input("Auswahl: ")

                    if action == "1":
                        add_task(user_id)
                    elif action == "2":
                        view_tasks(user_id)
                    elif action == "3":
                        complete_task(user_id)
                    elif action == "4":
                        delete_task(user_id)
                    elif action == "5":
                        print("Logout erfolgreich.")
                        break
                    else:
                        print("Ungültige Eingabe.")

        elif choice == "3":
            print("Programm beendet.")
            break
        else:
            print("Ungültige Eingabe.")


# Programm starten
if __name__ == "__main__":
    main()
