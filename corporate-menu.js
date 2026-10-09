/* Corporate catering prices transcribed from the Bhadawar Hotel menu supplied by the restaurant. */
(() => {
  const items = [];
  const add = (id, name, description, price, category, unitLabel, minQty = 1, emoji = '🍱') =>
    items.push({ id: `corp-${id}`, name, desc: description, price, category, unitLabel, minQty, emoji, veg: true, spice: 'Mild', tag: 'Corporate menu', available: true });

  const boxes = [
    ['box-1', 'Executive Box 1', 'Dal makhani, jeera rice, mix veg, 2 phulka, salad, pickle and sweet', 180],
    ['box-2', 'Executive Box 2', 'Paneer butter masala, jeera rice, veg pulao, 2 phulka, salad, pickle and sweet', 200],
    ['box-3', 'Executive Box 3', 'Kadhi pakora, rajma, jeera rice, mix veg, 2 phulka, salad, pickle and sweet', 180],
    ['premium-box', 'Premium Executive Box', 'Paneer lababdar, dal makhani, veg pulao, 2 lachha paratha, raita, salad, pickle and sweet', 230]
  ];
  boxes.forEach(([id, name, desc, price]) => add(id, name, desc, price, 'Executive lunch boxes', 'per box · minimum 10 boxes', 10));

  const combos = [
    ['combo-1', 'Team Combo 1', 'Paneer butter masala, mix veg, dal tadka, jeera rice, 2 phulka, salad and sweet', 320],
    ['combo-2', 'Team Combo 2', 'Shahi paneer, veg pulao, dal makhani, aloo jeera, 2 lachha paratha, salad and sweet', 350],
    ['combo-3', 'Team Combo 3', 'Paneer lababdar, kadai paneer, dal tadka, jeera rice, 2 phulka, salad and sweet', 330],
    ['combo-4', 'Team Combo 4', 'Veg biryani, chole, paneer do pyaza, raita, salad, 2 kulcha and sweet', 360]
  ];
  combos.forEach(([id, name, desc, price]) => add(id, name, desc, price, 'Team party combos', 'per person · minimum 10 people', 10, '🥘'));

  const snacks = [
    ['snacks-1', 'Snacks Package 1', 'Veg sandwich, mini samosa, veg cutlet, masala peanut, cookies and tea or coffee', 110],
    ['snacks-2', 'Snacks Package 2', 'Veg puff, cheese corn ball, spring roll, masala peanut and tea or coffee', 140],
    ['snacks-3', 'Snacks Package 3', 'Paneer tikka (2 pcs), veg manchurian dry, mini samosa, cookies and tea or coffee', 170]
  ];
  snacks.forEach(([id, name, desc, price]) => add(id, name, desc, price, 'Meeting snacks & hi-tea', 'per person · minimum 10 people', 10, '☕'));

  const conferences = [
    ['half-day', 'Half-day Conference Package', 'Welcome drink, tea or coffee, 2 snacks and lunch', 270],
    ['full-day', 'Full-day Conference Package', 'Welcome drink, tea or coffee, 2 snacks, lunch and evening hi-tea', 410],
    ['premium-day', 'Premium Conference Package', 'Welcome drink, tea or coffee, 2 snacks, premium lunch and dessert', 530]
  ];
  conferences.forEach(([id, name, desc, price]) => add(id, name, desc, price, 'Conference & seminar packages', 'per person · minimum 20 people', 20, '📋'));

  const mains = [
    ['Dal Makhani',450,850],['Dal Tadka',400,750],['Yellow Dal (Plain)',350,650],['Paneer Butter Masala',750,1400],['Shahi Paneer',750,1400],['Paneer Lababdar',750,1400],['Kadai Paneer',750,1400],['Paneer Do Pyaza',700,1300],['Handi Paneer',800,1500],['Palak Paneer',700,1300],['Matar Paneer',650,1200],['Mix Veg',450,850],['Veg Kolhapuri',550,1050],['Veg Jalfrezi',550,1050],['Aloo Jeera',400,750],['Chana Masala',400,750],['Rajma Masala',450,850],['Malai Kofta (2 pcs)',750,1400],['Mushroom Masala',700,1300]
  ];
  mains.forEach(([name, half, full], i) => {
    add(`main-${i+1}-half`, name, 'Pure vegetarian main course', half, 'Main course · pure veg', 'half · serves 5–6', 1, '🍛');
    add(`main-${i+1}-full`, name, 'Pure vegetarian main course', full, 'Main course · pure veg', 'full · serves 10–12', 1, '🍛');
  });

  const sides = [
    ['Jeera Rice',60],['Steam Rice',50],['Veg Pulao',80],['Veg Biryani',110],['Kashmiri Pulao',100],
    ['Lachha Paratha',40],['Phulka (2 pcs)',30],['Butter Naan',50],['Plain Naan',40],['Garlic Naan',50],['Kulcha (Plain)',50],['Kulcha (Aloo / Onion)',60]
  ];
  sides.forEach(([name, price], i) => add(`rice-bread-${i+1}`, name, 'Freshly prepared for your team', price, 'Rice & breads', 'per person / portion', 1, i < 5 ? '🍚' : '🫓'));

  const drinks = [['Tea',20],['Coffee',25],['Lemon Tea',25],['Masala Chai',30],['Fresh Lime Water',35],['Mineral Water (1 Ltr.)',20],['Buttermilk (Masala)',30],['Sweet Lassi',60]];
  drinks.forEach(([name, price], i) => add(`beverage-${i+1}`, name, 'Beverage for meetings and gatherings', price, 'Beverages', 'per cup / glass', 1, '🥤'));

  const extras = [['Salad',35,60],['Raita',40,70],['Boondi Raita',45,80],['Papad (2 pcs)',20,35],['Masala Papad',30,50],['Pickle (per portion)',15,25],['Masala Chaas',30,50],['Gulab Jamun (2 pcs)',40,70]];
  extras.forEach(([name, half, full], i) => {
    add(`extra-${i+1}-half`, name, 'À la carte extra', half, 'À la carte extras', 'half portion', 1, '🥗');
    add(`extra-${i+1}-full`, name, 'À la carte extra', full, 'À la carte extras', 'full portion', 1, '🥗');
  });

  window.BHADAWAR_CORPORATE_MENU = items;
})();
