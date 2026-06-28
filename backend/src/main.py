from datetime import timedelta
import re
from flask import Flask,request, jsonify
import mysql.connector
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from decimal import Decimal
import os

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "dev-flask-secret")
app.config["JWT_TOKEN_LOCATION"] = ["headers"] 
app.config["JWT_HEADER_NAME"] = "Authorization"
app.config["JWT_HEADER_TYPE"] = "Bearer"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)
CORS(app,
     resources={r"/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}},
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     always_send=True
)
jwt = JWTManager(app)

def get_db_connection(host='localhost', user='root', password='', db='apoteka_wsit'):
    return mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        db=db
    )

def validan_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_admin():
    claims = get_jwt() or {}
    return claims.get("role") == "administrator"

def is_seller():
    claims = get_jwt() or {}
    return claims.get("role") == "prodavac"

def is_buyer():
    claims = get_jwt() or {}
    return claims.get("role") == "kupac"

def zahteva_admina():
    if not is_admin():
        return jsonify({"message": "Zabranjena akcija: samo za admine"}), 403
    return None

def pretrazi_korisnika_po_id(cursor, user_id):
    cursor.execute("SELECT id, username, email, godina_rodjenja, profilna_slika, money, role, created_at FROM users WHERE id=%s", (user_id,))
    return cursor.fetchone()

def pretrazi_proizvod_po_id(cursor, product_id):
    cursor.execute("SELECT * FROM products WHERE id=%s", (product_id,))
    return cursor.fetchone()


@app.route('/products', methods=['GET'])
@jwt_required()
def svi_proizvodi():
    mydb = get_db_connection()
    cursor = mydb.cursor(dictionary=True)

    cursor.execute("""
        SELECT p.*,
               u.username AS seller_username
        FROM products p
        LEFT JOIN users u ON u.id = p.seller_id
    """)
    products = cursor.fetchall()

    cursor.close()
    mydb.close()

    return jsonify({
        'products': products,
        'message': 'Proizvodi su fetchovani iz baze!'
    }), 200

@app.route('/products/add', methods=['POST'])
@jwt_required()
def dodaj_proizvod():
    claims = get_jwt()
    if claims.get("role") not in ("prodavac", "administrator"):
        return jsonify({"message": "Zabranjen pristup"}), 403

    data = request.get_json(silent=True) or {}

    seller_id = data.get("seller_id")
    naziv = data.get("naziv")
    opis = data.get("opis", "")
    cena = data.get("cena")
    discount_percent = data.get("discount_percent", 0)
    stock = data.get("stock", 0)

    if naziv is None or str(naziv).strip() == "" or cena is None:
        return jsonify({"message": "naziv i cena su obavezni"}), 400

    naziv = str(naziv).strip()
    opis = "" if opis is None else str(opis).strip()

    if len(naziv) < 3:
        return jsonify({"message": "Naziv treba da sadrzi makar 3 karaktera"}), 400

    if len(naziv) > 255:
        return jsonify({"message": "Naziv je predugacak"}), 400
    
    if len(opis) > 5000:
        return jsonify({"message": "Opis je predugacak"}), 400

    if claims.get("role") == "prodavac":
        seller_id = int(get_jwt_identity())
    else:
        if not seller_id:
            return jsonify({"message": "seller_id je obavezan za admina"}), 400

    try:
        cena = float(cena)
        discount_percent = float(discount_percent)
        stock = int(stock)
        seller_id = int(seller_id)
    except (TypeError, ValueError):
        return jsonify({"message": "Neispravan tip podataka (cena/discount/stock/seller_id)"}), 400

    if cena < 0:
        return jsonify({"message": "cena ne moze biti negativna"}), 400
    if discount_percent < 0 or discount_percent > 100:
        return jsonify({"message": "discount_percent mora biti 0-100"}), 400
    if stock < 0:
        return jsonify({"message": "stock ne moze biti negativan"}), 400
    if seller_id <= 0:
        return jsonify({"message": "seller_id nije validan"}), 400

    mydb = get_db_connection()
    cursor = mydb.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, role FROM users WHERE id=%s", (seller_id,))
        s = cursor.fetchone()
        if not s:
            return jsonify({"message": "Prodavac ne postoji"}), 404
        if s.get("role") not in ("prodavac", "administrator"):
            return jsonify({"message": "seller_id mora biti prodavac"}), 400

        cursor.execute(
            "INSERT INTO products (seller_id, naziv, opis, cena, discount_percent, stock) VALUES (%s, %s, %s, %s, %s, %s)",
            (seller_id, naziv, opis, cena, discount_percent, stock)
        )
        mydb.commit()
        return jsonify({"message": "Proizvod dodat", "product_id": cursor.lastrowid}), 201
    
    except Exception as e:

        mydb.rollback()
        return jsonify({"message": "DB greska", "greska": str(e)}), 500
    finally:

        cursor.close()
        mydb.close()

@app.delete("/products/delete/<int:product_id>")
@jwt_required()
def products_delete(product_id):
    claims = get_jwt() or {}
    role = claims.get("role")
    user_id = get_jwt_identity()

    if role not in ("administrator", "prodavac"):
        return jsonify({"message": "Zabranjen pristup"}), 403

    mydb = get_db_connection()
    cursor = mydb.cursor(dictionary=True)

    try:
        product = pretrazi_proizvod_po_id(cursor, product_id)
        if not product:
            return jsonify({"message": "Proizvod nije pronadjen"}), 404

        if role == "prodavac" and int(product["seller_id"]) != int(user_id):
            return jsonify({"message": "Zabranjen pristup"}), 403

        cursor.execute("DELETE FROM cart_items WHERE product_id=%s", (product_id,))
        cursor.execute("DELETE FROM comments WHERE product_id=%s", (product_id,))

        try:
            cursor.execute("DELETE FROM products WHERE id=%s", (product_id,))
            mydb.commit()
            return jsonify({"message": "Proizvod obrisan"}), 200
        except Exception as e:
            mydb.rollback()
            msg = str(e)
            if "Cannot delete or update a parent row" in msg or "IntegrityError" in msg:
                return jsonify({"message": "Ne moze brisanje: proizvod je vec kupljen"}), 400
            return jsonify({"message": "Greska pri brisanju proizvoda", "error": msg}), 500

    except Exception as e:
        mydb.rollback()
        return jsonify({"message": "Greska pri brisanju proizvoda", "error": str(e)}), 500

    finally:
        cursor.close()
        mydb.close()

def ensure_admin_seed():
    mydb = get_db_connection()
    try:
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT id FROM users WHERE username=%s", ("admin",))
        if cursor.fetchone():
            return

        pw_hash = generate_password_hash("admin")
        cursor.execute("INSERT INTO users (username, password_hash, email, godina_rodjenja, profilna_slika, money, role) VALUES (%s,%s,%s,%s,%s,%s,%s)", 
                       ("admin", pw_hash, "admin@example.com", 2000, "", Decimal("0.00"), "administrator"))
        mydb.commit()
        print("Seedovan admin/admin")
    finally:
        mydb.close()

@app.route("/register", methods=["POST"])
@jwt_required(optional=True)
def register():
    data = request.get_json(silent=True) or {}

    username = data.get("username")
    password = data.get("password")
    email = data.get("email")
    godina = data.get("godinaRodjenja")
    slika = data.get("profilnaSlika", "")
    role = data.get("role")

    if username is None or str(username).strip() == "" or not password or not email or godina is None or godina == "" or not role:
        return jsonify({"message": "Nisu popunjena sva polja"}), 400

    username = str(username).strip()
    email = str(email).strip()
    slika = "" if slika is None else str(slika).strip()

    if len(username) < 3:
        return jsonify({"message": "Username mora imati bar 3 karaktera"}), 400
    if len(password) < 4:
        return jsonify({"message": "Lozinka mora imati bar 4 karaktera"}), 400

    if role == "administrator":
        claims = get_jwt() or {}
        if claims.get("role") != "administrator":
            return jsonify({"message": "Samo admin moze da napravi jos jednog admina!"}), 403

    if not validan_email(email):
        return jsonify({"message": "Email nije validan!"}), 400

    try:
        godina = int(godina)
    except:
        return jsonify({"message": "Godina rodjenja nije broj!"}), 400

    if godina < 1900 or godina > 2026:
        return jsonify({"message": "Godina rodjenja nije validna"}), 400

    if role != "administrator" and role not in ("kupac", "prodavac"):
        return jsonify({"message": "Uloga koju ste izabrali nije validna!"}), 400

    pw_hash = generate_password_hash(password)

    mydb = get_db_connection()
    try:
        cursor = mydb.cursor(dictionary=True)

        cursor.execute("SELECT id FROM users WHERE username=%s", (username,))
        if cursor.fetchone():
            return jsonify({"message": "Username vec postoji!"}), 409

        cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
        if cursor.fetchone():
            return jsonify({"message": "Email vec postoji!"}), 409

        cursor.execute("""
            INSERT INTO users (username, password_hash, email, godina_rodjenja, profilna_slika, money, role)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (username, pw_hash, email, godina, slika, Decimal("0.00"), role))

        mydb.commit()
        return jsonify({"message": "Korisnik registrovan"}), 201
    except mysql.connector.Error as e:
        mydb.rollback()
        return jsonify({"message": "DB error", "error": str(e)}), 500
    finally:
        mydb.close()

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    if username is None or str(username).strip() == "" or not password:
        return jsonify({"message": "Nisu popunjena sva polja!"}), 400

    username = str(username).strip()

    if len(username) < 3:
        return jsonify({"message": "Username mora imati bar 3 karaktera"}), 400
    if len(password) < 4:
        return jsonify({"message": "Lozinka mora imati bar 4 karaktera"}), 400

    mydb = get_db_connection()
    try:
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT id, username, password_hash, role FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()
        if not user:
            return jsonify({"message": "Pogresno korisnicko ime ili lozinka!"}), 401

        if not check_password_hash(user["password_hash"], password):
            return jsonify({"message": "Pogresno korisnicko ime ili lozinka!"}), 401

        token = create_access_token(
            identity=str(user["id"]),
            additional_claims={"role": user["role"], "username": user["username"]}
        )
        return jsonify({
            "token": token,
            "role": user["role"],
            "username": user["username"],
            "user_id": user["id"]
        }), 200
    finally:
        mydb.close()


@app.get("/profile/<username>")
@jwt_required()
def profile_get(username):
    claims = get_jwt() or {}
    identity = get_jwt_identity() 
    role = claims.get("role")

    mydb = get_db_connection()
    cursor = mydb.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, username, email, godina_rodjenja, profilna_slika, money, role, created_at FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()
        if not user:
            return jsonify({"message": "Korisnik ne postoji"}), 404

        if role == "administrator":
            pass
        else:
            if str(identity) != str(user["id"]) and str(identity) != str(user["username"]):
                return jsonify({"message": "Nemate dozvolu da vidite ovaj profil"}), 403

        cursor.execute("""
            SELECT
                o.id AS order_id,
                o.created_at AS order_date,
                o.total,
                oi.product_id,
                oi.quantity,
                oi.naziv_snapshot AS naziv,
                oi.price_snapshot AS cena,
                oi.discount_percent_snapshot AS discount_percent
            FROM orders o
            JOIN order_items oi ON oi.order_id = o.id
            WHERE o.buyer_id = %s
            ORDER BY o.created_at DESC
        """, (user["id"],))
        kupovine = cursor.fetchall()

        return jsonify({"user": user, "kupovine": kupovine}), 200

    finally:
        cursor.close()
        mydb.close()

@app.put("/profile/update")
@jwt_required()
def profile_update():
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    email = data.get("email")
    godina = data.get("godina_rodjenja")
    profilna = data.get("profilna_slika")
    new_password = data.get("password")

    fields = []
    params = []

    mydb = get_db_connection()
    cursor = mydb.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, email FROM users WHERE id=%s", (user_id,))
        me = cursor.fetchone()
        if not me:
            return jsonify({"message": "Korisnik ne postoji"}), 404

        if email is not None:
            email = str(email).strip()
            if not email or not validan_email(email):
                return jsonify({"message": "Neispravan email format"}), 400
            cursor.execute("SELECT id FROM users WHERE email=%s AND id<>%s", (email, user_id))
            if cursor.fetchone():
                return jsonify({"message": "Email je vec zauzet"}), 409
            fields.append("email=%s")
            params.append(email)

        if godina is not None:
            try:
                godina_int = int(godina)
            except (TypeError, ValueError):
                return jsonify({"message": "Godina rodjenja mora biti ceo broj"}), 400
            if godina_int < 1900 or godina_int > 2026:
                return jsonify({"message": "Godina rodjenja mora biti u opsegu 1900–2026"}), 400
            fields.append("godina_rodjenja=%s")
            params.append(godina_int)

        if profilna is not None:
            profilna = str(profilna).strip()
            fields.append("profilna_slika=%s")
            params.append(profilna)

        if new_password:
            new_password = str(new_password)
            if len(new_password) < 4:
                return jsonify({"message": "Lozinka je prekratka"}), 400
            fields.append("password_hash=%s")
            params.append(generate_password_hash(new_password))

        if not fields:
            return jsonify({"message": "Nema sta da se apdejtuje"}), 400

        params.append(user_id)

        cursor.execute(f"UPDATE users SET {', '.join(fields)} WHERE id=%s", tuple(params))
        mydb.commit()

        updated = pretrazi_korisnika_po_id(cursor, user_id)
        return jsonify({"message": "Profil ucitan", "user": updated}), 200
    finally:
        cursor.close()
        mydb.close()

@app.route("/products/update/<int:product_id>", methods=["PUT"])
@jwt_required()
def products_update(product_id):
    claims = get_jwt() or {}
    role = claims.get("role")
    user_id = int(get_jwt_identity())

    if role not in ("prodavac", "administrator"):
        return jsonify({"message": "Nemate dozvolu"}), 403

    data = request.get_json(silent=True) or {}

    if "cena" in data:
        try:
            cena = float(data["cena"])
        except (TypeError, ValueError):
            return jsonify({"message": "Cena mora biti broj"}), 400
        if cena < 0:
            return jsonify({"message": "Cena ne moze biti negativna"}), 400

    if "stock" in data:
        try:
            stock = int(data["stock"])
        except (TypeError, ValueError):
            return jsonify({"message": "Kolicina (stock) mora biti ceo broj"}), 400
        if stock < 0:
            return jsonify({"message": "Kolicina na stanju ne moze biti negativna"}), 400

    if "discount_percent" in data:
        try:
            discount = float(data["discount_percent"])
        except (TypeError, ValueError):
            return jsonify({"message": "Popust mora biti broj"}), 400
        if discount < 0 or discount > 100:
            return jsonify({"message": "Popust mora biti u opsegu 0-100"}), 400

    if "naziv" in data:
        naziv = str(data["naziv"]).strip()
        if not naziv:
            return jsonify({"message": "Naziv ne moze biti prazan"}), 400

    if "opis" in data and data["opis"] is not None:
        opis = str(data["opis"]).strip()
        if len(opis) > 5000:
            return jsonify({"message": "Opis je predugacak"}), 400

    mydb = get_db_connection()
    cursor = mydb.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, seller_id FROM products WHERE id=%s", (product_id,))
        p = cursor.fetchone()
        if not p:
            return jsonify({"message": "Proizvod ne postoji"}), 404

        if role != "administrator" and int(p["seller_id"]) != user_id:
            return jsonify({"message": "Mozete menjati samo svoje proizvode"}), 403

        fields = []
        values = []

        if "naziv" in data:
            fields.append("naziv=%s")
            values.append(str(data["naziv"]).strip())
        if "opis" in data:
            fields.append("opis=%s")
            values.append(data["opis"])
        if "cena" in data:
            fields.append("cena=%s")
            values.append(float(data["cena"]))
        if "discount_percent" in data:
            fields.append("discount_percent=%s")
            values.append(float(data["discount_percent"]))
        if "stock" in data:
            fields.append("stock=%s")
            values.append(int(data["stock"]))

        if not fields:
            return jsonify({"message": "Nema izmena"}), 400

        values.append(product_id)
        cursor.execute(f"UPDATE products SET {', '.join(fields)} WHERE id=%s", tuple(values))
        mydb.commit()

        return jsonify({"message": "Proizvod azuriran"}), 200
    finally:
        cursor.close()
        mydb.close()

@app.route("/cart/add/<product_id>", methods=["POST"])
@jwt_required()
def cart_add(product_id):
    user_id = int(get_jwt_identity())

    try:
        product_id_int = int(product_id)
    except (TypeError, ValueError):
        return jsonify({"message": "Neispravan product_id"}), 400

    mydb = get_db_connection()
    cursor = mydb.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, stock FROM products WHERE id=%s", (product_id_int,))
        p = cursor.fetchone()
        if not p:
            return jsonify({"message": "Proizvod ne postoji"}), 404
        if int(p["stock"]) <= 0:
            return jsonify({"message": "Nema na stanju"}), 400

        cursor.execute("SELECT quantity FROM cart_items WHERE user_id=%s AND product_id=%s", (user_id, product_id_int))
        row = cursor.fetchone()

        if row:
            new_q = int(row["quantity"]) + 1
            if new_q > int(p["stock"]):
                return jsonify({"message": "Nema dovoljno na stanju"}), 400
            cursor.execute("UPDATE cart_items SET quantity=%s WHERE user_id=%s AND product_id=%s", (new_q, user_id, product_id_int))
        else:
            cursor.execute("INSERT INTO cart_items (user_id, product_id, quantity) VALUES (%s, %s, %s)", (user_id, product_id_int, 1))

        mydb.commit()
        return jsonify({"message": "Dodato u korpu"}), 200
    finally:
        cursor.close()
        mydb.close()

@app.route("/cart", methods=["GET"])
@jwt_required()
def cart_get():
    buyer_id = int(get_jwt_identity())
    user_id = int(get_jwt_identity())

    mydb = get_db_connection()
    cursor = mydb.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT
              ci.product_id,
              ci.quantity,
              p.naziv,
              p.cena,
              p.discount_percent,
              p.stock,
              p.seller_id
            FROM cart_items ci
            JOIN products p ON p.id = ci.product_id
            WHERE ci.user_id=%s
        """, (user_id,))
        items = cursor.fetchall()

        total = Decimal("0.00")
        for it in items:
            sid = int(it.get("seller_id", -1))
            if int(it["seller_id"]) == buyer_id:
                mydb.rollback()
                return jsonify({"message":"Ne mozete kupiti svoj proizvod."}), 400

            cena = Decimal(str(it["cena"]))
            dp = Decimal(str(it.get("discount_percent", 0)))

            unit = (cena * (Decimal("100") - dp) / Decimal("100")).quantize(Decimal("0.01"))
            line = (unit * Decimal(int(it["quantity"]))).quantize(Decimal("0.01"))

            it["unit_price"] = str(unit)
            it["line_total"] = str(line)

            total += line

        return jsonify({"items": items, "total": total}), 200
    finally:
        cursor.close()
        mydb.close()

@app.route("/cart/update/<product_id>", methods=["PUT"])
@jwt_required()
def cart_update(product_id):
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}

    try:
        product_id_int = int(product_id)
    except (TypeError, ValueError):
        return jsonify({"message": "Neispravan product_id"}), 400

    try:
        qty = int(data.get("quantity", 0))
    except (TypeError, ValueError):
        return jsonify({"message": "Kolicina mora biti ceo broj"}), 400

    if qty < 1:
        return jsonify({"message": "Kolicina mora biti >= 1"}), 400

    mydb = get_db_connection()
    cursor = mydb.cursor(dictionary=True)
    try:
        cursor.execute("SELECT stock FROM products WHERE id=%s", (product_id_int,))
        p = cursor.fetchone()
        if not p:
            return jsonify({"message": "Proizvod ne postoji"}), 404
        if qty > int(p["stock"]):
            return jsonify({"message": "Nema dovoljno na stanju"}), 400

        cursor.execute("SELECT quantity FROM cart_items WHERE user_id=%s AND product_id=%s", (user_id, product_id_int))
        if not cursor.fetchone():
            return jsonify({"message": "Proizvod nije u korpi"}), 404

        cursor.execute("UPDATE cart_items SET quantity=%s WHERE user_id=%s AND product_id=%s", (qty, user_id, product_id_int))

        mydb.commit()
        return jsonify({"message": "Kolicina azurirana"}), 200
    finally:
        cursor.close()
        mydb.close()

@app.route("/cart/delete/<int:product_id>", methods=["DELETE"])
@jwt_required()
def cart_delete(product_id):
    user_id = int(get_jwt_identity())

    mydb = get_db_connection()
    cursor = mydb.cursor()
    try:
        cursor.execute("DELETE FROM cart_items WHERE user_id=%s AND product_id=%s", (user_id, product_id))
        mydb.commit()
        return jsonify({"message": "Obrisano iz korpe"}), 200
    finally:
        cursor.close()
        mydb.close()

@app.route("/checkout", methods=["POST"])
@jwt_required()
def checkout():
    buyer_id = int(get_jwt_identity())

    mydb = get_db_connection()
    cursor = mydb.cursor(dictionary=True)

    try:
        mydb.start_transaction()

        cursor.execute("""
            SELECT
              ci.product_id,
              ci.quantity,
              p.seller_id,
              p.naziv,
              p.cena,
              p.discount_percent,
              p.stock
            FROM cart_items ci
            JOIN products p ON p.id = ci.product_id
            WHERE ci.user_id=%s
            FOR UPDATE
        """, (buyer_id,))
        items = cursor.fetchall()

        if not items:
            mydb.rollback()
            return jsonify({"message": "Korpa je prazna"}), 400

        total = Decimal("0.00")
        seller_totals = {}

        for it in items:
            if int(it["seller_id"]) == buyer_id:
                mydb.rollback()
                return jsonify({"message": "Ne mozete kupiti sopstveni proizvod"}), 400

            try:
                qty = int(it["quantity"])
            except (TypeError, ValueError):
                mydb.rollback()
                return jsonify({"message": "Neispravna kolicina u korpi"}), 400

            if qty < 1:
                mydb.rollback()
                return jsonify({"message": "Neispravna kolicina u korpi"}), 400

            stock = int(it["stock"])
            if qty > stock:
                mydb.rollback()
                return jsonify({"message": f"Nema dovoljno na stanju za: {it['naziv']}"}), 400

            cena = Decimal(str(it["cena"] or 0))
            dp = Decimal(str(it["discount_percent"] or 0))
            if dp < 0 or dp > 100:
                mydb.rollback()
                return jsonify({"message": f"Neispravan popust za: {it['naziv']}"}), 400

            unit = (cena * (Decimal("100") - dp) / Decimal("100")).quantize(Decimal("0.01"))
            line = (unit * Decimal(qty)).quantize(Decimal("0.01"))

            total += line
            sid = int(it["seller_id"])
            seller_totals[sid] = seller_totals.get(sid, Decimal("0.00")) + line

        cursor.execute("SELECT money FROM users WHERE id=%s FOR UPDATE", (buyer_id,))
        buyer = cursor.fetchone()
        if not buyer:
            mydb.rollback()
            return jsonify({"message": "Kupac ne postoji"}), 404

        buyer_money = Decimal(str(buyer["money"] or 0))
        if buyer_money < total:
            mydb.rollback()
            return jsonify({"message": "Nemate dovoljno novca"}), 400

        cursor.execute(
            "UPDATE users SET money = money - %s WHERE id=%s",
            (total, buyer_id)
        )

        for sid, amount in seller_totals.items():
            cursor.execute(
                "UPDATE users SET money = money + %s WHERE id=%s",
                (amount, sid)
            )

        for proizvod in items:
            cursor.execute(
                "UPDATE products SET stock = stock - %s WHERE id=%s",
                (int(proizvod["quantity"]), int(proizvod["product_id"]))
            )

        cursor.execute(
            "INSERT INTO orders (buyer_id, total) VALUES (%s, %s)",
            (buyer_id, total)
        )
        order_id = cursor.lastrowid

        for proizvod in items:
            cursor.execute("""
                INSERT INTO order_items
                  (order_id, product_id, seller_id, naziv_snapshot, price_snapshot, discount_percent_snapshot, quantity)
                VALUES
                  (%s, %s, %s, %s, %s, %s, %s)
            """, (
                order_id,
                int(proizvod["product_id"]),
                int(proizvod["seller_id"]),
                proizvod["naziv"],
                Decimal(str(proizvod["cena"] or 0)),
                Decimal(str(proizvod["discount_percent"] or 0)),
                int(proizvod["quantity"])
            ))

        cursor.execute("DELETE FROM cart_items WHERE user_id=%s", (buyer_id,))

        cursor.execute("SELECT money FROM users WHERE id=%s", (buyer_id,))
        row = cursor.fetchone()
        new_money = row["money"] if row and row["money"] is not None else 0

        mydb.commit()
        return jsonify({
            "message": "Kupovina uspesna",
            "order_id": order_id,
            "total": str(total),
            "new_money": str(new_money)
        }), 200

    except Exception as e:
        mydb.rollback()
        return jsonify({"message": "Kupovina neuspesna", "error": str(e)}), 500

    finally:
        cursor.close()
        mydb.close()

        
@app.route("/products/<product_id>/comments", methods=["GET"])
def comments_list(product_id):
    try:
        pid = int(product_id)
    except (TypeError, ValueError):
        return jsonify({"message": "Neispravan product_id"}), 400

    mydb = get_db_connection()
    cursor = mydb.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id FROM products WHERE id=%s", (pid,))
        if not cursor.fetchone():
            return jsonify({"comments": []}), 200

        cursor.execute("""
            SELECT c.id, c.product_id, c.user_id, u.username,
                   c.content, c.created_at
            FROM comments c
            JOIN users u ON u.id = c.user_id
            WHERE c.product_id=%s
            ORDER BY c.created_at DESC
        """, (pid,))
        return jsonify({"comments": cursor.fetchall()}), 200
    finally:
        cursor.close()
        mydb.close()

@app.route("/products/<int:product_id>/comment", methods=["POST"])
@jwt_required()
def comment_add(product_id):
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    content = (data.get("content") or "").strip()

    if not content:
        return jsonify({"message": "Sadrzaj komentara je obavezan"}), 400

    mydb = get_db_connection()
    cursor = mydb.cursor(dictionary=True)
    try:
        product = pretrazi_proizvod_po_id(cursor, product_id)
        if not product:
            return jsonify({"message": "Proizvod nije pronadjen"}), 404

        cursor.execute("INSERT INTO comments (product_id, user_id, content, created_at) VALUES (%s, %s, %s, NOW())", (product_id, user_id, content))
        mydb.commit()
        return jsonify({"message": "Komentar dodat"}), 201
    finally:
        cursor.close()
        mydb.close()

@app.route("/products/<int:product_id>/comment/update/<int:comment_id>", methods=["PUT"])
@jwt_required()
def comment_update(product_id, comment_id):
    user_id = get_jwt_identity()
    claims = get_jwt() or {}
    role = claims.get("role")

    data = request.get_json() or {}
    content = (data.get("content") or "").strip()
    if not content:
        return jsonify({"message": "Sadrzaj komentaraje obavezan!"}), 400

    mydb = get_db_connection()
    cursor = mydb.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM comments WHERE id=%s AND product_id=%s", (comment_id, product_id))
        comment = cursor.fetchone()
        if not comment:
            return jsonify({"message": "Komentar nije pronadjen"}), 404

        if int(comment["user_id"]) != int(user_id) and role != "administrator":
            cursor.execute("SELECT seller_id FROM products WHERE id=%s", (product_id,))
            p = cursor.fetchone()
            if not p or int(p["seller_id"]) != int(user_id):
                return jsonify({"message": "Zabranjen pristup"}), 403

        cursor.execute("UPDATE comments SET content=%s WHERE id=%s", (content, comment_id))
        mydb.commit()
        return jsonify({"message": "Komentar azuriran"}), 200
    finally:
        cursor.close()
        mydb.close()

@app.route("/products/<product_id>/comment/delete/<int:comment_id>", methods=["DELETE"])
@jwt_required()
def comment_delete(product_id, comment_id):
    user_id = get_jwt_identity()
    claims = get_jwt() or {}
    role = claims.get("role")

    mydb = get_db_connection()
    cursor = mydb.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM comments WHERE id=%s AND product_id=%s", (comment_id, product_id))
        comment = cursor.fetchone()
        if not comment:
            return jsonify({"message": "Komentar nije pronadjen"}), 404

        if role == "administrator":
            pass
        elif int(comment["user_id"]) == int(user_id):
            pass
        else:
            cursor.execute("SELECT seller_id FROM products WHERE id=%s", (product_id,))
            p = cursor.fetchone()
            if not p or int(p["seller_id"]) != int(user_id):
                return jsonify({"message": "Zabranjen pristup"}), 403

        cursor.execute("DELETE FROM comments WHERE id=%s", (comment_id,))
        mydb.commit()
        return jsonify({"message": "Komentar obrisan"}), 200
    finally:
        cursor.close()
        mydb.close()

@app.route("/admin/users/<user_id>/money/add", methods=["POST"])
@jwt_required()
def admin_money_add(user_id):
    guard = zahteva_admina()
    if guard:
        return guard

    data = request.get_json() or {}
    amount = data.get("amount")

    try:
        amount = float(amount)
    except:
        return jsonify({"message": "Kolicina mora da bude broj"}), 400
    if amount <= 0:
        return jsonify({"message": "Kolicina mora da bude veca od 0"}), 400

    mydb = get_db_connection()
    cursor = mydb.cursor(dictionary=True)
    try:
        cursor.execute("UPDATE users SET money = money + %s WHERE id=%s", (amount, user_id))
        mydb.commit()
        user = pretrazi_korisnika_po_id(cursor, user_id)
        if not user:
            return jsonify({"message": "Korisnik nije pronadjen"}), 404
        return jsonify({"message": "Pare su dodate", "user": user}), 200
    finally:
        cursor.close()
        mydb.close()

@app.route("/admin/users", methods=["GET"])
@jwt_required()
def admin_users_list():
    guard = zahteva_admina()
    if guard:
        return guard

    mydb = get_db_connection()
    cursor = mydb.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, username, email, godina_rodjenja, profilna_slika, money, role, created_at FROM users ORDER BY id DESC")
        return jsonify({"users": cursor.fetchall()}), 200
    finally:
        cursor.close()
        mydb.close()

@app.route("/admin/users/add", methods=["POST"])
@jwt_required()
def admin_add_user():
    claims = get_jwt() or {}
    if claims.get("role") != "administrator":
        return jsonify({"message": "Samo admin moze da dodaje korisnike!"}), 403

    data = request.get_json() or {}

    username = data.get("username")
    password = data.get("password")
    email = data.get("email")
    godina = data.get("godina_rodjenja")
    slika = data.get("profilna_slika", "")
    role = data.get("role")

    if not username or not password or not email or godina is None or godina == "" or not role:
        return jsonify({"message": "Nisu popunjena sva polja"}), 400

    if not validan_email(email):
        return jsonify({"message": "Email nije validan!"}), 400

    try:
        godina = int(godina)
    except:
        return jsonify({"message": "Godina rodjenja nije broj!"}), 400

    if godina < 1900 or godina > 2026:
        return jsonify({"message": "Godina rodjenja nije validna"}), 400

    if role not in ("kupac", "prodavac", "administrator"):
        return jsonify({"message": "Uloga nije validna!"}), 400

    pw_hash = generate_password_hash(password)

    mydb = get_db_connection()
    try:
        cursor = mydb.cursor(dictionary=True)

        cursor.execute("SELECT id FROM users WHERE username=%s OR email=%s", (username, email))
        if cursor.fetchone():
            return jsonify({"message": "Username ili Email vec postoji!"}), 409

        cursor.execute("""
            INSERT INTO users (username, password_hash, email, godina_rodjenja, profilna_slika, money, role)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (username, pw_hash, email, godina, slika, Decimal("0.00"), role))

        mydb.commit()
        return jsonify({"message": "Korisnik dodat"}), 201
    except mysql.connector.Error as e:
        mydb.rollback()
        return jsonify({"message": "DB error", "error": str(e)}), 500
    finally:
        mydb.close()

@app.route("/admin/users/update/<int:user_id>", methods=["PUT"])
@jwt_required()
def admin_users_update(user_id):
    guard = zahteva_admina()
    if guard:
        return guard

    data = request.get_json(silent=True) or {}

    allowed_cols = {
        "username": "username",
        "email": "email",
        "godina_rodjenja": "godina_rodjenja",
        "profilna_slika": "profilna_slika",
        "money": "money",
        "role": "role",
    }

    mydb = get_db_connection()
    cursor = mydb.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id FROM users WHERE id=%s", (user_id,))
        if not cursor.fetchone():
            return jsonify({"message": "Korisnik nije pronadjen"}), 404

        fields = []
        params = []

        for k, col in allowed_cols.items():
            if k not in data or data[k] is None:
                continue

            val = data[k]

            if k == "role":
                if val not in ("kupac", "prodavac", "administrator"):
                    return jsonify({"message": "Uloga mora biti kupac/prodavac/administrator"}), 400

            if k == "money":
                try:
                    val = float(val)
                except:
                    return jsonify({"message": "Pare moraju biti broj"}), 400
                if val < 0:
                    return jsonify({"message": "Pare ne mogu biti negativne"}), 400

            if k == "godina_rodjenja":
                try:
                    val = int(val)
                except:
                    return jsonify({"message": "Godina rodjenja mora biti broj"}), 400
                if val < 1900 or val > 2026:
                    return jsonify({"message": "Godina rodjenja nije validna"}), 400

            if k == "email":
                val = str(val).strip()
                if not validan_email(val):
                    return jsonify({"message": "Neispravan email format"}), 400
                cursor.execute("SELECT id FROM users WHERE email=%s AND id<>%s", (val, user_id))
                if cursor.fetchone():
                    return jsonify({"message": "Email je vec zauzet"}), 409

            if k == "username":
                val = str(val).strip()
                if not val:
                    return jsonify({"message": "Username ne moze biti prazan"}), 400
                if len(val) < 3:
                    return jsonify({"message": "Username mora imati bar 3 karaktera"}), 400
                cursor.execute("SELECT id FROM users WHERE username=%s AND id<>%s", (val, user_id))
                if cursor.fetchone():
                    return jsonify({"message": "Username je vec zauzet"}), 409

            fields.append(f"{col}=%s")
            params.append(val)

        if "password" in data and data["password"] is not None:
            pw = str(data["password"])
            if len(pw) < 6:
                return jsonify({"message": "Lozinka mora imati bar 6 karaktera"}), 400
            fields.append("password_hash=%s")
            params.append(generate_password_hash(pw))

        if not fields:
            return jsonify({"message": "Nema sta da se izmeni"}), 400

        params.append(user_id)
        cursor.execute(
            f"UPDATE users SET {', '.join(fields)} WHERE id=%s",
            tuple(params)
        )
        mydb.commit()

        user = pretrazi_korisnika_po_id(cursor, user_id)
        if user and "password_hash" in user:
            user.pop("password_hash")

        return jsonify({"message": "Korisnik izmenjen", "user": user}), 200
    finally:
        cursor.close()
        mydb.close()

@app.route("/admin/users/delete/<int:user_id>", methods=["DELETE"])
@jwt_required()
def admin_users_delete(user_id):
    claims = get_jwt()
    if claims.get("role") != "administrator":
        return jsonify({"error": "Zabranjen pristup"}), 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT role FROM users WHERE id=%s", (user_id,))
        u = cursor.fetchone()
        if not u:
            return jsonify({"error": "User not found"}), 404
        if u["role"] == "administrator":
            return jsonify({"error": "Ne mozes obrisati admin korisnika."}), 400

        cursor.execute("DELETE FROM cart_items WHERE user_id=%s", (user_id,))
        cursor.execute("DELETE FROM comments WHERE user_id=%s", (user_id,))

        cursor.execute(
            "DELETE FROM order_items WHERE order_id IN (SELECT id FROM orders WHERE buyer_id=%s)",
            (user_id,)
        )
        cursor.execute("DELETE FROM orders WHERE buyer_id=%s", (user_id,))

        cursor.execute("SELECT id FROM products WHERE seller_id=%s", (user_id,))
        seller_products = [row["id"] for row in cursor.fetchall()]

        if seller_products:
            placeholders = ",".join(["%s"] * len(seller_products))

            cursor.execute(f"DELETE FROM comments WHERE product_id IN ({placeholders})", tuple(seller_products))
            cursor.execute(f"DELETE FROM cart_items WHERE product_id IN ({placeholders})", tuple(seller_products))
            cursor.execute(f"DELETE FROM order_items WHERE product_id IN ({placeholders})", tuple(seller_products))
            cursor.execute("DELETE FROM products WHERE seller_id=%s", (user_id,))

        cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))

        conn.commit()
        return jsonify({"message": "Korisnik obrisan"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

@app.route("/admin/products", methods=["GET"])
@jwt_required()
def admin_products_list():
    claims = get_jwt()
    if claims.get("role") != "administrator":
        return jsonify({"error": "Zabranjen pristup"}), 403

    mydb = get_db_connection()
    cursor = mydb.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT p.*, u.username AS seller_username
            FROM products p
            JOIN users u ON u.id = p.seller_id
            ORDER BY p.id DESC
        """)
        return jsonify({"products": cursor.fetchall()}), 200
    finally:
        cursor.close()
        mydb.close()

@app.route("/admin/products", methods=["PUT"])
@jwt_required()
def admin_products_update():
    claims = get_jwt()
    if claims.get("role") != "administrator":
        return jsonify({"error": "Zabranjen pristup"}), 403

    data = request.get_json() or {}
    pid = data.get("id", None)

    if not pid:
        return jsonify({"error": "Nedostaje product id"}), 400

    fields = []
    values = []

    if "naziv" in data:
        fields.append("naziv=%s")
        values.append(data.get("naziv"))

    if "opis" in data:
        fields.append("opis=%s")
        values.append(data.get("opis"))

    if "cena" in data:
        fields.append("cena=%s")
        values.append(data.get("cena"))

    if "stock" in data:
        fields.append("stock=%s")
        values.append(data.get("stock"))

    if "discount_percent" in data:
        fields.append("discount_percent=%s")
        values.append(data.get("discount_percent"))

    if "seller_id" in data:
        fields.append("seller_id=%s")
        values.append(data.get("seller_id"))

    if len(fields) == 0:
        return jsonify({"error": "Nema polja za azuriranje"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT id FROM products WHERE id=%s", (pid,))
        p = cursor.fetchone()
        if not p:
            return jsonify({"error": "Proizvod nije pronadjen"}), 404

        values.append(pid)
        sql = "UPDATE products SET " + ", ".join(fields) + " WHERE id=%s"
        cursor.execute(sql, tuple(values))
        conn.commit()

        return jsonify({"message": "Proizvod azuriran"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


@app.route("/admin/products/<int:pid>", methods=["DELETE"])
@jwt_required()
def admin_products_delete(pid):
    claims = get_jwt()
    if claims.get("role") != "administrator":
        return jsonify({"error": "Zabranjen pristup"}), 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT id FROM products WHERE id=%s", (pid,))
        p = cursor.fetchone()
        if not p:
            return jsonify({"error": "Proizvod nije pronadjen"}), 404
        cursor.execute("DELETE FROM cart_items WHERE product_id=%s", (pid,))
        cursor.execute("DELETE FROM order_items WHERE product_id=%s", (pid,))
        cursor.execute("DELETE FROM comments WHERE product_id=%s", (pid,))
        cursor.execute("DELETE FROM products WHERE id=%s", (pid,))

        conn.commit()
        return jsonify({"message": "Proizvod obrisan"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

@app.route("/admin/comments", methods=["GET"])
@jwt_required()
def admin_comments_list():
    guard = zahteva_admina()
    if guard:
        return guard

    mydb = get_db_connection()
    cursor = mydb.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT 
                c.id,
                c.product_id,
                c.user_id,
                u.username,
                p.naziv AS product_name,
                c.content,
                c.created_at
            FROM comments c
            JOIN users u ON u.id = c.user_id
            JOIN products p ON p.id = c.product_id
            ORDER BY c.id DESC
        """)
        return jsonify({"komentari": cursor.fetchall()}), 200
    finally:
        cursor.close()
        mydb.close()

@app.route("/admin/comments/<int:comment_id>", methods=["PUT"])
@jwt_required()
def admin_comments_update(comment_id):
    claims = get_jwt()
    if claims.get("role") != "administrator":
        return jsonify({"error": "Zabranjen pristup"}), 403

    data = request.get_json() or {}
    content = (data.get("content") or "").strip()

    if not content:
        return jsonify({"error": "Sadrzaj komentara je obavezan"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT id FROM comments WHERE id=%s", (comment_id,))
        c = cursor.fetchone()
        if not c:
            return jsonify({"error": "Comment not found"}), 404

        cursor.execute("UPDATE comments SET content=%s WHERE id=%s", (content, comment_id))
        conn.commit()

        return jsonify({"message": "Komentar azuriran"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


@app.route("/admin/comments/<int:comment_id>", methods=["DELETE"])
@jwt_required()
def admin_comments_delete(comment_id):
    claims = get_jwt()
    if claims.get("role") != "administrator":
        return jsonify({"error": "Zabranjen pristup"}), 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT id FROM comments WHERE id=%s", (comment_id,))
        c = cursor.fetchone()
        if not c:
            return jsonify({"error": "Komentar nije pronadjen"}), 404
        
        cursor.execute("DELETE FROM comments WHERE id=%s", (comment_id,))
        conn.commit()

        return jsonify({"message": "Comment deleted"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

@app.route("/money/add", methods=["POST"])
@jwt_required()
def money_add():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    amount = data.get("amount")

    try:
        amount = float(amount)
    except:
        return jsonify({"message": "Kolicina mora da bude broj"}), 400

    if amount <= 0:
        return jsonify({"message": "Kolicina mora da bude veca od 0"}), 400

    mydb = get_db_connection()
    cursor = mydb.cursor(dictionary=True)
    try:
        cursor.execute("UPDATE users SET money = money + %s WHERE id=%s", (amount, user_id))
        mydb.commit()

        cursor.execute("SELECT money FROM users WHERE id=%s", (user_id,))
        u = cursor.fetchone()
        return jsonify({"message": "Pare su dodate!", "money": u["money"]}), 200
    finally:
        cursor.close()
        mydb.close()

if __name__ == "__main__":
    ensure_admin_seed()
    app.run(debug=True)
