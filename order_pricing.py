"""Authoritative menu and checkout totals for the Bhadawar order API."""
import math
import re
from pathlib import Path


MENU_DATA_PATH = Path(__file__).with_name('menu-data.js')
RESTAURANT_LATITUDE = 27.185413
RESTAURANT_LONGITUDE = 78.02044


def _menu_id(category, name):
    slug = re.sub(r'[^a-z0-9]+', '-', name.casefold()).strip('-')
    return f'{category}-{slug}'


def load_menu_catalog():
    """Read the prices from the same owner-maintained menu data used by the UI."""
    source = MENU_DATA_PATH.read_text(encoding='utf-8')
    rows_match = re.search(r'const rows\s*=\s*`([^`]*)`\s*\.trim\(\)\s*;', source, re.DOTALL)
    if not rows_match:
        raise RuntimeError('The published menu price list could not be loaded.')

    catalog = {}
    for raw_row in rows_match.group(1).splitlines():
        row = raw_row.strip()
        if not row:
            continue
        parts = row.split('|')
        if len(parts) != 3:
            raise RuntimeError('A menu price row is malformed.')
        category, name, raw_price = parts
        try:
            price = int(raw_price)
        except ValueError as error:
            raise RuntimeError(f'The menu price for {name} is invalid.') from error
        if price < 0:
            raise RuntimeError(f'The menu price for {name} cannot be negative.')
        catalog[_menu_id(category, name)] = {'id': _menu_id(category, name), 'name': name, 'price': price}
    return catalog


def round_rupees(value):
    """Match JavaScript's Math.round for non-negative rupee amounts."""
    return math.floor(float(value) + 0.5)


def distance_km(latitude, longitude):
    radians = math.radians
    lat1, lon1, lat2, lon2 = map(float, (RESTAURANT_LATITUDE, RESTAURANT_LONGITUDE, latitude, longitude))
    delta_lat = radians(lat2 - lat1)
    delta_lon = radians(lon2 - lon1)
    half_chord = (math.sin(delta_lat / 2) ** 2
                  + math.cos(radians(lat1)) * math.cos(radians(lat2)) * math.sin(delta_lon / 2) ** 2)
    return 6371 * 2 * math.atan2(math.sqrt(half_chord), math.sqrt(1 - half_chord))


def checkout_totals(items, order_type, distance, first_order, tax_percent=5,
                    delivery_fee_under_5=35, delivery_fee_5_to_10=50):
    subtotal = sum(item['price'] * item['qty'] for item in items)
    tax = round_rupees(subtotal * float(tax_percent) / 100)
    delivery_fee = 0
    if order_type == 'delivery' and distance is not None and not first_order:
        delivery_fee = int(delivery_fee_5_to_10 if distance > 5 else delivery_fee_under_5)
    return {
        'subtotal': subtotal,
        'tax': tax,
        'delivery_fee': delivery_fee,
        'discount': 0,
        'total_before_points': subtotal + tax + delivery_fee,
    }
