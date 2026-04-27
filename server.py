import json
import os
import random
import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

HOST = '0.0.0.0'
PORT = int(os.environ.get('PORT', 8000))

ROLE_TEMPLATE = ["werewolf", "werewolf", "seer", "witch", "hunter", "villager", "villager", "villager"]
ROLE_NAME = {
    "werewolf": "狼人",
    "seer": "预言家",
    "witch": "女巫",
    "hunter": "猎人",
    "villager": "村民",
}
TEAM_NAME = {"werewolf": "狼人阵营", "good": "好人阵营"}


def role_team(role):
    return "werewolf" if role == "werewolf" else "good"


class GameState:
    def __init__(self):
        self.rooms = {}
        self.lock = threading.Lock()

    def create_room(self, host_name):
        room_id = uuid.uuid4().hex[:6]
        player_id = uuid.uuid4().hex[:8]
        room = {
            "room_id": room_id,
            "host_id": player_id,
            "status": "waiting",
            "day": 0,
            "phase": "waiting",
            "message": "等待玩家加入",
            "winner": None,
            "players": [
                {
                    "id": player_id,
                    "name": host_name,
                    "alive": True,
                    "role": None,
                    "ready": True,
                    "is_host": True,
                }
            ],
            "order": [],
            "current_speaker_index": 0,
            "speaker_done": False,
            "votes": {},
            "night_actions": {
                "werewolf_target": None,
                "seer_checked": None,
                "witch_save": False,
                "witch_poison": None,
                "used_save": False,
                "used_poison": False,
            },
            "night_result": [],
            "logs": [f"房主 {host_name} 创建了房间。"],
        }
        self.rooms[room_id] = room
        return room_id, player_id

    def get_room(self, room_id):
        return self.rooms.get(room_id)

    def find_player(self, room, player_id):
        for p in room["players"]:
            if p["id"] == player_id:
                return p
        return None

    def join_room(self, room_id, name):
        room = self.rooms.get(room_id)
        if not room:
            return None, "房间不存在"
        if room["status"] != "waiting":
            return None, "游戏已经开始，无法加入"
        if len(room["players"]) >= 12:
            return None, "房间已满"
        player_id = uuid.uuid4().hex[:8]
        room["players"].append(
            {
                "id": player_id,
                "name": name,
                "alive": True,
                "role": None,
                "ready": True,
                "is_host": False,
            }
        )
        room["logs"].append(f"玩家 {name} 加入了房间。")
        return player_id, None

    def start_game(self, room_id, player_id):
        room = self.rooms.get(room_id)
        if not room:
            return "房间不存在"
        if room["host_id"] != player_id:
            return "只有房主可以开始游戏"
        count = len(room["players"])
        if count < 6:
            return "至少需要 6 名玩家才能开始"
        roles = self.build_roles(count)
        random.shuffle(roles)
        for p, r in zip(room["players"], roles):
            p["role"] = r
            p["alive"] = True
        room["status"] = "playing"
        room["day"] = 1
        room["phase"] = "night_werewolf"
        room["message"] = "第 1 夜：狼人请选择击杀目标。"
        room["winner"] = None
        room["votes"] = {}
        room["night_actions"] = {
            "werewolf_target": None,
            "seer_checked": None,
            "witch_save": False,
            "witch_poison": None,
            "used_save": False,
            "used_poison": False,
        }
        room["night_result"] = []
        room["order"] = []
        room["current_speaker_index"] = 0
        room["speaker_done"] = False
        room["logs"].append("游戏开始，系统已分配身份。")
        return None

    def build_roles(self, count):
        roles = ROLE_TEMPLATE.copy()
        if count < len(roles):
            roles = roles[:count]
            if roles.count("werewolf") < 2 and count >= 6:
                roles[0] = "werewolf"
                roles[1] = "werewolf"
        elif count > len(roles):
            roles.extend(["villager"] * (count - len(roles)))
        return roles

    def living_players(self, room):
        return [p for p in room["players"] if p["alive"]]

    def living_by_role(self, room, role):
        return [p for p in room["players"] if p["alive"] and p["role"] == role]

    def check_winner(self, room):
        alive = self.living_players(room)
        wolves = [p for p in alive if p["role"] == "werewolf"]
        good = [p for p in alive if p["role"] != "werewolf"]
        if not wolves:
            room["winner"] = "好人阵营"
        elif len(wolves) >= len(good):
            room["winner"] = "狼人阵营"
        else:
            return None
        room["status"] = "ended"
        room["phase"] = "ended"
        room["message"] = f"游戏结束，{room['winner']} 获胜！"
        room["logs"].append(room["message"])
        return room["winner"]

    def advance_after_night(self, room):
        victim = room["night_actions"]["werewolf_target"]
        poison = room["night_actions"]["witch_poison"]
        saved = room["night_actions"]["witch_save"]
        deaths = []
        if victim and not saved:
            target = self.find_player(room, victim)
            if target and target["alive"]:
                target["alive"] = False
                deaths.append(target["name"])
        if poison:
            target = self.find_player(room, poison)
            if target and target["alive"]:
                target["alive"] = False
                deaths.append(target["name"])
        room["night_result"] = deaths
        room["phase"] = "day_discussion"
        room["message"] = f"第 {room['day']} 天白天开始。"
        if deaths:
            room["logs"].append("昨夜死亡：" + "、".join(deaths))
        else:
            room["logs"].append("昨夜是平安夜。")
        if self.check_winner(room):
            return
        room["order"] = [p["id"] for p in self.living_players(room)]
        room["current_speaker_index"] = 0
        room["speaker_done"] = False
        room["votes"] = {}

    def advance_discussion(self, room):
        room["phase"] = "day_vote"
        room["message"] = "讨论结束，请所有存活玩家投票放逐一名玩家。"
        room["votes"] = {}
        room["logs"].append("进入投票阶段。")

    def resolve_vote(self, room):
        tally = {}
        for target in room["votes"].values():
            tally[target] = tally.get(target, 0) + 1
        if not tally:
            room["logs"].append("无人投票，直接进入夜晚。")
            self.next_night(room)
            return
        max_votes = max(tally.values())
        top = [pid for pid, c in tally.items() if c == max_votes]
        if len(top) > 1:
            room["logs"].append("投票平票，无人被放逐。")
        else:
            target = self.find_player(room, top[0])
            if target and target["alive"]:
                target["alive"] = False
                room["logs"].append(f"{target['name']} 被投票放逐，身份是 {ROLE_NAME[target['role']]}。")
        if self.check_winner(room):
            return
        self.next_night(room)

    def next_night(self, room):
        room["day"] += 1
        room["phase"] = "night_werewolf"
        room["message"] = f"第 {room['day']} 夜：狼人请选择击杀目标。"
        room["votes"] = {}
        room["night_actions"]["werewolf_target"] = None
        room["night_actions"]["seer_checked"] = None
        room["night_actions"]["witch_save"] = False
        room["night_actions"]["witch_poison"] = None


STATE = GameState()

INDEX_HTML = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>WolfGame 狼人杀</title>
  <style>
    body { font-family: Arial, sans-serif; background: #111827; color: #f3f4f6; margin: 0; }
    .container { max-width: 1100px; margin: 0 auto; padding: 24px; }
    .card { background: #1f2937; border-radius: 14px; padding: 18px; margin-bottom: 16px; box-shadow: 0 6px 24px rgba(0,0,0,0.25); }
    h1, h2, h3 { margin-top: 0; }
    input, button, select { padding: 10px 12px; border-radius: 8px; border: none; margin: 6px 6px 6px 0; }
    button { background: #2563eb; color: white; cursor: pointer; }
    button.secondary { background: #4b5563; }
    button.danger { background: #dc2626; }
    button:disabled { background: #6b7280; cursor: not-allowed; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; }
    .player { padding: 10px; border-radius: 10px; background: #374151; margin-bottom: 8px; }
    .dead { opacity: 0.55; }
    .tag { display: inline-block; padding: 2px 8px; border-radius: 999px; background: #0f766e; margin-left: 6px; font-size: 12px; }
    .log { max-height: 280px; overflow-y: auto; background: #0b1220; padding: 12px; border-radius: 10px; }
    .muted { color: #9ca3af; }
    .hidden { display: none; }
  </style>
</head>
<body>
<div class="container">
  <h1>🐺 WolfGame 网页协同狼人杀</h1>
  <div id="auth" class="card">
    <h2>进入游戏</h2>
    <input id="name" placeholder="输入你的昵称" />
    <div>
      <button onclick="createRoom()">创建房间</button>
      <input id="roomInput" placeholder="输入房间号加入" />
      <button class="secondary" onclick="joinRoom()">加入房间</button>
    </div>
    <p class="muted">支持局域网多人访问：让其他玩家在浏览器打开你的 IP:8000 即可。</p>
  </div>

  <div id="game" class="hidden">
    <div class="card">
      <h2>房间信息</h2>
      <div id="roomInfo"></div>
      <div id="actions"></div>
    </div>

    <div class="grid">
      <div class="card">
        <h3>我的身份</h3>
        <div id="me"></div>
      </div>
      <div class="card">
        <h3>玩家列表</h3>
        <div id="players"></div>
      </div>
    </div>

    <div class="grid">
      <div class="card">
        <h3>阶段操作</h3>
        <div id="phasePanel"></div>
      </div>
      <div class="card">
        <h3>系统日志</h3>
        <div id="logs" class="log"></div>
      </div>
    </div>
  </div>
</div>
<script>
let playerId = localStorage.getItem('wolfgame_player_id') || '';
let roomId = localStorage.getItem('wolfgame_room_id') || '';

function saveSession() {
  localStorage.setItem('wolfgame_player_id', playerId);
  localStorage.setItem('wolfgame_room_id', roomId);
}

async function api(path, method='GET', body=null) {
  const res = await fetch(path, {
    method,
    headers: {'Content-Type': 'application/json'},
    body: body ? JSON.stringify(body) : null,
  });
  return await res.json();
}

async function createRoom() {
  const name = document.getElementById('name').value.trim();
  if (!name) return alert('请输入昵称');
  const data = await api('/api/create_room', 'POST', {name});
  if (data.error) return alert(data.error);
  playerId = data.player_id; roomId = data.room_id; saveSession();
  enterGame();
}

async function joinRoom() {
  const name = document.getElementById('name').value.trim();
  const joinRoomId = document.getElementById('roomInput').value.trim();
  if (!name || !joinRoomId) return alert('请输入昵称和房间号');
  const data = await api('/api/join_room', 'POST', {name, room_id: joinRoomId});
  if (data.error) return alert(data.error);
  playerId = data.player_id; roomId = joinRoomId; saveSession();
  enterGame();
}

function alivePlayers(state) {
  return state.players.filter(p => p.alive);
}

function optionPlayers(state, includeSelf=true) {
  return alivePlayers(state).filter(p => includeSelf || p.id !== state.me.id);
}

async function doAction(action, targetId=null, extra={}) {
  const data = await api('/api/action', 'POST', {room_id: roomId, player_id: playerId, action, target_id: targetId, ...extra});
  if (data.error) alert(data.error);
  await refresh();
}

function renderPlayers(state) {
  const div = document.getElementById('players');
  div.innerHTML = state.players.map(p => `
    <div class="player ${p.alive ? '' : 'dead'}">
      <strong>${p.name}</strong>
      ${p.is_host ? '<span class="tag">房主</span>' : ''}
      ${p.id === state.me.id ? '<span class="tag">你</span>' : ''}
      <div>${p.alive ? '存活' : '出局'}</div>
      <div class="muted">${p.public_role || ''}</div>
    </div>
  `).join('');
}

function renderMe(state) {
  const me = state.me;
  document.getElementById('me').innerHTML = `
    <div><strong>${me.name}</strong></div>
    <div>身份：<strong>${me.role_name || '未分配'}</strong></div>
    <div>阵营：${me.team_name || '-'}</div>
    <div>状态：${me.alive ? '存活' : '出局'}</div>
    ${me.seer_result ? `<div>最近查验：${me.seer_result}</div>` : ''}
  `;
}

function renderRoomInfo(state) {
  document.getElementById('roomInfo').innerHTML = `
    <div>房间号：<strong>${state.room_id}</strong></div>
    <div>状态：${state.status_text}</div>
    <div>阶段：${state.phase_text}</div>
    <div>提示：${state.message}</div>
    ${state.winner ? `<div><strong>${state.winner}</strong></div>` : ''}
  `;

  const actions = document.getElementById('actions');
  actions.innerHTML = '';
  if (state.is_host && state.status === 'waiting') {
    actions.innerHTML += `<button onclick="doAction('start_game')">开始游戏</button>`;
  }
  actions.innerHTML += `<button class="secondary" onclick="refresh()">刷新</button>`;
}

function buildTargetButtons(players, actionName, label) {
  if (!players.length) return '<div class="muted">暂无可选目标</div>';
  return players.map(p => `<button onclick="doAction('${actionName}', '${p.id}')">${label}：${p.name}</button>`).join('');
}

function renderPhasePanel(state) {
  const panel = document.getElementById('phasePanel');
  const me = state.me;
  let html = '';

  if (state.status === 'waiting') {
    html = '<div>等待房主开始游戏。</div>';
  } else if (state.status === 'ended') {
    html = '<div>本局已结束，可刷新查看最终结果。</div>';
  } else if (!me.alive) {
    html = '<div>你已出局，只能观战。</div>';
  } else if (state.phase === 'night_werewolf') {
    if (me.role === 'werewolf') {
      html += '<div>狼人行动：选择今晚击杀目标。</div>';
      html += buildTargetButtons(optionPlayers(state, false).filter(p => p.role_hint !== 'werewolf'), 'werewolf_kill', '击杀');
    } else {
      html = '<div>夜晚进行中，请等待狼人行动结束。</div>';
    }
  } else if (state.phase === 'night_seer') {
    if (me.role === 'seer') {
      html += '<div>预言家行动：选择一名玩家查验身份。</div>';
      html += buildTargetButtons(optionPlayers(state, false), 'seer_check', '查验');
    } else {
      html = '<div>预言家查验中，请等待。</div>';
    }
  } else if (state.phase === 'night_witch') {
    if (me.role === 'witch') {
      html += '<div>女巫行动：</div>';
      if (state.witch_can_save && state.night_victim_name) {
        html += `<button onclick="doAction('witch_save')">使用解药救 ${state.night_victim_name}</button>`;
      }
      if (state.witch_can_poison) {
        html += '<div>使用毒药：</div>' + buildTargetButtons(optionPlayers(state, false), 'witch_poison', '毒杀');
      }
      html += `<div><button class="secondary" onclick="doAction('witch_skip')">跳过女巫行动</button></div>`;
    } else {
      html = '<div>女巫行动中，请等待。</div>';
    }
  } else if (state.phase === 'day_discussion') {
    if (state.is_current_speaker) {
      html += '<div>轮到你发言，发言后点击结束。</div>';
      html += `<button onclick="doAction('finish_speaking')">我已发言</button>`;
    } else {
      html = `<div>讨论阶段，当前发言：${state.current_speaker_name || '无'}</div>`;
    }
  } else if (state.phase === 'day_vote') {
    html += '<div>投票放逐一名玩家：</div>';
    html += buildTargetButtons(optionPlayers(state, false), 'vote', '投票');
  }

  panel.innerHTML = html;
}

function renderLogs(state) {
  document.getElementById('logs').innerHTML = state.logs.map(line => `<div>${line}</div>`).join('');
}

async function refresh() {
  if (!roomId || !playerId) return;
  const state = await api(`/api/state?room_id=${roomId}&player_id=${playerId}`);
  if (state.error) return;
  document.getElementById('auth').classList.add('hidden');
  document.getElementById('game').classList.remove('hidden');
  renderRoomInfo(state);
  renderMe(state);
  renderPlayers(state);
  renderPhasePanel(state);
  renderLogs(state);
}

function enterGame() {
  document.getElementById('auth').classList.add('hidden');
  document.getElementById('game').classList.remove('hidden');
  refresh();
  setInterval(refresh, 2000);
}

if (roomId && playerId) {
  enterGame();
}
</script>
</body>
</html>
'''


class Handler(BaseHTTPRequestHandler):
    def _send(self, data, status=200, content_type="application/json; charset=utf-8"):
        payload = data.encode("utf-8") if isinstance(data, str) else json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self._send(INDEX_HTML, content_type="text/html; charset=utf-8")
            return
        if parsed.path == "/api/state":
            query = parse_qs(parsed.query)
            room_id = query.get("room_id", [""])[0]
            player_id = query.get("player_id", [""])[0]
            with STATE.lock:
                room = STATE.get_room(room_id)
                if not room:
                    self._send({"error": "房间不存在"}, 404)
                    return
                player = STATE.find_player(room, player_id)
                if not player:
                    self._send({"error": "玩家不存在"}, 404)
                    return
                self._send(build_state(room, player))
            return
        self._send({"error": "Not Found"}, 404)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length else "{}"
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            data = {}
        if self.path == "/api/create_room":
            name = (data.get("name") or "").strip()
            if not name:
                self._send({"error": "昵称不能为空"}, 400)
                return
            with STATE.lock:
                room_id, player_id = STATE.create_room(name)
            self._send({"room_id": room_id, "player_id": player_id})
            return
        if self.path == "/api/join_room":
            name = (data.get("name") or "").strip()
            room_id = (data.get("room_id") or "").strip()
            if not name or not room_id:
                self._send({"error": "参数不完整"}, 400)
                return
            with STATE.lock:
                player_id, err = STATE.join_room(room_id, name)
            if err:
                self._send({"error": err}, 400)
                return
            self._send({"player_id": player_id})
            return
        if self.path == "/api/action":
            room_id = data.get("room_id")
            player_id = data.get("player_id")
            action = data.get("action")
            target_id = data.get("target_id")
            with STATE.lock:
                result = handle_action(room_id, player_id, action, target_id)
            if result:
                self._send({"error": result}, 400)
            else:
                self._send({"ok": True})
            return
        self._send({"error": "Not Found"}, 404)


def build_state(room, player):
    current_speaker = None
    if room["phase"] == "day_discussion" and room["order"] and room["current_speaker_index"] < len(room["order"]):
        current_speaker = STATE.find_player(room, room["order"][room["current_speaker_index"]])
    players = []
    for p in room["players"]:
        public_role = ""
        if not p["alive"] and p["role"]:
            public_role = f"已知身份：{ROLE_NAME[p['role']]}"
        role_hint = "werewolf" if player["role"] == "werewolf" and p["role"] == "werewolf" else None
        players.append({
            "id": p["id"],
            "name": p["name"],
            "alive": p["alive"],
            "is_host": p["is_host"],
            "public_role": public_role,
            "role_hint": role_hint,
        })
    victim_name = None
    victim = room["night_actions"].get("werewolf_target")
    if victim:
        found = STATE.find_player(room, victim)
        victim_name = found["name"] if found else None
    return {
        "room_id": room["room_id"],
        "status": room["status"],
        "status_text": {"waiting": "等待开始", "playing": "进行中", "ended": "已结束"}[room["status"]],
        "phase": room["phase"],
        "phase_text": {
            "waiting": "等待阶段",
            "night_werewolf": "夜晚：狼人",
            "night_seer": "夜晚：预言家",
            "night_witch": "夜晚：女巫",
            "day_discussion": "白天：讨论",
            "day_vote": "白天：投票",
            "ended": "结算",
        }.get(room["phase"], room["phase"]),
        "message": room["message"],
        "winner": room["winner"],
        "is_host": player["is_host"],
        "players": players,
        "me": {
            "id": player["id"],
            "name": player["name"],
            "alive": player["alive"],
            "role": player["role"],
            "role_name": ROLE_NAME.get(player["role"]),
            "team_name": TEAM_NAME[role_team(player["role"])] if player["role"] else None,
            "seer_result": room.get("seer_result_" + player["id"]),
        },
        "logs": room["logs"][-20:],
        "current_speaker_name": current_speaker["name"] if current_speaker else None,
        "is_current_speaker": current_speaker and current_speaker["id"] == player["id"],
        "witch_can_save": player["role"] == "witch" and not room["night_actions"]["used_save"] and bool(victim_name),
        "witch_can_poison": player["role"] == "witch" and not room["night_actions"]["used_poison"],
        "night_victim_name": victim_name,
    }


def handle_action(room_id, player_id, action, target_id):
    room = STATE.get_room(room_id)
    if not room:
        return "房间不存在"
    player = STATE.find_player(room, player_id)
    if not player:
        return "玩家不存在"
    if action == "start_game":
        return STATE.start_game(room_id, player_id)
    if room["status"] != "playing":
        return "当前不在游戏中"
    if not player["alive"] and action not in {"refresh"}:
        return "你已出局，无法操作"

    if action == "werewolf_kill":
        if room["phase"] != "night_werewolf" or player["role"] != "werewolf":
            return "当前不能执行狼人操作"
        target = STATE.find_player(room, target_id)
        if not target or not target["alive"] or target["role"] == "werewolf":
            return "目标无效"
        room["night_actions"]["werewolf_target"] = target_id
        room["logs"].append(f"狼人已选择目标。")
        room["phase"] = "night_seer"
        room["message"] = "预言家请选择查验对象。"
        return None

    if action == "seer_check":
        if room["phase"] != "night_seer" or player["role"] != "seer":
            return "当前不能执行预言家操作"
        target = STATE.find_player(room, target_id)
        if not target:
            return "目标无效"
        result = "狼人" if target["role"] == "werewolf" else "好人"
        room["seer_result_" + player["id"]] = f"{target['name']} 是{result}"
        room["logs"].append("预言家已完成查验。")
        room["phase"] = "night_witch"
        room["message"] = "女巫请决定是否使用药剂。"
        return None

    if action == "witch_save":
        if room["phase"] != "night_witch" or player["role"] != "witch":
            return "当前不能执行女巫操作"
        if room["night_actions"]["used_save"]:
            return "解药已经使用过"
        room["night_actions"]["witch_save"] = True
        room["night_actions"]["used_save"] = True
        STATE.advance_after_night(room)
        return None

    if action == "witch_poison":
        if room["phase"] != "night_witch" or player["role"] != "witch":
            return "当前不能执行女巫操作"
        if room["night_actions"]["used_poison"]:
            return "毒药已经使用过"
        target = STATE.find_player(room, target_id)
        if not target or not target["alive"]:
            return "目标无效"
        room["night_actions"]["witch_poison"] = target_id
        room["night_actions"]["used_poison"] = True
        STATE.advance_after_night(room)
        return None

    if action == "witch_skip":
        if room["phase"] != "night_witch":
            return "当前不能跳过女巫操作"
        STATE.advance_after_night(room)
        return None

    if action == "finish_speaking":
        if room["phase"] != "day_discussion":
            return "当前不是讨论阶段"
        if room["current_speaker_index"] >= len(room["order"]):
            return "发言已结束"
        current_id = room["order"][room["current_speaker_index"]]
        if current_id != player_id:
            return "还没轮到你发言"
        room["logs"].append(f"{player['name']} 已完成发言。")
        room["current_speaker_index"] += 1
        if room["current_speaker_index"] >= len(room["order"]):
            STATE.advance_discussion(room)
        return None

    if action == "vote":
        if room["phase"] != "day_vote":
            return "当前不是投票阶段"
        target = STATE.find_player(room, target_id)
        if not target or not target["alive"] or target["id"] == player_id:
            return "投票目标无效"
        room["votes"][player_id] = target_id
        room["logs"].append(f"{player['name']} 已投票。")
        alive_count = len([p for p in room["players"] if p["alive"]])
        if len(room["votes"]) >= alive_count:
            STATE.resolve_vote(room)
        return None

    return "未知操作"


def run():
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"WolfGame 已启动: http://127.0.0.1:{PORT}")
    print(f"局域网访问: http://<你的本机IP>:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    run()
