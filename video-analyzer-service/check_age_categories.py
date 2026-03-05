from supabase_manager import supabase_manager

# Compter les vidéos par catégorie d'âge
age_groups = ['0+', '3+', '6+', '10+', '12+', '16+']

for age_group in age_groups:
    result = supabase_manager.client.table("analysis_results").select("*").eq("age_group", age_group).execute()
    count = len(result.data) if result.data else 0
    print(f"{age_group}: {count} vidéos")

# Vérifier aussi les vidéos sans catégorie d'âge
no_age = supabase_manager.client.table("analysis_results").select("*").is_("age_group", None).execute()
no_age_count = len(no_age.data) if no_age.data else 0
print(f"Sans catégorie d'âge: {no_age_count} vidéos")

# Afficher le total
total = supabase_manager.client.table("analysis_results").select("*").execute()
total_count = len(total.data) if total.data else 0
print(f"\nTotal: {total_count} vidéos")