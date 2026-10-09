import "./preview-mode-m_uY9Nxy.js";
import "./site-config-CmTOnvL0.js";
import { c as createApiModule, j as createWalletModule, a as createStoriesModule, h as hydrateIcons, d as calculateCart, i as icon, b as calculateWalletRedemption, g as addCartItem, r as renderCartDrawer, t as trapFocus, e as changeCartQuantity, f as deleteCartItem$1 } from "./focus-lock-B9ulNr_f.js";
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
  const localDishPhotos = /* @__PURE__ */ new Set(["accompaniments-boondi-rayata", "accompaniments-masala-papad", "accompaniments-meetha-dahi", "accompaniments-papad-fry", "accompaniments-plain-dahi", "accompaniments-plain-papad", "accompaniments-pyaz-rayata", "accompaniments-veg-rayata", "breads-bambaiya-naan", "breads-bambaiya-roti", "breads-butter-naan", "breads-butter-roti", "breads-chur-chur-naan", "breads-garlic-naan", "breads-lachha-parantha", "breads-lal-mirch-partha", "breads-masala-roti", "breads-missi-lachha-parantha", "breads-missi-masala", "breads-missi-roti", "breads-navratan-naan", "breads-paneer-naan", "breads-plain-naan", "breads-plain-roti", "breads-rumali-roti", "breads-stuff-naan", "breads-stuff-parantha", "chinese-chilli-garlic-noodles", "chinese-chilli-paneer", "chinese-chilli-potato", "chinese-fried-rice", "chinese-hakka-noodles", "chinese-honey-chilli-potato", "chinese-red-sauce-pasta", "chinese-singapuri-fried-rice", "chinese-singapuri-noodles", "chinese-veg-manchurian", "chinese-veg-noodles", "chinese-white-sauce-pasta", "daal-daal-arhar-fry", "daal-daal-bhukara", "daal-daal-makhni", "daal-daal-tadka-butter-", "daal-daal-tadka", "daal-daal-urad-chana-fry", "drinks-chai", "drinks-cold-drinks", "drinks-hot-coffee", "drinks-mineral-water", "mains-aloo-pyaz", "mains-baingan-bharta", "mains-bhadawari-special-paneer", "mains-chana-masala", "mains-chhole-paneer", "mains-dum-aloo", "mains-kadai-paneer", "mains-kajoo-curry", "mains-kajoo-matar", "mains-kashmiri-aloo", "mains-khoa-matar-paneer", "mains-khoa-paneer", "mains-maithee-aloo", "mains-malai-kofta", "mains-malai-paneer", "mains-mashroom-do-pyazee", "mains-mashroom-paneer-korma", "mains-matar-masala", "mains-matar-mashroom", "mains-matar-paneer", "mains-mix-veg-", "mains-navratan-curry", "mains-palak-paneer", "mains-paneer-bhurjee-without-onion-", "mains-paneer-bhurjee", "mains-paneer-butter-masala", "mains-paneer-changezee", "mains-paneer-do-pyaza", "mains-paneer-handi", "mains-paneer-korma", "mains-paneer-lawabdar", "mains-paneer-pasanda", "mains-paneer-tikka-masala", "mains-rajma-masala", "mains-sev-bhajee", "mains-sev-tamatar", "mains-shahi-paneer", "mains-soya-tikka-masala", "mains-tava-paneer", "mains-zeera-aloo", "paranthas-aloo-paratha", "paranthas-gobi-paratha", "paranthas-mater-paratha", "paranthas-mix-paratha", "paranthas-paneer-paratha", "rice-chhole-chawal", "rice-daal-chawal", "rice-jeera-rice", "rice-matar-paneer-rice", "rice-plain-rice", "rice-rajma-chawal", "rice-shahi-pulao", "rice-veg-pulao", "rolls-paneer-malai-tikka", "rolls-paneer-tikka-roll", "rolls-soya-malai-tikka-roll", "rolls-soya-tikka-roll", "rolls-spring-roll", "snacks-aloo-chana-paneer-chat", "snacks-cheez-balls", "snacks-crispy-paneer", "snacks-cutlet", "snacks-finger-chips", "snacks-hara-bhara-kabab", "snacks-hariyali-chaap", "snacks-mushroom-tikka", "snacks-paneer-achari-tikka", "snacks-paneer-hariyali-tikka", "snacks-paneer-malai-tikka", "snacks-paneer-tikka", "snacks-papad-bhurjee", "snacks-soya-achari-tikka", "snacks-soya-banjara-tikka", "snacks-soya-chaap", "snacks-soya-malai-chaap", "snacks-soya-tandoori-chaap", "snacks-special-peanut", "snacks-veg-finger", "soups-hot-n-sour", "soups-manchow-soup", "soups-sweet-corn-soup", "soups-tomato-soup", "soups-veg-soup", "thali-chinese-thali", "thali-delux-thali", "thali-maharaja-thali", "thali-special-thali"]);
  const mainCourseDishPhotos = {
    "mains-paneer-butter-masala": "assets/dishes/main-course-paneer-butter-masala-sharp.webp",
    "mains-kadai-paneer": "assets/dishes/main-course-kadai-paneer-sharp.webp",
    "mains-shahi-paneer": "assets/dishes/main-course-shahi-paneer-sharp.webp",
    "mains-matar-paneer": "assets/dishes/main-course-matar-paneer-sharp.webp",
    "mains-paneer-do-pyaza": "assets/dishes/main-course-paneer-do-pyaza-sharp.webp",
    "mains-paneer-changezee": "assets/dishes/main-course-paneer-changezi-sharp.webp",
    "mains-paneer-lawabdar": "assets/dishes/main-course-paneer-lawabdar-sharp.webp",
    "mains-paneer-pasanda": "assets/dishes/main-course-paneer-pasanda-sharp.webp",
    "mains-matar-mashroom": "assets/dishes/main-course-mushroom-matar-sharp.webp",
    "mains-mashroom-paneer-korma": "assets/dishes/main-course-mushroom-paneer-korma-sharp.webp",
    "mains-mashroom-do-pyazee": "assets/dishes/main-course-mushroom-do-pyaza-sharp.webp",
    "mains-mix-veg-": "assets/dishes/main-course-mix-veg-sharp.webp",
    "mains-malai-kofta": "assets/dishes/main-course-malai-kofta-sharp.webp",
    "mains-navratan-curry": "assets/dishes/main-course-navratan-korma-sharp.webp",
    "mains-zeera-aloo": "assets/dishes/main-course-aloo-jeera-sharp.webp",
    "daal-daal-makhni": "assets/dishes/upload-daal-makhni-sharp.webp",
    "daal-daal-tadka": "assets/dishes/main-course-daal-tadka-sharp.webp",
    "mains-chana-masala": "assets/dishes/main-course-chhole-masala-sharp.webp"
  };
  const uploadedDishPhotos = {
    "mains-paneer-butter-masala": "assets/dishes/upload-paneer-paneer-butter-masala-sharp.webp",
    "mains-paneer-bhurjee-without-onion-": "assets/dishes/upload-paneer-paneer-bhurjee-without-onion-sharp.webp",
    "mains-paneer-bhurjee": "assets/dishes/upload-paneer-paneer-bhurjee-sharp.webp",
    "mains-kajoo-curry": "assets/dishes/upload-paneer-kajoo-curry-sharp.webp",
    "mains-tava-paneer": "assets/dishes/upload-paneer-tava-paneer-sharp.webp",
    "mains-paneer-handi": "assets/dishes/upload-paneer-paneer-handi-sharp.webp",
    "mains-paneer-tikka-masala": "assets/dishes/upload-paneer-paneer-tikka-masala-sharp.webp",
    "mains-soya-tikka-masala": "assets/dishes/upload-paneer-soya-tikka-masala-sharp.webp",
    "mains-paneer-korma": "assets/dishes/upload-paneer-paneer-korma-sharp.webp",
    "mains-bhadawari-special-paneer": "assets/dishes/upload-paneer-bhadawari-special-paneer-sharp.webp",
    "mains-malai-paneer": "assets/dishes/upload-paneer-malai-paneer-sharp.webp",
    "mains-khoa-paneer": "assets/dishes/upload-paneer-khoa-paneer-sharp.webp",
    "mains-khoa-matar-paneer": "assets/dishes/upload-paneer-khoa-matar-paneer-sharp.webp",
    "mains-kajoo-matar": "assets/dishes/upload-paneer-kajoo-matar-sharp.webp",
    "mains-matar-mashroom": "assets/dishes/upload-paneer-matar-mashroom-sharp.webp",
    "mains-dum-aloo": "assets/dishes/upload-paneer-dum-aloo-sharp.webp",
    "mains-kashmiri-aloo": "assets/dishes/upload-paneer-kashmiri-aloo-sharp.webp",
    "mains-palak-paneer": "assets/dishes/upload-paneer-palak-paneer-sharp.webp",
    "mains-matar-masala": "assets/dishes/upload-paneer-matar-masala-sharp.webp",
    "mains-chhole-paneer": "assets/dishes/upload-paneer-chhole-paneer-sharp.webp",
    "mains-chana-masala": "assets/dishes/upload-paneer-chana-masala-sharp.webp",
    "mains-rajma-masala": "assets/dishes/upload-paneer-rajma-masala-sharp.webp",
    "mains-baingan-bharta": "assets/dishes/upload-paneer-baingan-bharta-sharp.webp",
    "mains-sev-bhajee": "assets/dishes/upload-paneer-sev-bhajee-sharp.webp",
    "mains-sev-tamatar": "assets/dishes/upload-paneer-sev-tamatar-sharp.webp",
    "mains-zeera-aloo": "assets/dishes/upload-paneer-zeera-aloo-sharp.webp",
    "mains-maithee-aloo": "assets/dishes/upload-paneer-maithee-aloo-sharp.webp",
    "mains-aloo-pyaz": "assets/dishes/upload-paneer-aloo-pyaz-sharp.webp",
    "snacks-paneer-malai-tikka": "assets/dishes/upload-snacks-paneer-malai-tikka-sharp.webp",
    "snacks-paneer-hariyali-tikka": "assets/dishes/upload-snacks-paneer-hariyali-tikka-sharp.webp",
    "snacks-paneer-achari-tikka": "assets/dishes/upload-snacks-paneer-achari-tikka-sharp.webp",
    "snacks-mushroom-tikka": "assets/dishes/upload-snacks-mushroom-tikka-sharp.webp",
    "snacks-soya-malai-chaap": "assets/dishes/upload-snacks-soya-malai-chaap-sharp.webp",
    "snacks-hariyali-chaap": "assets/dishes/upload-snacks-hariyali-chaap-sharp.webp",
    "snacks-soya-chaap": "assets/dishes/upload-snacks-soya-chaap-sharp.webp",
    "snacks-paneer-tikka": "assets/dishes/upload-snacks-paneer-tikka-sharp.webp",
    "snacks-soya-achari-tikka": "assets/dishes/upload-snacks-soya-achari-tikka-sharp.webp",
    "snacks-soya-banjara-tikka": "assets/dishes/upload-snacks-soya-banjara-tikka-sharp.webp",
    "snacks-soya-tandoori-chaap": "assets/dishes/upload-snacks-soya-tandoori-chaap-sharp.webp",
    "snacks-cheez-balls": "assets/dishes/upload-snacks-cheez-balls-sharp.webp",
    "snacks-crispy-paneer": "assets/dishes/upload-snacks-crispy-paneer-sharp.webp",
    "snacks-cutlet": "assets/dishes/upload-snacks-cutlet-sharp.webp",
    "snacks-hara-bhara-kabab": "assets/dishes/upload-snacks-hara-bhara-kabab-sharp.webp",
    "snacks-veg-finger": "assets/dishes/upload-snacks-veg-finger-sharp.webp",
    "snacks-special-peanut": "assets/dishes/upload-snacks-special-peanut-sharp.webp",
    "snacks-papad-bhurjee": "assets/dishes/generated-papad-bhurjee-v2.jpg",
    "snacks-aloo-chana-paneer-chat": "assets/dishes/upload-snacks-aloo-chana-paneer-chat-sharp.webp",
    "snacks-finger-chips": "assets/dishes/upload-snacks-finger-chips-sharp.webp",
    "rolls-spring-roll": "assets/dishes/upload-rolls-spring-roll.webp",
    "rolls-paneer-tikka-roll": "assets/dishes/upload-rolls-paneer-tikka-roll.webp",
    "rolls-soya-tikka-roll": "assets/dishes/upload-rolls-soya-tikka-roll.webp",
    "rolls-soya-malai-tikka-roll": "assets/dishes/upload-rolls-soya-malai-tikka-roll.webp",
    "rolls-paneer-malai-tikka": "assets/dishes/upload-rolls-paneer-malai-tikka-roll.webp",
    "soups-tomato-soup": "assets/dishes/upload-soups-tomato-soup.webp",
    "soups-veg-soup": "assets/dishes/upload-soups-veg-clear-soup.webp",
    "soups-sweet-corn-soup": "assets/dishes/upload-soups-sweet-corn-soup.webp",
    "soups-hot-n-sour": "assets/dishes/upload-soups-hot-sour-soup.webp",
    "accompaniments-boondi-rayata": "assets/dishes/remaining-hires-accompaniments-boondi-rayata.webp",
    "accompaniments-masala-papad": "assets/dishes/generated-papad-masala-v2.jpg",
    "accompaniments-meetha-dahi": "assets/dishes/generated-dahi-sweet-v2.jpg",
    "accompaniments-papad-fry": "assets/dishes/generated-papad-fry-v2.jpg",
    "accompaniments-plain-dahi": "assets/dishes/generated-dahi-plain-v2.jpg",
    "accompaniments-plain-papad": "assets/dishes/generated-papad-plain-v2.jpg",
    "accompaniments-pyaz-rayata": "assets/dishes/remaining-hires-accompaniments-pyaz-rayata.webp",
    "accompaniments-veg-rayata": "assets/dishes/remaining-hires-accompaniments-veg-rayata.webp",
    "breads-bambaiya-naan": "assets/dishes/generated-bread-bambaiya-naan.webp",
    "breads-bambaiya-roti": "assets/dishes/generated-bread-bambaiya-roti.webp",
    "breads-butter-naan": "assets/dishes/generated-bread-butter-naan.webp",
    "breads-butter-roti": "assets/dishes/generated-bread-butter-roti.webp",
    "breads-chur-chur-naan": "assets/dishes/generated-bread-chur-chur-naan.webp",
    "breads-garlic-naan": "assets/dishes/generated-bread-garlic-naan.webp",
    "breads-lachha-parantha": "assets/dishes/generated-bread-lachha-parantha.webp",
    "breads-lal-mirch-partha": "assets/dishes/generated-bread-lal-mirch-partha.webp",
    "breads-masala-roti": "assets/dishes/generated-bread-masala-roti.webp",
    "breads-missi-lachha-parantha": "assets/dishes/generated-bread-missi-lachha-parantha.webp",
    "breads-missi-masala": "assets/dishes/generated-bread-missi-masala.webp",
    "breads-missi-roti": "assets/dishes/generated-bread-missi-roti.webp",
    "breads-navratan-naan": "assets/dishes/generated-bread-navratan-naan.webp",
    "breads-paneer-naan": "assets/dishes/generated-bread-paneer-naan.webp",
    "breads-plain-naan": "assets/dishes/generated-bread-plain-naan.webp",
    "breads-plain-roti": "assets/dishes/generated-bread-plain-roti.webp",
    "breads-rumali-roti": "assets/dishes/generated-bread-rumali-roti.webp",
    "breads-stuff-naan": "assets/dishes/generated-bread-stuff-naan.webp",
    "breads-stuff-parantha": "assets/dishes/generated-bread-stuff-parantha.webp",
    "chinese-chilli-garlic-noodles": "assets/dishes/generated-chinese-chilli-garlic-noodles.webp",
    "chinese-chilli-paneer": "assets/dishes/generated-chinese-chilli-paneer.webp",
    "chinese-chilli-potato": "assets/dishes/generated-chinese-chilli-potato.webp",
    "chinese-fried-rice": "assets/dishes/generated-chinese-fried-rice.webp",
    "chinese-hakka-noodles": "assets/dishes/generated-chinese-hakka-noodles.webp",
    "chinese-honey-chilli-potato": "assets/dishes/generated-chinese-honey-chilli-potato.webp",
    "chinese-red-sauce-pasta": "assets/dishes/generated-chinese-red-sauce-pasta.webp",
    "chinese-singapuri-fried-rice": "assets/dishes/generated-chinese-singapuri-fried-rice.webp",
    "chinese-singapuri-noodles": "assets/dishes/generated-chinese-singapuri-noodles.webp",
    "chinese-veg-manchurian": "assets/dishes/generated-chinese-veg-manchurian.webp",
    "chinese-veg-noodles": "assets/dishes/generated-chinese-veg-noodles.webp",
    "chinese-white-sauce-pasta": "assets/dishes/generated-chinese-white-sauce-pasta.webp",
    "daal-daal-arhar-fry": "assets/dishes/generated-daal-arhar-fry.webp",
    "daal-daal-bhukara": "assets/dishes/remaining-hires-daal-daal-bhukara.webp",
    "daal-daal-tadka-butter-": "assets/dishes/remaining-hires-daal-daal-tadka-butter-.webp",
    "daal-daal-urad-chana-fry": "assets/dishes/generated-daal-urad-chana-fry.webp",
    "drinks-chai": "assets/dishes/generated-drink-chai-v2.jpg",
    "drinks-cold-drinks": "assets/dishes/generated-drink-cola-coca-cola-v2.jpg",
    "drinks-hot-coffee": "assets/dishes/remaining-hires-drinks-hot-coffee.webp",
    "drinks-mineral-water": "assets/dishes/generated-drink-water-v2.jpg",
    "paranthas-aloo-paratha": "assets/dishes/generated-parantha-aloo.webp",
    "paranthas-gobi-paratha": "assets/dishes/generated-parantha-gobi.webp",
    "paranthas-mater-paratha": "assets/dishes/generated-parantha-matar.webp",
    "paranthas-mix-paratha": "assets/dishes/generated-parantha-mix.webp",
    "paranthas-paneer-paratha": "assets/dishes/generated-parantha-paneer.webp",
    "rice-chhole-chawal": "assets/dishes/generated-rice-chhole-chawal.webp",
    "rice-daal-chawal": "assets/dishes/generated-rice-daal-chawal.webp",
    "rice-jeera-rice": "assets/dishes/generated-rice-jeera-rice.webp",
    "rice-matar-paneer-rice": "assets/dishes/generated-rice-matar-paneer-rice.webp",
    "rice-plain-rice": "assets/dishes/generated-rice-plain-rice.webp",
    "rice-rajma-chawal": "assets/dishes/generated-rice-rajma-chawal.webp",
    "rice-shahi-pulao": "assets/dishes/generated-rice-shahi-pulao.webp",
    "rice-veg-pulao": "assets/dishes/generated-rice-veg-pulao.webp",
    "soups-manchow-soup": "assets/dishes/remaining-hires-soups-manchow-soup.webp",
    "thali-chinese-thali": "assets/dishes/remaining-hires-thali-chinese-thali.webp",
    "thali-delux-thali": "assets/dishes/remaining-hires-thali-delux-thali.webp",
    "thali-maharaja-thali": "assets/dishes/remaining-hires-thali-maharaja-thali.webp",
    "thali-special-thali": "assets/dishes/remaining-hires-thali-special-thali.webp"
  };
  const categoryInfo = {
    soups: { label: "Soups", images: ["photo-1547592180-85f173990554", "photo-1545729869-e4f40b34394d"], icon: "bowl", desc: "A warm bowl, made fresh." },
    rolls: { label: "Rolls", images: ["photo-1574653853027-5d3e0c0e06bb", "photo-1572099107898-46f22b3af4f9"], icon: "bag", desc: "A freshly wrapped favorite." },
    snacks: { label: "Snacks & Tandoor", images: ["photo-1572099107898-46f22b3af4f9", "photo-1772729996007-40bad08b3c40"], icon: "bowl", desc: "A crisp, smoky bite for the table." },
    chinese: { label: "Chinese", images: ["photo-1545729869-e4f40b34394d", "photo-1683112687514-7cc801e4749b"], icon: "bowl", desc: "Indo-Chinese favorites, made to order." },
    mains: { label: "Main Course", images: ["photo-1701579231378-3726490a407b", "photo-1585937421612-70a008356fbe", "photo-1565557623262-b51c2513a641"], icon: "bowl", desc: "A hearty curry from our kitchen." },
    breads: { label: "Breads & Tandoori", images: ["photo-1680993032090-1ef7ea9b51e5", "photo-1680993032090-1ef7ea9b51e5"], icon: "restaurant", desc: "Freshly prepared breads for your meal." },
    paranthas: { label: "Paranthas", images: ["photo-1680993032090-1ef7ea9b51e5", "photo-1680993032090-1ef7ea9b51e5"], icon: "restaurant", desc: "Golden paranthas, made to order." },
    daal: { label: "Daal", images: ["photo-1585937421612-70a008356fbe", "photo-1565557623262-b51c2513a641"], icon: "bowl", desc: "Comforting lentils, tempered with spices." },
    rice: { label: "Rice", images: ["photo-1563379091339-03246963d96c", "photo-1680993032090-1ef7ea9b51e5"], icon: "bowl", desc: "A fragrant rice favorite." },
    accompaniments: { label: "Sides & Raita", images: ["photo-1512621776951-a57141f2eefd", "photo-1572099107898-46f22b3af4f9"], icon: "leaf", desc: "A little something extra for the table." },
    drinks: { label: "Drinks", images: ["photo-1544145945-f90425340c7e", "photo-1544145945-f90425340c7e"], icon: "drink", desc: "A sip to round out your meal." },
    thali: { label: "Thalis · packing only", images: ["photo-1680993032090-1ef7ea9b51e5", "photo-1563379091339-03246963d96c"], icon: "bowl", desc: "A full meal to take away. Packing only." }
  };
  const categoryPhotoFallbacks = {
    soups: "assets/food-soup.jpg",
    rolls: "assets/dishes/upload-rolls-spring-roll.webp",
    snacks: "assets/food-snacks.jpg",
    chinese: "assets/food-chinese.jpg",
    mains: "assets/food-paneer.jpg",
    breads: "assets/food-bread.jpg",
    paranthas: "assets/dishes/generated-bread-stuff-parantha.webp",
    daal: "assets/food-daal.jpg",
    rice: "assets/food-rice.jpg",
    accompaniments: "assets/food-raita.jpg",
    drinks: "assets/food-drinks.jpg",
    thali: "assets/food-thali.jpg"
  };
  const thaliDescriptions = {
    "thali-special-thali": "Daal Fry, Matar Paneer or Chhole Paneer, Mix Veg, Raita, Chawal, 4 Butter Rotis, Salad & Pickle.",
    "thali-delux-thali": "Paneer Butter Masala or Shahi Paneer, Daal Makhni, Mix Veg, Jeera Rice, 2 Naan, 2 Butter Rotis, Raita, Papad, Sweet, Salad & Pickle.",
    "thali-maharaja-thali": "Kadai Paneer, Malai Kofta, Daal Makhni, Veg Raita, Pulao, 1 Butter Naan, 1 Stuff Naan, 1 Missi Masala, Sweet, Salad & Pickle.",
    "thali-chinese-thali": "Fried Rice, Hakka Noodles, Manchurian, Chilli Potato, Soya Chaap & 2 Rumali Rotis."
  };
  const featured = /* @__PURE__ */ new Set(["Maharaja Thali", "Dum Aloo", "Bhadawari Special Paneer", "Paneer Pasanda", "Kadai Paneer", "Papad Bhurjee", "Rajma Chawal", "Chilli Paneer"]);
  const mediumSpice = /tikka|chaap|masala|curry|bhurjee|bhurji|paneer|chhole|chana|rajma|kabab|korma|manchurian|sev|achari/i;
  const hotSpice = /chilli|manchow|hot n sour|garlic noodles/i;
  const counts = {};
  window.BHADAWAR_MENU = rows.split(/\r?\n/).map((row) => {
    const [category, name, rawPrice] = row.split("|");
    const info = categoryInfo[category];
    const index = counts[category] || 0;
    counts[category] = index + 1;
    const isPopular = featured.has(name);
    const spice = hotSpice.test(name) ? "Hot" : mediumSpice.test(name) ? "Medium" : "Mild";
    const id = `${category}-${name.toLowerCase().replace(/[^a-z0-9]+/g, "-")}`;
    return {
      id,
      name,
      price: Number(rawPrice),
      category,
      veg: true,
      spice,
      tag: isPopular ? "Popular pick" : info.label,
      icon: info.icon,
      tone: category,
      photo: uploadedDishPhotos[id] || mainCourseDishPhotos[id] || (localDishPhotos.has(id) ? `assets/dishes/${id}.webp` : categoryPhotoFallbacks[category]),
      popular: isPopular ? 98 : 60,
      desc: thaliDescriptions[id] || info.desc,
      packingOnly: category === "thali"
    };
  });
})();
const KEY = "bhadawar-preview-v2";
const CONFIG = window.BHADAWAR_CONFIG || {
  restaurantName: "Bhadawar Hotel",
  phoneNumber: "+91 82736 59922",
  whatsappNumber: "918273659922",
  address: "3, Daresi, Near Patthar Mandi, Mantola, Agra",
  restaurantLatitude: 27.185413,
  restaurantLongitude: 78.02044,
  openingHours: "Daily · 11:00 AM–12:00 AM",
  sampleTaxPercent: 5,
  sampleDeliveryFee: 35,
  sampleLongDeliveryFee: 50
};
const defaultApiBase = window.location.protocol === "file:" ? "http://127.0.0.1:4175/api" : `${window.location.origin}/api`;
const API_BASE = (CONFIG.apiBase || defaultApiBase).replace(/\/$/, "");
const menu = window.BHADAWAR_MENU || [
  { id: "mains-paneer-butter-masala", name: "Paneer Butter Masala", desc: "Slow cooked creamy tomato gravy with rich butter.", price: 240, category: "mains", veg: true, spice: "Mild", tag: "Guest favorite", photo: "assets/dishes/mains-paneer-butter-masala.webp", popular: 98 },
  { id: "breads-butter-naan", name: "Butter Naan", desc: "Soft & fresh from the tandoor with real butter.", price: 45, category: "breads", veg: true, spice: "Mild", tag: "Fresh baked", photo: "assets/dishes/breads-butter-naan.webp", popular: 95 },
  { id: "daal-daal-makhni", name: "Dal Makhani", desc: "Slow cooked black lentils with fresh cream.", price: 200, category: "daal", veg: true, spice: "Mild", tag: "Traditional", photo: "assets/dishes/daal-daal-makhni.webp", popular: 96 },
  { id: "snacks-paneer-tikka", name: "Paneer Tikka", desc: "Charred paneer, mint chutney", price: 200, category: "snacks", veg: true, spice: "Medium", tag: "Most loved", photo: "assets/dishes/snacks-paneer-tikka.webp", popular: 94 },
  { id: "mains-bhadawari-special-paneer", name: "Bhadawari Special Paneer", desc: "Paneer simmered in a rich tomato gravy with house spices.", price: 280, category: "mains", veg: true, spice: "Mild", tag: "Bestseller", photo: "assets/food-paneer.jpg", popular: 99 }
];
const corporateMenu = window.BHADAWAR_CORPORATE_MENU || [];
const defaultData = {
  cart: [],
  orders: [],
  reservations: [],
  corporateProfile: null,
  corporateOrder: null,
  wallet: {
    balance: 0,
    verified: false,
    signedIn: false,
    phone: "",
    welcomeGranted: false,
    entries: []
  },
  walletAccounts: {},
  deliveryAddress: {
    flat: "",
    area: "",
    landmark: "",
    phone: "",
    tag: "Home",
    deliveryDistanceBand: "under5",
    latitude: null,
    longitude: null,
    deliveryDistanceKm: null,
    summary: "Choose your delivery address"
  },
  addresses: [],
  activeAddressId: "",
  favorites: [],
  settings: {
    orderMode: "delivery",
    welcomeBonus: 100,
    earnPercent: 5,
    pointValue: 1,
    maxRedeemPercent: 50,
    prepCancelPercent: 25,
    depositPerGuest: 50,
    offerTitle: "A little welcome, on us.",
    offerText: "Join Bhadawar Wallet for a welcome treat and points with every completed order.",
    offerEnabled: true,
    dineOfferEnabled: true,
    dineOfferTitle: "A little extra for your table",
    dineOfferText: "Get ₹100 off a dine-in bill of ₹999 or more. Mention TABLE100 before the bill is closed."
  },
  menuOptions: {},
  reviews: [],
  enquiries: [],
  paidFees: {},
  lastOrderId: null,
  customerName: "Guest",
  customerProfile: null,
  foodStories: [
    { id: "kitchen-story-paneer", author: "Bhadawar Kitchen", dish: "Paneer Butter Masala", dishId: "mains-paneer-butter-masala", rating: 0, text: "Our tomato gravy simmers slowly with house spices before paneer and a swirl of cream go into the kadai. Best enjoyed hot with fresh naan.", photo: "assets/dishes/story-paneer-butter-masala.webp", mediaType: "image", status: "approved", date: new Date(Date.now() - 30 * 60 * 1e3).toISOString(), pts: 0, orderAbove599: false, editorial: true },
    { id: "kitchen-story-tandoor", author: "Bhadawar Kitchen", dish: "Paneer Tikka", dishId: "snacks-paneer-tikka", rating: 0, text: "Marinated paneer meets the tandoor for a smoky char. We serve it straight away with mint chutney, lemon and crisp onion.", photo: "assets/dishes/story-paneer-tikka.webp", mediaType: "image", status: "approved", date: new Date(Date.now() - 60 * 60 * 1e3).toISOString(), pts: 0, orderAbove599: false, editorial: true },
    { id: "kitchen-story-naan", author: "Bhadawar Kitchen", dish: "Butter Naan", dishId: "breads-butter-naan", rating: 0, text: "Pulled from the tandoor while it is still warm, brushed lightly with butter and ready to tear and share around the table.", photo: "assets/dishes/story-butter-naan.webp", mediaType: "image", status: "approved", date: new Date(Date.now() - 90 * 60 * 1e3).toISOString(), pts: 0, orderAbove599: false, editorial: true }
  ],
  leaderboard: {
    alltime: [],
    monthly: []
  }
};
let data = loadData();
const hasSavedPreviewData = localStorage.getItem(KEY) !== null;
let publicPreviewMode = false;
let customerSession = null;
let accountAuthMode = "register";
let accountOtpChallenge = null;
let accountEmailOtpChallenge = false;
let customerAuthDraft = { name: "", email: "", phone: "" };
let activeCategory = "popular";
let preferredOrderType = ["delivery", "takeaway", "dine_in"].includes(data.settings?.orderMode) ? data.settings.orderMode : "delivery";
let toastTimer;
let releaseDrawerFocus = null;
const $ = (s, root = document) => root.querySelector(s);
const $$ = (s, root = document) => Array.from(root.querySelectorAll(s));
function loadData() {
  try {
    const saved = JSON.parse(localStorage.getItem(KEY) || "{}");
    return {
      ...structuredClone(defaultData),
      ...saved,
      cart: Array.isArray(saved.cart) ? saved.cart : structuredClone(defaultData.cart),
      wallet: { ...defaultData.wallet, ...saved.wallet, entries: saved.wallet?.entries || defaultData.wallet.entries },
      deliveryAddress: { ...defaultData.deliveryAddress, ...saved.deliveryAddress },
      addresses: Array.isArray(saved.addresses) ? saved.addresses : saved.deliveryAddress?.flat || saved.deliveryAddress?.area ? [{ id: "saved-home", ...saved.deliveryAddress }] : [],
      activeAddressId: saved.activeAddressId || "",
      settings: { ...defaultData.settings, ...saved.settings },
      favorites: saved.favorites || defaultData.favorites,
      foodStories: [...(saved.foodStories || []).filter((story) => story.status === "pending"), ...structuredClone(defaultData.foodStories)],
      leaderboard: saved.leaderboard || structuredClone(defaultData.leaderboard)
    };
  } catch {
    return structuredClone(defaultData);
  }
}
function save() {
  localStorage.setItem(KEY, JSON.stringify(data));
  updateCartCounters();
}
function money(n) {
  return "₹" + Math.max(0, Math.round(n || 0)).toLocaleString("en-IN");
}
function escapeHtml(s = "") {
  return String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
}
function toast(message, error = false) {
  const el = $("#toast");
  if (!el) return;
  el.textContent = message;
  el.classList.toggle("toast-error", error);
  el.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.remove("show"), 3e3);
}
let backendNoticeShownAt = 0;
window.addEventListener("bhadawar:api-error", (event) => {
  const now = Date.now();
  if (!event.detail?.unavailable || now - backendNoticeShownAt < 8e3) return;
  backendNoticeShownAt = now;
  toast("Some live data could not load. Please try again shortly.", true);
});
let storyModule = null;
const { API, mediaUrl, syncFromBackend } = createApiModule({
  baseUrl: API_BASE,
  getData: () => data,
  getDefaultData: () => defaultData,
  renderers: {
    renderStoryBar: () => storyModule?.renderStoryBar(),
    renderFoodStories: () => storyModule?.renderFoodStories(),
    renderLeaderboard: (period) => storyModule?.renderLeaderboard(period),
    renderMiniLeaderboard: (period) => storyModule?.renderMiniLeaderboard(period),
    updateCartCounters: () => updateCartCounters(),
    renderTeamPage: () => renderTeamPage()
  }
});
function applyCustomerSession(customer) {
  customerSession = customer?.phone ? customer : null;
  if (customerSession) {
    data.customerProfile = { ...customerSession, emailVerified: Boolean(customerSession.email_verified_at), phoneVerified: Boolean(customerSession.phone_verified_at) };
    data.customerName = customerSession.name || "Guest";
    data.deliveryAddress.phone = customerSession.phone;
    data.wallet.phone = customerSession.phone;
  } else {
    data.customerProfile = null;
    data.customerName = "Guest";
    data.orders = [];
    data.addresses = [];
    data.activeAddressId = "";
    data.deliveryAddress = {
      ...defaultData.deliveryAddress,
      flat: "",
      area: "",
      landmark: "",
      phone: "",
      latitude: null,
      longitude: null,
      deliveryDistanceKm: null,
      summary: "Choose your delivery address"
    };
    data.wallet = { ...defaultData.wallet, balance: 0, phone: "", entries: [] };
    accountOrdersLoadedFor = "";
  }
  save();
}
async function refreshCustomerSession() {
  const result = await API.get("customer-auth/me");
  applyCustomerSession(result?.success ? result.customer : null);
}
function checkoutSignInRequired() {
  if (customerSession?.phone) return true;
  sessionStorage.setItem("bhadawar-checkout-intent", "1");
  save();
  window.location.href = "account.html?next=checkout";
  return false;
}
function resumeCheckoutAfterSignIn() {
  return new URLSearchParams(window.location.search).get("next") === "checkout" || sessionStorage.getItem("bhadawar-checkout-intent") === "1";
}
function finishCustomerSignIn(customer) {
  applyCustomerSession(customer);
  if (resumeCheckoutAfterSignIn()) {
    sessionStorage.removeItem("bhadawar-checkout-intent");
    window.location.replace(`index.html?next=checkout&refresh=customer-signin-${Date.now()}#menu`);
    return;
  }
  accountSection = "profile";
  renderAccountPage();
  toast("You are signed in.");
}
function openDialog(html, wide = false) {
  $("#dialog-content").innerHTML = html;
  $("#dialog").classList.remove("corporate-dialog");
  $("#dialog").classList.toggle("dialog-wide", wide);
  $("#overlay").classList.add("open");
  $("#overlay").setAttribute("aria-hidden", "false");
  document.body.style.overflow = "hidden";
}
function closeDialog() {
  $("#overlay").classList.remove("open");
  $("#overlay").setAttribute("aria-hidden", "true");
  document.body.style.overflow = "";
  $("#dialog").classList.remove("dialog-wide", "corporate-dialog");
}
const walletModule = createWalletModule({
  getData: () => data,
  money,
  openDialog,
  closeDialog,
  openCartDrawer: () => openCartDrawer(),
  icon
});
function openWalletDialog() {
  walletModule.openWalletDialog();
}
function itemById(id) {
  const base = menu.find((i) => i.id === id) || corporateMenu.find((i) => i.id === id);
  if (!base) {
    if (id === "mains-bhadawari-special-paneer") {
      return { id, name: "Bhadawari Special Paneer", desc: "Paneer simmered in a rich tomato gravy with house spices.", price: 280, category: "mains", veg: true, spice: "Mild", photo: "assets/dishes/upload-paneer-bhadawari-special-paneer-sharp.webp" };
    }
    return void 0;
  }
  return {
    category: "mains",
    veg: true,
    spice: "Medium",
    tag: "From our menu",
    popular: 80,
    desc: "Prepared fresh in our kitchen.",
    photo: "",
    ...base,
    ...data.menuOptions?.[id] || {}
  };
}
function calcCart(orderType = preferredOrderType) {
  return calculateCart(cartContext, orderType);
}
function distanceFromRestaurantKm(latitude, longitude) {
  const toRadians = (value) => value * Math.PI / 180;
  const lat1 = Number(CONFIG.restaurantLatitude ?? 27.185413);
  const lon1 = Number(CONFIG.restaurantLongitude ?? 78.02044);
  const lat2 = Number(latitude);
  const lon2 = Number(longitude);
  if (![lat1, lon1, lat2, lon2].every(Number.isFinite)) return null;
  const dLat = toRadians(lat2 - lat1);
  const dLon = toRadians(lon2 - lon1);
  const a = Math.sin(dLat / 2) ** 2 + Math.cos(toRadians(lat1)) * Math.cos(toRadians(lat2)) * Math.sin(dLon / 2) ** 2;
  return 6371 * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}
const cartContext = {
  get data() {
    return data;
  },
  config: CONFIG,
  itemById,
  distanceFromRestaurantKm,
  getOrderType: () => preferredOrderType,
  $,
  money,
  escapeHtml,
  calcCart: () => calcCart(),
  save,
  renderDrawerCart: () => renderDrawerCart(),
  renderFullMenu: () => renderFullMenu(),
  addToCart: (id) => addToCart(id),
  toast,
  icon
};
function renderDrawerCart() {
  return renderCartDrawer(cartContext);
}
function updateOrderModeUI() {
  const isDelivery = preferredOrderType === "delivery";
  const isDineIn = preferredOrderType === "dine_in";
  const locationButton = $("#top-location-btn");
  const locationLabel = $("#top-loc-label");
  const locationName = $("#top-loc-name");
  if (locationLabel && locationName && locationButton) {
    locationLabel.textContent = isDelivery ? "Delivering to" : isDineIn ? "Dine-in at" : "Takeaway from";
    locationName.textContent = isDelivery ? `Agra, ${data.deliveryAddress.area}` : "Bhadawar, Agra";
    locationButton.disabled = !isDelivery;
    locationButton.setAttribute("aria-label", isDelivery ? "Change delivery location" : isDineIn ? "Dine-in at Bhadawar Hotel & Foods, Agra" : "Takeaway from Bhadawar Hotel & Foods, Agra");
  }
  $$(".mode-tab").forEach((button) => {
    const selected = button.dataset.orderMode === preferredOrderType;
    button.classList.toggle("selected", selected);
    button.setAttribute("aria-pressed", String(selected));
  });
  $$("[data-delivery-only]").forEach((element) => {
    element.hidden = !isDelivery;
  });
  const modeMessage = $("#hero-mode-message");
  if (modeMessage) {
    modeMessage.hidden = isDelivery;
    $("#hero-mode-title").textContent = isDineIn ? "Dine-in at Bhadawar" : "Takeaway from Bhadawar";
    $("#hero-mode-subtitle").textContent = isDineIn ? "Freshly served at your table" : "Pick up your order from the restaurant";
    const modeIcon = modeMessage.querySelector(".meta-icon");
    if (modeIcon) modeIcon.innerHTML = icon(isDineIn ? "dining" : "bag");
  }
  const bookingShortcut = $("#dine-in-booking-shortcut");
  if (bookingShortcut) bookingShortcut.hidden = !isDineIn;
  const feeLabel = $("#bill-service-fee-label");
  if (feeLabel) feeLabel.textContent = isDelivery ? "Delivery fee" : "Additional fee";
  const heroDeliveryFee = $("#hero-delivery-fee");
  const heroDeliveryOffer = $(".hero-delivery-offer");
  if (heroDeliveryFee) {
    const calc = calcCart("delivery");
    heroDeliveryFee.textContent = calc.outsideDeliveryRange ? "Unavailable" : calc.firstOrder ? "Free" : money(calc.delivery);
  }
  if (heroDeliveryOffer) heroDeliveryOffer.textContent = "First order free · within 10 km";
  const codLabel = $("#checkout-cod-label");
  if (codLabel) codLabel.textContent = isDelivery ? "Cash on Delivery (COD)" : "Pay at the restaurant";
  updateCartCounters();
  renderDrawerCart();
}
function updateCartCounters() {
  const count = data.cart.reduce((n, i) => n + i.qty, 0);
  const calc = calcCart();
  const heroDeliveryFee = $("#hero-delivery-fee");
  if (heroDeliveryFee) {
    const deliveryCalc = calcCart("delivery");
    heroDeliveryFee.textContent = deliveryCalc.outsideDeliveryRange ? "Unavailable" : deliveryCalc.firstOrder ? "Free" : money(deliveryCalc.delivery);
  }
  const badge = $("#cart-count");
  if (badge) badge.textContent = count;
  const totalLabel = $("#header-cart-total");
  if (totalLabel) totalLabel.textContent = money(calc.subtotal);
  const drawerCount = $("#drawer-cart-count");
  if (drawerCount) drawerCount.textContent = `${count} item${count === 1 ? "" : "s"}`;
  const mobileBar = $("#mobile-order-bar");
  if (mobileBar) {
    mobileBar.hidden = count === 0;
    const mobCount = $("#mobile-order-count");
    if (mobCount) mobCount.textContent = `${count} item${count === 1 ? "" : "s"}`;
    const mobTotal = $("#mobile-cart-total");
    if (mobTotal) mobTotal.textContent = money(calc.subtotal);
  }
  const ptsVal = $("#header-points-val");
  if (ptsVal) ptsVal.textContent = data.wallet.balance;
  const rewardsBalance = $("#rewards-points-balance");
  if (rewardsBalance) rewardsBalance.textContent = data.wallet.balance;
  updateCustomerHeader();
  updateFeaturedCardButtons();
}
function updateCustomerHeader() {
  const link = $("#header-signin-btn");
  if (!link) return;
  const signedIn = Boolean(customerSession?.phone);
  const label = link.querySelector("span:last-child");
  if (label) label.textContent = signedIn ? "Profile" : "Sign in";
  link.setAttribute("aria-label", signedIn ? "Open customer profile" : "Sign in to your customer profile");
}
function updateFeaturedCardButtons() {
  $$("[data-dish-slot]").forEach((slot) => {
    const id = slot.dataset.dishSlot;
    const item = itemById(id);
    const row = data.cart.find((r) => r.id === id);
    if (!item) return;
    if (row && row.qty > 0) {
      slot.innerHTML = `
        <div class="quantity-control" aria-label="${escapeHtml(item.name)} quantity">
          <button type="button" data-featured-qty="${id}" data-step="-1">−</button>
          <span>${row.qty}</span>
          <button type="button" data-featured-qty="${id}" data-step="1">+</button>
        </div>
      `;
    } else {
      slot.innerHTML = `<button type="button" class="add-to-cart-btn" data-add="${id}">Add +</button>`;
    }
  });
}
function openCartDrawer() {
  const drawer = $("#cart-drawer");
  const backdrop = $("#drawer-backdrop");
  if (!drawer || !backdrop) return;
  renderDrawerCart();
  drawer.hidden = false;
  backdrop.hidden = false;
  releaseDrawerFocus?.();
  releaseDrawerFocus = trapFocus(drawer, { onEscape: closeCartDrawer });
  requestAnimationFrame(() => {
    drawer.classList.add("open");
    backdrop.classList.add("open");
  });
}
function closeCartDrawer() {
  const drawer = $("#cart-drawer");
  const backdrop = $("#drawer-backdrop");
  if (!drawer || !backdrop) return;
  releaseDrawerFocus?.();
  releaseDrawerFocus = null;
  drawer.classList.remove("open");
  backdrop.classList.remove("open");
  setTimeout(() => {
    drawer.hidden = true;
    if (!$("#address-drawer")?.classList.contains("open")) {
      backdrop.hidden = true;
    }
  }, 250);
}
function openAddressDrawer() {
  const drawer = $("#address-drawer");
  const backdrop = $("#drawer-backdrop");
  if (!drawer || !backdrop) return;
  $("#addr-flat").value = data.deliveryAddress.flat || "";
  $("#addr-area").value = data.deliveryAddress.area || "";
  $("#addr-landmark").value = data.deliveryAddress.landmark || "";
  $("#addr-phone").value = data.deliveryAddress.phone || data.customerProfile?.phone || "";
  $("#addr-distance-band").value = data.deliveryAddress.deliveryDistanceBand || "under5";
  const savedPin = data.deliveryAddress.latitude != null && data.deliveryAddress.longitude != null && Number.isFinite(Number(data.deliveryAddress.latitude)) && Number.isFinite(Number(data.deliveryAddress.longitude));
  const mapFrame = $("#address-location-map");
  const mapGraphic = $(".map-graphic");
  const pinLink = $("#addr-google-maps-link");
  const distanceSelect = $("#addr-distance-band");
  if (savedPin) {
    const latitude = Number(data.deliveryAddress.latitude);
    const longitude = Number(data.deliveryAddress.longitude);
    const distanceKm = Number(data.deliveryAddress.deliveryDistanceKm ?? distanceFromRestaurantKm(latitude, longitude));
    if (Number.isFinite(distanceKm)) {
      data.deliveryAddress.deliveryDistanceKm = distanceKm;
      data.deliveryAddress.deliveryDistanceBand = distanceKm > 10 ? "over10" : distanceKm > 5 ? "5to10" : "under5";
      if (distanceSelect) {
        distanceSelect.value = data.deliveryAddress.deliveryDistanceBand;
        distanceSelect.disabled = true;
      }
    }
    if (mapFrame) {
      mapFrame.src = `https://www.google.com/maps?q=${latitude},${longitude}&z=17&output=embed`;
      mapFrame.hidden = false;
    }
    if (mapGraphic) mapGraphic.hidden = true;
    if (pinLink) {
      pinLink.href = `https://www.google.com/maps/dir/?api=1&destination=${latitude},${longitude}`;
      pinLink.hidden = false;
    }
    $("#addr-location-status").textContent = `Saved pin · ${Number.isFinite(distanceKm) ? `${distanceKm.toFixed(1)} km from Bhadawar` : `${latitude}, ${longitude}`}. Delivery fee/range is based on this pin.`;
    $("#use-gps-btn").innerHTML = `${icon("compass", "gps-icon")} Update my location`;
  } else {
    if (distanceSelect) distanceSelect.disabled = false;
    if (mapFrame) {
      mapFrame.removeAttribute("src");
      mapFrame.hidden = true;
    }
    if (mapGraphic) mapGraphic.hidden = false;
    if (pinLink) pinLink.hidden = true;
    $("#addr-location-status").textContent = "Share your location to attach a map pin to your delivery order.";
    $("#use-gps-btn").innerHTML = `${icon("compass", "gps-icon")} Use my current location`;
  }
  const tagRadio = $(`input[name="addr-tag"][value="${data.deliveryAddress.tag || "Home"}"]`);
  if (tagRadio) tagRadio.checked = true;
  drawer.hidden = false;
  backdrop.hidden = false;
  releaseDrawerFocus?.();
  releaseDrawerFocus = trapFocus(drawer, { onEscape: closeAddressDrawer });
  requestAnimationFrame(() => {
    drawer.classList.add("open");
    backdrop.classList.add("open");
  });
}
function requestCurrentDeliveryLocation() {
  const button = $("#use-gps-btn");
  const status = $("#addr-location-status");
  const pinLink = $("#addr-google-maps-link");
  const mapFrame = $("#address-location-map");
  const mapGraphic = $(".map-graphic");
  if (!button) return;
  if (!navigator.geolocation) {
    if (status) status.textContent = "Location is not supported by this browser. You can still enter your address above.";
    toast("This browser cannot share its location.", true);
    return;
  }
  button.disabled = true;
  button.innerHTML = `${icon("compass", "gps-icon")} Finding your location…`;
  if (status) status.textContent = "Requesting your current location. Allow access to attach a map pin to this delivery.";
  navigator.geolocation.getCurrentPosition((position) => {
    const latitude = Number(position.coords.latitude.toFixed(6));
    const longitude = Number(position.coords.longitude.toFixed(6));
    const distanceKm = distanceFromRestaurantKm(latitude, longitude);
    data.deliveryAddress.latitude = latitude;
    data.deliveryAddress.longitude = longitude;
    data.deliveryAddress.deliveryDistanceKm = distanceKm;
    data.deliveryAddress.deliveryDistanceBand = distanceKm > 10 ? "over10" : distanceKm > 5 ? "5to10" : "under5";
    $("#addr-distance-band").value = data.deliveryAddress.deliveryDistanceBand;
    $("#addr-distance-band").disabled = true;
    save();
    const mapUrl = `https://www.google.com/maps?q=${latitude},${longitude}&z=17&output=embed`;
    const directionsUrl = `https://www.google.com/maps/dir/?api=1&destination=${latitude},${longitude}`;
    if (mapFrame) {
      mapFrame.src = mapUrl;
      mapFrame.hidden = false;
    }
    if (mapGraphic) mapGraphic.hidden = true;
    if (pinLink) {
      pinLink.href = directionsUrl;
      pinLink.hidden = false;
    }
    if (status) status.textContent = `Pin saved · ${distanceKm.toFixed(1)} km from Bhadawar. ${distanceKm > 10 ? "Delivery is not available beyond 10 km." : `Estimated standard delivery: ${distanceKm > 5 ? "₹50" : "₹35"}; first order is free.`}`;
    updateOrderModeUI();
    button.disabled = false;
    button.innerHTML = `${icon("compass", "gps-icon")} Update my location`;
    toast(distanceKm > 10 ? "This location is outside the 10 km delivery range." : "Your delivery pin and distance were saved.");
  }, (error) => {
    const message = error.code === 1 ? "Location permission was not granted. You can enter your address manually." : error.code === 3 ? "Location took too long. Try again or enter your address manually." : "Could not detect your location. Check your device settings and try again.";
    if (status) status.textContent = message;
    button.disabled = false;
    button.innerHTML = `${icon("compass", "gps-icon")} Use my current location`;
    toast(message, true);
  }, { enableHighAccuracy: true, timeout: 15e3, maximumAge: 6e4 });
}
function closeAddressDrawer() {
  const drawer = $("#address-drawer");
  const backdrop = $("#drawer-backdrop");
  if (!drawer || !backdrop) return;
  releaseDrawerFocus?.();
  releaseDrawerFocus = null;
  drawer.classList.remove("open");
  backdrop.classList.remove("open");
  setTimeout(() => {
    drawer.hidden = true;
    if (!$("#cart-drawer")?.classList.contains("open")) {
      backdrop.hidden = true;
    }
  }, 250);
}
function addToCart(id) {
  return addCartItem(cartContext, id);
}
function changeQuantity(id, step) {
  return changeCartQuantity(cartContext, id, step);
}
function deleteCartItem(id) {
  return deleteCartItem$1(cartContext, id);
}
function renderFullMenu() {
  const grid = $("#menu-grid");
  if (!grid) return;
  const q = ($("#menu-search")?.value || "").trim().toLowerCase();
  const vegOnly = $("#veg-only")?.checked;
  const spice = $("#spice-filter")?.value || "all";
  const products = menu.map((m) => itemById(m.id)).filter((m) => m && m.available !== false).filter((m) => {
    if (activeCategory === "popular") return m.popular >= 90;
    if (activeCategory === "all") return true;
    return m.category === activeCategory;
  }).filter((m) => !vegOnly || m.veg).filter((m) => spice === "all" || m.spice === spice).filter((m) => !q || `${m.name} ${m.desc} ${m.tag}`.toLowerCase().includes(q)).sort((a, b) => (b.popular || 0) - (a.popular || 0));
  const countEl = $("#menu-result-count");
  if (countEl) {
    countEl.textContent = `${products.length} dish${products.length === 1 ? "" : "es"}`;
  }
  if (!products.length) {
    grid.innerHTML = '<div style="grid-column:1/-1;text-align:center;padding:36px;color:#7e878e;">No dishes found matching your search.</div>';
    return;
  }
  grid.innerHTML = products.map((item) => {
    const row = data.cart.find((r) => r.id === item.id);
    const photoSrc = item.photo?.startsWith("assets/") ? item.photo : "assets/food-paneer.jpg";
    const isFav = data.favorites.includes(item.id);
    return `
      <article class="dish-card" data-dish-id="${item.id}">
        <div class="dish-img-wrap">
          <img src="${escapeHtml(photoSrc)}" alt="${escapeHtml(item.name)}" loading="lazy" onerror="this.src='assets/food-paneer.jpg'">
          ${item.popular > 95 ? '<span class="card-tag-pill">★ Bestseller</span>' : ""}
            <button type="button" class="favorite-heart-btn ${isFav ? "active" : ""}" data-fav="${item.id}" aria-label="Favorite ${escapeHtml(item.name)}" aria-pressed="${isFav}">
            ${icon("heart")}
          </button>
        </div>
        <div class="dish-content">
          <h3 class="dish-name">${escapeHtml(item.name)}</h3>
          <p class="dish-desc">${escapeHtml(item.desc)}</p>
          <div class="dish-footer">
            <div class="dish-pricing">
              <strong class="dish-price">${money(item.price)}</strong>
              <span class="dish-rating">Made fresh</span>
            </div>
            ${row && row.qty > 0 ? `
              <div class="quantity-control">
                <button type="button" data-menu-qty="${item.id}" data-step="-1">−</button>
                <span>${row.qty}</span>
                <button type="button" data-menu-qty="${item.id}" data-step="1">+</button>
              </div>
            ` : `
              <button type="button" class="add-to-cart-btn" data-add="${item.id}">Add +</button>
            `}
          </div>
        </div>
      </article>
    `;
  }).join("");
}
async function bookingDialog(kind) {
  if (kind === "corporate") {
    window.location.href = "corporate.html";
    return;
  }
  const isDine = kind === "dine";
  const isParty = kind === "party" || kind === "gatherings";
  let kicker = "TABLE RESERVATION · BHADAWAR HOTEL";
  let title = "Save your table";
  let guestLabel = "Guest count";
  let defaultGuests = "4";
  let notice = "Table booking advance is ₹50 per person, credited fully towards your final dine-in bill.";
  if (isParty) {
    kicker = "PARTIES & GATHERINGS · BHADAWAR HOTEL";
    title = "Celebrate your special moments";
    guestLabel = "Expected guests (minimum 10)";
    defaultGuests = "25";
    notice = "Your booking advance is credited toward the final event bill. 10–11 guests: ₹50 per person · 12+ guests: ₹30 per person.";
  }
  const paymentConfig = isParty || isDine ? await API.get("payment-config") : null;
  const initialDeposit = isParty ? party_deposit_js(Number(defaultGuests)) : Number(defaultGuests) * 50;
  const today = (/* @__PURE__ */ new Date()).toISOString().split("T")[0];
  openDialog(`
    <div class="dialog-kicker">${kicker}</div>
    <h2>${title} <em>at Bhadawar.</em></h2>
    <p>We’ve been welcoming families and teams since 1963. Share your details below.</p>
    <form id="booking-modal-form">
      <div class="field">
        <label for="bk-name">Your name</label>
        <input id="bk-name" required placeholder="Name" value="${escapeHtml(data.customerName || "")}">
      </div>
      <div class="field">
        <label for="bk-phone">Mobile number</label>
        <input id="bk-phone" type="tel" required placeholder="10-digit mobile number" value="${escapeHtml(data.wallet.phone || "")}">
      </div>
      <div class="form-grid">
        <div class="field">
          <label for="bk-date">Date</label>
          <input id="bk-date" type="date" min="${today}" value="${today}" required>
        </div>
        <div class="field">
          <label for="bk-time">Time</label>
          <select id="bk-time" required>
            <option>12:30 PM</option>
            <option>1:00 PM</option>
            <option>1:30 PM</option>
            <option>2:00 PM</option>
            <option selected>7:30 PM</option>
            <option>8:00 PM</option>
            <option>8:30 PM</option>
            <option>9:00 PM</option>
          </select>
        </div>
        <div class="field full">
          <label for="bk-guests">${guestLabel}</label>
          <input id="bk-guests" type="number" min="${isParty ? 10 : 1}" max="500" value="${defaultGuests}" required>
        </div>
      </div>
      <div class="notice">
        ${notice}
      </div>
      ${isParty || isDine ? `<div class="party-deposit-preview"><span>Booking advance · ${isDine ? "₹50" : "₹50 (10–11) / ₹30 (12+)"} per guest</span><strong id="party-deposit-amount">${money(initialDeposit)}</strong></div>
        ${paymentConfig?.razorpay_enabled ? `<p class="party-payment-note">Secure Razorpay ${paymentConfig.mode === "test" ? "test" : "online"} checkout · Your advance will be credited to the ${isDine ? "final dine-in bill" : "final event bill"}.</p>` : `<p class="party-payment-warning">Online deposits are temporarily unavailable. Configure Razorpay test credentials on the server before taking booking payments.</p>`}` : ""}
      <button class="button button-green" type="submit" style="width:100%;margin-top:10px">
        ${isParty || isDine ? "Pay now to confirm booking" : "Confirm Request"} <span>→</span>
      </button>
    </form>
  `);
  if (isParty || isDine) {
    const guestInput = $("#bk-guests");
    const updateDeposit = () => {
      const minimum = isParty ? 10 : 1;
      const guests = Math.max(minimum, Number(guestInput.value) || minimum);
      $("#party-deposit-amount").textContent = money(isParty ? party_deposit_js(guests) : guests * 50);
    };
    guestInput?.addEventListener("input", updateDeposit);
    const submitButton = $('#booking-modal-form button[type="submit"]');
    if (!paymentConfig?.razorpay_enabled) submitButton.disabled = true;
  }
  $("#booking-modal-form").onsubmit = async (e) => {
    e.preventDefault();
    const guests = $("#bk-guests").value;
    const date = $("#bk-date").value;
    const time = $("#bk-time").value;
    const name = $("#bk-name").value.trim();
    const phone = $("#bk-phone").value.trim();
    if (isParty || isDine) {
      const paymentOrder = await API.post("party-payment/create", {
        booking_type: kind,
        name,
        phone,
        date,
        time,
        guests: parseInt(guests, 10)
      });
      if (!paymentOrder?.success) {
        toast(paymentOrder?.error || "Could not start the booking payment.", true);
        return;
      }
      try {
        await loadRazorpayCheckout();
        const checkout = new window.Razorpay({
          key: paymentOrder.key_id,
          amount: paymentOrder.amount,
          currency: paymentOrder.currency,
          name: "Bhadawar Restaurant",
          description: `${guests} guest ${isDine ? "dine-in table" : "party"} booking advance`,
          order_id: paymentOrder.razorpay_order_id,
          prefill: { name, contact: phone },
          theme: { color: "#b51f2b" },
          handler: async (response) => {
            const verified = await API.post("party-payment/verify", {
              booking_id: paymentOrder.booking_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_order_id: response.razorpay_order_id,
              razorpay_signature: response.razorpay_signature
            });
            if (!verified?.success) {
              toast(verified?.message || verified?.error || "Payment is awaiting verification. Contact the restaurant before retrying.", true);
              return;
            }
            closeDialog();
            openDialog(`<div class="booking-success"><div class="booking-success-mark">✓</div><div class="dialog-kicker">${isDine ? "TABLE BOOKING CONFIRMED" : "PARTY BOOKING CONFIRMED"}</div><h2>We’ll prepare for <em>${escapeHtml(guests)} guests.</em></h2><p>Booking <strong>#${escapeHtml(paymentOrder.booking_id)}</strong> is confirmed after verified payment. Your ${money(paymentOrder.amount / 100)} advance will be credited to the ${isDine ? "final dine-in bill" : "final event bill"}.</p><button class="button button-green" id="party-booking-done">Done →</button></div>`);
            $("#party-booking-done")?.addEventListener("click", closeDialog);
          },
          modal: { ondismiss: () => toast("Payment was not completed. Your booking is not confirmed.", true) }
        });
        checkout.on("payment.failed", (response) => toast(response?.error?.description || "Payment failed. Please try again.", true));
        checkout.open();
      } catch (error) {
        toast(error.message || "Online checkout could not be loaded.", true);
      }
      return;
    }
    const bookingResult = await API.post("bookings", {
      booking_type: kind,
      name,
      phone,
      date,
      time,
      guests: parseInt(guests) || 2,
      notes: `${kicker}`
    });
    if (!bookingResult?.success) {
      toast(bookingResult?.error || "Could not save this booking request.", true);
      return;
    }
    closeDialog();
    toast(`Request confirmed for ${guests} guests on ${date}! Saved to database.`);
  };
}
function party_deposit_js(guests) {
  return guests * (guests >= 12 ? 30 : 50);
}
function loadRazorpayCheckout() {
  if (window.Razorpay) return Promise.resolve();
  return new Promise((resolve, reject) => {
    const script = document.createElement("script");
    script.src = "https://checkout.razorpay.com/v1/checkout.js";
    script.onload = resolve;
    script.onerror = () => reject(new Error("Razorpay checkout could not be loaded. Check your connection and try again."));
    document.head.appendChild(script);
  });
}
function openCheckout() {
  if (!data.cart.length) {
    toast("Your cart is empty. Add a dish before checkout.", true);
    openCartDrawer();
    return;
  }
  const validRows = data.cart.filter((row) => itemById(row.id) && Number.isInteger(Number(row.qty)) && Number(row.qty) > 0);
  if (validRows.length !== data.cart.length) {
    data.cart = validRows;
    save();
  }
  const initialCalc = calcCart();
  if (!data.cart.length || initialCalc.subtotal <= 0 || initialCalc.total <= 0) {
    toast("Your cart total is ₹0. Add a menu item with a price before checkout.", true);
    openCartDrawer();
    return;
  }
  if (!checkoutSignInRequired()) return;
  const savedAddresses = data.addresses || [];
  let checkoutAddress = savedAddresses.find((item) => item.id === data.activeAddressId) || savedAddresses[0] || data.deliveryAddress;
  if (preferredOrderType === "delivery" && checkoutAddress) {
    data.deliveryAddress = { ...data.deliveryAddress, ...checkoutAddress, phone: data.customerProfile?.phone || checkoutAddress.phone || data.wallet.phone || "" };
  }
  let calc = calcCart();
  if (preferredOrderType === "delivery" && (!data.deliveryAddress?.flat || !data.deliveryAddress?.area || data.deliveryAddress?.latitude == null || data.deliveryAddress?.longitude == null)) {
    toast("Pin your delivery location so we can confirm the distance and delivery fee.", true);
    openAddressDrawer();
    return;
  }
  if (preferredOrderType === "delivery" && calc.outsideDeliveryRange && savedAddresses.length < 2) {
    toast("Delivery is available only within 10 km of the restaurant.", true);
    openAddressDrawer();
    return;
  }
  const usePoints = $("#cart-use-points")?.checked && data.wallet.balance > 0;
  let pointsDiscount = calculateWalletRedemption(calc.total, data.wallet.balance, data.settings?.maxRedeemPercent ?? 50, usePoints);
  let finalAmount = calc.total - pointsDiscount;
  const addressText = (address) => [address.flat, address.area, address.landmark].filter(Boolean).join(", ");
  let orderLocation = preferredOrderType === "delivery" ? addressText(data.deliveryAddress) : preferredOrderType === "takeaway" ? "Pickup at Bhadawar Hotel & Foods, Agra" : "Dine-in at Bhadawar Hotel & Foods, Agra";
  const orderModeLabel = preferredOrderType === "delivery" ? "Delivering to" : preferredOrderType === "takeaway" ? "Pickup location" : "Dining at";
  const checkoutIntro = preferredOrderType === "delivery" ? "Confirm your delivery address and choose a payment method." : preferredOrderType === "takeaway" ? "Your order will be ready for pickup at Bhadawar. Choose a payment method." : "Enjoy your meal at Bhadawar. Choose a payment method.";
  const addressOptions = preferredOrderType === "delivery" && savedAddresses.length > 1 ? `<div class="field checkout-field"><label for="checkout-address-select">Deliver to</label><select id="checkout-address-select">${savedAddresses.map((item) => `<option value="${escapeHtml(item.id)}" ${item.id === (data.activeAddressId || savedAddresses[0].id) ? "selected" : ""}>${escapeHtml(item.tag || "Other")} · ${escapeHtml(item.flat)}, ${escapeHtml(item.area)}</option>`).join("")}</select><a href="account.html" class="checkout-manage-addresses">Manage saved addresses</a></div>` : "";
  openDialog(`
    <div class="checkout-dialog">
      <div class="dialog-kicker">BHADAWAR · ORDER REVIEW</div>
      <h2>Review your <em>order.</em></h2>
      <p class="checkout-intro">${checkoutIntro}</p>
      <div class="checkout-order-summary"><span>${data.cart.reduce((sum, item) => sum + Number(item.qty || 0), 0)} items in your order</span><strong>${money(calc.subtotal)}</strong></div>
      ${publicPreviewMode ? '<div class="checkout-preview-notice">Preview only · Orders are for testing and will not be prepared or charged. Please do not use real contact details.</div>' : '<div class="checkout-preview-notice">Payment options are shown as a preview. No card or bank information is collected here.</div>'}
      <form id="final-checkout-form" class="checkout-form">
        ${addressOptions}
        <div class="field checkout-field"><label>${orderModeLabel}</label><input id="checkout-address-display" readonly value="${escapeHtml(orderLocation || "Add your delivery address")}" /></div>
        <div class="field checkout-field"><label for="checkout-customer-name">Your name</label><input id="checkout-customer-name" name="customer_name" autocomplete="name" required maxlength="120" readonly value="${escapeHtml(customerSession?.name || "")}" /></div>
        <div class="field checkout-field"><label for="checkout-customer-phone">Contact phone</label><input id="checkout-customer-phone" name="customer_phone" type="tel" autocomplete="tel" required readonly value="${escapeHtml(customerSession?.phone || "")}" /></div>
        ${preferredOrderType === "delivery" ? '<label class="field checkout-field">Delivery instructions<textarea id="checkout-delivery-instructions" maxlength="500" placeholder="Gate or floor, call before arrival, leave at reception…"></textarea><small>Keep it short and helpful for the rider.</small></label>' : ""}
        <fieldset class="checkout-payment"><legend>Choose how you will pay</legend>
          <label class="checkout-payment-option"><input type="radio" name="checkout-pay" value="upi" checked><span class="checkout-pay-icon">↗</span><span><strong>UPI</strong><small>Opens a sample payment screen · no charge</small></span></label>
          <label class="checkout-payment-option"><input type="radio" name="checkout-pay" value="card"><span class="checkout-pay-icon">▤</span><span><strong>Card / NetBanking</strong><small>Opens a sample payment screen · no charge</small></span></label>
          <label class="checkout-payment-option"><input type="radio" name="checkout-pay" value="cod"><span class="checkout-pay-icon">₹</span><span><strong>${preferredOrderType === "delivery" ? "Pay at delivery" : "Pay at restaurant"}</strong><small>${preferredOrderType === "delivery" ? "Rider can accept cash or UPI" : "Pay when you collect or dine in"}</small></span></label>
        </fieldset>
        <div class="checkout-total-row"><span>Total payable</span><strong id="checkout-total">${money(finalAmount)}</strong></div>
        <button class="button button-green checkout-place-order" type="submit" ${calc.outsideDeliveryRange ? "disabled" : ""}>${calc.outsideDeliveryRange ? "Outside delivery range" : "Continue to order review →"}</button>
      </form>
    </div>
  `, true);
  const selectSavedAddress = (id) => {
    const selected = savedAddresses.find((item) => item.id === id);
    if (!selected) return;
    checkoutAddress = selected;
    data.activeAddressId = selected.id;
    data.deliveryAddress = { ...data.deliveryAddress, ...selected, phone: data.customerProfile?.phone || selected.phone || data.wallet.phone || "" };
    calc = calcCart();
    pointsDiscount = calculateWalletRedemption(calc.total, data.wallet.balance, data.settings?.maxRedeemPercent ?? 50, usePoints);
    finalAmount = calc.total - pointsDiscount;
    orderLocation = addressText(data.deliveryAddress);
    $("#checkout-address-display").value = orderLocation;
    $("#checkout-total").textContent = money(finalAmount);
    const submit = $('#final-checkout-form button[type="submit"]');
    submit.disabled = calc.outsideDeliveryRange;
    submit.textContent = calc.outsideDeliveryRange ? "Outside delivery range" : "Continue to order review →";
  };
  $("#checkout-address-select")?.addEventListener("change", (event) => selectSavedAddress(event.target.value));
  let checkoutInstructions = "";
  let checkoutCustomerName = "";
  let checkoutCustomerPhone = "";
  const submitOrder = async (payMethod) => {
    const submitButton = $('#final-checkout-form button[type="submit"]');
    if (!customerSession?.phone) {
      toast("Sign in before placing your order.", true);
      closeDialog();
      checkoutSignInRequired();
      return;
    }
    if (!data.cart.length) {
      toast("Your cart is empty. Add a dish before checkout.", true);
      closeDialog();
      openCartDrawer();
      return;
    }
    if (calc.subtotal <= 0 || finalAmount <= 0) {
      toast("Your payable total must be greater than ₹0.", true);
      return;
    }
    if (preferredOrderType === "delivery" && calc.outsideDeliveryRange) {
      toast("This saved address is outside the delivery range.", true);
      return;
    }
    submitButton && (submitButton.disabled = true);
    const orderPayload = {
      customer_name: checkoutCustomerName,
      customer_phone: checkoutCustomerPhone,
      delivery_address: orderLocation,
      delivery_latitude: preferredOrderType === "delivery" ? data.deliveryAddress.latitude : null,
      delivery_longitude: preferredOrderType === "delivery" ? data.deliveryAddress.longitude : null,
      delivery_instructions: checkoutInstructions,
      order_type: preferredOrderType,
      payment_method: payMethod,
      subtotal: calc.subtotal,
      delivery_fee: calc.delivery,
      tax: calc.tax,
      discount: calc.corporateDiscount || 0,
      points_used: pointsDiscount,
      total_amount: finalAmount,
      items: data.cart.map((r) => ({ id: r.id, qty: r.qty, name: itemById(r.id)?.name || r.id, price: itemById(r.id)?.price || 0 }))
    };
    const orderResult = await API.post("orders", orderPayload);
    if (!orderResult?.success) {
      toast(orderResult?.error || "The order could not be saved. Please try again.", true);
      submitButton && (submitButton.disabled = false);
      return;
    }
    const orderId = orderResult.order_id;
    data.orders = data.orders || [];
    data.orders.unshift({
      ...orderPayload,
      id: orderId,
      items: orderResult.items || orderPayload.items,
      subtotal: orderResult.subtotal,
      delivery_fee: orderResult.delivery_fee,
      tax: orderResult.tax,
      discount: orderResult.discount,
      points_used: orderResult.points_used,
      total_amount: orderResult.total_amount,
      status: "received"
    });
    if (orderResult.wallet_balance != null && Number.isFinite(Number(orderResult.wallet_balance))) {
      data.wallet.balance = Number(orderResult.wallet_balance);
      data.wallet.entries = data.wallet.entries || [];
      data.wallet.entries.unshift({
        type: "debit",
        amount: orderResult.points_used,
        label: `Redeemed on Order #${orderId}`,
        date: (/* @__PURE__ */ new Date()).toISOString()
      });
    }
    data.customerName = checkoutCustomerName;
    data.deliveryAddress.phone = checkoutCustomerPhone;
    data.customerProfile = { ...customerSession };
    data.wallet.phone = customerSession.phone;
    save();
    closeDialog();
    closeCartDrawer();
    data.cart = [];
    save();
    openDialog(`
      <div class="order-confirmation">
        <div style="font-size:54px;color:#178345;margin-bottom:8px">✓</div>
        <div class="dialog-kicker">PREVIEW ORDER RECEIVED</div>
        <h2>Thank you! <em>Your order is in the kitchen queue.</em></h2>
        <p>Order <b>#${orderId}</b> has been received. Order total: <b>${money(orderResult.total_amount)}</b>.</p>
        <div class="checkout-preview-notice">This is a preview order. No payment is collected and no real food delivery or preparation is triggered.</div>
        <button class="button button-green" id="order-done-btn" style="margin-top:16px">Done →</button>
      </div>
    `);
    $("#order-done-btn").onclick = closeDialog;
  };
  $("#final-checkout-form").onsubmit = async (event) => {
    event.preventDefault();
    checkoutInstructions = $("#checkout-delivery-instructions")?.value.trim() || "";
    const payMethod = $('input[name="checkout-pay"]:checked')?.value || "upi";
    if (preferredOrderType === "delivery" && $("#checkout-address-select")?.value) selectSavedAddress($("#checkout-address-select").value);
    if (!customerSession?.phone) {
      toast("Sign in before placing your order.", true);
      closeDialog();
      checkoutSignInRequired();
      return;
    }
    checkoutCustomerName = customerSession.name || "";
    checkoutCustomerPhone = customerSession.phone || "";
    if (!checkoutCustomerName || checkoutCustomerPhone.replace(/\D/g, "").length < 10) {
      toast("Your account details are incomplete. Update your profile and try again.", true);
      return;
    }
    if (calc.subtotal <= 0 || finalAmount <= 0) {
      toast("Your payable total must be greater than ₹0.", true);
      return;
    }
    if (payMethod === "cod") {
      await submitOrder(payMethod);
      return;
    }
    const gatewayTitle = payMethod === "upi" ? "UPI payment" : "Card / NetBanking";
    openDialog(`<div class="gateway-preview"><div class="gateway-brand"><span class="gateway-brand-mark">B</span><span><strong>BHADAWAR</strong><small>SECURE PAYMENT PREVIEW</small></span><b>TEST</b></div><div class="gateway-preview-hero"><span>DEMO PAYMENT FLOW</span><h2>${gatewayTitle}</h2><p>This is a visual preview of the payment step. It will not open a bank app or move money.</p></div><div class="gateway-preview-amount"><span>Amount to pay</span><strong>${money(finalAmount)}</strong></div><div class="gateway-preview-method">${payMethod === "upi" ? "UPI · Google Pay · PhonePe · Paytm" : "Cards · RuPay · Visa · NetBanking"}</div><button type="button" id="demo-payment-complete" class="button button-green checkout-place-order">Simulate payment and continue</button><button type="button" id="demo-payment-back" class="gateway-back-button">Back to order details</button><p class="gateway-preview-footnote">No payment is collected. Live payment gateway setup is still required before launch.</p></div>`, true);
    $("#demo-payment-complete").onclick = () => submitOrder(payMethod);
    $("#demo-payment-back").onclick = openCheckout;
  };
}
function openTrackOrderDialog() {
  openDialog(`
    <div class="dialog-kicker">ORDER SUPPORT · BHADAWAR</div>
    <h2>Track your <em>order.</em></h2>
    <p>Enter the order number from your confirmation and the phone number used at checkout.</p>
    <form id="track-order-form">
      <div class="field"><label for="track-order-id">Order number</label><input id="track-order-id" required placeholder="For example, BH123456"></div>
      <div class="field"><label for="track-order-phone">Checkout phone number</label><input id="track-order-phone" type="tel" inputmode="tel" required placeholder="10-digit phone number" value="${escapeHtml(data.deliveryAddress.phone || data.wallet.phone || "")}"></div>
      <div id="track-order-result" class="track-order-result" role="status" hidden></div>
      <button class="button button-green" type="submit" style="width:100%">Find my order →</button>
    </form>
    <p class="help-contact-note">Need help? Call <a href="tel:+918273659922">+91 82736 59922</a>.</p>
  `);
  $("#track-order-form")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const button = $('#track-order-form button[type="submit"]');
    const resultBox = $("#track-order-result");
    button.disabled = true;
    button.textContent = "Looking up…";
    resultBox.hidden = true;
    const result = await API.post("orders/track", {
      order_id: $("#track-order-id").value.trim(),
      phone: $("#track-order-phone").value.trim()
    });
    button.disabled = false;
    button.textContent = "Find my order →";
    resultBox.hidden = false;
    if (!result?.success) {
      resultBox.classList.add("is-error");
      resultBox.textContent = result?.error || "Order tracking is unavailable right now. Please try again.";
      return;
    }
    const order = result.order;
    const status = String(order.status || "received").replaceAll("_", " ");
    resultBox.classList.remove("is-error");
    resultBox.innerHTML = `<strong>Order #${escapeHtml(order.id)}</strong><span>Status: ${escapeHtml(status)}</span><span>Order total: ${money(order.total_amount)}</span>`;
  });
}
function openHelpDialog(topic) {
  const faqItems = [
    ["How do I place an order?", "Choose Delivery, Takeaway, or Dine-in, add dishes to your cart, and continue to checkout. Review your items and contact details before confirming."],
    ["Can I change or cancel my order?", "Call Bhadawar as soon as possible at +91 82736 59922. Changes depend on whether the kitchen has started preparing your order."],
    ["How can I track my order?", "Open Track order in the Help section and enter the order number from your confirmation along with the phone number used at checkout."],
    ["What are the restaurant hours?", "Bhadawar is open daily from 11:00 AM to 12:00 AM. Delivery availability and estimated time can vary by location and demand."],
    ["How do I book a table?", "Choose Dine-in, tap “Save your table”, and enter your booking details. The booking screen shows the advance amount before payment."],
    ["Which payment methods can I use?", "Available payment methods are shown at checkout. For dine-in or takeaway, follow the payment choices shown for your selected order mode."],
    ["How do Bhadawar reward points work?", "Points are credited under the reward rules shown on the website. An approved food story earns 1 point; eligible completed orders above ₹599 can earn 2 extra points when linked to approved feedback."],
    ["Can I return food or get a refund?", "Please call or WhatsApp Bhadawar with your order or booking number. The team will review the order and payment status; refund handling depends on the situation."],
    ["How do I book party or corporate catering?", "Use the Gatherings option for a party booking. Corporate catering is available through the separate staff portal. Call +91 82736 59922 if you need help."]
  ];
  const content = {
    help: {
      kicker: "HELP CENTRE",
      title: "Frequently asked questions",
      body: `<div class="help-answer-list" id="help-answer-list">${faqItems.map(([question, answer], index) => `
        <article class="faq-item">
          <h3><button type="button" class="faq-question" aria-expanded="false" aria-controls="faq-answer-${index}" id="faq-question-${index}"><span>${question}</span><span class="faq-chevron" aria-hidden="true">⌄</span></button></h3>
          <div class="faq-answer" id="faq-answer-${index}" role="region" aria-labelledby="faq-question-${index}" hidden><p>${answer}</p></div>
        </article>`).join("")}
      </div>`
    },
    returns: {
      kicker: "ORDER SUPPORT",
      title: "Returns & refunds",
      body: `<p>Food orders and booking advances can have different cancellation and refund handling. Contact Bhadawar with your order or booking number so the team can check its preparation and payment status.</p><p>For a verified booking advance, any refund due is reviewed by staff; the preview does not send automatic refunds.</p><p><a class="help-contact-link" href="tel:+918273659922">Call +91 82736 59922</a> · <a class="help-contact-link" href="https://wa.me/918273659922" target="_blank" rel="noopener">WhatsApp Bhadawar</a></p>`
    },
    privacy: {
      kicker: "BHADAWAR GUEST INFORMATION",
      title: "Privacy policy",
      body: `<p>The website uses the details you provide, such as your name, phone number, delivery address, order, and booking details, to handle restaurant services and support.</p><p>Food stories are kept private while pending and shown publicly only after admin approval. Order tracking returns limited status information only when the order number and matching checkout phone are provided.</p><p>This is a local preview. Confirm the final retention and privacy terms before public launch.</p>`
    },
    terms: {
      kicker: "BHADAWAR GUEST INFORMATION",
      title: "Terms & conditions",
      body: `<p>Menu prices, item availability, fees, and preparation times may be confirmed by the restaurant before an order is accepted. An order or booking request is subject to Bhadawar confirmation.</p><p>Reward points are added only under the rules shown on the website.</p><p>This local preview is for demonstration. Confirm final operating, cancellation, and payment terms before public launch.</p>`
    }
  }[topic];
  if (!content) return;
  openDialog(`<div class="dialog-kicker">${content.kicker}</div><h2>${content.title}</h2><div class="help-dialog-copy">${content.body}</div><button type="button" class="button button-outline" id="help-dialog-done" style="margin-top:18px">Done</button>`);
  if (topic === "help") {
    $("#help-answer-list")?.addEventListener("click", (event) => {
      const question = event.target.closest(".faq-question");
      if (!question) return;
      const answer = document.getElementById(question.getAttribute("aria-controls"));
      const willOpen = question.getAttribute("aria-expanded") !== "true";
      question.setAttribute("aria-expanded", String(willOpen));
      if (answer) answer.hidden = !willOpen;
    });
  }
  $("#help-dialog-done")?.addEventListener("click", closeDialog);
}
function initEvents() {
  $$(".mode-tab").forEach((button) => {
    button.addEventListener("click", () => {
      const mode = button.dataset.orderMode;
      if (!["delivery", "takeaway", "dine_in"].includes(mode)) return;
      preferredOrderType = mode;
      data.settings.orderMode = mode;
      save();
      updateOrderModeUI();
      toast(mode === "delivery" ? "Delivery selected" : mode === "takeaway" ? "Takeaway selected" : "Dine-in selected");
    });
  });
  $("#save-table-shortcut")?.addEventListener("click", () => bookingDialog("dine"));
  $$("[data-drawer-track]").forEach((button) => button.addEventListener("click", openTrackOrderDialog));
  $$("[data-learn-more]").forEach((button) => button.addEventListener("click", () => openHelpDialog(button.dataset.learnMore)));
  $("#open-cart")?.addEventListener("click", openCartDrawer);
  $("#mobile-open-cart")?.addEventListener("click", openCartDrawer);
  $("#cart-drawer-close")?.addEventListener("click", closeCartDrawer);
  $("#top-location-btn")?.addEventListener("click", openAddressDrawer);
  $("#hero-change-addr")?.addEventListener("click", openAddressDrawer);
  $("#address-drawer-close")?.addEventListener("click", closeAddressDrawer);
  $("#drawer-backdrop")?.addEventListener("click", () => {
    closeCartDrawer();
    closeAddressDrawer();
  });
  $("#drawer-proceed-btn")?.addEventListener("click", () => {
    if (!data.cart.length) {
      toast("Your cart is empty", true);
      return;
    }
    closeCartDrawer();
    openCheckout();
  });
  $("#cart-use-points")?.addEventListener("change", renderDrawerCart);
  $("#coupon-row")?.addEventListener("click", () => {
    if (!data.cart.length) {
      toast("Add a dish before checking available offers.", true);
      return;
    }
    openDialog('<div class="dialog-kicker">BHADAWAR OFFERS</div><h2>Offers at <em>checkout.</em></h2><p>Wallet points can be applied to this preview order. The TABLE100 offer is for dine-in bills of ₹999 or more at the restaurant and is not a delivery checkout coupon.</p><div class="checkout-preview-notice">No coupon has been applied to your cart. Any offer or wallet discount is shown before you place an order.</div><button type="button" class="button button-green" id="offer-dialog-done">Back to cart</button>');
    $("#offer-dialog-done").onclick = closeDialog;
  });
  $("#drawer-cart-items")?.addEventListener("click", (e) => {
    const qtyBtn = e.target.closest("[data-drawer-qty]");
    if (qtyBtn) {
      changeQuantity(qtyBtn.dataset.drawerQty, Number(qtyBtn.dataset.step));
      return;
    }
    const delBtn = e.target.closest("[data-drawer-delete]");
    if (delBtn) {
      deleteCartItem(delBtn.dataset.drawerDelete);
    }
  });
  $("#bestsellers-featured-grid")?.addEventListener("click", (e) => {
    const addBtn = e.target.closest("[data-add]");
    if (addBtn) {
      addToCart(addBtn.dataset.add);
      return;
    }
    const qtyBtn = e.target.closest("[data-featured-qty]");
    if (qtyBtn) {
      changeQuantity(qtyBtn.dataset.featuredQty, Number(qtyBtn.dataset.step));
    }
  });
  $("#hero-featured-order-slot")?.addEventListener("click", (e) => {
    const addBtn = e.target.closest("[data-add]");
    if (addBtn) {
      addToCart(addBtn.dataset.add);
      return;
    }
    const qtyBtn = e.target.closest("[data-featured-qty]");
    if (qtyBtn) changeQuantity(qtyBtn.dataset.featuredQty, Number(qtyBtn.dataset.step));
  });
  $("#menu-grid")?.addEventListener("click", (e) => {
    const addBtn = e.target.closest("[data-add]");
    if (addBtn) {
      addToCart(addBtn.dataset.add);
      return;
    }
    const qtyBtn = e.target.closest("[data-menu-qty]");
    if (qtyBtn) {
      changeQuantity(qtyBtn.dataset.menuQty, Number(qtyBtn.dataset.step));
      renderFullMenu();
    }
    const favBtn = e.target.closest("[data-fav]");
    if (favBtn) {
      const id = favBtn.dataset.fav;
      if (data.favorites.includes(id)) {
        data.favorites = data.favorites.filter((x) => x !== id);
        favBtn.classList.remove("active");
        favBtn.setAttribute("aria-pressed", "false");
        favBtn.innerHTML = icon("heart");
      } else {
        data.favorites.push(id);
        favBtn.classList.add("active");
        favBtn.setAttribute("aria-pressed", "true");
        favBtn.innerHTML = icon("heart");
      }
      save();
    }
  });
  $$(".category-bubble").forEach((btn) => {
    btn.addEventListener("click", () => {
      const cat = btn.dataset.category;
      activeCategory = cat;
      $$(".category-bubble").forEach((b) => b.classList.toggle("active", b === btn));
      const fullCont = $("#full-menu-container");
      if (cat === "popular") {
        if (fullCont) fullCont.hidden = true;
      } else {
        if (fullCont) fullCont.hidden = false;
        renderFullMenu();
        fullCont.scrollIntoView({ behavior: "smooth" });
      }
    });
  });
  $("#view-full-menu-btn")?.addEventListener("click", () => {
    activeCategory = "all";
    $$(".category-bubble").forEach((b) => b.classList.toggle("active", b.dataset.category === "all"));
    const fullCont = $("#full-menu-container");
    if (fullCont) fullCont.hidden = false;
    renderFullMenu();
    fullCont.scrollIntoView({ behavior: "smooth" });
  });
  $("#hero-search-form")?.addEventListener("submit", (e) => {
    e.preventDefault();
    const query = $("#hero-search").value.trim();
    if ($("#menu-search")) $("#menu-search").value = query;
    activeCategory = "all";
    $$(".category-bubble").forEach((b) => b.classList.toggle("active", b.dataset.category === "all"));
    const fullCont = $("#full-menu-container");
    if (fullCont) fullCont.hidden = false;
    renderFullMenu();
    fullCont.scrollIntoView({ behavior: "smooth" });
  });
  $("#header-search-btn")?.addEventListener("click", () => {
    const searchForm = $("#hero-search-form");
    const searchInput = $("#hero-search");
    searchForm?.scrollIntoView({ behavior: "smooth", block: "center" });
    window.setTimeout(() => searchInput?.focus({ preventScroll: true }), 350);
  });
  $("#menu-search")?.addEventListener("input", renderFullMenu);
  $("#veg-only")?.addEventListener("change", renderFullMenu);
  $("#spice-filter")?.addEventListener("change", renderFullMenu);
  $("#address-edit-form")?.addEventListener("submit", (e) => {
    e.preventDefault();
    const flat = $("#addr-flat").value.trim();
    const area = $("#addr-area").value.trim();
    const landmark = $("#addr-landmark").value.trim();
    const phone = $("#addr-phone").value.trim();
    const deliveryDistanceBand = $("#addr-distance-band").value;
    const tag = $('input[name="addr-tag"]:checked')?.value || "Home";
    data.deliveryAddress = {
      ...data.deliveryAddress,
      flat,
      area,
      landmark,
      phone,
      tag,
      deliveryDistanceBand,
      summary: `Agra, ${area}, Agra`
    };
    if (data.customerProfile?.phone) {
      const addressId = data.activeAddressId || `address-${Date.now()}`;
      const savedAddress = { ...data.deliveryAddress, id: addressId };
      data.addresses = data.addresses || [];
      const savedIndex = data.addresses.findIndex((item) => item.id === addressId);
      if (savedIndex >= 0) data.addresses[savedIndex] = savedAddress;
      else data.addresses.push(savedAddress);
      data.activeAddressId = addressId;
    }
    save();
    $("#hero-address-display").textContent = data.deliveryAddress.summary;
    $("#top-loc-name").textContent = `Agra, ${area}`;
    updateOrderModeUI();
    closeAddressDrawer();
    toast("Delivery address updated");
  });
  $("#use-gps-btn")?.addEventListener("click", requestCurrentDeliveryLocation);
  $$(".favorite-heart-btn").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      btn.classList.toggle("active");
      btn.setAttribute("aria-pressed", String(btn.classList.contains("active")));
      btn.innerHTML = icon("heart");
      toast(btn.classList.contains("active") ? "Added to favorites" : "Removed from favorites");
    });
  });
  $$(".wallet-open").forEach((btn) => btn.addEventListener("click", openWalletDialog));
  $$("[data-booking]").forEach((btn) => {
    btn.addEventListener("click", () => bookingDialog(btn.dataset.booking));
  });
  $("#write-review")?.addEventListener("click", () => {
    openDialog(`
      <div class="dialog-kicker">GUEST REVIEW · BHADAWAR HOTEL</div>
      <h2>Share your <em>experience.</em></h2>
      <p>Tell us how you enjoyed your food from Bhadawar.</p>
      <form id="guest-review-form">
        <div class="field">
          <label>Your Name</label>
        <input id="rev-name" required maxlength="60" placeholder="Name or nickname" value="${escapeHtml(data.customerName || "")}">
        </div>
        <div class="field">
          <label>Rating</label>
          <select id="rev-stars">
            <option value="5">★★★★★ — 5 Stars (Excellent)</option>
            <option value="4">★★★★☆ — 4 Stars (Very Good)</option>
            <option value="3">★★★☆☆ — 3 Stars (Good)</option>
          </select>
        </div>
        <div class="field">
          <label>Review</label>
          <textarea id="rev-body" required minlength="10" maxlength="1000" placeholder="What dishes did you love most?"></textarea>
        </div>
        <p class="account-preview-note">Your feedback is saved for the restaurant team and is not posted publicly in this preview.</p>
        <button class="button button-green" type="submit" style="width:100%;margin-top:10px">
          Submit Review <span>→</span>
        </button>
      </form>
    `);
    $("#guest-review-form").onsubmit = async (e) => {
      e.preventDefault();
      const button = e.currentTarget.querySelector('button[type="submit"]');
      button.disabled = true;
      const name = $("#rev-name").value.trim();
      const rating = Number($("#rev-stars").value);
      const text = $("#rev-body").value.trim();
      const result = await API.post("reviews", { name, rating, text });
      if (!result?.success) {
        button.disabled = false;
        toast(result?.error || "Could not save your feedback. Please try again.", true);
        return;
      }
      data.customerName = name;
      save();
      closeDialog();
      toast("Thank you. Your feedback was saved for the restaurant team.");
    };
  });
  $("#staff-portals")?.addEventListener("click", () => {
    window.location.href = "team.html";
  });
  $("#dialog-close")?.addEventListener("click", closeDialog);
  $("#overlay")?.addEventListener("click", (e) => {
    if (e.target === $("#overlay")) closeDialog();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      closeDialog();
      closeCartDrawer();
      closeAddressDrawer();
    }
  });
  const menuToggle = $("#menu-toggle");
  const mainNav = $("#main-nav");
  const navScrim = $("#nav-scrim");
  const setMobileMenuOpen = (open) => {
    mainNav?.classList.toggle("open", open);
    navScrim?.classList.toggle("open", open);
    menuToggle?.setAttribute("aria-expanded", String(open));
    menuToggle?.setAttribute("aria-label", open ? "Close mobile menu" : "Open mobile menu");
  };
  menuToggle?.addEventListener("click", () => {
    setMobileMenuOpen(!mainNav?.classList.contains("open"));
  });
  navScrim?.addEventListener("click", () => setMobileMenuOpen(false));
  mainNav?.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => setMobileMenuOpen(false)));
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") setMobileMenuOpen(false);
  });
  const chatLaunch = $("#chat-launch");
  const chatPanel = $("#chat-panel");
  chatLaunch?.addEventListener("click", () => {
    chatPanel.hidden = !chatPanel.hidden;
    chatLaunch.setAttribute("aria-expanded", String(!chatPanel.hidden));
  });
  $("#chat-close")?.addEventListener("click", () => {
    chatPanel.hidden = true;
    chatLaunch?.setAttribute("aria-expanded", "false");
  });
  $("#chat-form")?.addEventListener("submit", (e) => {
    e.preventDefault();
    const input = $("#chat-input");
    const msg = input.value.trim();
    if (!msg) return;
    const log = $("#chat-log");
    log.innerHTML += `<div class="chat-bubble customer">${escapeHtml(msg)}</div>`;
    input.value = "";
    setTimeout(() => {
      log.innerHTML += `<div class="chat-bubble assistant">Thank you for asking! For orders, table reservations, or party catering at Bhadawar Hotel, you can also call our team at +91 82736 59922.</div>`;
      log.scrollTop = log.scrollHeight;
    }, 400);
  });
  $$("[data-chat-question]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const q = btn.dataset.chatQuestion;
      const log = $("#chat-log");
      log.innerHTML += `<div class="chat-bubble customer">${escapeHtml(q)}</div>`;
      setTimeout(() => {
        let ans = "Our team is ready to assist you.";
        if (q.includes("order")) ans = 'Browse bestsellers or category bubbles above, tap "Add +", and open your cart drawer on top right to checkout.';
        else if (q.includes("wallet")) ans = "Bhadawar Points give ₹1 discount for every point. You have 100 points ready to redeem!";
        else if (q.includes("dine-in")) ans = 'Tap "Save your table" above to reserve a dine-in spot at our family restaurant in Mantola, Agra.';
        else if (q.includes("payment")) ans = "We support Razorpay Online (UPI, Cards, NetBanking) and Cash on Delivery.";
        log.innerHTML += `<div class="chat-bubble assistant">${ans}</div>`;
        log.scrollTop = log.scrollHeight;
      }, 400);
    });
  });
}
let teamStaff = null;
let teamBookings = [];
let teamCorporateMenu = [];
let teamRiderAvailability = { is_available: false, available_riders: 0, active_assignments: 0, riders: [] };
let teamOrderSummary = {};
let teamRiderHeartbeat = null;
async function renderTeamPage() {
  if (teamRiderHeartbeat) clearTimeout(teamRiderHeartbeat);
  teamRiderHeartbeat = null;
  const container = $("#team-content");
  if (!container) return;
  document.body.classList.remove("team-dashboard-active");
  const auth = await API.get("auth/me");
  teamStaff = auth?.staff || null;
  if (teamStaff?.role === "corporate") {
    window.location.replace("corporate.html");
    return;
  }
  if (!teamStaff) {
    renderStaffLogin(container);
    return;
  }
  document.body.classList.add("team-dashboard-active");
  const [ordersResult, storiesResult] = await Promise.all([
    API.get("orders"),
    API.get("food-stories")
  ]);
  data.orders = ordersResult?.orders || [];
  teamOrderSummary = ordersResult?.summary || {};
  teamRiderAvailability = teamStaff.role === "delivery" || teamStaff.role === "admin" ? await API.get("rider/availability") || teamRiderAvailability : { is_available: false, available_riders: 0, active_assignments: 0, riders: [] };
  const approvedStories = storiesResult?.stories || [];
  data.foodStories = approvedStories.map((s) => ({ ...s, date: s.created_at, photo: s.photo ? mediaUrl(s.photo) : "", mediaType: s.media_type || "image" }));
  if (teamStaff.role === "admin") {
    const [pendingResult, bookingsResult, corporateResult] = await Promise.all([
      API.get("food-stories?status=pending"),
      API.get("bookings"),
      API.get("corporate-menu")
    ]);
    const pending = (pendingResult?.stories || []).map((s) => ({ ...s, date: s.created_at, photo: s.photo ? mediaUrl(s.photo) : "", mediaType: s.media_type || "image" }));
    data.foodStories = [...pending, ...data.foodStories];
    teamBookings = bookingsResult?.bookings || [];
    teamCorporateMenu = corporateResult?.items || [];
  }
  renderStaffDashboard(container);
  if (teamStaff.role === "delivery" && teamRiderAvailability.is_available) {
    teamRiderHeartbeat = setTimeout(async () => {
      const refreshed = await API.post("rider/availability", { is_available: true });
      if (refreshed?.success) await renderTeamPage();
      else {
        teamRiderAvailability.is_available = false;
        await renderTeamPage();
      }
    }, 3e4);
  }
}
function renderStaffLogin(container, error = "") {
  container.innerHTML = `
    <section class="team-login-card">
      <div class="team-login-mark"><img src="assets/bhadawar-mark.png" alt="Bhadawar Hotel logo"></div>
      <div class="eyebrow eyebrow-dark"><span></span> LOCAL PREVIEW ACCESS</div>
      <h2>Staff <em>sign in.</em></h2>
      <p>Use your configured account to open the right Bhadawar dashboard.</p>
      ${error ? `<div class="team-login-error" role="alert">${escapeHtml(error)}</div>` : ""}
      <form id="team-login-form">
        <label class="field"><span>Staff role</span><select id="team-login-role" required><option value="admin">Admin</option><option value="kitchen">Kitchen</option><option value="delivery">Delivery</option></select></label>
        <label class="field"><span>Username</span><input id="team-login-user" autocomplete="username" required></label>
        <label class="field"><span>Password</span><input id="team-login-password" type="password" autocomplete="current-password" required></label>
        <button class="button button-green" type="submit">Sign in to staff portal →</button>
      </form>
      <div class="team-demo-note">Local preview only · The matching demo account is filled from this server’s configuration. Change the role to switch accounts.</div>
    </section>`;
  const fillConfiguredPreviewAccount = async () => {
    const localHost = ["localhost", "127.0.0.1", "::1"].includes(window.location.hostname);
    if (publicPreviewMode || !localHost) return;
    const role = $("#team-login-role")?.value;
    if (!role) return;
    const account = await API.get("auth/preview-credentials?role=" + encodeURIComponent(role));
    const localDefaults = {
      admin: { username: "admin", password: "BhadawarAdminDemo!" },
      kitchen: { username: "kitchen", password: "BhadawarKitchenDemo!" },
      delivery: { username: "delivery", password: "BhadawarDeliveryDemo!" }
    };
    const credentials = account?.success ? account : localDefaults[role];
    if (!credentials) return;
    const username = $("#team-login-user");
    const password = $("#team-login-password");
    if (username && password) {
      username.value = credentials.username || "";
      password.value = credentials.password || "";
    }
  };
  $("#team-login-role")?.addEventListener("change", fillConfiguredPreviewAccount);
  fillConfiguredPreviewAccount();
  $("#team-login-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const button = e.currentTarget.querySelector('button[type="submit"]');
    button.disabled = true;
    const result = await API.post("auth/login", {
      role: $("#team-login-role").value,
      username: $("#team-login-user").value.trim(),
      password: $("#team-login-password").value
    });
    if (!result?.success) {
      renderStaffLogin(container, result?.error || "Could not sign in.");
      return;
    }
    await renderTeamPage();
  });
}
function renderStaffDashboard(container) {
  const role = teamStaff.role;
  const tabs = role === "admin" ? [["overview", "Overview"], ["orders", `Completed & cancelled (${data.orders.length})`], ["stories", `Story review (${data.foodStories.filter((s) => s.status === "pending").length})`], ["bookings", `Gatherings (${teamBookings.length})`], ["corporate", "Corporate menu"]] : role === "kitchen" ? [["orders", `Kitchen orders (${data.orders.length})`]] : [["orders", `Dispatch queue (${data.orders.length})`]];
  const initial = new URLSearchParams(location.search).get("view");
  const active = tabs.some(([key]) => key === initial) ? initial : tabs[0][0];
  container.innerHTML = `
    <section class="team-portal-card team-role-${escapeHtml(role)}">
      <header class="team-dashboard-head"><div><div class="eyebrow eyebrow-dark"><span></span> LOCAL PREVIEW · ${escapeHtml(role.toUpperCase())}</div><h2>${role === "admin" ? "Admin dashboard" : role === "kitchen" ? "Kitchen dashboard" : "Delivery dashboard"}</h2><p>Signed in as <strong>${escapeHtml(teamStaff.username)}</strong>. Role access is enforced by the local server.</p></div><button type="button" class="team-signout" id="team-signout">Sign out</button></header>
      <nav class="portal-tabs" aria-label="Admin dashboard sections">${tabs.map(([key, label]) => `<button type="button" class="portal-tab-btn ${key === active ? "active" : ""}" data-ptab="${key}">${label}</button>`).join("")}</nav>
      ${tabs.map(([key]) => `<section id="ptab-${key}" class="portal-tab-content" ${key === active ? "" : "hidden"}>${renderTeamTab(key, role)}</section>`).join("")}
    </section>`;
  container.querySelectorAll(".portal-tab-btn").forEach((btn) => btn.addEventListener("click", () => {
    container.querySelectorAll(".portal-tab-btn").forEach((b) => b.classList.toggle("active", b === btn));
    tabs.forEach(([key]) => {
      const panel = $(`#ptab-${key}`, container);
      if (panel) panel.hidden = key !== btn.dataset.ptab;
    });
    const next = new URL(location.href);
    next.searchParams.set("view", btn.dataset.ptab);
    history.replaceState({}, "", next);
    if (btn.dataset.ptab === "stories") initAdminStoriesDesk();
  }));
  container.querySelectorAll("[data-open-team-tab]").forEach((btn) => btn.addEventListener("click", () => {
    const target = btn.dataset.openTeamTab;
    const tabButton = container.querySelector(`[data-ptab="${CSS.escape(target)}"]`);
    tabButton?.click();
  }));
  $("#team-signout")?.addEventListener("click", async () => {
    if (teamRiderHeartbeat) clearTimeout(teamRiderHeartbeat);
    teamRiderHeartbeat = null;
    await API.post("auth/logout", {});
    teamStaff = null;
    document.body.classList.remove("team-dashboard-active");
    renderStaffLogin(container);
  });
  if (active === "stories") initAdminStoriesDesk();
  wireTeamDashboard(container);
}
function renderTeamTab(tab, role) {
  const todayKey = (/* @__PURE__ */ new Date()).toLocaleDateString("en-CA");
  const isToday = (order) => {
    const raw = String(order.created_at || "");
    const parsed = new Date(raw.includes("T") ? raw : raw.replace(" ", "T") + "Z");
    return !Number.isNaN(parsed.getTime()) && parsed.toLocaleDateString("en-CA") === todayKey;
  };
  const dayOrders = data.orders.filter(isToday);
  const isCod = (order) => ["cod", "cash on delivery"].includes(String(order.payment_method || "").toLowerCase());
  const isOpenIssue = (order) => Boolean(order.issue_note) || order.status === "cancelled" || isCod(order) && ["not_collected", "not_confirmed"].includes(order.cod_status);
  const paymentName = (order) => isCod(order) ? "Cash on delivery" : `Online · ${String(order.payment_method || "payment").toUpperCase()}`;
  const statusName = (status) => ({ received: "New order", accepted: "Accepted", preparing: "Preparing", ready_for_pickup: "Ready for pickup", picked_up: "Picked up", delivered: "Delivered", cancelled: "Cancelled" })[status] || String(status || "received").replaceAll("_", " ");
  const storyFor = (order) => data.foodStories.find((story) => String(story.order_id || "") === String(order.id));
  const orderCards = data.orders.map((order) => {
    const status = String(order.status || "received").toLowerCase();
    const hasDeliveryPin = order.order_type === "delivery" && order.delivery_latitude != null && order.delivery_longitude != null && Number.isFinite(Number(order.delivery_latitude)) && Number.isFinite(Number(order.delivery_longitude));
    const locationDetails = order.delivery_address || order.customer_phone || hasDeliveryPin || order.delivery_instructions ? `<div class="team-order-location">${order.delivery_address ? `<span>${escapeHtml(order.delivery_address)}</span>` : ""}${order.customer_phone ? `<a href="tel:${escapeHtml(order.customer_phone)}">${escapeHtml(order.customer_phone)}</a>` : ""}${order.delivery_instructions ? `<span class="team-delivery-instructions"><strong>Delivery instructions:</strong> ${escapeHtml(order.delivery_instructions)}</span>` : ""}${hasDeliveryPin && role !== "kitchen" ? `<a class="team-order-map-link" href="https://www.google.com/maps/dir/?api=1&destination=${Number(order.delivery_latitude)}%2C${Number(order.delivery_longitude)}&travelmode=two-wheeler&dir_action=navigate" target="_blank" rel="noopener noreferrer">Open delivery directions in Google Maps ↗</a>` : ""}</div>` : "";
    const story = storyFor(order);
    const itemSummary = Array.isArray(order.items) && order.items.length ? order.items.map((item) => `${escapeHtml(item.name || item.title || item.id || "Item")} × ${Number(item.qty || item.quantity || 1)}`).join(" · ") : "";
    const issueLine = order.issue_note ? `<div class="team-order-issue"><strong>Issue:</strong> ${escapeHtml(order.issue_note)}</div>` : order.status === "cancelled" ? '<div class="team-order-issue"><strong>Issue:</strong> Order cancelled</div>' : isCod(order) && ["not_collected", "not_confirmed"].includes(order.cod_status) ? `<div class="team-order-issue"><strong>Issue:</strong> COD ${order.cod_status === "not_collected" ? "not collected" : "collection not confirmed"}</div>` : "";
    const storyLine = story ? `Story ${escapeHtml(story.status || "submitted")}` : "No story submitted";
    const codCollectionLine = isCod(order) && order.cod_status === "collected" ? ` · COD received ${money(order.cod_collected_amount || order.total_amount)} by ${String(order.cod_collected_via || "payment").toUpperCase()}` : "";
    const riderFeedback = order.rider_feedback ? `<div class="team-order-issue"><strong>Rider feedback:</strong> ${escapeHtml(order.rider_feedback)}</div>` : "";
    const riderLine = order.delivery_rider ? ` · Rider: ${escapeHtml(order.delivery_rider)}` : order.order_type === "delivery" && status === "ready_for_pickup" ? " · Waiting for an available rider" : "";
    let action = "";
    if (role === "kitchen") {
      const next = status === "received" ? "accepted" : status === "accepted" ? "preparing" : status === "preparing" ? "ready_for_pickup" : "";
      if (next) action = `<button type="button" class="button button-green" data-order-status="${escapeHtml(order.id)}" data-next-status="${next}">${next === "accepted" ? "Accept order" : next === "preparing" ? "Start preparing" : "Mark ready for pickup"}</button>`;
    } else if (role === "delivery") {
      if (status === "ready_for_pickup") action = `<button type="button" class="button button-green" data-order-status="${escapeHtml(order.id)}" data-next-status="picked_up">Confirm pickup</button>`;
      if (status === "picked_up" && (!isCod(order) || ["collected", "not_collected"].includes(order.cod_status))) action = `<button type="button" class="button button-green" data-order-status="${escapeHtml(order.id)}" data-next-status="delivered">Mark delivered</button>`;
    }
    const codPanel = role === "delivery" && isCod(order) ? `<div class="team-cod-panel"><strong>Collect ${money(order.total_amount || 0)}</strong><span>COD: ${escapeHtml({ pending: "Awaiting collection", collected: "Received", not_collected: "Not received", not_confirmed: "Not confirmed" }[order.cod_status] || "Awaiting collection")}${order.cod_collected_via ? ` · ${escapeHtml(order.cod_collected_via.toUpperCase())}` : ""}</span>${status === "picked_up" ? `<div class="team-cod-actions"><label><input type="radio" name="cod-method-${escapeHtml(order.id)}" value="cash" checked> Cash</label><label><input type="radio" name="cod-method-${escapeHtml(order.id)}" value="upi"> UPI</label><button type="button" class="team-inline-action" data-cod-status="${escapeHtml(order.id)}" data-cod-value="collected">Record ${money(order.total_amount || 0)} received</button><button type="button" class="team-inline-action secondary" data-cod-status="${escapeHtml(order.id)}" data-cod-value="not_collected">Not received</button></div>` : order.cod_status === "collected" ? `<small>Amount received: ${money(order.cod_collected_amount || order.total_amount)} via ${escapeHtml(String(order.cod_collected_via || "").toUpperCase())}</small>` : ""}</div>` : "";
    const riderFeedbackForm = role === "delivery" && ["picked_up", "delivered"].includes(status) ? `<form class="team-rider-feedback-form" data-rider-feedback="${escapeHtml(order.id)}"><label>Delivery feedback or handover issue<textarea name="feedback" maxlength="500" placeholder="Gate, call-before-arrival, handover issue…">${escapeHtml(order.rider_feedback || "")}</textarea></label><button type="submit" class="team-inline-action">Save delivery note</button></form>` : "";
    const issueForm = role === "admin" ? `<form class="team-issue-form" data-save-order-issue="${escapeHtml(order.id)}"><label>Issue / staff note<input maxlength="500" name="issue_note" value="${escapeHtml(order.issue_note || "")}" placeholder="No issue noted"></label><button type="submit" class="team-inline-action">Save note</button></form>` : "";
    return `<article class="team-order-card"><div class="team-order-main"><div class="team-order-heading"><strong>Order #${escapeHtml(order.id)}</strong><span class="team-status-pill ${status}">${escapeHtml(statusName(status))}</span></div><div>${escapeHtml(order.customer_name || "Guest")} · ${escapeHtml(order.order_type || "delivery")} · ${escapeHtml(order.created_at || "")}</div>${itemSummary ? `<div class="team-order-items">${itemSummary}</div>` : ""}<div class="team-order-money"><strong>Total ${money(order.total_amount || 0)}</strong><span>${escapeHtml(paymentName(order))}</span></div><small>${money(order.subtotal || 0)} subtotal · ${storyLine}${order.order_type === "corporate" ? " · corporate catering" : ""}${riderLine}${codCollectionLine}</small>${locationDetails}${issueLine}${riderFeedback}${role === "admin" ? issueForm : ""}</div>${codPanel}${riderFeedbackForm}${action || (role === "admin" ? "" : '<span class="team-order-done">No action pending</span>')}</article>`;
  }).join("") || '<div class="team-empty-state">No orders in this queue yet.</div>';
  if (tab === "overview") {
    const pending = data.foodStories.filter((s) => s.status === "pending").length;
    const paidParties = teamBookings.filter((b) => b.booking_type === "party" && b.payment_status === "paid" && b.final_bill === null).length;
    dayOrders.filter(isCod);
    const onlineOrders = dayOrders.filter((order) => !isCod(order) && !["invoice", "cash"].includes(String(order.payment_method || "").toLowerCase()));
    const issues = data.orders.filter(isOpenIssue);
    const issueSummary = issues.length ? `<div class="team-issues-list">${issues.slice(0, 6).map((order) => `<article><strong>#${escapeHtml(order.id)}</strong><span>${escapeHtml(order.issue_note || (order.status === "cancelled" ? "Order cancelled" : "COD not confirmed"))}</span></article>`).join("")}</div>` : '<div class="team-empty-state">No order issues reported.</div>';
    const availableRiders = teamRiderAvailability.riders.filter((rider) => rider.is_available);
    const summary = teamOrderSummary;
    const receivedToday = Number(summary.received_today ?? dayOrders.length);
    const cancelledToday = Number(summary.cancelled_today ?? data.orders.filter((order) => order.status === "cancelled").length);
    const completedToday = Number(summary.completed_today ?? data.orders.filter((order) => ["delivered", "completed"].includes(order.status)).length);
    const codCash = Number(summary.cod_cash_today ?? 0);
    const codUpi = Number(summary.cod_upi_today ?? 0);
    const onlineTotal = Number(summary.online_selected_today ?? onlineOrders.reduce((sum, order) => sum + Number(order.total_amount || 0), 0));
    const issueCount = Number(summary.issue_count ?? issues.length);
    return `<div class="portal-stats-row"><div class="portal-stat-box"><div class="portal-stat-val">${receivedToday}</div><div class="portal-stat-lbl">Orders received today</div></div><div class="portal-stat-box"><div class="portal-stat-val">${completedToday}</div><div class="portal-stat-lbl">Completed today</div></div><div class="portal-stat-box"><div class="portal-stat-val">${cancelledToday}</div><div class="portal-stat-lbl">Cancelled today</div></div><div class="portal-stat-box"><div class="portal-stat-val">${money(onlineTotal)}</div><div class="portal-stat-lbl">Online selected · not settlement</div></div><div class="portal-stat-box"><div class="portal-stat-val">${money(codCash)}</div><div class="portal-stat-lbl">COD cash · today</div></div><div class="portal-stat-box"><div class="portal-stat-val">${money(codUpi)}</div><div class="portal-stat-lbl">COD UPI · today</div></div><div class="portal-stat-box"><div class="portal-stat-val">${issueCount}</div><div class="portal-stat-lbl">Orders with issues</div></div></div><p class="team-overview-note">Admin order history lists only completed or cancelled orders. Kitchen receives new orders immediately; ready deliveries go to riders marked available. Online selected totals are not verified settlements.</p><div class="team-admin-overview-grid"><section><div class="team-section-heading"><h3>Order issues</h3><button class="team-inline-action" type="button" data-open-team-tab="orders">Review finished orders</button></div>${issueSummary}<p class="team-overview-note">Available riders: ${availableRiders.length ? availableRiders.map((r) => escapeHtml(r.username)).join(", ") : "None"}</p></section><section><div class="team-section-heading"><h3>Guest stories</h3><span class="team-status-pill ${pending ? "received" : "delivered"}">${pending} pending</span></div><p class="team-overview-note">${data.foodStories.filter((s) => s.status === "approved").length} published stories</p><button class="button button-green" type="button" data-open-team-tab="stories">Open story review</button></section></div><div class="portal-stats-row team-admin-secondary-stats"><div class="portal-stat-box"><div class="portal-stat-val">${availableRiders.length}</div><div class="portal-stat-lbl">Riders available</div></div><div class="portal-stat-box"><div class="portal-stat-val">${paidParties}</div><div class="portal-stat-lbl">Party bills to settle</div></div></div><div class="team-preview-controls"><div><strong>Browser preview tools</strong><small>Resets this browser’s cart, preferences, and local preview state. Saved server orders and bookings remain.</small></div><button type="button" id="team-reset-preview" class="team-signout">Reset browser preview</button></div>`;
  }
  if (tab === "orders") {
    const riderPresence = role === "delivery" ? `<section class="team-rider-presence"><div><span class="team-presence-pill ${teamRiderAvailability.is_available ? "online" : "offline"}">${teamRiderAvailability.is_available ? "Available for orders" : "Currently unavailable"}</span><h3>Rider availability</h3><p>Available riders receive ready delivery orders automatically. Your active assignments: ${teamRiderAvailability.active_assignments || 0}.</p></div><button type="button" id="team-rider-toggle" data-rider-availability="${teamRiderAvailability.is_available ? "off" : "on"}" class="button ${teamRiderAvailability.is_available ? "button-outline" : "button-green"}">${teamRiderAvailability.is_available ? "Go unavailable" : "Go available"}</button></section>` : "";
    return `${riderPresence}<h3 class="team-tab-title">${role === "delivery" ? "Rider dispatch & delivery" : role === "kitchen" ? "Kitchen order queue" : "Completed & cancelled orders"}</h3><div class="team-orders-list">${orderCards}</div>`;
  }
  if (tab === "stories") return `<h3 class="team-tab-title">Customer food story review</h3><div id="admin-stories-desk"></div>`;
  if (tab === "bookings") return renderAdminBookings();
  if (tab === "corporate") return renderCorporateOrderTab();
  return "";
}
function renderAdminBookings() {
  const parties = teamBookings.filter((booking) => booking.booking_type === "party");
  const tables = teamBookings.filter((booking) => booking.booking_type === "dine");
  const partyCards = parties.map((booking) => {
    const settled = booking.final_bill !== null && booking.final_bill !== void 0;
    return `<article class="team-booking-card"><div class="team-booking-head"><div><strong>${escapeHtml(booking.customer_name)} · ${escapeHtml(booking.guest_count)} guests</strong><div>${escapeHtml(booking.booking_date)} at ${escapeHtml(booking.booking_time)} · ${escapeHtml(booking.customer_phone)}</div><small>Advance ${money(booking.deposit_amount || 0)} · ${escapeHtml(booking.payment_status || "pending")}</small></div><span class="team-booking-status">${escapeHtml(booking.status || "")}</span></div>${settled ? `<div class="settlement-result"><span>Final bill <strong>${money(booking.final_bill)}</strong></span><span>Advance credit <strong>${money(booking.deposit_amount)}</strong></span><span>${Number(booking.refund_due || 0) > 0 ? "Refund due" : "Balance due"} <strong>${money(Number(booking.refund_due || 0) > 0 ? booking.refund_due : booking.balance_due)}</strong></span>${Number(booking.refund_due || 0) > 0 ? "<small>Refund is flagged for staff follow-up; it is not sent automatically.</small>" : ""}</div>` : booking.payment_status === "paid" ? `<form class="team-settlement-form" data-settle-booking="${escapeHtml(booking.id)}"><label>Final event bill (₹)<input type="number" min="0" step="1" required placeholder="Enter final amount"></label><button class="button button-green" type="submit">Apply advance & settle</button></form>` : '<div class="team-pending-note">Waiting for verified online advance. This booking is not confirmed until payment is captured.</div>'}</article>`;
  });
  const tableCards = tables.map((booking) => `<article class="team-booking-card"><div class="team-booking-head"><div><strong>Table reservation · ${escapeHtml(booking.customer_name)} · ${escapeHtml(booking.guest_count)} guests</strong><div>${escapeHtml(booking.booking_date)} at ${escapeHtml(booking.booking_time)} · ${escapeHtml(booking.customer_phone)}</div><small>Advance ${money(booking.deposit_amount || 0)} · ${escapeHtml(booking.payment_status || "pending")}</small></div><span class="team-booking-status">${escapeHtml(booking.status || "")}</span></div>${booking.payment_status === "paid" ? '<div class="team-pending-note">Payment verified. Advance is recorded for the final dine-in bill.</div>' : '<div class="team-pending-note">Waiting for verified payment. The table reservation is not confirmed yet.</div>'}</article>`);
  return `<h3 class="team-tab-title">Table reservations</h3>${tableCards.length ? `<div class="team-bookings-list">${tableCards.join("")}</div>` : '<div class="team-empty-state">No table reservations yet.</div>'}<h3 class="team-tab-title" style="margin-top:24px">Party bookings & final bill settlement</h3>${partyCards.length ? `<div class="team-bookings-list">${partyCards.join("")}</div>` : '<div class="team-empty-state">No party bookings yet.</div>'}`;
}
function renderCorporateOrderTab() {
  if (!teamCorporateMenu.length) return '<h3 class="team-tab-title">Corporate catering · Admin only</h3><div class="team-empty-state">Corporate menu could not be loaded. Refresh after signing in as admin.</div>';
  return `<h3 class="team-tab-title">Corporate catering order</h3><p class="team-overview-note">This menu is private to signed-in admins. Add quantities and submit a catering order; it stays separate from the customer cart.</p><form id="corporate-order-form"><div class="corporate-admin-grid">${teamCorporateMenu.map((item) => `<label class="corporate-admin-item"><span><strong>${escapeHtml(item.name)}</strong><small>${escapeHtml(item.desc || "")}</small><b>${money(item.price)} <small>${escapeHtml(item.unitLabel || "")}</small></b></span><input type="number" min="0" max="500" data-corp-item="${escapeHtml(item.id)}" data-price="${Number(item.price)}" data-min-qty="${Number(item.minQty || 1)}" placeholder="0" aria-label="Quantity for ${escapeHtml(item.name)}"></label>`).join("")}</div><div class="corporate-admin-total" id="corporate-order-total" aria-live="polite"></div><div class="corporate-admin-details"><label>Customer or company<input id="corp-customer-name" required></label><label>Contact number<input id="corp-customer-phone" type="tel" required></label><label>Event date<input id="corp-event-date" type="date"></label></div><div class="notice">Orders above ₹10,000 receive 10% off; orders above ₹20,000 receive 15% off.</div><button class="button button-green" type="submit">Save catering order →</button></form>`;
}
function wireTeamDashboard(container, role) {
  $("#team-reset-preview", container)?.addEventListener("click", () => {
    if (!confirm("Reset this browser’s cart, preferences, and local preview state? Server orders, stories, and bookings will remain saved.")) return;
    localStorage.removeItem(KEY);
    location.reload();
  });
  container.querySelectorAll("[data-order-status]").forEach((btn) => btn.addEventListener("click", async () => {
    btn.disabled = true;
    const result = await API.post("orders/status", { order_id: btn.dataset.orderStatus, status: btn.dataset.nextStatus });
    if (!result?.success) {
      btn.disabled = false;
      toast(result?.error || "Could not update this order.", true);
      return;
    }
    toast(result.message || "Order updated.");
    await renderTeamPage();
  }));
  $("#team-rider-toggle", container)?.addEventListener("click", async (buttonEvent) => {
    const button = buttonEvent.currentTarget;
    button.disabled = true;
    const result = await API.post("rider/availability", { is_available: button.dataset.riderAvailability === "on" });
    if (!result?.success) {
      button.disabled = false;
      toast(result?.error || "Could not update availability.", true);
      return;
    }
    toast(result.message || "Rider availability updated.");
    await renderTeamPage();
  });
  container.querySelectorAll("[data-cod-status]").forEach((btn) => btn.addEventListener("click", async () => {
    btn.disabled = true;
    const collectionMethod = container.querySelector(`input[name="cod-method-${CSS.escape(btn.dataset.codStatus)}"]:checked`)?.value || "";
    const result = await API.post("orders/cod-status", { order_id: btn.dataset.codStatus, cod_status: btn.dataset.codValue, collection_method: collectionMethod });
    if (!result?.success) {
      btn.disabled = false;
      toast(result?.error || "Could not save COD status.", true);
      return;
    }
    toast(btn.dataset.codValue === "collected" ? "COD collection recorded." : "COD not received recorded.");
    await renderTeamPage();
  }));
  container.querySelectorAll("[data-rider-feedback]").forEach((form) => form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const button = form.querySelector('button[type="submit"]');
    button.disabled = true;
    const result = await API.post("orders/rider-note", { order_id: form.dataset.riderFeedback, feedback: form.elements.feedback.value.trim() });
    if (!result?.success) {
      button.disabled = false;
      toast(result?.error || "Could not save the delivery note.", true);
      return;
    }
    toast(result.message || "Delivery note saved.");
    await renderTeamPage();
  }));
  container.querySelectorAll("[data-save-order-issue]").forEach((form) => form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const result = await API.post("orders/issue", { order_id: form.dataset.saveOrderIssue, issue_note: form.elements.issue_note.value.trim() });
    if (!result?.success) {
      toast(result?.error || "Could not save the issue note.", true);
      return;
    }
    toast(result.message || "Issue note saved.");
    await renderTeamPage();
  }));
  container.querySelectorAll("[data-settle-booking]").forEach((form) => form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const result = await API.post("bookings/settle", { booking_id: form.dataset.settleBooking, final_bill: Number(form.querySelector("input").value) });
    if (!result?.success) {
      toast(result?.error || "Could not settle this bill.", true);
      return;
    }
    toast(`Bill settled. Balance due: ${money(result.balance_due)}${result.refund_due ? `, refund due: ${money(result.refund_due)}` : ""}`);
    await renderTeamPage();
  }));
  const corporateForm = $("#corporate-order-form", container);
  const updateCorporateTotal = () => {
    if (!corporateForm) return;
    const subtotal = $$("[data-corp-item]", corporateForm).reduce((sum, input) => sum + (Number(input.dataset.price) || 0) * (Number(input.value) || 0), 0);
    const discount = subtotal > 2e4 ? Math.round(subtotal * 0.15) : subtotal > 1e4 ? Math.round(subtotal * 0.1) : 0;
    const total = $("#corporate-order-total", corporateForm);
    if (total) total.innerHTML = `<span>Subtotal <strong>${money(subtotal)}</strong></span>${discount ? `<span>Volume discount <strong>−${money(discount)}</strong></span>` : ""}<span class="corporate-total-payable">Order total <strong>${money(subtotal - discount)}</strong></span>`;
  };
  corporateForm?.addEventListener("input", (e) => {
    if (e.target.matches("[data-corp-item]")) updateCorporateTotal();
  });
  updateCorporateTotal();
  corporateForm?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const items = $$("[data-corp-item]", container).map((input) => ({ id: input.dataset.corpItem, qty: Number(input.value || 0) })).filter((item) => item.qty > 0);
    for (const item of items) {
      const input = $(`[data-corp-item="${CSS.escape(item.id)}"]`, container);
      if (item.qty < Number(input.dataset.minQty || 1)) {
        toast(`Minimum quantity for this item is ${input.dataset.minQty}.`, true);
        return;
      }
    }
    const result = await API.post("corporate-orders", { customer_name: $("#corp-customer-name", container).value.trim(), customer_phone: $("#corp-customer-phone", container).value.trim(), event_date: $("#corp-event-date", container).value, items });
    if (!result?.success) {
      toast(result?.error || "Could not save the catering order.", true);
      return;
    }
    toast(`Corporate order ${result.order_id} saved for ${money(result.total)}.`);
    await renderTeamPage();
  });
}
let accountSection = "profile";
let accountOrdersLoadedFor = "";
let accountEditingAddress = null;
function renderAccountPage() {
  const container = $("#account-content");
  if (!container) return;
  const profile = data.customerProfile;
  data.deliveryAddress || {};
  document.body.classList.toggle("account-signed-in", Boolean(profile));
  if (!profile) {
    accountSection = "profile";
    const returningToCheckout = resumeCheckoutAfterSignIn();
    const registerMode = accountAuthMode === "register";
    const activeChallenge = accountOtpChallenge?.mode === accountAuthMode ? accountOtpChallenge : null;
    document.body.classList.remove("account-signed-in");
    container.innerHTML = `
      <div class="dialog-kicker">CUSTOMER ACCOUNT · SECURE SIGN IN</div>
      <h2 class="account-profile-title">${returningToCheckout ? "Sign in to finish your" : registerMode ? "Create your" : "Welcome back to your"} <em>${returningToCheckout ? "order." : registerMode ? "profile." : "account."}</em></h2>
      <p class="account-profile-copy">${returningToCheckout ? "Your cart is saved. Sign in or create an account to continue to checkout." : "Sign in to manage your orders and saved details."}</p>
      <div class="account-auth-switch" role="tablist" aria-label="Account access">
        <button type="button" data-account-auth-mode="register" class="${registerMode ? "active" : ""}" role="tab" aria-selected="${registerMode}">Create account</button>
        <button type="button" data-account-auth-mode="login" class="${!registerMode ? "active" : ""}" role="tab" aria-selected="${!registerMode}">Sign in</button>
      </div>
      <form id="customer-access-form" class="account-profile-form" data-auth-mode="${registerMode ? "register" : "login"}">
        ${registerMode ? `<label>Full name<input name="name" autocomplete="name" required maxlength="120" placeholder="Your name" value="${escapeHtml(customerAuthDraft.name)}"></label><label>Email address <span class="account-unverified">Optional</span><input name="email" type="email" autocomplete="email" placeholder="you@example.com" value="${escapeHtml(customerAuthDraft.email)}"></label>` : ""}
        <label class="${registerMode ? "" : "account-field-wide"}">Mobile number<input name="phone" type="tel" inputmode="tel" autocomplete="tel" pattern="[+0-9() -]{10,18}" required placeholder="+91 98765 43210" value="${escapeHtml(activeChallenge?.phone || customerAuthDraft.phone)}" ${activeChallenge ? "readonly" : ""}></label>
        ${activeChallenge ? `<label class="account-field-wide">SMS verification code<input name="otp" type="text" inputmode="numeric" autocomplete="one-time-code" pattern="[0-9]{4,8}" minlength="4" maxlength="8" required placeholder="Enter the code from SMS"></label><p class="account-otp-help account-field-wide">We sent a code to ${escapeHtml(activeChallenge.phone)}. <button type="button" id="customer-otp-change">Change number</button> · <button type="button" id="customer-otp-resend">Resend code</button></p>` : ""}
        <button class="button button-green account-profile-submit" type="submit">${activeChallenge ? "Verify & continue →" : registerMode ? "Send OTP →" : returningToCheckout ? "Send OTP & continue →" : "Send sign-in code →"}</button>
      </form>
      <p class="account-preview-note">Sign in with a one-time SMS code. Email is optional and can be verified from your profile.</p>`;
    container.querySelectorAll("[data-account-auth-mode]").forEach((button) => button.addEventListener("click", () => {
      accountAuthMode = button.dataset.accountAuthMode;
      accountOtpChallenge = null;
      customerAuthDraft = { name: "", email: "", phone: "" };
      renderAccountPage();
    }));
    $("#customer-access-form")?.addEventListener("submit", handleCustomerAccess);
    $("#customer-otp-change")?.addEventListener("click", () => {
      accountOtpChallenge = null;
      renderAccountPage();
    });
    $("#customer-otp-resend")?.addEventListener("click", () => requestCustomerOtp($("#customer-access-form"), true));
    return;
  }
  const nav = [
    ["orders", "▣", "Orders"],
    ["favorites", icon("heart"), "Favourites"],
    ["payments", icon("card"), "Payments"],
    ["addresses", icon("location"), "Addresses"],
    ["profile", '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="8" r="3.3"></circle><path d="M5.5 20c.8-3.2 3-5 6.5-5s5.7 1.8 6.5 5"></path></svg>', "Profile"]
  ];
  const navHtml = nav.map(([id, icon2, label]) => '<button type="button" class="account-side-link ' + (accountSection === id ? "active" : "") + '" data-account-view="' + id + '" aria-current="' + (accountSection === id ? "page" : "false") + '"><span aria-hidden="true">' + icon2 + "</span>" + label + "</button>").join("");
  let heading = "Your profile";
  let description = "Manage your personal contact details.";
  let panel = "";
  if (accountSection === "orders") {
    heading = "Order history";
    description = "See orders placed with the phone number saved to your profile.";
    const phoneDigits = String(profile.phone || "").replace(/\D/g, "").slice(-10);
    const orders = (data.orders || []).filter((order) => String(order.customer_phone || order.phone || "").replace(/\D/g, "").slice(-10) === phoneDigits);
    const cards = orders.map((order) => {
      const items = Array.isArray(order.items) ? order.items : [];
      const itemSummary = items.map((item) => escapeHtml(item.name || item.id || "Menu item") + " × " + Math.max(1, Number(item.qty || 1))).join(" · ");
      return '<article class="account-order-card"><div class="account-order-head"><strong>Order #' + escapeHtml(order.id || "—") + '</strong><span class="account-order-status">' + escapeHtml(String(order.status || "received").replaceAll("_", " ")) + '</span></div><div class="account-order-meta"><span>' + escapeHtml(order.created_at ? new Date(order.created_at).toLocaleString() : "Recent order") + "</span><strong>" + money(order.total_amount || order.total || 0) + "</strong></div><p>" + (itemSummary || "Order details") + "</p></article>";
    }).join("");
    panel = cards || '<div class="account-empty-state"><span>' + icon("receipt") + '</span><strong>No orders found yet</strong><p>Orders placed with this profile phone number will appear here.</p><a class="button button-outline" href="index.html#menu">Browse the menu</a></div>';
  } else if (accountSection === "favorites") {
    heading = "Your favourites";
    description = "The dishes you have saved for another visit.";
    const favorites = menu.filter((item) => (data.favorites || []).includes(item.id));
    panel = favorites.length ? '<div class="account-favorite-list">' + favorites.map(
      (item) => "<article><span>" + icon("heart") + "</span><div><strong>" + escapeHtml(item.name) + "</strong><small>" + escapeHtml(item.category) + "</small></div><b>" + money(item.price) + '</b><button type="button" data-remove-favorite="' + escapeHtml(item.id) + '" aria-label="Remove ' + escapeHtml(item.name) + ' from favourites">Remove</button></article>'
    ).join("") + "</div>" : '<div class="account-empty-state"><span>' + icon("heart") + '</span><strong>No saved dishes yet</strong><p>Tap the heart on a menu card to save a favourite.</p><a class="button button-outline" href="index.html#menu">Browse the menu</a></div>';
  } else if (accountSection === "payments") {
    heading = "Payments";
    description = "Payment methods are chosen when you place an order.";
    panel = '<div class="account-payment-note"><span>▤</span><div><strong>Choose at checkout</strong><p>Use the payment option shown during checkout. This preview does not save card or bank details in your profile.</p></div></div>';
  } else if (accountSection === "addresses") {
    heading = "Saved addresses";
    description = "Save Home, Work, and other places. Choose one at checkout.";
    const addresses = data.addresses || [];
    const editing = accountEditingAddress ? addresses.find((item) => item.id === accountEditingAddress) || {} : {};
    if (accountEditingAddress) {
      panel = '<form id="account-address-form" class="account-profile-form" data-address-id="' + escapeHtml(accountEditingAddress === "new" ? "" : accountEditingAddress) + '"><label>Address label<select name="tag"><option ' + (editing.tag === "Home" ? "selected" : "") + ">Home</option><option " + (editing.tag === "Work" ? "selected" : "") + ">Work</option><option " + (editing.tag === "Other" ? "selected" : "") + '>Other</option></select></label><label>Flat / house number<input name="flat" required autocomplete="address-line1" value="' + escapeHtml(editing.flat || "") + '"></label><label class="account-field-wide">Area / street<input name="area" required autocomplete="address-level2" value="' + escapeHtml(editing.area || "") + '"></label><label class="account-field-wide">Landmark / delivery note<input name="landmark" autocomplete="address-line2" value="' + escapeHtml(editing.landmark || "") + '"></label><input type="hidden" name="latitude" value="' + escapeHtml(editing.latitude ?? "") + '"><input type="hidden" name="longitude" value="' + escapeHtml(editing.longitude ?? "") + '"><div class="account-address-pin account-field-wide"><button type="button" class="account-pin-button" id="account-pin-address">⌖ Pin this address with my current location</button><small id="account-pin-status">' + (editing.latitude != null ? "Map pin saved for delivery." : "A map pin is needed for delivery orders.") + '</small></div><div class="account-address-actions account-field-wide"><button type="submit" class="button button-green">Save address</button><button type="button" class="button button-outline" id="account-cancel-address">Cancel</button></div></form>';
    } else {
      panel = '<div class="account-address-list">' + (addresses.length ? addresses.map((item) => {
        const isDefault = item.id === data.activeAddressId || !data.activeAddressId && item.id === addresses[0].id;
        const mapLink = item.latitude != null && item.longitude != null ? '<a href="https://www.google.com/maps/dir/?api=1&destination=' + Number(item.latitude) + "," + Number(item.longitude) + '" target="_blank" rel="noopener noreferrer">View pin ↗</a>' : "<small>Delivery pin needed</small>";
        const icon2 = item.tag === "Work" ? "▣" : item.tag === "Home" ? "⌂" : "⌖";
        return '<article class="account-address-card ' + (isDefault ? "is-default" : "") + '"><div class="account-address-icon" aria-hidden="true">' + icon2 + '</div><div><div class="account-address-title-row"><span class="account-address-label">' + escapeHtml(item.tag || "Other") + "</span>" + (isDefault ? '<span class="account-default-badge">Selected</span>' : "") + "</div><h3>" + escapeHtml(item.flat || "") + "</h3><p>" + escapeHtml(item.area || "") + (item.landmark ? ", " + escapeHtml(item.landmark) : "") + ', Agra</p><div class="account-address-map">' + mapLink + '</div><div class="account-address-card-actions"><button type="button" data-edit-address="' + escapeHtml(item.id) + '">Edit</button>' + (!isDefault ? '<button type="button" data-select-address="' + escapeHtml(item.id) + '">Use at checkout</button>' : "") + '<button type="button" data-delete-address="' + escapeHtml(item.id) + '">Remove</button></div></div></article>';
      }).join("") : '<div class="account-empty-state"><span>⌖</span><strong>No saved addresses yet</strong><p>Add Home, Work, or another delivery address. Pick one at checkout.</p></div>') + '</div><button type="button" class="button button-green account-add-address" id="account-add-address">＋ Add address</button>';
    }
  } else {
    const emailVerified = Boolean(profile.email_verified_at || profile.emailVerified);
    const emailStatus = emailVerified ? '<span class="account-verified">Email verified</span>' : '<span class="account-unverified">Not verified</span>';
    const emailVerificationPanel = emailVerified ? '<p class="account-verification-note account-field-wide">Your email address has been verified.</p>' : !profile.email ? '<p class="account-verification-note account-field-wide">Add an email address and save your profile to verify it.</p>' : accountEmailOtpChallenge ? '<form id="account-email-otp-form" class="account-email-verification account-field-wide"><label>Email verification code<input name="otp" type="text" inputmode="numeric" autocomplete="one-time-code" pattern="[0-9]{6}" minlength="6" maxlength="6" required placeholder="6-digit code"></label><div><button class="button button-green" type="submit">Verify email</button><button class="account-email-resend" id="account-email-resend" type="button">Resend code</button></div></form><p class="account-verification-note account-field-wide">Enter the code sent to your saved email address. It expires in 10 minutes.</p>' : '<div class="account-email-verification account-field-wide"><p class="account-verification-note">Email is optional. Verify it to confirm it belongs to you.</p><button class="button button-outline" id="account-email-send" type="button">Send email verification code</button></div>';
    panel = '<form id="account-profile-form" class="account-profile-form"><label>Full name<input name="name" autocomplete="name" required maxlength="120" value="' + escapeHtml(profile.name || "") + '"></label><label>Email address ' + emailStatus + '<input name="email" type="email" autocomplete="email" value="' + escapeHtml(profile.email || "") + '"></label><label class="account-field-wide">Phone number <span class="account-verified">' + (profile.phone_verified_at ? "SMS verified" : "Verification required") + '</span><input name="phone" type="tel" readonly value="' + escapeHtml(profile.phone || "") + '"></label><p class="account-verification-note account-field-wide">Your mobile number is verified by SMS. Save profile changes before requesting an email code.</p><button class="button button-green account-profile-submit" type="submit">Save profile</button></form>' + emailVerificationPanel;
  }
  container.innerHTML = '<div class="account-profile-head"><div><div class="dialog-kicker">CUSTOMER PROFILE</div><h2 class="account-profile-title">Welcome, <em>' + escapeHtml(profile.name || "Food Lover") + '.</em></h2><p class="account-profile-copy">Your Bhadawar account, in one place.</p></div><button type="button" id="account-signout" class="account-signout">Sign out</button></div><div class="account-dashboard"><nav class="account-side-nav" aria-label="Profile sections">' + navHtml + '</nav><section class="account-section-panel" aria-live="polite"><div class="account-section-heading"><h3>' + heading + "</h3><p>" + description + "</p></div>" + panel + '</section></div><div class="account-profile-actions"><a href="index.html#menu" class="button button-outline">Order food</a></div>';
  container.querySelectorAll("[data-account-view]").forEach((button) => button.addEventListener("click", () => {
    accountSection = button.dataset.accountView;
    accountEditingAddress = null;
    renderAccountPage();
    if (accountSection === "orders") loadAccountOrderHistory(profile.phone);
  }));
  $("#account-add-address")?.addEventListener("click", () => {
    accountEditingAddress = "new";
    renderAccountPage();
  });
  $("#account-cancel-address")?.addEventListener("click", () => {
    accountEditingAddress = null;
    renderAccountPage();
  });
  container.querySelectorAll("[data-edit-address]").forEach((button) => button.addEventListener("click", () => {
    accountEditingAddress = button.dataset.editAddress;
    renderAccountPage();
  }));
  container.querySelectorAll("[data-select-address]").forEach((button) => button.addEventListener("click", () => {
    const selected = data.addresses.find((item) => item.id === button.dataset.selectAddress);
    if (!selected) return;
    data.activeAddressId = selected.id;
    data.deliveryAddress = { ...data.deliveryAddress, ...selected, phone: profile.phone, summary: `Agra, ${selected.area}, Agra` };
    save();
    renderAccountPage();
    toast(`${selected.tag || "Address"} selected for checkout.`);
  }));
  container.querySelectorAll("[data-delete-address]").forEach((button) => button.addEventListener("click", () => {
    data.addresses = (data.addresses || []).filter((item) => item.id !== button.dataset.deleteAddress);
    if (data.activeAddressId === button.dataset.deleteAddress) data.activeAddressId = data.addresses[0]?.id || "";
    if (data.activeAddressId) {
      const selected = data.addresses.find((item) => item.id === data.activeAddressId);
      data.deliveryAddress = { ...data.deliveryAddress, ...selected, phone: profile.phone, summary: `Agra, ${selected.area}, Agra` };
    } else {
      data.deliveryAddress = { ...defaultData.deliveryAddress, flat: "", area: "", landmark: "", phone: profile.phone, latitude: null, longitude: null, deliveryDistanceKm: null };
    }
    save();
    renderAccountPage();
    toast("Address removed.");
  }));
  $("#account-pin-address")?.addEventListener("click", () => {
    const status = $("#account-pin-status");
    if (!navigator.geolocation) {
      status.textContent = "Location is unavailable in this browser.";
      return;
    }
    status.textContent = "Finding your location…";
    navigator.geolocation.getCurrentPosition((position) => {
      const form = $("#account-address-form");
      form.elements.latitude.value = Number(position.coords.latitude.toFixed(6));
      form.elements.longitude.value = Number(position.coords.longitude.toFixed(6));
      status.textContent = "Delivery pin added.";
    }, () => {
      status.textContent = "Could not get location. Allow location access and try again.";
    }, { enableHighAccuracy: true, timeout: 12e3, maximumAge: 6e4 });
  });
  $("#account-address-form")?.addEventListener("submit", saveAccountAddress);
  $("#account-profile-form")?.addEventListener("submit", saveAccountProfile);
  $("#account-email-send")?.addEventListener("click", async () => {
    const emailInput = $('#account-profile-form [name="email"]');
    if (!emailInput?.value.trim()) {
      toast("Add an email address and save your profile first.", true);
      return;
    }
    if (emailInput.value.trim().toLowerCase() !== String(customerSession?.email || "").toLowerCase()) {
      toast("Save your changed email address before requesting a code.", true);
      return;
    }
    await requestAccountEmailOtp(false);
  });
  $("#account-email-otp-form")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const submit = event.currentTarget.querySelector('button[type="submit"]');
    if (submit) submit.disabled = true;
    const result = await API.post("customer-auth/email-otp/verify", { otp: new FormData(event.currentTarget).get("otp") });
    if (!result?.success || !result.customer) {
      if (submit) submit.disabled = false;
      toast(result?.error || "That email code could not be verified. Request another code and try again.", true);
      return;
    }
    accountEmailOtpChallenge = false;
    customerSession = result.customer;
    data.customerProfile = { ...result.customer, emailVerified: true, phoneVerified: Boolean(result.customer.phone_verified_at) };
    save();
    renderAccountPage();
    toast("Your email address is verified.");
  });
  $("#account-email-resend")?.addEventListener("click", () => requestAccountEmailOtp(true));
  container.querySelectorAll("[data-remove-favorite]").forEach((button) => button.addEventListener("click", () => {
    data.favorites = (data.favorites || []).filter((id) => id !== button.dataset.removeFavorite);
    save();
    renderAccountPage();
  }));
  $("#account-signout")?.addEventListener("click", async () => {
    await API.post("customer-auth/logout", {});
    applyCustomerSession(null);
    renderAccountPage();
    toast("You have signed out.");
  });
  if (accountSection === "orders") loadAccountOrderHistory(profile.phone);
}
async function handleCustomerAccess(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const fields = new FormData(form);
  const mode = form.dataset.authMode;
  const payload = {
    phone: String(fields.get("phone") || "").trim(),
    purpose: mode
  };
  if (mode === "register") {
    payload.name = String(fields.get("name") || "").trim();
    payload.email = String(fields.get("email") || "").trim();
    customerAuthDraft = { ...customerAuthDraft, name: payload.name, email: payload.email, phone: payload.phone };
  } else customerAuthDraft.phone = payload.phone;
  if (accountOtpChallenge?.mode === mode) {
    payload.otp = String(fields.get("otp") || "").trim();
    const submit = form.querySelector('button[type="submit"]');
    if (submit) submit.disabled = true;
    const result = await API.post("customer-auth/otp/verify", payload);
    if (!result?.success || !result.customer) {
      if (submit) submit.disabled = false;
      toast(customerOtpErrorMessage(result, "That code could not be verified. Request another code and try again."), true);
      return;
    }
    accountOtpChallenge = null;
    finishCustomerSignIn(result.customer);
    return;
  }
  await requestCustomerOtp(form, false, payload);
}
function customerOtpErrorMessage(result, fallback) {
  if (result?.httpStatus === 503) return "SMS sign-in is temporarily unavailable. Please try again later.";
  if (result?.httpStatus === 502) return "We could not reach the SMS service. Please try again shortly.";
  return result?.error || fallback;
}
async function requestCustomerOtp(form, isResend = false, suppliedPayload = null) {
  if (!form) return;
  const fields = new FormData(form);
  const mode = form.dataset.authMode;
  const payload = suppliedPayload || {
    phone: String(fields.get("phone") || "").trim(),
    purpose: mode,
    name: mode === "register" ? String(fields.get("name") || "").trim() : "",
    email: mode === "register" ? String(fields.get("email") || "").trim() : ""
  };
  const submit = form.querySelector('button[type="submit"]');
  if (submit) submit.disabled = true;
  const result = await API.post("customer-auth/otp/request", payload);
  if (!result?.success) {
    if (submit) submit.disabled = false;
    toast(customerOtpErrorMessage(result, "Could not send the sign-in code. Please try again."), true);
    return;
  }
  accountOtpChallenge = { mode, phone: payload.phone };
  toast(isResend ? "A new verification code was requested." : "Verification code sent by SMS.");
  renderAccountPage();
}
async function requestAccountEmailOtp(isResend = false) {
  const result = await API.post("customer-auth/email-otp/request", {});
  if (!result?.success) {
    toast(result?.error || "Could not send an email verification code. Please try again.", true);
    return;
  }
  if (result.already_verified && result.customer) {
    customerSession = result.customer;
    data.customerProfile = { ...result.customer, emailVerified: true, phoneVerified: Boolean(result.customer.phone_verified_at) };
    accountEmailOtpChallenge = false;
    save();
    renderAccountPage();
    toast("Your email address is already verified.");
    return;
  }
  accountEmailOtpChallenge = true;
  renderAccountPage();
  toast(isResend ? "A new email verification code was sent." : "Email verification code sent.");
}
async function saveAccountProfile(event) {
  event.preventDefault();
  if (!customerSession?.phone) {
    accountAuthMode = "login";
    renderAccountPage();
    return;
  }
  const fields = new FormData(event.currentTarget);
  const name = String(fields.get("name") || "").trim();
  const email = String(fields.get("email") || "").trim();
  const result = await API.post("customer-auth/profile", { name, email });
  if (!result?.success || !result.customer) {
    toast(result?.error || "Your profile could not be updated. Please try again.", true);
    return;
  }
  const emailChanged = String(customerSession?.email || "").toLowerCase() !== email.toLowerCase();
  customerSession = result.customer;
  if (emailChanged) accountEmailOtpChallenge = false;
  data.customerProfile = { ...result.customer, emailVerified: Boolean(result.customer.email_verified_at), phoneVerified: Boolean(result.customer.phone_verified_at) };
  data.customerName = data.customerProfile.name;
  save();
  renderAccountPage();
  toast("Your profile was updated.");
}
function saveAccountAddress(event) {
  event.preventDefault();
  const fields = new FormData(event.currentTarget);
  const addressId = event.currentTarget.dataset.addressId || "";
  const previous = (data.addresses || []).find((item) => item.id === addressId) || {};
  const nextAddress = {
    ...previous,
    id: addressId || `address-${Date.now()}`,
    tag: String(fields.get("tag") || "Home"),
    flat: String(fields.get("flat") || "").trim(),
    area: String(fields.get("area") || "").trim(),
    landmark: String(fields.get("landmark") || "").trim(),
    phone: data.customerProfile?.phone || data.wallet.phone || "",
    latitude: fields.get("latitude") ? Number(fields.get("latitude")) : null,
    longitude: fields.get("longitude") ? Number(fields.get("longitude")) : null,
    summary: "Agra, " + String(fields.get("area") || "").trim() + ", Agra"
  };
  data.addresses = data.addresses || [];
  const existingIndex = data.addresses.findIndex((item) => item.id === addressId);
  if (existingIndex >= 0) data.addresses[existingIndex] = nextAddress;
  else data.addresses.push(nextAddress);
  if (!data.activeAddressId || data.activeAddressId === addressId || data.addresses.length === 1) {
    data.activeAddressId = nextAddress.id;
    data.deliveryAddress = { ...data.deliveryAddress, ...nextAddress };
  }
  accountEditingAddress = null;
  save();
  renderAccountPage();
  toast(addressId ? "Your saved address was updated." : "Address added and saved.");
}
async function loadAccountOrderHistory(phone) {
  if (!phone || accountOrdersLoadedFor === phone) return;
  accountOrdersLoadedFor = phone;
  const result = await API.get("orders/history");
  if (!result?.success || data.customerProfile?.phone !== phone) return;
  const local = data.orders || [];
  const remote = result.orders || [];
  const combined = new Map([...remote, ...local].map((order) => [String(order.id), order]));
  data.orders = [...combined.values()].sort((a, b) => new Date(b.created_at || b.date || 0) - new Date(a.created_at || a.date || 0));
  save();
  if (accountSection === "orders") renderAccountPage();
}
async function init() {
  const page = document.body.dataset.page;
  const localHost = ["localhost", "127.0.0.1", "::1"].includes(window.location.hostname);
  const temporaryTunnel = window.location.hostname.endsWith(".trycloudflare.com");
  const container = page === "team" ? $("#team-content") : null;
  if (container && !localHost) {
    publicPreviewMode = true;
    renderStaffLogin(container);
  }
  const previewReady = window.BHADAWAR_PREVIEW_READY || Promise.resolve(false);
  const previewConfigured = await Promise.race([
    Promise.resolve(previewReady).catch(() => false),
    new Promise((resolve) => setTimeout(() => resolve(temporaryTunnel), 1800))
  ]);
  publicPreviewMode = Boolean(previewConfigured) || Boolean(container && !localHost);
  if (publicPreviewMode && !document.querySelector(".public-preview-banner")) {
    const notice = document.createElement("aside");
    notice.className = "public-preview-banner";
    notice.setAttribute("role", "status");
    notice.textContent = "TEMPORARY PREVIEW · Orders and bookings are for testing only and will not be prepared or charged. Please do not enter real phone numbers or addresses.";
    document.body.prepend(notice);
  }
  if (publicPreviewMode && !hasSavedPreviewData) {
    data.cart = [];
    data.wallet = { ...defaultData.wallet, balance: 0, signedIn: false, phone: "", welcomeGranted: false, entries: [] };
    data.deliveryAddress = { ...defaultData.deliveryAddress, flat: "", area: "", landmark: "", phone: "", latitude: null, longitude: null, deliveryDistanceKm: null };
    data.orders = [];
    data.reservations = [];
    save();
  }
  if (page !== "team") await refreshCustomerSession();
  if (page === "team") {
    try {
      await renderTeamPage();
    } catch {
      renderStaffLogin(container, "Could not connect to the staff portal. Refresh and try again.");
    }
    return;
  }
  if (page === "account") {
    renderAccountPage();
    return;
  }
  updateCartCounters();
  updateOrderModeUI();
  renderFullMenu();
  initEvents();
  initFoodStories();
  syncFromBackend();
  if (resumeCheckoutAfterSignIn() && data.cart.length) {
    sessionStorage.removeItem("bhadawar-checkout-intent");
    window.setTimeout(() => openCheckout(), 350);
  }
}
storyModule = createStoriesModule({
  data,
  menu,
  API,
  $,
  $$,
  money,
  escapeHtml,
  toast,
  save,
  updateCartCounters,
  updateOrderModeUI,
  openDialog,
  closeDialog,
  config: CONFIG,
  mediaUrl,
  syncFromBackend,
  loadData
});
const { initFoodStories, initAdminStoriesDesk, renderStoryBar, renderFoodStories, renderLeaderboard, renderMiniLeaderboard } = storyModule;
hydrateIcons(document);
init();
