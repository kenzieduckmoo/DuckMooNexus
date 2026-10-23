"""Focused boundary checks for the new character adapters."""
import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from character_adapter import character_rows


class CharacterBoundaryTests(unittest.TestCase):
    def test_each_field_keeps_its_own_observation_time(self):
        rows=list(character_rows('DuckMooFolio.lua',{'DuckMooFolioDB':{'version':1,'characters':{
            'Player-1-X':{'name':'Example','realm':"Aman'Thul",'lastSeen':300,'repSeenAt':200,
                'professions':{171:{'id':171,'name':'Alchemy','seenAt':250,'expansions':{1:{'id':1,'rank':25,'max':100,'seenAt':100}}}},
                'reputations':{123:{'name':'Example faction','value':30}}}}}}))
        self.assertEqual({r[1]:r[3] for r in rows},{'profile':300,'profession':100,'reputation':200})

    def test_unknown_times_and_schema_do_not_become_current_readings(self):
        data={'DuckMooPlannerDB':{'schema':3,'characters':{'Player-1-X':{
            'name':'Example','realm':'Example','lastSeen':999,
            'professions':{1:{'name':'Alchemy','amount':200,'max':1000,'lastChecked':999}}}}}}
        pools=[r for r in character_rows('DuckMooPlanner.lua',data) if r[1]=='concentration']
        self.assertIsNone(pools[0][3])
        data['DuckMooPlannerDB']['schema']=999
        with self.assertRaises(ValueError):list(character_rows('DuckMooPlanner.lua',data))

if __name__=='__main__':unittest.main()
