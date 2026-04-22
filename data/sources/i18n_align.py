"""
i18n_align.py
Multilingual alignment scoring for wikidata_ingest.py.
Sourced from MULTILINGUAL-TERMS.md - DO NOT duplicate; update that file and regenerate.

Usage:
    from i18n_align import alignment_score_multilingual
    score = alignment_score_multilingual(name, description)
"""

import unicodedata

def _norm(s):
    """NFC normalize + lowercase."""
    return unicodedata.normalize('NFC', (s or '')).lower()


# ── STRONG positive terms (+3 each) ───────────────────────────────────────────
# Worker cooperatives, mutual aid, commons, solidarity economy
STRONG_POS = [
    # English
    'cooperative', 'co-op', 'mutual aid', 'indigenous', 'agroecol', 'solidarity',
    'restorative', 'credit union', 'land trust', 'commons', 'open source',
    'fair trade', 'degrowth', 'commoning', 'platform co-op',
    # Spanish
    'cooperativa', 'economía solidaria', 'economia solidaria', 'ayuda mutua',
    'soberanía alimentaria', 'semillas criollas', 'ejido', 'bienes comunales',
    'presupuesto participativo',
    # Portuguese
    'economia solidária', 'economia solidaria', 'ajuda mútua', 'quilombo',
    'sementes crioulas', 'orçamento participativo',
    # French
    'coopérative', 'cooperatif', 'économie solidaire', 'entraide',
    'biens communs', 'budget participatif',
    'société coopérative', 'scop', 'scic',
    # Italian
    'cooperativa di lavoro', 'usi civici', 'beni comuni', 'mutuo soccorso',
    'economia solidale', 'bilancio partecipativo',
    # German
    'genossenschaft', 'solidarische ökonomie', 'allmende', 'gemeingut',
    'bürgerhaushalt',
    # Dutch
    'coöperatie', 'coöperatieve',
    # Russian
    'кооператив', 'артель', 'взаимопомощь',
    # Polish
    'spółdzielnia',
    # Mandarin (unicode)
    '合作社', '互助', '公地', '集体土地', '参与式预算',
    # Japanese
    '協同組合', '入会地', '互助',
    # Korean
    '협동조합', '상호부조',
    # Indonesian/Malay
    'koperasi', 'gotong royong', 'gotong-royong', 'tanah ulayat',
    # Vietnamese
    'hợp tác xã',
    # Thai
    'สหกรณ์',
    # Hindi
    'सहकारी समिति', 'परस्पर सहायता',
    # Arabic
    'تعاونية', 'تعاونيات', 'وقف', 'تكافل', 'حمى',
    # Turkish
    'kooperatif', 'dayanışma', 'imece',
    # Swahili
    'ushirika', 'harambee',
    # Yoruba
    'egbe ajose',
    # Igbo
    'otu nkwado',
    # Amharic
    'የህብረት ስራ',
    # Quechua/Aymara
    'ayni', 'minka', 'minga', 'ayllu', 'tequio',
    # Maori
    'whenua',
]

# ── MODERATE positive terms (+1 each) ─────────────────────────────────────────
MODERATE_POS = [
    # English
    'community', 'environmental', 'health', 'education', 'housing', 'food',
    'energy', 'justice', 'rights', 'civil society', 'advocacy', 'humanitarian',
    'development', 'ngo', 'nonprofit', 'charity', 'amnesty', 'transparency',
    'accountability', 'democracy', 'human rights', 'social', 'international',
    'foundation', 'association', 'network', 'alliance', 'federation', 'welfare',
    'relief', 'aid', 'sustainable', 'ecology', 'biodiversity', 'climate',
    'peace', 'conflict', 'refugee', 'migration', 'disability', 'women', 'youth',
    'children', 'workers', 'labor', 'labour', 'union', 'civic', 'participat',
    # Spanish
    'comunidad', 'salud comunitaria', 'derechos', 'medio ambiente', 'vivienda',
    'justicia', 'democracia', 'mujeres', 'juventud', 'trabajadores',
    'sociedad civil', 'fundación', 'asociación', 'sindicato',
    # Portuguese
    'comunidade', 'direitos', 'meio ambiente', 'saúde comunitária', 'habitação',
    'mulheres', 'trabalhadores', 'sindicato', 'fundação', 'associação',
    # French
    'communauté', 'droits', 'santé communautaire', 'logement', 'femmes',
    'travailleurs', 'syndicat', 'fondation', 'association', 'démocratie',
    'société civile',
    # German
    'gemeinschaft', 'gesundheit', 'wohnen', 'frauen', 'arbeit', 'gewerkschaft',
    'stiftung', 'verein', 'bürgerrecht',
    # Dutch
    'gemeenschap', 'gezondheid', 'vakbond', 'stichting', 'vereniging',
    # Italian
    'comunità', 'salute', 'abitazione', 'donne', 'lavoratori', 'sindacato',
    'fondazione', 'associazione',
    # Russian
    'сообщество', 'здравоохранение', 'права', 'женщины', 'профсоюз',
    # Arabic
    'مجتمع', 'صحة', 'حقوق', 'نساء', 'عمال', 'نقابة', 'مؤسسة',
    'منظمة غير حكومية', 'المجتمع المدني',
    # Swahili
    'jamii', 'afya', 'haki', 'wanawake', 'wafanyakazi', 'shirika',
    # Hindi
    'समुदाय', 'स्वास्थ्य', 'अधिकार', 'महिला', 'मजदूर',
    # Indonesian
    'masyarakat', 'kesehatan', 'hak', 'perempuan', 'buruh', 'yayasan',
    'organisasi',
    # Vietnamese
    'cộng đồng', 'sức khỏe', 'quyền', 'phụ nữ', 'công đoàn',
    # Thai
    'ชุมชน', 'สุขภาพ', 'สิทธิ', 'สตรี', 'แรงงาน',
    # Turkish
    'topluluk', 'sağlık', 'haklar', 'kadın', 'işçi', 'sendika', 'vakıf', 'dernek',
    # Japanese
    '地域', '健康', '権利', '女性', '労働', '組合', '財団', '協会',
    # Korean
    '공동체', '건강', '권리', '여성', '노동', '노조', '재단', '협회',
    # Amharic
    'ማህበረሰብ', 'ጤና', 'መብቶች',
    # Yoruba
    'agbegbe', 'ilera', 'eto',
]

# ── NEGATIVE terms (-3 each) ───────────────────────────────────────────────────
NEGATIVE = [
    'church', 'parish', 'fraternal', 'golf', 'country club', 'hoa', 'booster',
    'cemetery', 'political party', 'military', 'armed forces', 'beauty pageant',
    'casino', 'lottery',
]


def alignment_score_multilingual(name, desc=''):
    """
    Score alignment using multilingual keyword list.
    Returns int clamped to [-5, 5].
    For thin countries (caller sets min_score=0), any non-negative score passes.
    """
    t = _norm(name) + ' ' + _norm(desc)
    s = (
        sum(3 for k in STRONG_POS  if k in t)
      + sum(1 for k in MODERATE_POS if k in t)
      - sum(3 for k in NEGATIVE    if k in t)
    )
    return max(-5, min(10, s))  # allow higher ceiling for multilingual matches
