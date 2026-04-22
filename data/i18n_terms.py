# -*- coding: utf-8 -*-
"""
i18n_terms.py - Multilingual term bank for the Commonweave pipeline.

Source of truth: commonweave/MULTILINGUAL-TERMS.md (2026-04-17)
Purpose: Supply STRONG_POS_MULTI (scoring), SEARCH_TEMPLATES (researcher bots),
         COUNTRY_LANGUAGES (country -> language list), and build_local_queries().

All terms are lowercase where possible. Native script forms are preserved as-is.
Transliterations are included alongside native script forms where the source
document provides them.

ISO 639-1 codes used throughout. Exceptions:
  'nah' - Nahuatl (no ISO 639-1; uses ISO 639-2/3 code)
  'nah' is used consistently here rather than inventing a 2-letter code.
"""

# ---------------------------------------------------------------------------
# 1. CONCEPT_TERMS
# Organized by concept, then by ISO language code.
# Each concept maps language -> list of terms.
# ---------------------------------------------------------------------------

CONCEPT_TERMS = {

    # -----------------------------------------------------------------------
    # Concept 1: Worker / Producer Cooperatives
    # Commonweave principles: Common Ownership, Voluntary Contribution,
    # Democratic Sovereignty
    # -----------------------------------------------------------------------
    'worker_cooperative': {
        'en': [
            'cooperative', 'co-op', 'coop', 'worker-owned', 'employee-owned',
            'worker cooperative', 'worker co-op', 'producer cooperative',
        ],
        'es': [
            'cooperativa', 'sociedad cooperativa', 'cooperativa de trabajo',
            'cooperativa obrera', 'cooperativa de trabajo asociado',
            'cooperativa de produccion',
        ],
        'pt': [
            'cooperativa', 'cooperativa de trabalho', 'cooperativa popular',
            'cooperativa de producao',
        ],
        'fr': [
            'coopérative', 'société coopérative', 'scop',
            'société coopérative et participative', 'scic',
            'coopérative ouvrière',
        ],
        'it': [
            'cooperativa', 'cooperativa di lavoro', 'società cooperativa',
            'cooperativa di produzione',
        ],
        'de': [
            'genossenschaft', 'eg', 'eingetragene genossenschaft',
            'produktivgenossenschaft', 'arbeitergenossenschaft',
        ],
        'nl': [
            'coöperatie', 'coöperatieve vereniging', 'arbeidscoöperatie',
        ],
        'ru': [
            # Native script + transliteration
            'кооператив', 'kooperativ',
            'артель', 'artel',
            'производственный кооператив',
        ],
        'pl': [
            'spółdzielnia', 'spółdzielnia pracy',
        ],
        'zh': [
            # Native script + pinyin romanization
            '合作社', 'hézuòshè',
            '生产合作社', 'shēngchǎn hézuòshè',
            '工人合作社',
        ],
        'ja': [
            # Native script + romaji
            '協同組合', 'kyōdō kumiai',
            '労働者協同組合', 'rōdōsha kyōdō kumiai',
        ],
        'ko': [
            # Native script + romanization
            '협동조합', 'hyeopdong johab',
            '노동자협동조합',
        ],
        'id': [
            'koperasi', 'koperasi pekerja', 'koperasi produsen',
        ],
        'ms': [
            'koperasi', 'koperasi pekerja',
        ],
        'tl': [
            'kooperatiba', 'kooperatibang manggagawa',
        ],
        'vi': [
            'hợp tác xã', 'hợp tác xã lao động',
        ],
        'th': [
            # Native script + romanization
            'สหกรณ์', 'sahakon',
            'สหกรณ์การผลิต',
        ],
        'hi': [
            # Devanagari + romanization
            'सहकारी समिति', 'sahkari samiti',
            'श्रमिक सहकारी',
        ],
        'bn': [
            # Bengali script + romanization
            'সমবায় সমিতি', 'samabay samiti',
        ],
        'ur': [
            # Urdu script + romanization
            'کوآپریٹو',
            'تعاونی سوسائٹی', 'taawuni society',
        ],
        'tr': [
            'kooperatif', 'işçi kooperatifi', 'üretim kooperatifi',
        ],
        'ar': [
            # Arabic script + transliterations
            'تعاونية', "ta'awuniya",
            'شركة تعاونية', "sharika ta'awuniya", "sharikat ta'awuniya",
            'جمعية تعاونية',
        ],
        'fa': [
            # Persian script + transliteration
            'تعاونی', "ta'avoni",
            'شرکت تعاونی کارگری',
        ],
        'sw': [
            'ushirika', 'chama cha ushirika',
        ],
        'ha': [
            # Hausa (Northern Nigeria, Niger)
            'kungiya ta hada-hadar tattalin arziki', 'kungiyar manoma',
        ],
        'yo': [
            # Yoruba (Southwestern Nigeria)
            'egbe ajose', 'egbe agbe',
        ],
        'ig': [
            # Igbo (Southeastern Nigeria)
            'otu nkwado', 'otu oru',
        ],
        'am': [
            # Amharic script + romanization
            'የህብረት ስራ ማህበር', 'yehbret sera mahber',
        ],
        'zu': [
            # Zulu
            'inhlangano yokusebenzelana', 'i-cooperative',
        ],
        'xh': [
            # Xhosa
            'umbutho wokusebenzisana',
        ],
        'he': [
            # Hebrew script + romanization
            'קואופרטיב', "ko'operativ",
            'קיבוץ', 'kibbutz',
            'מושב שיתופי', 'moshav shitufi',
        ],
    },

    # -----------------------------------------------------------------------
    # Concept 2: Mutual Aid / Solidarity Economy
    # Commonweave principles: Universal Sufficiency, Voluntary Contribution
    # -----------------------------------------------------------------------
    'mutual_aid': {
        'en': [
            'mutual aid', 'solidarity economy', 'commons',
            'rotating savings', 'self-help group',
        ],
        'es': [
            'ayuda mutua', 'economía solidaria', 'economía social',
        ],
        'pt': [
            'ajuda mútua', 'economia solidária', 'economia popular',
        ],
        'fr': [
            'entraide', 'économie solidaire', 'économie sociale et solidaire',
            'ess',
        ],
        'it': [
            'mutuo soccorso', 'società di mutuo soccorso', 'sms',
            'economia solidale',
        ],
        'de': [
            'solidarische ökonomie', 'genossenschaftsbewegung',
        ],
        'ru': [
            'взаимопомощь', 'vzaimopomoshch',
            'общество взаимопомощи',
        ],
        'zh': [
            '互助', 'hùzhù',
            '团结经济', 'tuánjié jīngjì',
        ],
        'ja': [
            '互助', 'gojo',
            '連帯経済', 'rentai keizai',
        ],
        'ko': [
            '상호부조', 'sanghobujo',
            '연대경제', 'yeondae gyeongje',
        ],
        'id': [
            'gotong royong', 'tolong menolong', 'koperasi solidaritas',
        ],
        'ms': [
            'gotong-royong', 'bantu-membantu',
        ],
        'tl': [
            'bayanihan', 'damayan',
        ],
        'vi': [
            'tương trợ', 'giúp đỡ lẫn nhau',
        ],
        'th': [
            'ช่วยเหลือเกื้อกูล', 'chuai lueu',
            'น้ำใจ', 'nam jai',
        ],
        'hi': [
            'परस्पर सहायता', 'paraspar sahayata',
            'स्वयं सहायता समूह', 'shg',
        ],
        'bn': [
            'স্বনির্ভর গোষ্ঠী', 'swanirbhar goshthi',
        ],
        'ur': [
            'باہمی امداد', 'bahami imdad',
        ],
        'tr': [
            'dayanışma', 'imece',
        ],
        'ar': [
            # Waqf = charitable endowment (Islamic commons tradition)
            'waqf',
            'تكافل', 'takaful',
            'تعاون', "ta'awun",
        ],
        'sw': [
            'msaada wa pande zote', 'harambee',
        ],
        'ha': [
            # Gayya = communal labor tradition (Hausa)
            'gayya',
        ],
        'yo': [
            # Owe = reciprocal labor, esusu = rotating savings
            'owe', 'esusu',
        ],
        'ig': [
            # Isusu = rotating savings (Igbo)
            'isusu', 'igba boyi',
        ],
        'am': [
            # Idir = burial society, equb = rotating savings (Ethiopian)
            'ድር', 'idir',
            'equb',
        ],
        'zu': [
            # Ilima = collective labor, stokvel = rotating savings
            'ilima', 'stokvel',
        ],
        'xh': [
            'ilima', 'umgalelo',
        ],
        'qu': [
            # Quechua (Andes: Peru, Bolivia, Ecuador)
            'ayni', 'minga', 'minka',
        ],
        'ay': [
            # Aymara
            "ayni", "mink'a",
        ],
        'nah': [
            # Nahuatl (Mexico) - tequio = collective community labor
            'tequio',
        ],
    },

    # -----------------------------------------------------------------------
    # Concept 3: Commons, Common Lands, Shared Resources
    # Commonweave principles: Common Ownership of the Commons,
    # Ecological Equilibrium
    # -----------------------------------------------------------------------
    'commons': {
        'en': [
            'commons', 'community land trust', 'common land', 'commoning',
            'land commons',
        ],
        'es': [
            # Ejido = post-revolution land commons (Mexico)
            'ejido', 'comunidad agraria', 'bienes comunales',
            'tierras comunales',
        ],
        'pt': [
            # Quilombo = Afro-Brazilian maroon communities
            'quilombo', 'baldios', 'terras de uso comum', 'fundo de pasto',
        ],
        'fr': [
            'biens communaux', 'terres communales', 'commun', 'communs',
        ],
        'it': [
            # Usi civici = medieval common-land tradition
            'usi civici', 'beni comuni', 'proprietà collettiva',
        ],
        'de': [
            # Allmende = historical German commons
            'allmende', 'gemeingut', 'gemeinschaftsgut',
        ],
        'ru': [
            # Obshchina = pre-Soviet peasant commune
            'община', 'obshchina',
            'общинное землевладение',
        ],
        'zh': [
            '公地', 'gōngdì',
            '集体土地', 'jítǐ tǔdì',
        ],
        'ja': [
            # Iriai-chi = traditional village commons
            '入会地', 'iriai-chi',
            'コモンズ', 'komonzu',
        ],
        'ko': [
            '공유지', 'gongyuji',
            '마을공동체', 'maeul gongdongche',
        ],
        'id': [
            # Tanah ulayat = customary land
            'tanah ulayat', 'tanah adat',
        ],
        'th': [
            'ที่ดินสาธารณะ', 'tidin satharana',
            # Pa chumchon = community forest
            'ป่าชุมชน', 'pa chumchon',
        ],
        'vi': [
            'đất công', 'rừng cộng đồng',
        ],
        'hi': [
            # Gochar = village grazing commons
            'साझा भूमि', 'sajha bhoomi',
            'गोचर', 'gochar',
        ],
        'ar': [
            # Hima = pre-Islamic/Islamic pastoral commons
            'hima',
            "musha'a",
        ],
        'tr': [
            'mera', 'orman köyleri',
        ],
        'sw': [
            'ardhi ya kijiji', 'ardhi ya jamii',
        ],
        'zu': [
            'umhlaba wesizwe', 'indlu yesizwe',
        ],
        'qu': [
            # Ayllu = Andean kinship-land unit
            'ayllu',
        ],
        'mi': [
            # Maori ancestral and tribal land
            'whenua', 'iwi',
        ],
        'iu': [
            # Inuktitut - nunavut = "our land"
            'nunavut',
        ],
    },

    # -----------------------------------------------------------------------
    # Concept 4: Agroecology, Food Sovereignty, Seed Commons
    # Commonweave principles: Ecological Equilibrium, Universal Sufficiency
    # -----------------------------------------------------------------------
    'agroecology': {
        'en': [
            'agroecology', 'food sovereignty', 'seed library',
            'regenerative agriculture', 'seed commons', 'permaculture',
        ],
        'es': [
            # Via Campesina origin
            'agroecología', 'soberanía alimentaria',
            'semillas criollas', 'semillas nativas',
            'agricultura regenerativa',
        ],
        'pt': [
            'agroecologia', 'soberania alimentar', 'sementes crioulas',
        ],
        'fr': [
            'agroécologie', 'souveraineté alimentaire', 'semences paysannes',
        ],
        'it': [
            'agroecologia', 'sovranità alimentare', 'sementi contadine',
        ],
        'de': [
            'agrarökologie', 'ernährungssouveränität', 'bäuerliches saatgut',
        ],
        'hi': [
            'कृषि पारिस्थितिकी', 'खाद्य संप्रभुता',
            'देसी बीज', 'desi beej',
        ],
        'ta': [
            # Tamil
            'உணவு இறையாண்மை',
        ],
        'sw': [
            'kilimo-ikolojia', 'uhuru wa chakula', 'mbegu asilia',
        ],
        'ar': [
            'زراعة بيئية', "zira'a bi'iya",
            'سيادة غذائية', 'siyada ghida\'iya',
        ],
        'th': [
            'เกษตรนิเวศ', 'kaset niwet',
            'อธิปไตยทางอาหาร',
        ],
        'id': [
            'pertanian agroekologi', 'kedaulatan pangan',
        ],
        'ko': [
            '농생태학', 'nongsaengtaehak',
            '식량주권', 'sikryang jugwon',
        ],
        'ja': [
            'アグロエコロジー',
            '食料主権', 'shokuryō shuken',
        ],
    },

    # -----------------------------------------------------------------------
    # Concept 5: Community Health, Care, Healing
    # Commonweave principle: Universal Sufficiency
    # -----------------------------------------------------------------------
    'community_health': {
        'en': [
            'community health', 'free clinic', 'community health worker',
            'primary care cooperative',
        ],
        'es': [
            'salud comunitaria', 'promotor de salud',
            'centro de salud comunitario',
        ],
        'pt': [
            # Brazil's ACS program is a world-scale model
            'saúde comunitária', 'agente comunitário de saúde',
        ],
        'fr': [
            'santé communautaire', 'maison de santé',
        ],
        'ar': [
            'صحة مجتمعية', "sihha mujtama'iya",
        ],
        'sw': [
            'afya ya jamii', 'kituo cha afya',
        ],
        'hi': [
            # ASHA = India's community health worker program
            'सामुदायिक स्वास्थ्य',
            'आशा कार्यकर्ता', 'asha worker',
        ],
    },

    # -----------------------------------------------------------------------
    # Concept 6: Democratic / Participatory Governance
    # Commonweave principles: Democratic Sovereignty, Transparency
    # -----------------------------------------------------------------------
    'participatory_governance': {
        'en': [
            'participatory budgeting', 'citizen assembly', 'commons governance',
            'participatory democracy', 'community council',
        ],
        'es': [
            # Porto Alegre origin
            'presupuesto participativo', 'asamblea ciudadana',
            'consejo comunal', 'democracia participativa',
        ],
        'pt': [
            'orçamento participativo', 'assembleia popular',
        ],
        'fr': [
            'budget participatif', 'assemblée citoyenne',
            'démocratie participative',
        ],
        'it': [
            'bilancio partecipativo', 'assemblea cittadina',
        ],
        'de': [
            'bürgerhaushalt', 'bürgerrat',
        ],
        'zh': [
            '参与式预算', 'cānyù shì yùsuàn',
            '居民议事会',
        ],
        'ja': [
            '市民参加', '参加型予算',
        ],
        'ar': [
            'الموازنة التشاركية', 'mawazana tasharukiya',
        ],
    },

    # -----------------------------------------------------------------------
    # Concept 7: Digital Commons, Platform Cooperativism
    # Commonweave principles: Common Ownership, Democratic Sovereignty,
    # Transparency
    # -----------------------------------------------------------------------
    'digital_commons': {
        'en': [
            'platform cooperative', 'platform co-op', 'open source',
            'digital commons', 'data trust', 'commons-based peer production',
            'open data', 'copyleft',
        ],
        'es': [
            'plataforma cooperativa', 'cooperativa de plataforma',
            'bienes comunes digitales', 'código abierto',
        ],
        'pt': [
            'cooperativa de plataforma', 'bens comuns digitais',
            'código aberto',
        ],
        'fr': [
            'coopérative de plateforme', 'communs numériques',
            'logiciel libre',
        ],
        'it': [
            'cooperativa di piattaforma', 'beni comuni digitali',
        ],
        'de': [
            'plattformgenossenschaft', 'digitale allmende',
        ],
    },
}


# ---------------------------------------------------------------------------
# 2. STRONG_POS_MULTI
# Flat sorted list of alignment terms from the concept bank. Intended for
# WORD-BOUNDARY matching by phase2_filter.score_org, not naive substring.
#
# Quality filter applied here to cut false positives:
#   - Exclude Latin-script terms shorter than 5 chars (too ambiguous:
#     'eg', 'ess', 'sms', 'shg', 'owe', 'iwi', 'iu', 'mera').
#   - Keep all non-Latin-script terms regardless of length (Chinese/Japanese/
#     Korean/Arabic/Amharic/etc. are already unambiguous when matched on
#     whole-character boundaries).
#   - TERMS_MOVED_TO_SEARCH_ONLY is the excluded set, still available for
#     researcher-bot queries where false positives do not compound.
# ---------------------------------------------------------------------------

_MIN_LATIN_LEN = 5


def _is_latin_script(term):
    # A term is Latin-script if every non-space char is in the basic Latin
    # or Latin-1 Supplement or Latin Extended-A block. Anything with CJK,
    # Arabic, Devanagari, Cyrillic, etc. is treated as non-Latin so short
    # native-script terms survive.
    for ch in term:
        if ch.isspace() or not ch.isalpha():
            continue
        cp = ord(ch)
        in_latin = (
            (0x0041 <= cp <= 0x007A) or   # Basic Latin letters
            (0x00C0 <= cp <= 0x024F) or   # Latin-1 + Latin Extended-A/B
            (0x1E00 <= cp <= 0x1EFF)      # Latin Extended Additional
        )
        if not in_latin:
            return False
    return True


def _build_term_sets():
    all_terms = []
    kept = []
    excluded = []
    for concept in CONCEPT_TERMS.values():
        for lang_terms in concept.values():
            for term in lang_terms:
                t = term.lower().strip()
                if not t:
                    continue
                all_terms.append(t)
                # Always keep non-Latin-script native forms, they are unambiguous.
                if not _is_latin_script(t):
                    kept.append(t)
                    continue
                # For Latin-script terms, require a minimum length OR at least
                # one word-char of 5+ chars in a multi-word phrase.
                longest_word = max((len(w) for w in t.split()), default=0)
                if len(t) >= _MIN_LATIN_LEN or longest_word >= _MIN_LATIN_LEN:
                    kept.append(t)
                else:
                    excluded.append(t)
    return sorted(set(kept)), sorted(set(excluded)), sorted(set(all_terms))


STRONG_POS_MULTI, TERMS_MOVED_TO_SEARCH_ONLY, _ALL_CONCEPT_TERMS = _build_term_sets()


# ---------------------------------------------------------------------------
# 3. COUNTRY_LANGUAGES
# Maps ISO 3166-1 alpha-2 country code -> list of ISO 639-1 language codes.
# Primary language listed first. Covers all countries in data/regional/ and
# any country referenced in researcher scripts.
# Note: 'nah' (Nahuatl) uses ISO 639-2 code - no ISO 639-1 equivalent.
# ---------------------------------------------------------------------------

COUNTRY_LANGUAGES = {
    'AE': ['ar'],                          # UAE
    'AF': ['fa', 'ps'],                    # Afghanistan
    'AL': ['sq'],                          # Albania
    'AM': ['hy'],                          # Armenia
    'AO': ['pt'],                          # Angola
    'AR': ['es'],                          # Argentina
    'AT': ['de'],                          # Austria
    'AU': ['en'],                          # Australia
    'AZ': ['az'],                          # Azerbaijan
    'BA': ['bs'],                          # Bosnia and Herzegovina
    'BD': ['bn'],                          # Bangladesh
    'BE': ['nl', 'fr', 'de'],              # Belgium
    'BF': ['fr'],                          # Burkina Faso
    'BG': ['bg'],                          # Bulgaria
    'BH': ['ar'],                          # Bahrain
    'BJ': ['fr'],                          # Benin
    'BN': ['ms'],                          # Brunei
    'BO': ['es', 'qu', 'ay'],              # Bolivia
    'BR': ['pt'],                          # Brazil
    'BW': ['en'],                          # Botswana
    'BY': ['be', 'ru'],                    # Belarus
    'BZ': ['en'],                          # Belize
    'CA': ['en', 'fr'],                    # Canada
    'CD': ['fr', 'sw'],                    # DR Congo
    'CF': ['fr'],                          # Central African Republic
    'CG': ['fr'],                          # Republic of Congo
    'CH': ['de', 'fr', 'it'],              # Switzerland
    'CI': ['fr'],                          # Ivory Coast
    'CL': ['es'],                          # Chile
    'CM': ['fr', 'en'],                    # Cameroon
    'CN': ['zh'],                          # China
    'CO': ['es'],                          # Colombia
    'CR': ['es'],                          # Costa Rica
    'CU': ['es'],                          # Cuba
    'CY': ['el', 'tr'],                    # Cyprus
    'CZ': ['cs'],                          # Czech Republic
    'DE': ['de'],                          # Germany
    'DJ': ['fr', 'ar'],                    # Djibouti
    'DK': ['da'],                          # Denmark
    'DO': ['es'],                          # Dominican Republic
    'DZ': ['ar', 'fr'],                    # Algeria
    'EC': ['es'],                          # Ecuador
    'EE': ['et'],                          # Estonia
    'EG': ['ar'],                          # Egypt
    'ER': ['ti', 'ar'],                    # Eritrea
    'ES': ['es'],                          # Spain
    'ET': ['am'],                          # Ethiopia
    'FI': ['fi'],                          # Finland
    'FJ': ['en'],                          # Fiji
    'FR': ['fr'],                          # France
    'GA': ['fr'],                          # Gabon
    'GB': ['en'],                          # United Kingdom
    'GE': ['ka'],                          # Georgia
    'GH': ['en'],                          # Ghana
    'GM': ['en'],                          # Gambia
    'GN': ['fr'],                          # Guinea
    'GQ': ['es', 'fr'],                    # Equatorial Guinea
    'GR': ['el'],                          # Greece
    'GT': ['es'],                          # Guatemala
    'GW': ['pt'],                          # Guinea-Bissau
    'GY': ['en'],                          # Guyana
    'HN': ['es'],                          # Honduras
    'HR': ['hr'],                          # Croatia
    'HT': ['fr', 'ht'],                    # Haiti
    'HU': ['hu'],                          # Hungary
    'ID': ['id'],                          # Indonesia
    'IE': ['en'],                          # Ireland
    'IN': ['hi', 'bn', 'ta', 'te', 'mr'], # India (top 5 of 22 official)
    'IQ': ['ar'],                          # Iraq
    'IR': ['fa'],                          # Iran
    'IS': ['is'],                          # Iceland
    'IT': ['it'],                          # Italy
    'JM': ['en'],                          # Jamaica
    'JO': ['ar'],                          # Jordan
    'JP': ['ja'],                          # Japan
    'KE': ['sw', 'en'],                    # Kenya
    'KG': ['ky', 'ru'],                    # Kyrgyzstan
    'KH': ['km'],                          # Cambodia
    'KR': ['ko'],                          # South Korea
    'KW': ['ar'],                          # Kuwait
    'KZ': ['kk', 'ru'],                    # Kazakhstan
    'LA': ['lo'],                          # Laos
    'LB': ['ar'],                          # Lebanon
    'LK': ['si', 'ta'],                    # Sri Lanka
    'LR': ['en'],                          # Liberia
    'LS': ['st', 'en'],                    # Lesotho
    'LT': ['lt'],                          # Lithuania
    'LU': ['fr', 'de'],                    # Luxembourg
    'LV': ['lv'],                          # Latvia
    'LY': ['ar'],                          # Libya
    'MA': ['ar', 'fr'],                    # Morocco
    'MD': ['ro', 'ru'],                    # Moldova
    'ME': ['sr'],                          # Montenegro
    'MG': ['mg', 'fr'],                    # Madagascar
    'MK': ['mk'],                          # North Macedonia
    'ML': ['fr'],                          # Mali
    'MM': ['my'],                          # Myanmar
    'MN': ['mn'],                          # Mongolia
    'MT': ['mt', 'en'],                    # Malta
    'MW': ['en'],                          # Malawi
    'MX': ['es', 'nah'],                   # Mexico (Nahuatl for indigenous coverage)
    'MY': ['ms'],                          # Malaysia
    'MZ': ['pt'],                          # Mozambique
    'NA': ['en', 'af'],                    # Namibia
    'NE': ['fr', 'ha'],                    # Niger (Hausa widely spoken)
    'NG': ['en', 'ha', 'yo', 'ig'],        # Nigeria
    'NI': ['es'],                          # Nicaragua
    'NL': ['nl'],                          # Netherlands
    'NO': ['no'],                          # Norway
    'NP': ['ne'],                          # Nepal
    'NZ': ['en', 'mi'],                    # New Zealand
    'OM': ['ar'],                          # Oman
    'PA': ['es'],                          # Panama
    'PE': ['es', 'qu'],                    # Peru
    'PG': ['en'],                          # Papua New Guinea
    'PH': ['tl', 'en'],                    # Philippines
    'PK': ['ur', 'en'],                    # Pakistan
    'PL': ['pl'],                          # Poland
    'PS': ['ar'],                          # Palestine
    'PT': ['pt'],                          # Portugal
    'PY': ['es'],                          # Paraguay
    'QA': ['ar'],                          # Qatar
    'RO': ['ro'],                          # Romania
    'RS': ['sr'],                          # Serbia
    'RU': ['ru'],                          # Russia
    'RW': ['rw', 'fr', 'en'],             # Rwanda
    'SA': ['ar'],                          # Saudi Arabia
    'SD': ['ar'],                          # Sudan
    'SE': ['sv'],                          # Sweden
    'SI': ['sl'],                          # Slovenia
    'SK': ['sk'],                          # Slovakia
    'SL': ['en'],                          # Sierra Leone
    'SN': ['fr'],                          # Senegal
    'SO': ['so', 'ar'],                    # Somalia
    'SR': ['nl'],                          # Suriname
    'SS': ['en', 'ar'],                    # South Sudan
    'SV': ['es'],                          # El Salvador
    'SY': ['ar'],                          # Syria
    'SZ': ['en', 'ss'],                    # Eswatini (Swati)
    'TD': ['fr', 'ar'],                    # Chad
    'TG': ['fr'],                          # Togo
    'TH': ['th'],                          # Thailand
    'TJ': ['tg', 'ru'],                    # Tajikistan
    'TL': ['pt'],                          # Timor-Leste
    'TM': ['tk'],                          # Turkmenistan
    'TN': ['ar', 'fr'],                    # Tunisia
    'TR': ['tr'],                          # Turkey
    'TT': ['en'],                          # Trinidad and Tobago
    'TW': ['zh'],                          # Taiwan
    'TZ': ['sw', 'en'],                    # Tanzania
    'UA': ['uk'],                          # Ukraine
    'UG': ['sw', 'en'],                    # Uganda
    'US': ['en'],                          # United States
    'UY': ['es'],                          # Uruguay
    'UZ': ['uz', 'ru'],                    # Uzbekistan
    'VE': ['es'],                          # Venezuela
    'VN': ['vi'],                          # Vietnam
    'YE': ['ar'],                          # Yemen
    'ZA': ['zu', 'xh', 'af', 'en'],       # South Africa
    'ZM': ['en'],                          # Zambia
    'ZW': ['en'],                          # Zimbabwe
}


# ---------------------------------------------------------------------------
# 4. SEARCH_TEMPLATES
# Search query fragments per language per topic.
# Topics include the 7 CONCEPT_TERMS concepts plus extra research topics
# needed for country researcher bots (renewable energy, indigenous rights,
# education, etc.).
# These are topic fragments - build_local_queries() prepends the country name.
# ---------------------------------------------------------------------------

SEARCH_TEMPLATES = {
    'en': {
        'worker_cooperative': [
            'worker cooperative federation',
            'cooperatives directory worker-owned',
            'employee-owned enterprises',
        ],
        'mutual_aid': [
            'mutual aid network solidarity economy',
            'self-help group rotating savings',
        ],
        'commons': [
            'community land trust commons',
            'common land shared resources organizations',
        ],
        'agroecology': [
            'food sovereignty agroecology organizations',
            'seed library regenerative agriculture',
        ],
        'community_health': [
            'community health organizations free clinic',
            'community health worker primary care',
        ],
        'participatory_governance': [
            'participatory budgeting citizen assembly',
            'democratic governance community participation organizations',
        ],
        'digital_commons': [
            'open source technology civic tech organizations',
            'platform cooperative digital commons',
        ],
        'renewable_energy': [
            'renewable energy community cooperative solar',
            'community energy cooperative wind solar',
        ],
        'indigenous_rights': [
            'indigenous peoples organizations rights',
            'indigenous rights land tenure organizations',
        ],
        'womens_organizations': [
            'women organizations cooperative self-help savings group',
            'women empowerment cooperative association',
        ],
        'restorative_justice': [
            'restorative justice peacebuilding organizations',
            'community justice reconciliation',
        ],
        'nonprofit_directory': [
            'NGO directory civil society organizations',
            'nonprofit registry registered charities database',
        ],
        'education': [
            'education grassroots community school federation',
            'community education cooperative',
        ],
        'environmental_conservation': [
            'environmental conservation ecology organizations',
            'ecology conservation community organizations',
        ],
    },
    'es': {
        'worker_cooperative': [
            'federación de cooperativas directorio',
            'cooperativa de trabajo asociado organizaciones',
            'economía social empresas',
        ],
        'mutual_aid': [
            'economía solidaria ayuda mutua',
            'redes de apoyo mutuo organizaciones',
        ],
        'commons': [
            'bienes comunes tierras comunales',
            'ejido comunidad agraria organizaciones',
        ],
        'agroecology': [
            'agroecología soberanía alimentaria organizaciones',
            'semillas criollas agricultura campesina',
        ],
        'community_health': [
            'salud comunitaria promotores de salud',
            'centro de salud comunitario organizaciones',
        ],
        'participatory_governance': [
            'presupuesto participativo asamblea ciudadana',
            'democracia participativa consejo comunal',
        ],
        'digital_commons': [
            'cooperativa de plataforma bienes comunes digitales',
            'código abierto tecnología cívica',
        ],
        'renewable_energy': [
            'energía renovable cooperativa solar comunitaria',
            'energía solar cooperativa comunidad',
        ],
        'indigenous_rights': [
            'organizaciones pueblos indígenas derechos',
            'derechos territoriales indígenas organizaciones',
        ],
        'womens_organizations': [
            'organizaciones de mujeres cooperativa',
            'empoderamiento femenino asociaciones cooperativas',
        ],
        'restorative_justice': [
            'justicia restaurativa organizaciones paz',
            'reconciliación comunitaria organizaciones',
        ],
        'nonprofit_directory': [
            'directorio ONG sociedad civil organizaciones',
            'registro sin fines de lucro base de datos',
        ],
        'education': [
            'educación comunitaria cooperativa escuela',
            'federación escuelas comunitarias',
        ],
        'environmental_conservation': [
            'conservación ambiental ecología organizaciones',
            'organizaciones ecología comunidad',
        ],
    },
    'pt': {
        'worker_cooperative': [
            'federação de cooperativas diretório',
            'cooperativa de trabalho organizações',
            'economia solidária empresas',
        ],
        'mutual_aid': [
            'economia solidária ajuda mútua',
            'redes de apoio mútuo organizações',
        ],
        'commons': [
            'bens comuns terras de uso comum',
            'quilombo comunidade agrária',
        ],
        'agroecology': [
            'agroecologia soberania alimentar organizações',
            'sementes crioulas agricultura camponesa',
        ],
        'community_health': [
            'saúde comunitária agente comunitário de saúde',
            'centro de saúde comunitário organizações',
        ],
        'participatory_governance': [
            'orçamento participativo assembleia popular',
            'democracia participativa conselho comunitário',
        ],
        'digital_commons': [
            'cooperativa de plataforma bens comuns digitais',
            'código aberto tecnologia cívica',
        ],
        'renewable_energy': [
            'energia renovável cooperativa solar comunitária',
            'cooperativa de energia solar comunidade',
        ],
        'indigenous_rights': [
            'organizações povos indígenas direitos',
            'direitos territoriais indígenas organizações',
        ],
        'womens_organizations': [
            'organizações de mulheres cooperativa',
            'empoderamento feminino associações cooperativas',
        ],
        'restorative_justice': [
            'justiça restaurativa organizações paz',
            'reconciliação comunitária organizações',
        ],
        'nonprofit_directory': [
            'diretório ONG sociedade civil organizações',
            'registro sem fins lucrativos banco de dados',
        ],
        'education': [
            'educação comunitária cooperativa escola',
            'federação escolas comunitárias',
        ],
        'environmental_conservation': [
            'conservação ambiental ecologia organizações',
            'organizações ecologia comunidade',
        ],
    },
    'fr': {
        'worker_cooperative': [
            'fédération de coopératives annuaire',
            'société coopérative et participative scop',
            'économie sociale entreprises',
        ],
        'mutual_aid': [
            'économie solidaire entraide organisations',
            'économie sociale et solidaire ess',
        ],
        'commons': [
            'biens communaux terres communales',
            'communs ressources partagées organisations',
        ],
        'agroecology': [
            'agroécologie souveraineté alimentaire organisations',
            'semences paysannes agriculture biologique',
        ],
        'community_health': [
            'santé communautaire maison de santé',
            'agents de santé communautaire organisations',
        ],
        'participatory_governance': [
            'budget participatif assemblée citoyenne',
            'démocratie participative conseil communal',
        ],
        'digital_commons': [
            'coopérative de plateforme communs numériques',
            'logiciel libre technologie civique',
        ],
        'renewable_energy': [
            'énergie renouvelable coopérative solaire communautaire',
            'coopérative énergie solaire communauté',
        ],
        'indigenous_rights': [
            'organisations peuples autochtones droits',
            'droits fonciers autochtones organisations',
        ],
        'womens_organizations': [
            'organisations de femmes coopérative',
            'autonomisation des femmes associations coopératives',
        ],
        'restorative_justice': [
            'justice restaurative organisations paix',
            'réconciliation communautaire organisations',
        ],
        'nonprofit_directory': [
            'annuaire ONG société civile organisations',
            'registre à but non lucratif base de données',
        ],
        'education': [
            'éducation communautaire coopérative école',
            'fédération écoles communautaires',
        ],
        'environmental_conservation': [
            'conservation environnementale écologie organisations',
            'organisations écologie communauté',
        ],
    },
    'de': {
        'worker_cooperative': [
            'Genossenschaft Verzeichnis Mitarbeiter',
            'eingetragene Genossenschaft eG Organisationen',
        ],
        'mutual_aid': [
            'solidarische Ökonomie gegenseitige Hilfe',
            'Nachbarschaftshilfe Organisationen',
        ],
        'commons': [
            'Allmende Gemeingut Organisationen',
            'Gemeinschaftsgut Boden Organisationen',
        ],
        'agroecology': [
            'Agrarökologie Ernährungssouveränität Organisationen',
            'bäuerliches Saatgut Permakultur',
        ],
        'participatory_governance': [
            'Bürgerhaushalt Bürgerrat Organisationen',
            'partizipative Demokratie Organisationen',
        ],
        'digital_commons': [
            'Plattformgenossenschaft digitale Allmende',
            'Open Source Civic Tech Organisationen',
        ],
    },
    'ar': {
        'worker_cooperative': [
            'تعاونية دليل منظمات',
            'شركة تعاونية منظمات',
        ],
        'mutual_aid': [
            'تكافل اقتصاد تضامني منظمات',
            'وقف مجتمعي منظمات',
        ],
        'commons': [
            'حمى أراضي مشتركة منظمات',
            'أراضي عامة موارد مشتركة',
        ],
        'agroecology': [
            'زراعة بيئية سيادة غذائية منظمات',
            'زراعة مستدامة تقاوي محلية',
        ],
        'community_health': [
            'صحة مجتمعية عيادات مجانية منظمات',
            'عمال صحة مجتمعية',
        ],
        'participatory_governance': [
            'موازنة تشاركية جمعية مواطنين',
            'حوكمة ديمقراطية مجتمعية منظمات',
        ],
        'digital_commons': [
            'مشاع رقمي مفتوح المصدر منظمات',
            'تعاونية منصة رقمية',
        ],
        'nonprofit_directory': [
            'دليل منظمات غير حكومية مجتمع مدني',
            'قاعدة بيانات منظمات خيرية',
        ],
        'womens_organizations': [
            'منظمات نسائية تعاونية',
            'تمكين المرأة جمعيات تعاونية',
        ],
        'renewable_energy': [
            'طاقة متجددة تعاونية شمسية مجتمعية',
            'طاقة شمسية تعاونية',
        ],
        'environmental_conservation': [
            'حفاظ بيئي ايكولوجيا منظمات',
            'منظمات بيئة مجتمع',
        ],
    },
    'sw': {
        'worker_cooperative': [
            'ushirika wa wafanyakazi orodha',
            'chama cha ushirika shirika',
        ],
        'mutual_aid': [
            'harambee msaada wa pande zote',
            'uchumi wa mshikamano mashirika',
        ],
        'commons': [
            'ardhi ya jamii ardhi ya kijiji',
            'ardhi ya msingi mashirika',
        ],
        'agroecology': [
            'kilimo-ikolojia uhuru wa chakula mashirika',
            'mbegu asilia kilimo endelevu',
        ],
        'community_health': [
            'afya ya jamii kituo cha afya',
            'wafanyakazi afya jamii',
        ],
        'nonprofit_directory': [
            'orodha ya mashirika ya kiraia',
            'shirika lisilo la faida database',
        ],
        'womens_organizations': [
            'vikundi vya wanawake ushirika',
            'uwezeshaji wanawake ushirika',
        ],
        'indigenous_rights': [
            'haki za watu wa asili mashirika',
            'ardhi ya watu asili haki',
        ],
        'environmental_conservation': [
            'uhifadhi wa mazingira ikolojia mashirika',
            'mashirika ya mazingira jamii',
        ],
        'renewable_energy': [
            'nishati mbadala ushirika wa nishati ya jua',
            'umeme wa jua ushirika',
        ],
    },
    'ha': {
        # Hausa - Northern Nigeria, Niger
        'worker_cooperative': [
            'kungiya ta hada-hadar tattalin arziki Nigeria',
            'kungiyar manoma hadin gwiwa',
        ],
        'mutual_aid': [
            'gayya taimakon juna Nigeria',
            'hadin gwiwa al\'umma',
        ],
        'commons': [
            'filaye na al\'umma kasa ta jama\'a',
            'gari na hadin gwiwa filaye',
        ],
        'agroecology': [
            'noma na yanayi wadatar abinci Nigeria',
            'tsaba na gida noma na kasa',
        ],
        'community_health': [
            'lafiyar al\'umma asibiti kyauta Nigeria',
            'ma\'aikatan lafiya na al\'umma',
        ],
        'nonprofit_directory': [
            'kungiyar sa kai Nigeria jerin',
            'ƙungiyoyin farar hula Nigeria',
        ],
        'womens_organizations': [
            'kungiyar mata hadin gwiwa Nigeria',
            'karfin gwiwa mata ƙungiya',
        ],
        'indigenous_rights': [
            'hakkokin yan asalin kasa ƙungiya',
            'dan asali kasa hakki Nigeria',
        ],
        'renewable_energy': [
            'kuzarin hasken rana hadin gwiwa Nigeria',
            'makamashin rana ƙungiya',
        ],
        'restorative_justice': [
            'adalci na gyarawa zaman lafiya Nigeria',
            'sasantawa al\'umma',
        ],
        'education': [
            'ilimi al\'umma makaranta Nigeria',
            'ilimin gargajiya ƙungiya',
        ],
        'environmental_conservation': [
            'kare muhalli ikoloji ƙungiya Nigeria',
            'ƙungiyoyin muhalli al\'umma',
        ],
    },
    'yo': {
        # Yoruba - Southwestern Nigeria
        'worker_cooperative': [
            'egbe ajose Nigeria orisirisi',
            'egbe agbe iṣowo',
        ],
        'mutual_aid': [
            'owe esusu egbe Nigeria',
            'ifowosowopo aje Nigeria',
        ],
        'commons': [
            'ile aye ti gbogbo eniyan ni Nigeria',
            'ilẹ ti ilu ni arinrin',
        ],
        'agroecology': [
            'ogbin ajogun ẹtọ si ounje Nigeria',
            'irugbin ile ogbin adayeba',
        ],
        'community_health': [
            'ilera agbegbe ile iwosan ọfẹ Nigeria',
            'oṣiṣẹ ilera agbegbe',
        ],
        'nonprofit_directory': [
            'ẹgbẹ alainèrè Nigeria atokọ',
            'ẹgbẹ awujọ Nigeria',
        ],
        'womens_organizations': [
            'ẹgbẹ awọn obinrin ifowosowopo Nigeria',
            'agbara awọn obinrin ẹgbẹ',
        ],
        'indigenous_rights': [
            'ẹtọ eniyan ibile Nigeria ẹgbẹ',
            'ẹtọ ilẹ awọn eniyan ibile',
        ],
        'renewable_energy': [
            'agbara adayeba ifowosowopo oorun Nigeria',
            'ẹgbẹ agbara oorun',
        ],
        'restorative_justice': [
            'idajọ atunṣe alaafia Nigeria',
            'isọdọtun agbegbe',
        ],
        'education': [
            'ẹkọ agbegbe ile-iwe Nigeria',
            'ẹkọ ẹgbẹ Nigeria',
        ],
        'environmental_conservation': [
            'itọju ayika ikoloji Nigeria ẹgbẹ',
            'ẹgbẹ ayika agbegbe',
        ],
    },
    'ig': {
        # Igbo - Southeastern Nigeria
        'worker_cooperative': [
            'otu nkwado otu oru Nigeria',
            'otu olu ihe nọọ Nigeria',
        ],
        'mutual_aid': [
            'isusu igba boyi otu Nigeria',
            'enyemaka nke onwe onwe Nigeria',
        ],
        'commons': [
            'ala nke obodo ọnụ Nigeria',
            'ala nke ụmụ nna ebe obibi',
        ],
        'agroecology': [
            'ọrụ ugbo ime ụwa nri ụmụ obodo Nigeria',
            'mkpụrụ obodo ọrụ ugbo ala',
        ],
        'community_health': [
            'ahụ ike obodo ọ bụghị ụlọ ọgwụ Nigeria',
            'ndị ọrụ ahụike obodo',
        ],
        'nonprofit_directory': [
            'otu enweghị uru Nigeria ndepụta',
            'ọchịchọ ọmọ obodo Nigeria',
        ],
        'womens_organizations': [
            'otu ụmụ nwanyị nkwado Nigeria',
            'ike ụmụ nwanyị otu',
        ],
        'indigenous_rights': [
            'ikike ndị obodo Nigeria otu',
            'ikike ala ndị obodo',
        ],
        'renewable_energy': [
            'ike ọhụrụ nkwado anyanwụ Nigeria',
            'otu ike anyanwụ',
        ],
        'restorative_justice': [
            'ikpe iweghachi udo Nigeria',
            'idozi obodo Nigeria',
        ],
        'education': [
            'ọmụmụ ihe obodo ụlọ akwụkwọ Nigeria',
            'ọmụmụ otu Nigeria',
        ],
        'environmental_conservation': [
            'ichekwa gburugburu ebe obibi Nigeria otu',
            'otu gburugburu ọchịchọ',
        ],
    },
    'zh': {
        'worker_cooperative': [
            '合作社 工人 组织',
            '生产合作社 目录',
        ],
        'mutual_aid': [
            '互助 团结经济 组织',
            '共同体 互助组织',
        ],
        'commons': [
            '公地 集体土地 组织',
            '公共资源 管理组织',
        ],
        'agroecology': [
            '农业生态学 食物主权 组织',
            '种子图书馆 再生农业',
        ],
        'participatory_governance': [
            '参与式预算 市民大会',
            '社区治理 民主参与',
        ],
        'digital_commons': [
            '平台合作社 数字公地',
            '开源 公民技术',
        ],
    },
    'ja': {
        'worker_cooperative': [
            '協同組合 労働者 組織',
            '労働者協同組合 ディレクトリ',
        ],
        'mutual_aid': [
            '互助 連帯経済 組織',
            'コミュニティ 相互扶助',
        ],
        'commons': [
            '入会地 コモンズ 組織',
            '共有地 共有資源',
        ],
        'agroecology': [
            'アグロエコロジー 食料主権 組織',
            '種子ライブラリ 再生農業',
        ],
        'participatory_governance': [
            '参加型予算 市民集会',
            '市民参加 民主主義 組織',
        ],
        'digital_commons': [
            'プラットフォーム協同組合 デジタルコモンズ',
            'オープンソース シビックテック',
        ],
    },
    'ko': {
        'worker_cooperative': [
            '협동조합 노동자 조직',
            '노동자협동조합 디렉토리',
        ],
        'mutual_aid': [
            '상호부조 연대경제 조직',
            '커뮤니티 상호 지원',
        ],
        'agroecology': [
            '농생태학 식량주권 조직',
            '씨앗 도서관 지속가능한 농업',
        ],
        'participatory_governance': [
            '참여 예산 시민 의회',
            '시민 참여 민주주의 조직',
        ],
    },
    'id': {
        'worker_cooperative': [
            'koperasi pekerja direktori',
            'koperasi produsen organisasi',
        ],
        'mutual_aid': [
            'gotong royong ekonomi solidaritas',
            'tolong menolong koperasi',
        ],
        'agroecology': [
            'pertanian agroekologi kedaulatan pangan',
            'benih lokal pertanian berkelanjutan',
        ],
        'nonprofit_directory': [
            'direktori LSM masyarakat sipil',
            'organisasi nirlaba database',
        ],
    },
    'hi': {
        'worker_cooperative': [
            'सहकारी समिति श्रमिक संगठन',
            'कर्मचारी स्वामित्व सहकारी',
        ],
        'mutual_aid': [
            'स्वयं सहायता समूह परस्पर सहायता',
            'एकजुटता अर्थव्यवस्था संगठन',
        ],
        'agroecology': [
            'कृषि पारिस्थितिकी खाद्य संप्रभुता संगठन',
            'देसी बीज जैविक खेती',
        ],
        'community_health': [
            'सामुदायिक स्वास्थ्य आशा कार्यकर्ता',
            'स्वास्थ्य सहकारी समुदाय',
        ],
    },
    'vi': {
        'worker_cooperative': [
            'hợp tác xã lao động tổ chức',
            'hợp tác xã sản xuất danh mục',
        ],
        'mutual_aid': [
            'tương trợ kinh tế đoàn kết tổ chức',
            'giúp đỡ lẫn nhau cộng đồng',
        ],
        'agroecology': [
            'nông nghiệp sinh thái chủ quyền lương thực',
            'hạt giống địa phương nông nghiệp bền vững',
        ],
    },
    'th': {
        'worker_cooperative': [
            'สหกรณ์แรงงาน ไดเรกทอรี',
            'สหกรณ์การผลิต องค์กร',
        ],
        'mutual_aid': [
            'ช่วยเหลือเกื้อกูล เศรษฐกิจสมานฉันท์',
            'น้ำใจ ชุมชน',
        ],
        'agroecology': [
            'เกษตรนิเวศ อธิปไตยทางอาหาร องค์กร',
            'เมล็ดพันธุ์พื้นเมือง เกษตรอินทรีย์',
        ],
    },
    'tr': {
        'worker_cooperative': [
            'kooperatif işçi işçi kooperatifi dizin',
            'üretim kooperatifi organizasyonlar',
        ],
        'mutual_aid': [
            'dayanışma ekonomisi imece',
            'karşılıklı yardım organizasyonlar',
        ],
        'agroecology': [
            'tarım ekolojisi gıda egemenliği',
            'yerel tohum sürdürülebilir tarım',
        ],
    },
    'ru': {
        'worker_cooperative': [
            'кооператив рабочих организации',
            'производственный кооператив каталог',
        ],
        'mutual_aid': [
            'взаимопомощь солидарная экономика',
            'общество взаимопомощи организации',
        ],
        'commons': [
            'община общинное землевладение',
            'общее достояние организации',
        ],
    },
    'pl': {
        'worker_cooperative': [
            'spółdzielnia pracy katalog',
            'spółdzielnie pracownicze organizacje',
        ],
        'mutual_aid': [
            'ekonomia solidarna wzajemna pomoc',
            'organizacje solidarnej ekonomii',
        ],
    },
    'he': {
        'worker_cooperative': [
            'קואופרטיב עובדים ישראל',
            'קיבוץ מושב שיתופי',
        ],
        'mutual_aid': [
            'עזרה הדדית כלכלה סולידרית',
            'ארגוני עזרה הדדית',
        ],
    },
    'am': {
        'worker_cooperative': [
            'የህብረት ስራ ማህበር ድርጅቶች',
            'ሕብረት ስራ ማህበር ዝርዝር',
        ],
        'mutual_aid': [
            'ድር ኢዲር ቆቦ ኢቁብ ድርጅቶች',
            'የጋራ ድጋፍ ድርጅቶች',
        ],
    },
}

# A simple English country name lookup used by build_local_queries().
# Covers all codes in COUNTRY_LANGUAGES plus common extras.
_COUNTRY_NAMES = {
    'AE': 'UAE', 'AF': 'Afghanistan', 'AL': 'Albania', 'AM': 'Armenia',
    'AO': 'Angola', 'AR': 'Argentina', 'AT': 'Austria', 'AU': 'Australia',
    'AZ': 'Azerbaijan', 'BA': 'Bosnia', 'BD': 'Bangladesh', 'BE': 'Belgium',
    'BF': 'Burkina Faso', 'BG': 'Bulgaria', 'BH': 'Bahrain', 'BJ': 'Benin',
    'BN': 'Brunei', 'BO': 'Bolivia', 'BR': 'Brazil', 'BW': 'Botswana',
    'BY': 'Belarus', 'BZ': 'Belize', 'CA': 'Canada', 'CD': 'DR Congo',
    'CF': 'Central African Republic', 'CG': 'Congo', 'CH': 'Switzerland',
    'CI': 'Ivory Coast', 'CL': 'Chile', 'CM': 'Cameroon', 'CN': 'China',
    'CO': 'Colombia', 'CR': 'Costa Rica', 'CU': 'Cuba', 'CY': 'Cyprus',
    'CZ': 'Czech Republic', 'DE': 'Germany', 'DJ': 'Djibouti', 'DK': 'Denmark',
    'DO': 'Dominican Republic', 'DZ': 'Algeria', 'EC': 'Ecuador', 'EE': 'Estonia',
    'EG': 'Egypt', 'ER': 'Eritrea', 'ES': 'Spain', 'ET': 'Ethiopia',
    'FI': 'Finland', 'FJ': 'Fiji', 'FR': 'France', 'GA': 'Gabon',
    'GB': 'United Kingdom', 'GE': 'Georgia', 'GH': 'Ghana', 'GM': 'Gambia',
    'GN': 'Guinea', 'GQ': 'Equatorial Guinea', 'GR': 'Greece', 'GT': 'Guatemala',
    'GW': 'Guinea-Bissau', 'GY': 'Guyana', 'HN': 'Honduras', 'HR': 'Croatia',
    'HT': 'Haiti', 'HU': 'Hungary', 'ID': 'Indonesia', 'IE': 'Ireland',
    'IN': 'India', 'IQ': 'Iraq', 'IR': 'Iran', 'IS': 'Iceland',
    'IT': 'Italy', 'JM': 'Jamaica', 'JO': 'Jordan', 'JP': 'Japan',
    'KE': 'Kenya', 'KG': 'Kyrgyzstan', 'KH': 'Cambodia', 'KR': 'South Korea',
    'KW': 'Kuwait', 'KZ': 'Kazakhstan', 'LA': 'Laos', 'LB': 'Lebanon',
    'LK': 'Sri Lanka', 'LR': 'Liberia', 'LS': 'Lesotho', 'LT': 'Lithuania',
    'LU': 'Luxembourg', 'LV': 'Latvia', 'LY': 'Libya', 'MA': 'Morocco',
    'MD': 'Moldova', 'ME': 'Montenegro', 'MG': 'Madagascar', 'MK': 'North Macedonia',
    'ML': 'Mali', 'MM': 'Myanmar', 'MN': 'Mongolia', 'MT': 'Malta',
    'MW': 'Malawi', 'MX': 'Mexico', 'MY': 'Malaysia', 'MZ': 'Mozambique',
    'NA': 'Namibia', 'NE': 'Niger', 'NG': 'Nigeria', 'NI': 'Nicaragua',
    'NL': 'Netherlands', 'NO': 'Norway', 'NP': 'Nepal', 'NZ': 'New Zealand',
    'OM': 'Oman', 'PA': 'Panama', 'PE': 'Peru', 'PG': 'Papua New Guinea',
    'PH': 'Philippines', 'PK': 'Pakistan', 'PL': 'Poland', 'PS': 'Palestine',
    'PT': 'Portugal', 'PY': 'Paraguay', 'QA': 'Qatar', 'RO': 'Romania',
    'RS': 'Serbia', 'RU': 'Russia', 'RW': 'Rwanda', 'SA': 'Saudi Arabia',
    'SD': 'Sudan', 'SE': 'Sweden', 'SI': 'Slovenia', 'SK': 'Slovakia',
    'SL': 'Sierra Leone', 'SN': 'Senegal', 'SO': 'Somalia', 'SR': 'Suriname',
    'SS': 'South Sudan', 'SV': 'El Salvador', 'SY': 'Syria', 'SZ': 'Eswatini',
    'TD': 'Chad', 'TG': 'Togo', 'TH': 'Thailand', 'TJ': 'Tajikistan',
    'TL': 'Timor-Leste', 'TM': 'Turkmenistan', 'TN': 'Tunisia', 'TR': 'Turkey',
    'TT': 'Trinidad and Tobago', 'TW': 'Taiwan', 'TZ': 'Tanzania',
    'UA': 'Ukraine', 'UG': 'Uganda', 'US': 'United States', 'UY': 'Uruguay',
    'UZ': 'Uzbekistan', 'VE': 'Venezuela', 'VN': 'Vietnam', 'YE': 'Yemen',
    'ZA': 'South Africa', 'ZM': 'Zambia', 'ZW': 'Zimbabwe',
}


def build_local_queries(country_code: str, concepts: list | None = None) -> list:
    """Return search queries in each language spoken in the country, for each concept.

    Looks up COUNTRY_LANGUAGES[country_code] for the language list, then
    SEARCH_TEMPLATES[lang][concept] for query fragments. Prepends the country
    name (English) to each fragment.

    Args:
        country_code: ISO 3166-1 alpha-2 code (e.g. 'NG', 'BR').
        concepts: List of concept/topic keys to include. If None, uses all
                  keys from SEARCH_TEMPLATES for each available language.

    Returns:
        List of query strings. Empty list if country_code is unknown.
    """
    languages = COUNTRY_LANGUAGES.get(country_code)
    if not languages:
        return []

    country_name = _COUNTRY_NAMES.get(country_code, country_code)
    queries = []

    for lang in languages:
        lang_templates = SEARCH_TEMPLATES.get(lang)
        if not lang_templates:
            continue

        if concepts is None:
            topics_to_use = lang_templates.keys()
        else:
            topics_to_use = [c for c in concepts if c in lang_templates]

        for topic in topics_to_use:
            for fragment in lang_templates[topic]:
                queries.append(f"{country_name} {fragment}")

    return queries
