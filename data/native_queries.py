"""
Native-language search queries for civil society research.
Each entry: list of queries in the country's primary language(s).
Terms chosen to match how locals actually name these organizations.
"""

NATIVE_QUERIES = {

    # ── Latin America (Spanish) ───────────────────────────────────────────────
    'MX': [
        'organizaciones sociedad civil México directorio',
        'cooperativas trabajo México federación',
        'comunidades indígenas organizaciones México',
        'movimientos sociales México agroecología',
        'redes solidarias México economía popular',
    ],
    'CO': [
        'organizaciones sociales Colombia directorio',
        'cooperativas Colombia economía solidaria',
        'comunidades campesinas Colombia organizaciones',
        'juntas de acción comunal Colombia',
        'organizaciones indígenas Colombia ONIC',
    ],
    'AR': [
        'organizaciones sociedad civil Argentina directorio',
        'cooperativas trabajo Argentina INAES',
        'movimientos sociales Argentina piqueteros economía popular',
        'organizaciones comunitarias Argentina barrio',
        'empresas recuperadas Argentina',
    ],
    'PE': [
        'organizaciones sociedad civil Perú directorio',
        'cooperativas agrarias Perú',
        'comunidades campesinas indígenas Perú organizaciones',
        'rondas campesinas Perú',
        'organizaciones amazónicas Perú AIDESEP',
    ],
    'CL': [
        'organizaciones sociedad civil Chile directorio',
        'cooperativas Chile FUCOOP',
        'organizaciones mapuche Chile',
        'juntas de vecinos Chile organizaciones territoriales',
        'economía solidaria Chile redes',
    ],
    'VE': [
        'organizaciones sociedad civil Venezuela directorio',
        'consejos comunales Venezuela',
        'cooperativas Venezuela economía social',
        'organizaciones indígenas Venezuela',
    ],
    'BO': [
        'organizaciones indígenas Bolivia CIDOB CONAMAQ',
        'cooperativas Bolivia mineras agrarias',
        'organizaciones campesinas Bolivia CSUTCB',
        'economía comunitaria Bolivia organizaciones',
    ],
    'EC': [
        'organizaciones sociedad civil Ecuador directorio',
        'cooperativas Ecuador economía popular solidaria',
        'organizaciones indígenas Ecuador CONAIE',
        'juntas parroquiales Ecuador organizaciones',
    ],
    'PY': [
        'organizaciones sociedad civil Paraguay directorio',
        'cooperativas Paraguay CONPACOOP',
        'organizaciones campesinas Paraguay',
        'comunidades indígenas Paraguay organizaciones',
    ],
    'UY': [
        'organizaciones sociedad civil Uruguay directorio',
        'cooperativas Uruguay CUDECOOP FUCVAM',
        'organizaciones sociales Uruguay',
    ],
    'GT': [
        'organizaciones sociedad civil Guatemala directorio',
        'organizaciones indígenas mayas Guatemala',
        'cooperativas Guatemala CONFECOOP',
        'organizaciones campesinas Guatemala',
    ],
    'HN': [
        'organizaciones sociedad civil Honduras directorio',
        'cooperativas Honduras FEHCOOBAN',
        'organizaciones campesinas indígenas Honduras',
        'movimientos sociales Honduras',
    ],
    'NI': [
        'organizaciones sociedad civil Nicaragua directorio',
        'cooperativas Nicaragua CONACOOP',
        'organizaciones comunitarias Nicaragua',
    ],
    'CR': [
        'organizaciones sociedad civil Costa Rica directorio',
        'cooperativas Costa Rica INFOCOOP',
        'asociaciones desarrollo comunal Costa Rica',
    ],
    'PA': [
        'organizaciones sociedad civil Panamá directorio',
        'cooperativas Panamá IPACOOP',
        'organizaciones indígenas Panamá comarcas',
    ],
    'CU': [
        'organizaciones Cuba sociedad civil',
        'cooperativas agropecuarias Cuba CPA UBPC',
        'asociaciones Cuba directorio',
    ],
    'DO': [
        'organizaciones sociedad civil República Dominicana',
        'cooperativas dominicanas IDECOOP',
        'juntas de vecinos República Dominicana',
    ],
    'SR': [
        'organisaties Suriname maatschappelijk middenveld',
        'coöperaties Suriname',
        'inheemse organisaties Suriname',
    ],
    'GY': [
        'civil society organizations Guyana directory',
        'Amerindian organizations Guyana',
        'cooperatives Guyana',
    ],

    # ── Brazil (Portuguese) ──────────────────────────────────────────────────
    'BR': [
        'organizações sociedade civil Brasil diretório',
        'cooperativas Brasil OCB sistema cooperativista',
        'movimentos sociais Brasil MST Via Campesina',
        'associações comunitárias Brasil',
        'economia solidária Brasil redes FBES',
        'organizações indígenas Brasil COIAB APIB',
        'quilombolas organizações Brasil',
    ],

    # ── West Africa (French) ─────────────────────────────────────────────────
    'SN': [
        'organisations société civile Sénégal annuaire',
        'coopératives Sénégal agriculture',
        'groupements femmes Sénégal organisations',
        'organisations paysannes Sénégal CNCR',
    ],
    'CI': [
        'organisations société civile Côte d\'Ivoire annuaire',
        'coopératives agricoles Côte d\'Ivoire café cacao',
        'organisations communautaires Côte d\'Ivoire',
    ],
    'CM': [
        'organisations société civile Cameroun annuaire',
        'coopératives Cameroun agriculture',
        'organisations communautaires Cameroun',
    ],
    'MG': [
        'organisations société civile Madagascar annuaire',
        'coopératives Madagascar agriculture',
        'fokontany organismes Madagascar communautaires',
    ],

    # ── North Africa / Arab world (Arabic) ───────────────────────────────────
    'EG': [
        'منظمات المجتمع المدني مصر دليل',
        'جمعيات أهلية مصر',
        'تعاونيات مصر الاتحاد التعاوني',
        'منظمات حقوق الإنسان مصر',
        'مبادرات مجتمعية مصر',
    ],
    'MA': [
        'منظمات المجتمع المدني المغرب دليل',
        'جمعيات المغرب',
        'تعاونيات المغرب النسائية',
        'organisations société civile Maroc annuaire',
        'coopératives féminines Maroc',
    ],
    'TN': [
        'منظمات المجتمع المدني تونس',
        'جمعيات تونس دليل',
        'تعاونيات تونس',
        'organisations société civile Tunisie',
    ],
    'JO': [
        'منظمات المجتمع المدني الأردن دليل',
        'جمعيات أهلية الأردن',
        'تعاونيات الأردن',
        'منظمات حقوق الإنسان الأردن',
    ],
    'LB': [
        'منظمات المجتمع المدني لبنان دليل',
        'جمعيات لبنانية',
        'تعاونيات لبنان',
        'مبادرات مجتمعية لبنان',
    ],

    # ── East Africa (Swahili + English) ──────────────────────────────────────
    'KE': [
        'mashirika ya kiraia Kenya orodha',
        'vikundi vya ushirika Kenya',
        'mashirika ya mazingira Kenya',
        'vikundi vya wanawake Kenya',
        'mashirika ya haki binadamu Kenya',
    ],
    'TZ': [
        'mashirika ya kiraia Tanzania orodha',
        'vikundi vya ushirika Tanzania',
        'mashirika ya mazingira Tanzania',
        'VETA vikundi Tanzania jamii',
    ],
    'UG': [
        'civil society organizations Uganda Swahili',
        'vikundi vya jamii Uganda',
        'mashirika ya ushirika Uganda',
        'community organizations Uganda directory',
    ],

    # ── South Asia ───────────────────────────────────────────────────────────
    'IN': [
        'नागरिक समाज संगठन भारत सूची',
        'सहकारी समिति भारत NCUI',
        'स्वयं सहायता समूह भारत',
        'आदिवासी संगठन भारत',
        'पर्यावरण संगठन भारत',
        'civil society organizations India directory NGO Darpan',
        'self-help groups India SHG federation',
    ],
    'BD': [
        'নাগরিক সমাজ সংগঠন বাংলাদেশ তালিকা',
        'সমবায় সমিতি বাংলাদেশ',
        'গ্রামীণ উন্নয়ন সংগঠন বাংলাদেশ',
        'civil society organizations Bangladesh directory',
        'NGO Bangladesh BRAC Grameen',
    ],
    'NP': [
        'नागरिक समाज संगठन नेपाल',
        'सहकारी समिति नेपाल',
        'आदिवासी संगठन नेपाल',
        'civil society organizations Nepal directory',
    ],
    'LK': [
        'civil society organizations Sri Lanka directory',
        'cooperative societies Sri Lanka',
        'சிவில் சமூக அமைப்புகள் இலங்கை',  # Tamil
        'ශ්‍රී ලංකා සිවිල් සමාජ සංවිධාන',  # Sinhala
    ],
    'PK': [
        'سول سوسائٹی تنظیمیں پاکستان',
        'تعاونی انجمنیں پاکستان',
        'civil society organizations Pakistan directory',
        'NGO Pakistan directory',
    ],

    # ── Southeast Asia ───────────────────────────────────────────────────────
    'ID': [
        'organisasi masyarakat sipil Indonesia direktori',
        'koperasi Indonesia DEKOPIN',
        'lembaga swadaya masyarakat Indonesia LSM',
        'organisasi lingkungan hidup Indonesia',
        'organisasi adat Indonesia',
    ],
    'PH': [
        'civil society organizations Philippines directory',
        'kooperatiba Pilipinas CDA',
        'samahan ng mamamayan Pilipinas',
        'organisasyon kalikasan Pilipinas',
        'people\'s organizations Philippines NGO',
    ],
    'VN': [
        'tổ chức xã hội dân sự Việt Nam danh sách',
        'hợp tác xã Việt Nam liên minh',
        'tổ chức phi chính phủ Việt Nam',
        'civil society Vietnam directory',
    ],
    'TH': [
        'องค์กรภาคประชาสังคม ไทย รายชื่อ',
        'สหกรณ์ ไทย กรมส่งเสริมสหกรณ์',
        'องค์กรสิ่งแวดล้อม ไทย',
        'civil society organizations Thailand',
    ],
    'KH': [
        'អង្គការ​សង្គម​ស៊ីវិល​កម្ពុជា',
        'civil society organizations Cambodia directory',
        'cooperative Cambodia',
    ],
    'MM': [
        'civil society organizations Myanmar directory',
        'အရပ်ဘက်အဖွဲ့အစည်းများ မြန်မာ',
        'cooperative Myanmar',
    ],
    'MY': [
        'civil society organizations Malaysia directory',
        'koperasi Malaysia SKM',
        'pertubuhan masyarakat Malaysia',
        'persatuan alam sekitar Malaysia',
    ],

    # ── East Asia ────────────────────────────────────────────────────────────
    'CN': [
        '公民社会组织 中国 目录',
        '合作社 中国 全国合作社',
        '非政府组织 中国',
        'civil society China NGO English',
    ],
    'TW': [
        '公民社會組織 台灣 名單',
        '合作社 台灣',
        '非政府組織 台灣 NGO',
        'civil society Taiwan directory English',
    ],
    'JP': [
        'NPO法人 日本 一覧',
        '協同組合 日本 JCA',
        '市民社会組織 日本',
        'civil society Japan NPO directory',
    ],
    'KR': [
        '시민사회단체 한국 목록',
        '협동조합 한국 기획재정부',
        'NGO 한국 디렉토리',
        'civil society South Korea directory',
    ],
    'MN': [
        'иргэний нийгмийн байгууллага Монгол',
        'хоршоо Монгол',
        'civil society organizations Mongolia',
    ],

    # ── Central Asia ─────────────────────────────────────────────────────────
    'KZ': [
        'гражданское общество Казахстан организации',
        'кооперативы Казахстан',
        'НПО Казахстан реестр',
        'civil society Kazakhstan NGO',
    ],
    'UZ': [
        'фуқаролик жамияти ташкилотлари Ўзбекистон',
        'кооперативлар Ўзбекистон',
        'civil society Uzbekistan NGO',
    ],
    'GE': [
        'სამოქალაქო საზოგადოება საქართველო ორგანიზაციები',
        'კოოპერატივები საქართველო',
        'civil society Georgia NGO directory',
    ],
    'AM': [
        'քաղաքացիական հասարակություն Հայաստան կազմակերպություններ',
        'կոոператիվ Հայաստան',
        'civil society Armenia NGO',
    ],
    'TR': [
        'sivil toplum kuruluşları Türkiye dizin',
        'kooperatifler Türkiye',
        'dernekler Türkiye STGM',
        'çevre kuruluşları Türkiye',
    ],
    'IR': [
        'سازمان‌های جامعه مدنی ایران',
        'تعاونی‌های ایران',
        'NGO ایران فهرست',
        'civil society Iran organizations',
    ],

    # ── Eastern Europe ───────────────────────────────────────────────────────
    'UA': [
        'громадянське суспільство Україна організації',
        'кооперативи Україна',
        'НГО Україна реєстр',
        'civil society Ukraine NGO directory',
    ],
    'PL': [
        'organizacje społeczeństwa obywatelskiego Polska',
        'spółdzielnie Polska KRS',
        'NGO Polska baza organizacji',
        'stowarzyszenia fundacje Polska',
    ],
    'RO': [
        'organizații societate civilă România',
        'cooperative România',
        'ONG România registru',
    ],
    'RS': [
        'civilno društvo Srbija organizacije',
        'zadruge Srbija',
        'NVO Srbija registar',
    ],
    'HU': [
        'civil szervezetek Magyarország',
        'szövetkezetek Magyarország',
        'NGO Magyarország nyilvántartás',
    ],
    'BG': [
        'гражданско общество България организации',
        'кооперации България',
        'НПО България регистър',
    ],
    'GR': [
        'οργανώσεις κοινωνίας πολιτών Ελλάδα',
        'συνεταιρισμοί Ελλάδα',
        'ΜΚΟ Ελλάδα μητρώο',
    ],

    # ── Western Europe ───────────────────────────────────────────────────────
    'DE': [
        'Zivilgesellschaft Organisationen Deutschland',
        'Genossenschaften Deutschland DGRV',
        'NGO Deutschland Verzeichnis',
        'Vereine gemeinnützig Deutschland',
    ],
    'FR': [
        'organisations société civile France annuaire',
        'coopératives France Coop FR',
        'associations France RNA annuaire',
        'économie sociale solidaire France ESS',
    ],
    'ES': [
        'organizaciones sociedad civil España directorio',
        'cooperativas España CEPES',
        'ONG España directorio',
        'economía social España',
    ],
    'IT': [
        'organizzazioni società civile Italia',
        'cooperative Italia Legacoop Confcooperative',
        'ONG Italia registro',
        'terzo settore Italia',
    ],
    'PT': [
        'organizações sociedade civil Portugal',
        'cooperativas Portugal CASES',
        'ONG Portugal ONGD',
        'economia social Portugal',
    ],
    'NL': [
        'maatschappelijk middenveld Nederland organisaties',
        'coöperaties Nederland',
        'NGO Nederland register',
    ],
    'BE': [
        'organisations société civile Belgique',
        'coopératives Belgique',
        'maatschappelijk middenveld België organisaties',
        'ONG Belgique répertoire',
    ],
    'SE': [
        'civilsamhällesorganisationer Sverige',
        'kooperativ Sverige Coompanion',
        'NGO Sverige register',
    ],
    'NO': [
        'sivilsamfunnsorganisasjoner Norge',
        'samvirkeforetak Norge',
        'NGO Norge register Frivillighet',
    ],
    'DK': [
        'civilsamfundsorganisationer Danmark',
        'andelsforeninger Danmark kooperativer',
        'NGO Danmark register',
    ],
    'FI': [
        'kansalaisyhteiskunnan järjestöt Suomi',
        'osuuskunnat Suomi Pellervo',
        'NGO Suomi rekisteri',
    ],
    'CH': [
        'Zivilgesellschaft Organisationen Schweiz',
        'Genossenschaften Schweiz',
        'organisations société civile Suisse',
        'NGO Schweiz Verzeichnis',
    ],
    'AT': [
        'Zivilgesellschaft Organisationen Österreich',
        'Genossenschaften Österreich',
        'NGO Österreich Verzeichnis',
    ],
    'IE': [
        'civil society organizations Ireland directory',
        'cooperatives Ireland Co-operative',
        'charities Ireland register',
    ],
    'GB': [
        'civil society organisations UK directory',
        'cooperatives UK Co-operatives UK',
        'charities England Wales register',
        'community interest companies UK',
    ],

    # ── Sub-Saharan Africa ───────────────────────────────────────────────────
    'ZA': [
        'civil society organizations South Africa directory',
        'cooperatives South Africa SACCOL',
        'community organizations South Africa',
        'Ubuntu mutual aid South Africa',
    ],
    'GH': [
        'civil society organizations Ghana directory',
        'cooperatives Ghana GCIL',
        'community organizations Ghana',
        'susu savings groups Ghana',
    ],
    'RW': [
        'civil society organizations Rwanda directory',
        'cooperative Rwanda RCSN Sacco',
        'umuryango community Rwanda',
        'imihigo community organizations Rwanda',
    ],
    'ET': [
        'civil society organizations Ethiopia directory',
        'cooperative Ethiopia FCA',
        'iddirs Ethiopia community organizations',
        'equbs Ethiopia savings groups',
    ],
    'NG': [
        'civil society organizations Nigeria directory',
        'cooperatives Nigeria NACCIMA',
        'community organizations Nigeria',
        'thrift cooperative Nigeria esusu',
    ],
    'MZ': [
        'organizações sociedade civil Moçambique',
        'cooperativas Moçambique',
        'associações comunitárias Moçambique',
    ],
    'ZM': [
        'civil society organizations Zambia directory',
        'cooperatives Zambia',
        'community organizations Zambia',
    ],
    'ZW': [
        'civil society organizations Zimbabwe directory',
        'cooperatives Zimbabwe',
        'community organizations Zimbabwe burial societies',
    ],
    'MW': [
        'civil society organizations Malawi directory',
        'cooperatives Malawi',
        'community organizations Malawi',
    ],

    # ── Pacific ──────────────────────────────────────────────────────────────
    'AU': [
        'civil society organizations Australia directory',
        'cooperatives Australia Business Council',
        'community organizations Australia ACNC',
        'Indigenous organizations Australia AIATSIS',
    ],
    'NZ': [
        'civil society organizations New Zealand',
        'cooperatives New Zealand',
        'Māori organizations New Zealand',
        'community organizations New Zealand Charities register',
    ],
    'FJ': [
        'civil society organizations Fiji',
        'cooperatives Fiji',
        'community organizations Fiji',
        'iTaukei community organizations Fiji',
    ],
    'PG': [
        'civil society organizations Papua New Guinea',
        'cooperatives Papua New Guinea',
        'community organizations PNG',
        'wantok organizations Papua New Guinea',
    ],

    # ── North America ────────────────────────────────────────────────────────
    'CA': [
        'civil society organizations Canada directory',
        'cooperatives Canada Co-operatives Canada',
        'Indigenous organizations Canada FNIGC',
        'charities Canada CRA registered',
        'économie sociale Québec coopératives',
    ],

    # ── Caribbean ────────────────────────────────────────────────────────────
    'JM': [
        'civil society organizations Jamaica directory',
        'cooperatives Jamaica JCUL',
        'community organizations Jamaica',
    ],
    'TT': [
        'civil society organizations Trinidad Tobago',
        'cooperatives Trinidad TTCCU',
        'community organizations Trinidad',
    ],
    'HT': [
        'organisations société civile Haïti',
        'coopératives Haïti ANACAPH',
        'òganizasyon sosyete sivil Ayiti',
        'konbit solidarity Haiti',
    ],
    'CU': [
        'organizaciones sociedad civil Cuba',
        'cooperativas no agropecuarias Cuba',
        'asociaciones Cuba CDR',
    ],
}


def get_queries(cc, country_name):
    """
    Return all search queries for a country:
    standard English queries + native language queries.
    """
    standard = [
        f'civil society organizations {country_name} NGO nonprofit directory',
        f'{country_name} nonprofit registry charities database',
        f'{country_name} cooperative federation worker-owned solidarity economy',
        f'{country_name} environmental organizations ecology',
        f'{country_name} food sovereignty agroecology peasant organizations',
        f'{country_name} community health organizations',
        f'{country_name} democratic governance citizen participation',
        f'{country_name} housing land trust community organizations',
        f'{country_name} restorative justice peacebuilding organizations',
        f'{country_name} renewable energy community cooperative',
        f'{country_name} indigenous peoples organizations rights',
        f'{country_name} women cooperative self-help solidarity',
        f'{country_name} mutual aid solidarity economy network',
        f'{country_name} open source civic tech digital rights',
        f'{country_name} nonprofit social enterprise directory',
    ]
    native = NATIVE_QUERIES.get(cc, [])
    return standard + native
