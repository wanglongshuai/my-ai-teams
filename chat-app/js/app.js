// ── AI Teams IM — 前端主逻辑 ──────────────────────────────────────

const API = 'http://localhost:8080';

// 状态
let state = {
  members: [],       // 所有成员
  groups: [],        // 所有群组
  currentGroupId: null,
  currentGroupMembers: [],
  selectedResponder: '',  // 群聊中指定回复的成员
  sending: false,
};

// ── 初始化 ────────────────────────────────────────────────────────
async function init() {
  try {
    const [members, groups] = await Promise.all([
      fetch(`${API}/api/members`).then(r => r.json()),
      fetch(`${API}/api/groups`).then(r => r.json()),
    ]);
    state.members = members;
    state.groups = groups;
    renderSidebar();
    renderOrgChart();
    setStatus(true);
  } catch (e) {
    setStatus(false);
    console.error('初始化失败', e);
  }
}

function setStatus(online) {
  const dot = document.querySelector('.status-dot');
  const text = document.getElementById('status-text');
  if (online) {
    dot.classList.add('online');
    text.textContent = '已连接';
  } else {
    dot.classList.remove('online');
    text.textContent = '未连接（请启动 server.py）';
  }
}

// ── 视图切换 ──────────────────────────────────────────────────────
function switchView(view) {
  document.querySelectorAll('.view').forEach(v => v.classList.add('hidden'));
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  document.getElementById(`view-${view}`).classList.remove('hidden');
  document.querySelector(`[data-view="${view}"]`).classList.add('active');
}

// ── 侧边栏渲染 ────────────────────────────────────────────────────
function renderSidebar() {
  const teamEl = document.getElementById('group-list-team');
  const mgmtEl = document.getElementById('group-list-management');
  const directEl = document.getElementById('group-list-direct');
  const customEl = document.getElementById('group-list-custom');

  teamEl.innerHTML = '';
  mgmtEl.innerHTML = '';
  directEl.innerHTML = '';
  customEl.innerHTML = '';

  for (const g of state.groups) {
    const el = createGroupItem(g);
    if (g.type === 'team') teamEl.appendChild(el);
    else if (g.type === 'management') mgmtEl.appendChild(el);
    else if (g.type === 'direct') directEl.appendChild(el);
    else customEl.appendChild(el);
  }
}

function createGroupItem(g) {
  const div = document.createElement('div');
  div.className = 'group-item';
  div.dataset.groupId = g.id;
  div.onclick = () => openGroup(g.id);

  const color = getGroupColor(g);
  const icon = getGroupIcon(g);

  div.innerHTML = `
    <div class="group-avatar" style="background:${color}">${icon}</div>
    <div class="group-info">
      <div class="group-name">${g.name}</div>
      <div class="group-meta">${getGroupMeta(g)}</div>
    </div>
  `;
  return div;
}

function getGroupColor(g) {
  if (g.type === 'team') {
    if (g.id === 'team1') return '#4A90D9';
    if (g.id === 'team2') return '#3182CE';
    if (g.id === 'team3') return '#38A169';
  }
  if (g.type === 'management') return '#D4A017';
  if (g.type === 'direct') {
    const mid = g.id.replace('dm-', '');
    return getMember(mid)?.color || '#718096';
  }
  return '#805AD5';
}

function getGroupIcon(g) {
  if (g.type === 'team') return ['🎯','⚙️','📣'][['team1','team2','team3'].indexOf(g.id)] || '👥';
  if (g.type === 'management') return '👑';
  if (g.type === 'direct') {
    const mid = g.id.replace('dm-', '');
    return getMember(mid)?.avatar || '?';
  }
  return '💬';
}

function getGroupMeta(g) {
  if (g.type === 'direct') {
    const mid = g.id.replace('dm-', '');
    return getMember(mid)?.role || '';
  }
  return `${g.members?.length || 0} 人`;
}

function getMember(id) {
  return state.members.find(m => m.id === id);
}

// ── 打开群组 ──────────────────────────────────────────────────────
async function openGroup(groupId) {
  state.currentGroupId = groupId;
  state.selectedResponder = '';

  // 高亮侧边栏
  document.querySelectorAll('.group-item').forEach(el => {
    el.classList.toggle('active', el.dataset.groupId === groupId);
  });

  const group = state.groups.find(g => g.id === groupId);
  if (!group) return;

  state.currentGroupMembers = (group.members || []).map(id => getMember(id)).filter(Boolean);

  // 显示聊天面板
  document.getElementById('chat-empty').classList.add('hidden');
  document.getElementById('chat-panel').classList.remove('hidden');

  // 设置标题
  document.getElementById('chat-title').textContent = group.name;
  document.getElementById('chat-subtitle').textContent =
    group.type === 'direct' ? '' : `${group.members?.length || 0} 人`;

  // 群聊显示回复者选择
  const responderDiv = document.getElementById('chat-responder-select');
  const responderSelect = document.getElementById('responder-select');
  if (group.type !== 'direct') {
    responderDiv.classList.remove('hidden');
    responderSelect.innerHTML = '<option value="">自动（Leader）</option>';
    for (const m of state.currentGroupMembers) {
      const opt = document.createElement('option');
      opt.value = m.id;
      opt.textContent = `${m.name}（${m.role}）`;
      responderSelect.appendChild(opt);
    }
  } else {
    responderDiv.classList.add('hidden');
  }

  // 渲染右侧信息面板
  renderInfoPanel(group);

  // 加载消息
  await loadMessages(groupId);

  // 聚焦输入框
  document.getElementById('msg-input').focus();
}

function setResponder(val) {
  state.selectedResponder = val;
}

// ── 消息加载与渲染 ────────────────────────────────────────────────
async function loadMessages(groupId) {
  const container = document.getElementById('messages');
  container.innerHTML = '<div style="text-align:center;color:#999;font-size:13px;padding:20px">加载中...</div>';
  try {
    const msgs = await fetch(`${API}/api/messages/${groupId}`).then(r => r.json());
    container.innerHTML = '';
    for (const msg of msgs) renderMessage(msg, false);
    scrollToBottom();
  } catch (e) {
    container.innerHTML = '<div style="text-align:center;color:#e53e3e;font-size:13px;padding:20px">加载失败</div>';
  }
}

function renderMessage(msg, scroll = true) {
  const container = document.getElementById('messages');
  const isUser = msg.sender_id === 'user';
  const member = isUser ? null : getMember(msg.sender_id);

  const div = document.createElement('div');
  div.className = `message ${isUser ? 'from-user' : 'from-ai'}`;

  const avatarColor = isUser ? '#1677ff' : (member?.color || '#718096');
  const avatarText = isUser ? '我' : (member?.avatar || '?');

  const time = formatTime(msg.created_at);
  const htmlContent = renderMarkdown(msg.content);

  if (isUser) {
    div.innerHTML = `
      <div class="msg-avatar" style="background:${avatarColor}" title="我">${avatarText}</div>
      <div>
        <div class="bubble">${htmlContent}</div>
        <div class="msg-meta">${time}</div>
      </div>
    `;
  } else {
    div.innerHTML = `
      <div class="msg-avatar" style="background:${avatarColor}" title="${member?.name || ''}"
        onclick="openProfileModal('${msg.sender_id}')">${avatarText}</div>
      <div>
        <div class="msg-sender">${member?.name || msg.sender_id} · ${member?.role || ''}</div>
        <div class="bubble">${htmlContent}</div>
        <div class="msg-meta">${time}</div>
      </div>
    `;
  }

  container.appendChild(div);
  if (scroll) scrollToBottom();
}

function renderMarkdown(text) {
  if (typeof marked !== 'undefined') {
    try { return marked.parse(text); } catch (e) {}
  }
  return text.replace(/\n/g, '<br>');
}

function scrollToBottom() {
  const el = document.getElementById('messages');
  el.scrollTop = el.scrollHeight;
}

function formatTime(ts) {
  if (!ts) return '';
  const d = new Date(ts);
  const now = new Date();
  const isToday = d.toDateString() === now.toDateString();
  if (isToday) return d.toTimeString().slice(0, 5);
  return `${d.getMonth()+1}/${d.getDate()} ${d.toTimeString().slice(0, 5)}`;
}

// ── 发送消息 ──────────────────────────────────────────────────────
async function sendMessage() {
  if (state.sending) return;
  const input = document.getElementById('msg-input');
  const text = input.value.trim();
  if (!text || !state.currentGroupId) return;

  state.sending = true;
  input.value = '';
  document.querySelector('.send-btn').disabled = true;

  // 立即显示用户消息
  renderMessage({ sender_id: 'user', content: text, created_at: new Date().toISOString() });

  // 显示 typing
  const typingEl = document.getElementById('typing-indicator');
  const typingName = document.getElementById('typing-name');
  const responder = state.selectedResponder ||
    (state.currentGroupMembers.find(m => m.is_leader) || state.currentGroupMembers[0])?.id;
  const respMember = getMember(responder);
  typingName.textContent = respMember?.name || '';
  typingEl.classList.remove('hidden');
  scrollToBottom();

  try {
    const res = await fetch(`${API}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        group_id: state.currentGroupId,
        message: text,
        member_id: state.selectedResponder || null,
      }),
    });
    const data = await res.json();
    typingEl.classList.add('hidden');

    if (data.responses) {
      for (const r of data.responses) {
        renderMessage({
          sender_id: r.member_id,
          content: r.content,
          created_at: new Date().toISOString(),
        });
      }
    }
  } catch (e) {
    typingEl.classList.add('hidden');
    renderMessage({
      sender_id: 'system',
      content: `❌ 发送失败：${e.message}`,
      created_at: new Date().toISOString(),
    });
  } finally {
    state.sending = false;
    document.querySelector('.send-btn').disabled = false;
    input.focus();
  }
}

function handleInputKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
}

// ── 右侧信息面板 ──────────────────────────────────────────────────
function renderInfoPanel(group) {
  document.getElementById('info-empty').classList.add('hidden');
  document.getElementById('info-content').classList.remove('hidden');

  const color = getGroupColor(group);
  const icon = getGroupIcon(group);
  const typeLabels = { team: '团队群', management: '管理层群', direct: '单聊', custom: '自定义群' };

  document.getElementById('info-header').innerHTML = `
    <div class="info-group-header">
      <div class="info-group-avatar" style="background:${color}">${icon}</div>
      <div class="info-group-name">${group.name}</div>
      <div class="info-group-type">${typeLabels[group.type] || ''}</div>
    </div>
  `;

  const membersDiv = document.getElementById('info-members');
  if (group.type === 'direct') {
    const mid = group.id.replace('dm-', '');
    const m = getMember(mid);
    if (m) {
      membersDiv.innerHTML = `
        <div class="info-members-title">成员</div>
        ${renderInfoMemberItem(m)}
      `;
    }
  } else {
    const members = (group.members || []).map(id => getMember(id)).filter(Boolean);
    const sorted = [...members].sort((a, b) => (b.is_leader ? 1 : 0) - (a.is_leader ? 1 : 0));
    membersDiv.innerHTML = `
      <div class="info-members-title">成员（${sorted.length}）</div>
      ${sorted.map(renderInfoMemberItem).join('')}
    `;
  }
}

function renderInfoMemberItem(m) {
  return `
    <div class="info-member-item" onclick="openProfileModal('${m.id}')">
      <div class="info-member-avatar" style="background:${m.color}">${m.avatar}</div>
      <div>
        <div class="info-member-name">
          ${m.name}
          ${m.is_leader ? '<span class="leader-badge">Leader</span>' : ''}
        </div>
        <div class="info-member-role">${m.role}</div>
      </div>
    </div>
  `;
}

// ── 成员资料 Modal ────────────────────────────────────────────────
function openProfileModal(memberId) {
  const m = getMember(memberId);
  if (!m) return;
  document.getElementById('profile-name').textContent = m.name;
  document.getElementById('profile-body').innerHTML = `
    <div class="profile-avatar-lg" style="background:${m.color}">${m.avatar}</div>
    <div class="profile-info">
      <div class="profile-name">${m.name} ${m.is_leader ? '<span class="leader-badge">Leader</span>' : ''}</div>
      <div class="profile-role">${m.role}</div>
      <div class="profile-team">${m.team_name}</div>
    </div>
    <div class="profile-actions">
      <button class="btn-dm" onclick="openDM('${m.id}'); closeProfileModal()">发消息</button>
    </div>
  `;
  document.getElementById('modal-profile').classList.remove('hidden');
}

function closeProfileModal() {
  document.getElementById('modal-profile').classList.add('hidden');
}

function openDM(memberId) {
  const dmGroupId = `dm-${memberId}`;
  openGroup(dmGroupId);
  // 确保在侧边栏中可见
  switchView('chat');
}

// ── 新建群聊 Modal ────────────────────────────────────────────────
function openNewGroupModal() {
  document.getElementById('new-group-name').value = '';
  const container = document.getElementById('member-checkboxes');
  container.innerHTML = '';

  // 按团队分组显示
  const teams = [
    { id: 1, name: '产品研发团队' },
    { id: 2, name: '技术研发团队' },
    { id: 3, name: '推广营销团队' },
  ];
  for (const team of teams) {
    const label = document.createElement('div');
    label.style.cssText = 'font-size:11px;font-weight:600;color:#999;text-transform:uppercase;padding:8px 4px 4px;letter-spacing:.5px';
    label.textContent = team.name;
    container.appendChild(label);

    const teamMembers = state.members.filter(m => m.team === team.id);
    for (const m of teamMembers) {
      const item = document.createElement('label');
      item.className = 'member-checkbox-item';
      item.innerHTML = `
        <input type="checkbox" value="${m.id}">
        <div class="member-checkbox-avatar" style="background:${m.color}">${m.avatar}</div>
        <div>
          <div style="font-size:13px;font-weight:500">${m.name} ${m.is_leader ? '<span class="leader-badge">Leader</span>' : ''}</div>
          <div style="font-size:12px;color:#999">${m.role}</div>
        </div>
      `;
      container.appendChild(item);
    }
  }

  document.getElementById('modal-new-group').classList.remove('hidden');
}

function closeNewGroupModal() {
  document.getElementById('modal-new-group').classList.add('hidden');
}

async function createGroup() {
  const name = document.getElementById('new-group-name').value.trim();
  const checked = [...document.querySelectorAll('#member-checkboxes input:checked')].map(el => el.value);
  if (!name) { alert('请输入群聊名称'); return; }
  if (checked.length < 1) { alert('请至少选择一个成员'); return; }

  try {
    const group = await fetch(`${API}/api/groups/create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, members: checked }),
    }).then(r => r.json());

    state.groups.push(group);
    renderSidebar();
    closeNewGroupModal();
    openGroup(group.id);
  } catch (e) {
    alert('创建失败：' + e.message);
  }
}

// ── 组织架构渲染 ──────────────────────────────────────────────────
function renderOrgChart() {
  const container = document.getElementById('org-teams');
  const teams = [
    {
      id: 1, icon: '🎯', name: '团队一·产品研发团队',
      desc: '发现市场痛点 → 验证真实需求 → 评估增长潜力 → 产出完善产品设计',
    },
    {
      id: 2, icon: '⚙️', name: '团队二·技术研发团队',
      desc: '技术可行性评估 → 制定技术方案 → 执行研发 → 产品上线',
    },
    {
      id: 3, icon: '📣', name: '团队三·推广营销团队',
      desc: '多渠道推广 → 用户获取 → 直播变现 → 实现真实收益',
    },
  ];

  container.innerHTML = teams.map(team => {
    const members = state.members.filter(m => m.team === team.id);
    const sorted = [...members].sort((a, b) => (b.is_leader ? 1 : 0) - (a.is_leader ? 1 : 0));
    return `
      <div class="org-team">
        <div class="org-team-header">
          <span class="org-team-icon">${team.icon}</span>
          <div>
            <div class="org-team-name">${team.name}</div>
            <div class="org-team-desc">${team.desc}</div>
          </div>
        </div>
        <div class="org-members">
          ${sorted.map(m => `
            <div class="org-member-card ${m.is_leader ? 'is-leader' : ''}"
              onclick="openProfileModal('${m.id}')">
              <div class="org-member-avatar-lg" style="background:${m.color}">${m.avatar}</div>
              <div class="org-member-name">${m.name} ${m.is_leader ? '<span class="leader-badge">Leader</span>' : ''}</div>
              <div class="org-member-role">${m.role}</div>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  }).join('');
}

// ── 启动 ──────────────────────────────────────────────────────────
init();
