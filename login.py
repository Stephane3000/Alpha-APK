import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk  # Pour un look moderne

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("M.OPTIQUE - Connexion")
        self.root.geometry("400x500")
        self.root.resizable(True, True)

        # Configuration pour un look moderne
        ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
        ctk.set_default_color_theme("blue")  # Thèmes: "blue" (standard), "green", "dark-blue"

        # Frame principal
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Titre
        self.title_label = ctk.CTkLabel(self.main_frame, text="Bienvenue dans M.OPTIQUE",
                                        font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=(20, 10))

        # Champ Email/Utilisateur
        self.username_label = ctk.CTkLabel(self.main_frame, text="Email ou Nom d'utilisateur:")
        self.username_label.pack(pady=(10, 0))
        self.username_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Entrez votre email")
        self.username_entry.pack(pady=(0, 10), fill="x", padx=20)

        # Champ Mot de passe
        self.password_label = ctk.CTkLabel(self.main_frame, text="Mot de passe:")
        self.password_label.pack(pady=(10, 0))
        self.password_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Entrez votre mot de passe",
                                           show="*")
        self.password_entry.pack(pady=(0, 20), fill="x", padx=20)

        # Bouton Connexion
        self.login_button = ctk.CTkButton(self.main_frame, text="Connexion",
                                          command=self.login, fg_color="blue", hover_color="darkblue")
        self.login_button.pack(pady=(0, 10), fill="x", padx=20)

        # Bouton Créer un compte
        self.register_button = ctk.CTkButton(self.main_frame, text="Créer un compte",
                                             command=self.register, fg_color="green", hover_color="darkgreen")
        self.register_button.pack(pady=(0, 20), fill="x", padx=20)

        # Lien Mot de passe oublié (optionnel)
        self.forgot_password_label = ctk.CTkLabel(self.main_frame, text="Mot de passe oublié?",
                                                 text_color="white", cursor="hand2")
        self.forgot_password_label.pack(pady=(0, 10))
        self.forgot_password_label.bind("<Button-1>", self.forgot_password)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
            return

        # Ici, vous pouvez ajouter la logique de vérification des credentials
        # Pour l'exemple, on simule une connexion réussie
        if username == "admin" and password == "password":
            messagebox.showinfo("Succès", "Connexion réussie!")
            self.open_main_app()
        else:
            messagebox.showerror("Erreur", "Nom d'utilisateur ou mot de passe incorrect.")

    def register(self):
        # Ouvrir une fenêtre d'inscription
        register_window = ctk.CTkToplevel(self.root)
        register_window.title("Créer un compte")
        register_window.geometry("400x400")

        # Champs pour l'inscription
        ctk.CTkLabel(register_window, text="Nom d'utilisateur:").pack(pady=(20, 0))
        username_entry = ctk.CTkEntry(register_window, placeholder_text="Entrez un nom d'utilisateur")
        username_entry.pack(pady=(0, 10), fill="x", padx=20)

        ctk.CTkLabel(register_window, text="Email:").pack(pady=(10, 0))
        email_entry = ctk.CTkEntry(register_window, placeholder_text="Entrez votre email")
        email_entry.pack(pady=(0, 10), fill="x", padx=20)

        ctk.CTkLabel(register_window, text="Mot de passe:").pack(pady=(10, 0))
        password_entry = ctk.CTkEntry(register_window, placeholder_text="Entrez un mot de passe", show="*")
        password_entry.pack(pady=(0, 10), fill="x", padx=20)

        ctk.CTkLabel(register_window, text="Confirmer mot de passe:").pack(pady=(10, 0))
        confirm_password_entry = ctk.CTkEntry(register_window, placeholder_text="Confirmez le mot de passe", show="*")
        confirm_password_entry.pack(pady=(0, 20), fill="x", padx=20)

        def create_account():
            username = username_entry.get()
            email = email_entry.get()
            password = password_entry.get()
            confirm_password = confirm_password_entry.get()

            if not username or not email or not password or not confirm_password:
                messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
                return

            if password != confirm_password:
                messagebox.showerror("Erreur", "Les mots de passe ne correspondent pas.")
                return

            # Ici, ajouter la logique pour créer le compte (sauvegarder en base, etc.)
            messagebox.showinfo("Succès", "Compte créé avec succès!")
            register_window.destroy()

        ctk.CTkButton(register_window, text="Créer le compte", command=create_account,
                      fg_color="green", hover_color="darkgreen").pack(fill="x", padx=20)

    def forgot_password(self, event):
        # Logique pour mot de passe oublié
        messagebox.showinfo("Mot de passe oublié", "Fonctionnalité à implémenter.")

    def open_main_app(self):
        """Ferme le formulaire de connexion et lance l'application principale."""
        # Fermer la fenêtre de connexion
        try:
            self.root.destroy()
        except Exception:
            pass

        # Importer et démarrer l'application principale (my_home_app.py)
        # l'import est fait ici pour éviter de charger cette dépendance si l'utilisateur ne se connecte jamais.
        from my_home_app import MyHomeApp

        main_root = tk.Tk()
        MyHomeApp(main_root)
        main_root.mainloop()

if __name__ == "__main__":
    root = ctk.CTk()
    app = LoginApp(root)
    root.mainloop()
