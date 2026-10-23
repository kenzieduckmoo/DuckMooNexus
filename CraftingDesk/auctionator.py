"""Read Auctionator v8 CBOR snapshots as data; never execute addon code."""
from datetime import datetime
import math

def decode_cbor(blob):
    data=blob.encode('latin1') if isinstance(blob,str) else blob
    pos=0
    def take(n):
        nonlocal pos
        if pos+n>len(data): raise ValueError('Truncated Auctionator CBOR')
        value=data[pos:pos+n];pos+=n;return value
    def read(depth=0):
        if depth>30: raise ValueError('Auctionator CBOR nesting exceeds limit')
        head=take(1)[0];major,info=head>>5,head&31
        if info<24: size=info
        elif info in (24,25,26,27): size=int.from_bytes(take(1<<(info-24)),'big')
        else: raise ValueError('Unsupported Auctionator CBOR length')
        if major==0:return size
        if major==1:return -1-size
        if major in (2,3):return take(size).decode('latin1' if major==2 else 'utf-8')
        if major==4:return [read(depth+1) for _ in range(size)]
        if major==5:
            if size>1000000: raise ValueError('Auctionator map exceeds limit')
            result={}
            for _ in range(size):
                key=read(depth+1);result[key]=read(depth+1)
            return result
        raise ValueError('Unsupported Auctionator CBOR type')
    value=read()
    if pos!=len(data): raise ValueError('Trailing Auctionator CBOR data')
    return value

def auctionator_prices(database,market):
    if database.get('__dbversion')!=8: raise ValueError('Unsupported Auctionator database version')
    result={'commodities':{},'realms':{},'entries':0,'warnings':[]}
    # Auctionator uses local Jan 1 2020 midnight and records days, not exact times.
    epoch=int(datetime(2020,1,1).timestamp())
    for realm,raw in database.items():
        if realm=='__dbversion':continue
        try:
            records=decode_cbor(raw) if isinstance(raw,str) else raw
        except ValueError:
            result['warnings'].append(f'No readable saved price table for {realm}; that realm was skipped. Other price tables can still be imported.');continue
        if not isinstance(records,dict):
            result['warnings'].append(f'No readable saved price table for {realm}; that realm was skipped. Other price tables can still be imported.');continue
        for key,row in records.items():
            if not str(key).isdigit():continue # Never collapse gear or pet variants.
            if isinstance(row,str):row=decode_cbor(row)
            if not isinstance(row,dict):continue
            price=row.get('m')
            days=[int(day) for day in row.get('h',{}) if str(day).isdigit()]
            if not days or not isinstance(price,(int,float)) or not math.isfinite(price) or price<=0:continue
            item='i:'+str(key);at=epoch+max(days)*86400
            commodity=item in market.get('commodities',{})
            bucket=result['commodities'] if commodity else result['realms'].setdefault(realm.replace(' ','').casefold(),{})
            quote={'price':price,'at':at,'source':'Auctionator scan (day precision)','scope':'US' if commodity else realm,'dayPrecision':True}
            if item not in bucket or at>bucket[item]['at']:bucket[item]=quote
            result['entries']+=1
    return result
