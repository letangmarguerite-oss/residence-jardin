from flask import Flask, render_template, request, redirect, url_for, flash
from database import get_connection, add_absence, get_absences
import calendar
from datetime import date, datetime




app = Flask(__name__)
app.secret_key = "change_this_secret_key"

# Initialize database at startup
@app.template_filter('fr_date')
def fr_date(value):
    try:
        d = datetime.strptime(value, "%Y-%m-%d")
        return d.strftime("%d/%m/%Y")
    except:
        return value

# ---------------------------
# CALENDAR VIEW WITH NAVIGATION
# ---------------------------
@app.route("/calendar")
def calendar_view():
    MOIS_FR = {
        1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril", 5: "Mai", 6: "Juin",
        7: "Juillet", 8: "Août", 9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"
    }

    today = date.today()
    year = int(request.args.get("year", today.year))
    month = int(request.args.get("month", today.month))

    # 🔹 Récupérer les absences
    absences = get_absences()

    # 🔹 Générer le calendrier
    cal = calendar.monthcalendar(year, month)

    # 🔹 Charger les créneaux
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT resident, date, hour FROM slots")
    slots = c.fetchall()
    conn.close()

    # 🔹 Organiser les réservations par jour
    bookings = {}
    for slot in slots:
        resident = slot["resident"]
        date_value = slot["date"]
        hour = slot["hour"]

        y, m, d = map(int, date_value.split("-"))
        if y == year and m == month:
            if d not in bookings:
                bookings[d] = []
            bookings[d].append(f"{hour} — {resident}")

    # 🔹 Organiser les absences par jour
    absences_by_day = {}
    for a in absences:
        start = datetime.strptime(a["date_depart"], "%Y-%m-%d").date()
        end = datetime.strptime(a["date_retour"], "%Y-%m-%d").date()

        current = start
        while current <= end:
            if current.year == year and current.month == month:
                day = current.day
                if day not in absences_by_day:
                    absences_by_day[day] = []
                absences_by_day[day].append(a["resident"])
            current = current + timedelta(days=1)

    # 🔹 Navigation mois précédent / suivant
    prev_month = month - 1
    prev_year = year
    next_month = month + 1
    next_year = year

    if prev_month == 0:
        prev_month = 12
        prev_year -= 1

    if next_month == 13:
        next_month = 1
        next_year += 1

    return render_template(
        "calendar.html",
        cal=cal,
        month=month,
        year=year,
        month_name=MOIS_FR[month],
        bookings=bookings,
        absences_by_day=absences_by_day,   # 🔹 AJOUT IMPORTANT
        prev_month=prev_month,
        prev_year=prev_year,
        next_month=next_month,
        next_year=next_year
    )


# ---------------------------
# DATABASE HELPERS
# ---------------------------
def get_all_slots():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, resident, date, hour FROM slots ORDER BY date, hour")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows



def add_slot(resident, day, time_slot):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO slots (resident, date, hour) VALUES (%s, %s, %s)",
        (resident, day, time_slot)
    )
    conn.commit()
    cur.close()
    conn.close()


def delete_slot(slot_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM slots WHERE id = %s", (slot_id,))
    conn.commit()
    cur.close()
    conn.close()



# ---------------------------
# TIME SLOT GENERATOR (ADD THIS HERE)
# ---------------------------
def generate_time_slots():
    slots = []
    for hour in range(7, 23):  # 08:00 to 18:30
        slots.append(f"{hour:02d}:00")
        slots.append(f"{hour:02d}:30")
    return slots

# ---------------------------
# ROUTES
# ---------------------------
@app.route("/")
def index():
    slots = get_all_slots()
    return render_template("index.html", slots=slots)


@app.route("/add", methods=["GET", "POST"])

def add():
    preselected_day = request.args.get("preselected_day")

    if request.method == "POST":
        resident = request.form.get("resident", "").strip()
        day = request.form.get("day", "").strip()
        time_slot = request.form.get("time_slot", "").strip()

        if not resident or not day or not time_slot:
            flash("Veuillez remplir tous les champs.")
            return redirect(url_for("add"))

        add_slot(resident, day, time_slot)
        flash("Créneau ajouté avec succès.")
        return redirect(url_for("index"))

    return render_template(
        "add_slot.html",
        preselected_day=preselected_day,
        time_slots=generate_time_slots()
    )

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM slots WHERE id = %s", (id,))

    conn.commit()
    cur.close()
    conn.close()

    flash("Créneau supprimé")
    return redirect(url_for('index'))

@app.route("/absences", methods=["GET", "POST"])
def absences():
    if request.method == "POST":
        resident = request.form.get("resident", "").strip()
        date_depart = request.form.get("date_depart", "").strip()
        date_retour = request.form.get("date_retour", "").strip()

        if not resident or not date_depart or not date_retour:
            flash("Veuillez remplir tous les champs.")
            return redirect(url_for("absences"))

        add_absence(resident, date_depart, date_retour)
        flash("Absence enregistrée avec succès.")
        return redirect(url_for("absences"))

    absences_list = get_absences()
    return render_template("absences.html", absences=absences_list)


# ---------------------------
# RUN APP
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)
