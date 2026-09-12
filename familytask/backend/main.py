import hashlib  # Importe le module permettant de calculer un hash SHA-256.
import os  # Importe le module permettant de lire les variables d'environnement.
import secrets  # Importe le module permettant de générer des codes et des tokens aléatoires.

from fastapi import Depends, FastAPI, Header, HTTPException  # Importe les dépendances FastAPI, la lecture des en-têtes et les erreurs HTTP.
from fastapi.middleware.cors import CORSMiddleware  # Importe le middleware qui autorise les requêtes cross-origin.
from sqlmodel import Field, Session, SQLModel, create_engine, select  # Importe les outils SQLModel nécessaires au modèle, aux sessions et aux requêtes.


class Task(SQLModel, table=True):  # Déclare le modèle Task et l'associe à une table SQL.
    id: int | None = Field(default=None, primary_key=True)  # Définit l'identifiant entier généré automatiquement comme clé primaire.
    family_code: str = Field(index=True)  # Rattache la tâche à la famille du membre qui l'a créée.
    member_id: int | None = Field(default=None, foreign_key="member.id", index=True)  # Rattache éventuellement la tâche à un membre de la famille.
    title: str  # Définit le titre textuel de la tâche.
    done: bool = False  # Définit l'état de la tâche, faux par défaut.


class Member(SQLModel, table=True):  # Déclare le modèle Member et l'associe à une table SQL.
    id: int | None = Field(default=None, primary_key=True)  # Définit l'identifiant entier généré automatiquement comme clé primaire.
    email: str = Field(unique=True, index=True)  # Définit l'adresse électronique unique et indexée du membre.
    name: str  # Définit le nom du membre.
    lien: str  # Définit le lien familial du membre.
    is_admin: bool = False  # Définit le statut administrateur, faux par défaut.
    family_code: str = Field(index=True)  # Définit le code de la famille du membre et l'indexe.
    password_hash: str  # Stocke le hash du mot de passe du membre.
    token: str | None = None  # Stocke le jeton du membre, facultatif par défaut.


class Lien(SQLModel, table=True):  # Déclare la liste des liens de parenté d'une famille.
    id: int | None = Field(default=None, primary_key=True)  # Définit l'identifiant entier généré automatiquement comme clé primaire.
    family_code: str = Field(index=True)  # Rattache le lien de parenté à une famille précise.
    label: str  # Stocke le libellé du lien de parenté.


LIENS_DEFAUT = ["parent", "mère", "père", "fille", "fils", "frère", "sœur", "autre"]  # Définit les liens proposés à une nouvelle famille.


def hash_password(pw: str) -> str:  # Déclare la fonction qui transforme un mot de passe en hash.
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()  # Calcule et retourne le hash SHA-256 en format hexadécimal.


def public_member(member: Member) -> dict:  # Prépare les informations publiques d'un membre sans son hash.
    return {"id": member.id, "email": member.email, "name": member.name, "lien": member.lien, "is_admin": member.is_admin, "family_code": member.family_code}  # Retourne les champs publics sans le hash ni le token.


def seed_family_links(session: Session, family_code: str) -> None:  # Ajoute les liens de parenté initiaux d'une famille.
    for label in LIENS_DEFAUT:  # Parcourt les liens proposés par défaut.
        session.add(Lien(family_code=family_code, label=label))  # Ajoute le lien à la session de la base.


def current_member(authorization: str | None = Header(default=None)) -> Member:  # Recherche le membre connecté à partir de l'en-tête d'autorisation.
    token = authorization[7:].strip() if authorization and authorization.startswith("Bearer ") else ""  # Extrait le token uniquement depuis un en-tête Bearer valide.
    with Session(engine) as session:  # Ouvre une session SQLModel liée au moteur de la base.
        member = session.exec(select(Member).where(Member.token == token)).first() if token else None  # Recherche le membre associé au token.
        if member is None:  # Vérifie que le token correspond bien à un membre.
            raise HTTPException(status_code=401, detail="Authentification requise")  # Refuse l'accès avec un message neutre.
        return member  # Renvoie le membre authentifié.


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./familytask.db")  # Récupère l'adresse de la base avec SQLite comme valeur par défaut.
engine = create_engine(DATABASE_URL)  # Crée le moteur de connexion à la base de données.

app = FastAPI(title="FamilyTask")  # Crée l'application FastAPI avec son titre.
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])  # Autorise les requêtes provenant de toutes les origines.


@app.on_event("startup")  # Enregistre la fonction de création des tables pour le démarrage de l'application.
def create_db_and_tables():  # Déclare la fonction exécutée au démarrage de l'application.
    SQLModel.metadata.create_all(engine)  # Crée les tables SQLModel qui n'existent pas encore.


@app.get("/api/health")  # Déclare la route GET de contrôle de santé de l'application.
def health():  # Déclare le point de contrôle de santé de l'application.
    return {"status": "ok"}  # Retourne un statut confirmant que l'application fonctionne.


@app.post("/api/signup")  # Déclare la route POST de création d'une famille et de son membre administrateur.
def signup(email: str, password: str, name: str, family: str, lien: str):  # Reçoit les informations du premier membre et de sa famille.
    normalized_email = email.strip().lower()  # Normalise l'adresse électronique pour éviter les doublons de casse.
    with Session(engine) as session:  # Ouvre une session SQLModel liée au moteur de la base.
        existing_member = session.exec(select(Member).where(Member.email == normalized_email)).first()  # Vérifie si l'adresse est déjà utilisée.
        if existing_member is not None:  # Vérifie qu'aucun membre ne possède déjà cette adresse.
            raise HTTPException(status_code=400, detail="Cet email est déjà utilisé")  # Refuse la création avec un message explicite.
        family_code = "fam-" + secrets.token_hex(4)  # Génère le code unique de la nouvelle famille.
        member = Member(email=normalized_email, name=name, lien=lien, is_admin=True, family_code=family_code, password_hash=hash_password(password), token=secrets.token_hex(16))  # Crée le membre administrateur avec son hash et son token.
        seed_family_links(session, family_code)  # Initialise la liste des liens de parenté de la nouvelle famille.
        session.add(member)  # Ajoute le membre administrateur à la session.
        session.commit()  # Enregistre la nouvelle famille et son membre dans la base.
        session.refresh(member)  # Recharge le membre après son enregistrement.
    return {"token": member.token}  # Renvoie le token permettant d'authentifier le nouveau membre.


@app.post("/api/login")  # Déclare la route POST de connexion d'un membre existant.
def login(email: str, password: str):  # Reçoit l'adresse électronique et le mot de passe du membre.
    normalized_email = email.strip().lower()  # Normalise l'adresse électronique comme lors de l'inscription.
    with Session(engine) as session:  # Ouvre une session SQLModel liée au moteur de la base.
        member = session.exec(select(Member).where(Member.email == normalized_email)).first()  # Recherche le membre par son adresse.
        if member is None or member.password_hash != hash_password(password):  # Vérifie le membre et son mot de passe hashé.
            raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")  # Refuse les identifiants invalides avec un message clair.
        member.token = secrets.token_hex(16)  # Génère un nouveau token pour cette connexion.
        session.add(member)  # Ajoute la modification du membre à la session.
        session.commit()  # Enregistre le nouveau token dans la base.
    return {"token": member.token}  # Renvoie le nouveau token d'authentification.


@app.get("/api/me")  # Déclare la route qui renvoie le membre actuellement connecté.
def get_me(member: Member = Depends(current_member)):  # Reçoit le membre identifié par son token d'authentification.
    return public_member(member)  # Renvoie les informations du membre sans son hash de mot de passe.


@app.post("/api/logout")  # Déclare la route qui déconnecte le membre actuellement connecté.
def logout(member: Member = Depends(current_member)):  # Reçoit le membre identifié par son token d'authentification.
    with Session(engine) as session:  # Ouvre une session SQLModel pour enregistrer la déconnexion.
        stored_member = session.get(Member, member.id)  # Recharge le membre dans la session active.
        stored_member.token = None  # Efface le token du membre dans la base de données.
        session.add(stored_member)  # Ajoute la modification du membre à la session.
        session.commit()  # Enregistre la suppression du token.
    return {"message": "Déconnexion réussie"}  # Renvoie une confirmation de déconnexion.


@app.get("/api/liens")  # Déclare la route qui liste les liens de parenté de la famille connectée.
def get_links(member: Member = Depends(current_member)):  # Reçoit le membre connecté pour déterminer sa famille.
    with Session(engine) as session:  # Ouvre une session SQLModel liée au moteur de la base.
        links = session.exec(select(Lien).where(Lien.family_code == member.family_code)).all()  # Sélectionne les liens de la famille connectée.
    return [link.label for link in links]  # Renvoie les libellés des liens sous forme de liste.


@app.post("/api/liens")  # Déclare la route qui ajoute un lien de parenté à la famille.
def add_link(label: str, member: Member = Depends(current_member)):  # Reçoit le libellé et le membre connecté.
    if not member.is_admin:  # Vérifie que le membre connecté est administrateur.
        raise HTTPException(status_code=403, detail="Seul l'administrateur peut modifier les liens")  # Refuse l'accès aux membres non administrateurs.
    normalized_label = label.strip()  # Nettoie le libellé reçu avant son enregistrement.
    if not normalized_label:  # Vérifie que le libellé n'est pas vide.
        raise HTTPException(status_code=422, detail="Le lien de parenté ne peut pas être vide")  # Refuse un lien sans libellé.
    with Session(engine) as session:  # Ouvre une session SQLModel liée au moteur de la base.
        existing_link = session.exec(select(Lien).where(Lien.family_code == member.family_code, Lien.label == normalized_label)).first()  # Vérifie si ce lien existe déjà dans la famille.
        if existing_link is not None:  # Vérifie qu'il n'y a pas de doublon dans la famille.
            raise HTTPException(status_code=400, detail="Ce lien existe déjà dans la famille")  # Refuse le doublon avec un message explicite.
        link = Lien(family_code=member.family_code, label=normalized_label)  # Crée le lien dans la famille du membre.
        session.add(link)  # Ajoute le lien à la session.
        session.commit()  # Enregistre le nouveau lien dans la base.
        links = session.exec(select(Lien).where(Lien.family_code == member.family_code)).all()  # Recharge tous les liens de la famille après l'ajout.
    return [item.label for item in links]  # Renvoie la liste actualisée des libellés.


@app.get("/api/members")  # Déclare la route qui liste les membres de la famille connectée.
def get_members(member: Member = Depends(current_member)):  # Reçoit le membre connecté pour déterminer sa famille.
    with Session(engine) as session:  # Ouvre une session SQLModel liée au moteur de la base.
        members = session.exec(select(Member).where(Member.family_code == member.family_code)).all()  # Sélectionne uniquement les membres de la famille connectée.
    return [public_member(item) for item in members]  # Renvoie les membres sans hash ni token.


@app.post("/api/members")  # Déclare la route qui crée un compte dans la famille connectée.
def add_member(email: str, password: str, name: str, lien: str, is_admin: bool = False, member: Member = Depends(current_member)):  # Reçoit les informations du nouveau membre et le membre connecté.
    if not member.is_admin:  # Vérifie que le membre connecté est administrateur.
        raise HTTPException(status_code=403, detail="Seul l'administrateur peut créer un compte")  # Refuse l'accès aux membres non administrateurs.
    normalized_email = email.strip().lower()  # Normalise l'adresse électronique du nouveau compte.
    if not normalized_email or not password.strip() or not name.strip() or not lien.strip():  # Vérifie que les champs obligatoires sont renseignés.
        raise HTTPException(status_code=422, detail="Les informations du membre sont obligatoires")  # Refuse les informations incomplètes.
    with Session(engine) as session:  # Ouvre une session SQLModel liée au moteur de la base.
        existing_member = session.exec(select(Member).where(Member.email == normalized_email)).first()  # Vérifie si l'adresse est déjà utilisée.
        if existing_member is not None:  # Vérifie qu'aucun compte ne possède déjà cette adresse.
            raise HTTPException(status_code=400, detail="Cet email est déjà utilisé")  # Refuse la création du doublon.
        new_member = Member(email=normalized_email, password_hash=hash_password(password), name=name.strip(), lien=lien.strip(), is_admin=is_admin, family_code=member.family_code)  # Crée le nouveau compte dans la famille de l'administrateur.
        session.add(new_member)  # Ajoute le nouveau membre à la session.
        session.commit()  # Enregistre le nouveau membre dans la base.
        session.refresh(new_member)  # Recharge le membre pour obtenir son identifiant.
    return public_member(new_member)  # Renvoie le compte créé sans hash ni token.


@app.delete("/api/members/{id}")  # Déclare la route qui supprime un membre de la famille.
def delete_member(id: int, member: Member = Depends(current_member)):  # Reçoit l'identifiant et le membre connecté.
    if not member.is_admin:  # Vérifie que le membre connecté est administrateur.
        raise HTTPException(status_code=403, detail="Seul l'administrateur peut supprimer un compte")  # Refuse l'accès aux membres non administrateurs.
    if id == member.id:  # Vérifie que l'administrateur ne tente pas de se supprimer lui-même.
        raise HTTPException(status_code=400, detail="Vous ne pouvez pas supprimer votre propre compte")  # Refuse l'auto-suppression.
    with Session(engine) as session:  # Ouvre une session SQLModel liée au moteur de la base.
        target = session.get(Member, id)  # Recherche le membre ciblé par son identifiant.
        if target is None or target.family_code != member.family_code:  # Vérifie que le membre appartient à la famille connectée.
            raise HTTPException(status_code=404, detail="Membre de la famille introuvable")  # Refuse un membre absent ou extérieur à la famille.
        tasks = session.exec(select(Task).where(Task.member_id == target.id)).all()  # Sélectionne les tâches assignées au membre supprimé.
        for task in tasks:  # Parcourt les tâches qui doivent être supprimées avec le compte.
            session.delete(task)  # Supprime la tâche du membre.
        session.delete(target)  # Supprime le compte ciblé.
        session.commit()  # Enregistre la suppression du compte et de ses tâches.
    return {"message": "Membre et tâches supprimés", "id": id}  # Renvoie une confirmation de suppression.


@app.get("/api/tasks")  # Déclare la route GET qui permet de récupérer les tâches du membre connecté.
def get_tasks(member: Member = Depends(current_member)):  # Reçoit le membre connecté pour déterminer sa famille et ses tâches.
    with Session(engine) as session:  # Ouvre une session SQLModel liée au moteur de la base.
        tasks = session.exec(select(Task).where(Task.family_code == member.family_code, Task.member_id == member.id)).all()  # Sélectionne les tâches assignées au membre connecté dans sa famille.
    return list(tasks)  # Renvoie les tâches sous forme de liste.


@app.get("/api/tasks/famille")  # Déclare la route qui permet à l'administrateur de voir toutes les tâches familiales.
def get_family_tasks(member: Member = Depends(current_member)):  # Reçoit le membre connecté pour contrôler son accès à la famille.
    if not member.is_admin:  # Vérifie que le membre connecté est administrateur.
        raise HTTPException(status_code=403, detail="Accès réservé à l'administrateur")  # Refuse l'accès aux membres non administrateurs.
    with Session(engine) as session:  # Ouvre une session SQLModel liée au moteur de la base.
        tasks = session.exec(select(Task).where(Task.family_code == member.family_code)).all()  # Sélectionne toutes les tâches de la famille du membre.
    return list(tasks)  # Renvoie les tâches familiales sous forme de liste.


@app.post("/api/tasks")  # Déclare la route POST qui permet de créer une tâche.
def create_task(title: str, member_id: int | None = None, member: Member = Depends(current_member)):  # Reçoit le titre et le membre éventuellement ciblé.
    if not title.strip():  # Vérifie que le titre contient autre chose que des espaces.
        raise HTTPException(status_code=422, detail="Le titre de la tâche ne peut pas être vide")  # Refuse la création avec un message explicite.
    assigned_member_id = member.id  # Destine par défaut la tâche au membre connecté.
    if member_id is not None:  # Vérifie si un membre cible a été fourni.
        if not member.is_admin:  # Vérifie que seul un administrateur peut choisir un autre membre.
            raise HTTPException(status_code=403, detail="Seul l'administrateur peut assigner une tâche")  # Refuse l'assignation aux membres non administrateurs.
        with Session(engine) as session:  # Ouvre une session pour vérifier le membre cible.
            assigned_member = session.get(Member, member_id)  # Recherche le membre cible par son identifiant.
            if assigned_member is None or assigned_member.family_code != member.family_code:  # Vérifie que le membre appartient à la même famille.
                raise HTTPException(status_code=404, detail="Membre de la famille introuvable")  # Refuse une cible absente ou extérieure à la famille.
        assigned_member_id = member_id  # Conserve l'identifiant du membre cible validé.
    task = Task(family_code=member.family_code, member_id=assigned_member_id, title=title.strip(), done=False)  # Crée la tâche dans la famille du membre connecté.
    with Session(engine) as session:  # Ouvre une session SQLModel liée au moteur de la base.
        session.add(task)  # Ajoute la nouvelle tâche à la session.
        session.commit()  # Enregistre la nouvelle tâche dans la base de données.
        session.refresh(task)  # Recharge la tâche pour obtenir son identifiant généré.
    return task  # Renvoie la tâche créée avec son identifiant.


@app.patch("/api/tasks/{id}")  # Déclare la route PATCH qui permet de basculer l'état d'une tâche.
def toggle_task(id: int, member: Member = Depends(current_member)):  # Reçoit l'identifiant et le membre connecté.
    with Session(engine) as session:  # Ouvre une session SQLModel liée au moteur de la base.
        task = session.get(Task, id)  # Recherche la tâche correspondant à l'identifiant fourni.
        if task is None or task.family_code != member.family_code:  # Vérifie que la tâche appartient à la famille connectée.
            raise HTTPException(status_code=404, detail=f"La tâche avec l'identifiant {id} est introuvable")  # Renvoie une erreur claire si la tâche n'existe pas.
        task.done = not task.done  # Inverse la valeur actuelle du champ done.
        session.add(task)  # Ajoute la tâche modifiée à la session.
        session.commit()  # Enregistre la nouvelle valeur dans la base de données.
        session.refresh(task)  # Recharge la tâche après son enregistrement.
    return task  # Renvoie la tâche modifiée.


@app.delete("/api/tasks/{id}")  # Déclare la route DELETE qui permet de supprimer une tâche.
def delete_task(id: int, member: Member = Depends(current_member)):  # Reçoit l'identifiant et le membre connecté.
    with Session(engine) as session:  # Ouvre une session SQLModel liée au moteur de la base.
        task = session.get(Task, id)  # Recherche la tâche correspondant à l'identifiant fourni.
        if task is None or task.family_code != member.family_code:  # Vérifie que la tâche appartient à la famille connectée.
            raise HTTPException(status_code=404, detail=f"La tâche avec l'identifiant {id} est introuvable")  # Renvoie une erreur claire si la tâche n'existe pas.
        session.delete(task)  # Supprime la tâche de la session.
        session.commit()  # Enregistre la suppression dans la base de données.
    return {"message": "Tâche supprimée", "id": id}  # Renvoie une confirmation avec l'identifiant supprimé.
