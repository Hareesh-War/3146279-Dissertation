"""
Database Manager - Medicinal Plant Identification
==================================================
SQLite database layer for species metadata and prediction logging.

Tables:
    species     - Plant species metadata (name, conservation, region, etc.)
    predictions - Prediction history log (timestamp, species, confidence)
"""

import os
import sqlite3
from datetime import datetime


class DatabaseManager:
    """Manages SQLite database for the medicinal plant identification system."""

    def __init__(self, db_path):
        self.db_path = db_path

    def _connect(self):
        """Create a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def initialize(self):
        """Create tables and populate initial species data."""
        conn = self._connect()
        cursor = conn.cursor()

        # Create species table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS species (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                scientific_name TEXT,
                common_names TEXT,
                conservation_status TEXT DEFAULT 'Unknown',
                harvesting_legal INTEGER DEFAULT 1,
                region TEXT,
                description TEXT,
                medicinal_uses TEXT,
                dataset_source TEXT,
                image_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create predictions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                image_path TEXT,
                predicted_species TEXT,
                confidence REAL,
                all_predictions TEXT,
                user_feedback TEXT,
                is_correct INTEGER
            )
        ''')

        # Create index for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_predictions_timestamp
            ON predictions(timestamp DESC)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_species_name
            ON species(name)
        ''')

        conn.commit()

        # Populate species data if table is empty
        cursor.execute('SELECT COUNT(*) FROM species')
        if cursor.fetchone()[0] == 0:
            self._populate_species(cursor)
            conn.commit()
            print(f"  Populated {cursor.execute('SELECT COUNT(*) FROM species').fetchone()[0]} species records")
        else:
            # Even for existing DBs, ensure all model species are present
            self._ensure_model_species(cursor)
            conn.commit()

        conn.close()

    def _ensure_model_species(self, cursor):
        """Ensure all model class names have a matching species record in the DB.
        
        This handles the case where the DB was created before all SIMPD
        species were added. Runs INSERT OR IGNORE so existing rows stay intact.
        """
        import os, json
        model_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')
        class_path = os.path.join(model_dir, 'phase3b_class_names.json')
        if not os.path.exists(class_path):
            return

        with open(class_path, 'r') as f:
            class_names = json.load(f)

        added = 0
        for name in class_names:
            # Check if findable via get_species logic (name, alias, or scientific_name)
            cursor.execute('SELECT 1 FROM species WHERE name = ? COLLATE NOCASE', (name,))
            if cursor.fetchone():
                continue
            alias = self.NAME_ALIASES.get(name)
            if alias:
                cursor.execute('SELECT 1 FROM species WHERE name = ? COLLATE NOCASE', (alias,))
                if cursor.fetchone():
                    continue
            cursor.execute('SELECT 1 FROM species WHERE scientific_name = ? COLLATE NOCASE', (name,))
            if cursor.fetchone():
                continue
            # Not found - insert a minimal entry so predictions don't get "Not Found"
            cursor.execute('''
                INSERT OR IGNORE INTO species (name, scientific_name, conservation_status, dataset_source)
                VALUES (?, ?, 'Unknown', 'Dataset 5 (SIMPD Commercial)')
            ''', (name, name))
            if cursor.rowcount > 0:
                added += 1
        if added > 0:
            print(f"  Added {added} missing model species to database")

    def _populate_species(self, cursor):
        """Insert known species data from all datasets."""
        species_data = [
            # ---- Dataset 1: General medicinal plants (6 species) ----
            {
                'name': 'Aloevera',
                'scientific_name': 'Aloe barbadensis miller',
                'common_names': 'Aloe vera, Burn plant, Ghritkumari',
                'conservation_status': 'Least Concern',
                'harvesting_legal': 1,
                'region': 'Global',
                'description': 'Succulent plant species widely used in traditional medicine and cosmetics.',
                'medicinal_uses': 'Skin healing, burns, digestive health, anti-inflammatory',
                'dataset_source': 'Dataset 1 (General)'
            },
            {
                'name': 'Amla',
                'scientific_name': 'Phyllanthus emblica',
                'common_names': 'Indian gooseberry, Amlaki',
                'conservation_status': 'Least Concern',
                'harvesting_legal': 1,
                'region': 'South Asia',
                'description': 'Deciduous tree native to South Asia, rich in Vitamin C.',
                'medicinal_uses': 'Immunity booster, hair care, digestive health, antioxidant',
                'dataset_source': 'Dataset 1 (General)'
            },
            {
                'name': 'Amruta_Balli',
                'scientific_name': 'Tinospora cordifolia',
                'common_names': 'Guduchi, Giloy, Heart-leaved moonseed',
                'conservation_status': 'Least Concern',
                'harvesting_legal': 1,
                'region': 'South Asia',
                'description': 'Herbaceous vine used extensively in Ayurvedic medicine.',
                'medicinal_uses': 'Immunity, fever reduction, diabetes management, anti-inflammatory',
                'dataset_source': 'Dataset 1 (General)'
            },
            {
                'name': 'Neem',
                'scientific_name': 'Azadirachta indica',
                'common_names': 'Neem, Margosa, Nimtree',
                'conservation_status': 'Least Concern',
                'harvesting_legal': 1,
                'region': 'South Asia',
                'description': 'Fast-growing tree known for its medicinal and pest-repellent properties.',
                'medicinal_uses': 'Antibacterial, antifungal, skin disorders, dental care',
                'dataset_source': 'Dataset 1 (General)'
            },
            {
                'name': 'Sandalwood',
                'scientific_name': 'Santalum album',
                'common_names': 'Indian sandalwood, Chandan',
                'conservation_status': 'Vulnerable',
                'harvesting_legal': 0,
                'region': 'South Asia',
                'description': 'Highly valued aromatic tree. Listed as Vulnerable due to over-harvesting.',
                'medicinal_uses': 'Skin care, anti-inflammatory, anxiety relief, aromatherapy',
                'dataset_source': 'Dataset 1 (General)'
            },
            {
                'name': 'Tulsi',
                'scientific_name': 'Ocimum tenuiflorum',
                'common_names': 'Holy basil, Tulasi',
                'conservation_status': 'Least Concern',
                'harvesting_legal': 1,
                'region': 'South Asia',
                'description': 'Sacred plant in Hinduism, widely used in traditional medicine.',
                'medicinal_uses': 'Respiratory health, stress relief, immunity, anti-inflammatory',
                'dataset_source': 'Dataset 1 (General)'
            },

            # ---- Dataset 2: Bangladesh regional (6 species) ----
            {
                'name': 'Basak',
                'scientific_name': 'Justicia adhatoda',
                'common_names': 'Malabar nut, Adulsa, Vasaka',
                'conservation_status': 'Least Concern',
                'harvesting_legal': 1,
                'region': 'Bangladesh, South Asia',
                'description': 'Commonly used in Bangladesh for treating respiratory conditions.',
                'medicinal_uses': 'Cough, bronchitis, asthma, tuberculosis',
                'dataset_source': 'Dataset 2 (Bangladesh Regional)'
            },
            {
                'name': 'Dhatura',
                'scientific_name': 'Datura stramonium',
                'common_names': 'Thorn apple, Jimsonweed',
                'conservation_status': 'Least Concern',
                'harvesting_legal': 1,
                'region': 'Bangladesh, Global',
                'description': 'Poisonous plant used cautiously in traditional medicine. All parts are toxic.',
                'medicinal_uses': 'Asthma (traditional), pain relief. CAUTION: Highly toxic!',
                'dataset_source': 'Dataset 2 (Bangladesh Regional)'
            },
            {
                'name': 'Talmakhna',
                'scientific_name': 'Hygrophila auriculata',
                'common_names': 'Kokilaksha, Marsh barbel',
                'conservation_status': 'Least Concern',
                'harvesting_legal': 1,
                'region': 'Bangladesh, South Asia',
                'description': 'Aquatic plant commonly found in marshy areas of Bangladesh.',
                'medicinal_uses': 'Liver disorders, urinary problems, inflammation',
                'dataset_source': 'Dataset 2 (Bangladesh Regional)'
            },
            {
                'name': 'Bohera',
                'scientific_name': 'Terminalia bellirica',
                'common_names': 'Baheda, Bibhitaki',
                'conservation_status': 'Least Concern',
                'harvesting_legal': 1,
                'region': 'Bangladesh, South Asia',
                'description': 'One of the three fruits of Triphala. Large deciduous tree.',
                'medicinal_uses': 'Digestive health, cough, laxative, hair care',
                'dataset_source': 'Dataset 2 (Bangladesh Regional)'
            },
            {
                'name': 'Arjun',
                'scientific_name': 'Terminalia arjuna',
                'common_names': 'Arjuna tree',
                'conservation_status': 'Least Concern',
                'harvesting_legal': 1,
                'region': 'Bangladesh, South Asia',
                'description': 'Bark used traditionally for cardiovascular health.',
                'medicinal_uses': 'Heart health, blood pressure, cholesterol',
                'dataset_source': 'Dataset 2 (Bangladesh Regional)'
            },
            {
                'name': 'Kalmegh',
                'scientific_name': 'Andrographis paniculata',
                'common_names': 'Green chiretta, King of bitters',
                'conservation_status': 'Least Concern',
                'harvesting_legal': 1,
                'region': 'Bangladesh, South Asia',
                'description': 'Known as King of Bitters, widely used in traditional medicine.',
                'medicinal_uses': 'Fever, cold, liver protection, anti-inflammatory',
                'dataset_source': 'Dataset 2 (Bangladesh Regional)'
            },

            # ---- Dataset 4: Endangered species (sample) ----
            {
                'name': 'Centella_asiatica',
                'scientific_name': 'Centella asiatica',
                'common_names': 'Gotu kola, Brahmi, Thankuni',
                'conservation_status': 'Near Threatened',
                'harvesting_legal': 0,
                'region': 'Asia, Africa',
                'description': 'Traditional herb endangered due to over-collection from wild habitats.',
                'medicinal_uses': 'Memory enhancement, wound healing, anxiety, skin health',
                'dataset_source': 'Dataset 4 (REMP Endangered)'
            },
            {
                'name': 'Rauvolfia_serpentina',
                'scientific_name': 'Rauvolfia serpentina',
                'common_names': 'Sarpagandha, Indian snakeroot',
                'conservation_status': 'Critically Endangered',
                'harvesting_legal': 0,
                'region': 'South Asia',
                'description': 'Listed as Critically Endangered. Source of reserpine alkaloid.',
                'medicinal_uses': 'Hypertension, mental disorders (historical). Protected species!',
                'dataset_source': 'Dataset 4 (REMP Endangered)'
            },
            {
                'name': 'Gloriosa_superba',
                'scientific_name': 'Gloriosa superba',
                'common_names': 'Flame lily, Glory lily',
                'conservation_status': 'Endangered',
                'harvesting_legal': 0,
                'region': 'South Asia, Africa',
                'description': 'Beautiful but endangered climbing lily. All parts are poisonous.',
                'medicinal_uses': 'Gout, arthritis (traditional). PROTECTED - do not harvest!',
                'dataset_source': 'Dataset 4 (REMP Endangered)'
            },

            # ---- Dataset 5: South Indian commercial species (sample) ----
            {
                'name': 'Curry_Leaf',
                'scientific_name': 'Murraya koenigii',
                'common_names': 'Curry leaf, Kadi patta, Kariveppilai',
                'conservation_status': 'Least Concern',
                'harvesting_legal': 1,
                'region': 'South India',
                'description': 'Commercially important culinary and medicinal herb from South India.',
                'medicinal_uses': 'Digestive health, diabetes, hair growth, antioxidant',
                'dataset_source': 'Dataset 5 (SIMPD Commercial)'
            },
            {
                'name': 'Hibiscus',
                'scientific_name': 'Hibiscus rosa-sinensis',
                'common_names': 'Hibiscus, Sembaruthi, Shoe flower',
                'conservation_status': 'Least Concern',
                'harvesting_legal': 1,
                'region': 'South India, Tropical',
                'description': 'Commercially grown ornamental and medicinal plant.',
                'medicinal_uses': 'Hair care, blood pressure, cholesterol, menstrual regulation',
                'dataset_source': 'Dataset 5 (SIMPD Commercial)'
            },
            {
                'name': 'Jasmine',
                'scientific_name': 'Jasminum sambac',
                'common_names': 'Jasmine, Mogra, Malligai',
                'conservation_status': 'Least Concern',
                'harvesting_legal': 1,
                'region': 'South India',
                'description': 'Commercially cultivated fragrant flower with medicinal properties.',
                'medicinal_uses': 'Stress relief, skin care, aromatherapy, wound healing',
                'dataset_source': 'Dataset 5 (SIMPD Commercial)'
            },
            {
                'name': 'Lemon_Grass',
                'scientific_name': 'Cymbopogon citratus',
                'common_names': 'Lemon grass, Sera',
                'conservation_status': 'Least Concern',
                'harvesting_legal': 1,
                'region': 'South India, Tropical',
                'description': 'Commercially important aromatic grass used in food and medicine.',
                'medicinal_uses': 'Digestive health, fever, pain relief, insect repellent',
                'dataset_source': 'Dataset 5 (SIMPD Commercial)'
            },
            {
                'name': 'Moringa',
                'scientific_name': 'Moringa oleifera',
                'common_names': 'Drumstick tree, Murungai',
                'conservation_status': 'Least Concern',
                'harvesting_legal': 1,
                'region': 'South India, Tropical',
                'description': 'Nutrient-rich tree commercially grown across South India.',
                'medicinal_uses': 'Nutrition supplement, anti-inflammatory, diabetes, lactation support',
                'dataset_source': 'Dataset 5 (SIMPD Commercial)'
            },

            # ---- Dataset 5: SIMPD species matching model class names ----
            # These entries ensure every model prediction maps to a DB record
            {
                'name': 'Abutilon Indicum',
                'scientific_name': 'Abutilon indicum',
                'common_names': 'Indian mallow, Thuthi, Atibala',
                'conservation_status': 'Least Concern',
                'harvesting_legal': 1,
                'region': 'South India, Tropical Asia',
                'description': 'A small shrub common across tropical Asia, used in traditional Siddha and Ayurvedic medicine. The leaves, roots, and bark all have medicinal value.',
                'medicinal_uses': 'Demulcent, anti-inflammatory, laxative, diuretic, fever, toothache, piles',
                'dataset_source': 'Dataset 5 (SIMPD Commercial)'
            },
            {
                'name': 'Calotropis gigantea',
                'scientific_name': 'Calotropis gigantea',
                'common_names': 'Crown flower, Giant milkweed, Erukku, Madar',
                'conservation_status': 'Least Concern',
                'harvesting_legal': 1,
                'region': 'South India, South Asia',
                'description': 'Large shrub with waxy flowers. All parts are used in traditional medicine but the latex is toxic and must be handled carefully.',
                'medicinal_uses': 'Skin diseases, digestive disorders, fever, asthma, wound healing. CAUTION: Latex is toxic!',
                'dataset_source': 'Dataset 5 (SIMPD Commercial)'
            },
            {
                'name': 'Canna indica',
                'scientific_name': 'Canna indica',
                'common_names': 'Indian shot, Canna lily, Kalvazhaikizhangu',
                'conservation_status': 'Least Concern',
                'harvesting_legal': 1,
                'region': 'South India, Tropical Americas',
                'description': 'Ornamental flowering plant with rhizomes used in traditional medicine. Commonly cultivated in gardens.',
                'medicinal_uses': 'Diuretic, anti-inflammatory, fever, wound healing, demulcent',
                'dataset_source': 'Dataset 5 (SIMPD Commercial)'
            },
            {
                'name': 'Cissus quadrangularis',
                'scientific_name': 'Cissus quadrangularis',
                'common_names': 'Veld grape, Pirandai, Hadjod, Adamant creeper',
                'conservation_status': 'Least Concern',
                'harvesting_legal': 1,
                'region': 'South India, Africa',
                'description': 'A perennial climbing plant with square stems, widely used in Siddha medicine for bone fracture healing.',
                'medicinal_uses': 'Bone healing, weight management, joint pain, digestive health, hemorrhoids',
                'dataset_source': 'Dataset 5 (SIMPD Commercial)'
            },
            {
                'name': 'Curcuma longa',
                'scientific_name': 'Curcuma longa',
                'common_names': 'Turmeric, Haldi, Manjal',
                'conservation_status': 'Least Concern',
                'harvesting_legal': 1,
                'region': 'South India, South Asia',
                'description': 'Rhizomatous herbaceous perennial plant and one of the most important commercial spices and medicinal plants in South India.',
                'medicinal_uses': 'Anti-inflammatory, antioxidant, wound healing, digestive health, skin care, immunity',
                'dataset_source': 'Dataset 5 (SIMPD Commercial)'
            },
            {
                'name': 'Eclipta prostrate',
                'scientific_name': 'Eclipta prostrata',
                'common_names': 'False daisy, Bhringraj, Karisalankanni',
                'conservation_status': 'Least Concern',
                'harvesting_legal': 1,
                'region': 'South India, Tropical worldwide',
                'description': 'A common weed with significant medicinal value, especially prized in Ayurveda for hair and liver health.',
                'medicinal_uses': 'Hair growth, liver health, anti-inflammatory, skin disorders, eye health',
                'dataset_source': 'Dataset 5 (SIMPD Commercial)'
            },
            {
                'name': 'Eichhornia Crassipes',
                'scientific_name': 'Eichhornia crassipes',
                'common_names': 'Water hyacinth, Agaya thamarai',
                'conservation_status': 'Invasive Species',
                'harvesting_legal': 1,
                'region': 'Tropical worldwide',
                'description': 'An aquatic invasive species studied for bioremediation and traditional medicine. Despite being invasive, it has documented medicinal properties.',
                'medicinal_uses': 'Wound healing, skin ailments, water purification, anti-inflammatory (traditional)',
                'dataset_source': 'Dataset 5 (SIMPD Commercial)'
            },
            {
                'name': 'Ixora coccinea',
                'scientific_name': 'Ixora coccinea',
                'common_names': 'Jungle geranium, Flame of the woods, Iddlimba, Vedchi',
                'conservation_status': 'Least Concern',
                'harvesting_legal': 1,
                'region': 'South India',
                'description': 'Common flowering shrub native to South India, used in both Ayurvedic and Siddha medicine systems.',
                'medicinal_uses': 'Diarrhea, dysentery, wound healing, leucorrhoea, anti-inflammatory',
                'dataset_source': 'Dataset 5 (SIMPD Commercial)'
            },
            {
                'name': 'Ouretlanata',
                'scientific_name': 'Aerva lanata',
                'common_names': 'Mountain knotgrass, Sirupeelai, Polpala',
                'conservation_status': 'Least Concern',
                'harvesting_legal': 1,
                'region': 'South India, Sri Lanka',
                'description': 'Small herbaceous plant highly valued in traditional medicine for urinary and kidney disorders.',
                'medicinal_uses': 'Kidney stones, urinary disorders, cough, headache, anti-inflammatory',
                'dataset_source': 'Dataset 5 (SIMPD Commercial)'
            },
            {
                'name': 'Phyllanthus amarus',
                'scientific_name': 'Phyllanthus amarus',
                'common_names': 'Stonebreaker, Keelanelli, Bhumyamalaki',
                'conservation_status': 'Least Concern',
                'harvesting_legal': 1,
                'region': 'South India, Tropical worldwide',
                'description': 'A small herb known for its hepatoprotective and kidney stone-dissolving properties in traditional medicine.',
                'medicinal_uses': 'Liver protection, kidney stones, jaundice, hepatitis B, diabetes',
                'dataset_source': 'Dataset 5 (SIMPD Commercial)'
            },
            {
                'name': 'Ricinus communis',
                'scientific_name': 'Ricinus communis',
                'common_names': 'Castor oil plant, Amanakku, Erand',
                'conservation_status': 'Least Concern',
                'harvesting_legal': 1,
                'region': 'South India, Tropical worldwide',
                'description': 'Fast-growing plant whose seeds produce castor oil. Widely used in traditional medicine and commercial products.',
                'medicinal_uses': 'Laxative, skin care, anti-inflammatory, hair growth, joint pain',
                'dataset_source': 'Dataset 5 (SIMPD Commercial)'
            },
            {
                'name': 'Senna Atriculata',
                'scientific_name': 'Senna auriculata',
                'common_names': "Tanner's cassia, Avaram, Aavartaki",
                'conservation_status': 'Least Concern',
                'harvesting_legal': 1,
                'region': 'South India',
                'description': 'Small tree with bright yellow flowers, commonly used in Siddha medicine for managing blood sugar levels.',
                'medicinal_uses': 'Diabetes management, skin health, urinary disorders, body detox',
                'dataset_source': 'Dataset 5 (SIMPD Commercial)'
            },
            {
                'name': 'Sesbania grandiflora',
                'scientific_name': 'Sesbania grandiflora',
                'common_names': 'Agathi, Vegetable hummingbird, Gaach munga',
                'conservation_status': 'Least Concern',
                'harvesting_legal': 1,
                'region': 'South India, Southeast Asia',
                'description': 'Fast-growing tree with edible flowers and leaves, used in both cuisine and traditional medicine.',
                'medicinal_uses': 'Night blindness, headache, anti-inflammatory, nasal congestion, fever',
                'dataset_source': 'Dataset 5 (SIMPD Commercial)'
            },
            {
                'name': 'Trifolium Repens',
                'scientific_name': 'Trifolium repens',
                'common_names': 'White clover, Dutch clover',
                'conservation_status': 'Least Concern',
                'harvesting_legal': 1,
                'region': 'Global (naturalised)',
                'description': 'Low-creeping herbaceous plant with documented use in folk medicine traditions worldwide.',
                'medicinal_uses': 'Blood purifier, cold remedy, gout, rheumatism (traditional folk medicine)',
                'dataset_source': 'Dataset 5 (SIMPD Commercial)'
            },
            {
                'name': 'Ziziphus mauritiana',
                'scientific_name': 'Ziziphus mauritiana',
                'common_names': 'Indian jujube, Ber, Elanthai, Badari',
                'conservation_status': 'Least Concern',
                'harvesting_legal': 1,
                'region': 'South India, South Asia',
                'description': 'Fruit-bearing tree with multiple medicinal uses, important in Ayurvedic and Unani medicine systems.',
                'medicinal_uses': 'Digestive health, wound healing, insomnia, fever, diabetes, diarrhea',
                'dataset_source': 'Dataset 5 (SIMPD Commercial)'
            },
        ]

        for species in species_data:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO species
                    (name, scientific_name, common_names, conservation_status,
                     harvesting_legal, region, description, medicinal_uses, dataset_source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    species['name'],
                    species.get('scientific_name', ''),
                    species.get('common_names', ''),
                    species.get('conservation_status', 'Unknown'),
                    species.get('harvesting_legal', 1),
                    species.get('region', ''),
                    species.get('description', ''),
                    species.get('medicinal_uses', ''),
                    species.get('dataset_source', '')
                ))
            except sqlite3.IntegrityError:
                pass

    # ============================================================
    # Species CRUD
    # ============================================================

    # Mapping from model class names to database common names
    # Handles cases where model training data used slightly different names
    NAME_ALIASES = {
        'Hibiscus Rosasinensis': 'Hibiscus',
        'Justica adhatoda': 'Basak',
        'Aloe barbadensis miller': 'Aloevera',
        'Murraya koenigii': 'Curry_Leaf',
        'Ocimum tenuiflorum': 'Tulsi',
    }

    def get_species(self, name):
        """Get species info by name, scientific name, or alias (case-insensitive)."""
        conn = self._connect()
        cursor = conn.cursor()

        # 1. Exact match by name
        cursor.execute('SELECT * FROM species WHERE name = ? COLLATE NOCASE', (name,))
        result = cursor.fetchone()

        # 2. Check known aliases (model class name -> DB common name)
        if not result:
            alias = self.NAME_ALIASES.get(name)
            if alias:
                cursor.execute('SELECT * FROM species WHERE name = ? COLLATE NOCASE', (alias,))
                result = cursor.fetchone()

        # 3. Exact match by scientific_name
        if not result:
            cursor.execute('SELECT * FROM species WHERE scientific_name = ? COLLATE NOCASE', (name,))
            result = cursor.fetchone()

        # 4. Fuzzy match on name (underscores/spaces/hyphens normalised)
        if not result:
            clean_name = name.replace('_', ' ').replace('-', ' ').strip()
            cursor.execute(
                "SELECT * FROM species WHERE REPLACE(REPLACE(name, '_', ' '), '-', ' ') LIKE ? COLLATE NOCASE",
                (f'%{clean_name}%',)
            )
            result = cursor.fetchone()

        # 5. Fuzzy match on scientific_name
        if not result:
            clean_name = name.replace('_', ' ').replace('-', ' ').strip()
            cursor.execute(
                "SELECT * FROM species WHERE REPLACE(REPLACE(scientific_name, '_', ' '), '-', ' ') LIKE ? COLLATE NOCASE",
                (f'%{clean_name}%',)
            )
            result = cursor.fetchone()

        conn.close()
        if result:
            return dict(result)
        return None

    def get_all_species(self):
        """Get all species records."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM species ORDER BY name')
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    def add_species(self, **kwargs):
        """Add a new species record."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO species
            (name, scientific_name, common_names, conservation_status,
             harvesting_legal, region, description, medicinal_uses, dataset_source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            kwargs.get('name', ''),
            kwargs.get('scientific_name', ''),
            kwargs.get('common_names', ''),
            kwargs.get('conservation_status', 'Unknown'),
            kwargs.get('harvesting_legal', 1),
            kwargs.get('region', ''),
            kwargs.get('description', ''),
            kwargs.get('medicinal_uses', ''),
            kwargs.get('dataset_source', '')
        ))
        conn.commit()
        conn.close()

    # ============================================================
    # Prediction Logging
    # ============================================================

    def log_prediction(self, image_path, predicted_species, confidence, all_predictions=None):
        """Log a prediction to the database."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO predictions (image_path, predicted_species, confidence, all_predictions)
            VALUES (?, ?, ?, ?)
        ''', (image_path, predicted_species, confidence, all_predictions))
        conn.commit()
        prediction_id = cursor.lastrowid
        conn.close()
        return prediction_id

    def get_recent_predictions(self, limit=20, offset=0):
        """Get recent predictions."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM predictions ORDER BY timestamp DESC LIMIT ? OFFSET ?',
            (limit, offset)
        )
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    def get_prediction_count(self):
        """Get total number of predictions."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM predictions')
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def update_prediction_feedback(self, prediction_id, is_correct, feedback=None):
        """Update a prediction with user feedback."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE predictions SET is_correct = ?, user_feedback = ?
            WHERE id = ?
        ''', (is_correct, feedback, prediction_id))
        conn.commit()
        conn.close()
