
from flask import Flask, jsonify, request, Response
from pathlib import Path
import os
import time
import threading

# ==========================================
# 1. CONFIGURACION
# ==========================================

BASE = Path(r"C:\MAKO_PACS\control_movil")

COMMAND_FILE = BASE / "comando.txt"
STATUS_FILE = BASE / "estado.txt"
HEARTBEAT_FILE = BASE / "telefono_activo.txt"

PUERTO = 5001
IP_SERVIDOR = "10.23.146.1"

app = Flask(__name__)

command_lock = threading.Lock()
command_id = int(time.time() * 1000)

# ==========================================
# 2. LIMITES DE MOVIMIENTO
# ==========================================

LIMITS = {
    "J0": (-90, 90),
    "J1": (-90, 90),
    "J2": (-120, 120),
    "J3": (-120, 120),
    "J5": (-90, 90),
    "J6": (-180, 180),
}

# ==========================================
# 3. INTERFAZ MOVIL
# ==========================================

PAGE = r'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">

<title>MAKO Robot - Control movil</title>

<style>
* { box-sizing: border-box; }

body {
    margin: 0;
    background: #101923;
    color: #eef3f8;
    font-family: Arial, sans-serif;
    padding: 12px;
}

main {
    max-width: 620px;
    margin: auto;
    background: #202e3d;
    border-radius: 20px;
    padding: 20px;
    box-shadow: 0 8px 28px #0006;
}

h1 {
    text-align: center;
    color: #78b9f4;
    margin: 8px 0;
    font-size: 30px;
}

h2 {
    text-align: center;
    margin: 6px 0 18px;
    font-size: 20px;
}

h3 {
    margin-top: 24px;
    padding-bottom: 10px;
    border-bottom: 1px solid #526273;
    color: #78b9f4;
}

#status {
    text-align: center;
    padding: 13px;
    border-radius: 10px;
    background: #293d50;
    color: #ffc66d;
    font-weight: bold;
    margin-bottom: 16px;
}

.joint {
    padding: 12px 8px;
    border-bottom: 1px solid #526273;
}

.top {
    display: flex;
    justify-content: space-between;
    font-weight: bold;
    margin-bottom: 8px;
}

input[type=range] {
    width: 100%;
    accent-color: #58a6e8;
    height: 30px;
}

.example {
    background: #293d50;
    border-radius: 12px;
    padding: 15px;
    margin: 12px 0;
    border-left: 5px solid #58a6e8;
}

.example h4 {
    margin: 0 0 8px;
    font-size: 17px;
}

.example p {
    color: #c5d2df;
    font-size: 13px;
    line-height: 1.5;
}

button {
    border: 0;
    border-radius: 10px;
    padding: 15px;
    font-size: 15px;
    font-weight: bold;
    color: white;
    background: #397db5;
    cursor: pointer;
}

.run {
    width: 100%;
    background: #397db5;
}

.example2 {
    border-left-color: #39a878;
}

.example2 .run {
    background: #26845a;
}

.example3 {
    border-left-color: #a879dc;
}

.example3 .run {
    background: #8155ae;
}

.actions {
    display: flex;
    gap: 10px;
    margin-top: 18px;
}

.actions button {
    flex: 1;
}

.stop {
    background: #b83c42;
}

.home {
    background: #26845a;
}

button:active {
    transform: scale(0.98);
    opacity: 0.85;
}

.note {
    font-size: 12px;
    color: #b7c4d1;
    text-align: center;
    line-height: 1.5;
    margin-top: 18px;
}
</style>
</head>

<body>
<main>

<h1>MAKO ROBOT</h1>
<h2>CONTROL MOVIL</h2>

<div id="status">
Conectando con el simulador...
</div>

<!-- CONTROL MANUAL -->

<h3>1. CONTROL DE ARTICULACIONES</h3>

<div id="controls"></div>

<!-- EJEMPLOS AUTOMATICOS -->

<h3>2. MOVIMIENTOS PREPROGRAMADOS</h3>

<div class="example">

    <h4>EXAMPLE 1 - APROXIMACION</h4>

    <p>
    Aproximacion y posicionamiento del brazo
    quirurgico frente a la rodilla.
    Duracion aproximada: 3 segundos.
    </p>

    <button class="run" onclick="sendExample('EXAMPLE1')">
    RUN - APROXIMACION
    </button>

</div>

<div class="example example2">

    <h4>EXAMPLE 2 - CICLO DE CORTE</h4>

    <p>
    Avance, contacto, retroceso y repeticion.
    Ejecuta cinco oscilaciones automaticas
    de la herramienta quirurgica.
    </p>

    <button class="run" onclick="sendExample('EXAMPLE2')">
    RUN - INICIAR CICLO
    </button>

</div>

<div class="example example3">

    <h4>EXAMPLE 3 - POSICION INICIAL</h4>

    <p>
    Regreso progresivo del robot
    a su posicion inicial.
    </p>

    <button class="run" onclick="sendExample('EXAMPLE3')">
    RUN - REGRESAR
    </button>

</div>

<!-- ACCIONES GENERALES -->

<h3>3. ACCIONES GENERALES</h3>

<div class="actions">

<button class="home" onclick="sendAction('HOME')">
POSICION INICIAL
</button>

<button class="stop" onclick="sendAction('STOP')">
DETENER
</button>

</div>

<div class="note">
Control de una simulacion educativa en CoppeliaSim.
Mantener el telefono y la computadora conectados
al mismo hotspot Wi-Fi.
No controla un robot quirurgico fisico.
</div>

</main>

<script>

// ==========================================
// 4. ARTICULACIONES
// ==========================================

const joints = [
    ['J0', 'Base', -90, 90],
    ['J1', 'Hombro', -90, 90],
    ['J2', 'Brazo', -120, 120],
    ['J3', 'Codo', -120, 120],
    ['J5', 'Inclinacion', -90, 90],
    ['J6', 'Herramienta', -180, 180]
];

const controls = document.getElementById('controls');

let commandTimers = {};

// Crear controles automaticamente

for (const [id, name, min, max] of joints) {

    const d = document.createElement('div');
    d.className = 'joint';

    d.innerHTML = `
        <div class="top">
            <span>${id} - ${name}</span>
            <span id="v-${id}">0°</span>
        </div>

        <input
            id="s-${id}"
            type="range"
            min="${min}"
            max="${max}"
            value="0"
            step="1">
    `;

    controls.appendChild(d);

    const slider = d.querySelector('input');

    slider.addEventListener('input', () => {

        document.getElementById('v-' + id).textContent =
            slider.value + '°';

        clearTimeout(commandTimers[id]);

        commandTimers[id] = setTimeout(() => {

            sendMove(id, Number(slider.value));

        }, 100);

    });
}

// ==========================================
// 5. ENVIAR MOVIMIENTO MANUAL
// ==========================================

async function sendMove(joint, value) {

    try {

        const r = await fetch('/api/move', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                joint: joint,
                value: value
            })
        });

        if (!r.ok) throw Error();

    } catch (e) {

        document.getElementById('status').textContent =
            'No se pudo enviar el movimiento';

    }
}

// ==========================================
// 6. ENVIAR EJEMPLOS AUTOMATICOS
// ==========================================

async function sendExample(example) {

    const nombres = {
        EXAMPLE1: 'Iniciando aproximacion',
        EXAMPLE2: 'Iniciando ciclo de corte',
        EXAMPLE3: 'Regresando a posicion inicial'
    };

    if (!confirm('¿Deseas ejecutar ' + example + '?')) {
        return;
    }

    try {

        const r = await fetch('/api/example', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                example: example
            })
        });

        const data = await r.json();

        if (!r.ok) {
            throw Error(data.error || 'Error');
        }

        document.getElementById('status').textContent =
            nombres[example] + ' - orden enviada';

    } catch (e) {

        document.getElementById('status').textContent =
            'Error al ejecutar el ejemplo';

    }
}

// ==========================================
// 7. ACCIONES HOME Y STOP
// ==========================================

async function sendAction(action) {

    try {

        const r = await fetch('/api/action', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                action: action
            })
        });

        if (!r.ok) throw Error();

        const nombres = {
            HOME: 'Regreso a posicion inicial solicitado',
            STOP: 'Detencion solicitada'
        };

        document.getElementById('status').textContent =
            nombres[action];

    } catch (e) {

        document.getElementById('status').textContent =
            'Error de comunicacion';

    }
}

// ==========================================
// 8. ACTUALIZAR ESTADO DEL ROBOT
// ==========================================

async function refresh() {

    try {

        const r = await fetch('/api/status', {
            cache: 'no-store'
        });

        const d = await r.json();

        document.getElementById('status').textContent =
            d.simulator
            ? 'SIMULADOR CONECTADO'
            : 'Servidor activo; esperando CoppeliaSim';

        if (d.pose && d.pose.length >= 6) {

            joints.forEach((j, i) => {

                const val = Math.round(d.pose[i] || 0);

                const s = document.getElementById('s-' + j[0]);

                if (document.activeElement !== s) {

                    s.value = val;

                    document.getElementById(
                        'v-' + j[0]
                    ).textContent = val + '°';

                }

            });

        }

    } catch (e) {

        document.getElementById('status').textContent =
            'Servidor no disponible';

    }

}

refresh();

setInterval(refresh, 1000);

</script>
</body>
</html>'''

# ==========================================
# 9. PAGINA PRINCIPAL
# ==========================================

@app.get("/")
def home():

    return Response(
        PAGE,
        mimetype="text/html"
    )

# ==========================================
# 10. ESTADO DEL SIMULADOR
# ==========================================

@app.get("/api/status")
def status():

    BASE.mkdir(parents=True, exist_ok=True)

    HEARTBEAT_FILE.write_text(
        str(int(time.time())),
        encoding="utf-8"
    )

    simulator = False
    pose = None

    try:

        lines = STATUS_FILE.read_text(
            encoding="utf-8"
        ).splitlines()

        timestamp = float(lines[0]) if lines else 0

        simulator = (
            time.time() - timestamp
        ) <= 3

        if len(lines) > 1:

            pose = [
                float(x)
                for x in lines[1].split(",")
            ]

    except (OSError, ValueError):

        pass

    return jsonify({
        "simulator": simulator,
        "pose": pose
    })

# ==========================================
# 11. COLA DE COMANDOS
# ==========================================

def queue_command(action, joint="", value=0):

    global command_id

    BASE.mkdir(parents=True, exist_ok=True)

    with command_lock:

        command_id += 1

        line = (
            f"{command_id}|{action}|"
            f"{joint}|{value}"
        )

        temp = COMMAND_FILE.with_suffix(".tmp")

        temp.write_text(
            line,
            encoding="utf-8"
        )

        os.replace(temp, COMMAND_FILE)

    return command_id

# ==========================================
# 12. CONTROL DE ARTICULACIONES
# ==========================================

@app.post("/api/move")
def move():

    data = request.get_json(silent=True) or {}

    joint = str(data.get("joint", ""))

    if joint not in LIMITS:

        return jsonify({
            "error": "Articulacion no valida"
        }), 400

    try:

        value = float(data.get("value"))

    except (TypeError, ValueError):

        return jsonify({
            "error": "Valor no valido"
        }), 400

    low, high = LIMITS[joint]

    value = max(low, min(high, value))

    queue_command("MOVE", joint, value)

    return jsonify({
        "ok": True,
        "joint": joint,
        "value": value
    })

# ==========================================
# 13. EJECUTAR EJEMPLOS
# ==========================================

@app.post("/api/example")
def example():

    data = request.get_json(silent=True) or {}

    selected = str(data.get("example", "")).upper()

    examples = (
        "EXAMPLE1",
        "EXAMPLE2",
        "EXAMPLE3"
    )

    if selected not in examples:

        return jsonify({
            "error": "Ejemplo no valido"
        }), 400

    queue_command(selected)

    return jsonify({
        "ok": True,
        "example": selected,
        "message": "Ejemplo enviado a CoppeliaSim"
    })

# ==========================================
# 14. ACCIONES DEL ROBOT
# ==========================================

@app.post("/api/action")
def action():

    data = request.get_json(silent=True) or {}

    selected = str(data.get("action", "")).upper()

    if selected not in ("STOP", "HOME"):

        return jsonify({
            "error": "Accion no valida"
        }), 400

    queue_command(selected)

    return jsonify({
        "ok": True,
        "action": selected
    })

# ==========================================
# 15. INICIAR SERVIDOR MAKO
# PUERTO INDEPENDIENTE: 5001
# ==========================================

if __name__ == "__main__":

    BASE.mkdir(parents=True, exist_ok=True)

    print("======================================")
    print("       MAKO MOBILE SERVER")
    print("       CONTROL DE SIMULACION")
    print("======================================")

    print("Servidor iniciado correctamente")
    print("Puerto:", PUERTO)

    print("Abre desde el telefono:")
    print(f"http://{IP_SERVIDOR}:{PUERTO}")

    print("======================================")

    app.run(
        host="0.0.0.0",
        port=PUERTO,
        debug=False,
        use_reloader=False,
        threaded=True
    )
