"""Source-specific observations. Bank deposits/withdrawals are internal transfers."""
from collections import Counter
import hashlib
import json


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def accountant(data):
    db = data['WarbandAccountantDB']
    occurrences = Counter()
    for entry in db.get('ledger', {}).values():
        if entry.get('type') not in ('DEPOSIT', 'MANUAL_DEPOSIT', 'WITHDRAW', 'MANUAL_WITHDRAW'):
            raise ValueError('Unknown accountant transfer type')
        stamp, amount, balance = entry['timestamp'], entry['amount'], entry['balanceAfter']
        if any(type(x) is not int or x < 0 for x in (stamp, amount, balance)):
            raise ValueError('Invalid accountant copper/timestamp')
        # Ledger indices shift on every prepend. Payload hash plus multiplicity
        # survives reordering, overlaps, and genuine identical entries.
        key = hashlib.sha256(canonical(entry).encode()).hexdigest()
        occurrences[key] += 1
        yield dict(kind='warbank_balance', entity='account', source_key=f'ledger:{key}:{occurrences[key]}',
                   observed_at=stamp, precision='second', copper=balance,
                   quality='recorded_after_transfer', payload=entry)
    for entity, row in db.get('characters', {}).items():
        if type(row.get('currentGold')) is int and type(row.get('lastUpdate')) is int:
            yield dict(kind='character_balance', entity=entity, source_key=entity,
                       observed_at=row['lastUpdate'], precision='second', copper=row['currentGold'],
                       quality='cached_character', payload=row)
    # accountTotalHistory is intentionally NOT imported as Warbank history.


def syndicator(data):
    db = data['SYNDICATOR_DATA']
    for key, row in db.get('Warband', {}).items():
        if type(row.get('money')) is int and row['money'] >= 0:
            yield dict(kind='warbank_balance', entity='account', source_key=f'Warband:{key}',
                       observed_at=None, precision='unknown', copper=row['money'],
                       quality='cached_without_observation_time', payload={'money': row['money'], 'details': row.get('details')})
    for entity, row in db.get('Characters', {}).items():
        if type(row.get('money')) is int and row['money'] >= 0:
            yield dict(kind='character_balance', entity=entity, source_key=entity,
                       observed_at=None, precision='unknown', copper=row['money'],
                       quality='cached_without_observation_time', payload={'money': row['money']})


def warband(data):
    activity = data['DuckMooWarbandDB'].get('activity', {})
    bank = activity.get('bank', {})
    if type(bank.get('at')) is int and type(bank.get('amount')) is int:
        yield dict(kind='warbank_balance', entity='account', source_key='activity.bank',
                   observed_at=bank['at'], precision='second', copper=bank['amount'],
                   quality='legacy_api_sample_unvalidated', payload=bank)
    # Session bankEnd timestamps are not exact sample timestamps. Preserve sessions
    # in the source snapshot, do not invent observation times for them.


ADAPTERS = {'WarbandAccountant.lua': accountant, 'Syndicator.lua': syndicator,
            'DuckMooWarband.lua': warband}


def observations(source, data):
    yield from ADAPTERS.get(source, lambda _: ()) (data)
