/* Transcribed from the Bhadawar Hotel menu supplied by the owner. Prices are rupees. */
(() => {
  const rows = `
soups|Tomato Soup|100
soups|Veg. Soup|100
soups|Sweet Corn Soup|100
soups|Manchow Soup|100
soups|Hot N Sour|100
rolls|Spring Roll|80
rolls|Paneer Tikka Roll|120
rolls|Soya Tikka Roll|120
rolls|Soya Malai Tikka Roll|120
rolls|Paneer Malai Tikka|120
snacks|Paneer Malai Tikka|250
snacks|Paneer Hariyali Tikka|250
snacks|Paneer Achari Tikka|250
snacks|Mushroom Tikka|220
snacks|Soya Malai Chaap|200
snacks|Hariyali Chaap|200
snacks|Soya Chaap|200
snacks|Paneer Tikka|200
snacks|Soya Achari Tikka|200
snacks|Soya Banjara Tikka|200
snacks|Soya Tandoori Chaap|200
snacks|Cheez Balls|200
snacks|Crispy Paneer|200
snacks|Cutlet|150
snacks|Hara Bhara Kabab|150
snacks|Veg. Finger|150
snacks|Special Peanut|150
snacks|Papad Bhurjee|150
snacks|Aloo Chana Paneer Chat|150
snacks|Finger Chips|100
chinese|Chilli Paneer|250
chinese|Honey Chilli Potato|220
chinese|Chilli Potato|200
chinese|White Sauce Pasta|200
chinese|Red Sauce Pasta|150
chinese|Veg. Manchurian|150
chinese|Singapuri Fried Rice|140
chinese|Chilli Garlic Noodles|120
chinese|Hakka Noodles|120
chinese|Singapuri Noodles|120
chinese|Fried Rice|120
chinese|Veg. Noodles|100
mains|Navratan Curry|350
mains|Paneer Bhurjee (without Onion)|330
mains|Paneer Bhurjee|320
mains|Kajoo Curry|300
mains|Tava Paneer|300
mains|Paneer Handi|280
mains|Paneer Tikka Masala|280
mains|Soya Tikka Masala|280
mains|Paneer Changezee|280
mains|Paneer Korma|280
mains|Mashroom Paneer Korma|280
mains|Bhadawari Special Paneer|280
mains|Paneer Lawabdar|280
mains|Mashroom Do Pyazee|260
mains|Paneer Do Pyaza|240
mains|Paneer Pasanda|240
mains|Paneer Butter Masala|240
mains|Kadai Paneer|240
mains|Shahi Paneer|220
mains|Malai Paneer|220
mains|Khoa Paneer|220
mains|Malai Kofta|220
mains|Khoa Matar Paneer|220
mains|Kajoo Matar|220
mains|Matar Mashroom|220
mains|Dum Aloo|220
mains|Kashmiri Aloo|220
mains|Palak Paneer|180
mains|Matar Paneer|180
mains|Matar Masala|180
mains|Chhole Paneer|180
mains|Chana Masala|180
mains|Rajma Masala|180
mains|Mix Veg.|140
mains|Baingan Bharta|140
mains|Sev Bhajee|140
mains|Sev Tamatar|140
mains|Zeera Aloo|140
mains|Maithee Aloo|140
mains|Aloo Pyaz|140
breads|Plain Roti|10
breads|Butter Roti|15
breads|Rumali Roti|15
breads|Masala Roti|20
breads|Missi Roti|25
breads|Missi Masala|30
breads|Bambaiya Roti|30
breads|Plain Naan|40
breads|Butter Naan|45
breads|Bambaiya Naan|50
breads|Stuff Naan|55
breads|Garlic Naan|55
breads|Paneer Naan|70
breads|Chur Chur Naan|100
breads|Navratan Naan|120
breads|Lachha Parantha|45
breads|Missi Lachha Parantha|55
breads|Stuff Parantha|80
breads|Lal Mirch Partha|80
paranthas|Aloo Paratha|100
paranthas|Mix Paratha|120
paranthas|Mater Paratha|120
paranthas|Paneer Paratha|120
paranthas|Gobi Paratha|120
daal|Daal Arhar Fry|100
daal|Daal Urad Chana Fry|100
daal|Daal Tadka|130
daal|Daal Tadka (Butter)|150
daal|Daal Bhukara|200
daal|Daal Makhni|200
rice|Plain Rice|70
rice|Jeera Rice|80
rice|Daal Chawal|100
rice|Chhole Chawal|120
rice|Rajma Chawal|120
rice|Matar Paneer Rice|170
rice|Veg. Pulao|170
rice|Shahi Pulao|200
accompaniments|Plain Papad|35
accompaniments|Papad Fry|45
accompaniments|Plain Dahi|80
accompaniments|Meetha Dahi|90
accompaniments|Boondi Rayata|100
accompaniments|Pyaz Rayata|100
accompaniments|Veg. Rayata|120
accompaniments|Masala Papad|120
drinks|Mineral Water|25
drinks|Cold Drinks|40
drinks|Chai|15
drinks|Hot Coffee|30
thali|Special Thali|250
thali|Delux Thali|300
thali|Maharaja Thali|350
thali|Chinese Thali|400`.trim();

  const localDishPhotos = new Set(["accompaniments-boondi-rayata","accompaniments-masala-papad","accompaniments-meetha-dahi","accompaniments-papad-fry","accompaniments-plain-dahi","accompaniments-plain-papad","accompaniments-pyaz-rayata","accompaniments-veg-rayata","breads-bambaiya-naan","breads-bambaiya-roti","breads-butter-naan","breads-butter-roti","breads-chur-chur-naan","breads-garlic-naan","breads-lachha-parantha","breads-lal-mirch-partha","breads-masala-roti","breads-missi-lachha-parantha","breads-missi-masala","breads-missi-roti","breads-navratan-naan","breads-paneer-naan","breads-plain-naan","breads-plain-roti","breads-rumali-roti","breads-stuff-naan","breads-stuff-parantha","chinese-chilli-garlic-noodles","chinese-chilli-paneer","chinese-chilli-potato","chinese-fried-rice","chinese-hakka-noodles","chinese-honey-chilli-potato","chinese-red-sauce-pasta","chinese-singapuri-fried-rice","chinese-singapuri-noodles","chinese-veg-manchurian","chinese-veg-noodles","chinese-white-sauce-pasta","daal-daal-arhar-fry","daal-daal-bhukara","daal-daal-makhni","daal-daal-tadka-butter-","daal-daal-tadka","daal-daal-urad-chana-fry","drinks-chai","drinks-cold-drinks","drinks-hot-coffee","drinks-mineral-water","mains-aloo-pyaz","mains-baingan-bharta","mains-bhadawari-special-paneer","mains-chana-masala","mains-chhole-paneer","mains-dum-aloo","mains-kadai-paneer","mains-kajoo-curry","mains-kajoo-matar","mains-kashmiri-aloo","mains-khoa-matar-paneer","mains-khoa-paneer","mains-maithee-aloo","mains-malai-kofta","mains-malai-paneer","mains-mashroom-do-pyazee","mains-mashroom-paneer-korma","mains-matar-masala","mains-matar-mashroom","mains-matar-paneer","mains-mix-veg-","mains-navratan-curry","mains-palak-paneer","mains-paneer-bhurjee-without-onion-","mains-paneer-bhurjee","mains-paneer-butter-masala","mains-paneer-changezee","mains-paneer-do-pyaza","mains-paneer-handi","mains-paneer-korma","mains-paneer-lawabdar","mains-paneer-pasanda","mains-paneer-tikka-masala","mains-rajma-masala","mains-sev-bhajee","mains-sev-tamatar","mains-shahi-paneer","mains-soya-tikka-masala","mains-tava-paneer","mains-zeera-aloo","paranthas-aloo-paratha","paranthas-gobi-paratha","paranthas-mater-paratha","paranthas-mix-paratha","paranthas-paneer-paratha","rice-chhole-chawal","rice-daal-chawal","rice-jeera-rice","rice-matar-paneer-rice","rice-plain-rice","rice-rajma-chawal","rice-shahi-pulao","rice-veg-pulao","rolls-paneer-malai-tikka","rolls-paneer-tikka-roll","rolls-soya-malai-tikka-roll","rolls-soya-tikka-roll","rolls-spring-roll","snacks-aloo-chana-paneer-chat","snacks-cheez-balls","snacks-crispy-paneer","snacks-cutlet","snacks-finger-chips","snacks-hara-bhara-kabab","snacks-hariyali-chaap","snacks-mushroom-tikka","snacks-paneer-achari-tikka","snacks-paneer-hariyali-tikka","snacks-paneer-malai-tikka","snacks-paneer-tikka","snacks-papad-bhurjee","snacks-soya-achari-tikka","snacks-soya-banjara-tikka","snacks-soya-chaap","snacks-soya-malai-chaap","snacks-soya-tandoori-chaap","snacks-special-peanut","snacks-veg-finger","soups-hot-n-sour","soups-manchow-soup","soups-sweet-corn-soup","soups-tomato-soup","soups-veg-soup","thali-chinese-thali","thali-delux-thali","thali-maharaja-thali","thali-special-thali"]);
  const mainCourseDishPhotos = {
    'mains-paneer-butter-masala': 'assets/dishes/main-course-paneer-butter-masala-sharp.webp',
    'mains-kadai-paneer': 'assets/dishes/main-course-kadai-paneer-sharp.webp',
    'mains-shahi-paneer': 'assets/dishes/main-course-shahi-paneer-sharp.webp',
    'mains-matar-paneer': 'assets/dishes/main-course-matar-paneer-sharp.webp',
    'mains-paneer-do-pyaza': 'assets/dishes/main-course-paneer-do-pyaza-sharp.webp',
    'mains-paneer-changezee': 'assets/dishes/main-course-paneer-changezi-sharp.webp',
    'mains-paneer-lawabdar': 'assets/dishes/main-course-paneer-lawabdar-sharp.webp',
    'mains-paneer-pasanda': 'assets/dishes/main-course-paneer-pasanda-sharp.webp',
    'mains-matar-mashroom': 'assets/dishes/main-course-mushroom-matar-sharp.webp',
    'mains-mashroom-paneer-korma': 'assets/dishes/main-course-mushroom-paneer-korma-sharp.webp',
    'mains-mashroom-do-pyazee': 'assets/dishes/main-course-mushroom-do-pyaza-sharp.webp',
    'mains-mix-veg-': 'assets/dishes/main-course-mix-veg-sharp.webp',
    'mains-malai-kofta': 'assets/dishes/main-course-malai-kofta-sharp.webp',
    'mains-navratan-curry': 'assets/dishes/main-course-navratan-korma-sharp.webp',
    'mains-zeera-aloo': 'assets/dishes/main-course-aloo-jeera-sharp.webp',
    'daal-daal-makhni': 'assets/dishes/upload-daal-makhni-sharp.webp',
    'daal-daal-tadka': 'assets/dishes/main-course-daal-tadka-sharp.webp',
    'mains-chana-masala': 'assets/dishes/main-course-chhole-masala-sharp.webp'
  };
  const uploadedDishPhotos = {
    'mains-paneer-butter-masala': 'assets/dishes/upload-paneer-paneer-butter-masala-sharp.webp',
    'mains-paneer-bhurjee-without-onion-': 'assets/dishes/upload-paneer-paneer-bhurjee-without-onion-sharp.webp',
    'mains-paneer-bhurjee': 'assets/dishes/upload-paneer-paneer-bhurjee-sharp.webp',
    'mains-kajoo-curry': 'assets/dishes/upload-paneer-kajoo-curry-sharp.webp',
    'mains-tava-paneer': 'assets/dishes/upload-paneer-tava-paneer-sharp.webp',
    'mains-paneer-handi': 'assets/dishes/upload-paneer-paneer-handi-sharp.webp',
    'mains-paneer-tikka-masala': 'assets/dishes/upload-paneer-paneer-tikka-masala-sharp.webp',
    'mains-soya-tikka-masala': 'assets/dishes/upload-paneer-soya-tikka-masala-sharp.webp',
    'mains-paneer-korma': 'assets/dishes/upload-paneer-paneer-korma-sharp.webp',
    'mains-bhadawari-special-paneer': 'assets/dishes/upload-paneer-bhadawari-special-paneer-sharp.webp',
    'mains-malai-paneer': 'assets/dishes/upload-paneer-malai-paneer-sharp.webp',
    'mains-khoa-paneer': 'assets/dishes/upload-paneer-khoa-paneer-sharp.webp',
    'mains-khoa-matar-paneer': 'assets/dishes/upload-paneer-khoa-matar-paneer-sharp.webp',
    'mains-kajoo-matar': 'assets/dishes/upload-paneer-kajoo-matar-sharp.webp',
    'mains-matar-mashroom': 'assets/dishes/upload-paneer-matar-mashroom-sharp.webp',
    'mains-dum-aloo': 'assets/dishes/upload-paneer-dum-aloo-sharp.webp',
    'mains-kashmiri-aloo': 'assets/dishes/upload-paneer-kashmiri-aloo-sharp.webp',
    'mains-palak-paneer': 'assets/dishes/upload-paneer-palak-paneer-sharp.webp',
    'mains-matar-masala': 'assets/dishes/upload-paneer-matar-masala-sharp.webp',
    'mains-chhole-paneer': 'assets/dishes/upload-paneer-chhole-paneer-sharp.webp',
    'mains-chana-masala': 'assets/dishes/upload-paneer-chana-masala-sharp.webp',
    'mains-rajma-masala': 'assets/dishes/upload-paneer-rajma-masala-sharp.webp',
    'mains-baingan-bharta': 'assets/dishes/upload-paneer-baingan-bharta-sharp.webp',
    'mains-sev-bhajee': 'assets/dishes/upload-paneer-sev-bhajee-sharp.webp',
    'mains-sev-tamatar': 'assets/dishes/upload-paneer-sev-tamatar-sharp.webp',
    'mains-zeera-aloo': 'assets/dishes/upload-paneer-zeera-aloo-sharp.webp',
    'mains-maithee-aloo': 'assets/dishes/upload-paneer-maithee-aloo-sharp.webp',
    'mains-aloo-pyaz': 'assets/dishes/upload-paneer-aloo-pyaz-sharp.webp',
    'snacks-paneer-malai-tikka': 'assets/dishes/upload-snacks-paneer-malai-tikka-sharp.webp',
    'snacks-paneer-hariyali-tikka': 'assets/dishes/upload-snacks-paneer-hariyali-tikka-sharp.webp',
    'snacks-paneer-achari-tikka': 'assets/dishes/upload-snacks-paneer-achari-tikka-sharp.webp',
    'snacks-mushroom-tikka': 'assets/dishes/upload-snacks-mushroom-tikka-sharp.webp',
    'snacks-soya-malai-chaap': 'assets/dishes/upload-snacks-soya-malai-chaap-sharp.webp',
    'snacks-hariyali-chaap': 'assets/dishes/upload-snacks-hariyali-chaap-sharp.webp',
    'snacks-soya-chaap': 'assets/dishes/upload-snacks-soya-chaap-sharp.webp',
    'snacks-paneer-tikka': 'assets/dishes/upload-snacks-paneer-tikka-sharp.webp',
    'snacks-soya-achari-tikka': 'assets/dishes/upload-snacks-soya-achari-tikka-sharp.webp',
    'snacks-soya-banjara-tikka': 'assets/dishes/upload-snacks-soya-banjara-tikka-sharp.webp',
    'snacks-soya-tandoori-chaap': 'assets/dishes/upload-snacks-soya-tandoori-chaap-sharp.webp',
    'snacks-cheez-balls': 'assets/dishes/upload-snacks-cheez-balls-sharp.webp',
    'snacks-crispy-paneer': 'assets/dishes/upload-snacks-crispy-paneer-sharp.webp',
    'snacks-cutlet': 'assets/dishes/upload-snacks-cutlet-sharp.webp',
    'snacks-hara-bhara-kabab': 'assets/dishes/upload-snacks-hara-bhara-kabab-sharp.webp',
    'snacks-veg-finger': 'assets/dishes/upload-snacks-veg-finger-sharp.webp',
    'snacks-special-peanut': 'assets/dishes/upload-snacks-special-peanut-sharp.webp',
    'snacks-papad-bhurjee': 'assets/dishes/generated-papad-bhurjee-v2.jpg',
    'snacks-aloo-chana-paneer-chat': 'assets/dishes/upload-snacks-aloo-chana-paneer-chat-sharp.webp',
    'snacks-finger-chips': 'assets/dishes/upload-snacks-finger-chips-sharp.webp',
    'rolls-spring-roll': 'assets/dishes/upload-rolls-spring-roll.webp',
    'rolls-paneer-tikka-roll': 'assets/dishes/upload-rolls-paneer-tikka-roll.webp',
    'rolls-soya-tikka-roll': 'assets/dishes/upload-rolls-soya-tikka-roll.webp',
    'rolls-soya-malai-tikka-roll': 'assets/dishes/upload-rolls-soya-malai-tikka-roll.webp',
    'rolls-paneer-malai-tikka': 'assets/dishes/upload-rolls-paneer-malai-tikka-roll.webp',
    'soups-tomato-soup': 'assets/dishes/upload-soups-tomato-soup.webp',
    'soups-veg-soup': 'assets/dishes/upload-soups-veg-clear-soup.webp',
    'soups-sweet-corn-soup': 'assets/dishes/upload-soups-sweet-corn-soup.webp',
    'soups-hot-n-sour': 'assets/dishes/upload-soups-hot-sour-soup.webp',
    'accompaniments-boondi-rayata': 'assets/dishes/remaining-hires-accompaniments-boondi-rayata.webp',
    'accompaniments-masala-papad': 'assets/dishes/generated-papad-masala-v2.jpg',
    'accompaniments-meetha-dahi': 'assets/dishes/generated-dahi-sweet-v2.jpg',
    'accompaniments-papad-fry': 'assets/dishes/generated-papad-fry-v2.jpg',
    'accompaniments-plain-dahi': 'assets/dishes/generated-dahi-plain-v2.jpg',
    'accompaniments-plain-papad': 'assets/dishes/generated-papad-plain-v2.jpg',
    'accompaniments-pyaz-rayata': 'assets/dishes/remaining-hires-accompaniments-pyaz-rayata.webp',
    'accompaniments-veg-rayata': 'assets/dishes/remaining-hires-accompaniments-veg-rayata.webp',
    'breads-bambaiya-naan': 'assets/dishes/generated-bread-bambaiya-naan.webp',
    'breads-bambaiya-roti': 'assets/dishes/generated-bread-bambaiya-roti.webp',
    'breads-butter-naan': 'assets/dishes/generated-bread-butter-naan.webp',
    'breads-butter-roti': 'assets/dishes/generated-bread-butter-roti.webp',
    'breads-chur-chur-naan': 'assets/dishes/generated-bread-chur-chur-naan.webp',
    'breads-garlic-naan': 'assets/dishes/generated-bread-garlic-naan.webp',
    'breads-lachha-parantha': 'assets/dishes/generated-bread-lachha-parantha.webp',
    'breads-lal-mirch-partha': 'assets/dishes/generated-bread-lal-mirch-partha.webp',
    'breads-masala-roti': 'assets/dishes/generated-bread-masala-roti.webp',
    'breads-missi-lachha-parantha': 'assets/dishes/generated-bread-missi-lachha-parantha.webp',
    'breads-missi-masala': 'assets/dishes/generated-bread-missi-masala.webp',
    'breads-missi-roti': 'assets/dishes/generated-bread-missi-roti.webp',
    'breads-navratan-naan': 'assets/dishes/generated-bread-navratan-naan.webp',
    'breads-paneer-naan': 'assets/dishes/generated-bread-paneer-naan.webp',
    'breads-plain-naan': 'assets/dishes/generated-bread-plain-naan.webp',
    'breads-plain-roti': 'assets/dishes/generated-bread-plain-roti.webp',
    'breads-rumali-roti': 'assets/dishes/generated-bread-rumali-roti.webp',
    'breads-stuff-naan': 'assets/dishes/generated-bread-stuff-naan.webp',
    'breads-stuff-parantha': 'assets/dishes/generated-bread-stuff-parantha.webp',
    'chinese-chilli-garlic-noodles': 'assets/dishes/generated-chinese-chilli-garlic-noodles.webp',
    'chinese-chilli-paneer': 'assets/dishes/generated-chinese-chilli-paneer.webp',
    'chinese-chilli-potato': 'assets/dishes/generated-chinese-chilli-potato.webp',
    'chinese-fried-rice': 'assets/dishes/generated-chinese-fried-rice.webp',
    'chinese-hakka-noodles': 'assets/dishes/generated-chinese-hakka-noodles.webp',
    'chinese-honey-chilli-potato': 'assets/dishes/generated-chinese-honey-chilli-potato.webp',
    'chinese-red-sauce-pasta': 'assets/dishes/generated-chinese-red-sauce-pasta.webp',
    'chinese-singapuri-fried-rice': 'assets/dishes/generated-chinese-singapuri-fried-rice.webp',
    'chinese-singapuri-noodles': 'assets/dishes/generated-chinese-singapuri-noodles.webp',
    'chinese-veg-manchurian': 'assets/dishes/generated-chinese-veg-manchurian.webp',
    'chinese-veg-noodles': 'assets/dishes/generated-chinese-veg-noodles.webp',
    'chinese-white-sauce-pasta': 'assets/dishes/generated-chinese-white-sauce-pasta.webp',
    'daal-daal-arhar-fry': 'assets/dishes/generated-daal-arhar-fry.webp',
    'daal-daal-bhukara': 'assets/dishes/remaining-hires-daal-daal-bhukara.webp',
    'daal-daal-tadka-butter-': 'assets/dishes/remaining-hires-daal-daal-tadka-butter-.webp',
    'daal-daal-urad-chana-fry': 'assets/dishes/generated-daal-urad-chana-fry.webp',
    'drinks-chai': 'assets/dishes/generated-drink-chai-v2.jpg',
    'drinks-cold-drinks': 'assets/dishes/generated-drink-cola-coca-cola-v2.jpg',
    'drinks-hot-coffee': 'assets/dishes/remaining-hires-drinks-hot-coffee.webp',
    'drinks-mineral-water': 'assets/dishes/generated-drink-water-v2.jpg',
    'paranthas-aloo-paratha': 'assets/dishes/generated-parantha-aloo.webp',
    'paranthas-gobi-paratha': 'assets/dishes/generated-parantha-gobi.webp',
    'paranthas-mater-paratha': 'assets/dishes/generated-parantha-matar.webp',
    'paranthas-mix-paratha': 'assets/dishes/generated-parantha-mix.webp',
    'paranthas-paneer-paratha': 'assets/dishes/generated-parantha-paneer.webp',
    'rice-chhole-chawal': 'assets/dishes/generated-rice-chhole-chawal.webp',
    'rice-daal-chawal': 'assets/dishes/generated-rice-daal-chawal.webp',
    'rice-jeera-rice': 'assets/dishes/generated-rice-jeera-rice.webp',
    'rice-matar-paneer-rice': 'assets/dishes/generated-rice-matar-paneer-rice.webp',
    'rice-plain-rice': 'assets/dishes/generated-rice-plain-rice.webp',
    'rice-rajma-chawal': 'assets/dishes/generated-rice-rajma-chawal.webp',
    'rice-shahi-pulao': 'assets/dishes/generated-rice-shahi-pulao.webp',
    'rice-veg-pulao': 'assets/dishes/generated-rice-veg-pulao.webp',
    'soups-manchow-soup': 'assets/dishes/remaining-hires-soups-manchow-soup.webp',
    'thali-chinese-thali': 'assets/dishes/remaining-hires-thali-chinese-thali.webp',
    'thali-delux-thali': 'assets/dishes/remaining-hires-thali-delux-thali.webp',
    'thali-maharaja-thali': 'assets/dishes/remaining-hires-thali-maharaja-thali.webp',
    'thali-special-thali': 'assets/dishes/remaining-hires-thali-special-thali.webp',
  };
  const categoryInfo = {
    soups: { label: 'Soups', images: ['photo-1547592180-85f173990554', 'photo-1545729869-e4f40b34394d'], icon: 'bowl', desc: 'A warm bowl, made fresh.' },
    rolls: { label: 'Rolls', images: ['photo-1574653853027-5d3e0c0e06bb', 'photo-1572099107898-46f22b3af4f9'], icon: 'bag', desc: 'A freshly wrapped favorite.' },
    snacks: { label: 'Snacks & Tandoor', images: ['photo-1572099107898-46f22b3af4f9', 'photo-1772729996007-40bad08b3c40'], icon: 'bowl', desc: 'A crisp, smoky bite for the table.' },
    chinese: { label: 'Chinese', images: ['photo-1545729869-e4f40b34394d', 'photo-1683112687514-7cc801e4749b'], icon: 'bowl', desc: 'Indo-Chinese favorites, made to order.' },
    mains: { label: 'Main Course', images: ['photo-1701579231378-3726490a407b', 'photo-1585937421612-70a008356fbe', 'photo-1565557623262-b51c2513a641'], icon: 'bowl', desc: 'A hearty curry from our kitchen.' },
    breads: { label: 'Breads & Tandoori', images: ['photo-1680993032090-1ef7ea9b51e5', 'photo-1680993032090-1ef7ea9b51e5'], icon: 'restaurant', desc: 'Freshly prepared breads for your meal.' },
    paranthas: { label: 'Paranthas', images: ['photo-1680993032090-1ef7ea9b51e5', 'photo-1680993032090-1ef7ea9b51e5'], icon: 'restaurant', desc: 'Golden paranthas, made to order.' },
    daal: { label: 'Daal', images: ['photo-1585937421612-70a008356fbe', 'photo-1565557623262-b51c2513a641'], icon: 'bowl', desc: 'Comforting lentils, tempered with spices.' },
    rice: { label: 'Rice', images: ['photo-1563379091339-03246963d96c', 'photo-1680993032090-1ef7ea9b51e5'], icon: 'bowl', desc: 'A fragrant rice favorite.' },
    accompaniments: { label: 'Sides & Raita', images: ['photo-1512621776951-a57141f2eefd', 'photo-1572099107898-46f22b3af4f9'], icon: 'leaf', desc: 'A little something extra for the table.' },
    drinks: { label: 'Drinks', images: ['photo-1544145945-f90425340c7e', 'photo-1544145945-f90425340c7e'], icon: 'drink', desc: 'A sip to round out your meal.' },
    thali: { label: 'Thalis · packing only', images: ['photo-1680993032090-1ef7ea9b51e5', 'photo-1563379091339-03246963d96c'], icon: 'bowl', desc: 'A full meal to take away. Packing only.' }
  };
  const categoryPhotoFallbacks = {
    soups:'assets/food-soup.jpg', rolls:'assets/dishes/upload-rolls-spring-roll.webp', snacks:'assets/food-snacks.jpg',
    chinese:'assets/food-chinese.jpg', mains:'assets/food-paneer.jpg', breads:'assets/food-bread.jpg',
    paranthas:'assets/dishes/generated-bread-stuff-parantha.webp', daal:'assets/food-daal.jpg',
    rice:'assets/food-rice.jpg', accompaniments:'assets/food-raita.jpg', drinks:'assets/food-drinks.jpg', thali:'assets/food-thali.jpg'
  };
  const thaliDescriptions = {
    'thali-special-thali': 'Daal Fry, Matar Paneer or Chhole Paneer, Mix Veg, Raita, Chawal, 4 Butter Rotis, Salad & Pickle.',
    'thali-delux-thali': 'Paneer Butter Masala or Shahi Paneer, Daal Makhni, Mix Veg, Jeera Rice, 2 Naan, 2 Butter Rotis, Raita, Papad, Sweet, Salad & Pickle.',
    'thali-maharaja-thali': 'Kadai Paneer, Malai Kofta, Daal Makhni, Veg Raita, Pulao, 1 Butter Naan, 1 Stuff Naan, 1 Missi Masala, Sweet, Salad & Pickle.',
    'thali-chinese-thali': 'Fried Rice, Hakka Noodles, Manchurian, Chilli Potato, Soya Chaap & 2 Rumali Rotis.'
  };  const featured = new Set(['Maharaja Thali', 'Dum Aloo', 'Bhadawari Special Paneer', 'Paneer Pasanda', 'Kadai Paneer', 'Papad Bhurjee', 'Rajma Chawal', 'Chilli Paneer']);
  const mediumSpice = /tikka|chaap|masala|curry|bhurjee|bhurji|paneer|chhole|chana|rajma|kabab|korma|manchurian|sev|achari/i;
  const hotSpice = /chilli|manchow|hot n sour|garlic noodles/i;
  const counts = {};
  window.BHADAWAR_MENU = rows.split(/\r?\n/).map((row) => {
    const [category, name, rawPrice] = row.split('|');
    const info = categoryInfo[category];
    const index = counts[category] || 0;
    counts[category] = index + 1;
    const isPopular = featured.has(name);
    const spice = hotSpice.test(name) ? 'Hot' : mediumSpice.test(name) ? 'Medium' : 'Mild';
    const dishPhoto = /paneer/i.test(name) ? 'photo-1603894584373-5ac82b2ae398'
      : /thali/i.test(name) ? 'photo-1680993032090-1ef7ea9b51e5'
        : /rajma|biryani|pulao|chawal|rice/i.test(name) ? 'photo-1563379091339-03246963d96c'
          : /naan|phulka|paratha|kulcha|roti|bread/i.test(name) ? 'photo-1680993032090-1ef7ea9b51e5'
            : /samosa|pakora|cutlet|finger|papad|tikka|chaap|kabab/i.test(name) ? 'photo-1572099107898-46f22b3af4f9'
              : /chilli|noodle|manchow|manchurian|chinese|spring roll/i.test(name) ? 'photo-1545729869-e4f40b34394d'
                : null;
    const id = `${category}-${name.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`;
    return {
      id,
      name,
      price: Number(rawPrice),
      category,
      veg: true,
      spice,
      tag: isPopular ? 'Popular pick' : info.label,
      icon: info.icon,
      tone: category,
      photo: uploadedDishPhotos[id] || mainCourseDishPhotos[id] || (localDishPhotos.has(id) ? `assets/dishes/${id}.webp` : categoryPhotoFallbacks[category]),
      popular: isPopular ? 98 : 60,
      desc: thaliDescriptions[id] || info.desc,
      packingOnly: category === 'thali'
    };
  });
})();
