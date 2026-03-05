# -*- coding: utf-8 -*-
from supabase_manager import SupabaseManager

m = SupabaseManager()

r = m.client.table('analysis_results').select('*').eq('scan_type', 'dailymotion_enfant').eq('success', True).is_('pacing_score', 'null').execute()
print(f'Videos avec success=True mais pacing_score=NULL: {len(r.data)}')

r2 = m.client.table('analysis_results').select('*').eq('scan_type', 'dailymotion_enfant').eq('success', True).execute()
print(f'Videos Dailymotion reussies: {len(r2.data)}')

r3 = m.client.table('video_analyses').select('*').execute()
print(f'Videos dans video_analyses: {len(r3.data)}')

success_titles = [v.get('series_title') for v in r2.data if v.get('series_title')]
analyses_titles = [v.get('metadata', {}).get('fr_title') for v in r3.data]
missing = [t for t in success_titles if t not in analyses_titles]
print(f'Videos reussies non dans video_analyses: {len(missing)}')
if missing:
    print('Exemples:')
    for t in missing[:5]:
        print(f' - {t}')