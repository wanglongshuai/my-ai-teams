// ── AI Teams IM — 前端主逻辑（多 Agent 协作版）──────────────────

const API = 'http://localhost:8080';

// ── MBTI 个人面板数据 ─────────────────────────────────────────────
const MEMBER_PROFILE = {
  'zhiyuan':  {
    mbti: 'ENTJ', mbtiName: '指挥官',
    drive: '让正确的产品在正确的时间被正确的人用到',
    traits: ['外向直接，快速推进决策，不喜欢绕弯子', '天然从系统视角看问题，善于识别结构性机会', '以结果为锚，对"没有产出的讨论"容忍度极低', '会挑战所有人的假设，但被数据说服时愿意快速转向'],
    weakness: '有时推进太快，容易忽略团队情绪',
    style: '先说结论，再说依据。句子短，不废话，直接进入核心。',
    quote: '这个方向的用户证据在哪？',
    skills: ['产品战略', '需求验证', 'PRD撰写', '跨团队协调', '路线图规划', '数据决策'],
  },
  'xiaomin':  {
    mbti: 'ENTP', mbtiName: '辩论家',
    drive: '在趋势变成共识之前，第一个看到它',
    traits: ['对新趋势、新模式天然敏感，喜欢探索边界', '能把看似不相关的信号连接成有意义的洞察', '会主动挑战现有假设，不满足于表面答案', '思维发散，有时需要刻意收敛到可执行结论'],
    weakness: '容易被新鲜事物吸引，需克制"什么都想研究"的冲动',
    style: '分享趋势时会附上"反直觉的地方"，喜欢用类比解释复杂现象。',
    quote: '这个信号有意思，但反面论据是……',
    skills: ['市场趋势分析', '竞品研究', '行业报告解读', '信号识别', '用户痛点发现'],
  },
  'jianguo':  {
    mbti: 'INFJ', mbtiName: '提倡者',
    drive: '听懂用户说不出口的那句话',
    traits: ['能快速建立用户信任，挖掘深层动机而非表面诉求', '善于从零散访谈中归纳出系统性洞察', '坚持"用户真实需求"高于"用户说的需求"', '不抢风头，但洞察往往是团队里最深刻的'],
    weakness: '有时过度共情，难以对用户反馈做冷静的优先级排序',
    style: '表达时引用具体用户原话，不轻易下结论，但一旦说出来通常很准。',
    quote: '这位用户说的是 A，但她真正担心的是……',
    skills: ['深度用户访谈', '需求真实性验证', '用户行为分析', '同理心地图', '用户画像'],
  },
  'siyuan':   {
    mbti: 'INTJ', mbtiName: '建筑师',
    drive: '让每一个进入开发的需求都经得起推敲',
    traits: ['天然对所有假设保持怀疑，需要证据才买单', '把碎片化反馈整理成有逻辑的结构', '不受团队情绪影响，敢于说"这是伪需求"', '对"差不多够了"的结论感到不适'],
    weakness: '有时过于挑剔，让团队觉得什么都过不了关',
    style: '直接指出论证漏洞，给结论时会附上置信度说明。',
    quote: '这个假设成立的前提是……但我们没有证据支撑。',
    skills: ['伪需求识别', '反馈数据综合', '假设压力测试', '用户洞察提炼', '优先级判断'],
  },
  'huimin':   {
    mbti: 'ISTJ', mbtiName: '物流师',
    drive: '在团队踩坑之前，先把坑标出来',
    traits: ['不相信"感觉应该没问题"，只相信有据可查的评估', '能发现别人忽略的执行风险和边界条件', '每次输出都有清晰的结构和可追溯的依据', '宁可高估风险，也不愿低估'],
    weakness: '有时过于保守，会让团队觉得"做什么都有风险"',
    style: '用矩阵或清单呈现风险，遇到高风险项会反复强调直到团队确认已知晓。',
    quote: '这个方向有 3 个高风险项，我逐一说明。',
    skills: ['市场风险评估', '竞争风险分析', '执行风险识别', '风险矩阵', '尽职调查'],
  },
  'mingyuan': {
    mbti: 'ESTJ', mbtiName: '总经理',
    drive: '好产品也要有好生意，两者缺一不可',
    traits: ['只关心能落地、能变现的商业路径', '评估商业模式时会拆解每一个假设的可靠性', '不喜欢"长远来看"的模糊表达，要求具体数字', '在商业判断上有自己的立场，不容易被说服'],
    weakness: '有时对用户价值关注不足，过于聚焦财务指标',
    style: '说话干脆，直接给结论和数字，不喜欢"可能""也许"。',
    quote: '这个方向的 LTV 是多少？CAC 能控制在什么范围？',
    skills: ['商业模式设计', '增长潜力评估', '变现路径分析', '财务建模', '定价策略', '市场规模测算'],
  },
  'yalin':    {
    mbti: 'INTP', mbtiName: '逻辑学家',
    drive: '把模糊的需求变成清晰的结构',
    traits: ['天然把复杂系统拆解成清晰的层次和关系', '不满足于"能用"，要找到最简洁的架构方案', '不受既有设计模式束缚，愿意从第一原理出发', '进入设计状态后思维深度极强，不喜欢被打断'],
    weakness: '有时过于追求完美结构，导致交付延迟',
    style: '精准表达，善用图和流程图，喜欢从"为什么这样设计"开始解释。',
    quote: '这个流程有个边界条件没有处理……',
    skills: ['产品架构设计', '用户流程设计', '信息架构', '交互框架', '需求结构化', '原型设计'],
  },
  'jiaxin':   {
    mbti: 'ISFP', mbtiName: '探险家',
    drive: '让界面有温度，让用户感受到被照顾',
    traits: ['对视觉细节极度敏感，能感知别人注意不到的不协调', '设计出发点始终是"用户用起来舒不舒服"', '温和低调，用作品说话', '有时凭直觉做出的设计决策比理性推导更准确'],
    weakness: '不擅长主动表达设计意图，需要被问才会详细解释',
    style: '话不多，每次输出都经过认真打磨。倾向于展示而非描述。',
    quote: '我做了两个版本，你看哪个更顺眼？',
    skills: ['UI设计', '设计系统', '视觉规范', '组件库', '色彩理论', '字体排版', 'Figma'],
  },
  'zihao':    {
    mbti: 'INTJ', mbtiName: '建筑师',
    drive: '设计经得起时间考验的系统',
    traits: ['在写第一行代码前，已经想清楚三个月后的演进路径', '对"凑合能跑"的方案有生理性排斥', '不需要外部认可，自己的判断就是标准', '在技术争论中不动感情，只看逻辑和数据'],
    weakness: '有时对团队成员的能力边界估计过高，导致沟通成本增加',
    style: '说话精炼，直接说"我的判断是 X，原因是 Y，风险是 Z"。',
    quote: '这个架构在 10 万用户时会出问题，我们换个方向。',
    skills: ['系统架构设计', '技术选型', 'DDD领域驱动设计', '架构决策记录', '技术债务管理'],
  },
  'haoran':   {
    mbti: 'ISTP', mbtiName: '鉴赏家',
    drive: '系统要稳，代码要干净，性能要够',
    traits: ['比起讨论，更喜欢直接写代码验证想法', '遇到线上问题不慌，快速定位、快速修复', '给任务就能自己跑，不需要频繁同步', '代码和表达都追求最小化，不写多余的东西'],
    weakness: '不擅长主动同步进度，有时让团队觉得"不知道他在干嘛"',
    style: '话少，但说的都是关键信息。遇到问题会先自己研究，确实卡住了才来找人。',
    quote: '我测了一下，瓶颈在数据库查询这里。',
    skills: ['后端架构', 'API设计', '数据库优化', '微服务', '性能调优', 'Redis', '消息队列'],
  },
  'yuxin':    {
    mbti: 'ENFP', mbtiName: '活动家',
    drive: '让用户第一眼就爱上这个界面',
    traits: ['不满足于"实现设计稿"，会主动提出交互改进建议', '喜欢和设计师、后端一起讨论，推动跨职能协作', '写代码时脑子里始终有"用户用起来是什么感受"', '需求变化时不抱怨，快速调整'],
    weakness: '有时想法太多，容易超出当前迭代的范围',
    style: '活跃，会主动分享想法，喜欢用"如果我们……会怎样？"来引发讨论。',
    quote: '这个动效我觉得可以更流畅一点，我试了个版本……',
    skills: ['React', 'Vue', 'TypeScript', 'CSS动效', '响应式布局', '性能优化', '组件封装'],
  },
  'bowen':    {
    mbti: 'INTP', mbtiName: '逻辑学家',
    drive: '把复杂问题拆解到最简单的解法',
    traits: ['遇到复杂技术问题会反复推敲，直到找到本质原因', '对"能跑但很丑"的代码有强烈的重构冲动', '代码逻辑清晰，边界条件处理周全', '沉浸编码状态时效率极高，不喜欢被频繁打断'],
    weakness: '有时过度思考，在简单问题上花了太多时间',
    style: '说话精准，喜欢把问题拆解后再回答，遇到不确定的地方会明确说"需要验证"。',
    quote: '这个 bug 的根本原因是……',
    skills: ['核心功能开发', '算法优化', '代码重构', '复杂业务逻辑', '单元测试', '问题定位'],
  },
  'chenxi':   {
    mbti: 'ENTP', mbtiName: '辩论家',
    drive: '用最快的速度证明一个想法能不能跑通',
    traits: ['2 天内跑通原型是常规操作，不追求完美只追求验证', '喜欢接手"没人知道能不能做"的技术探索任务', '一个问题能想出 5 种实现路径，然后选最快的那条', '把"原型跑不通"视为有价值的结论，不是失败'],
    weakness: '原型代码质量较低，需要他人接手正式实现',
    style: '能量高，喜欢边做边讲，会把验证过程中的发现实时同步给团队。',
    quote: '我跑了个 demo，结论是可行，但有个坑……',
    skills: ['快速原型', '技术可行性验证', 'POC开发', '技术选型调研', '全栈开发'],
  },
  'pengcheng':{
    mbti: 'ISTJ', mbtiName: '物流师',
    drive: '流程要自动化，部署要可回滚，一切要可追溯',
    traits: ['坚守流程和规范，不接受"这次先跳过"', '承诺的事情一定完成，不会给团队意外', 'CI/CD 配置、环境变量、权限设置，每个细节都要对', '上线前一定要有回滚方案，没有就不上'],
    weakness: '有时过于保守，对新工具的接受速度较慢',
    style: '说话严谨，喜欢用清单和流程图，不喜欢口头承诺。',
    quote: '回滚方案确认了吗？',
    skills: ['CI/CD', '基础设施自动化', 'Docker/K8s', '监控告警', '生产部署', '安全加固', 'IaC'],
  },
  'siqi':     {
    mbti: 'INTJ', mbtiName: '建筑师',
    drive: '没有经过审查的代码，不应该进生产',
    traits: ['对代码质量有明确的内部标准，不会因为"时间紧"降低要求', '审查时不只看当前代码，会考虑对整体架构的影响', 'Review 评论直接指出问题，不会为了照顾情绪而模糊措辞', '不因为是 Leader 写的代码就放水'],
    weakness: '有时 Review 颗粒度过细，让开发者觉得压力大',
    style: '评论精准有力，区分"必须改"和"建议改"，遇到设计层面问题直接升级讨论。',
    quote: '这里有个潜在的竞态条件，必须修复。',
    skills: ['代码审查', '安全审计', '性能分析', '代码规范', '重构建议', '技术债务识别'],
  },
  'jianping': {
    mbti: 'ESTJ', mbtiName: '总经理',
    drive: '让每个任务都有人负责、有时间节点、有明确结果',
    traits: ['把方案拆解成任务、分配责任人、跟进进度，一气呵成', '喜欢清单、甘特图、状态看板，不喜欢"大概差不多"', '项目延期会让他感到不安，会提前识别风险并推动解决', '不喜欢绕弯子，会直接问"这个任务什么时候能完成"'],
    weakness: '有时推进节奏太紧，让团队感到压力',
    style: '沟通高效，每次同步都有明确议题和结论，不开没有结果的会。',
    quote: '这个任务的 owner 是谁？',
    skills: ['项目计划', '任务拆解', '进度跟踪', '风险管理', '里程碑管理', '跨团队协调', 'Scrum/Kanban'],
  },
  'jiaqi':    {
    mbti: 'ENTJ', mbtiName: '指挥官',
    drive: '用数据和实验驱动增长，拿到真实收益',
    traits: ['只关心能被追踪、能被优化、能带来实际转化的增长动作', '数据说话，快速拍板，不拖延', '同时管理 8 个渠道，能快速识别哪个值得加码', '对团队成员的输出有明确预期，不接受模糊的"效果还不错"'],
    weakness: '有时推进太快，给执行层带来压力',
    style: '沟通直接，以数据为语言，不接受没有指标支撑的判断。',
    quote: '这个渠道的 CAC 是多少？',
    skills: ['增长战略', '渠道管理', '数据驱动决策', 'A/B测试', '用户获取', '转化率优化', '预算分配'],
  },
  'shihan':   {
    mbti: 'ESFP', mbtiName: '表演者',
    drive: '让用户在刷到内容的那一刻就心动',
    traits: ['内容天然有温度，能让用户产生共鸣和信任', '对小红书的视觉风格和文案调性极度敏感', '喜欢和 KOL/KOC 建立真实关系，而不是纯商务合作', '喜欢看到内容发出去后的实时互动数据'],
    weakness: '有时过于追求"好看"，对转化率的关注不够系统',
    style: '活泼有趣，分享内容时会带着自己的感受，让人很快进入状态。',
    quote: '这个封面太吸睛了，用户一定会停下来！',
    skills: ['小红书种草', 'KOL/KOC合作', '内容策划', '爆款公式', '社区运营', '品牌种草'],
  },
  'yuhang':   {
    mbti: 'ESTP', mbtiName: '企业家',
    drive: '抓住算法的节奏，把流量变成用户',
    traits: ['不喜欢过度分析，先发出去再看数据调整', '对抖音推荐机制有强烈的感知，能快速判断内容潜力', '时刻关注竞品在做什么，要比他们快一步', '能在短时间内产出大量内容想法，不怕试错'],
    weakness: '有时行动太快，缺乏系统性的内容规划',
    style: '节奏快，喜欢直接说"我们现在就试"，直接给播放量、完播率、涨粉数。',
    quote: '这条视频前 3 秒没钩子，重做。',
    skills: ['抖音算法', '短视频策划', '爆款内容', 'DOU+投放', '达人合作', '直播引流', '内容矩阵'],
  },
  'wenjing':  {
    mbti: 'ISFJ', mbtiName: '守护者',
    drive: '让每一个进入私域的用户都感受到被照顾',
    traits: ['记得用户的偏好、生日、上次咨询的问题', '私域运营是长线工作，她不急于求成', '用真诚的服务让用户从"路人"变成"忠粉"', '社群运营节奏稳定，用户知道什么时候会有推送'],
    weakness: '有时过于保守，不敢尝试大胆的私域转化动作',
    style: '说话温柔，让用户感觉在和朋友聊天而不是被推销。',
    quote: '您上次问的问题，我帮您整理了一个答案……',
    skills: ['微信私域运营', '社群管理', '用户留存', '复购策略', '企微SCRM', '用户分层运营'],
  },
  'xiaotong': {
    mbti: 'ENFP', mbtiName: '活动家',
    drive: '用一句话让用户停下来，用一篇文章让用户记住你',
    traits: ['每天能产出大量内容想法，脑子里总有新角度', '能快速切换到不同平台的用户视角写内容', '写出来的内容有温度，让人感觉是真人在说话', '能同时为小红书、抖音、微信写不同风格的内容'],
    weakness: '有时想法太多，需要帮助聚焦到最优先的内容任务',
    style: '充满热情，分享内容方案时会带着代入感，喜欢问"我们想让用户看完之后做什么"。',
    quote: '这个角度没人写过，我们来做第一个！',
    skills: ['多平台内容创作', '文案撰写', '小红书笔记', '抖音脚本', '微信推文', '广告文案'],
  },
  'mengqi':   {
    mbti: 'ESFJ', mbtiName: '执政官',
    drive: '让直播间每一分钟都在产生转化',
    traits: ['天然适合直播环境，能快速感知观众情绪并调整节奏', '把观众当朋友，而不是流量，建立真实的信任感', '话术、选品、排品、逼单时机，每个环节都有标准', '喜欢和主播、运营、投流紧密配合'],
    weakness: '有时过于关注氛围，对数据分析的深度不够',
    style: '热情务实，复盘时把"场感"和数据结合起来分析，讲解话术时直接示范。',
    quote: '这个逼单话术要在库存倒计时的时候说，效果最好。',
    skills: ['直播话术设计', '选品排品', '直播间运营', '转化率优化', '主播培训', 'GMV管理'],
  },
  'zhiqiang': {
    mbti: 'ESTJ', mbtiName: '总经理',
    drive: '每一分预算都要有可衡量的回报',
    traits: ['对 ROI、CPC、CTR、转化率的变化极度敏感', '账户结构、出价策略、素材分组，每个环节都有明确的逻辑', '预算分配有纪律，不会因为"感觉不错"就随意加量', '只问"花了多少、带来了多少"，不关心过程是否优雅'],
    weakness: '有时过于保守，在有效渠道上加量不够果断',
    style: '汇报时全是数字，说话直接，不喜欢绕弯子。',
    quote: '这个计划的 ROI 跌破 2 了，今天暂停。',
    skills: ['SEM竞价', '信息流广告', 'DOU+投放', '账户结构优化', '出价策略', 'ROI管理', '预算分配'],
  },
  'yawen':    {
    mbti: 'ENFJ', mbtiName: '主人公',
    drive: '让品牌在每个平台上都有自己的声音和存在感',
    traits: ['善于把多个平台的内容和节奏统一到一个品牌叙事下', '时刻思考"这个内容在用户心里留下了什么印象"', '能协调多个渠道策略保持一致', '不只看当下，会提前规划节点营销和话题造势'],
    weakness: '有时过于追求"品牌调性"，对短期转化目标关注不够',
    style: '视野开阔，说话有感召力，善于把大家的工作连接成一个整体故事。',
    quote: '这次上市我们的核心叙事是……各平台围绕这个主题展开。',
    skills: ['多平台上市策略', '品牌叙事', '内容日历统筹', '话题营销', 'KOL矩阵规划', '渠道协同'],
  },
  'botao':    {
    mbti: 'INTP', mbtiName: '逻辑学家',
    drive: '让数据说话，让直觉靠边站',
    traits: ['分析结论有完整的推导链，不跳过中间步骤', '对"看起来不错"的数据会反复验证，找出可能的干扰因素', '宁可花更多时间把一个问题分析透，也不愿浅尝辄止', '数据不好看就是不好看，不会为了让人开心而美化结论'],
    weakness: '有时分析太深，输出报告过于复杂，让团队难以快速消化',
    style: '报告结构清晰，结论明确，先说结论再展开数据支撑。',
    quote: '这个渠道的转化率下降了 23%，根本原因是……',
    skills: ['增长数据分析', '渠道效果评估', 'A/B测试分析', '漏斗分析', '数据可视化', 'SQL'],
  },
};

// MBTI 类型颜色映射
const MBTI_COLOR = {
  'ENTJ': '#1677ff', 'INTJ': '#2f54eb', 'ENTP': '#722ed1', 'INTP': '#531dab',
  'ENTJ': '#1677ff', 'ENFJ': '#08979c', 'INFJ': '#006d75', 'ENFP': '#d4380d',
  'INFP': '#ad4e00', 'ESTJ': '#389e0d', 'ISTJ': '#237804', 'ESTP': '#d48806',
  'ISTP': '#ad6800', 'ESFJ': '#c41d7f', 'ISFJ': '#9e1068', 'ESFP': '#cf1322',
  'ISFP': '#a8071a',
};

// ── 个性化头像系统 ────────────────────────────────────────────────
// 每个成员的专属配置：渐变色对 + 职业 emoji
const MEMBER_AVATAR_CONFIG = {
  // 团队一：产品研发
  'zhiyuan':  { grad: ['#667eea','#764ba2'], emoji: '🎯' },
  'xiaomin':  { grad: ['#f093fb','#f5576c'], emoji: '📊' },
  'jianguo':  { grad: ['#4facfe','#00f2fe'], emoji: '🔍' },
  'siyuan':   { grad: ['#43e97b','#38f9d7'], emoji: '✅' },
  'huimin':   { grad: ['#fa709a','#fee140'], emoji: '⚠️' },
  'mingyuan': { grad: ['#a18cd1','#fbc2eb'], emoji: '💹' },
  'yalin':    { grad: ['#ffecd2','#fcb69f'], emoji: '🏗️' },
  'jiaxin':   { grad: ['#ff9a9e','#fecfef'], emoji: '🎨' },
  // 团队二：技术研发
  'zihao':    { grad: ['#2196f3','#21cbf3'], emoji: '⚡' },
  'haoran':   { grad: ['#1a237e','#283593'], emoji: '🖥️' },
  'yuxin':    { grad: ['#00bcd4','#26c6da'], emoji: '💻' },
  'bowen':    { grad: ['#00897b','#26a69a'], emoji: '🔧' },
  'chenxi':   { grad: ['#43a047','#66bb6a'], emoji: '🚀' },
  'pengcheng':{ grad: ['#e65100','#ef6c00'], emoji: '⚙️' },
  'siqi':     { grad: ['#546e7a','#78909c'], emoji: '🔎' },
  'jianping': { grad: ['#37474f','#546e7a'], emoji: '📋' },
  // 团队三：推广营销
  'jiaqi':    { grad: ['#11998e','#38ef7d'], emoji: '📈' },
  'shihan':   { grad: ['#ff6b6b','#feca57'], emoji: '📱' },
  'yuhang':   { grad: ['#1a1a2e','#16213e'], emoji: '🎬' },
  'wenjing':  { grad: ['#134e5e','#71b280'], emoji: '💬' },
  'xiaotong': { grad: ['#f7971e','#ffd200'], emoji: '✍️' },
  'mengqi':   { grad: ['#8e2de2','#4a00e0'], emoji: '🎙️' },
  'zhiqiang': { grad: ['#c94b4b','#4b134f'], emoji: '💰' },
  'yawen':    { grad: ['#005c97','#363795'], emoji: '📣' },
  'botao':    { grad: ['#373b44','#4286f4'], emoji: '📉' },
};

// 用户（我）的头像配置
const USER_AVATAR_CONFIG = { grad: ['#1677ff','#0958d9'], emoji: '👤' };

/**
 * 生成个性化 SVG 头像 HTML
 * @param {string} memberId - 成员 ID，null 表示用户自己
 * @param {number} size - 头像尺寸（px）
 * @returns {string} - 可直接插入 innerHTML 的 SVG 字符串
 */
function buildAvatarSvg(memberId, size = 36) {
  const cfg = memberId ? (MEMBER_AVATAR_CONFIG[memberId] || { grad: ['#718096','#4a5568'], emoji: '🤖' }) : USER_AVATAR_CONFIG;
  const [c1, c2] = cfg.grad;
  const gradId = `g_${memberId || 'user'}_${size}`;
  const fontSize = Math.round(size * 0.44);
  return `<svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="${gradId}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="${c1}"/>
      <stop offset="100%" stop-color="${c2}"/>
    </linearGradient>
    <clipPath id="cp_${gradId}"><circle cx="${size/2}" cy="${size/2}" r="${size/2}"/></clipPath>
  </defs>
  <circle cx="${size/2}" cy="${size/2}" r="${size/2}" fill="url(#${gradId})"/>
  <text x="${size/2}" y="${size/2}" dominant-baseline="central" text-anchor="middle"
    font-size="${fontSize}" style="user-select:none">${cfg.emoji}</text>
</svg>`;
}

/**
 * 生成头像容器 div（替代原来纯色 div）
 * @param {string|null} memberId
 * @param {number} size
 * @param {string} extraClass
 * @param {string} extraStyle
 * @param {string} extraAttr - 额外 HTML 属性
 */
function buildAvatarDiv(memberId, size, extraClass = '', extraStyle = '', extraAttr = '') {
  return `<div class="${extraClass}" style="width:${size}px;height:${size}px;border-radius:50%;overflow:hidden;flex-shrink:0;${extraStyle}" ${extraAttr}>${buildAvatarSvg(memberId, size)}</div>`;
}

// 状态
let state = {
  members: [],
  groups: [],
  currentGroupId: null,
  currentGroupMembers: [],
  selectedResponder: '',
  sending: false,
  // SSE
  sseSource: null,
  lastMsgId: 0,
  lastEventId: 0,
  renderedMsgIds: new Set(),
  // 任务
  tasks: [],
  currentTaskId: null,
  taskFilter: 'all',
  activeTaskIds: new Set(),
  // P0 新增
  replyTo: null,
  mentionSearch: '',
  mentionIndex: 0,
  // 连续消息合并：记录最后一条消息的发送者和时间
  lastRenderedSenderId: null,
  lastRenderedTime: null,
  // 群组最后一条消息缓存
  groupLastMessages: {},
  // 终端面板
  terminalStepId: null,
  // 内嵌终端（聊天区域实时日志）
  inlineTerminalStepId: null,
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
    // 定期刷新任务看板
    setInterval(refreshTaskBadge, 5000);
    // 定期检测跨团队移交通知（每 8 秒）
    setInterval(checkHandoffNotifications, 8000);
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
  if (view === 'tasks') loadTaskBoard();
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
  const lastMsg = state.groupLastMessages[g.id];
  const lastMsgText = lastMsg
    ? escapeHtml(lastMsg.slice(0, 20)) + (lastMsg.length > 20 ? '…' : '')
    : escapeHtml(getGroupMeta(g));
  div.innerHTML = `
    <div class="group-avatar" style="background:${color}">${icon}</div>
    <div class="group-info">
      <div class="group-name">${g.name}</div>
      <div class="group-meta group-last-msg">${lastMsgText}</div>
    </div>
  `;
  return div;
}

function updateGroupLastMsg(groupId, content) {
  if (!content) return;
  // 去掉 markdown 符号，取纯文本预览
  const plain = content.replace(/[#*`>\-_~\[\]]/g, '').replace(/\n/g, ' ').trim();
  state.groupLastMessages[groupId] = plain;
  // 更新侧边栏对应项
  const el = document.querySelector(`.group-item[data-group-id="${groupId}"] .group-last-msg`);
  if (el) {
    el.textContent = plain.slice(0, 20) + (plain.length > 20 ? '…' : '');
  }
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

function getMemberByName(name) {
  return state.members.find(m => m.name === name);
}

// ── 打开群组 ──────────────────────────────────────────────────────
async function openGroup(groupId) {
  state.currentGroupId = groupId;
  state.selectedResponder = '';
  clearGroupUnreadDot(groupId);

  document.querySelectorAll('.group-item').forEach(el => {
    el.classList.toggle('active', el.dataset.groupId === groupId);
  });

  const group = state.groups.find(g => g.id === groupId);
  if (!group) return;

  state.currentGroupMembers = (group.members || []).map(id => getMember(id)).filter(Boolean);

  document.getElementById('chat-empty').classList.add('hidden');
  const chatPanel = document.getElementById('chat-panel');
  chatPanel.classList.remove('hidden');
  chatPanel.classList.remove('fade-in');
  // 触发重排以重新播放动画
  void chatPanel.offsetWidth;
  chatPanel.classList.add('fade-in');

  document.getElementById('chat-title').textContent = group.name;
  document.getElementById('chat-subtitle').textContent =
    group.type === 'direct' ? '' : `${group.members?.length || 0} 人`;

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

  renderInfoPanel(group);
  await loadMessages(groupId);

  // 启动 SSE 监听
  startSSE(groupId);

  document.getElementById('msg-input').focus();
}

function setResponder(val) {
  state.selectedResponder = val;
}

// ── SSE 实时推送 ──────────────────────────────────────────────────
function startSSE(groupId) {
  if (state.sseSource) {
    state.sseSource.close();
    state.sseSource = null;
  }

  const url = `${API}/api/events/${groupId}?last_msg_id=${state.lastMsgId}&last_event_id=${state.lastEventId}`;
  const es = new EventSource(url);
  state.sseSource = es;

  es.addEventListener('message', (e) => {
    try {
      const msg = JSON.parse(e.data);
      // 更新 lastMsgId（包括用户消息，防止重连时重复）
      state.lastMsgId = Math.max(state.lastMsgId, msg.id);
      // 只渲染 AI/系统消息，用户消息已本地渲染
      if (msg.sender_id !== 'user') {
        if (!state.renderedMsgIds.has(msg.id)) {
          state.renderedMsgIds.add(msg.id);
          renderMessage(msg);
          // AI 消息到达后隐藏内嵌终端
          if (state.inlineTerminalStepId) {
            hideInlineTerminal();
            hideTyping();
          }
        }
      }
    } catch (err) {
      console.error('SSE message parse error', err);
    }
  });

  es.addEventListener('task_event', (e) => {
    try {
      const ev = JSON.parse(e.data);
      state.lastEventId = Math.max(state.lastEventId, ev.id || 0);
      handleTaskEvent(ev);
    } catch (err) {}
  });

  es.onerror = () => {
    // 重连时使用最新的 lastMsgId 重新建立连接
    es.close();
    state.sseSource = null;
    setTimeout(() => {
      if (state.currentGroupId === groupId) {
        startSSE(groupId);
      }
    }, 2000);
  };
}

function handleTaskEvent(ev) {
  const { event_type, payload, task_id } = ev;
  const tid = payload.task_id || task_id;

  if (event_type === 'task_created' || event_type === 'task_running') {
    state.activeTaskIds.add(tid);
    updateTaskIndicator(true);
    refreshTaskBadge();
    if (!document.getElementById('view-tasks').classList.contains('hidden')) {
      loadTaskBoard();
      if (state.currentTaskId === tid) loadTaskDetail(tid);
    }
  } else if (event_type === 'step_started') {
    const name = payload.member_name || '';
    showTypingFor(name);
    if (state.currentTaskId && !document.getElementById('view-tasks').classList.contains('hidden')) {
      loadTaskDetail(state.currentTaskId);
    }
    // 自动切换终端到新启动的步骤
    if (payload.step_id) {
      openTerminalForStep(payload.step_id, payload.member_name || '', true);
    }
  } else if (event_type === 'step_completed' || event_type === 'step_failed') {
    hideTyping();
    if (state.currentTaskId && !document.getElementById('view-tasks').classList.contains('hidden')) {
      loadTaskDetail(state.currentTaskId);
    }
    if (event_type === 'step_completed' && state.terminalStepId === payload.step_id) {
      appendTerminalLine('system', '— 步骤完成 —');
    }
  } else if (event_type === 'step_log') {
    // 实时追加日志到任务看板终端
    if (state.terminalStepId === payload.step_id) {
      appendTerminalLine(payload.log_type, payload.content);
    }
    // 实时追加日志到聊天区域内嵌终端
    if (state.inlineTerminalStepId === payload.step_id) {
      appendInlineTerminalLine(payload.log_type, payload.content);
    }
  } else if (event_type === 'task_completed' || event_type === 'task_failed') {
    hideTyping();
    state.activeTaskIds.delete(tid);
    if (state.activeTaskIds.size === 0) updateTaskIndicator(false);
    refreshTaskBadge();
    if (!document.getElementById('view-tasks').classList.contains('hidden')) {
      loadTaskBoard();
      if (state.currentTaskId) loadTaskDetail(state.currentTaskId);
    }
  }
}

// ── 终端面板 ──────────────────────────────────────────────────────

async function openTerminalForStep(stepId, memberName, autoScroll = false) {
  state.terminalStepId = stepId;
  const body = document.getElementById('terminal-body');
  const label = document.getElementById('terminal-member-label');
  if (label) label.textContent = memberName ? `● ${memberName}` : '';
  body.innerHTML = '';

  // 加载已有日志
  try {
    const logs = await fetch(`${API}/api/step-logs/${stepId}`).then(r => r.json());
    if (logs.length === 0) {
      body.innerHTML = '<div class="terminal-placeholder">等待执行中...</div>';
    } else {
      for (const log of logs) {
        appendTerminalLine(log.log_type, log.content, false);
      }
    }
  } catch (e) {
    body.innerHTML = '<div class="terminal-placeholder" style="color:#f38ba8">加载失败</div>';
  }
  if (autoScroll) terminalScrollToBottom();

  // 高亮选中的步骤行
  document.querySelectorAll('.step-row.selected').forEach(el => el.classList.remove('selected'));
  const stepEl = document.querySelector(`.step-row[data-step-id="${stepId}"]`);
  if (stepEl) stepEl.classList.add('selected');
}

function appendTerminalLine(logType, content, scroll = true) {
  const body = document.getElementById('terminal-body');
  // 移除 placeholder
  const ph = body.querySelector('.terminal-placeholder');
  if (ph) ph.remove();

  if (logType === 'text') {
    // 文字可能是增量片段，按换行拆分
    const lines = content.split('\n');
    for (const line of lines) {
      if (!line) continue;
      const div = document.createElement('div');
      div.className = 'terminal-line text';
      div.textContent = line;
      body.appendChild(div);
    }
  } else if (logType === 'tool_call') {
    const div = document.createElement('div');
    div.className = 'terminal-line tool_call';
    div.textContent = content;
    body.appendChild(div);
  } else if (logType === 'tool_result') {
    const lines = content.split('\n');
    for (const line of lines) {
      if (!line) continue;
      const div = document.createElement('div');
      div.className = 'terminal-line tool_result';
      div.textContent = line;
      body.appendChild(div);
    }
  } else if (logType === 'system') {
    const div = document.createElement('div');
    div.className = 'terminal-line system';
    div.textContent = content;
    body.appendChild(div);
  }

  if (scroll) terminalScrollToBottom();
}

function terminalScrollToBottom() {
  const body = document.getElementById('terminal-body');
  if (body) body.scrollTop = body.scrollHeight;
}

function clearTerminal() {
  const body = document.getElementById('terminal-body');
  body.innerHTML = '<div class="terminal-placeholder">← 点击步骤查看实时执行过程</div>';
  state.terminalStepId = null;
  document.getElementById('terminal-member-label').textContent = '';
  document.querySelectorAll('.step-row.selected').forEach(el => el.classList.remove('selected'));
}

// ── 内嵌终端（聊天区域实时执行日志）────────────────────────────────
function showInlineTerminal() {
  const el = document.getElementById('inline-terminal');
  if (!el) return;
  document.getElementById('inline-terminal-body').innerHTML = '';
  document.getElementById('inline-terminal-title').textContent = '正在处理...';
  el.classList.remove('hidden');
  scrollToBottom();
}

function hideInlineTerminal() {
  const el = document.getElementById('inline-terminal');
  if (el) el.classList.add('hidden');
  state.inlineTerminalStepId = null;
}

function toggleInlineTerminal() {
  const body = document.getElementById('inline-terminal-body');
  const btn = document.querySelector('.term-toggle');
  if (!body || !btn) return;
  if (body.style.display === 'none') {
    body.style.display = '';
    btn.textContent = '收起';
  } else {
    body.style.display = 'none';
    btn.textContent = '展开';
  }
}

function appendInlineTerminalLine(logType, content) {
  const body = document.getElementById('inline-terminal-body');
  if (!body) return;
  const div = document.createElement('div');
  div.className = `iterm-line ${logType}`;
  div.textContent = content;
  body.appendChild(div);
  body.scrollTop = body.scrollHeight;
}

function showTypingFor(memberName) {
  const typingEl = document.getElementById('typing-indicator');
  const typingName = document.getElementById('typing-name');
  typingName.textContent = memberName;
  typingEl.classList.remove('hidden');
  scrollToBottom();
}

function hideTyping() {
  document.getElementById('typing-indicator').classList.add('hidden');
}

function updateTaskIndicator(active) {
  const indicator = document.getElementById('task-indicator');
  if (active) {
    indicator.classList.remove('hidden');
  } else {
    indicator.classList.add('hidden');
  }
}

async function refreshTaskBadge() {
  try {
    const tasks = await fetch(`${API}/api/tasks`).then(r => r.json());
    state.tasks = tasks;
    const running = tasks.filter(t => t.status === 'running' || t.status === 'planning').length;
    const badge = document.getElementById('task-running-badge');
    if (running > 0) {
      badge.textContent = running;
      badge.classList.remove('hidden');
    } else {
      badge.classList.add('hidden');
    }
  } catch (e) {}
}

// ── 跨团队移交通知 ────────────────────────────────────────────────
// 记录已见过的 handoff 消息 ID，避免重复提示
const seenHandoffIds = new Set();

async function checkHandoffNotifications() {
  try {
    const data = await fetch(`${API}/api/group-stats`).then(r => r.json());
    const handoffs = data.handoffs || [];
    for (const h of handoffs) {
      if (seenHandoffIds.has(h.id)) continue;
      seenHandoffIds.add(h.id);
      // 如果不是当前群组，在侧边栏显示红点
      if (h.group_id !== state.currentGroupId) {
        showGroupUnreadDot(h.group_id);
        // 顶部简短提示
        showHandoffToast(h.group_id, h.content);
      }
    }
  } catch (e) {}
}

function showGroupUnreadDot(groupId) {
  const el = document.querySelector(`.group-item[data-group-id="${groupId}"]`);
  if (!el) return;
  if (el.querySelector('.group-unread-dot')) return; // 已有红点
  const dot = document.createElement('div');
  dot.className = 'group-unread-dot';
  dot.style.cssText = 'width:8px;height:8px;border-radius:50%;background:#e53e3e;position:absolute;top:8px;right:8px;';
  el.style.position = 'relative';
  el.appendChild(dot);
}

function clearGroupUnreadDot(groupId) {
  const el = document.querySelector(`.group-item[data-group-id="${groupId}"] .group-unread-dot`);
  if (el) el.remove();
}

function showHandoffToast(groupId, content) {
  const group = state.groups.find(g => g.id === groupId);
  const groupName = group ? group.name : groupId;
  // 提取移交任务名
  const match = content.match(/任务：(.+)/);
  const taskName = match ? match[1] : '新任务';

  const toast = document.createElement('div');
  toast.style.cssText = `
    position:fixed;top:60px;right:20px;z-index:9999;
    background:#1677ff;color:#fff;padding:10px 16px;border-radius:8px;
    font-size:13px;max-width:280px;cursor:pointer;
    box-shadow:0 4px 12px rgba(0,0,0,0.2);
    animation:slideIn 0.3s ease;
  `;
  toast.innerHTML = `📨 <b>跨团队移交</b><br>${groupName}：${escapeHtml(taskName)}`;
  toast.onclick = () => { openGroup(groupId); toast.remove(); };
  document.body.appendChild(toast);
  setTimeout(() => { if (toast.parentNode) toast.remove(); }, 6000);
}

// ── 消息加载与渲染 ────────────────────────────────────────────────
async function loadMessages(groupId) {
  const container = document.getElementById('messages');
  container.innerHTML = '<div style="text-align:center;color:#999;font-size:13px;padding:20px">加载中...</div>';
  state.renderedMsgIds.clear();
  state.lastMsgId = 0;
  // 重置连续消息合并状态
  state.lastRenderedSenderId = null;
  state.lastRenderedTime = null;

  try {
    const msgs = await fetch(`${API}/api/messages/${groupId}`).then(r => r.json());
    container.innerHTML = '';
    for (const msg of msgs) {
      state.renderedMsgIds.add(msg.id);
      state.lastMsgId = Math.max(state.lastMsgId, msg.id);
      renderMessage(msg, false);
    }
    scrollToBottom();
  } catch (e) {
    container.innerHTML = '<div style="text-align:center;color:#e53e3e;font-size:13px;padding:20px">加载失败</div>';
  }
}

function renderMessage(msg, scroll = true) {
  const container = document.getElementById('messages');
  const isUser = msg.sender_id === 'user';
  const isSystem = msg.sender_id === 'system';
  // 收到新消息时隐藏 typing（如果是 AI/系统消息）
  if (!isUser && scroll) hideTyping();
  const member = (!isUser && !isSystem) ? getMember(msg.sender_id) : null;

  const div = document.createElement('div');

  if (isSystem) {
    // 系统消息（任务状态）
    div.className = 'message system-msg';
    div.innerHTML = `<div class="system-bubble">${renderMarkdown(msg.content)}</div>`;
    container.appendChild(div);
    if (scroll) scrollToBottom();
    // 系统消息重置合并状态（打断连续性）
    state.lastRenderedSenderId = null;
    state.lastRenderedTime = null;
    return;
  }

  const isCollab = !isUser && member && msg.mention_users && msg.mention_users.length > 0;
  div.className = `message ${isUser ? 'from-user' : 'from-ai'}${(!isUser && member) ? ' is-ai-agent' : ''}${isCollab ? ' is-collab' : ''}`;
  if (msg.id) div.dataset.msgId = msg.id;

  const senderName = isUser ? '我' : (member?.name || msg.sender_id);
  const time = formatTime(msg.created_at);

  // 连续消息合并：同一发送者5分钟内不重复显示时间戳和发送者名
  const msgTime = msg.created_at ? new Date(msg.created_at).getTime() : Date.now();
  const sameGroup = state.lastRenderedSenderId === msg.sender_id;
  const within5min = state.lastRenderedTime && (msgTime - state.lastRenderedTime) < 5 * 60 * 1000;
  const isConsecutive = sameGroup && within5min;
  state.lastRenderedSenderId = msg.sender_id;
  state.lastRenderedTime = msgTime;

  // 更新侧边栏最后消息预览
  if (state.currentGroupId) {
    updateGroupLastMsg(state.currentGroupId, msg.content);
  }

  // 先 markdown 渲染，再做 @高亮替换（避免 marked 转义 span 标签）
  let htmlContent = renderMarkdown(msg.content || '');
  for (const m of state.currentGroupMembers) {
    htmlContent = htmlContent.replace(
      new RegExp('@' + m.name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'),
      `<span class="mention">@${escapeHtml(m.name)}</span>`
    );
  }

  const replyBlock = renderReplyQuote(msg.reply_to ?? null);
  const msgIdAttr = msg.id ? msg.id : '';
  const replyBtn = msgIdAttr
    ? `<button class="msg-toolbar-btn reply-btn"
        data-msg-id="${msgIdAttr}"
        data-sender="${escapeHtml(senderName)}"
        data-content="${escapeHtml(msg.content || '')}">回复</button>`
    : '';
  const toolbar = replyBtn ? `<div class="msg-toolbar">${replyBtn}</div>` : '';

  // 个性化 SVG 头像（连续消息时用占位保持对齐）
  const avatarPlaceholder = `<div style="width:36px;height:36px;flex-shrink:0"></div>`;
  const userAvatarHtml = isConsecutive ? avatarPlaceholder : buildAvatarDiv(null, 36, 'msg-avatar', '', 'title="我"');
  const aiAvatarHtml = isConsecutive ? avatarPlaceholder : buildAvatarDiv(msg.sender_id, 36, 'msg-avatar', 'cursor:pointer',
    `title="${escapeHtml(senderName)}" onclick="openProfileModal('${escapeHtml(msg.sender_id)}')" `);

  // 连续消息时减少顶部间距
  if (isConsecutive) div.classList.add('consecutive');

  if (isUser) {
    div.innerHTML = `
      ${toolbar}
      ${userAvatarHtml}
      <div>
        ${replyBlock}
        <div class="bubble">${htmlContent}</div>
        ${!isConsecutive ? `<div class="msg-meta">${time}</div>` : `<div class="msg-meta msg-meta-hidden">${time}</div>`}
      </div>
    `;
  } else {
    div.innerHTML = `
      ${toolbar}
      ${aiAvatarHtml}
      <div>
        ${!isConsecutive ? `<div class="msg-sender">${escapeHtml(senderName)} · ${escapeHtml(member?.role || '')}</div>` : ''}
        ${replyBlock}
        <div class="bubble">${htmlContent}</div>
        ${!isConsecutive ? `<div class="msg-meta">${time}</div>` : `<div class="msg-meta msg-meta-hidden">${time}</div>`}
      </div>
    `;
  }

  container.appendChild(div);
  if (scroll) scrollToBottom();
}

function renderMarkdown(text) {
  if (typeof marked !== 'undefined') {
    try {
      // marked v1.x: sanitize=true; v4+: 依赖调用方做 DOMPurify（此处用 v1.x 兼容写法）
      return marked.parse(text, { sanitize: true });
    } catch (e) {}
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

  // 提取 @提及的成员 ID
  const mentionUsers = state.currentGroupMembers
    .filter(m => text.includes('@' + m.name))
    .map(m => m.id);

  const replyTo = state.replyTo ? { ...state.replyTo } : null;

  // 立即显示用户消息（本地渲染）
  const userMsg = {
    sender_id: 'user', content: text,
    created_at: new Date().toISOString(),
    reply_to: replyTo,
  };
  renderMessage(userMsg);
  clearReply();

  try {
    const res = await fetch(`${API}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        group_id: state.currentGroupId,
        message: text,
        member_id: state.selectedResponder || null,
        mention_users: mentionUsers.length > 0 ? mentionUsers : undefined,
        reply_to: replyTo || undefined,
      }),
    });
    const data = await res.json();

    if (data.mode === 'task') {
      // 任务模式：AI 消息通过 SSE 实时到达，不手动渲染
      updateTaskIndicator(true);
      state.activeTaskIds.add(data.task_id);
      showTypingFor('Leader');
    } else if (data.mode === 'streaming') {
      // 流式模式（Team2 工具成员）：显示内嵌终端等待 SSE 推送
      state.activeTaskIds.add(data.task_id);
      state.inlineTerminalStepId = data.step_id;
      showInlineTerminal();
      showTypingFor('');
    } else if (data.responses) {
      // 普通模式：直接渲染
      for (const r of data.responses) {
        renderMessage({
          sender_id: r.member_id,
          content: r.content,
          created_at: new Date().toISOString(),
        });
      }
    }
  } catch (e) {
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
  const dropdown = document.getElementById('mention-dropdown');
  const dropdownVisible = !dropdown.classList.contains('hidden');

  if (dropdownVisible) {
    const items = dropdown.querySelectorAll('.mention-item');
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      state.mentionIndex = Math.min(state.mentionIndex + 1, items.length - 1);
      items.forEach((el, i) => el.classList.toggle('active', i === state.mentionIndex));
      return;
    }
    if (e.key === 'ArrowUp') {
      e.preventDefault();
      state.mentionIndex = Math.max(state.mentionIndex - 1, 0);
      items.forEach((el, i) => el.classList.toggle('active', i === state.mentionIndex));
      return;
    }
    if (e.key === 'Enter') {
      e.preventDefault();
      const activeItem = items[state.mentionIndex];
      if (activeItem) selectMentionById(activeItem.dataset.memberId);
      return;
    }
    if (e.key === 'Escape') {
      hideMentionDropdown();
      return;
    }
  }

  if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) {
    e.preventDefault();
    sendMessage();
    return;
  }

  // 监听 @ 触发下拉（在 keyup 里更准确，但这里用 input 事件）
}

document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('msg-input');
  if (input) {
    input.addEventListener('input', () => {
      const val = input.value;
      const atPos = val.lastIndexOf('@');
      if (atPos !== -1) {
        const keyword = val.slice(atPos + 1);
        // 关键词不含空格才触发
        if (!keyword.includes(' ') && state.currentGroupMembers.length > 0) {
          showMentionDropdown(keyword);
          return;
        }
      }
      hideMentionDropdown();
    });
  }

  // 回复按钮事件委托（避免内联字符串拼接 XSS）
  const messagesEl = document.getElementById('messages');
  if (messagesEl) {
    messagesEl.addEventListener('mousedown', e => {
      const btn = e.target.closest('.reply-btn');
      if (!btn) return;
      startReply(btn.dataset.msgId, btn.dataset.sender, btn.dataset.content);
    });
  }
});

// ── 任务看板 ──────────────────────────────────────────────────────
async function loadTaskBoard() {
  try {
    const tasks = await fetch(`${API}/api/tasks`).then(r => r.json());
    state.tasks = tasks;
    renderTaskList(tasks);
    updateTaskBadgeCount(tasks);
  } catch (e) {
    console.error('加载任务失败', e);
  }
}

function updateTaskBadgeCount(tasks) {
  const running = tasks.filter(t => t.status === 'running' || t.status === 'planning').length;
  const badge = document.getElementById('task-running-badge');
  if (running > 0) {
    badge.textContent = running;
    badge.classList.remove('hidden');
  } else {
    badge.classList.add('hidden');
  }
}

function filterTasks(status, btn) {
  state.taskFilter = status;
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  renderTaskList(state.tasks);
}

function renderTaskList(tasks) {
  const list = document.getElementById('task-list');
  const filtered = state.taskFilter === 'all'
    ? tasks
    : tasks.filter(t => t.status === state.taskFilter);

  if (filtered.length === 0) {
    list.innerHTML = '<div class="task-list-empty">暂无任务</div>';
    return;
  }

  list.innerHTML = filtered.map(task => {
    const pct = task.step_counts.total > 0
      ? Math.round((task.step_counts.completed / task.step_counts.total) * 100)
      : (task.status === 'completed' ? 100 : 0);
    const statusIcon = { pending: '⏳', planning: '🤔', running: '⚡', completed: '✅', failed: '❌' }[task.status] || '❓';
    const isActive = state.currentTaskId === task.id;
    return `
      <div class="task-card ${task.status} ${isActive ? 'active' : ''}"
           onclick="openTaskDetail('${task.id}')">
        <div class="task-card-header">
          <span class="task-status-icon">${statusIcon}</span>
          <span class="task-title-text">${escapeHtml(task.title)}</span>
        </div>
        <div class="task-card-meta">
          <span class="task-leader" style="color:${task.leader_color}">
            ${task.leader_name}
          </span>
          <span class="task-group-name">${escapeHtml(task.group_name)}</span>
          <span class="task-time">${formatTime(task.created_at)}</span>
        </div>
        ${task.step_counts.total > 0 ? `
        <div class="task-progress">
          <div class="progress-bar">
            <div class="progress-fill ${task.status}" style="width:${pct}%"></div>
          </div>
          <span class="progress-text">${task.step_counts.completed}/${task.step_counts.total} 步骤</span>
        </div>` : ''}
      </div>
    `;
  }).join('');
}

async function openTaskDetail(taskId) {
  state.currentTaskId = taskId;
  // 高亮选中
  document.querySelectorAll('.task-card').forEach(el => el.classList.remove('active'));
  document.querySelector(`.task-card[onclick="openTaskDetail('${taskId}')"]`)?.classList.add('active');
  await loadTaskDetail(taskId);
}

async function loadTaskDetail(taskId) {
  try {
    const task = await fetch(`${API}/api/tasks/${taskId}`).then(r => r.json());
    renderTaskDetail(task);
  } catch (e) {
    console.error('加载任务详情失败', e);
  }
}

function renderTaskDetail(task) {
  const empty = document.getElementById('task-detail-empty');
  const content = document.getElementById('task-detail-content');
  empty.classList.add('hidden');
  content.classList.remove('hidden');

  const statusLabel = { pending: '待开始', planning: '规划中', running: '执行中', completed: '已完成', failed: '失败' }[task.status] || task.status;
  const statusClass = task.status;

  content.innerHTML = `
    <div class="task-detail-header">
      <div class="task-detail-title">${escapeHtml(task.title)}</div>
      <div class="task-detail-meta">
        <span class="task-status-badge ${statusClass}">${statusLabel}</span>
        <span>负责人：${escapeHtml(task.leader_name)}</span>
        <span>创建：${formatTime(task.created_at)}</span>
        ${task.completed_at ? `<span>完成：${formatTime(task.completed_at)}</span>` : ''}
      </div>
      <div class="task-detail-desc">${escapeHtml(task.description)}</div>
    </div>
    <div class="task-steps-title">执行步骤</div>
    <div class="task-steps-tree">
      ${task.steps && task.steps.length > 0
        ? renderStepTree(task.steps)
        : '<div style="color:#999;padding:16px;text-align:center">暂无步骤</div>'}
    </div>
  `;
}

function renderStepTree(steps, indent = 0) {
  return steps.map(s => {
    const statusIcon = { pending: '⏳', running: '⚡', completed: '✅', failed: '❌', skipped: '⏭️' }[s.status] || '❓';
    const isSelected = state.terminalStepId === s.id;
    const memberName = escapeHtml(s.assigned_to_name);
    return `
      <div class="step-row depth-${Math.min(indent, 3)} clickable ${isSelected ? 'selected' : ''}"
           data-step-id="${s.id}"
           onclick="openTerminalForStep('${s.id}', '${memberName}')">
        <div class="step-header">
          <span class="step-status-icon ${s.status}">${statusIcon}</span>
          ${buildAvatarDiv(getMemberByName(s.assigned_to_name)?.id || null, 24, 'step-avatar', '', '')}
          <div class="step-info">
            <span class="step-title-text">${escapeHtml(s.title)}</span>
            <span class="step-assignee">${memberName}</span>
          </div>
          ${s.started_at ? `<span class="step-time">${formatTime(s.started_at)}</span>` : ''}
        </div>
        ${s.children && s.children.length > 0
          ? `<div class="step-children">${renderStepTree(s.children, indent + 1)}</div>`
          : ''}
      </div>
    `;
  }).join('');
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
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
      ${buildAvatarDiv(m.id, 36, 'info-member-avatar', '', '')}
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
  const p = MEMBER_PROFILE[memberId] || {};
  const mbtiColor = MBTI_COLOR[p.mbti] || '#718096';

  document.getElementById('profile-name').textContent = m.name;
  document.getElementById('profile-body').innerHTML = `
    <div class="profile-hero">
      ${buildAvatarDiv(m.id, 72, 'profile-avatar-lg', '', '')}
      <div class="profile-hero-info">
        <div class="profile-name-row">
          ${escapeHtml(m.name)}
          ${m.is_leader ? '<span class="leader-badge">Leader</span>' : ''}
          ${p.mbti ? `<span class="mbti-badge" style="background:${mbtiColor}15;color:${mbtiColor};border-color:${mbtiColor}30">${p.mbti}</span>` : ''}
        </div>
        <div class="profile-role">${escapeHtml(m.role)}</div>
        <div class="profile-team">${escapeHtml(m.team_name)}</div>
        ${p.mbtiName ? `<div class="profile-mbti-name" style="color:${mbtiColor}">「${p.mbtiName}」</div>` : ''}
      </div>
    </div>

    ${p.drive ? `
    <div class="profile-section">
      <div class="profile-section-label">核心驱动</div>
      <div class="profile-drive">${escapeHtml(p.drive)}</div>
    </div>` : ''}

    ${p.traits ? `
    <div class="profile-section">
      <div class="profile-section-label">性格特质</div>
      <ul class="profile-traits">
        ${p.traits.map(t => `<li>${escapeHtml(t)}</li>`).join('')}
        ${p.weakness ? `<li class="trait-weakness">⚠️ ${escapeHtml(p.weakness)}</li>` : ''}
      </ul>
    </div>` : ''}

    ${p.style ? `
    <div class="profile-section">
      <div class="profile-section-label">沟通风格</div>
      <div class="profile-style-text">${escapeHtml(p.style)}</div>
      ${p.quote ? `<div class="profile-quote">"${escapeHtml(p.quote)}"</div>` : ''}
    </div>` : ''}

    ${p.skills ? `
    <div class="profile-section">
      <div class="profile-section-label">技能标签</div>
      <div class="profile-skills">
        ${p.skills.map(s => `<span class="skill-tag">${escapeHtml(s)}</span>`).join('')}
      </div>
    </div>` : ''}

    <div class="profile-actions">
      <button class="btn-dm" onclick="openDM('${escapeHtml(m.id)}'); closeProfileModal()">发消息</button>
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
  switchView('chat');
}

// ── 新建群聊 Modal ────────────────────────────────────────────────
function openNewGroupModal() {
  document.getElementById('new-group-name').value = '';
  const container = document.getElementById('member-checkboxes');
  container.innerHTML = '';
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
        ${buildAvatarDiv(m.id, 28, 'member-checkbox-avatar', '', '')}
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
    { id: 1, icon: '🎯', name: '团队一·产品研发团队',
      desc: '发现市场痛点 → 验证真实需求 → 评估增长潜力 → 产出完善产品设计' },
    { id: 2, icon: '⚙️', name: '团队二·技术研发团队',
      desc: '技术可行性评估 → 制定技术方案 → 执行研发 → 产品上线' },
    { id: 3, icon: '📣', name: '团队三·推广营销团队',
      desc: '多渠道推广 → 用户获取 → 直播变现 → 实现真实收益' },
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
              ${buildAvatarDiv(m.id, 48, 'org-member-avatar-lg', '', '')}
              <div class="org-member-name">${m.name} ${m.is_leader ? '<span class="leader-badge">Leader</span>' : ''}</div>
              <div class="org-member-role">${m.role}</div>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  }).join('');
}

// ── P0 新增：@提及 ────────────────────────────────────────────────
function showMentionDropdown(keyword) {
  const dropdown = document.getElementById('mention-dropdown');
  const members = state.currentGroupMembers.filter(m =>
    m.name.includes(keyword) || m.role.includes(keyword)
  );
  if (members.length === 0) { hideMentionDropdown(); return; }

  state.mentionSearch = keyword;
  state.mentionIndex = 0;
  dropdown.innerHTML = members.map((m, i) => `
    <div class="mention-item ${i === 0 ? 'active' : ''}" data-member-id="${escapeHtml(m.id)}"
      onmousedown="selectMentionById('${escapeHtml(m.id)}')">
      ${buildAvatarDiv(m.id, 32, 'mention-avatar', '', '')}
      <div>
        <div style="font-size:13px;font-weight:500">${escapeHtml(m.name)}</div>
        <div style="font-size:11px;color:#999">${escapeHtml(m.role)}</div>
      </div>
    </div>
  `).join('');

  // 定位到输入框上方（fixed 定位，先显示再算高度）
  dropdown.classList.remove('hidden');
  const input = document.getElementById('msg-input');
  const rect = input.getBoundingClientRect();
  const dropH = dropdown.offsetHeight;
  dropdown.style.top = (rect.top - dropH - 6) + 'px';
  dropdown.style.left = rect.left + 'px';
  dropdown.style.width = rect.width + 'px';
}

function hideMentionDropdown() {
  document.getElementById('mention-dropdown').classList.add('hidden');
  state.mentionSearch = '';
  state.mentionIndex = 0;
}

function selectMentionById(memberId) {
  const member = getMember(memberId);
  if (member) selectMention(member);
}

function selectMention(member) {
  const input = document.getElementById('msg-input');
  const val = input.value;
  const atPos = val.lastIndexOf('@');
  if (atPos === -1) { hideMentionDropdown(); return; }
  input.value = val.slice(0, atPos) + '@' + member.name + ' ';
  hideMentionDropdown();
  input.focus();
}

// ── P0 新增：消息引用 ─────────────────────────────────────────────
function startReply(msgId, senderName, content) {
  state.replyTo = { id: msgId, sender: senderName, content };
  const preview = document.getElementById('reply-preview');
  document.getElementById('reply-preview-text').textContent =
    `回复 ${senderName}：${content.slice(0, 40)}${content.length > 40 ? '...' : ''}`;
  preview.classList.remove('hidden');
  document.getElementById('msg-input').focus();
}

function clearReply() {
  state.replyTo = null;
  document.getElementById('reply-preview').classList.add('hidden');
}

function renderReplyQuote(replyTo) {
  if (!replyTo) return '';
  return `<div class="reply-quote" onclick="scrollToMsg(${replyTo.id})">
    <span style="font-weight:500;color:#666">${escapeHtml(replyTo.sender)}</span>：${escapeHtml(replyTo.content.slice(0, 60))}${replyTo.content.length > 60 ? '...' : ''}
  </div>`;
}

function scrollToMsg(msgId) {
  const el = document.querySelector(`[data-msg-id="${msgId}"]`);
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

// ── 启动 ──────────────────────────────────────────────────────────
init();
